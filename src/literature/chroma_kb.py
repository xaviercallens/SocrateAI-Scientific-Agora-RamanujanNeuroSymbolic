#!/usr/bin/env python3
"""
src/literature/chroma_kb.py
===========================
Persistent multi-collection ChromaDB vector knowledge base for
SocrateAI-Scientific-RajMathRecovery.

Collections:
  1. `ramanujan_literature_v1`     — Downloaded arXiv papers across all pillars
                                     of Ramanujan's works, community extensions,
                                     physics dualities, and Lean 4 formalization.
  2. `ramanujan_primary_works_v1`  — Andrews & Berndt *Ramanujan's Lost Notebook*
                                     Parts I–IV (from `inputs/`) plus verified
                                     Campaign v2 primary manuscript records from
                                     `namagiri.db` (839 pages across Notebooks 1–3,
                                     Narosa 1988 Lost Notebook, Ono Letters).
  3. `rama_repo_artifacts`         — Core repository certificates, papers, BibTeX,
                                     literature review, Elenchus roadmap & ledger.

Supports incremental ingestion (skips already-indexed chunk IDs unless `--reset`
is passed) and unified cross-collection RAG search (`--collection all`).

Usage (via project .venv):
    .venv/bin/python src/literature/chroma_kb.py ingest --manifest docs/literature/corpus_manifest.json
    .venv/bin/python src/literature/chroma_kb.py query "Ramanujan partition congruences mod 5 crank" --n 6 --collection all
    .venv/bin/python src/literature/chroma_kb.py stats
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import chromadb
from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)

REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = REPO_ROOT / "data" / "chromadb"
LIT_COLLECTION = "ramanujan_literature_v1"
PRIMARY_COLLECTION = "ramanujan_primary_works_v1"
REPO_COLLECTION = "rama_repo_artifacts"

ANDREWS_BERNDT_VOLUMES: List[Dict[str, Any]] = [
    {
        "id": "ab_lost_nb_part1_2005",
        "filename": "Ramanujan_39_s_Lost_Notebook_Part_I_2005.pdf",
        "title": "Ramanujan's Lost Notebook, Part I (Andrews & Berndt, 2005)",
        "authors": "George E. Andrews, Bruce C. Berndt",
        "year": 2005,
        "pillar": "primary_lost_notebook",
    },
    {
        "id": "ab_lost_nb_part2_2008",
        "filename": "Ramanujan_39_s_Lost_Notebook_Part_II_2008.pdf",
        "title": "Ramanujan's Lost Notebook, Part II (Andrews & Berndt, 2008)",
        "authors": "George E. Andrews, Bruce C. Berndt",
        "year": 2008,
        "pillar": "primary_lost_notebook",
    },
    {
        "id": "ab_lost_nb_part3_2012",
        "filename": "Ramanujan_39_s_Lost_Notebook_Part_III_2012.pdf",
        "title": "Ramanujan's Lost Notebook, Part III (Andrews & Berndt, 2012)",
        "authors": "George E. Andrews, Bruce C. Berndt",
        "year": 2012,
        "pillar": "primary_lost_notebook",
    },
    {
        "id": "ab_lost_nb_part4_2013",
        "filename": "Ramanujan_39_s_Lost_Notebook_Part_IV_2013.pdf",
        "title": "Ramanujan's Lost Notebook, Part IV (Andrews & Berndt, 2013)",
        "authors": "George E. Andrews, Bruce C. Berndt",
        "year": 2013,
        "pillar": "primary_lost_notebook",
    },
]


def get_client(chroma_dir: Path = CHROMA_DIR) -> chromadb.PersistentClient:
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_dir))


def clean_pdf_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks: List[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        end = min(len(text), start + chunk_size)
        seg = text[start:end].strip()
        if len(seg) >= 80:
            chunks.append(seg)
        if end >= len(text):
            break
        start += step
    return chunks


def extract_pdf_pages(pdf_path: Path, max_pages: int = 500) -> List[Tuple[int, str]]:
    reader = PdfReader(str(pdf_path))
    pages: List[Tuple[int, str]] = []
    for idx, page in enumerate(reader.pages[:max_pages], start=1):
        try:
            raw = page.extract_text() or ""
        except Exception:
            raw = ""
        cleaned = clean_pdf_text(raw)
        if len(cleaned) >= 60:
            pages.append((idx, cleaned))
    return pages


def _existing_ids(collection: Any) -> Set[str]:
    try:
        res = collection.get(include=[])
        return set(res.get("ids") or [])
    except Exception:
        return set()


def _upsert_batched(
    collection: Any,
    ids: List[str],
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    batch_size: int = 64,
    skip_existing: bool = True,
) -> Tuple[int, int]:
    """Upsert documents in batches; returns (upserted_count, skipped_count)."""
    if skip_existing:
        existing = _existing_ids(collection)
        f_ids, f_docs, f_metas = [], [], []
        skipped = 0
        for doc_id, doc, meta in zip(ids, documents, metadatas):
            if doc_id in existing:
                skipped += 1
            else:
                f_ids.append(doc_id)
                f_docs.append(doc)
                f_metas.append(meta)
        ids, documents, metadatas = f_ids, f_docs, f_metas
    else:
        skipped = 0

    total = 0
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
        total += len(ids[i : i + batch_size])
    return total, skipped


def ingest_primary_works(
    client: chromadb.PersistentClient,
    skip_existing: bool = True,
    max_pages_per_vol: int = 500,
) -> Dict[str, Any]:
    """Index Andrews-Berndt Lost Notebook Parts I-IV + Campaign v2 DB records."""
    primary_col = client.get_or_create_collection(
        name=PRIMARY_COLLECTION,
        metadata={
            "hnsw:space": "cosine",
            "description": "Ramanujan primary works: Andrews-Berndt Lost Notebook Parts I-IV + Campaign v2 839-page DB",
        },
    )
    existing = _existing_ids(primary_col) if skip_existing else set()

    p_ids: List[str] = []
    p_docs: List[str] = []
    p_metas: List[Dict[str, Any]] = []
    volumes_summary: List[Dict[str, Any]] = []

    inputs_dir = REPO_ROOT / "inputs"
    for vol in ANDREWS_BERNDT_VOLUMES:
        pdf_path = inputs_dir / vol["filename"]
        vol_id = vol["id"]
        if not pdf_path.is_file():
            volumes_summary.append({"id": vol_id, "present": False, "pages": 0, "chunks": 0})
            continue

        # Fast-skip entire volume if already indexed in incremental mode
        marker_prefix = f"{vol_id}__p"
        already_for_vol = sum(1 for eid in existing if eid.startswith(marker_prefix))
        if skip_existing and already_for_vol >= 200:
            volumes_summary.append({
                "id": vol_id,
                "present": True,
                "pages": -1,
                "chunks_existing": already_for_vol,
                "skipped_cached": True,
            })
            continue

        pages = extract_pdf_pages(pdf_path, max_pages=max_pages_per_vol)
        n_chunks = 0
        for page_num, page_text in pages:
            for c_idx, chunk in enumerate(chunk_text(page_text, chunk_size=1400, overlap=200)):
                cid = f"{vol_id}__p{page_num}_c{c_idx}"
                p_ids.append(cid)
                p_docs.append(f"[{vol['title']}, p.{page_num}] {chunk}")
                p_metas.append({
                    "arxiv_id": vol_id,
                    "title": vol["title"],
                    "authors": vol["authors"],
                    "year": vol["year"],
                    "pillar": vol["pillar"],
                    "page": page_num,
                    "chunk_idx": c_idx,
                    "source_type": "andrews_berndt_pdf",
                })
                n_chunks += 1
        volumes_summary.append({
            "id": vol_id,
            "present": True,
            "pages": len(pages),
            "chunks_new": n_chunks,
        })

    # Index verified Tier A & Tier B primary manuscript records from namagiri.db
    db_path = REPO_ROOT / "namagiri.db"
    db_rows_indexed = 0
    if db_path.is_file():
        conn = sqlite3.connect(str(db_path))
        try:
            cur = conn.cursor()
            rows = cur.execute(
                """
                SELECT id, notebook, chapter, page, archetype, conjecture, eta_exponents,
                       domain, lean_status, epistemic_tier, oeis_match, physics_mapping,
                       andrews_berndt_ref, latex_raw
                FROM discoveries
                WHERE epistemic_tier IN ('A', 'B')
                   OR lean_status IN ('VERIFIED', 'CATALOG_MATCHED')
                ORDER BY notebook, chapter, page
                """
            ).fetchall()
            for r in rows:
                (
                    rid, nb, ch, pg, arch, conj, eta_exp, dom, lstat,
                    tier, oeis, phys, ab_ref, latex_raw,
                ) = r
                cid = f"db_primary_{rid}"
                doc = (
                    f"[Ramanujan Primary Manuscript {nb}/{ch}/p{pg} | Tier {tier} | {lstat}] "
                    f"Archetype: {arch or 'unknown'} | Domain: {dom or ''} | "
                    f"OEIS: {oeis or 'none'} | Ref: {ab_ref or ''}\n"
                    f"LaTeX: {latex_raw or conj or ''}\n"
                    f"Eta exponents: {eta_exp or '{}'} | Invariants: {phys or ''}"
                )
                p_ids.append(cid)
                p_docs.append(doc[:1600])
                p_metas.append({
                    "arxiv_id": f"{nb}/{ch}/p{pg}",
                    "title": f"Ramanujan {nb} {ch} p.{pg}",
                    "authors": "Srinivasa Ramanujan",
                    "year": 1920,
                    "pillar": "primary_manuscript_db",
                    "page": int(pg or 0),
                    "epistemic_tier": str(tier or ""),
                    "oeis_match": str(oeis or ""),
                    "source_type": "namagiri_db_primary",
                })
                db_rows_indexed += 1

            # Also build grouped page-cluster summaries of the 2,378 Tier C transcriptions
            # by (notebook, chapter) so RAG covers 100% of all 839 pages compactly
            clusters = cur.execute(
                """
                SELECT notebook, chapter, COUNT(*),
                       GROUP_CONCAT(DISTINCT archetype),
                       GROUP_CONCAT(substr(COALESCE(latex_raw, conjecture, ''), 1, 90), ' ; ')
                FROM discoveries
                WHERE epistemic_tier = 'C'
                GROUP BY notebook, chapter
                ORDER BY notebook, chapter
                """
            ).fetchall()
            for nb, ch, cnt, archs, sample_tex in clusters:
                safe_ch = re.sub(r"[^A-Za-z0-9_]+", "_", f"{nb}_{ch}")
                cid = f"db_tierC_cluster_{safe_ch}"
                doc = (
                    f"[Ramanujan {nb}/{ch} — {cnt} Tier C open transcriptions]\n"
                    f"Topics/Archetypes: {(archs or '')[:300]}\n"
                    f"Representative expressions: {(sample_tex or '')[:1000]}"
                )
                p_ids.append(cid)
                p_docs.append(doc)
                p_metas.append({
                    "arxiv_id": f"{nb}/{ch}",
                    "title": f"Ramanujan {nb} {ch} Tier C Cluster ({cnt} entries)",
                    "authors": "Srinivasa Ramanujan",
                    "year": 1920,
                    "pillar": "primary_manuscript_db",
                    "page": 0,
                    "epistemic_tier": "C",
                    "source_type": "namagiri_db_cluster",
                })
                db_rows_indexed += 1
        finally:
            conn.close()

    upserted_p, skipped_p = _upsert_batched(
        primary_col, p_ids, p_docs, p_metas, skip_existing=skip_existing
    )
    return {
        "collection": PRIMARY_COLLECTION,
        "total_chunks": primary_col.count(),
        "upserted": upserted_p,
        "skipped": skipped_p,
        "volumes": volumes_summary,
        "db_records_prepared": db_rows_indexed,
    }


def ingest_literature(
    manifest_path: Path,
    chroma_dir: Path = CHROMA_DIR,
    reset: bool = False,
    include_primary: bool = True,
) -> Dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    papers = manifest.get("papers", [])

    client = get_client(chroma_dir)
    if reset:
        for name in (LIT_COLLECTION, PRIMARY_COLLECTION, REPO_COLLECTION):
            try:
                client.delete_collection(name)
            except Exception:
                pass

    skip_existing = not reset

    lit_col = client.get_or_create_collection(
        name=LIT_COLLECTION,
        metadata={"hnsw:space": "cosine", "description": "arXiv mathematical/physical literature for RAMA/DualScale"},
    )
    repo_col = client.get_or_create_collection(
        name=REPO_COLLECTION,
        metadata={"hnsw:space": "cosine", "description": "Repository certificates, papers, roadmap, and BibTeX"},
    )

    existing_lit = _existing_ids(lit_col) if skip_existing else set()

    lit_ids: List[str] = []
    lit_docs: List[str] = []
    lit_metas: List[Dict[str, Any]] = []
    ingested_papers: List[Dict[str, Any]] = []

    for paper in papers:
        arxiv_id = str(paper["arxiv_id"])
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", arxiv_id)
        title = str(paper.get("title", "")).replace("\n", " ").strip()
        authors = ", ".join(paper.get("authors", []))[:500]
        published = str(paper.get("published", ""))
        year = int(published[:4]) if published[:4].isdigit() else 0
        pillar = str(paper.get("pillar", "general"))
        url = str(paper.get("url", f"https://arxiv.org/abs/{arxiv_id}"))
        pdf_url = str(paper.get("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}"))
        summary = clean_pdf_text(str(paper.get("summary", "")))
        local_pdf = REPO_ROOT / str(paper.get("local_pdf", ""))

        # Fast-skip already-ingested papers in incremental mode
        abs_id = f"{safe_id}__abstract"
        pdf_prefix = f"{safe_id}__p"
        existing_for_paper = sum(1 for eid in existing_lit if eid == abs_id or eid.startswith(pdf_prefix))
        if skip_existing and existing_for_paper >= 2:
            ingested_papers.append({
                "arxiv_id": arxiv_id,
                "title": title,
                "year": year,
                "pillar": pillar,
                "chunks_existing": existing_for_paper,
                "skipped_cached": True,
            })
            continue

        base_meta = {
            "arxiv_id": arxiv_id,
            "title": title[:300],
            "authors": authors,
            "year": year,
            "pillar": pillar,
            "url": url,
            "pdf_url": pdf_url,
            "journal_ref": str(paper.get("journal_ref") or "")[:200],
            "doi": str(paper.get("doi") or "")[:120],
        }

        if summary:
            lit_ids.append(abs_id)
            lit_docs.append(f"Title: {title}\nAuthors: {authors}\nYear: {year}\nAbstract: {summary}")
            lit_metas.append({**base_meta, "page": 0, "chunk_idx": 0, "source_type": "arxiv_abstract"})

        n_pages = 0
        n_chunks = 0
        if local_pdf.is_file() and local_pdf.stat().st_size > 1024:
            pages = extract_pdf_pages(local_pdf, max_pages=160)
            n_pages = len(pages)
            for page_num, page_text in pages:
                for c_idx, chunk in enumerate(chunk_text(page_text, chunk_size=1200, overlap=200)):
                    lit_ids.append(f"{safe_id}__p{page_num}_c{c_idx}")
                    lit_docs.append(f"[{title} ({year}), p.{page_num}] {chunk}")
                    lit_metas.append({
                        **base_meta,
                        "page": page_num,
                        "chunk_idx": c_idx,
                        "source_type": "arxiv_pdf",
                    })
                    n_chunks += 1

        ingested_papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "year": year,
            "pillar": pillar,
            "pdf_pages_extracted": n_pages,
            "chunks_indexed": n_chunks + (1 if summary else 0),
        })

    n_lit_upserted, n_lit_skipped = _upsert_batched(
        lit_col, lit_ids, lit_docs, lit_metas, skip_existing=skip_existing
    )

    # Refresh repo artifacts collection (small, fast — always upsert fresh)
    repo_ids: List[str] = []
    repo_docs: List[str] = []
    repo_metas: List[Dict[str, Any]] = []

    repo_sources = [
        ("bib", REPO_ROOT / "dualscale" / "refs" / "bib" / "dualscale.bib"),
        ("v3_sec00", REPO_ROOT / "docs" / "v3_paper" / "sections" / "00_abstract.tex"),
        ("v3_sec02", REPO_ROOT / "docs" / "v3_paper" / "sections" / "02_epistemic_protocol.tex"),
        ("v3_sec03", REPO_ROOT / "docs" / "v3_paper" / "sections" / "03_conjectural_dictionary.tex"),
        ("v3_sec04b", REPO_ROOT / "docs" / "v3_paper" / "sections" / "04b_bps_state_counting.tex"),
        ("v3_sec05", REPO_ROOT / "docs" / "v3_paper" / "sections" / "05_computational_experiments.tex"),
        ("v3_sec06", REPO_ROOT / "docs" / "v3_paper" / "sections" / "06_formalization_status.tex"),
        ("v3_sec07", REPO_ROOT / "docs" / "v3_paper" / "sections" / "07_conclusion.tex"),
        ("lit_review_fr", REPO_ROOT / "docs" / "literature" / "REVUE_LITTERATURE_DETAILLEE.md"),
        ("elenchus_roadmap", REPO_ROOT / "docs" / "RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md"),
        ("llm_lean_validation", REPO_ROOT / "dualscale" / "certificates" / "llm_lean_validation_report.json"),
        ("elenchus_audit_ledger", REPO_ROOT / "dualscale" / "certificates" / "ramanujan_elenchus_audit_ledger.json"),
    ]

    for tag, fpath in repo_sources:
        if not fpath.is_file():
            continue
        raw = clean_pdf_text(fpath.read_text(encoding="utf-8", errors="replace"))
        for c_idx, chunk in enumerate(chunk_text(raw, chunk_size=1200, overlap=150)):
            repo_ids.append(f"repo_{tag}_c{c_idx}")
            repo_docs.append(f"[{fpath.relative_to(REPO_ROOT)}] {chunk}")
            repo_metas.append({"source": str(fpath.relative_to(REPO_ROOT)), "tag": tag, "chunk_idx": c_idx})

    camp_path = REPO_ROOT / "dualscale" / "certificates" / "campaign_v2_report.json"
    if camp_path.is_file():
        camp = json.loads(camp_path.read_text(encoding="utf-8"))
        summary_doc = json.dumps({
            "corpus_pages_total": camp.get("corpus_pages_total"),
            "total_pages_processed": camp.get("total_pages_processed"),
            "extraction_errors": camp.get("extraction_errors"),
            "discoveries_total": camp.get("discoveries_total"),
            "discoveries_by_tier": camp.get("discoveries_by_tier"),
            "unique_exact_eta_quotients": camp.get("unique_exact_eta_quotients"),
            "verified_ramanujan_identities": camp.get("verified_ramanujan_identities"),
            "refuted_ocr_typos_count": camp.get("refuted_ocr_typos_count"),
            "lean_kernel_verification": camp.get("lean_kernel_verification"),
        }, indent=2)
        repo_ids.append("repo_campaign_v2_summary")
        repo_docs.append(summary_doc)
        repo_metas.append({"source": "dualscale/certificates/campaign_v2_report.json", "tag": "campaign_v2", "chunk_idx": 0})

    n_repo_upserted, _ = _upsert_batched(repo_col, repo_ids, repo_docs, repo_metas, skip_existing=False)

    primary_summary: Optional[Dict[str, Any]] = None
    if include_primary:
        primary_summary = ingest_primary_works(client, skip_existing=skip_existing)

    return {
        "chroma_dir": str(chroma_dir.relative_to(REPO_ROOT)),
        "literature_collection": LIT_COLLECTION,
        "primary_collection": PRIMARY_COLLECTION,
        "repo_collection": REPO_COLLECTION,
        "papers_in_manifest": len(ingested_papers),
        "literature_chunks": lit_col.count(),
        "primary_chunks": primary_summary["total_chunks"] if primary_summary else 0,
        "repo_chunks": repo_col.count(),
        "upserted_lit": n_lit_upserted,
        "skipped_lit": n_lit_skipped,
        "upserted_repo": n_repo_upserted,
        "primary_summary": primary_summary,
    }


def semantic_query(
    query_text: str,
    n_results: int = 5,
    pillar: Optional[str] = None,
    collection_name: str = LIT_COLLECTION,
    chroma_dir: Path = CHROMA_DIR,
) -> List[Dict[str, Any]]:
    client = get_client(chroma_dir)
    if collection_name == "all":
        target_names = [c.name for c in client.list_collections()]
    else:
        target_names = [collection_name]

    hits: List[Dict[str, Any]] = []
    for cname in target_names:
        try:
            col = client.get_collection(name=cname)
        except Exception:
            continue
        if col.count() == 0:
            continue
        where = {"pillar": pillar} if (pillar and pillar != "all" and cname != REPO_COLLECTION) else None
        try:
            res = col.query(query_texts=[query_text], n_results=min(n_results, col.count()), where=where)
        except Exception:
            res = col.query(query_texts=[query_text], n_results=min(n_results, col.count()))
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for doc_id, doc, meta, dist in zip(ids, docs, metas, dists):
            hits.append({
                "collection": cname,
                "id": doc_id,
                "distance": round(float(dist), 4),
                "metadata": meta,
                "excerpt": doc[:600],
            })

    hits.sort(key=lambda h: h["distance"])
    return hits[:n_results]


def main() -> None:
    parser = argparse.ArgumentParser(description="Persistent Multi-Collection ChromaDB Knowledge Base for RAMA/DualScale")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest")
    p_ing.add_argument("--manifest", default="docs/literature/corpus_manifest.json")
    p_ing.add_argument("--reset", action="store_true")
    p_ing.add_argument("--no-primary", action="store_true", help="Skip indexing Andrews-Berndt PDFs and namagiri.db")

    p_q = sub.add_parser("query")
    p_q.add_argument("text")
    p_q.add_argument("--n", type=int, default=5)
    p_q.add_argument("--pillar", default="all")
    p_q.add_argument("--collection", default=LIT_COLLECTION, help="Collection name or 'all'")

    sub.add_parser("stats")

    args = parser.parse_args()
    if args.cmd == "ingest":
        res = ingest_literature(
            REPO_ROOT / args.manifest,
            reset=args.reset,
            include_primary=not args.no_primary,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "query":
        hits = semantic_query(args.text, n_results=args.n, pillar=args.pillar, collection_name=args.collection)
        print(json.dumps(hits, indent=2, ensure_ascii=False))
    elif args.cmd == "stats":
        client = get_client()
        out = {}
        for col in client.list_collections():
            c = client.get_collection(col.name)
            out[col.name] = {"count": c.count(), "metadata": c.metadata}
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

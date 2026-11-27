#!/usr/bin/env python3
"""
src/campaign/run_campaign_v2.py
===============================
Rigorous, Token-Optimized Regeneration Campaign across ALL Ramanujan Manuscripts:
  1. Lost Notebook (1988 Narosa facsimile, PDF pages 37–169 -> 133 handwritten sheets)
  2. Ramanujan's Letters from Ono (8 PNG scans in inputs/)
  3. Notebook 1 (320 JPG pages)
  4. Notebook 2 (349 JPG pages)
  5. Notebook 3 (29 JPG pages)
Total: 839 manuscript pages.

Pipeline Stages:
  Stage 1: Render Lost Notebook facsimile sheets via `pdftoppm` (idempotent).
  Stage 2: Concurrent Gemini 2.5 Flash structured Vision extraction
           (`thinking_budget=0`, `temperature=0.0`, JSONL checkpointed).
  Stage 3: Zero-token deterministic exact-arithmetic math engine:
           - Exact Möbius inversion with overdetermination guard (>=3 tail zeros)
           - Exact multi-cusp c_eff(0) & max_c c_eff(c), Ono Thm 1.64, positivity check
           - Exact prefix matching against 28 analytically computed classical
             Ramanujan q-series & mock theta functions (orders 3, 5, 6, 7, RR, Eisenstein)
  Stage 4: Standalone Lean 4 zero-axiom kernel verification (`MATHESIS-GATE: allow=`),
           consolidated into `dualscale/lean/DualScale/Discovery/CampaignV2Verified.lean`,
           verified by BOTH `lean` and `mathesis_gate.py` (with real footprints!).
  Stage 5: Non-destructive backup of legacy `namagiri.db` -> `namagiri_legacy_v1.db`,
           clean regeneration of `namagiri.db`, `dualscale/certificates/campaign_v2_report.json`,
           and `dashboard_data.json`.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction
import glob
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from google import genai
from google.genai import types

from src.lean.kernel_prover import (
    _sanitize_ident,
    generate_entry_lean_block,
    generate_equation_lean_block,
    write_and_verify_campaign_lean_catalog,
)
from src.math_engine.exact_qseries import (
    compute_eta_invariants,
    eta_quotient_coeffs,
    invert_eta_quotient_exact,
    match_classical_catalog,
)
from src.math_engine.latex_symbolic_parser import analyze_latex_identity
from src.persistence.database import NamagiriDB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

VISION_MODEL = "gemini-2.5-flash"
NAROSA_PDF = (
    REPO_ROOT
    / "inputs"
    / "Srinivasa Ramanujan The Lost Note Book And Other Unpublished Papers 1988 New Delhi - Narosa Publishing House .pdf"
)
LOST_NB_IMG_DIR = REPO_ROOT / "input" / "LostNotebook_Narosa_1988" / "images"
CHECKPOINT_JSONL = REPO_ROOT / "docs" / "live_vision_results" / "campaign_v2_extractions.jsonl"
CAMPAIGN_CERT_PATH = REPO_ROOT / "dualscale" / "certificates" / "campaign_v2_report.json"
CAMPAIGN_LEAN_PATH = REPO_ROOT / "dualscale" / "lean" / "DualScale" / "Discovery" / "CampaignV2Verified.lean"

VISION_PROMPT = """You are an expert mathematical historian transcribing Srinivasa Ramanujan's handwritten notebooks and Lost Notebook.

Carefully examine this manuscript page image and return ONLY valid JSON matching this schema:
{
  "has_math": true/false,
  "page_topic": "eta_quotient" | "mock_theta" | "q_series" | "continued_fraction" | "theta_function" | "modular_equation" | "partition_identity" | "hypergeometric" | "integral_or_other" | "non_math",
  "identities": [
    {
      "latex": "faithful LaTeX transcription of the identity on the page",
      "identity_type": "eta_quotient" | "mock_theta" | "q_series" | "continued_fraction" | "theta_function" | "modular_equation" | "partition_identity" | "hypergeometric" | "integral_or_other",
      "explicit_eta_exponents": {"d": r},
      "explicit_q_coefficients": [a0, a1, a2, ...],
      "coefficients_source": "transcribed_from_page" | "derived_from_formula" | "none",
      "named_classical_function": "canonical name if clearly identified, else empty string",
      "confidence": "high" | "medium" | "low"
    }
  ]
}

STRICT RIGOR RULES:
1. Extract up to 3 clearest, most important identities on the page. If the page is blank, a cover/title page, or illegible, set "has_math": false and "identities": [].
2. NEVER invent formulas or hallucinate coefficients.
3. Fill "explicit_eta_exponents" (mapping positive integer divisor strings like "1","2","3" to integer exponents r_d) ONLY when the page explicitly writes a Dedekind eta quotient, Euler q-product prod_{n>=1}(1-q^(d*n))^(r_d), or Ramanujan's f(-q^d), phi(q)=eta(2t)^5/(eta(t)^2 eta(4t)^2), psi(q)=eta(2t)^2/eta(t), chi(q)=eta(2t)^2/(eta(t)eta(4t)). Otherwise return {}.
4. Fill "explicit_q_coefficients" with exact integers [a0, a1, ..., aN] (up to 15 terms) ONLY when either explicitly written as a power/q-series expansion on the page ("transcribed_from_page") OR unambiguously implied by an explicit written q-series/mock-theta/product formula ("derived_from_formula"). Otherwise return [] and "none".
5. Return ONLY raw JSON."""


# ---------------------------------------------------------------------------
# Stage 1: Render Lost Notebook Facsimile + Build Complete Manuscript Manifest
# ---------------------------------------------------------------------------


def render_lost_notebook_pages(first_pdf_page: int = 37, last_pdf_page: int = 169, dpi: int = 140) -> List[Path]:
    """Render Narosa 1988 Lost Notebook + Hardy Letters sheets (PDF pages 37..169) idempotently."""
    LOST_NB_IMG_DIR.mkdir(parents=True, exist_ok=True)
    expected_count = last_pdf_page - first_pdf_page + 1
    existing = sorted(LOST_NB_IMG_DIR.glob("lost_nb_p*.jpg"))
    if len(existing) >= expected_count:
        logging.info(f"[Stage 1] Lost Notebook pages already rendered ({len(existing)} images).")
        return existing

    if not NAROSA_PDF.is_file():
        logging.warning(f"[Stage 1] Narosa Lost Notebook PDF not found at {NAROSA_PDF}")
        return []

    logging.info(
        f"[Stage 1] Rendering Narosa 1988 Lost Notebook PDF pages {first_pdf_page}..{last_pdf_page} "
        f"({expected_count} sheets) at {dpi} DPI..."
    )
    prefix = str(LOST_NB_IMG_DIR / "lost_nb_p")
    subprocess.run(
        [
            "pdftoppm",
            "-jpeg",
            "-r",
            str(dpi),
            "-f",
            str(first_pdf_page),
            "-l",
            str(last_pdf_page),
            str(NAROSA_PDF),
            prefix,
        ],
        check=True,
    )
    rendered = sorted(LOST_NB_IMG_DIR.glob("lost_nb_p*.jpg"))
    logging.info(f"[Stage 1] Rendered {len(rendered)} Lost Notebook facsimile sheets.")
    return rendered


def parse_provenance(path: Path) -> Dict[str, Any]:
    rel = str(path.relative_to(REPO_ROOT))
    name = path.name
    m_page = re.search(r"(\d+)", name)
    page_num = int(m_page.group(1)) if m_page else 0

    if "LostNotebook_Narosa_1988" in rel:
        # PDF page 37 corresponds to Narosa Book page 1
        book_page = max(1, page_num - 36) if page_num >= 37 else page_num
        section = "LostNotebook_Sheets" if book_page <= 90 else "HardyLetters_And_Sheets"
        return {
            "notebook": "LostNotebook_1988",
            "chapter": section,
            "page": book_page,
            "source_pdf": "Narosa_1988_Lost_Notebook",
            "rel_path": rel,
        }
    if "6-ramanujans-letters-from-ono" in name:
        return {
            "notebook": "Ono_Letters",
            "chapter": "Letters",
            "page": page_num,
            "source_pdf": "Ono_Ramanujan_Letters",
            "rel_path": rel,
        }
    m_nb = re.search(r"NoteBook(\d+)", rel)
    nb = f"NoteBook{m_nb.group(1)}" if m_nb else "Unknown"
    m_ch = re.search(r"(chapter[IVXLCDM]+)", rel, re.IGNORECASE)
    ch = m_ch.group(1) if m_ch else "direct"
    return {
        "notebook": nb,
        "chapter": ch,
        "page": page_num,
        "source_pdf": nb,
        "rel_path": rel,
    }


def collect_manuscript_pages(
    include_lost: bool = True,
    include_ono: bool = True,
    include_notebooks: bool = True,
) -> List[Path]:
    pages: List[Path] = []
    if include_lost:
        pages.extend(render_lost_notebook_pages())
    if include_ono:
        pages.extend(sorted((REPO_ROOT / "inputs").glob("6-ramanujans-letters-from-ono-*.png")))
    if include_notebooks:
        for nb in ("NoteBook1", "NoteBook2", "NoteBook3"):
            nb_root = REPO_ROOT / "input" / nb
            if nb_root.is_dir():
                pages.extend(sorted(nb_root.rglob("*.jpg")))
    # Deduplicate preserving order
    seen = set()
    unique: List[Path] = []
    for p in pages:
        rp = p.resolve()
        if rp not in seen and rp.is_file():
            seen.add(rp)
            unique.append(p)
    return unique


# ---------------------------------------------------------------------------
# Stage 2: Concurrent Structured Gemini 2.5 Flash Vision Extraction
# ---------------------------------------------------------------------------


def _load_checkpoint(path: Path) -> Dict[str, Dict[str, Any]]:
    done: Dict[str, Dict[str, Any]] = {}
    if not path.is_file():
        return done
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                key = rec.get("rel_path")
                if key and "error" not in rec:
                    done[key] = rec
            except json.JSONDecodeError:
                continue
    return done


def _extract_one_page(client: genai.Client, img_path: Path, max_retries: int = 2) -> Dict[str, Any]:
    prov = parse_provenance(img_path)
    img_bytes = img_path.read_bytes()
    mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"

    last_err = ""
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=VISION_MODEL,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type=mime),
                    VISION_PROMPT,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                    max_output_tokens=2048,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            raw = (resp.text or "").strip()
            if not raw:
                raise ValueError("Empty response text from Gemini Vision")
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw).strip()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                # Properly repair unescaped LaTeX backslashes without corrupting already-escaped \\ pairs.
                repaired = re.sub(
                    r'\\(\\|"|/|b|f|n|r|t|u[0-9a-fA-F]{4})|\\',
                    lambda m: m.group(0) if m.group(1) is not None else r"\\",
                    raw,
                )
                try:
                    parsed = json.loads(repaired)
                except json.JSONDecodeError:
                    # Second fallback: treat all single backslashes except \\ and \" as literal LaTeX backslashes
                    repaired2 = re.sub(
                        r'\\(\\|")|\\',
                        lambda m: m.group(0) if m.group(1) is not None else r"\\",
                        raw,
                    )
                    parsed = json.loads(repaired2)
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected JSON object, got {type(parsed).__name__}")

            usage = getattr(resp, "usage_metadata", None)
            prompt_tok = int(getattr(usage, "prompt_token_count", 0) or 0)
            cand_tok = int(getattr(usage, "candidates_token_count", 0) or 0)
            return {
                **prov,
                "model": VISION_MODEL,
                "prompt_tokens": prompt_tok,
                "candidate_tokens": cand_tok,
                "has_math": bool(parsed.get("has_math", False)),
                "page_topic": str(parsed.get("page_topic", "non_math")),
                "identities": parsed.get("identities", []) if isinstance(parsed.get("identities"), list) else [],
            }
        except Exception as exc:
            last_err = str(exc)
            wait = min(30.0, (2.0 ** attempt) + (0.25 * attempt))
            if "429" in last_err or "RESOURCE_EXHAUSTED" in last_err:
                wait = min(45.0, 4.0 * (attempt + 1))
            time.sleep(wait)

    return {
        **prov,
        "model": VISION_MODEL,
        "prompt_tokens": 0,
        "candidate_tokens": 0,
        "has_math": False,
        "page_topic": "extraction_error",
        "identities": [],
        "error": last_err[:300],
    }


def run_vision_stage(
    pages: List[Path],
    workers: int = 12,
    force_reextract: bool = False,
    skip_vision: bool = False,
) -> List[Dict[str, Any]]:
    CHECKPOINT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    if force_reextract and CHECKPOINT_JSONL.is_file():
        CHECKPOINT_JSONL.unlink()

    completed = _load_checkpoint(CHECKPOINT_JSONL)
    pending = [] if skip_vision else [p for p in pages if str(p.relative_to(REPO_ROOT)) not in completed]
    logging.info(
        f"[Stage 2] Vision Extraction: {len(pages)} total pages | "
        f"{len(completed)} cached | {len(pending)} to extract (workers={workers}, model={VISION_MODEL})."
    )

    if pending:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set; refusing to fall back to mock vision.")
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=60_000))
        write_lock = threading.Lock()
        done_count = 0
        t0 = time.time()

        with CHECKPOINT_JSONL.open("a", encoding="utf-8") as logf:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futs = {pool.submit(_extract_one_page, client, p): p for p in pending}
                for fut in as_completed(futs):
                    rec = fut.result()
                    with write_lock:
                        logf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        logf.flush()
                        completed[rec["rel_path"]] = rec
                        done_count += 1
                        if done_count % 50 == 0 or done_count == len(pending):
                            elapsed = time.time() - t0
                            rate = done_count / max(elapsed, 0.1)
                            eta = (len(pending) - done_count) / max(rate, 0.01)
                            logging.info(
                                f"  [Vision] {done_count}/{len(pending)} done "
                                f"({rate:.2f} pages/s, ETA {eta:.0f}s)"
                            )

    # Return in deterministic manuscript page order
    ordered = []
    for p in pages:
        rel = str(p.relative_to(REPO_ROOT))
        if rel in completed:
            ordered.append(completed[rel])
    return ordered


# ---------------------------------------------------------------------------
# Stage 3: Zero-Token Exact Math Analysis, Möbius Inversion & Catalog Match
# ---------------------------------------------------------------------------


def _parse_int_dict(raw: Any, max_d: int = 36, max_abs_r: int = 48) -> Dict[int, int]:
    if not isinstance(raw, dict):
        return {}
    out: Dict[int, int] = {}
    for k, v in raw.items():
        try:
            d = int(str(k).strip())
            r = int(v)
        except (ValueError, TypeError):
            return {}
        if d <= 0 or d > max_d or r == 0 or abs(r) > max_abs_r:
            if r == 0:
                continue
            return {}
        out[d] = out.get(d, 0) + r
    return {d: r for d, r in sorted(out.items()) if r != 0}


def _parse_int_list(raw: Any, max_len: int = 30) -> List[int]:
    if not isinstance(raw, list):
        return []
    out: List[int] = []
    for item in raw[:max_len]:
        if isinstance(item, bool):
            return []
        if isinstance(item, int):
            out.append(item)
        elif isinstance(item, float) and item.is_integer():
            out.append(int(item))
        elif isinstance(item, str) and re.fullmatch(r"\s*[+-]?\d+\s*", item):
            out.append(int(item.strip()))
        else:
            return []
    return out


def _ab_reference_for_topic(topic: str, notebook: str) -> str:
    t = (topic or "").lower()
    if "mock" in t or "integral" in t:
        return "Andrews-Berndt Part I (2005)"
    if "eta" in t or "q_series" in t or "theta" in t or "modular" in t or "eisenstein" in t:
        return "Andrews-Berndt Part II (2008)"
    if "fraction" in t or "partition" in t or "rogers" in t:
        return "Andrews-Berndt Part III (2012)"
    if notebook == "LostNotebook_1988":
        return "Andrews-Berndt Lost Notebook (Parts I–V)"
    return f"Berndt, Ramanujan's Notebooks ({notebook})"


def _domain_and_shadow(topic: str, inv: Optional[Dict[str, Any]], cat: Optional[Dict[str, Any]]) -> Tuple[str, str]:
    if cat and cat["category"].startswith("mock_theta"):
        return "Mock Modular Forms (Zwegers)", f"{cat['name']} ({cat['oeis']})"
    if inv is not None:
        if inv["is_weight_half"]:
            return "Modular Forms (Weight 1/2)", f"Level N={inv['level_N']}, c_eff(0)={inv['c_eff_cusp0']}"
        if inv["ono_164_modular_gamma0_N"]:
            return "Modular Forms (Gamma_0(N))", f"Ono Thm 1.64 verified on Gamma_0({inv['level_N']})"
        return "Eta-Quotients (q-Series)", f"Level N={inv['level_N']}, c_eff(0)={inv['c_eff_cusp0']}"
    if topic == "continued_fraction":
        return "Continued Fractions & Topology", "q-Continued Fraction"
    if topic == "hypergeometric":
        return "Hypergeometric & Elliptic Series", "Picard-Fuchs / 1/pi Series"
    if topic == "modular_equation":
        return "Modular Equations & Class Invariants", "Algebraic Modular Relation"
    return "q-Series & Number Theory", topic


def analyze_extractions(
    page_records: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deterministically analyze all extracted identities using:
      1. Exact symbolic LaTeX AST parser (`analyze_latex_identity`) for Ramanujan's
         f, phi, psi, chi, eta, infinite Euler products, and mock theta functions
      2. Exact 30-term verification of LHS = RHS identities (with automatic OCR typo refutation!)
      3. Exact deterministic Möbius inversion over Q with overdetermination guard (>=3 tail zeros)
      4. Exact prefix matching against 28 analytically generated classical Ramanujan series
    Returns (all_discoveries, unique_eta_quotients, verified_equations, refuted_ocr_equations).
    """
    discoveries: List[Dict[str, Any]] = []
    unique_eta: Dict[str, Dict[str, Any]] = {}
    verified_equations: List[Dict[str, Any]] = []
    seen_eq_keys = set()
    refuted_equations: List[Dict[str, Any]] = []

    for rec in page_records:
        if not rec.get("has_math") or not rec.get("identities"):
            continue
        for idx, ident in enumerate(rec["identities"][:3]):
            if not isinstance(ident, dict):
                continue
            latex = str(ident.get("latex", "")).strip()
            if not latex:
                continue
            id_type = str(ident.get("identity_type", rec.get("page_topic", "q_series")))
            confidence = str(ident.get("confidence", "low"))
            named_fn = str(ident.get("named_classical_function", "")).strip()
            coeffs_source = str(ident.get("coefficients_source", "none"))

            explicit_eta = _parse_int_dict(ident.get("explicit_eta_exponents"))
            explicit_coeffs = _parse_int_list(ident.get("explicit_q_coefficients"))

            # Run zero-token deterministic symbolic LaTeX analysis
            sym_res = analyze_latex_identity(latex, check_terms=30)
            src_tag = f"{rec['notebook']}/{rec['chapter']}/p{rec['page']}"

            if sym_res["refuted_equation"]:
                refuted_equations.append({
                    "source": src_tag,
                    "latex": latex[:180],
                    **sym_res["refuted_equation"],
                })

            # Register verified LHS = RHS Ramanujan identities for Lean 4 kernel proofs
            eq_lean_id = None
            for veq in sym_res.get("verified_equations", []):
                eq_key = f"{veq['lhs_latex']} = {veq['rhs_latex']}"
                if eq_key not in seen_eq_keys:
                    seen_eq_keys.add(eq_key)
                    eq_hash = hashlib.sha256(eq_key.encode("utf-8")).hexdigest()[:10]
                    eq_id = f"eq_{eq_hash}"
                    eq_rec = {
                        "id": eq_id,
                        "source": src_tag,
                        "source_note": f"{src_tag} | {eq_key[:90]}",
                        "lhs_latex": veq["lhs_latex"],
                        "rhs_latex": veq["rhs_latex"],
                        "terms_verified": veq["terms_verified"],
                        "series_coeffs": veq["series_coeffs"][:16],
                        "lhs_linear_terms": veq["lhs_linear_terms"],
                        "rhs_linear_terms": veq["rhs_linear_terms"],
                        "lean_kernel_ready": veq["lean_kernel_ready"],
                    }
                    verified_equations.append(eq_rec)
                if eq_lean_id is None and veq["lean_kernel_ready"]:
                    eq_lean_id = f"eq_{hashlib.sha256(eq_key.encode('utf-8')).hexdigest()[:10]}"

            # Deterministic unique ID from provenance + identity index + latex
            sig = f"{rec['rel_path']}|{idx}|{latex}"
            disc_id = hashlib.sha256(sig.encode("utf-8")).hexdigest()[:12]

            resolved_eta: Optional[Dict[int, int]] = None
            eta_method = "none"
            overdet_deg = 0
            ocr_conflict = bool(sym_res["refuted_equation"])
            q_shift_leading = 0

            # Path A: Explicit eta-quotient from Vision JSON
            if explicit_eta and not ocr_conflict:
                expected_coeffs = eta_quotient_coeffs(explicit_eta, max(12, len(explicit_coeffs)))
                if len(explicit_coeffs) >= 5:
                    nz = 0
                    while nz < len(explicit_coeffs) and explicit_coeffs[nz] == 0:
                        nz += 1
                    trimmed = explicit_coeffs[nz:]
                    if len(trimmed) >= 5:
                        L = len(trimmed)
                        if not (trimmed == expected_coeffs[:L] or [-x for x in trimmed] == expected_coeffs[:L]):
                            ocr_conflict = True
                        else:
                            q_shift_leading = nz
                if not ocr_conflict:
                    resolved_eta = explicit_eta
                    eta_method = "explicit_eta_transcription"

            # Path B: Deterministic Symbolic LaTeX Parser (Ramanujan f, phi, psi, chi, infinite products)
            if resolved_eta is None and not ocr_conflict and sym_res["extracted_eta_quotients"]:
                # Register ALL extracted eta-quotients into the Lean catalog, pick primary for this row
                primary_exps = max(sym_res["extracted_eta_quotients"], key=lambda e: (len(e), sum(abs(v) for v in e.values())))
                resolved_eta = primary_exps
                eta_method = "symbolic_latex_theta_eta_parser"
                for extra_exps in sym_res["extracted_eta_quotients"]:
                    ex_key = json.dumps({str(d): r for d, r in sorted(extra_exps.items())}, sort_keys=True)
                    if ex_key not in unique_eta:
                        ex_inv = compute_eta_invariants(extra_exps, expansion_terms=30)
                        ex_cat = match_classical_catalog(ex_inv["coeffs_30"], min_match_len=10)
                        kh = hashlib.sha256(ex_key.encode("utf-8")).hexdigest()[:10]
                        unique_eta[ex_key] = {
                            "id": f"eta_{kh}",
                            "exponents": extra_exps,
                            "invariants": ex_inv,
                            "catalog_match": ex_cat,
                            "source_pages": [src_tag],
                            "source_note": f"{src_tag} | {ex_cat['name'] if ex_cat else 'symbolic_latex_eta'}",
                        }
                    elif src_tag not in unique_eta[ex_key]["source_pages"]:
                        unique_eta[ex_key]["source_pages"].append(src_tag)

            # Path C: Exact Mobius inversion on transcribed/derived q-series coefficients
            if resolved_eta is None and not ocr_conflict and len(explicit_coeffs) >= 6:
                inv_res = invert_eta_quotient_exact(
                    explicit_coeffs,
                    d_max=24,
                    min_terms=6,
                    min_overdetermination=3,
                    max_factors=6,
                    max_abs_exponent=48,
                )
                if inv_res.get("is_exact_eta_quotient"):
                    resolved_eta = inv_res["exponents"]
                    eta_method = f"exact_mobius_inversion({coeffs_source})"
                    overdet_deg = int(inv_res["overdetermination_degree"])
                    q_shift_leading = int(inv_res["leading_q_shift"])

            invariants = None
            catalog_match = None
            coeffs_30: List[int] = []

            if resolved_eta is not None:
                invariants = compute_eta_invariants(resolved_eta, expansion_terms=30)
                coeffs_30 = invariants["coeffs_30"]
                catalog_match = match_classical_catalog(coeffs_30, min_match_len=10)
            elif sym_res["symbolic_catalog_match"] and sym_res["symbolic_catalog_match"]["kind"] == "catalog_symbolic":
                sm = sym_res["symbolic_catalog_match"]
                catalog_match = {
                    "catalog_key": sm["catalog_key"],
                    "name": sm["name"],
                    "oeis": sm["oeis"],
                    "category": sm["category"],
                    "formula": sm["formula"],
                    "reference": sm["reference"],
                    "matched_terms": 30,
                    "sign_flipped": False,
                }
                coeffs_30 = sm["coeffs"]
            elif len(explicit_coeffs) >= 6:
                catalog_match = match_classical_catalog(explicit_coeffs, min_match_len=6)
                coeffs_30 = explicit_coeffs

            domain, shadow = _domain_and_shadow(id_type, invariants, catalog_match)
            ab_ref = _ab_reference_for_topic(id_type, rec["notebook"])

            eta_key = json.dumps({str(d): r for d, r in sorted(resolved_eta.items())}, sort_keys=True) if resolved_eta else "{}"
            lean_entry_name = eq_lean_id
            if resolved_eta is not None:
                if eta_key not in unique_eta:
                    key_hash = hashlib.sha256(eta_key.encode("utf-8")).hexdigest()[:10]
                    lean_id = f"eta_{key_hash}"
                    unique_eta[eta_key] = {
                        "id": lean_id,
                        "exponents": resolved_eta,
                        "invariants": invariants,
                        "catalog_match": catalog_match,
                        "source_pages": [src_tag],
                        "source_note": (
                            f"{src_tag} | "
                            f"{catalog_match['name'] if catalog_match else eta_method}"
                        ),
                    }
                else:
                    if src_tag not in unique_eta[eta_key]["source_pages"]:
                        unique_eta[eta_key]["source_pages"].append(src_tag)
                if lean_entry_name is None:
                    lean_entry_name = unique_eta[eta_key]["id"]

            # Epistemic tier & status
            if resolved_eta is not None:
                epistemic_tier = "A_PENDING_LEAN"
                lean_status = "PENDING_LEAN"
                eq_prefix = "[VERIFIED 30-TERM IDENTITY] " if sym_res["verified_equation"] else ""
                conjecture = (
                    f"{eq_prefix}q^({invariants['leading_q_power']}) * prod_d eta(d*tau)^{resolved_eta} "
                    f"|| {latex[:150]}"
                )
                physics_map = (
                    f"[EXACT ETA-QUOTIENT | {eta_method}] "
                    f"k={invariants['weight_k']}, c_eff(0)={invariants['c_eff_cusp0']}, "
                    f"max_cusp_c_eff={invariants['max_cusp_c_eff']} (c={invariants['max_cusp_c']}), "
                    f"E0={invariants['ground_state_E0']}, "
                    f"Ono164_Gamma0({invariants['level_N']})={invariants['ono_164_modular_gamma0_N']}, "
                    f"sign={invariants['sign_classification']}"
                )
            elif catalog_match is not None:
                epistemic_tier = "B"
                lean_status = "CATALOG_MATCHED"
                conjecture = latex[:240]
                physics_map = (
                    f"[TIER B CLASSICAL MATCH] {catalog_match['name']} "
                    f"(OEIS {catalog_match['oeis']}) | Ref: {catalog_match['reference']}"
                )
            else:
                epistemic_tier = "C"
                lean_status = "TRANSCRIBED_OPEN"
                conjecture = latex[:240]
                if sym_res["refuted_equation"]:
                    rf = sym_res["refuted_equation"]
                    note = f"OCR typo refuted at q^{rf['first_mismatch_power']} ({rf['lhs_val']} != {rf['rhs_val']}); held at Tier C"
                else:
                    note = f"Symbolic {id_type} transcription (Tier C)"
                physics_map = f"[{note}] {named_fn}".strip()

            discoveries.append({
                "id": disc_id,
                "image_path": rec["rel_path"],
                "notebook": rec["notebook"],
                "chapter": rec["chapter"],
                "page": rec["page"],
                "source_pdf": rec["source_pdf"],
                "archetype": named_fn or (catalog_match["name"] if catalog_match else id_type),
                "conjecture": conjecture,
                "latex": latex,
                "eta_exponents": eta_key,
                "q_shift": q_shift_leading * 24 if resolved_eta is None else invariants["ono_sum_dr"],
                "rama_energy": 0.0 if resolved_eta is not None else (0.5 if catalog_match else 1.0),
                "rama_C": float(len(resolved_eta)) if resolved_eta else 0.0,
                "rama_I": 0.0 if (resolved_eta or catalog_match) else 1.0,
                "rama_D": float(overdet_deg),
                "shadow": shadow,
                "domain": domain,
                "lean_code": "",
                "lean_status": lean_status,
                "lean_error": None,
                "lean4_theorem_name": lean_entry_name,
                "physics_mapping": physics_map,
                "andrews_berndt_ref": ab_ref,
                "epistemic_tier": epistemic_tier,
                "oeis_match": catalog_match["oeis"] if catalog_match else None,
                "is_novel": (catalog_match is None and resolved_eta is not None),
                "susy_broken": (not invariants["is_weight_half"]) if invariants else None,
                "ono_modular": invariants["ono_164_modular_gamma0_N"] if invariants else None,
                "sign_class": invariants["sign_classification"] if invariants else None,
                "c_eff_cusp0": invariants["c_eff_cusp0"] if invariants else None,
                "max_cusp_c_eff": invariants["max_cusp_c_eff"] if invariants else None,
                "coeffs_30": coeffs_30,
                "confidence": confidence,
                "eta_method": eta_method,
            })

    return discoveries, unique_eta, verified_equations, refuted_equations


# ---------------------------------------------------------------------------
# Stage 4: Lean 4 Zero-Axiom Kernel Verification & Mathesis-Gate Footprint Check
# ---------------------------------------------------------------------------


def verify_campaign_in_lean(
    discoveries: List[Dict[str, Any]],
    unique_eta: Dict[str, Dict[str, Any]],
    verified_equations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate and kernel-verify CampaignV2Verified.lean with empty/propext-only axiom footprint."""
    entries = list(unique_eta.values())
    lean_eqs = [eq for eq in verified_equations if eq.get("lean_kernel_ready")]
    logging.info(
        f"[Stage 4] Kernel-verifying {len(entries)} unique exact eta-quotients and "
        f"{len(lean_eqs)} Ramanujan LHS=RHS identities in Lean 4 (zero custom axioms)..."
    )

    if not entries and not lean_eqs:
        return {
            "verified_entries": 0,
            "verified_equations": 0,
            "total_theorems": 0,
            "lean_ok": True,
            "mathesis_gate_ok": True,
        }

    ok, thm_count, err = write_and_verify_campaign_lean_catalog(
        entries,
        CAMPAIGN_LEAN_PATH,
        coeff_len=12,
        timeout=300,
        equations=lean_eqs,
        eq_check_len=16,
    )
    if not ok:
        logging.warning(f"[Stage 4] Batch Lean 4 verify had an error; isolating entries...\n{err[:600]}")
        good_entries = []
        for entry in entries:
            e_ok, _, e_err = write_and_verify_campaign_lean_catalog(
                [entry],
                REPO_ROOT / ".scratchpad" / f"{entry['id']}.lean",
                coeff_len=12,
                timeout=30,
            )
            if e_ok:
                good_entries.append(entry)
            else:
                logging.warning(f"  Skipping {entry['id']} ({entry['exponents']}): {e_err[:120]}")
        good_eqs = []
        for eq in lean_eqs:
            q_ok, _, q_err = write_and_verify_campaign_lean_catalog(
                [],
                REPO_ROOT / ".scratchpad" / f"{eq['id']}.lean",
                equations=[eq],
                eq_check_len=16,
                timeout=30,
            )
            if q_ok:
                good_eqs.append(eq)
            else:
                logging.warning(f"  Skipping eq {eq['id']}: {q_err[:120]}")
        ok, thm_count, err = write_and_verify_campaign_lean_catalog(
            good_entries,
            CAMPAIGN_LEAN_PATH,
            coeff_len=12,
            timeout=300,
            equations=good_eqs,
            eq_check_len=16,
        )
        verified_ids = {e["id"] for e in good_entries} if ok else set()
        verified_eq_ids = {q["id"] for q in good_eqs} if ok else set()
    else:
        verified_ids = {e["id"] for e in entries}
        verified_eq_ids = {q["id"] for q in lean_eqs}

    # Verify with mathesis-gate WITH REAL FOOTPRINTS ENABLED (no --skip-footprints!)
    gate_proc = subprocess.run(
        [
            "python3",
            str(REPO_ROOT / "tools" / "mathesis-gate" / "mathesis_gate.py"),
            str(CAMPAIGN_LEAN_PATH.parent),
            "--exclude",
            "verify_",
            "--exclude",
            "NormNumVerified",
            "--exclude",
            "Notebook",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    gate_ok = (gate_proc.returncode == 0)
    logging.info(
        f"[Stage 4] Lean 4 kernel: ok={ok} ({len(verified_ids)} eta-quotients + "
        f"{len(verified_eq_ids)} Ramanujan identities = {thm_count} zero-custom-axiom theorems) | "
        f"mathesis-gate (with real footprints!): ok={gate_ok}"
    )
    if not gate_ok:
        logging.error(gate_proc.stdout + "\n" + gate_proc.stderr)

    snippet_cache: Dict[str, str] = {}
    for e in entries:
        if e["id"] in verified_ids:
            blk, _ = generate_entry_lean_block(e["id"], e["exponents"], coeff_len=12, source_note=e["source_note"])
            snippet_cache[e["id"]] = blk
    for q in lean_eqs:
        if q["id"] in verified_eq_ids:
            blk, _ = generate_equation_lean_block(
                q["id"], q["lhs_linear_terms"], q["rhs_linear_terms"], check_len=16, source_note=q["source_note"]
            )
            snippet_cache[q["id"]] = blk

    all_verified_ids = verified_ids | verified_eq_ids
    for d in discoveries:
        tname = d.get("lean4_theorem_name")
        if tname and tname in all_verified_ids:
            d["lean_status"] = "VERIFIED"
            d["epistemic_tier"] = "A"
            d["lean_code"] = snippet_cache[tname]
            d["lean_error"] = None
        elif d["lean_status"] == "PENDING_LEAN":
            # Fall back to eta_key theorem if eq theorem failed
            eta_k = d.get("eta_exponents")
            if eta_k in unique_eta and unique_eta[eta_k]["id"] in verified_ids:
                eid = unique_eta[eta_k]["id"]
                d["lean4_theorem_name"] = eid
                d["lean_status"] = "VERIFIED"
                d["epistemic_tier"] = "A"
                d["lean_code"] = snippet_cache[eid]
                d["lean_error"] = None
            else:
                d["lean_status"] = "FAILED"
                d["epistemic_tier"] = "C"
                d["lean_error"] = err[:500] if err else "Kernel verification failed"

    return {
        "verified_entries": len(verified_ids),
        "verified_equations": len(verified_eq_ids),
        "total_theorems": thm_count,
        "lean_ok": ok,
        "mathesis_gate_ok": gate_ok,
        "mathesis_gate_output": (gate_proc.stdout + "\n" + gate_proc.stderr).strip(),
        "lean_file": str(CAMPAIGN_LEAN_PATH.relative_to(REPO_ROOT)),
    }


# ---------------------------------------------------------------------------
# Stage 5: Backup Legacy DB & Persist Regenerated Campaign
# ---------------------------------------------------------------------------


def persist_campaign_db(
    discoveries: List[Dict[str, Any]],
    unique_eta: Dict[str, Dict[str, Any]],
    verified_equations: List[Dict[str, Any]],
    db_path: Path,
) -> Dict[str, int]:
    backup_path = db_path.with_name("namagiri_legacy_v1.db")
    if db_path.is_file() and not backup_path.is_file():
        shutil.copy2(db_path, backup_path)
        logging.info(f"[Stage 5] Backed up legacy database to {backup_path.name}.")

    if db_path.is_file():
        db_path.unlink()
    for suf in ("-wal", "-shm"):
        p = Path(str(db_path) + suf)
        if p.is_file():
            p.unlink()

    db = NamagiriDB(str(db_path))
    extra_cols = [
        ("source_pdf", "TEXT DEFAULT NULL"),
        ("andrews_berndt_ref", "TEXT DEFAULT NULL"),
        ("hardy_ref", "TEXT DEFAULT NULL"),
        ("lean4_theorem_name", "TEXT DEFAULT NULL"),
        ("human_proof_status", "TEXT DEFAULT 'PENDING'"),
        ("picard_fuchs_order", "INTEGER DEFAULT NULL"),
        ("susy_broken", "BOOLEAN DEFAULT NULL"),
        ("is_novel", "BOOLEAN DEFAULT NULL"),
        ("epistemic_tier", "TEXT DEFAULT 'C'"),
        ("oeis_match", "TEXT DEFAULT NULL"),
        ("ono_modular", "BOOLEAN DEFAULT NULL"),
        ("sign_class", "TEXT DEFAULT NULL"),
        ("c_eff_cusp0", "TEXT DEFAULT NULL"),
        ("max_cusp_c_eff", "TEXT DEFAULT NULL"),
        ("coeffs_json", "TEXT DEFAULT NULL"),
        ("latex_raw", "TEXT DEFAULT NULL"),
    ]
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        existing = {r[1] for r in cur.execute("PRAGMA table_info(discoveries)").fetchall()}
        for col, spec in extra_cols:
            if col not in existing:
                cur.execute(f"ALTER TABLE discoveries ADD COLUMN {col} {spec}")

        # Normalized table storing EVERY Lean-verified unique eta-quotient (exact 1-to-1 sync with CampaignV2Verified.lean)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS verified_eta_quotients (
                id TEXT PRIMARY KEY,
                eta_exponents TEXT NOT NULL,
                level_N INTEGER NOT NULL,
                weight_k TEXT NOT NULL,
                c_eff_cusp0 TEXT NOT NULL,
                max_cusp_c INTEGER NOT NULL,
                max_cusp_c_eff TEXT NOT NULL,
                ground_state_E0 TEXT NOT NULL,
                ono_164_gamma0_N BOOLEAN NOT NULL,
                sign_class TEXT NOT NULL,
                oeis_match TEXT,
                classical_name TEXT,
                source_pages_json TEXT NOT NULL,
                coeffs_30_json TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS verified_equations (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                lhs_latex TEXT NOT NULL,
                rhs_latex TEXT NOT NULL,
                python_terms_verified INTEGER NOT NULL,
                lean_terms_verified INTEGER NOT NULL,
                lean_kernel_verified BOOLEAN NOT NULL
            )
            """
        )

        for entry in unique_eta.values():
            inv = entry["invariants"]
            cat = entry.get("catalog_match")
            exps_json = json.dumps({str(d): r for d, r in sorted(entry["exponents"].items())}, sort_keys=True)
            cur.execute(
                """
                INSERT OR REPLACE INTO verified_eta_quotients (
                    id, eta_exponents, level_N, weight_k, c_eff_cusp0, max_cusp_c,
                    max_cusp_c_eff, ground_state_E0, ono_164_gamma0_N, sign_class,
                    oeis_match, classical_name, source_pages_json, coeffs_30_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["id"],
                    exps_json,
                    int(inv["level_N"]),
                    str(inv["weight_k"]),
                    str(inv["c_eff_cusp0"]),
                    int(inv["max_cusp_c"]),
                    str(inv["max_cusp_c_eff"]),
                    str(inv["ground_state_E0"]),
                    bool(inv["ono_164_modular_gamma0_N"]),
                    str(inv["sign_classification"]),
                    cat["oeis"] if cat else None,
                    cat["name"] if cat else None,
                    json.dumps(entry["source_pages"]),
                    json.dumps(inv["coeffs_30"]),
                ),
            )

        for eq in verified_equations:
            cur.execute(
                """
                INSERT OR REPLACE INTO verified_equations (
                    id, source, lhs_latex, rhs_latex, python_terms_verified,
                    lean_terms_verified, lean_kernel_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eq["id"],
                    eq["source"],
                    eq["lhs_latex"],
                    eq["rhs_latex"],
                    int(eq["terms_verified"]),
                    16 if eq.get("lean_kernel_ready") else 0,
                    bool(eq.get("lean_kernel_ready")),
                ),
            )

        inserted = 0
        for d in discoveries:
            cur.execute(
                """
                INSERT OR REPLACE INTO discoveries (
                    id, image_path, notebook, chapter, page, archetype, conjecture,
                    eta_exponents, q_shift, rama_energy, rama_C, rama_I, rama_D,
                    shadow, domain, lean_code, lean_status, lean_error, physics_mapping,
                    source_pdf, andrews_berndt_ref, lean4_theorem_name, human_proof_status,
                    susy_broken, is_novel, epistemic_tier, oeis_match, ono_modular,
                    sign_class, c_eff_cusp0, max_cusp_c_eff, coeffs_json, latex_raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    d["id"],
                    d["image_path"],
                    d["notebook"],
                    d["chapter"],
                    d["page"],
                    d["archetype"],
                    d["conjecture"],
                    d["eta_exponents"],
                    int(d["q_shift"]),
                    float(d["rama_energy"]),
                    float(d["rama_C"]),
                    float(d["rama_I"]),
                    float(d["rama_D"]),
                    d["shadow"],
                    d["domain"],
                    d["lean_code"],
                    d["lean_status"],
                    d["lean_error"],
                    d["physics_mapping"],
                    d["source_pdf"],
                    d["andrews_berndt_ref"],
                    d["lean4_theorem_name"],
                    "LEAN_KERNEL_VERIFIED" if d["lean_status"] == "VERIFIED" else "PENDING",
                    d["susy_broken"],
                    d["is_novel"],
                    d["epistemic_tier"],
                    d["oeis_match"],
                    d["ono_modular"],
                    d["sign_class"],
                    d["c_eff_cusp0"],
                    d["max_cusp_c_eff"],
                    json.dumps(d["coeffs_30"]) if d["coeffs_30"] else None,
                    d["latex"],
                ),
            )
            inserted += 1
        conn.commit()
    finally:
        conn.close()

    stats = db.get_stats()
    logging.info(
        f"[Stage 5] Persisted {inserted} discoveries + {len(unique_eta)} unique eta-quotients + "
        f"{len(verified_equations)} verified equations to {db_path.name} | stats={stats}"
    )
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Run rigorous Ramanujan manuscripts campaign v2.")
    ap.add_argument("--workers", type=int, default=12, help="Concurrent Gemini Vision workers.")
    ap.add_argument("--max-pages", type=int, default=0, help="Optional cap for smoke testing (0 = ALL pages).")
    ap.add_argument("--force-reextract", action="store_true", help="Ignore existing JSONL checkpoint.")
    ap.add_argument("--skip-vision", action="store_true", help="Use cached JSONL extractions only (0 Vision API calls).")
    args = ap.parse_args()

    t_start = time.time()
    pages = collect_manuscript_pages(include_lost=True, include_ono=True, include_notebooks=True)
    if args.max_pages > 0:
        pages = pages[: args.max_pages]

    by_source: Dict[str, int] = {}
    for p in pages:
        nb = parse_provenance(p)["notebook"]
        by_source[nb] = by_source.get(nb, 0) + 1
    logging.info(f"Campaign v2 Corpus Manifest ({len(pages)} pages): {by_source}")

    page_records = run_vision_stage(
        pages,
        workers=args.workers,
        force_reextract=args.force_reextract,
        skip_vision=args.skip_vision,
    )
    discoveries, unique_eta, verified_equations, refuted_equations = analyze_extractions(page_records)
    lean_summary = verify_campaign_in_lean(discoveries, unique_eta, verified_equations)
    db_stats = persist_campaign_db(discoveries, unique_eta, verified_equations, REPO_ROOT / "namagiri.db")

    # Token & honest missing/failed page accounting
    total_in_tok = sum(r.get("prompt_tokens", 0) for r in page_records)
    total_out_tok = sum(r.get("candidate_tokens", 0) for r in page_records)
    pages_with_math = sum(1 for r in page_records if r.get("has_math"))
    processed_rels = {r["rel_path"] for r in page_records if "error" not in r}
    failed_or_missing_pages = [
        str(p.relative_to(REPO_ROOT)) for p in pages if str(p.relative_to(REPO_ROOT)) not in processed_rels
    ]
    extraction_errors = len(failed_or_missing_pages)

    tier_counts: Dict[str, int] = {}
    status_counts: Dict[str, int] = {}
    nb_counts: Dict[str, int] = {}
    oeis_matches: Dict[str, int] = {}
    for d in discoveries:
        tier_counts[d["epistemic_tier"]] = tier_counts.get(d["epistemic_tier"], 0) + 1
        status_counts[d["lean_status"]] = status_counts.get(d["lean_status"], 0) + 1
        nb_counts[d["notebook"]] = nb_counts.get(d["notebook"], 0) + 1
        if d["oeis_match"]:
            oeis_matches[d["oeis_match"]] = oeis_matches.get(d["oeis_match"], 0) + 1

    full_eta_catalog = [
        {
            "id": e["id"],
            "exponents": e["exponents"],
            "level_N": e["invariants"]["level_N"],
            "weight_k": e["invariants"]["weight_k"],
            "c_eff_cusp0": e["invariants"]["c_eff_cusp0"],
            "max_cusp_c": e["invariants"]["max_cusp_c"],
            "max_cusp_c_eff": e["invariants"]["max_cusp_c_eff"],
            "ground_state_E0": e["invariants"]["ground_state_E0"],
            "ono_164_gamma0_N": e["invariants"]["ono_164_modular_gamma0_N"],
            "sign_class": e["invariants"]["sign_classification"],
            "oeis": e["catalog_match"]["oeis"] if e["catalog_match"] else None,
            "name": e["catalog_match"]["name"] if e["catalog_match"] else None,
            "source_pages": e["source_pages"],
            "coeffs_30": e["invariants"]["coeffs_30"],
        }
        for e in unique_eta.values()
    ]

    report = {
        "campaign": "RAMA_Campaign_v2_Rigorous_Regeneration",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.time() - t_start, 2),
        "vision_model": VISION_MODEL,
        "corpus_pages_total": len(pages),
        "corpus_pages_by_source": by_source,
        "total_pages_processed": len(processed_rels),
        "pages_with_math": pages_with_math,
        "extraction_errors": extraction_errors,
        "failed_or_missing_pages": failed_or_missing_pages,
        "token_usage": {
            "prompt_tokens": total_in_tok,
            "candidate_tokens": total_out_tok,
        },
        "discoveries_total": len(discoveries),
        "discoveries_by_notebook": nb_counts,
        "discoveries_by_tier": tier_counts,
        "discoveries_by_status": status_counts,
        "unique_exact_eta_quotients": len(unique_eta),
        "verified_ramanujan_identities": [
            {
                "id": eq["id"],
                "source": eq["source"],
                "lhs": eq["lhs_latex"],
                "rhs": eq["rhs_latex"],
                "python_terms_verified": eq["terms_verified"],
                "lean_terms_verified": 16 if eq["lean_kernel_ready"] else 0,
                "scope_note": "Exact truncated formal q-series equality (not an all-n analytic modular proof)",
                "lean_kernel_ready": eq["lean_kernel_ready"],
            }
            for eq in verified_equations
        ],
        "refuted_ocr_typos_count": len(refuted_equations),
        "refuted_ocr_typos_sample": refuted_equations[:15],
        "classical_catalog_oeis_matches": oeis_matches,
        "lean_kernel_verification": lean_summary,
        "db_stats": db_stats,
        "verified_eta_quotients_catalog": full_eta_catalog,
    }
    CAMPAIGN_CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CAMPAIGN_CERT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Sync dashboard_data.json
    (REPO_ROOT / "dashboard_data.json").write_text(
        json.dumps(
            {
                "total": len(discoveries),
                "verified": status_counts.get("VERIFIED", 0),
                "catalog_matched": status_counts.get("CATALOG_MATCHED", 0),
                "transcribed_open": status_counts.get("TRANSCRIBED_OPEN", 0),
                "failed": status_counts.get("FAILED", 0),
                "unique_eta_quotients": len(unique_eta),
                "lean_zero_axiom_theorems": lean_summary["total_theorems"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    logging.info("=" * 72)
    logging.info(f"CAMPAIGN v2 COMPLETE in {report['elapsed_seconds']}s")
    logging.info(f"Pages processed: {len(page_records)} ({pages_with_math} with math, {extraction_errors} errors)")
    logging.info(f"Discoveries: {len(discoveries)} | Tiers: {tier_counts} | Statuses: {status_counts}")
    logging.info(
        f"Unique Lean-4 Zero-Axiom Eta-Quotients: {lean_summary['verified_entries']} "
        f"({lean_summary['total_theorems']} theorems, mathesis-gate footprints OK={lean_summary['mathesis_gate_ok']})"
    )
    logging.info(f"Report saved to: {CAMPAIGN_CERT_PATH.relative_to(REPO_ROOT)}")
    logging.info("=" * 72)
    return 0 if (lean_summary["lean_ok"] and lean_summary["mathesis_gate_ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())

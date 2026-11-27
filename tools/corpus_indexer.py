#!/usr/bin/env python3
"""
Corpus Index Builder (v2)
Builds corpus_index.json covering LostNotebook_Narosa_1988, Ono_Letters,
NoteBook1, NoteBook2, NoteBook3, and reference PDFs.
"""

import glob
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_corpus_index() -> dict:
    index: dict = {"notebooks": {}, "total_pages": 0, "reference_pdfs": []}

    for pdf in sorted((ROOT / "inputs").glob("*.pdf")):
        index["reference_pdfs"].append({
            "filename": pdf.name,
            "size_bytes": pdf.stat().st_size,
            "rel_path": str(pdf.relative_to(ROOT)),
        })

    # Lost Notebook rendered facsimile
    lost_dir = ROOT / "input" / "LostNotebook_Narosa_1988" / "images"
    if lost_dir.is_dir():
        lost_pages = sorted(lost_dir.glob("*.jpg"))
        index["notebooks"]["LostNotebook_1988"] = {
            "chapters": {"Narosa_1988_PDF_p37_to_p169": {"page_count": len(lost_pages), "pages": [p.name for p in lost_pages]}},
            "total_pages": len(lost_pages),
        }
        index["total_pages"] += len(lost_pages)

    # Ono Letters scans
    ono_pages = sorted((ROOT / "inputs").glob("6-ramanujans-letters-from-ono-*.png"))
    if ono_pages:
        index["notebooks"]["Ono_Letters"] = {
            "chapters": {"Letters": {"page_count": len(ono_pages), "pages": [p.name for p in ono_pages]}},
            "total_pages": len(ono_pages),
        }
        index["total_pages"] += len(ono_pages)

    # Notebooks 1, 2, 3
    for nb_name in ("NoteBook1", "NoteBook2", "NoteBook3"):
        nb_dir = ROOT / "input" / nb_name
        if not nb_dir.is_dir():
            continue
        nb_entry: dict = {"chapters": {}, "total_pages": 0}
        chapter_dirs = sorted(p for p in nb_dir.glob("chapter*") if p.is_dir())
        if not chapter_dirs:
            img_dir = nb_dir / "images"
            pages = sorted(img_dir.glob("*.jpg")) if img_dir.is_dir() else []
            nb_entry["chapters"]["direct"] = {"page_count": len(pages), "pages": [p.name for p in pages]}
            nb_entry["total_pages"] = len(pages)
        else:
            for ch_dir in chapter_dirs:
                img_dir = ch_dir / "images"
                pages = sorted(img_dir.glob("*.jpg")) if img_dir.is_dir() else []
                nb_entry["chapters"][ch_dir.name] = {"page_count": len(pages), "pages": [p.name for p in pages]}
                nb_entry["total_pages"] += len(pages)
        index["notebooks"][nb_name] = nb_entry
        index["total_pages"] += nb_entry["total_pages"]

    out_path = ROOT / "corpus_index.json"
    out_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Built corpus_index.json: {index['total_pages']} total pages across {len(index['notebooks'])} manuscript collections.")
    return index


if __name__ == "__main__":
    build_corpus_index()

#!/usr/bin/env python3
"""
Task 0.3 + 0.4: Corpus Index Builder & Cross-Reference Linker
Builds corpus_index.json from manuscript page images and populates
the lean4_theorem_name + source_pdf columns in namagiri.db.
"""
import sqlite3
import json
import os
import glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
DB = os.path.join(ROOT, 'namagiri.db')

# ═══════════════════════════════════════════════════════════════════════════════
# Task 0.3: Build corpus index from page images
# ═══════════════════════════════════════════════════════════════════════════════
def build_corpus_index():
    """Scan all notebook page images and build a structured index."""
    index = {"notebooks": {}, "total_pages": 0, "reference_pdfs": []}
    
    # Reference PDFs
    for pdf in sorted(glob.glob(os.path.join(ROOT, "inputs", "*.pdf"))):
        index["reference_pdfs"].append({
            "filename": os.path.basename(pdf),
            "size_bytes": os.path.getsize(pdf),
            "path": pdf
        })
    
    # Notebook page images
    for nb_dir in sorted(glob.glob(os.path.join(ROOT, "input", "NoteBook*"))):
        nb_name = os.path.basename(nb_dir)
        nb_entry = {"chapters": {}, "total_pages": 0}
        
        # Find chapter dirs (or direct images for NB3)
        chapter_dirs = sorted(glob.glob(os.path.join(nb_dir, "chapter*")))
        if not chapter_dirs:
            # NoteBook3 has images/ directly
            img_dir = os.path.join(nb_dir, "images")
            if os.path.isdir(img_dir):
                pages = sorted(glob.glob(os.path.join(img_dir, "*.jpg")))
                nb_entry["chapters"]["direct"] = {
                    "page_count": len(pages),
                    "pages": [os.path.basename(p) for p in pages]
                }
                nb_entry["total_pages"] = len(pages)
        else:
            for ch_dir in chapter_dirs:
                ch_name = os.path.basename(ch_dir)
                img_dir = os.path.join(ch_dir, "images")
                if os.path.isdir(img_dir):
                    pages = sorted(glob.glob(os.path.join(img_dir, "*.jpg")))
                    nb_entry["chapters"][ch_name] = {
                        "page_count": len(pages),
                        "pages": [os.path.basename(p) for p in pages]
                    }
                    nb_entry["total_pages"] += len(pages)
        
        index["notebooks"][nb_name] = nb_entry
        index["total_pages"] += nb_entry["total_pages"]
    
    # Andrews-Berndt mapping (by part)
    index["andrews_berndt_mapping"] = {
        "Part_I_2005": {
            "pdf": "Ramanujan_39_s_Lost_Notebook_Part_I_2005.pdf",
            "topics": ["Mock theta functions", "Partial fractions", "Hadamard products",
                       "Integrals", "Incomplete elliptic integrals", "Infinite series"]
        },
        "Part_II_2008": {
            "pdf": "Ramanujan_39_s_Lost_Notebook_Part_II_2008.pdf",
            "topics": ["q-series", "Eisenstein series", "Modular equations",
                       "Lambert series", "Theta functions"]
        },
        "Part_III_2012": {
            "pdf": "Ramanujan_39_s_Lost_Notebook_Part_III_2012.pdf",
            "topics": ["q-continued fractions", "Rogers-Ramanujan identities",
                       "Diophantine approximation", "Partitions"]
        },
        "Part_IV_2013": {
            "pdf": "Ramanujan_39_s_Lost_Notebook_Part_IV_2013.pdf",
            "topics": ["Location of zeros", "Class invariants",
                       "Ramanujan-Weber class invariants", "Modular equations of degrees 3,5,7"]
        }
    }
    
    out_path = os.path.join(ROOT, "corpus_index.json")
    with open(out_path, "w") as f:
        json.dump(index, f, indent=2)
    
    print(f"=== Task 0.3: Corpus Index ===")
    print(f"  Total pages: {index['total_pages']}")
    for nb, data in index["notebooks"].items():
        print(f"  {nb}: {data['total_pages']} pages, {len(data['chapters'])} chapters")
    print(f"  Reference PDFs: {len(index['reference_pdfs'])}")
    print(f"  Saved: {out_path}")
    return index


# ═══════════════════════════════════════════════════════════════════════════════
# Task 0.4: Cross-Reference Linker — populate DB columns
# ═══════════════════════════════════════════════════════════════════════════════
def cross_reference_linker():
    """Link each discovery to its source PDF and generate lean4_theorem_name."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Get all discoveries
    c.execute("""SELECT id, image_path, notebook, chapter, page, eta_exponents, 
                        lean_status, physics_mapping
                 FROM discoveries""")
    rows = c.fetchall()
    
    updated = 0
    for row in rows:
        did, img_path, notebook, chapter, page, eta_exp, lean_status, physics = row
        
        # Generate lean4_theorem_name from discovery id
        short_id = did[:11] if did and len(did) >= 11 else did
        theorem_name = f"verify_{short_id}" if short_id else None
        
        # Determine source_pdf from notebook
        source_pdf = None
        if notebook and "1" in str(notebook):
            source_pdf = "NoteBook1"
        elif notebook and "2" in str(notebook):
            source_pdf = "NoteBook2"
        elif notebook and "3" in str(notebook):
            source_pdf = "NoteBook3"
        elif img_path:
            if "NoteBook1" in str(img_path):
                source_pdf = "NoteBook1"
            elif "NoteBook2" in str(img_path):
                source_pdf = "NoteBook2"
            elif "NoteBook3" in str(img_path):
                source_pdf = "NoteBook3"
        
        # Determine human_proof_status
        human_status = "PENDING"
        if lean_status == "VERIFIED":
            human_status = "LEAN_VERIFIED_HUMAN_PENDING"
        
        c.execute("""UPDATE discoveries 
                     SET lean4_theorem_name = ?,
                         source_pdf = ?,
                         human_proof_status = ?
                     WHERE id = ?""",
                  (theorem_name, source_pdf, human_status, did))
        updated += 1
    
    conn.commit()
    
    # Verification
    c.execute("SELECT COUNT(*) FROM discoveries WHERE lean4_theorem_name IS NOT NULL")
    named = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM discoveries WHERE source_pdf IS NOT NULL")
    sourced = c.fetchone()[0]
    c.execute("SELECT source_pdf, COUNT(*) FROM discoveries WHERE source_pdf IS NOT NULL GROUP BY source_pdf")
    by_nb = c.fetchall()
    
    conn.close()
    
    print(f"\n=== Task 0.4: Cross-Reference Linker ===")
    print(f"  Updated: {updated} discoveries")
    print(f"  With theorem name: {named}")
    print(f"  With source PDF: {sourced}")
    for nb, cnt in by_nb:
        print(f"    {nb}: {cnt}")
    print(f"=== Task 0.4: DONE ===")


if __name__ == "__main__":
    build_corpus_index()
    cross_reference_linker()

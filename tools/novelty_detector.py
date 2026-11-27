"""
Exact catalog-based novelty & OEIS cross-reference classifier on namagiri.db.
Replaces the legacy dummy `len(coeffs) % 2 != 0` placeholder with exact
30-term integer sequence matching against `src.math_engine.exact_qseries.CLASSICAL_CATALOG`.

Epistemic note: `is_novel = 1` means "UNMATCHED_IN_LOCAL_CLASSICAL_CATALOG"
(a candidate for further OEIS lookup), NOT a proof of absolute absence from OEIS.
"""

import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.math_engine.exact_qseries import eta_quotient_coeffs, match_classical_catalog

DB_PATH = REPO_ROOT / "namagiri.db"


def run(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        c = conn.cursor()
        cols = [row[1] for row in c.execute("PRAGMA table_info(discoveries)").fetchall()]
        if "is_novel" not in cols:
            c.execute("ALTER TABLE discoveries ADD COLUMN is_novel BOOLEAN")
        if "oeis_match" not in cols:
            c.execute("ALTER TABLE discoveries ADD COLUMN oeis_match TEXT DEFAULT NULL")

        rows = c.execute(
            "SELECT id, eta_exponents, coeffs_json FROM discoveries"
        ).fetchall()

        updates = []
        matched = 0
        unmatched_eta = 0
        for id_, eta_str, coeffs_json in rows:
            seq = []
            has_eta = False
            if eta_str and eta_str != "{}":
                try:
                    raw = json.loads(eta_str)
                    exps = {int(k): int(v) for k, v in raw.items() if int(k) > 0 and int(v) != 0}
                    if exps:
                        has_eta = True
                        seq = eta_quotient_coeffs(exps, 30)
                except (ValueError, TypeError, json.JSONDecodeError):
                    seq = []
            elif coeffs_json:
                try:
                    seq = json.loads(coeffs_json)
                except json.JSONDecodeError:
                    seq = []

            match = match_classical_catalog(seq, min_match_len=6) if len(seq) >= 6 else None
            if match:
                matched += 1
                updates.append((False, match["oeis"], id_))
            elif has_eta:
                unmatched_eta += 1
                updates.append((True, None, id_))
            else:
                updates.append((False, None, id_))

        c.executemany("UPDATE discoveries SET is_novel = ?, oeis_match = ? WHERE id = ?", updates)
        conn.commit()
    finally:
        conn.close()

    print(
        f"Exact catalog cross-check complete ({len(updates)} rows): "
        f"{matched} exact classical/OEIS matches | {unmatched_eta} unmatched exact eta-quotient candidates."
    )


if __name__ == "__main__":
    run()

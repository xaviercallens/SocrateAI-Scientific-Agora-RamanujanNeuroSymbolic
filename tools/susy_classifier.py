"""Exact Fraction weight classification (k = 1/2 vs k != 1/2) on namagiri.db."""

from fractions import Fraction
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "namagiri.db"


def compute_mod_weight(factors_json: str) -> Fraction | None:
    try:
        factors = json.loads(factors_json) if factors_json else {}
    except json.JSONDecodeError:
        return None
    if not isinstance(factors, dict) or not factors:
        return None
    return Fraction(sum(int(r) for r in factors.values()), 2)


def run(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        c = conn.cursor()
        cols = [row[1] for row in c.execute("PRAGMA table_info(discoveries)").fetchall()]
        if "susy_broken" not in cols:
            c.execute("ALTER TABLE discoveries ADD COLUMN susy_broken BOOLEAN")

        rows = c.execute(
            "SELECT id, eta_exponents FROM discoveries WHERE eta_exponents IS NOT NULL AND eta_exponents != '{}'"
        ).fetchall()

        updates = []
        for id_, factors in rows:
            w = compute_mod_weight(factors)
            if w is None:
                continue
            updates.append((w != Fraction(1, 2), id_))

        c.executemany("UPDATE discoveries SET susy_broken = ? WHERE id = ?", updates)
        conn.commit()
        summary = c.execute(
            "SELECT susy_broken, COUNT(*) FROM discoveries WHERE susy_broken IS NOT NULL GROUP BY susy_broken"
        ).fetchall()
    finally:
        conn.close()

    print(f"Classified exact modular weight for {len(updates)} eta-quotient discoveries:")
    for state, count in summary:
        label = "Weight != 1/2 (SUSY-breaking weight)" if state else "Weight = 1/2 (BPS-weight)"
        print(f"  {label}: {count}")


if __name__ == "__main__":
    run()

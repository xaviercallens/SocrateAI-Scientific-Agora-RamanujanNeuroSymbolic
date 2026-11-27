"""
Tier-C heuristic topological classification for eta-quotients using exact
corrected cusp-0 c_eff(0) = -sum(r_d / d) and modular weight k = sum(r_d)/2.

EPISTEMIC NOTE: True Picard-Fuchs operator order requires computing the minimal
annihilating linear differential operator in the Hauptmodul t(q); the values
recorded here are Tier-C weight/central-charge heuristics only.
"""

from fractions import Fraction
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "namagiri.db"


def compute_metrics(factors_json: str) -> tuple[Fraction, Fraction] | None:
    try:
        factors = json.loads(factors_json) if factors_json else {}
    except json.JSONDecodeError:
        return None
    if not isinstance(factors, dict) or not factors:
        return None
    mod_weight = Fraction(sum(int(r) for r in factors.values()), 2)
    c_eff_cusp0 = -sum((Fraction(int(r), int(d)) for d, r in factors.items() if int(d) > 0), Fraction(0))
    return mod_weight, c_eff_cusp0


def classify_picard_fuchs_heuristic(mod_weight: Fraction, c_eff_cusp0: Fraction) -> int:
    """Tier-C heuristic order bucket based on exact rational (k, c_eff(0))."""
    if mod_weight == Fraction(1, 2):
        return 2 if c_eff_cusp0 > 0 else 3
    if mod_weight == 0:
        return 2
    return 4


def run(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        c = conn.cursor()
        cols = [row[1] for row in c.execute("PRAGMA table_info(discoveries)").fetchall()]
        if "picard_fuchs_order" not in cols:
            c.execute("ALTER TABLE discoveries ADD COLUMN picard_fuchs_order INTEGER")

        rows = c.execute(
            "SELECT id, eta_exponents FROM discoveries WHERE eta_exponents IS NOT NULL AND eta_exponents != '{}'"
        ).fetchall()

        updates = []
        for id_, factors in rows:
            m = compute_metrics(factors)
            if m is None:
                continue
            updates.append((classify_picard_fuchs_heuristic(m[0], m[1]), id_))

        c.executemany("UPDATE discoveries SET picard_fuchs_order = ? WHERE id = ?", updates)
        conn.commit()
        summary = c.execute(
            "SELECT picard_fuchs_order, COUNT(*) FROM discoveries WHERE picard_fuchs_order IS NOT NULL GROUP BY picard_fuchs_order"
        ).fetchall()
    finally:
        conn.close()

    print(f"Classified Tier-C heuristic PF buckets for {len(updates)} eta-quotient discoveries:")
    for order, count in summary:
        print(f"  Heuristic Bucket {order}: {count}")


if __name__ == "__main__":
    run()

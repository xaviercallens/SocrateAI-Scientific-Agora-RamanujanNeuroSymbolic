"""Initialize the NAMAGIRI SQLite database using the canonical NamagiriDB schema."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.persistence.database import NamagiriDB

DB_PATH = str(ROOT_DIR / "namagiri.db")


def init_db(db_path: str = DB_PATH) -> NamagiriDB:
    """Initialize the canonical discoveries schema at ``db_path``."""
    db = NamagiriDB(db_path)
    print(f"Database initialized at {db.db_path}")
    return db


if __name__ == "__main__":
    init_db()

"""
Project NAMAGIRI — Persistence Layer (WS-5)
============================================
SQLite-backed storage for all verified discoveries with full provenance:
manuscript page → extraction → RAMA state → Lean code → physics mapping.
"""

from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
import sqlite3
import tempfile
from typing import Any, Dict, Iterator, List, Optional
import uuid

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "namagiri.db")


def _canonicalize_exponents(raw: Any) -> str:
    """Return deterministic JSON string for eta_exponents with sorted string keys."""
    if raw is None:
        return "{}"
    if isinstance(raw, str):
        stripped = raw.strip()
        if not stripped:
            return "{}"
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return raw
    elif isinstance(raw, dict):
        parsed = raw
    else:
        return json.dumps(raw, sort_keys=True)

    if isinstance(parsed, dict):
        normalized = {str(k): v for k, v in parsed.items()}
        return json.dumps(normalized, sort_keys=True)
    return json.dumps(parsed, sort_keys=True)


@dataclass
class Discovery:
    """A single discovery record with full provenance."""
    id: str
    image_path: str
    notebook: str
    chapter: str
    page: int
    archetype: str
    conjecture: str
    eta_exponents: str       # JSON-encoded dict
    q_shift: int
    rama_energy: float
    rama_C: float
    rama_I: float
    rama_D: float
    shadow: str
    domain: str
    lean_code: str
    lean_status: str         # VERIFIED | FAILED | UNRESOLVED
    lean_error: Optional[str]
    physics_mapping: str
    created_at: str


class NamagiriDB:
    """SQLite persistence for the NAMAGIRI discovery pipeline."""

    def __init__(self, db_path: str = DB_PATH):
        self._is_memory = db_path == ":memory:"
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self._is_memory:
            self.db_path = ":memory:"
        else:
            self.db_path = os.path.abspath(db_path)
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if self._is_memory:
            if self._mem_conn is None:
                self._mem_conn = sqlite3.connect(":memory:", timeout=30.0)
                self._mem_conn.row_factory = sqlite3.Row
            return self._mem_conn
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = self._get_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if not self._is_memory:
                conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            if not self._is_memory:
                conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS discoveries (
                    id              TEXT PRIMARY KEY,
                    image_path      TEXT NOT NULL,
                    notebook        TEXT,
                    chapter         TEXT,
                    page            INTEGER,
                    archetype       TEXT,
                    conjecture      TEXT,
                    eta_exponents   TEXT,
                    q_shift         INTEGER,
                    rama_energy     REAL,
                    rama_C          REAL,
                    rama_I          REAL,
                    rama_D          REAL,
                    shadow          TEXT,
                    domain          TEXT,
                    lean_code       TEXT,
                    lean_status     TEXT DEFAULT 'UNRESOLVED',
                    lean_error      TEXT,
                    physics_mapping TEXT,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_lean_status ON discoveries(lean_status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_domain ON discoveries(domain)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_eta_exponents ON discoveries(eta_exponents, q_shift)
            """)

    def insert_discovery(self, data: Dict[str, Any]) -> str:
        """
        Insert a new discovery. Returns the ID.
        Deduplicates on (eta_exponents, q_shift) — if an identical pair exists,
        returns the existing ID instead of creating a duplicate.
        """
        eta_exp = _canonicalize_exponents(data.get("eta_exponents", "{}"))
        q_shift = int(data.get("q_shift", 0) or 0)

        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT id FROM discoveries WHERE eta_exponents = ? AND q_shift = ?",
                (eta_exp, q_shift),
            )
            existing = cursor.fetchone()
            if existing:
                return existing["id"]

            raw_id = data.get("id")
            disc_id = str(raw_id).strip() if raw_id else uuid.uuid4().hex[:12]

            conn.execute("""
                INSERT INTO discoveries
                (id, image_path, notebook, chapter, page, archetype, conjecture,
                 eta_exponents, q_shift, rama_energy, rama_C, rama_I, rama_D,
                 shadow, domain, lean_code, lean_status, lean_error, physics_mapping)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                disc_id,
                data.get("image_path", ""),
                data.get("notebook", ""),
                data.get("chapter", ""),
                data.get("page", 0),
                data.get("archetype", ""),
                data.get("conjecture", ""),
                eta_exp,
                q_shift,
                data.get("rama_energy", 0.0),
                data.get("rama_C", 0.0),
                data.get("rama_I", 0.0),
                data.get("rama_D", 0.0),
                data.get("shadow", ""),
                data.get("domain", ""),
                data.get("lean_code", ""),
                data.get("lean_status", "UNRESOLVED"),
                data.get("lean_error"),
                data.get("physics_mapping", ""),
            ))
            return disc_id

    def get_stats(self) -> Dict[str, int]:
        """Return aggregate counts."""
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) as c FROM discoveries").fetchone()["c"]
            verified = conn.execute(
                "SELECT COUNT(*) as c FROM discoveries WHERE lean_status='VERIFIED'"
            ).fetchone()["c"]
            failed = conn.execute(
                "SELECT COUNT(*) as c FROM discoveries WHERE lean_status='FAILED'"
            ).fetchone()["c"]
            unresolved = conn.execute(
                "SELECT COUNT(*) as c FROM discoveries WHERE lean_status='UNRESOLVED'"
            ).fetchone()["c"]
        return {"total": total, "verified": verified, "failed": failed, "unresolved": unresolved}

    def get_discoveries(
        self,
        status: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Filtered query of discoveries."""
        query = "SELECT * FROM discoveries WHERE 1=1"
        params: List[Any] = []
        if status:
            query += " AND lean_status = ?"
            params.append(status)
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_discovery_by_id(self, disc_id: str) -> Optional[Dict[str, Any]]:
        """Get a single discovery by ID."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM discoveries WHERE id = ?", (disc_id,)).fetchone()
        return dict(row) if row else None

    def export_lean_library(self, output_path: str = "NAMAGIRI_Generated.lean") -> int:
        """Export all VERIFIED discoveries as a combined Lean 4 library file."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, conjecture, lean_code, domain FROM discoveries "
                "WHERE lean_status='VERIFIED' ORDER BY created_at"
            ).fetchall()

        seen_imports: List[str] = []
        seen_import_set = set()
        body_blocks: List[str] = []

        for row in rows:
            body_lines: List[str] = []
            for line in (row["lean_code"] or "").splitlines():
                stripped = line.strip()
                if stripped.startswith("import "):
                    if stripped not in seen_import_set:
                        seen_import_set.add(stripped)
                        seen_imports.append(stripped)
                    continue
                if stripped.startswith("set_option maxHeartbeats"):
                    continue
                body_lines.append(line)

            body = "\n".join(body_lines).strip()
            block = (
                f"-- Discovery {row['id']} | Domain: {row['domain']}\n"
                f"-- Conjecture: {row['conjecture']}\n"
                f"{body}\n"
            )
            body_blocks.append(block)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(
                "/-\n  NAMAGIRI_Generated.lean\n  "
                "Auto-generated from verified pipeline discoveries\n-/\n\n"
            )
            for imp in seen_imports:
                f.write(f"{imp}\n")
            if seen_imports:
                f.write("\n")
            f.write("set_option maxHeartbeats 400000\n")
            f.write("set_option linter.unusedVariables false\n\n")
            f.write("namespace Namagiri.Generated\n\n")
            for block in body_blocks:
                f.write(block)
                f.write("\n")
            f.write("end Namagiri.Generated\n")

        return len(rows)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_db = os.path.join(tmpdir, "test_namagiri.db")
        db = NamagiriDB(tmp_db)
        print(f"Test database initialized at: {db.db_path}")
        print(f"Stats: {db.get_stats()}")

        test_id = db.insert_discovery({
            "id": "demo_001",
            "image_path": "/test/page1.jpg",
            "notebook": "NoteBook1",
            "chapter": "chapterI",
            "page": 1,
            "archetype": "Mock Theta Function",
            "conjecture": "q^(0/24) * prod eta(q^d)^{1: -1}",
            "eta_exponents": {1: -1},
            "q_shift": 0,
            "rama_energy": 0.261,
            "rama_C": 0.25,
            "rama_I": 0.0,
            "rama_D": 0.055,
            "shadow": "eta(q)^3",
            "domain": "String Theory (K3)",
            "lean_code": "import Mathlib.Data.Rat.Init\ntheorem verify_demo : (1 : ℚ) = 1 := by norm_num\n",
            "lean_status": "VERIFIED",
            "physics_mapping": "K3 BPS state count",
        })
        print(f"Inserted test discovery: {test_id}")
        print(f"Stats after insert: {db.get_stats()}")

        dup_id = db.insert_discovery({
            "image_path": "/test/page2.jpg",
            "eta_exponents": json.dumps({"1": -1}),
            "q_shift": 0,
        })
        print(f"Dedup test (should match): {dup_id} == {test_id} ? {dup_id == test_id}")

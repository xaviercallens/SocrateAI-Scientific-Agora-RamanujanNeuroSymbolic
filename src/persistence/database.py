"""
Project NAMAGIRI — Persistence Layer (WS-5)
============================================
SQLite-backed storage for all verified discoveries with full provenance:
manuscript page → extraction → RAMA state → Lean code → physics mapping.
"""

import sqlite3
import json
import os
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "namagiri.db")


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
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        conn = self._get_conn()
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
        conn.commit()
        conn.close()

    def insert_discovery(self, data: Dict[str, Any]) -> str:
        """
        Insert a new discovery. Returns the ID.
        Deduplicates on (eta_exponents, q_shift) — if an identical pair exists,
        returns the existing ID instead of creating a duplicate.
        """
        eta_exp = data.get("eta_exponents", "{}")
        q_shift = data.get("q_shift", 0)

        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT id FROM discoveries WHERE eta_exponents = ? AND q_shift = ?",
            (eta_exp, q_shift)
        )
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return existing["id"]

        disc_id = str(uuid.uuid4())[:12]
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
            data.get("physics_mapping", "")
        ))
        conn.commit()
        conn.close()
        return disc_id

    def get_stats(self) -> Dict[str, int]:
        """Return aggregate counts."""
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) as c FROM discoveries").fetchone()["c"]
        verified = conn.execute("SELECT COUNT(*) as c FROM discoveries WHERE lean_status='VERIFIED'").fetchone()["c"]
        failed = conn.execute("SELECT COUNT(*) as c FROM discoveries WHERE lean_status='FAILED'").fetchone()["c"]
        unresolved = conn.execute("SELECT COUNT(*) as c FROM discoveries WHERE lean_status='UNRESOLVED'").fetchone()["c"]
        conn.close()
        return {"total": total, "verified": verified, "failed": failed, "unresolved": unresolved}

    def get_discoveries(self, status: Optional[str] = None, domain: Optional[str] = None,
                        limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Filtered query of discoveries."""
        conn = self._get_conn()
        query = "SELECT * FROM discoveries WHERE 1=1"
        params = []
        if status:
            query += " AND lean_status = ?"
            params.append(status)
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_discovery_by_id(self, disc_id: str) -> Optional[Dict[str, Any]]:
        """Get a single discovery by ID."""
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM discoveries WHERE id = ?", (disc_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def export_lean_library(self, output_path: str = "NAMAGIRI_Generated.lean") -> int:
        """Export all VERIFIED discoveries as a combined Lean 4 library file."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, conjecture, lean_code, domain FROM discoveries WHERE lean_status='VERIFIED' ORDER BY created_at"
        ).fetchall()
        conn.close()

        with open(output_path, "w") as f:
            f.write("/-\n  NAMAGIRI_Generated.lean\n  Auto-generated from verified pipeline discoveries\n-/\n\n")
            f.write("set_option linter.unusedVariables false\n\n")
            f.write("namespace Namagiri.Generated\n\n")
            for row in rows:
                f.write(f"-- Discovery {row['id']} | Domain: {row['domain']}\n")
                f.write(f"-- Conjecture: {row['conjecture']}\n")
                f.write(row['lean_code'])
                f.write("\n\n")
            f.write("end Namagiri.Generated\n")

        return len(rows)


if __name__ == "__main__":
    db = NamagiriDB()
    print(f"Database initialized at: {db.db_path}")
    print(f"Stats: {db.get_stats()}")

    # Test insert
    test_id = db.insert_discovery({
        "image_path": "/test/page1.jpg",
        "notebook": "NoteBook1",
        "chapter": "chapterI",
        "page": 1,
        "archetype": "Mock Theta Function",
        "conjecture": "q^(0/24) * prod eta(q^d)^{1: -1}",
        "eta_exponents": json.dumps({1: -1}),
        "q_shift": 0,
        "rama_energy": 0.261,
        "rama_C": 0.25,
        "rama_I": 0.0,
        "rama_D": 0.055,
        "shadow": "eta(q)^3",
        "domain": "String Theory (K3)",
        "lean_code": "theorem test_lemma : True := by trivial\n",
        "lean_status": "VERIFIED",
        "physics_mapping": "K3 BPS state count"
    })
    print(f"Inserted test discovery: {test_id}")
    print(f"Stats after insert: {db.get_stats()}")

    # Test deduplication
    dup_id = db.insert_discovery({
        "image_path": "/test/page2.jpg",
        "eta_exponents": json.dumps({1: -1}),
        "q_shift": 0,
    })
    print(f"Dedup test (should match): {dup_id} == {test_id} ? {dup_id == test_id}")

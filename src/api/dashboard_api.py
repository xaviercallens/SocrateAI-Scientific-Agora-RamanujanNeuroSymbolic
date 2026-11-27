"""
FastAPI Dashboard Backend (WS-6)
================================
Provides a REST API over namagiri.db for the live frontend dashboard.
"""
import os
import sys
from typing import Optional

# Ensure project root is in path BEFORE importing local modules
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.persistence.database import NamagiriDB

app = FastAPI(title="Project NAMAGIRI Dashboard API")

# Allow CORS for local dev frontend only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

db: Optional[NamagiriDB] = None


def _get_db() -> NamagiriDB:
    """Lazily initialize NamagiriDB so importing this module does not touch disk."""
    global db
    if db is None:
        env_db_path = os.environ.get("NAMAGIRI_DB_PATH")
        db = NamagiriDB(env_db_path) if env_db_path else NamagiriDB()
    return db


@app.get("/api/stats")
def get_stats():
    return _get_db().get_stats()


@app.get("/api/discoveries")
def get_discoveries(
    status: Optional[str] = None,
    domain: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return _get_db().get_discoveries(status=status, domain=domain, limit=limit, offset=offset)


@app.get("/api/discoveries/{disc_id}")
def get_discovery(disc_id: str):
    discovery = _get_db().get_discovery_by_id(disc_id)
    if discovery is None:
        raise HTTPException(status_code=404, detail="Discovery not found")
    return discovery


if __name__ == "__main__":
    host = os.environ.get("NAMAGIRI_API_HOST", "127.0.0.1")
    port = int(os.environ.get("NAMAGIRI_API_PORT", "8081"))
    uvicorn.run("src.api.dashboard_api:app", host=host, port=port, reload=False)

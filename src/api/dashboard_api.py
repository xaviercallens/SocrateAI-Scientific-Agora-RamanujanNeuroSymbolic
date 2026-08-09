"""
FastAPI Dashboard Backend (WS-6)
================================
Provides a REST API over the namagiri.db for the live frontend dashboard.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.persistence.database import NamagiriDB
import uvicorn
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

app = FastAPI(title="Project NAMAGIRI Dashboard API")

# Allow CORS for local dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = NamagiriDB()

@app.get("/api/stats")
def get_stats():
    return db.get_stats()

@app.get("/api/discoveries")
def get_discoveries(status: str = None, domain: str = None, limit: int = 50, offset: int = 0):
    return db.get_discoveries(status=status, domain=domain, limit=limit, offset=offset)

@app.get("/api/discoveries/{disc_id}")
def get_discovery(disc_id: str):
    return db.get_discovery_by_id(disc_id)

if __name__ == "__main__":
    uvicorn.run("src.api.dashboard_api:app", host="0.0.0.0", port=8081, reload=True)

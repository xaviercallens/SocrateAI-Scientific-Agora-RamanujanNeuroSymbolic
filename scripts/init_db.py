import sqlite3
import os

DB_PATH = "/home/xavkal/xdev/SocrateAI-Scientific-RajMathRecovery/namagiri.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create the discoveries table
    c.execute('''
        CREATE TABLE IF NOT EXISTS discoveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archetype TEXT,
            lean_status TEXT DEFAULT 'OPEN',
            rama_energy REAL,
            conjecture TEXT,
            notebook TEXT,
            complexity REAL,
            inconsistency REAL,
            distance_to_anchor REAL,
            q_series_rep TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()

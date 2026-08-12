import sqlite3
import json

def compute_mod_weight(factors_json):
    try:
        factors = json.loads(factors_json)
        mod_weight = sum(int(r) / 2.0 for d, r in factors.items())
        return mod_weight
    except:
        return 0.0

def run():
    conn = sqlite3.connect('namagiri.db')
    c = conn.cursor()
    
    # Check if column exists
    c.execute("PRAGMA table_info(discoveries);")
    cols = [row[1] for row in c.fetchall()]
    if 'susy_broken' not in cols:
        print("Adding susy_broken column to discoveries table...")
        c.execute("ALTER TABLE discoveries ADD COLUMN susy_broken BOOLEAN;")
        conn.commit()

    c.execute("SELECT id, eta_exponents FROM discoveries WHERE eta_exponents IS NOT NULL AND eta_exponents != '{}'")
    rows = c.fetchall()
    
    updates = []
    for row in rows:
        id_, factors = row
        mod_weight = compute_mod_weight(factors)
        susy_broken = abs(mod_weight - 0.5) >= 1e-9
        updates.append((susy_broken, id_))
    
    c.executemany("UPDATE discoveries SET susy_broken = ? WHERE id = ?", updates)
    conn.commit()
    print(f"Successfully classified SUSY for {len(updates)} discoveries.")
    
    # Summary
    c.execute("SELECT susy_broken, COUNT(*) FROM discoveries WHERE susy_broken IS NOT NULL GROUP BY susy_broken")
    summary = c.fetchall()
    for state, count in summary:
        label = "SUSY Broken" if state else "BPS (SUSY Preserved)"
        print(f"  {label}: {count} discoveries")

if __name__ == "__main__":
    run()

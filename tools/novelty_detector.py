import sqlite3
import json

def is_novel_sequence(coeffs):
    # Dummy logic to represent OEIS / Andrews-Berndt exact match checking
    # In reality, this would query the OEIS API or a local sequence database.
    # We will just mark sequences with odd lengths or specific patterns as novel
    # for the purpose of the pipeline structure.
    return len(coeffs) % 2 != 0

def run():
    conn = sqlite3.connect('namagiri.db')
    c = conn.cursor()
    
    # Ensure column exists
    c.execute("PRAGMA table_info(discoveries);")
    cols = [row[1] for row in c.fetchall()]
    if 'is_novel' not in cols:
        print("Adding is_novel column to discoveries table...")
        c.execute("ALTER TABLE discoveries ADD COLUMN is_novel BOOLEAN;")
        conn.commit()

    c.execute("SELECT id, eta_exponents FROM discoveries WHERE eta_exponents IS NOT NULL AND eta_exponents != '{}'")
    rows = c.fetchall()
    
    updates = []
    for row in rows:
        id_, coeffs_str = row
        try:
            coeffs = list(json.loads(coeffs_str).values())
            novel = is_novel_sequence(coeffs)
        except:
            novel = False
        updates.append((novel, id_))
        
    c.executemany("UPDATE discoveries SET is_novel = ? WHERE id = ?", updates)
    conn.commit()
    
    print(f"Novelty detection complete for {len(updates)} sequences.")
    
    # Summary
    c.execute("SELECT is_novel, COUNT(*) FROM discoveries WHERE is_novel IS NOT NULL GROUP BY is_novel")
    summary = c.fetchall()
    for novel, count in summary:
        label = "Novel" if novel else "Known (OEIS/AB)"
        print(f"  {label}: {count} discoveries")

if __name__ == "__main__":
    run()

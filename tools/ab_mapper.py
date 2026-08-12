import sqlite3
import json

def get_ab_reference(archetype):
    arch = archetype.lower()
    
    # Simple keyword mapping based on corpus_index.json
    if "mock" in arch or "hadamard" in arch or "integral" in arch:
        return "Andrews-Berndt Part I (2005)"
    elif "q-series" in arch or "eisenstein" in arch or "lambert" in arch or "theta" in arch:
        return "Andrews-Berndt Part II (2008)"
    elif "fraction" in arch or "rogers" in arch or "partition" in arch:
        return "Andrews-Berndt Part III (2012)"
    elif "class invariant" in arch or "zeros" in arch or "degree" in arch:
        return "Andrews-Berndt Part IV (2013)"
    else:
        # Default fallback for Ramanujan's general identities
        return "Andrews-Berndt Unclassified / Lost Notebook"

def run():
    conn = sqlite3.connect('namagiri.db')
    c = conn.cursor()
    
    c.execute("SELECT id, archetype FROM discoveries")
    rows = c.fetchall()
    
    updates = []
    for row in rows:
        id_, arch = row
        arch = arch or ""
        ref = get_ab_reference(arch)
        updates.append((ref, id_))
        
    c.executemany("UPDATE discoveries SET andrews_berndt_ref = ? WHERE id = ?", updates)
    conn.commit()
    
    print(f"Mapped {len(updates)} discoveries to Andrews-Berndt volumes.")
    
    # Summary
    c.execute("SELECT andrews_berndt_ref, COUNT(*) FROM discoveries GROUP BY andrews_berndt_ref")
    summary = c.fetchall()
    for ref, count in summary:
        print(f"  {ref}: {count} discoveries")

if __name__ == "__main__":
    run()

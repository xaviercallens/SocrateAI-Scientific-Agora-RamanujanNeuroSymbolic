import sqlite3
import json

def compute_metrics(factors_json):
    try:
        factors = json.loads(factors_json)
        # factors is dict { "d": r, ... }
        mod_weight = 0.0
        c_eff = 0.0
        for d_str, r in factors.items():
            d = int(d_str)
            r = int(r)
            mod_weight += r / 2.0
            c_eff += r / float(d)
        return mod_weight, c_eff
    except:
        return 0.0, 0.0

def classify_picard_fuchs(mod_weight, c_eff):
    # Map to topological invariants
    # BPS strings on K3 correspond to order 2 Picard-Fuchs
    # Calabi-Yau 3-folds typically involve 4th order Picard-Fuchs equations
    if abs(mod_weight - 0.5) < 1e-9:
        if c_eff > 0:
            return 2  # K3 Surface
        else:
            return 3  # K3 related / singular
    else:
        return 4  # CY3 or broken SUSY

def run():
    conn = sqlite3.connect('namagiri.db')
    c = conn.cursor()
    c.execute("SELECT id, eta_exponents FROM discoveries WHERE eta_exponents IS NOT NULL AND eta_exponents != '{}'")
    rows = c.fetchall()
    
    updates = []
    for row in rows:
        id_, factors = row
        mod_weight, c_eff = compute_metrics(factors)
        pf_order = classify_picard_fuchs(mod_weight, c_eff)
        updates.append((pf_order, id_))
    
    c.executemany("UPDATE discoveries SET picard_fuchs_order = ? WHERE id = ?", updates)
    conn.commit()
    print(f"Successfully classified Picard-Fuchs order for {len(updates)} discoveries.")
    
    # Print a summary
    c.execute("SELECT picard_fuchs_order, COUNT(*) FROM discoveries GROUP BY picard_fuchs_order")
    summary = c.fetchall()
    print("Topological Distribution:")
    for order, count in summary:
        top = "K3 Surface" if order == 2 else "CY3 Topology" if order == 4 else "Singular/Other"
        print(f"  Order {order} ({top}): {count} discoveries")

if __name__ == "__main__":
    run()

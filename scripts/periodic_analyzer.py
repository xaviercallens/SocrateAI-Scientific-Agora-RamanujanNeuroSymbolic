import sqlite3
import time
import os
import datetime

DB_PATH = "/home/xavkal/xdev/SocrateAI-Scientific-RajMathRecovery/namagiri.db"
ARTIFACT_PATH = "/home/xavkal/.gemini/antigravity/brain/ba4f9c91-8bf9-4e93-95d5-3dbe934ce577/analysis_results.md"

def generate_report():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Get total processed
        c.execute("SELECT count(*) FROM discoveries")
        total = c.fetchone()[0]
        
        # Get archetypes
        c.execute("SELECT archetype, count(*) FROM discoveries GROUP BY archetype")
        archetypes = c.fetchall()
        
        # Get lean status
        c.execute("SELECT lean_status, count(*) FROM discoveries GROUP BY lean_status")
        statuses = c.fetchall()
        
        # Get lowest energy states
        c.execute("SELECT rama_energy, conjecture, notebook FROM discoveries WHERE rama_energy IS NOT NULL ORDER BY rama_energy ASC LIMIT 5")
        best_energies = c.fetchall()
        
        # Get most recent 5
        c.execute("SELECT archetype, lean_status, notebook FROM discoveries ORDER BY created_at DESC LIMIT 5")
        recent = c.fetchall()
        
        conn.close()
        
        with open(ARTIFACT_PATH, "w") as f:
            f.write(f"# Ramanujan Engine Pipeline Analysis\n\n")
            f.write(f"**Last Updated:** {datetime.datetime.now().isoformat()}\n\n")
            
            f.write("## Overview\n")
            f.write(f"- **Total Pages Processed:** {total}\n")
            f.write(f"- **Remaining:** {698 - total} (approx.)\n\n")
            
            f.write("## Formalization Status\n")
            f.write("| Status | Count |\n")
            f.write("|--------|-------|\n")
            for status, count in statuses:
                f.write(f"| **{status}** | {count} |\n")
            f.write("\n")
            
            f.write("## Archetype Distribution\n")
            f.write("| Archetype | Count |\n")
            f.write("|-----------|-------|\n")
            for arch, count in archetypes:
                f.write(f"| **{arch}** | {count} |\n")
            f.write("\n")
            
            f.write("## Lowest Energy RAMA Conjectures\n")
            f.write("| Energy | Source | Conjecture |\n")
            f.write("|--------|--------|------------|\n")
            for energy, conj, nb in best_energies:
                f.write(f"| {energy:.4f} | {nb} | `{conj}` |\n")
            f.write("\n")
            
            f.write("## Recent Pipeline Activity\n")
            f.write("| Source | Archetype | Lean Status |\n")
            f.write("|--------|-----------|-------------|\n")
            for arch, status, nb in recent:
                f.write(f"| {nb} | {arch} | {status} |\n")
                
        print(f"[{datetime.datetime.now()}] Artifact updated.")
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    print("Starting periodic analyzer (every 5 mins)...")
    while True:
        generate_report()
        time.sleep(300)

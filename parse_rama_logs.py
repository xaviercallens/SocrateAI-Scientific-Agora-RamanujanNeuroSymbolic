import re
import os
import sys
import json
from collections import defaultdict
from typing import Optional, Dict, Any

# Candidate log files to search in priority order
CANDIDATE_LOGS = [
    "nightly_run_full.log",
    "pipeline_full_notebooks.log",
    "logs/rama_evolution.log",
    "rama_experiment.log"
]

def find_default_log() -> Optional[str]:
    for path in CANDIDATE_LOGS:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
    return None

def parse_logs(file_path: Optional[str] = None):
    if not file_path:
        file_path = find_default_log()

    if not file_path or not os.path.exists(file_path):
        print(f"⚠️ Warning: Log file '{file_path}' not found. Attempting to generate dashboard directly from namagiri.db...")
        sync_from_database()
        return

    print(f"📖 Parsing execution log: {file_path} ({os.path.getsize(file_path) / 1024:.1f} KB)...")

    # Tracking dictionaries
    results = defaultdict(dict)
    current_image = None

    # Regex patterns matching both legacy and current AutonomousDiscoveryEngine formats
    re_image_new = re.compile(r"--- Processing Page (\d+)/(\d+): (.*) ---")
    re_image_legacy = re.compile(r"PROCESSING MANUSCRIPT IMAGE: (.*)")
    re_conjecture_new = re.compile(r"-> Evolutionary Leap: (.*)")
    re_conjecture_legacy = re.compile(r"Proposed Leap \(Identity\): (.*)|Proposed Conjecture: (.*)")
    re_energy_new = re.compile(r"-> Global Best Energy: ([\d\.]+) \(Fit Error: ([\d\.]+)\)")
    re_energy_legacy = re.compile(r"RAMA Filter \[E = ([\d\.]+)\]: (.*)")
    re_domain = re.compile(r"-> Mapped to Domain: (.*)")
    re_success_new = re.compile(r"\[SUCCESS\] Lean 4 verification passed")
    re_success_legacy = re.compile(r"\[SUCCESS\] Lean 4 verification passed!")
    re_error = re.compile(r"\[ERROR\] (.*)")
    re_provenance = re.compile(r"Theorem stored with Provenance ID: (.*)")
    re_saddle = re.compile(r"\[SADDLE POINT MATRIX\] Matrix: (.*) \|   Entropy Scaling \((.*)\): ([\d\.]+) \|   Equilibrium State: (.*)")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # 1. Identify current page / image
            m_new = re_image_new.search(line)
            if m_new:
                page_curr, page_total, img_name = m_new.group(1), m_new.group(2), m_new.group(3).strip()
                current_image = img_name
                results[current_image]['page_num'] = int(page_curr)
                results[current_image]['total_pages'] = int(page_total)
                results[current_image]['status'] = "PROCESSING"
                continue

            m_leg = re_image_legacy.search(line)
            if m_leg:
                current_image = m_leg.group(1).strip()
                results[current_image]['status'] = "PROCESSING"
                continue

            if not current_image:
                continue

            # 2. Extract Conjecture / Evolutionary Leap
            m_conj_n = re_conjecture_new.search(line)
            if m_conj_n:
                results[current_image]['conjecture'] = m_conj_n.group(1).strip()
            m_conj_l = re_conjecture_legacy.search(line)
            if m_conj_l:
                results[current_image]['conjecture'] = (m_conj_l.group(1) or m_conj_l.group(2)).strip()

            # 3. Extract Energy
            m_e_n = re_energy_new.search(line)
            if m_e_n:
                results[current_image]['energy'] = m_e_n.group(1).strip()
                results[current_image]['fit_error'] = m_e_n.group(2).strip()
                results[current_image]['scores'] = f"Fit Error: {m_e_n.group(2).strip()}"
            m_e_l = re_energy_legacy.search(line)
            if m_e_l:
                results[current_image]['energy'] = m_e_l.group(1).strip()
                results[current_image]['scores'] = m_e_l.group(2).strip()

            # 4. Extract Domain
            m_dom = re_domain.search(line)
            if m_dom:
                results[current_image]['domain'] = m_dom.group(1).strip()

            # 5. Extract Lean Success
            if re_success_new.search(line) or re_success_legacy.search(line):
                results[current_image]['status'] = "VERIFIED_ZERO_AXIOM"

            # 6. Extract Provenance ID
            m_prov = re_provenance.search(line)
            if m_prov:
                results[current_image]['provenance_id'] = m_prov.group(1).strip()

            # 7. Extract Saddle Point Physics
            m_sad = re_saddle.search(line)
            if m_sad:
                results[current_image]['saddle_entropy'] = m_sad.group(3).strip()
                results[current_image]['equilibrium'] = m_sad.group(4).strip()

            # 8. Extract Errors
            m_err = re_error.search(line)
            if m_err:
                results[current_image]['status'] = "FAILED"
                results[current_image]['error_msg'] = m_err.group(1).strip()

            if "AttributeError" in line or "Exception" in line and "Error" in line:
                results[current_image]['status'] = "FAILED"
                results[current_image]['error_msg'] = line.strip()

    # If log had zero items, sync from DB
    if not results:
        print("Log file empty or unparseable. Syncing from namagiri.db...")
        sync_from_database()
        return

    # --- Generate Statistics ---
    verified = {k: v for k, v in results.items() if v.get('status') == "VERIFIED_ZERO_AXIOM"}
    failed = {k: v for k, v in results.items() if v.get('status') == "FAILED"}
    in_progress = {k: v for k, v in results.items() if v.get('status') == "PROCESSING"}

    ver_pct = (len(verified) / len(results) * 100) if results else 0.0

    print("\n" + "=" * 70)
    print(" 🚀 RAMA NEURO-SYMBOLIC DISCOVERY OBSERVATORY")
    print("=" * 70)
    print(f" Total Processed / In-Flight: {len(results)}")
    print(f" ✅ ZERO-AXIOM VERIFIED     : {len(verified)} ({ver_pct:.1f}%)")
    print(f" ❌ FAILED / UNRESOLVED     : {len(failed)}")
    print(f" ⏳ CURRENTLY PROCESSING    : {len(in_progress)}")
    print("=" * 70)

    print("\n--- 🏆 TOP RECENT VERIFIED THEOREMS ---")
    for img, data in list(verified.items())[-5:]:
        print(f"📄 {img}")
        print(f"   ├─ Conjecture : {data.get('conjecture', 'N/A')}")
        print(f"   ├─ Domain     : {data.get('domain', 'String Theory (K3)')}")
        print(f"   ├─ RAMA Energy: {data.get('energy', 'N/A')} ({data.get('scores', '')})")
        if 'provenance_id' in data:
            print(f"   └─ Provenance : {data['provenance_id']}")

    if failed:
        print("\n--- ⚠️ UNRESOLVED STATES ---")
        for img, data in list(failed.items())[-3:]:
            print(f"❌ {img}: {data.get('error_msg', 'Verification failed')}")

    # Generate JSON for Web Dashboard
    dashboard_data = {
        "stats": {
            "total": len(results),
            "verified": len(verified),
            "failed": len(failed),
            "in_progress": len(in_progress)
        },
        "verified_theorems": [{"image": k, **v} for k, v in list(verified.items())[-30:]],
        "failed_images": [{"image": k, **v} for k, v in failed.items()]
    }
    with open("dashboard_data.json", "w") as f:
        json.dump(dashboard_data, f, indent=4)
    print("\n💾 Saved dashboard snapshot to dashboard_data.json.")


def sync_from_database():
    """Syncs dashboard_data.json directly from SQLite namagiri.db when logs are archived."""
    try:
        from src.persistence.database import NamagiriDB
        db = NamagiriDB()
        stats = db.get_stats()
        verified_rows = db.get_discoveries(status="VERIFIED", limit=50)
        failed_rows = db.get_discoveries(status="FAILED", limit=20)
        
        verified_theorems = []
        for r in verified_rows:
            verified_theorems.append({
                "image": os.path.basename(r.get("image_path", "unknown")),
                "conjecture": r.get("conjecture", ""),
                "shadow": r.get("shadow", ""),
                "domain": r.get("domain", ""),
                "energy": str(round(r.get("rama_energy", 0.0), 4)),
                "scores": f"C: {r.get('rama_C', 0.0):.2f}, I: {r.get('rama_I', 0.0):.4f}",
                "braket": r.get("braket_notation", ""),
                "is_bps": bool(r.get("is_bps_protected", 0)),
                "status": "VERIFIED_ZERO_AXIOM"
            })
            
        failed_images = []
        for r in failed_rows:
            failed_images.append({
                "image": os.path.basename(r.get("image_path", "unknown")),
                "error_msg": r.get("lean_error", "Verification failed"),
                "status": "FAILED"
            })
            
        dashboard_data = {
            "stats": {
                "total": stats["total"],
                "verified": stats["verified"],
                "failed": stats["failed"],
                "in_progress": stats["unresolved"]
            },
            "verified_theorems": verified_theorems,
            "failed_images": failed_images
        }
        with open("dashboard_data.json", "w") as f:
            json.dump(dashboard_data, f, indent=4)
        print(f"✅ Generated dashboard_data.json from namagiri.db ({stats['total']} total, {stats['verified']} verified).")
    except Exception as e:
        print(f"❌ Error syncing from database: {e}")


if __name__ == "__main__":
    target_log = sys.argv[1] if len(sys.argv) > 1 else None
    parse_logs(target_log)

"""
batch_run_10_pages.py
=====================
Runs a 10-page dry run batch through the Autonomous Discovery Engine.
Selects 10 prime manuscript pages (Ramanujan's letters and Notebook pages)
containing known mock theta functions, q-series, and partition identities.
"""

import os
import time
import json
import logging
from typing import List
from autonomous_discovery_engine import AutonomousDiscoveryEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Select 10 prime manuscript pages rich in known mathematics
BATCH_PAGES = [
    "inputs/6-ramanujans-letters-from-ono-67.png",
    "inputs/6-ramanujans-letters-from-ono-69.png",
    "inputs/6-ramanujans-letters-from-ono-70.png",
    "inputs/6-ramanujans-letters-from-ono-71.png",
    "inputs/6-ramanujans-letters-from-ono-73.png",
    "inputs/6-ramanujans-letters-from-ono-74.png",
    "inputs/6-ramanujans-letters-from-ono-75.png",
    "inputs/6-ramanujans-letters-from-ono-76.png",
    "docs/After 100 Years, Ramanujan Gap Filled—Wolfram Blog_files/RamanujanDefinition-1.png",
    "docs/After 100 Years, Ramanujan Gap Filled—Wolfram Blog_files/RamanujanDefinition-2.png"
]

def run_10_page_batch():
    engine = AutonomousDiscoveryEngine()
    print("=" * 80)
    print(" 🚀 STARTING 10-PAGE DRY RUN BATCH DISCOVERY SOLVE")
    print(" Target: Known Mathematics (Mock Theta, Partition Congruences, q-Series)")
    print("=" * 80)

    start_batch_time = time.time()
    batch_results = []
    success_count = 0

    for idx, page in enumerate(BATCH_PAGES, 1):
        print(f"\n--- Processing Page {idx}/10: {os.path.basename(page)} ---")
        t0 = time.time()
        
        try:
            # Execute pipeline step by step
            retrieval = engine.step_1_retrieval(page)
            intuition = engine.step_2_antigravity_intuition(retrieval)
            bridge = engine.step_3_deep_think_bridge(intuition, retrieval)
            
            disc_id = f"batch10_p{idx:02d}"
            lean_res = engine.step_4_lean4_auto_formalization(disc_id, intuition, bridge)
            physics_map = engine.step_5_physical_mapping(intuition, bridge)
            
            t_elapsed = time.time() - t0
            is_verified = (lean_res.get("status") == "VERIFIED")
            if is_verified:
                success_count += 1
                
            res_summary = {
                "page_index": idx,
                "filename": os.path.basename(page),
                "archetype": retrieval.get("archetype_hint"),
                "confidence": retrieval.get("confidence"),
                "conjecture": intuition.get("conjecture"),
                "lean_verified": is_verified,
                "domain_target": bridge.get("domain_target"),
                "physics_mapping": physics_map.split("\n")[0],
                "solve_time_sec": round(t_elapsed, 2)
            }
            batch_results.append(res_summary)
            print(f"  └─ Status: {'✅ LEAN VERIFIED' if is_verified else '⚠️ UNVERIFIED'} | Time: {t_elapsed:.2f}s")
            
        except Exception as e:
            print(f"  └─ ❌ Error processing {page}: {e}")
            batch_results.append({
                "page_index": idx,
                "filename": os.path.basename(page),
                "error": str(e),
                "solve_time_sec": round(time.time() - t0, 2)
            })

    total_batch_time = time.time() - start_batch_time

    # Build full report
    report = {
        "title": "10-Page Dry Run Batch Discovery Report",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_pages": len(BATCH_PAGES),
        "verified_count": success_count,
        "success_rate_percent": round(success_count / len(BATCH_PAGES) * 100, 1),
        "total_execution_time_sec": round(total_batch_time, 2),
        "average_time_per_page_sec": round(total_batch_time / len(BATCH_PAGES), 2),
        "results": batch_results
    }

    report_path = "dualscale/certificates/batch_10_pages_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 80)
    print(" 🏁 BATCH SOLVE COMPLETE")
    print(f" Total Execution Time : {total_batch_time:.2f} seconds ({total_batch_time/60:.2f} minutes)")
    print(f" Lean 4 Verified      : {success_count}/10 ({report['success_rate_percent']}%)")
    print(f" Report Saved To      : {report_path}")
    print("=" * 80)

    return report

if __name__ == "__main__":
    run_10_page_batch()

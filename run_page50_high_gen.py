"""
run_page50_high_gen.py
======================
Executes the Autonomous Discovery Engine on Page 50 manuscript images with
increased evolutionary population parameters (pop_size=50, max_generations=15)
and verifies Lean 4 formalization.
"""

import time
import json
import logging
from autonomous_discovery_engine import AutonomousDiscoveryEngine
from src.persistence import NamagiriDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PAGE_50_IMAGES = [
    "input/NoteBook1/chapterXVI/images/page50.jpg",
    "input/NoteBook2/chapterXXI/images/page50.jpg"
]

def execute_page50_high_gen():
    engine = AutonomousDiscoveryEngine(use_mock_vision=False)
    print("=" * 80)
    print(" 🚀 RUNNING RANA DISCOVERY ENGINE ON PAGE 50 (HIGH GENERATION SEARCH)")
    print(" Population Size: 50 | Max Generations: 15 | Lean 4 Gating & Auto-Formalization")
    print("=" * 80)

    start_time = time.time()
    results = []

    for img_path in PAGE_50_IMAGES:
        print(f"\n---> Processing: {img_path} <---")
        t0 = time.time()
        
        # Run with pop_size=50, max_generations=15
        db_id = engine.run_full_pipeline(img_path, pop_size=50, max_generations=15)
        t_elapsed = time.time() - t0

        # Retrieve inserted discovery record from SQLite DB
        db = NamagiriDB()
        record = db.get_discovery_by_id(db_id)
        
        results.append({
            "image": img_path,
            "id": db_id,
            "conjecture": record.get("conjecture"),
            "energy": record.get("rama_energy"),
            "fit_error": record.get("rama_I"),
            "lean_status": record.get("lean_status"),
            "physics_mapping": record.get("physics_mapping"),
            "elapsed_sec": round(t_elapsed, 2)
        })

    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(" 🏁 HIGH GENERATION PAGE 50 SEARCH COMPLETE")
    print(f" Total Elapsed Time: {total_time:.2f} seconds")
    print(" Summary of Discovered Candidates:")
    for r in results:
        print(f"  • ID: {r['id']} | Lean: {r['lean_status']} | Energy: {r['energy']:.4f} | Error: {r['fit_error']:.4f}")
        print(f"    Conjecture: {r['conjecture']}")
        print(f"    Physics:    {r['physics_mapping'].splitlines()[0]}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    execute_page50_high_gen()

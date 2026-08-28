"""
tools/run_cache_discovery_batch.py
==================================
Runs the Autonomous Discovery Engine over all live Gemini extractions
currently stored in docs/live_vision_results/cache.json.
Stores discoveries in namagiri.db and generates a structured batch report.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path

sys.path.insert(0, "/home/callensxavier_gmail_com/SocrateAI-Scientific-Agora-RamanujanNeuroSymbolic")

from autonomous_discovery_engine import AutonomousDiscoveryEngine
from src.persistence import NamagiriDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    cache_file = Path("docs/live_vision_results/cache.json")
    if not cache_file.exists():
        print("❌ Cache file docs/live_vision_results/cache.json not found!")
        return

    with open(cache_file, "r", encoding="utf-8") as f:
        cache = json.load(f)

    print("================================================================================")
    print(f" 🚀 RUNNING BATCH DISCOVERY ENGINE OVER {len(cache)} CACHED MANUSCRIPT EXTRACTIONS")
    print("================================================================================")

    engine = AutonomousDiscoveryEngine()
    db = NamagiriDB()

    start_time = time.time()
    results = []
    verified_count = 0

    for idx, (img_hash, extraction_data) in enumerate(cache.items(), 1):
        image_path = extraction_data.get("image_path", f"hash_{img_hash[:8]}")
        filename = os.path.basename(image_path)
        print(f"\n--- [{idx}/{len(cache)}] Processing {filename} ({img_hash[:8]}) ---")

        try:
            # 1. Extraction data
            retrieval_data = extraction_data
            archetype = retrieval_data.get("archetype_hint", "N/A")

            # 2. Intuition (Genetic Evolutionary Search)
            intuition = engine.step_2_antigravity_intuition(retrieval_data, pop_size=20, max_generations=5)

            # 3. Multi-Domain Bridge
            bridge = engine.step_3_deep_think_bridge(intuition, retrieval_data)

            # 4. Lean 4 Formalization
            disc_id = f"disc_{img_hash[:8]}"
            lean_res = engine.step_4_lean4_auto_formalization(disc_id, intuition, bridge, skip_lean=False)
            is_verified = lean_res.get("status") == "VERIFIED"

            if is_verified:
                verified_count += 1
                print(f"  └─ Status: ✅ LEAN VERIFIED")
            else:
                print(f"  └─ Status: ⚠️ UNVERIFIED / OPEN ({lean_res.get('status')})")

            # 5. Physics Mapping
            physics_map = engine.step_5_physical_mapping(intuition, bridge)

            # 6. Database Persistence
            state = intuition.get("state")
            db.insert_discovery({
                "id": disc_id,
                "image_path": image_path,
                "notebook": "ManuscriptCache",
                "chapter": "VisionPipeline",
                "page": filename,
                "archetype": archetype,
                "latex_extracted": retrieval_data.get("raw_latex", ""),
                "conjecture": intuition.get("conjecture", ""),
                "fit_error": intuition.get("metrics", {}).get("i", 0.0),
                "exponents": json.dumps(state.exponents if state else {}),
                "q_shift_24": state.q_shift_24 if state else 0,
                "domain_target": bridge.get("domain_target", ""),
                "physics_detail": physics_map,
                "lean_verified": 1 if is_verified else 0,
                "lean_code": lean_res.get("lean_code", "")
            })

            results.append({
                "index": idx,
                "hash": img_hash,
                "filename": filename,
                "archetype": archetype,
                "conjecture": intuition.get("conjecture", ""),
                "lean_verified": is_verified,
                "domain_target": bridge.get("domain_target", ""),
                "db_id": disc_id
            })

        except Exception as e:
            logging.error(f"Error processing {filename}: {e}", exc_info=True)

    total_time = time.time() - start_time
    stats = db.get_stats()

    report = {
        "title": "Cached Manuscript Extraction Discovery Batch Report",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_extractions_processed": len(cache),
        "verified_count": verified_count,
        "verification_rate_percent": round(verified_count / len(cache) * 100, 2) if len(cache) > 0 else 0.0,
        "total_runtime_sec": round(total_time, 2),
        "database_stats": stats,
        "results": results
    }

    report_path = Path("dualscale/certificates/cache_discovery_batch_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n================================================================================")
    print(" 🏁 BATCH DISCOVERY SOLVE COMPLETE")
    print(f" Total Extractions Processed : {len(cache)}")
    print(f" Lean 4 Verified Discoveries : {verified_count} ({report['verification_rate_percent']}%)")
    print(f" Total Runtime               : {total_time:.2f}s ({total_time / 60:.2f} min)")
    print(f" Database Stats              : {stats}")
    print(f" Report Saved To             : {report_path}")
    print("================================================================================")

if __name__ == "__main__":
    main()

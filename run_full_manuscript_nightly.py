"""
run_full_manuscript_nightly.py
==============================
Executes the Autonomous Discovery Engine on the entire manuscript corpus
(Notebooks 1, 2, and 3) using high-generation evolutionary parameters
(pop_size=50, max_generations=15). Designed for a long, multi-hour night run.
"""

import time
import os
import glob
import logging
from autonomous_discovery_engine import AutonomousDiscoveryEngine
from src.persistence import NamagiriDB

# Setup logging to both console and file
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("nightly_run_full.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

def run_nightly_deep_burn():
    engine = AutonomousDiscoveryEngine()
    db = NamagiriDB()
    
    target_dirs = [
        "input/NoteBook1/**/*.jpg",
        "input/NoteBook2/**/*.jpg",
        "input/NoteBook3/**/*.jpg"
    ]
    
    target_images = []
    for d in target_dirs:
        target_images.extend(glob.glob(d, recursive=True))
        
    logging.info(f"Discovered {len(target_images)} manuscript images for Phase 2 processing.")
    
    # Optional: fetch already verified discoveries if you want to skip them
    # For a full fresh deep burn, we run on all of them.
    
    start_time = time.time()
    success_count = 0
    total_processed = 0
    
    print("\n" + "=" * 80)
    print(" 🌑 INITIATING FULL MANUSCRIPT NIGHT RUN (DEEP BURN)")
    print(f" Target: {len(target_images)} Pages")
    print(" Population Size: 50 | Max Generations: 15")
    print(" Log File: nightly_run_full.log")
    print("=" * 80)

    for idx, img in enumerate(target_images, 1):
        try:
            logging.info(f"--- Processing Page {idx}/{len(target_images)}: {os.path.basename(img)} ---")
            
            # Execute with high-generation settings
            db_id = engine.run_full_pipeline(img, pop_size=50, max_generations=15)
            
            record = db.get_discovery_by_id(db_id)
            if record and record.get("lean_status") == "VERIFIED":
                success_count += 1
                
            total_processed += 1
            
        except KeyboardInterrupt:
            logging.info("Night run interrupted by user.")
            break
        except Exception as e:
            logging.error(f"Error processing {img}: {e}")

    total_time = time.time() - start_time
    logging.info("=" * 80)
    logging.info(" 🏁 NIGHT RUN COMPLETE")
    logging.info(f" Total Processed: {total_processed}/{len(target_images)}")
    logging.info(f" Lean 4 Verified: {success_count} new Zero-Axiom theorems")
    logging.info(f" Total Time:      {total_time/3600:.2f} hours")
    logging.info("=" * 80)

if __name__ == "__main__":
    run_nightly_deep_burn()

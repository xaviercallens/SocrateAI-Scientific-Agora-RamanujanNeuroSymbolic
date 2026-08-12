#!/usr/bin/env python3
"""
tools/vision_pipeline.py — Task 4.1: Gemini Vision Extraction (698 pages)
===========================================================================
A dedicated pipeline script to execute the live Gemini Vision extraction
over the complete Ramanujan manuscript corpus.

This script uses the API Key configured in your environment.
"""

import os
import sys
import glob
import logging
from pathlib import Path

# Add project root to path to import live_vision_extractor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from live_vision_extractor import LiveVisionExtractor, get_api_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_vision_pipeline(dry_run: bool = False, max_pages: int = 10):
    api_key = get_api_key()
    if not api_key:
        logging.error("No Gemini API key found. Please export GEMINI_API_KEY.")
        sys.exit(1)
        
    logging.info("Gemini API Key detected. Initializing Vision Pipeline...")
    extractor = LiveVisionExtractor(api_key)
    
    # Target all manuscript images
    target_dirs = [
        "input/NoteBook1/**/*.jpg", "input/NoteBook1/**/*.png",
        "input/NoteBook2/**/*.jpg", "input/NoteBook2/**/*.png",
        "input/NoteBook3/**/*.jpg", "input/NoteBook3/**/*.png",
        "inputs/**/*.jpg", "inputs/**/*.png"
    ]
    
    image_paths = []
    for pattern in target_dirs:
        image_paths.extend(glob.glob(os.path.join("..", pattern), recursive=True))
        image_paths.extend(glob.glob(pattern, recursive=True))
        
    # Deduplicate and sort
    image_paths = sorted(list(set([os.path.abspath(p) for p in image_paths if os.path.exists(p)])))
    
    if not image_paths:
        logging.warning("No manuscript images found in input/ or inputs/ directories.")
        sys.exit(0)
        
    logging.info(f"Total manuscript pages identified: {len(image_paths)}")
    
    if dry_run:
        logging.info(f"DRY RUN ENABLED. Limiting to first {max_pages} pages.")
        image_paths = image_paths[:max_pages]
        
    out_dir = Path("docs/live_vision_results")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    series_count = 0
    
    logging.info(f"Commencing extraction on {len(image_paths)} pages...")
    for i, img_path in enumerate(image_paths, 1):
        logging.info(f"Processing [{i}/{len(image_paths)}]: {os.path.basename(img_path)}")
        res = extractor.extract_from_image(img_path)
        if res.get("has_series") and len(res.get("coefficients", [])) > 0:
            series_count += 1
            logging.info(f"  -> SUCCESS: Found series with {len(res['coefficients'])} terms.")
        else:
            logging.info("  -> No series detected.")
        results.append(res)
        
    # Summarize
    logging.info("=" * 60)
    logging.info(" VISION PIPELINE COMPLETE")
    logging.info(f" Pages Processed: {len(image_paths)}")
    logging.info(f" Mathematical Series Discovered: {series_count}")
    logging.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Gemini Vision Pipeline for Ramanujan Manuscripts.")
    parser.add_argument("--full", action="store_true", help="Run on the entire 698 page corpus. Otherwise runs a dry-run of 5 pages.")
    args = parser.parse_args()
    
    if args.full:
        run_vision_pipeline(dry_run=False)
    else:
        run_vision_pipeline(dry_run=True, max_pages=5)

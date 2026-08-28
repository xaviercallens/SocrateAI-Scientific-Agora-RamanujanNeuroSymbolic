#!/usr/bin/env python3
"""
tools/vision_pipeline.py — Task 4.1: Gemini Vision Extraction (Manuscripts)
===========================================================================
A dedicated pipeline script to execute live Gemini Vision extraction
over the complete Ramanujan manuscript corpus using GEMINI_API_KEY.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add project root to path to import live_vision_extractor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from live_vision_extractor import LiveVisionExtractor, get_api_key, discover_notebook_images

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_vision_pipeline(dry_run: bool = False, max_pages: int = 10, no_cache: bool = False):
    api_key = get_api_key()
    if not api_key:
        logging.error("No Gemini API key found. Please export GEMINI_API_KEY.")
        sys.exit(1)

    logging.info("Gemini API Key detected. Initializing Vision Pipeline...")
    extractor = LiveVisionExtractor(api_key=api_key)

    image_paths = discover_notebook_images()

    if not image_paths:
        logging.warning("No manuscript images found in workspace directories.")
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
        logging.info(f"Processing [{i}/{len(image_paths)}]: {img_path.name}")
        res = extractor.extract_from_image(str(img_path), use_cache=not no_cache)

        if res.get("has_series") and len(res.get("coefficients", [])) > 0:
            series_count += 1
            logging.info(f"  -> SUCCESS: Found series with {len(res['coefficients'])} terms [{res.get('archetype')}]")
        elif res.get("cached"):
            logging.info(f"  -> [CACHED]: {res.get('archetype', 'Analysed')}")
        else:
            logging.info(f"  -> Context: {res.get('archetype', 'No series')}")

        results.append(res)

    out_file = out_dir / "extraction_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logging.info("=" * 60)
    logging.info(" VISION PIPELINE COMPLETE")
    logging.info(f" Pages Processed: {len(image_paths)}")
    logging.info(f" Mathematical Series Discovered: {series_count}")
    logging.info(f" Results Saved To: {out_file}")
    logging.info("=" * 60)

    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Gemini Vision Pipeline for Ramanujan Manuscripts.")
    parser.add_argument("--full", action="store_true", help="Run on the entire manuscript corpus. Otherwise runs a dry-run of 5 pages.")
    parser.add_argument("--pages", type=int, default=5, help="Number of pages for dry-run")
    parser.add_argument("--no-cache", action="store_true", help="Disable extraction caching")
    args = parser.parse_args()

    run_vision_pipeline(dry_run=not args.full, max_pages=args.pages, no_cache=args.no_cache)

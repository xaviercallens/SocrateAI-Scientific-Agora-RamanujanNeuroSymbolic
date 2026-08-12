"""
live_vision_extractor.py — Task 1.1
=====================================
Replaces the static Mock OCR array in the RAMA pipeline with live
Gemini Vision API calls to extract page-specific q-series data from
Ramanujan manuscript images.

USAGE:
  python3 live_vision_extractor.py [--dry-run] [--pages N] [--output dir]

TASK 1.1 SPEC:
  "Replace the static 'Mock OCR' array with the live vision API.
   Running the full corpus of manuscript pages to extract distinct,
   page-specific q-series coefficients will validate the engine's
   true discovery rate."

REFERENCES:
  - Gemini API: https://ai.google.dev/api/generate-content
  - Target format: JSON list of q-expansion coefficients [a0, a1, ..., aN]
"""

import os
import sys
import json
import base64
import argparse
import sqlite3
import re
import time
from pathlib import Path

# Use the modern google-genai SDK
from google import genai
from google.genai import types

# ============================================================================
# CONFIG
# ============================================================================

MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

EXTRACTION_PROMPT = """You are a specialist in analyzing Ramanujan's mathematical notebooks.

Examine this manuscript page carefully. Your task is to:

1. Identify any q-series, power series, or eta-function expansions on the page.
2. Extract the explicit numerical COEFFICIENTS of the first available series.
3. Return ONLY a JSON object with these fields:
   - "coefficients": a list of integers [a0, a1, a2, ...] (at least 5, up to 15 terms)
   - "formula_text": the formula as written on the page (LaTeX if possible)
   - "page_context": brief description of what mathematical topic is on this page
   - "confidence": "high", "medium", or "low"
   - "has_series": true or false

If no series is visible, return {"has_series": false, "coefficients": [], "formula_text": "", "page_context": "no series found", "confidence": "low"}.

Do NOT invent coefficients. Only extract what is explicitly written.
Return VALID JSON only — no markdown, no explanation."""

# ============================================================================
# EXTRACTOR
# ============================================================================

class LiveVisionExtractor:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = MODEL
        
    def extract_from_image(self, image_path: str) -> dict:
        """Extract q-series coefficients from a single manuscript page image."""
        path = Path(image_path)
        if not path.exists():
            return {"has_series": False, "coefficients": [], "error": f"File not found: {image_path}"}
        
        # Read and encode image
        with open(path, "rb") as f:
            image_bytes = f.read()
        
        # Detect MIME type
        suffix = path.suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png", ".gif": "image/gif",
                    ".webp": "image/webp"}
        mime_type = mime_map.get(suffix, "image/jpeg")
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        EXTRACTION_PROMPT,
                    ],
                )
                
                text = response.text.strip()
                
                # Clean up any markdown wrapping
                text = re.sub(r'^```(?:json)?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)
                text = text.strip()
                
                prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                candidate_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                
                result = json.loads(text)
                result["source_image"] = str(image_path)
                result["model"] = self.model
                result["prompt_tokens"] = prompt_tokens
                result["candidate_tokens"] = candidate_tokens
                return result
                
            except json.JSONDecodeError as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return {"has_series": False, "coefficients": [], 
                        "error": f"JSON parse error: {e}", "raw": text[:200]}
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return {"has_series": False, "coefficients": [], "error": str(e)}
        
        return {"has_series": False, "coefficients": [], "error": "Max retries exceeded"}


def get_api_key() -> str:
    """Try common env vars for Gemini API key."""
    for var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY"]:
        key = os.environ.get(var, "")
        if key:
            return key
    return ""


def main():
    parser = argparse.ArgumentParser(description="Live Gemini Vision extractor for Ramanujan manuscripts")
    parser.add_argument("--dry-run", action="store_true", help="Test with first 3 images only")
    parser.add_argument("--pages", type=int, default=10, help="Number of pages to process (default: 10)")
    parser.add_argument("--output", type=str, default="docs/live_vision_results", help="Output directory")
    parser.add_argument("--image-dir", type=str, default="input/NoteBook1", help="Input image directory")
    parser.add_argument("--api-key", type=str, default="", help="Gemini API key (or set GEMINI_API_KEY env var)")
    args = parser.parse_args()
    
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: No Gemini API key found.")
        print("Set GEMINI_API_KEY environment variable or use --api-key flag.")
        print("Get a key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    # Find images
    image_dir = Path(args.image_dir)
    if not image_dir.exists():
        print(f"WARNING: {image_dir} not found, using test mode with NoteBook image dir structure")
        # List all available image dirs
        for nb_dir in Path("input").glob("NoteBook*"):
            for ch_dir in nb_dir.glob("chapter*"):
                imgs = list(ch_dir.glob("images/*.jpg")) + list(ch_dir.glob("images/*.png"))
                if imgs:
                    image_dir = imgs[0].parent
                    print(f"Found images in: {image_dir}")
                    break
            if image_dir.exists():
                break
    
    images = []
    for pattern in ["**/*.jpg", "**/*.png", "**/*.jpeg"]:
        images.extend(sorted(image_dir.glob(pattern)))
    
    if args.dry_run:
        images = images[:3]
    else:
        images = images[:args.pages]
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Processing {len(images)} images with {MODEL}")
    print(f"Output: {args.output}")
    print("-" * 60)
    
    extractor = LiveVisionExtractor(api_key)
    
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    series_count = 0
    
    for i, img_path in enumerate(images, 1):
        print(f"[{i:3}/{len(images)}] {img_path.name}... ", end="", flush=True)
        
        result = extractor.extract_from_image(str(img_path))
        
        if result.get("has_series") and len(result.get("coefficients", [])) >= 5:
            series_count += 1
            marker = f"✓ {len(result['coefficients'])} terms [{result.get('confidence', '?')}]"
        elif "error" in result:
            marker = f"✗ ERROR: {result['error'][:50]}"
        else:
            marker = "- (no series)"
        
        print(marker)
        results.append(result)
    
    # Save results
    out_file = out_dir / "extraction_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    
    total_prompt_tokens = sum(r.get("prompt_tokens", 0) for r in results)
    total_candidate_tokens = sum(r.get("candidate_tokens", 0) for r in results)
    
    # Gemini 2.5 Flash pricing: $0.075 / 1M prompt tokens, $0.30 / 1M candidate tokens
    cost_input = (total_prompt_tokens / 1_000_000) * 0.075
    cost_output = (total_candidate_tokens / 1_000_000) * 0.30
    total_cost = cost_input + cost_output
    
    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY & COST AUDIT")
    print(f"{'='*60}")
    print(f"Pages processed:        {len(images)}")
    print(f"Series found:           {series_count} ({100*series_count/max(len(images),1):.1f}%)")
    print(f"Total Input Tokens:     {total_prompt_tokens:,}")
    print(f"Total Output Tokens:    {total_candidate_tokens:,}")
    print(f"Dry-run Actual Cost:    ${total_cost:.6f}")
    if len(images) > 0:
        avg_input = total_prompt_tokens / len(images)
        avg_output = total_candidate_tokens / len(images)
        est_698_input = avg_input * 698
        est_698_output = avg_output * 698
        est_698_cost = ((est_698_input / 1_000_000) * 0.075) + ((est_698_output / 1_000_000) * 0.30)
        print(f"Avg Input per page:     {avg_input:.1f} tokens")
        print(f"Avg Output per page:    {avg_output:.1f} tokens")
        print(f"ESTIMATED FULL CORPUS COST (698 pages): ${est_698_cost:.4f} USD (~{est_698_cost*100:.1f} cents)")
    print(f"Output saved to:        {out_file}")
    
    # Show sample
    for r in results[:3]:
        if r.get("has_series") and r.get("coefficients"):
            print(f"\nSample extraction from {r.get('source_image', '?')}")
            print(f"  Formula: {r.get('formula_text', 'N/A')[:80]}")
            print(f"  Coefficients: {r['coefficients'][:8]}")
            print(f"  Context: {r.get('page_context', '')[:60]}")
            break
    
    return results


if __name__ == "__main__":
    main()

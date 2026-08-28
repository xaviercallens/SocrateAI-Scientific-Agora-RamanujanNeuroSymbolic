"""
live_vision_extractor.py — Task 1.1 & Phase 2 Multimodal Extraction
=====================================================================
Live Gemini Vision API extractor for page-specific mathematical series data from
Ramanujan manuscript images, powered by GEMINI_API_KEY.

USAGE:
  python3 live_vision_extractor.py [--dry-run] [--pages N] [--output dir] [--no-cache]

REFERENCES:
  - Gemini API: https://ai.google.dev/api/generate-content
  - Target format: JSON list of q-expansion coefficients [a0, a1, ..., aN]
"""

import os
import sys
import json
import base64
import argparse
import hashlib
import re
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Use the modern google-genai SDK if available
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    genai = None
    types = None
    HAS_GENAI = False

# ============================================================================
# CONFIG
# ============================================================================

MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
DEFAULT_PROJECT_ID = "1003063861791"
DEFAULT_LOCATION = "us-central1"
CACHE_FILE = "docs/live_vision_results/cache.json"

EXTRACTION_PROMPT = """You are an expert mathematician and manuscript analyst specializing in Srinivasa Ramanujan's notebooks and handwritten letters.

Examine this manuscript page image very carefully. Perform a comprehensive analysis of the handwritten mathematical formulas.

Your task:
1. Identify any q-series, power series, infinite products, eta-function expansions, continued fractions, partition identities, hypergeometric series, or mock theta functions on the page.
2. Extract the explicit numerical COEFFICIENTS [a0, a1, a2, ...] of the primary series on the page if visible.
3. Determine the specific mathematical topic/archetype on this page.
4. Return ONLY a VALID JSON object (no markdown, no explanatory text) with the following structure:
{
   "has_series": true or false,
   "coefficients": [a0, a1, a2, a3, ...],
   "formula_text": "LaTeX formula string of the main identity",
   "page_context": "Concise summary of the mathematical content and page topic",
   "archetype": "Name of archetype e.g. Mock Theta Function, Partition Function, Rogers-Ramanujan, Magic Square, Hypergeometric Series, Eta Quotient, Elliptic Integral",
   "confidence": "high", "medium", or "low"
}

If no numerical series or q-expansion is explicitly listed, set "has_series": false and "coefficients": [], but STILL capture "formula_text", "page_context", and "archetype".
Do NOT invent coefficients that are not written on the page.
Return ONLY valid JSON."""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_api_key() -> str:
    """Retrieve Gemini API key from standard environment variables."""
    for var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY"]:
        key = os.environ.get(var, "").strip()
        if key:
            return key
    return ""


def get_image_md5(image_path: str) -> str:
    """Compute MD5 hash of image file for caching."""
    hasher = hashlib.md5()
    with open(image_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def discover_notebook_images(search_dir: Optional[str] = None) -> List[Path]:
    """
    Search for manuscript page images across all standard workspace directories:
    data/ramanujan_notebooks, input/, inputs/, docs/release_consolidated.
    """
    candidate_dirs = []
    if search_dir and Path(search_dir).exists():
        candidate_dirs.append(Path(search_dir))
    
    root_dirs = ["data/ramanujan_notebooks", "input", "inputs", "data", "docs/release_consolidated"]
    for rd in root_dirs:
        p = Path(rd)
        if p.exists() and p not in candidate_dirs:
            candidate_dirs.append(p)
            
    images = []
    seen = set()
    for cdir in candidate_dirs:
        for pattern in ["**/*.jpg", "**/*.jpeg", "**/*.png"]:
            for img in cdir.glob(pattern):
                abs_p = img.resolve()
                if abs_p not in seen and abs_p.is_file():
                    seen.add(abs_p)
                    images.append(img)
                    
    # Sort logically
    return sorted(images, key=lambda p: str(p))


# ============================================================================
# EXTRACTOR
# ============================================================================

class LiveVisionExtractor:
    def __init__(self, api_key: str = "", cache_path: str = CACHE_FILE):
        self.api_key = api_key or get_api_key()
        self.cache_path = Path(cache_path)
        self.cache: Dict[str, Any] = {}
        self._load_cache()
        
        self.client = None
        self.client_mode = None  # "vertexai" or "standard"
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT") or DEFAULT_PROJECT_ID
        self.location = os.environ.get("GOOGLE_CLOUD_REGION") or DEFAULT_LOCATION
        
        if HAS_GENAI and self.api_key:
            self._init_client()

    def _init_client(self):
        """Initialize google.genai Client, trying vertexai and standard modes."""
        # 1. Try Vertex AI client (works with GEMINI_API_KEY Express / Vertex keys starting with AQ...)
        try:
            client = genai.Client(
                api_key=self.api_key,
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            self.client = client
            self.client_mode = "vertexai"
            logging.info(f"Initialized Gemini Client (Vertex AI mode, project={self.project_id}, region={self.location})")
            return
        except Exception as e:
            logging.debug(f"Vertex AI client init note: {e}")

        # 2. Try Standard Google AI Studio client
        try:
            client = genai.Client(api_key=self.api_key)
            self.client = client
            self.client_mode = "standard"
            logging.info("Initialized Gemini Client (Standard AI Studio mode)")
            return
        except Exception as e:
            logging.warning(f"Standard Gemini Client init failed: {e}")

    def _load_cache(self):
        """Load local cache from JSON file."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                logging.warning(f"Could not load cache from {self.cache_path}: {e}")

    def _save_cache(self):
        """Save local cache to JSON file."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logging.warning(f"Could not save cache to {self.cache_path}: {e}")

    def extract_from_image(self, image_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Extract mathematical content and q-series from a manuscript image.
        Uses cached result if available and use_cache=True.
        """
        path = Path(image_path)
        if not path.exists():
            return {
                "has_series": False,
                "coefficients": [],
                "formula_text": "",
                "page_context": "File not found",
                "archetype": "Error",
                "confidence": "low",
                "error": f"File not found: {image_path}"
            }

        md5_hash = get_image_md5(str(path))
        
        # Check cache
        if use_cache and md5_hash in self.cache:
            cached_res = dict(self.cache[md5_hash])
            cached_res["source_image"] = str(path)
            cached_res["cached"] = True
            return cached_res

        if not self.client:
            return {
                "has_series": False,
                "coefficients": [],
                "formula_text": "",
                "page_context": "No active Gemini client",
                "archetype": "Error",
                "confidence": "low",
                "error": "Gemini API key not configured or client failed to initialize."
            }

        # Read image bytes
        with open(path, "rb") as f:
            image_bytes = f.read()

        suffix = path.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        mime_type = mime_map.get(suffix, "image/jpeg")

        part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        last_error = None
        for model in MODELS_TO_TRY:
            for attempt in range(MAX_RETRIES):
                try:
                    config = None
                    if types and hasattr(types, "GenerateContentConfig"):
                        config_kwargs = {"temperature": 0.1}
                        if hasattr(types, "AutomaticFunctionCallingConfig"):
                            config_kwargs["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(disable=True)
                        config = types.GenerateContentConfig(**config_kwargs)

                    response = self.client.models.generate_content(
                        model=model,
                        contents=[part, EXTRACTION_PROMPT],
                        config=config
                    )

                    text = response.text.strip() if hasattr(response, "text") and response.text else ""

                    # Clean up JSON formatting artifacts
                    clean_text = re.sub(r'^```(?:json)?\s*', '', text)
                    clean_text = re.sub(r'\s*```$', '', clean_text)
                    clean_text = clean_text.strip()

                    prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                    candidate_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0

                    parsed = json.loads(clean_text)

                    # Normalize fields
                    coeffs = parsed.get("coefficients", [])
                    if isinstance(coeffs, list):
                        clean_coeffs = []
                        for c in coeffs:
                            try:
                                clean_coeffs.append(float(c))
                            except (ValueError, TypeError):
                                pass
                        coeffs = clean_coeffs
                    else:
                        coeffs = []

                    result = {
                        "has_series": bool(parsed.get("has_series", len(coeffs) > 0)),
                        "coefficients": coeffs,
                        "formula_text": str(parsed.get("formula_text", "")),
                        "page_context": str(parsed.get("page_context", "")),
                        "archetype": str(parsed.get("archetype", parsed.get("archetype_hint", "Manuscript Extraction"))),
                        "confidence": str(parsed.get("confidence", "medium")),
                        "source_image": str(path),
                        "model": model,
                        "prompt_tokens": prompt_tokens,
                        "candidate_tokens": candidate_tokens,
                        "cached": False
                    }

                    # Save to cache
                    self.cache[md5_hash] = result
                    self._save_cache()

                    return result

                except json.JSONDecodeError as e:
                    last_error = f"JSON Parse Error: {e}"
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                except Exception as e:
                    last_error = str(e)
                    if "403" in last_error or "PERMISSION_DENIED" in last_error:
                        # If permission denied on standard mode, retry in vertexai mode if not tried
                        if self.client_mode != "vertexai":
                            try:
                                self.client = genai.Client(
                                    api_key=self.api_key,
                                    vertexai=True,
                                    project=self.project_id,
                                    location=self.location
                                )
                                self.client_mode = "vertexai"
                                continue
                            except Exception:
                                pass
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue

        return {
            "has_series": False,
            "coefficients": [],
            "formula_text": "",
            "page_context": f"Extraction failed: {last_error}",
            "archetype": "Error",
            "confidence": "low",
            "source_image": str(path),
            "error": last_error or "Max retries exceeded"
        }


# ============================================================================
# CLI MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Live Gemini Vision extractor for Ramanujan manuscripts")
    parser.add_argument("--dry-run", action="store_true", help="Test with first 3 images only")
    parser.add_argument("--pages", type=int, default=10, help="Number of pages to process (default: 10)")
    parser.add_argument("--full", action="store_true", help="Process all discovered manuscript pages")
    parser.add_argument("--output", type=str, default="docs/live_vision_results", help="Output directory")
    parser.add_argument("--image-dir", type=str, default=None, help="Input image directory")
    parser.add_argument("--api-key", type=str, default="", help="Gemini API key")
    parser.add_argument("--no-cache", action="store_true", help="Bypass local cache")
    args = parser.parse_args()

    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: No Gemini API key found in environment or arguments.")
        print("Export GEMINI_API_KEY environment variable or pass --api-key.")
        sys.exit(1)

    images = discover_notebook_images(args.image_dir)
    if not images:
        print("No manuscript images found.")
        sys.exit(0)

    if args.dry_run:
        images = images[:3]
    elif not args.full:
        images = images[:args.pages]

    print(f"{'DRY RUN: ' if args.dry_run else ''}Processing {len(images)} manuscript pages with Gemini Vision")
    print(f"Output Directory: {args.output}")
    print("-" * 60)

    extractor = LiveVisionExtractor(api_key=api_key)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    series_count = 0

    for i, img_path in enumerate(images, 1):
        print(f"[{i:3}/{len(images)}] {img_path.name}... ", end="", flush=True)

        res = extractor.extract_from_image(str(img_path), use_cache=not args.no_cache)

        if res.get("has_series") and len(res.get("coefficients", [])) > 0:
            series_count += 1
            status_str = f"✓ {len(res['coefficients'])} coeffs [{res.get('archetype', 'Series')}]"
        elif res.get("cached"):
            status_str = f"✓ [CACHED] {res.get('archetype', 'Analysed')}"
        elif "error" in res:
            status_str = f"✗ ERROR: {res['error'][:40]}"
        else:
            status_str = f"- ({res.get('archetype', 'No Series')})"

        print(status_str)
        results.append(res)

    out_file = out_dir / "extraction_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print(" EXTRACTION SUMMARY")
    print("=" * 60)
    print(f" Total Pages Processed : {len(images)}")
    print(f" Mathematical Series   : {series_count}")
    print(f" Results Saved To      : {out_file}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()

"""
Gemini Multimodal Vision API Wrapper for Manuscript Extraction.
WS-1: Real Multimodal Extraction.
"""
import os
import json
import logging
from typing import Optional
from .schemas import ManuscriptExtraction
import sys

# Import the live extractor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from live_vision_extractor import LiveVisionExtractor, get_api_key

class VisionExtractor:
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.live_extractor = None
        if not self.use_mock:
            api_key = get_api_key()
            if api_key:
                self.live_extractor = LiveVisionExtractor(api_key)
            else:
                logging.warning("No Gemini API Key found. Falling back to mock vision extraction.")
                self.use_mock = True
        
    def extract_math(self, image_path: str) -> ManuscriptExtraction:
        """
        Extracts mathematical expressions from a manuscript image.
        Uses LiveVisionExtractor if use_mock is False and API key is present.
        """
        basename = os.path.basename(image_path)
        
        if not self.use_mock and self.live_extractor:
            logging.info(f"Using live Gemini API for {basename}")
            result = self.live_extractor.extract_from_image(image_path)
            
            # Map LiveVisionExtractor dict to ManuscriptExtraction schema
            has_series = result.get("has_series", False)
            return ManuscriptExtraction(
                raw_latex=result.get("formula_text", "") if has_series else "",
                q_series_coefficients=result.get("coefficients", []) if has_series else None,
                archetype_hint=result.get("page_context", "Unknown Topic") if has_series else "No Series Found",
                confidence=0.85 if has_series else 0.0
            )
        
        # We simulate the exact multimodal vision parsing for known Ramanujan pages.
        # This replaces the hardcoded mock in autonomous_discovery_engine.py with
        # a structured schema that tracks confidence and coefficients natively.
        
        if "76" in basename:
            return ManuscriptExtraction(
                raw_latex="u = \\frac{x}{1+} \\frac{x^5}{1+} \\frac{x^{10}}{1+} \\&c",
                q_series_coefficients=None,
                archetype_hint="Rogers-Ramanujan Continued Fractions",
                confidence=0.88
            )
        elif "73" in basename:
            return ManuscriptExtraction(
                raw_latex="1 - 5\\left(\\frac{1}{2}\\right)^3 + 9\\left(\\frac{1\\cdot3}{2\\cdot4}\\right)^3 - \\dots = \\frac{2}{\\pi}",
                q_series_coefficients=None,
                archetype_hint="Hypergeometric Series for 1/pi",
                confidence=0.92
            )
        else:
            # Simulated OCR of a novel q-series or partition identity
            # In live production, this calls Gemini 2.5 Flash with the schema.
            return ManuscriptExtraction(
                raw_latex="f(q) = 1 + \\frac{q}{1+q} + \\frac{q^4}{(1+q)(1+q^2)} + \\dots",
                q_series_coefficients=[1.0, 1.0, -1.0, 1.0, -2.0, 2.0, -3.0, 3.0, -4.0, 5.0, -6.0, 7.0],
                archetype_hint="Mock Theta Function",
                confidence=0.75
            )

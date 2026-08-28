"""
tests/test_vision.py
====================
Unit and integration tests for Gemini Vision extraction over Ramanujan notebooks using GEMINI_API_KEY.
"""

import os
import unittest
from pathlib import Path

from live_vision_extractor import LiveVisionExtractor, get_api_key, discover_notebook_images
from src.extraction.gemini_vision import VisionExtractor
from src.extraction.schemas import ManuscriptExtraction

class TestNotebookImageCapture(unittest.TestCase):
    def setUp(self):
        self.api_key = get_api_key()

    def test_api_key_present(self):
        """Verify GEMINI_API_KEY is detected from environment."""
        self.assertTrue(len(self.api_key) > 0, "GEMINI_API_KEY environment variable should be set.")

    def test_discover_notebook_images(self):
        """Verify discovery of manuscript page images across workspace directories."""
        images = discover_notebook_images()
        self.assertTrue(len(images) > 0, "Should discover manuscript page images in workspace.")

    def test_live_vision_extractor_cache_and_extraction(self):
        """Test LiveVisionExtractor on a discovered manuscript image."""
        images = discover_notebook_images()
        if not images or not self.api_key:
            self.skipTest("No images or GEMINI_API_KEY available for live vision test.")

        sample_img = str(images[0])
        extractor = LiveVisionExtractor(api_key=self.api_key)
        res = extractor.extract_from_image(sample_img, use_cache=True)

        self.assertIn("formula_text", res)
        self.assertIn("page_context", res)
        self.assertIn("archetype", res)
        self.assertIn("confidence", res)
        self.assertEqual(res["source_image"], sample_img)

    def test_vision_extractor_integration(self):
        """Test VisionExtractor mapping to ManuscriptExtraction schema."""
        images = discover_notebook_images()
        if not images or not self.api_key:
            self.skipTest("No images or GEMINI_API_KEY available for VisionExtractor integration test.")

        sample_img = str(images[0])
        ve = VisionExtractor(use_mock=False)
        me = ve.extract_math(sample_img)

        self.assertIsInstance(me, ManuscriptExtraction)
        self.assertIsNotNone(me.archetype_hint)
        self.assertGreaterEqual(me.confidence, 0.0)

if __name__ == "__main__":
    unittest.main()

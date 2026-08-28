"""
Unit tests for RAMA Multi-Source Data Ingestion & Multi-Domain Physics Mapping
==============================================================================
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.extraction.multi_source_ingestor import MultiSourceIngestor, InputSourceType
from src.physics.domain_mapper import DomainMapper
from autonomous_discovery_engine import AutonomousDiscoveryEngine


class TestMultiSourceAndMultiDomain(unittest.TestCase):
    def setUp(self):
        self.ingestor = MultiSourceIngestor(use_mock_vision=True)
        self.domain_mapper = DomainMapper()
        self.engine = AutonomousDiscoveryEngine(use_mock_vision=True)

    def test_multi_source_ingestion(self):
        # 1. COEFFICIENTS_VECTOR
        res_coeffs = self.ingestor.ingest("coefficients_vector", [1, 1, 2, 3, 5, 7, 11])
        self.assertEqual(res_coeffs.q_series_coefficients[:4], [1.0, 1.0, 2.0, 3.0])

        # 2. OEIS_ID
        res_oeis = self.ingestor.ingest("oeis_id", "A000041")
        self.assertIn("Partition", res_oeis.archetype_hint)
        self.assertEqual(res_oeis.q_series_coefficients[0], 1.0)

        # 3. RAW_LATEX
        res_latex = self.ingestor.ingest("raw_latex", "1 + q + 2q^2 + 3q^3")
        self.assertIsNotNone(res_latex.q_series_coefficients)

        # 4. ARXIV_PAPER
        res_arxiv = self.ingestor.ingest("arxiv_paper", "Paper on mock theta functions and black holes")
        self.assertIn("ArXiv", res_arxiv.archetype_hint)

    def test_multi_domain_mapping(self):
        # 1. Hydrodynamics
        m_hydro = self.domain_mapper.map_domain("Navier-Stokes fluid flow", k_weight=1.0, c_eff=0.356277, exponents={1: 1, 5: -1})
        self.assertEqual(m_hydro["domain_target"], "Arnold Symplectic Hydrodynamics")
        self.assertIn("Liquid Dimension", m_hydro["shadow"])

        # 2. String Theory K3
        m_k3 = self.domain_mapper.map_domain("BPS Ground State", k_weight=0.5, c_eff=1.0, exponents={1: 1})
        self.assertIn("String Theory", m_k3["domain_target"])

        # 3. Kerr Gravity
        m_kerr = self.domain_mapper.map_domain("Kerr Black Hole", k_weight=-91.5, c_eff=0.356277, exponents={1: 24})
        self.assertIn("Kerr", m_kerr["domain_target"])

        # 4. QCD Triadic Confinement
        m_qcd = self.domain_mapper.map_domain("Baryon Quark Confinement", k_weight=1.5, c_eff=0.5, exponents={1: 3})
        self.assertIn("QCD", m_qcd["domain_target"])

        # 5. Quantum Chaos
        m_chaos = self.domain_mapper.map_domain("Spectral gap Alon-Boppana", k_weight=0.0, c_eff=0.0, exponents={})
        self.assertIn("Quantum Chaos", m_chaos["domain_target"])

    def test_engine_multi_source_execution(self):
        # Test full engine with OEIS source and skip_lean=True for instant execution
        db_id = self.engine.run_full_pipeline("A000041", source_type="oeis_id", pop_size=20, max_generations=2, skip_lean=True)
        self.assertTrue(len(db_id) > 0)


if __name__ == "__main__":
    unittest.main()

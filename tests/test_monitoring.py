"""
Tests for RAMA Monitoring and Database Query Engines
====================================================
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.monitor_rama import RAMAProgressMonitor
from query_db import show_stats, list_discoveries, export_json_dataset, format_dirac_state, format_partition_projection, parse_state_spectrum, classify_symmetry_class
from src.persistence.database import NamagiriDB


class TestMonitoringAndQuery(unittest.TestCase):
    def setUp(self):
        self.db = NamagiriDB()
        self.monitor = RAMAProgressMonitor()

    def test_monitor_parse_state(self):
        state = self.monitor.parse_state()
        self.assertIn("log", state)
        self.assertIn("db", state)
        self.assertIn("total", state["db"])
        self.assertGreater(state["db"]["total"], 0)
        self.assertGreater(state["db"]["verified"], 0)

    def test_sync_web_json(self):
        state = self.monitor.parse_state()
        self.monitor.sync_web_json(state)
        self.assertTrue(os.path.exists("dashboard_data.json"))

        with open("dashboard_data.json", "r") as f:
            data = json.load(f)

        self.assertIn("stats", data)
        self.assertIn("verified_theorems", data)
        self.assertGreaterEqual(data["stats"]["total"], 0)

    def test_database_stats_retrieval(self):
        stats = self.db.get_stats()
        self.assertIn("total", stats)
        self.assertIn("verified", stats)
        self.assertIn("failed", stats)

    def test_export_json_dataset(self):
        tmp_export = "/tmp/test_namagiri_export.json"
        export_json_dataset(self.db, tmp_export)
        self.assertTrue(os.path.exists(tmp_export))

    def test_dirac_state_formatting(self):
        exps = {1: 1, 5: -1, 6: 2}
        dirac = format_dirac_state(exps, q_shift=2, k_weight=1.0, c_eff=1.1333)
        self.assertIn("r₁=1", dirac)
        self.assertIn("r₅=-1", dirac)
        self.assertIn("r₆=2", dirac)
        self.assertIn("Ŵ = 1", dirac)
        self.assertIn("Ĉ = 1.1333", dirac)

        proj = format_partition_projection(exps, q_shift=2)
        self.assertIn("⟨τ|Ω_r⟩", proj)
        self.assertIn("η(τ)", proj)
        self.assertIn("η(5τ)⁻¹", proj)

        # Classification
        self.assertIn("Classe I", classify_symmetry_class(0.5))
        self.assertIn("Classe II", classify_symmetry_class(0.0))
        self.assertIn("Classe III", classify_symmetry_class(8.0))
        self.assertIn("Classe III", classify_symmetry_class(-91.5))

    def test_f1_wald_kerr_standalone_script(self):
        from test_f1_wald_kerr import execute_f1_test
        verdict = execute_f1_test(verbose=False)
        self.assertIn("asymptotic_entropy_ratio", verdict)
        self.assertAlmostEqual(verdict["asymptotic_entropy_ratio"], 0.34461418, places=4)
        self.assertEqual(verdict["verdict"]["direct_kerr_identity"], "FALSIFIED")
        self.assertEqual(verdict["verdict"]["holographic_subcft"], "CONFIRMED")
        self.assertEqual(verdict["verdict"]["arnold_hydrodynamics"], "VALIDATED")

    def test_failed_diagnostics(self):
        from query_db import show_failed_diagnostics
        show_failed_diagnostics(self.db)


if __name__ == "__main__":
    unittest.main()

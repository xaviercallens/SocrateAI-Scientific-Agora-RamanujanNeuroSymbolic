"""
Tests for Newman Modular Form Operator and HoloAlg Integration
==============================================================
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.physics.holoalg import RamanujanState, NewmanModularFormOperator, HoloAlgMasterEngine


class TestNewmanOperator(unittest.TestCase):
    def setUp(self):
        self.newman_op = NewmanModularFormOperator()
        self.holo_engine = HoloAlgMasterEngine()

    def test_level_computation(self):
        # f(τ) = η(2τ)^2 η(4τ)^(-1) -> level lcm(2, 4) = 4
        state = RamanujanState(exponents={2: 2, 4: -1})
        self.assertEqual(self.newman_op.compute_level(state), 4)

        # f(τ) = η(3τ) η(5τ) -> level lcm(3, 5) = 15
        state2 = RamanujanState(exponents={3: 1, 5: 1})
        self.assertEqual(self.newman_op.compute_level(state2), 15)

    def test_delta_modular_form(self):
        # Ramanujan Delta: η(τ)^24 on SL_2(ℤ) = Γ_0(1)
        # Weight k = 12, 1*24 ≡ 0 (mod 24), cusp ord_1 = 1 > 0 -> Cusp form
        state_delta = RamanujanState(exponents={1: 24})
        res = self.newman_op.check_newman_congruences(state_delta)
        self.assertEqual(res["level_N"], 1)
        self.assertEqual(res["weight_k"], 12.0)
        self.assertTrue(res["mod24_d_congruence"])
        self.assertTrue(res["mod24_nd_congruence"])
        self.assertTrue(res["is_cusp_form"])
        self.assertEqual(self.newman_op.act(state_delta), 2.0)

    def test_holoalg_master_engine_analysis_with_newman(self):
        # Analyze state with HoloAlg Master Engine
        analysis = self.holo_engine.analyze_state(exponents={1: 24}, conjecture_id="DELTA-STATE")
        self.assertIn("newman", analysis["operators"])
        self.assertTrue(analysis["operators"]["newman"]["is_cusp_form"])
        self.assertIn("Newman Congruence:", analysis["demonstration"])


if __name__ == "__main__":
    unittest.main()

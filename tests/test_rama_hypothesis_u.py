"""
tests/test_rama_hypothesis_u.py
================================
Unit tests for the 4-step RAMA Hypothesis U proof solver.
"""

import unittest
from src.physics.rama_hypothesis_u_solver import RAMAHypothesisUSolver

class TestRAMAHypothesisU(unittest.TestCase):
    def setUp(self):
        self.solver = RAMAHypothesisUSolver(alpha_prime=0.01)

    def test_step1_sum_of_tails(self):
        res = self.solver.step1_sum_of_tails_bound(0.01)
        self.assertTrue(res["is_bounded"])
        self.assertEqual(res["status"], "PASS")

    def test_step2_elliptic_integral(self):
        res = self.solver.step2_elliptic_integral_lipschitz_bound(0.01)
        self.assertTrue(res["is_finite"])
        self.assertGreater(res["lipschitz_modulus"], 0)

    def test_step3_spectral_gap(self):
        res = self.solver.step3_spectral_gap_echo_annihilation(degree=6)
        self.assertTrue(res["echoes_annihilated"])
        self.assertLess(res["decoupling_factor"], 1.0)

    def test_step4_continued_fractions(self):
        res = self.solver.step4_continued_fraction_fracture()
        self.assertEqual(res["hausdorff_dimension"], 0.0)
        self.assertTrue(res["is_zero_dimension"])

    def test_full_proof_execution(self):
        cert = self.solver.execute_full_proof(alpha_prime=0.01)
        self.assertTrue(cert["all_steps_verified"])
        self.assertEqual(len(cert["steps"]), 4)

if __name__ == "__main__":
    unittest.main()

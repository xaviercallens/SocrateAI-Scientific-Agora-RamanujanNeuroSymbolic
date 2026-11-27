"""
tests/test_rama_hypothesis_u.py
================================
Unit tests for the Tier-C RAMA Hypothesis U heuristic scaling estimator.
Verifies threshold behavior, input validation, non-proof epistemic flags,
and zero side-effect writes to `dualscale/certificates/`.
"""

import os
import tempfile
import unittest

from src.physics.rama_hypothesis_u_solver import (
    RAMAHypothesisUEstimator,
    RAMAHypothesisUSolver,
)


class TestRAMAHypothesisU(unittest.TestCase):
    def setUp(self) -> None:
        self.solver = RAMAHypothesisUSolver(alpha_prime=0.01)

    def test_step1_sum_of_tails_pass_and_fail(self) -> None:
        res_ok = self.solver.step1_sum_of_tails_bound(0.01)
        self.assertTrue(res_ok["is_bounded"])
        self.assertEqual(res_ok["status"], "HEURISTIC_SATISFIED")

        res_fail = self.solver.step1_sum_of_tails_bound(0.6)
        self.assertFalse(res_fail["is_bounded"])
        self.assertGreater(res_fail["tail_bound"], 1.0)
        self.assertEqual(res_fail["status"], "THRESHOLD_EXCEEDED")

    def test_step2_elliptic_integral(self) -> None:
        res = self.solver.step2_elliptic_integral_lipschitz_bound(0.01)
        self.assertTrue(res["is_finite"])
        self.assertGreater(res["lipschitz_modulus"], 0.0)
        self.assertEqual(res["status"], "HEURISTIC_SATISFIED")

    def test_step3_spectral_gap_pass_and_fail(self) -> None:
        res_ok = self.solver.step3_spectral_gap_echo_annihilation(degree=6)
        self.assertTrue(res_ok["echoes_annihilated"])
        self.assertLess(res_ok["decoupling_factor"], 1.0)
        self.assertEqual(res_ok["status"], "HEURISTIC_SATISFIED")

        res_fail = self.solver.step3_spectral_gap_echo_annihilation(degree=2)
        self.assertFalse(res_fail["echoes_annihilated"])
        self.assertEqual(res_fail["decoupling_factor"], 1.0)
        self.assertEqual(res_fail["status"], "THRESHOLD_EXCEEDED")

    def test_step4_continued_fractions_is_conjectural_open(self) -> None:
        res = self.solver.step4_continued_fraction_fracture()
        self.assertEqual(res["conjectured_hausdorff_dimension"], 0.0)
        self.assertFalse(res["is_zero_dimension_proven"])
        self.assertFalse(res["proven"])
        self.assertEqual(res["status"], "CONJECTURAL_OPEN")
        self.assertEqual(res["epistemic_tier"], "C")

    def test_estimate_scaling_heuristics_is_non_proof_and_no_disk_write(self) -> None:
        cert_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "dualscale",
                "certificates",
                "hypothesis_u_rama_proof_certificate.json",
            )
        )
        existed_before = os.path.exists(cert_path)
        mtime_before = os.path.getmtime(cert_path) if existed_before else None

        estimator = RAMAHypothesisUEstimator(alpha_prime=0.01)
        report = estimator.estimate_scaling_heuristics()
        self.assertFalse(report["is_rigorous_proof"])
        self.assertFalse(report["all_steps_verified"])
        self.assertTrue(report["heuristic_thresholds_met"])
        self.assertEqual(report["epistemic_tier"], "C")
        self.assertEqual(len(report["steps"]), 4)

        # Threshold failure propagates to heuristic_thresholds_met
        report_fail = self.solver.execute_full_proof(alpha_prime=0.6)
        self.assertFalse(report_fail["is_rigorous_proof"])
        self.assertFalse(report_fail["all_steps_verified"])
        self.assertFalse(report_fail["heuristic_thresholds_met"])

        # Default output_path=None must not create or modify tracked certificates
        if existed_before:
            self.assertEqual(os.path.getmtime(cert_path), mtime_before)
        else:
            self.assertFalse(os.path.exists(cert_path))

    def test_optional_explicit_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "heuristic_report.json")
            self.solver.estimate_scaling_heuristics(alpha_prime=0.01, output_path=out_file)
            self.assertTrue(os.path.isfile(out_file))

    def test_validation_errors(self) -> None:
        for bad_alpha in [0.0, -0.1, 1.0, 1.5, float("nan")]:
            with self.assertRaises(ValueError):
                RAMAHypothesisUSolver(alpha_prime=bad_alpha)
            with self.assertRaises(ValueError):
                self.solver.step1_sum_of_tails_bound(bad_alpha)
            with self.assertRaises(ValueError):
                self.solver.step2_elliptic_integral_lipschitz_bound(bad_alpha)

        for bad_deg in [0, 1, -3]:
            with self.assertRaises(ValueError):
                self.solver.step3_spectral_gap_echo_annihilation(degree=bad_deg)


if __name__ == "__main__":
    unittest.main()

"""
Tests for HoloAlg Operator Formalism and Category Theory Engine
================================================================
"""

import unittest
import json
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.physics.holoalg import (
    RamanujanState,
    SupersymmetryOperator,
    CentralChargeOperator,
    GroundEnergyOperator,
    ModularInversionOperator,
    CategoryN_Object,
    CategoryG_Object,
    CategoryF_Object,
    HoloAlgFunctor,
    DualScaleFunctor,
    HoloAlgMasterEngine
)
from src.lean.code_generator import LeanCodeGenerator
from src.persistence.database import NamagiriDB


class TestHoloAlg(unittest.TestCase):

    def setUp(self):
        self.w_op = SupersymmetryOperator()
        self.c_op = CentralChargeOperator()
        self.e0_op = GroundEnergyOperator()
        self.s_op = ModularInversionOperator()
        self.engine = HoloAlgMasterEngine(kappa=1.0, n_level=1.0)

    def test_state_braket_representation(self):
        # State: η(τ)^2 η(3τ)^(-1)
        state = RamanujanState(exponents={1: 2, 3: -1}, q_shift_24=0)
        self.assertEqual(state.to_braket(), "|Ω_(r_1=2, r_3=-1)⟩")
        self.assertIn("\\vert \\Omega_", state.to_latex_braket())
        self.assertIn("\\mathcal{Z}(\\tau)", state.partition_function_latex())

    def test_operators_eigenvalues(self):
        # BPS state: weight k = (1/2) * (1) = 0.5
        state_bps = RamanujanState(exponents={2: 1})
        self.assertEqual(self.w_op.act(state_bps), 0.5)
        self.assertTrue(self.w_op.is_bps_protected(state_bps))
        self.assertEqual(self.c_op.act(state_bps), 0.5)
        self.assertTrue(self.c_op.is_unitary(state_bps))

        # Weight k = (1/2) * (2 + 2) = 2.0 (Non-BPS)
        state_non_bps = RamanujanState(exponents={1: 2, 4: 2})
        self.assertEqual(self.w_op.act(state_non_bps), 2.0)
        self.assertFalse(self.w_op.is_bps_protected(state_non_bps))

    def test_categorical_functors(self):
        # State: η(τ)^1 -> k = 0.5, c_eff = 1.0
        state = RamanujanState(exponents={1: 1})
        obj_N = CategoryN_Object(
            state=state,
            weight_k=self.w_op.act(state),
            c_eff=self.c_op.act(state),
            is_bps=self.w_op.is_bps_protected(state)
        )
        
        # HoloAlg Functor Φ: N → G
        phi = HoloAlgFunctor(n_level=1.0)
        obj_G = phi.map_object(obj_N)
        self.assertGreater(obj_G.bps_entropy, 0.0)
        self.assertTrue(obj_G.is_stable_vacuum)

        # DualScale Functor Ψ: G → F
        psi = DualScaleFunctor(kappa=1.5)
        obj_F = psi.map_object(obj_G)
        self.assertAlmostEqual(obj_F.enstrophy_bound, 1.5 * obj_G.bps_entropy)
        self.assertTrue(obj_F.is_globally_regular)

    def test_3act_demonstration_generation(self):
        analysis = self.engine.analyze_state(
            exponents={1: 1},
            q_shift_24=0,
            conjecture_id="TEST-DISCOVERY-1"
        )
        demo = analysis["demonstration"]
        self.assertIn("HOLOALG 3-ACT THEOREM DEMONSTRATION", demo)
        self.assertIn("ACT I: THE ALGEBRAIC FOUNDATION", demo)
        self.assertIn("ACT II: THE HOLOGRAPHIC DICTIONARY", demo)
        self.assertIn("ACT III: THE NAVIER-STOKES RESOLUTION", demo)
        self.assertIn("Aubin-Lions Compactness Lemma", demo)

    def test_lean_code_generator_holoalg(self):
        gen = LeanCodeGenerator()
        code = gen.generate_verification_file(
            "TEST-101",
            {"exponents": {1: 1, 2: 2}, "shadow": "MockShadow", "domain": "String Theory (K3)"}
        )
        self.assertIn("open DualScale.HoloAlg", code)
        self.assertIn("def state : RamanujanState", code)
        self.assertIn("theorem verify_weight : OpW state = state.weight", code)
        self.assertIn("theorem verify_c_eff : OpC state = state.c_eff", code)

    def test_database_holoalg_persistence(self):
        db = NamagiriDB(db_path=":memory:")
        analysis = self.engine.analyze_state(exponents={2: 1}, conjecture_id="DB-TEST")
        disc_id = db.insert_discovery({
            "image_path": "test://img.png",
            "archetype": "Topological Vacuum",
            "conjecture": analysis["partition_function"],
            "eta_exponents": json.dumps({2: 1}),
            "q_shift": 0,
            "braket_notation": analysis["braket"],
            "w_eigenvalue": analysis["operators"]["W_eigenvalue"],
            "c_eigenvalue": analysis["operators"]["C_eigenvalue"],
            "is_bps_protected": analysis["operators"]["is_bps_protected"],
            "demonstration_3act": analysis["demonstration"]
        })
        self.assertTrue(len(disc_id) > 0)


if __name__ == "__main__":
    unittest.main()

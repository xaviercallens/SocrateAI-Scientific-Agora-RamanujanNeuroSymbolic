"""
Project NAMAGIRI — Fitness Gate & Energy Evaluator (WS-7)
Calculates raw RAMA energy and applies Lean 4 verification as an absolute fitness gate.
"""
import sys
import os
import uuid
import logging
from typing import Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from rama_framework import EnergyWeights, EtaQuotientState, TrackAInverseEngineering
from src.lean.code_generator import LeanCodeGenerator
from src.lean.verifier import LeanVerifier


class FitnessEvaluator:
    def __init__(self, target_coeffs, weights: EnergyWeights = None):
        self.track_a = TrackAInverseEngineering(target_coeffs, d_max=12)
        self.weights = weights or EnergyWeights(alpha=1.0, beta=1.0, gamma=0.2)
        
        self.lean_gen = LeanCodeGenerator()
        self.lean_ver = LeanVerifier()

    def evaluate_energy(self, state: EtaQuotientState) -> Tuple[float, float, float, float]:
        """Returns total energy, C, I, D."""
        C, I, D = self.track_a.compute_metrics(state)
        energy = self.weights.alpha * C + self.weights.beta * I + self.weights.gamma * D
        return energy, C, I, D

    def lean_fitness_gate(self, state: EtaQuotientState) -> bool:
        """
        The absolute Lean 4 fitness gate. 
        If the state's arithmetic coefficients can't be structurally verified, it dies.
        """
        # We only pass low-energy candidates to the Lean compiler to save time
        energy, _, I, _ = self.evaluate_energy(state)
        
        # If the fit is terrible, don't even bother waking up Lean
        if I > 0.5:
            return False
            
        conjecture_id = f"gen_cand_{str(uuid.uuid4())[:8]}"
        lean_code = self.lean_gen.generate_tier_a_eta_quotient_verification(
            conjecture_id, 
            state.exponents, 
            state.q_shift_24
        )
        
        # We don't retry here - evolutionary pressure requires strict survival
        success, _, _ = self.lean_ver.verify(lean_code, filename="evo_gate.lean", retries=1)
        
        if success:
            logging.info(f"    [FITNESS GATE PASSED] Candidate {conjecture_id} verified mathematically.")
        else:
            logging.debug(f"    [FITNESS GATE FAILED] Candidate {conjecture_id} killed.")
            
        return success

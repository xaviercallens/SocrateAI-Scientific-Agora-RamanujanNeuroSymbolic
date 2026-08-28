"""
Tests for Memetic RAMA Evolution, Seeding, and Genetic Operators
================================================================
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rama_framework import EtaQuotientState
from src.evolution.population import PopulationManager
from src.evolution.fitness import FitnessEvaluator
from src.evolution.genetic_rama import GeneticRAMAEngine


class TestMemeticEvolution(unittest.TestCase):
    def setUp(self):
        # Target coefficients for partition function p(n) generator: 1/η(q)
        # Expansion: 1 + 1q + 2q^2 + 3q^3 + 5q^4 + 7q^5 + 11q^6 + 15q^7
        self.target_coeffs = [1.0, 1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 15.0]
        self.pop_mgr = PopulationManager(d_max=12)
        self.fitness = FitnessEvaluator(self.target_coeffs)

    def test_population_initialization_with_seeds(self):
        pop = self.pop_mgr.generate_initial_population(pop_size=20, include_newman_seeds=True)
        self.assertEqual(len(pop), 20)
        # Verify that partition seed {1: -1} is present
        has_partition_seed = any(s.exponents == {1: -1} for s in pop)
        self.assertTrue(has_partition_seed)

    def test_memetic_polish(self):
        # Perturbed state: {1: -2} instead of optimal {1: -1}
        perturbed = EtaQuotientState(q_shift_24=0, exponents={1: -2})
        initial_energy, _, _, _ = self.fitness.evaluate_energy(perturbed)

        polished = self.pop_mgr.memetic_polish(perturbed, self.fitness, max_steps=5)
        polished_energy, _, _, _ = self.fitness.evaluate_energy(polished)

        self.assertLessEqual(polished_energy, initial_energy)
        # Should discover exact {1: -1}
        self.assertEqual(polished.exponents, {1: -1})

    def test_genetic_rama_engine_run_with_callback(self):
        callback_history = []

        def on_gen(gen, max_gen, best_e, diversity, best_state):
            callback_history.append((gen, best_e, diversity))

        engine = GeneticRAMAEngine(
            target_coeffs=self.target_coeffs,
            pop_size=20,
            max_generations=5,
            memetic_polish=True
        )
        best_state, history = engine.run(progress_callback=on_gen)

        self.assertIsNotNone(best_state)
        self.assertEqual(len(history), 5)
        self.assertEqual(len(callback_history), 5)
        self.assertLessEqual(history[-1]["best_energy"], history[0]["best_energy"])


if __name__ == "__main__":
    unittest.main()

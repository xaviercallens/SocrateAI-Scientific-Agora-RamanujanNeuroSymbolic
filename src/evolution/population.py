"""
Project NAMAGIRI — Population Management & Genetic Operators (WS-7)
Handles crossover and mutation of symbolic states for the Genetic RAMA engine.
"""
import random
from typing import List, Dict
import numpy as np

# We import the base state from our rama_framework
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from rama_framework import EtaQuotientState


class PopulationManager:
    def __init__(self, d_max: int = 12):
        self.d_max = d_max

    def generate_initial_population(self, pop_size: int = 50) -> List[EtaQuotientState]:
        """Generate a diverse initial population of eta-quotient states."""
        pop = []
        for _ in range(pop_size):
            # Start with random small exponents on a few dividers
            num_factors = random.randint(1, 4)
            exponents = {}
            for _ in range(num_factors):
                d = random.randint(1, self.d_max)
                r = random.choice([-24, -12, -4, -3, -2, -1, 1, 2, 3, 4, 12, 24])
                exponents[d] = exponents.get(d, 0) + r
            
            # Clean up zero exponents
            exponents = {d: r for d, r in exponents.items() if r != 0}
            if not exponents:
                exponents = {1: 1}
                
            q_shift = random.choice([-24, -12, -4, -2, 0, 2, 4, 12, 24])
            pop.append(EtaQuotientState(q_shift_24=q_shift, exponents=exponents))
        return pop

    def crossover(self, parent_a: EtaQuotientState, parent_b: EtaQuotientState) -> EtaQuotientState:
        """
        Exchange exponent mappings between two parent states.
        E.g., Parent A contributes {1: -1}, Parent B contributes {3: -2}.
        Child gets {1: -1, 3: -2}.
        """
        child_exp = {}
        all_ds = set(parent_a.exponents.keys()).union(set(parent_b.exponents.keys()))
        
        for d in all_ds:
            if d in parent_a.exponents and d in parent_b.exponents:
                # If both have it, randomly pick one or average
                if random.random() < 0.5:
                    child_exp[d] = parent_a.exponents[d]
                else:
                    child_exp[d] = parent_b.exponents[d]
            elif d in parent_a.exponents:
                if random.random() < 0.7:  # 70% chance to inherit trait
                    child_exp[d] = parent_a.exponents[d]
            else:
                if random.random() < 0.7:
                    child_exp[d] = parent_b.exponents[d]
                    
        # Mix q_shifts
        if random.random() < 0.5:
            child_shift = parent_a.q_shift_24
        else:
            child_shift = parent_b.q_shift_24
            
        return EtaQuotientState(q_shift_24=child_shift, exponents=child_exp)

    def mutate(self, state: EtaQuotientState, mutation_rate: float = 0.2) -> EtaQuotientState:
        """Apply random micro-operators to a state."""
        mutated = state.copy()
        
        if random.random() < mutation_rate:
            # Exponent edit
            d = random.randint(1, self.d_max)
            delta = random.choice([-4, -2, -1, 1, 2, 4])
            mutated.exponents[d] = mutated.exponents.get(d, 0) + delta
            if mutated.exponents[d] == 0:
                del mutated.exponents[d]
                
        if random.random() < mutation_rate:
            # Modular shift edit
            mutated.q_shift_24 += random.choice([-24, -1, 1, 24])
            
        if random.random() < mutation_rate:
            # Cyclotomic jump
            if mutated.exponents:
                d = random.choice(list(mutated.exponents.keys()))
                r = mutated.exponents[d]
                m = random.choice([2, 3])
                if d * m <= self.d_max:
                    del mutated.exponents[d]
                    mutated.exponents[d * m] = mutated.exponents.get(d * m, 0) + r
                    
        return mutated

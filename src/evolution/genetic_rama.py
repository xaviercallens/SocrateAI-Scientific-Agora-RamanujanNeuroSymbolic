"""
Project NAMAGIRI — Genetic RAMA Engine (WS-7)
Replaces single-trajectory simulated annealing with population-based evolutionary search.
"""
import logging
from typing import List, Tuple, Any

from src.evolution.population import PopulationManager
from src.evolution.fitness import FitnessEvaluator


class GeneticRAMAEngine:
    """Evolutionary intuition engine driving combinatorial discovery."""
    
    def __init__(self, target_coeffs, pop_size=50, max_generations=15, lean_gated=False):
        self.pop_size = pop_size
        self.max_generations = max_generations
        self.lean_gated = lean_gated
        
        self.pop_manager = PopulationManager(d_max=12)
        self.fitness = FitnessEvaluator(target_coeffs)

    def run(self) -> Tuple[Any, List[dict]]:
        """Executes the genetic algorithm. Returns the best state and a history of the population."""
        logging.info(f"  [GeneticRAMA] Initializing population of {self.pop_size} symbolic states...")
        population = self.pop_manager.generate_initial_population(self.pop_size)
        
        history = []
        best_overall_state = None
        best_overall_energy = float('inf')
        
        for gen in range(self.max_generations):
            # 1. Evaluate Fitness
            scored_pop = []
            for state in population:
                energy, C, I, D = self.fitness.evaluate_energy(state)
                scored_pop.append((energy, state, C, I, D))
                
            # Sort by lowest energy
            scored_pop.sort(key=lambda x: x[0])
            
            # Update overall best
            if scored_pop[0][0] < best_overall_energy:
                best_overall_energy = scored_pop[0][0]
                best_overall_state = scored_pop[0][1]
                
            # Calculate Diversity (unique exponent sets)
            unique_configs = len(set(str(s.exponents) for _, s, _, _, _ in scored_pop))
            
            # Log generation stats
            logging.info(f"  [GeneticRAMA] Gen {gen+1}/{self.max_generations} | Best E: {scored_pop[0][0]:.4f} | Diversity: {unique_configs}/{self.pop_size}")
            
            history.append({
                "generation": gen,
                "best_energy": scored_pop[0][0],
                "avg_energy": sum(x[0] for x in scored_pop) / len(scored_pop),
                "diversity": unique_configs
            })
            
            # 2. Lean 4 Fitness Gate (Axiomatic Cull)
            if self.lean_gated:
                # We only gate the top 10% to prevent massive compilation overhead
                top_candidates = [s for _, s, _, _, _ in scored_pop[:max(2, self.pop_size // 10)]]
                survivors = []
                for cand in top_candidates:
                    if self.fitness.lean_fitness_gate(cand):
                        survivors.append(cand)
                
                # If all died, we need to inject immigrants
                if not survivors:
                    logging.warning("  [GeneticRAMA] Mass extinction at Lean Gate. Injecting immigrants.")
                    survivors = self.pop_manager.generate_initial_population(5)
            else:
                survivors = [s for _, s, _, _, _ in scored_pop[:self.pop_size // 2]]
                
            # 3. Selection & Crossover (Tournament)
            next_gen = survivors.copy()
            while len(next_gen) < self.pop_size:
                # Tournament selection
                p1 = self._tournament_select(scored_pop)
                p2 = self._tournament_select(scored_pop)
                
                child = self.pop_manager.crossover(p1, p2)
                
                # 4. Mutation
                child = self.pop_manager.mutate(child, mutation_rate=0.3)
                next_gen.append(child)
                
            # 5. Immigrant Injection (Diversity preservation)
            if unique_configs < 5:
                immigrants = self.pop_manager.generate_initial_population(5)
                next_gen[-5:] = immigrants
                
            population = next_gen
            
        logging.info(f"  [GeneticRAMA] Evolution complete. Global Best Energy: {best_overall_energy:.4f}")
        return best_overall_state, history

    def _tournament_select(self, scored_pop, k=3):
        import random
        # Select k random individuals, return the one with lowest energy
        contestants = random.sample(scored_pop, min(k, len(scored_pop)))
        contestants.sort(key=lambda x: x[0])
        return contestants[0][1]

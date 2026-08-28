"""
Project NAMAGIRI — Genetic RAMA Engine (WS-7)
Replaces single-trajectory simulated annealing with population-based evolutionary search.
"""
import logging
from typing import List, Tuple, Any

from src.evolution.population import PopulationManager
from src.evolution.fitness import FitnessEvaluator


class GeneticRAMAEngine:
    """Evolutionary intuition engine driving combinatorial discovery with memetic refinement."""
    
    def __init__(self, target_coeffs, pop_size=50, max_generations=15, lean_gated=False, memetic_polish=True):
        self.pop_size = pop_size
        self.max_generations = max_generations
        self.lean_gated = lean_gated
        self.enable_memetic = memetic_polish
        
        self.pop_manager = PopulationManager(d_max=12)
        self.fitness = FitnessEvaluator(target_coeffs)

    def run(self, progress_callback=None) -> Tuple[Any, List[dict]]:
        """Executes the genetic algorithm. Returns the best state and a history of the population."""
        logging.info(f"  [GeneticRAMA] Initializing population of {self.pop_size} symbolic states (memetic={self.enable_memetic})...")
        population = self.pop_manager.generate_initial_population(self.pop_size, include_newman_seeds=True)
        
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
            
            # Memetic local polish on top elite candidate
            if self.enable_memetic and scored_pop:
                top_state = scored_pop[0][1]
                polished_state = self.pop_manager.memetic_polish(top_state, self.fitness, max_steps=6)
                p_energy, p_C, p_I, p_D = self.fitness.evaluate_energy(polished_state)
                if p_energy < scored_pop[0][0]:
                    scored_pop[0] = (p_energy, polished_state, p_C, p_I, p_D)
                    population[0] = polished_state
                    scored_pop.sort(key=lambda x: x[0])

            # Update overall best
            if scored_pop[0][0] < best_overall_energy:
                best_overall_energy = scored_pop[0][0]
                best_overall_state = scored_pop[0][1]
                
            # Calculate Diversity (unique exponent sets)
            unique_configs = len(set(str(s.exponents) for _, s, _, _, _ in scored_pop))
            diversity_ratio = unique_configs / max(1, self.pop_size)
            
            # Adaptive mutation rate based on population diversity
            adaptive_mutation = 0.4 if diversity_ratio < 0.5 else 0.2
            
            # Log generation stats
            logging.info(f"  [GeneticRAMA] Gen {gen+1}/{self.max_generations} | Best E: {scored_pop[0][0]:.4f} | Diversity: {unique_configs}/{self.pop_size}")
            
            gen_data = {
                "generation": gen + 1,
                "best_energy": scored_pop[0][0],
                "avg_energy": sum(x[0] for x in scored_pop) / len(scored_pop),
                "diversity": unique_configs,
                "best_state": scored_pop[0][1]
            }
            history.append(gen_data)
            
            if progress_callback:
                try:
                    progress_callback(gen + 1, self.max_generations, scored_pop[0][0], unique_configs, scored_pop[0][1])
                except Exception:
                    pass
            
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
                survivors = [s for _, s, _, _, _ in scored_pop[:max(2, self.pop_size // 2)]]
                
            # 3. Selection & Crossover (Tournament)
            next_gen = [s for _, s, _, _, _ in scored_pop[:max(1, self.pop_size // 10)]] # Elite preservation
            while len(next_gen) < self.pop_size:
                # Tournament selection
                p1 = self._tournament_select(scored_pop)
                p2 = self._tournament_select(scored_pop)
                
                child = self.pop_manager.crossover(p1, p2)
                
                # 4. Mutation with adaptive rate
                child = self.pop_manager.mutate(child, mutation_rate=adaptive_mutation)
                next_gen.append(child)
                
            # 5. Immigrant Injection (Diversity preservation)
            if unique_configs < 6:
                immigrants = self.pop_manager.generate_initial_population(5, include_newman_seeds=True)
                next_gen[-5:] = immigrants
                
            population = next_gen
            
        logging.info(f"  [GeneticRAMA] Evolution complete. Global Best Energy: {best_overall_energy:.4f}")
        return best_overall_state, history

    def _tournament_select(self, scored_pop, k=3):
        import random
        contestants = random.sample(scored_pop, min(k, len(scored_pop)))
        contestants.sort(key=lambda x: x[0])
        return contestants[0][1]

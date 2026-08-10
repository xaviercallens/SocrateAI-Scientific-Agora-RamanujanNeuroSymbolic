import torch
import time
import os

# Set device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Initializing RAMA Deep Burn Evolutionary Engine on: {device}")

def deep_burn_evolution(pop_size=100_000, epochs=50, d_max=12, top_k=100):
    """
    Executes a highly parallel evolutionary loop on PyTorch tensors to find 
    supersymmetry-breaking non-extremal Kerr topological backgrounds.
    """
    # Exponent limits
    min_exp, max_exp = -24, 25
    
    # 1. Initialize random population
    print(f"Generating initial population of {pop_size:,} candidates...")
    population = torch.randint(min_exp, max_exp, (pop_size, d_max), device=device, dtype=torch.float32)
    divisors = torch.arange(1, d_max + 1, device=device, dtype=torch.float32).unsqueeze(0).expand(pop_size, -1)
    
    # Target bounds for supersymmetry breaking
    # Want c_eff close to known bounds but slightly shifted, and k != 1/2
    target_c_eff = 0.3606
    
    best_candidate_ever = None
    best_fitness_ever = float('-inf')
    
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        
        # --- FITNESS EVALUATION ---
        c_eff = torch.sum(population / divisors, dim=1)
        weight = 0.5 * torch.sum(population, dim=1)
        p_shift = (1.0 / 24.0) * torch.sum(divisors * population, dim=1)
        
        # Fitness Function (adapted from v3 position paper §5.2):
        #   F(e) = |k - 1/2| / (1 + |k - 1/2|) · exp(-1/c_eff) · (1 + |E₀|) · G(c_eff)
        # where G(c_eff) = exp(-(c_eff - target)² / 2σ²) is a Gaussian attractor
        # preventing trivial boundary saturation at extreme exponents.
        
        # Soft constraints: c_eff must be positive for unitarity
        valid_mask = (c_eff > 0)
        
        # Safe reciprocal (avoid division by zero)
        safe_c_eff = torch.clamp(c_eff, min=1e-6)
        
        susy_deviation = torch.abs(weight - 0.5)
        term1 = susy_deviation / (1.0 + susy_deviation)    # SUSY breaking reward (0 at k=0.5, →1 at k→∞)
        term2 = torch.exp(-1.0 / safe_c_eff)               # Central charge proximity (→1 for large c_eff)
        term3 = 1.0 + torch.abs(p_shift)                    # Ground state depth
        
        # Gaussian attractor: keeps c_eff near target BPS value (σ = 2.0)
        c_eff_target = 0.3606
        term4 = torch.exp(-((c_eff - c_eff_target) ** 2) / (2.0 * 2.0 ** 2))
        
        fitness = term1 * term2 * term3 * term4
        fitness[~valid_mask] = -9999.0  # Kill non-unitary candidates
        
        # --- SELECTION ---
        top_fitness, top_indices = torch.topk(fitness, top_k)
        
        if top_fitness[0].item() > best_fitness_ever:
            best_fitness_ever = top_fitness[0].item()
            best_candidate_ever = population[top_indices[0]].clone()
            best_c_eff = c_eff[top_indices[0]].item()
            best_weight = weight[top_indices[0]].item()
            best_shift = p_shift[top_indices[0]].item()
        
        if epoch % 10 == 0 or epoch == 1:
            epoch_time = time.time() - epoch_start
            print(f"Epoch {epoch:03d} | Max Fitness: {top_fitness[0]:.4f} | Time: {epoch_time:.3f}s")
            
        # --- CROSSOVER & MUTATION ---
        # Extract the elite parents
        elites = population[top_indices]
        
        # Generate new population by randomly sampling two parents for each offspring
        parent1_idx = torch.randint(0, top_k, (pop_size,), device=device)
        parent2_idx = torch.randint(0, top_k, (pop_size,), device=device)
        
        parent1 = elites[parent1_idx]
        parent2 = elites[parent2_idx]
        
        # Uniform crossover: randomly pick genes from parent 1 or 2
        mask = torch.rand((pop_size, d_max), device=device) > 0.5
        next_population = torch.where(mask, parent1, parent2)
        
        # Mutation: randomly shift exponents
        # 10% chance to mutate a gene
        mutation_mask = torch.rand((pop_size, d_max), device=device) < 0.1
        mutations = torch.randint(-4, 5, (pop_size, d_max), device=device, dtype=torch.float32)
        next_population = next_population + mutation_mask * mutations
        
        # Clamp to bounds
        population = torch.clamp(next_population, min_exp, max_exp - 1)
        
        # Keep elites elitism
        population[:top_k] = elites
        
    total_time = time.time() - start_time
    print(f"\nEvolution Complete. {epochs} epochs evaluated in {total_time:.2f} seconds.")
    print("\n--- BEST DISCOVERY (Supersymmetry Breaking) ---")
    print(f"Exponents: {best_candidate_ever.cpu().numpy()}")
    print(f"Effective Central Charge (c_eff): {best_c_eff:.4f}")
    print(f"Modular Weight (k): {best_weight:.4f} (Susy Broken, != 0.5)")
    print(f"Ground State Energy Shift: {best_shift:.4f}")
    print(f"Fitness Score: {best_fitness_ever:.4f}")

if __name__ == "__main__":
    # If on CPU locally, use a moderate population size. T4 can easily handle 1M+
    pop_size = 5_000_000 if torch.cuda.is_available() else 100_000
    deep_burn_evolution(pop_size=pop_size, epochs=100)

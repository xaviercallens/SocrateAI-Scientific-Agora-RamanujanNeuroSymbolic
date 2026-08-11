import torch
import time
import os

# Set device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Initializing RAMA Deep Burn Evolutionary Engine on: {device}")

def deep_burn_evolution(pop_size=100_000, epochs=50, d_max=12, top_k=100, kerr_mode=True):
    """
    Executes a highly parallel evolutionary loop on PyTorch tensors to find 
    supersymmetry-breaking non-extremal Kerr topological backgrounds.
    
    If kerr_mode=True: Incorporates Kerr/CFT angular momentum parity asymmetry A_J
    and non-BPS mass gap bounds into the multi-objective fitness landscape.
    """
    # Exponent limits
    min_exp, max_exp = -24, 25
    
    # 1. Initialize random population
    print(f"Generating initial population of {pop_size:,} candidates (Kerr Mode: {kerr_mode})...")
    population = torch.randint(min_exp, max_exp, (pop_size, d_max), device=device, dtype=torch.float32)
    divisors = torch.arange(1, d_max + 1, device=device, dtype=torch.float32).unsqueeze(0).expand(pop_size, -1)
    
    # Target bounds for Kerr black hole supersymmetry breaking
    target_c_eff = 1.8104  # Effective central charge for non-BPS Kerr candidate
    
    best_candidate_ever = None
    best_fitness_ever = float('-inf')
    
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        
        # --- FITNESS EVALUATION ---
        c_eff = torch.sum(population / divisors, dim=1)
        weight = 0.5 * torch.sum(population, dim=1)
        p_shift = (1.0 / 24.0) * torch.sum(divisors * population, dim=1)
        
        # Parity/Angular Momentum Asymmetry A_J = sum_{odd} e_d - sum_{even} e_d
        odd_mask = (torch.arange(1, d_max + 1, device=device) % 2 == 1).float().unsqueeze(0)
        even_mask = (torch.arange(1, d_max + 1, device=device) % 2 == 0).float().unsqueeze(0)
        a_j = torch.sum(population * odd_mask, dim=1) - torch.sum(population * even_mask, dim=1)
        
        # Fitness Function (Kerr/CFT Non-Extremal Extension):
        #   F_Kerr(e) = |k - 1/2| / (1 + |k - 1/2|) · exp(-1/c_eff) · (1 + |A_J|/12) · G(c_eff)
        
        valid_mask = (c_eff > 0)
        safe_c_eff = torch.clamp(c_eff, min=1e-6)
        
        susy_deviation = torch.abs(weight - 0.5)
        term1 = susy_deviation / (1.0 + susy_deviation)    # Non-BPS SUSY breaking reward
        term2 = torch.exp(-1.0 / safe_c_eff)               # Unitarity / central charge scaling
        term3 = 1.0 + torch.abs(a_j) / 12.0                # Kerr angular momentum asymmetry
        
        # Gaussian attractor around non-BPS Kerr CFT target (sigma = 1.5)
        c_eff_target = target_c_eff if kerr_mode else 0.3606
        term4 = torch.exp(-((c_eff - c_eff_target) ** 2) / (2.0 * 1.5 ** 2))
        
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
            best_aj = a_j[top_indices[0]].item()
        
        if epoch % 10 == 0 or epoch == 1:
            epoch_time = time.time() - epoch_start
            print(f"Epoch {epoch:03d} | Max Fitness: {top_fitness[0]:.4f} | c_eff: {best_c_eff:.4f} | k: {best_weight:.2f} | Time: {epoch_time:.3f}s")
            
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
    exponents_list = best_candidate_ever.cpu().numpy().tolist()
    print(f"Exponents: {exponents_list}")
    print(f"Effective Central Charge (c_eff): {best_c_eff:.4f}")
    print(f"Modular Weight (k): {best_weight:.4f} (Susy Broken, != 0.5)")
    print(f"Ground State Energy Shift: {best_shift:.4f}")
    print(f"Fitness Score: {best_fitness_ever:.4f}")
    return {
        "fitness": best_fitness_ever,
        "c_eff": best_c_eff,
        "k": best_weight,
        "shift": best_shift,
        "exponents": exponents_list,
    }

if __name__ == "__main__":
    # If on GPU (GCP T4), use large population. Local CPU: moderate size.
    pop_size = int(os.environ.get("POP_SIZE", 5_000_000 if torch.cuda.is_available() else 100_000))
    epochs   = int(os.environ.get("EPOCHS", 100))
    
    results = deep_burn_evolution(pop_size=pop_size, epochs=epochs)
    
    # GCS persistence for GCP runs
    bucket_name = os.environ.get("GCS_BUCKET_NAME", "")
    if bucket_name:
        try:
            from google.cloud import storage
            import json, datetime
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            payload = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "device": str(device),
                "pop_size": pop_size,
                "epochs": epochs,
                "best_fitness": results.get("fitness"),
                "best_c_eff": results.get("c_eff"),
                "best_k": results.get("k"),
                "best_shift": results.get("shift"),
                "exponents": results.get("exponents"),
            }
            blob = bucket.blob(f"runs/{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
            blob.upload_from_string(json.dumps(payload, indent=2))
            print(f"\nResults persisted to gs://{bucket_name}/{blob.name}")
        except ImportError:
            print("google-cloud-storage not installed; skipping GCS upload.")
        except Exception as e:
            print(f"GCS upload failed: {e}")

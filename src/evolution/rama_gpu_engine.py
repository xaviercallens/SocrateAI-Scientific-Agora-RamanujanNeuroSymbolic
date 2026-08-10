import torch
import time
import os

# Set device to GPU if available (Local or GCP T4)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Initializing RAMA GPU Engine on device: {device}")

def vectorized_rama_search(batch_size=1_000_000, d_max=12):
    """
    Vectorized search for non-extremal Kerr black hole topological backgrounds.
    Evaluates millions of candidate eta-quotient combinations simultaneously.
    """
    start_time = time.time()
    
    # Random exponents for each candidate (batch_size x d_max)
    # Range -24 to 24
    exponents = torch.randint(-24, 25, (batch_size, d_max), device=device, dtype=torch.float32)
    
    # The divisors: [1, 2, ..., d_max]
    divisors = torch.arange(1, d_max + 1, device=device, dtype=torch.float32).unsqueeze(0).expand(batch_size, -1)
    
    # 1. Effective Central Charge (c_eff = sum(r_d / d))
    c_eff = torch.sum(exponents / divisors, dim=1)
    
    # 2. Modular Weight (k = 1/2 * sum(r_d))
    weight = 0.5 * torch.sum(exponents, dim=1)
    
    # 3. Ground State Energy Shift (P = 1/24 * sum(d * r_d))
    p_shift = (1.0 / 24.0) * torch.sum(divisors * exponents, dim=1)
    
    # Non-extremal Kerr constraint target (e.g., specific c_eff or weight bounds)
    # Seeking broken supersymmetry: c_eff > 0, k != 1/2
    valid_mask = (c_eff > 0) & (torch.abs(weight - 0.5) > 1e-4) & (torch.abs(c_eff - 0.3606) < 1.0)
    
    valid_indices = torch.nonzero(valid_mask).squeeze()
    
    num_found = valid_indices.numel() if valid_indices.dim() > 0 else (1 if valid_indices.item() else 0)
    
    end_time = time.time()
    print(f"Evaluated {batch_size:,} candidates in {end_time - start_time:.4f} seconds.")
    print(f"Found {num_found} non-extremal candidates breaking supersymmetry constraints.")
    
    if num_found > 0:
        # Show top 5
        top_k = valid_indices[:5] if valid_indices.dim() > 0 else [valid_indices]
        for idx in top_k:
            print(f"Candidate {idx}: c_eff={c_eff[idx]:.4f}, weight={weight[idx]:.4f}, shift={p_shift[idx]:.4f}")
            print(f"Exponents: {exponents[idx].cpu().numpy()}")

if __name__ == "__main__":
    # If on CPU locally, lower batch size to avoid OOM/freezing
    bs = 10_000_000 if torch.cuda.is_available() else 1_000_000
    vectorized_rama_search(batch_size=bs)

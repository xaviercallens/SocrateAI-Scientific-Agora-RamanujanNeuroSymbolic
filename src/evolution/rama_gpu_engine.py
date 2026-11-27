import time
import torch

# Set device to GPU if available (Local or GCP T4)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def vectorized_rama_search(batch_size: int = 1_000_000, d_max: int = 12) -> None:
    """
    Tier-C vectorized heuristic search over random eta-quotient exponent vectors.
    Note: Positive cusp-0 `c_eff` alone does NOT prove modularity (Ono Thm 1.64)
    or positive/unitary q-series coefficients.
    """
    print(f"Initializing RAMA GPU Engine on device: {device}")
    start_time = time.time()

    # Random exponents for each candidate (batch_size x d_max), range -24 to 24
    exponents = torch.randint(-24, 25, (batch_size, d_max), device=device, dtype=torch.float32)

    # The divisors: [1, 2, ..., d_max]
    divisors = torch.arange(1, d_max + 1, device=device, dtype=torch.float32).unsqueeze(0).expand(batch_size, -1)

    # 1. Cusp-0 effective central charge: c_eff(0) = -sum(r_d / d)
    c_eff = -torch.sum(exponents / divisors, dim=1)

    # 2. Modular weight: k = (1/2) * sum(r_d)
    weight = 0.5 * torch.sum(exponents, dim=1)

    # 3. Leading q-power = (1/24) * sum(d * r_d), and ground state shift E0 = -leading_q_power
    leading_q_power = (1.0 / 24.0) * torch.sum(divisors * exponents, dim=1)
    ground_state_shift = -leading_q_power

    # Tier-C heuristic filter: cusp-0 positive (0 < c_eff < 2.0) and non-BPS weight (k != 1/2)
    valid_mask = (c_eff > 0.0) & (c_eff < 2.0) & (torch.abs(weight - 0.5) > 1e-4)

    valid_indices = torch.nonzero(valid_mask, as_tuple=False).flatten()
    num_found = int(valid_indices.numel())

    end_time = time.time()
    print(f"Evaluated {batch_size:,} candidates in {end_time - start_time:.4f} seconds.")
    print(
        f"Found {num_found} Tier-C heuristic search candidates "
        "(cusp-0 c_eff in (0, 2), k != 1/2; modularity & positivity unverified)."
    )

    if num_found > 0:
        top_k = valid_indices[:5]
        for idx_tensor in top_k:
            idx = int(idx_tensor.item())
            print(
                f"Candidate {idx} [Tier-C heuristic]: "
                f"c_eff(0)={c_eff[idx]:.4f}, weight={weight[idx]:.4f}, "
                f"leading_q_power={leading_q_power[idx]:.4f}, "
                f"ground_state_shift={ground_state_shift[idx]:.4f}"
            )
            print(f"Exponents: {exponents[idx].cpu().numpy()}")


if __name__ == "__main__":
    bs = 10_000_000 if torch.cuda.is_available() else 1_000_000
    vectorized_rama_search(batch_size=bs)

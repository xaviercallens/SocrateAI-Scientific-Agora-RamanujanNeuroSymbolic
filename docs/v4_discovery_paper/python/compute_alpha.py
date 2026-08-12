"""
compute_alpha.py
================
Computes exact invariants for Discovery Alpha (6c588637-899).
Reproduces the proof of Proposition 4.1 computationally.
"""
from fractions import Fraction

# Exponent vector: (divisor d, exponent r_d)
factors = [
    (1, 1), (5, -1), (6, 2), (7, -1),
    (8, 4), (9, -2), (10, 12), (11, -3), (12, 4)
]

# --- c_eff = sum(r_d / d) ---
c_eff = sum(Fraction(r, d) for d, r in factors)
print(f"c_eff = {c_eff} = {float(c_eff):.6f}")

# --- weight = sum(r_d) / 2 ---
weight = Fraction(sum(r for _, r in factors), 2)
print(f"weight = {weight} = {float(weight)}")

# --- leading_power = sum(d * r_d) / 24 ---
leading_power = Fraction(sum(d * r for d, r in factors), 24)
print(f"leading_power = {leading_power} = {float(leading_power):.6f}")

# --- Modularity check: sum(d * r_d) mod 24 ---
sum_d_rd = sum(d * r for d, r in factors)
print(f"sum(d * r_d) = {sum_d_rd}")
print(f"sum(d * r_d) mod 24 = {sum_d_rd % 24}")
print(f"Modularity condition (M2) satisfied: {sum_d_rd % 24 == 0}")

# --- q-expansion (first 20 terms) ---
print("\n--- q-expansion (first 20 coefficients) ---")
N = 20
# Build the q-expansion via Euler product
# eta(d*tau)^r = q^(d*r/24) * prod_{n>=1} (1 - q^(d*n))^r
coeffs = [0.0] * (N + 1)
coeffs[0] = 1.0

for d, r in factors:
    # Multiply by (1 - q^(d*n))^r for n = 1, 2, ...
    for n in range(1, N // d + 1):
        k = d * n
        if r > 0:
            for _ in range(r):
                for j in range(N, k - 1, -1):
                    coeffs[j] -= coeffs[j - k]
        else:
            for _ in range(-r):
                for j in range(k, N + 1):
                    coeffs[j] += coeffs[j - k]

for i in range(min(N + 1, 15)):
    print(f"  a({i}) = {coeffs[i]:.0f}")

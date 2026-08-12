#!/usr/bin/env python3
import sys

def get_eta_coeffs(N):
    """Returns coefficients of \prod_{n=1}^{N} (1-x^n) up to x^N via Pentagonal Number Theorem."""
    coeffs = [0] * N
    for k in range(-N, N+1):
        # k(3k-1)/2
        p = k * (3 * k - 1) // 2
        if p < N:
            coeffs[p] = 1 if k % 2 == 0 else -1
    return coeffs

def poly_mul(A, B, N):
    C = [0] * N
    for i in range(N):
        for j in range(N - i):
            C[i+j] += A[i] * B[j]
    return C

def poly_inv(A, N):
    # A[0] must be 1
    B = [0] * N
    B[0] = 1
    for n in range(1, N):
        s = 0
        for k in range(1, n + 1):
            s += A[k] * B[n - k]
        B[n] = -s
    return B

def eta_quotient_coeffs(factors, N):
    """factors is a list of (divisor, exponent)."""
    # Base eta product without q^(1/24)
    # \prod_{d} ( \prod_{n=1} (1-q^{d n}) )^{r}
    result = [0] * N
    result[0] = 1
    
    for d, r in factors:
        if r == 0: continue
        
        # Build \prod_{n=1} (1-q^{dn})
        base = [0] * N
        for k in range(-N, N+1):
            p = k * (3 * k - 1) // 2
            idx = p * d
            if idx < N:
                base[idx] = 1 if k % 2 == 0 else -1
        
        # Apply exponent r
        if r > 0:
            for _ in range(r):
                result = poly_mul(result, base, N)
        else:
            base_inv = poly_inv(base, N)
            for _ in range(-r):
                result = poly_mul(result, base_inv, N)
                
    return result

if __name__ == "__main__":
    tests = [
        # nb1_ch1
        [(3, 1), (8, 1), (9, -1)],
        # nb3_vacuum
        [(8, 6), (10, 3), (11, -3), (12, -5)],
        # deep_burn
        [(1, 24), (2, 23), (3, -14), (4, -24), (5, -24), (6, -24),
         (7, -24), (8, -24), (9, -24), (10, -24), (11, -24), (12, -24)],
        # A simple one: eta(q)
        [(1, 1)],
        # eta(q)^{-1} (Partition function)
        [(1, -1)]
    ]
    
    for i, t in enumerate(tests):
        c = eta_quotient_coeffs(t, 20)
        print(f"Test {i+1} {t}:")
        print(f"  {c}")

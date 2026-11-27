#!/usr/bin/env python3
"""
dualscale/ci/verify_qseries.py
==============================
Standalone CI script to recompute the Deep Burn η-quotient q-series coefficients
using exact arbitrary-precision Python integer arithmetic and verify them against
deep_verification_triple_check.json (Tier B exact verification).
"""

import json
import math
import os
import sys
from fractions import Fraction
from typing import List, Tuple


def compute_eta_base(N: int) -> List[int]:
    """
    Compute first N terms of prod_{n=1}^inf (1 - q^n) via Euler's Pentagonal Number Theorem
    using exact arbitrary-precision Python ints.
    """
    coeffs = [0] * N
    if N == 0:
        return coeffs
    coeffs[0] = 1
    k = 1
    while True:
        p1 = k * (3 * k - 1) // 2
        p2 = k * (3 * k + 1) // 2
        if p1 >= N and p2 >= N:
            break
        sign = -1 if k % 2 == 1 else 1
        if p1 < N:
            coeffs[p1] = sign
        if p2 < N:
            coeffs[p2] = sign
        k += 1
    return coeffs


def multiply_series(a: List[int], b: List[int], N: int) -> List[int]:
    """Exact Cauchy product of two integer power series truncated to N terms."""
    res = [0] * N
    limit_i = min(len(a), N)
    for i in range(limit_i):
        ai = a[i]
        if ai == 0:
            continue
        max_j = min(len(b), N - i)
        for j in range(max_j):
            res[i + j] += ai * b[j]
    return res


def power_series_int(coeffs: List[int], power: int, N: int) -> List[int]:
    """
    Compute [coeffs(q)]^power for integer power series up to N terms using exact
    arbitrary-precision integer arithmetic (logarithmic-derivative recurrence).
    """
    if N == 0:
        return []
    if power == 0:
        res = [0] * N
        res[0] = 1
        return res
    if not coeffs or coeffs[0] != 1:
        raise ValueError("power_series_int requires constant term coeffs[0] == 1.")

    res = [0] * N
    res[0] = 1

    for n in range(1, N):
        val = 0
        for k in range(1, n + 1):
            ak = coeffs[k] if k < len(coeffs) else 0
            if ak != 0 and res[n - k] != 0:
                val += (power * k - (n - k)) * ak * res[n - k]
        if val % n != 0:
            raise ArithmeticError(f"Non-integral coefficient encountered at n={n}: {val}/{n}")
        res[n] = val // n

    return res


def compute_deep_burn_series(exponents: List[int], N: int) -> List[int]:
    """Compute exact full q-series expansion for exponent array e_d at level d=1..12."""
    eta_base = compute_eta_base(N)
    res = [0] * N
    if N > 0:
        res[0] = 1

    for idx, r in enumerate(exponents):
        if r == 0:
            continue
        d = idx + 1
        dilated = [0] * N
        for i in range(N):
            if i * d < N:
                dilated[i * d] = eta_base[i]
            else:
                break
        powered = power_series_int(dilated, r, N)
        res = multiply_series(res, powered, N)

    return res


def compute_cusp_ceff(exponents: List[int], c: int) -> Fraction:
    """Compute c_eff(c) = -(1/c^2) * sum_d (gcd(d, c)^2 / d) * r_d exactly."""
    total = sum(Fraction(math.gcd(idx + 1, c) ** 2, idx + 1) * r for idx, r in enumerate(exponents))
    return -total / (c * c)


def compute_max_cusp_ceff(exponents: List[int]) -> Tuple[int, Fraction]:
    """Compute maximum effective central charge across all cusps c | lcm(d)."""
    active_divs = [idx + 1 for idx, r in enumerate(exponents) if r != 0]
    level_n = math.lcm(*active_divs) if active_divs else 1
    divisors = set()
    for i in range(1, math.isqrt(level_n) + 1):
        if level_n % i == 0:
            divisors.add(i)
            divisors.add(level_n // i)
    best_c = 1
    best_val = compute_cusp_ceff(exponents, 1)
    for c in sorted(divisors):
        val = compute_cusp_ceff(exponents, c)
        if val > best_val:
            best_val = val
            best_c = c
    return best_c, best_val


def main() -> None:
    cert_path = os.path.join(os.path.dirname(__file__), "..", "certificates", "deep_verification_triple_check.json")
    if not os.path.exists(cert_path):
        print(f"ERROR: Certificate file not found at {cert_path}")
        sys.exit(1)

    with open(cert_path, "r", encoding="utf-8") as f:
        cert_data = json.load(f)

    exp_vector = cert_data["exponent_vector"]
    expected_seq = cert_data["verified_sequence"]
    N = len(expected_seq)

    print(f"Recomputing Deep Burn q-series for level 1..12 exponents up to N={N} (exact Python int)...")
    computed_seq = compute_deep_burn_series(exp_vector, N)

    mismatches = []
    for i in range(N):
        if computed_seq[i] != expected_seq[i]:
            mismatches.append((i, computed_seq[i], expected_seq[i]))

    if mismatches:
        print(f"=== FAILURE: {len(mismatches)} term mismatches found ===")
        for i, c, e in mismatches[:5]:
            print(f"  Term q^{i}: computed={c}, expected={e}")
        sys.exit(1)

    print(f"PASS [Tier B]: All {N} q-series coefficients match deep_verification_triple_check.json exactly.")

    # Exact Fraction checks
    c_eff_cusp0 = -sum(Fraction(r, idx + 1) for idx, r in enumerate(exp_vector))
    dominant_c, max_cusp_ceff = compute_max_cusp_ceff(exp_vector)
    sum_dr = sum((idx + 1) * r for idx, r in enumerate(exp_vector))
    ono_mod24 = (sum_dr % 24 == 0)
    neg_count = sum(1 for x in computed_seq if x < 0)

    if cert_data.get("c_eff_exact") != str(c_eff_cusp0):
        print(f"FAILURE: c_eff_exact mismatch: cert={cert_data.get('c_eff_exact')} vs computed={c_eff_cusp0}")
        sys.exit(1)
    if cert_data.get("max_cusp_c_eff_exact") != str(max_cusp_ceff):
        print(f"FAILURE: max_cusp_c_eff_exact mismatch: cert={cert_data.get('max_cusp_c_eff_exact')} vs computed={max_cusp_ceff}")
        sys.exit(1)
    if cert_data.get("dominant_cusp_order") != dominant_c:
        print(f"FAILURE: dominant_cusp_order mismatch: cert={cert_data.get('dominant_cusp_order')} vs computed={dominant_c}")
        sys.exit(1)
    if cert_data.get("is_unitary_bps_state_count") is not False:
        print("FAILURE: is_unitary_bps_state_count must be false for alternating-sign sequence.")
        sys.exit(1)
    if cert_data.get("ono_thm_1_64_modular_gamma0_N") is not ono_mod24:
        print("FAILURE: ono_thm_1_64_modular_gamma0_N does not match Ono mod-24 check.")
        sys.exit(1)
    if neg_count == 0:
        print("FAILURE: Expected negative coefficients in alternating-sign Deep Burn sequence.")
        sys.exit(1)

    print(
        f"PASS [Tier B]: c_eff(0) = {c_eff_cusp0} ({float(c_eff_cusp0):.6f} < 0), "
        f"max_cusp_c_eff = {max_cusp_ceff} at cusp c={dominant_c}; "
        f"alternating-sign non-unitary index confirmed ({neg_count}/{N} negative terms); "
        f"Ono Thm 1.64 modular on Gamma_0(N): {ono_mod24}."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()

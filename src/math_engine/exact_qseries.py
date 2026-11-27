"""
src/math_engine/exact_qseries.py
================================
Exact arbitrary-precision (ℤ / ℚ) q-series and Dedekind η-quotient engine.

Epistemic Design (Rules R1–R5):
- ZERO floating-point rounding for series coefficients or rational invariants.
- Deterministic Möbius inversion recovers the UNIQUE exact η-quotient exponents
  r_d for any power series f(q) = 1 + ∑ a_n q^n, and enforces overdetermination
  (zero-free-parameter verification of higher-order tail coefficients) to forbid
  spurious curve-fitting.
- Exact cusp-0 and multi-cusp Cardy central charges, Ono (2004) Theorem 1.64
  modularity checks, positivity/sign classification, and exact matching against
  an analytically generated catalog of 28 classical Ramanujan q-series & mock
  theta functions (orders 3, 5, 6, 7, Rogers-Ramanujan, Eisenstein, theta).
"""

from __future__ import annotations

from fractions import Fraction
import math
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Exact integer power series primitives (truncated to length N: q^0 .. q^{N-1})
# ---------------------------------------------------------------------------


def poly_mul_int(a: List[int], b: List[int], N: int) -> List[int]:
    """Exact Cauchy product of two integer power series truncated to length N."""
    res = [0] * N
    la = min(len(a), N)
    lb = min(len(b), N)
    for i in range(la):
        ai = a[i]
        if ai == 0:
            continue
        limit = min(lb, N - i)
        for j in range(limit):
            res[i + j] += ai * b[j]
    return res


def poly_inv_int(a: List[int], N: int) -> List[int]:
    """Exact multiplicative inverse of an integer power series with a[0] in {1, -1}."""
    if not a or a[0] not in (1, -1):
        raise ValueError(f"Series constant term must be ±1 for exact integer inversion, got {a[:1]}")
    a0 = a[0]
    res = [0] * N
    res[0] = a0
    la = min(len(a), N)
    for n in range(1, N):
        s = 0
        for k in range(1, min(n + 1, la)):
            ak = a[k]
            if ak:
                s += ak * res[n - k]
        res[n] = -s * a0
    return res


def poly_pow_int(a: List[int], exp: int, N: int) -> List[int]:
    """Exact integer power [a(q)]^exp truncated to length N (binary exponentiation)."""
    if exp == 0:
        out = [0] * N
        if N > 0:
            out[0] = 1
        return out
    base = a[:N] + [0] * max(0, N - len(a))
    if exp < 0:
        base = poly_inv_int(base, N)
        exp = -exp
    res = [0] * N
    if N > 0:
        res[0] = 1
    while exp > 0:
        if exp & 1:
            res = poly_mul_int(res, base, N)
        exp >>= 1
        if exp > 0:
            base = poly_mul_int(base, base, N)
    return res


def poly_add_int(a: List[int], b: List[int], N: int) -> List[int]:
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(N)]


def q_pochhammer(sign_a: int, q_step: int, start_pow: int, n_terms: int, N: int) -> List[int]:
    """Exact expansion of prod_{k=0}^{n_terms-1} (1 - sign_a * q^{start_pow + k*q_step}) mod q^N.
    For (a; q)_n with a = ±q^{start_pow}, pass sign_a = +1 for (1 - q^p) or -1 for (1 + q^p).
    """
    res = [0] * N
    if N == 0:
        return res
    res[0] = 1
    for k in range(n_terms):
        p = start_pow + k * q_step
        if p >= N:
            break
        if p == 0:
            # Multiply by (1 - sign_a)
            factor = 1 - sign_a
            res = [v * factor for v in res]
        else:
            for i in range(N - 1, p - 1, -1):
                res[i] -= sign_a * res[i - p]
    return res


def eta_base_coeffs(N: int) -> List[int]:
    """Exact first N coefficients of prod_{n>=1} (1 - q^n) via Euler's Pentagonal Number Theorem."""
    if N <= 0:
        return []
    coeffs = [0] * N
    coeffs[0] = 1
    k = 1
    while True:
        p1 = k * (3 * k - 1) // 2
        p2 = k * (3 * k + 1) // 2
        if p1 >= N and p2 >= N:
            break
        sign = -1 if (k & 1) else 1
        if p1 < N:
            coeffs[p1] = sign
        if p2 < N:
            coeffs[p2] = sign
        k += 1
    return coeffs


def eta_quotient_coeffs(exponents: Dict[int, int], N: int) -> List[int]:
    """Exact first N integer coefficients of prod_d (prod_{m>=1} (1 - q^{d*m}))^{r_d}."""
    if N <= 0:
        return []
    for d, r in exponents.items():
        if not isinstance(d, int) or isinstance(d, bool) or d <= 0:
            raise ValueError(f"Divisor must be a positive int, got {d!r}")
        if not isinstance(r, int) or isinstance(r, bool):
            raise ValueError(f"Exponent must be an int, got {r!r}")

    eta_base = eta_base_coeffs(N)
    res = [0] * N
    res[0] = 1
    for d, r in sorted(exponents.items()):
        if r == 0:
            continue
        dilated = [0] * N
        for i in range(N):
            idx = i * d
            if idx >= N:
                break
            dilated[idx] = eta_base[i]
        powered = poly_pow_int(dilated, r, N)
        res = poly_mul_int(res, powered, N)
    return res


# ---------------------------------------------------------------------------
# Exact Möbius Inversion: Deterministic η-Quotient Identification
# ---------------------------------------------------------------------------


def mobius(n: int) -> int:
    """Exact Möbius function μ(n)."""
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1:
        return 1
    temp = n
    primes = 0
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            primes += 1
            temp //= p
            if temp % p == 0:
                return 0
        p += 1
    if temp > 1:
        primes += 1
    return -1 if (primes & 1) else 1


def divisors(n: int) -> List[int]:
    """All positive divisors of n sorted ascending."""
    small: List[int] = []
    large: List[int] = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            small.append(d)
            if d * d != n:
                large.append(n // d)
        d += 1
    return small + large[::-1]


def invert_eta_quotient_exact(
    coeffs: List[int],
    d_max: int = 24,
    min_terms: int = 6,
    min_overdetermination: int = 3,
    max_factors: int = 6,
    max_abs_exponent: int = 48,
) -> Dict[str, Any]:
    """
    Deterministically test whether an integer sequence [a_0, ..., a_{N-1}] is an
    EXACT finite Dedekind η-quotient (up to an overall sign and q^s shift), using
    exact logarithmic derivative + double Möbius inversion over ℚ.

    Overdetermination guardrail:
      Any N-term sequence can trivially be fitted with N-1 free exponents.
      We REQUIRE at least `min_overdetermination` higher-order coefficients
      (n > max(d)) to vanish identically in r_n (0 free parameters), and verify
      forward exact equality on ALL terms.
    """
    if not coeffs or len(coeffs) < min_terms:
        return {"is_exact_eta_quotient": False, "reason": "too_few_terms"}

    # Strip leading zeros (pure integer q-shift)
    q_shift_terms = 0
    while q_shift_terms < len(coeffs) and coeffs[q_shift_terms] == 0:
        q_shift_terms += 1
    trimmed = coeffs[q_shift_terms:]
    if len(trimmed) < min_terms:
        return {"is_exact_eta_quotient": False, "reason": "too_few_nonzero_terms"}

    a0 = trimmed[0]
    if a0 == 0:
        return {"is_exact_eta_quotient": False, "reason": "zero_leading_term"}

    # Allow normalization by a0 if all terms are divisible by a0 (e.g., a0 = -1 or a0 = 2)
    if any(x % a0 != 0 for x in trimmed):
        return {"is_exact_eta_quotient": False, "reason": "leading_term_not_divisor"}

    norm = [x // a0 for x in trimmed]
    N = len(norm)

    # 1. Exact logarithmic derivative: q f'(q)/f(q) = -sum_{n>=1} s_n q^n
    #    => n * a_n = -sum_{k=1}^n s_k * a_{n-k}
    s: Dict[int, Fraction] = {}
    for n in range(1, N):
        acc = Fraction(0)
        for k in range(1, n):
            acc += s[k] * norm[n - k]
        s[n] = Fraction(-n * norm[n]) - acc

    # 2. Euler product exponents: f(q) = prod_{m>=1} (1 - q^m)^{c_m}
    #    s_n = sum_{d|n} d * c_d  =>  c_m = (1/m) * sum_{d|m} mu(m/d) * s_d
    c: Dict[int, Fraction] = {}
    for m in range(1, N):
        val = sum(mobius(m // d) * s[d] for d in divisors(m))
        c[m] = val / m

    # 3. Dedekind eta exponents: c_m = sum_{d|m} r_d  =>  r_m = sum_{d|m} mu(m/d) * c_d
    r_all: Dict[int, Fraction] = {}
    for m in range(1, N):
        r_all[m] = sum(mobius(m // d) * c[d] for d in divisors(m))

    # Every r_m must be an integer
    if any(v.denominator != 1 for v in r_all.values()):
        return {
            "is_exact_eta_quotient": False,
            "reason": "non_integer_eta_exponents",
            "euler_exponents_sample": {str(m): str(c[m]) for m in range(1, min(N, 8))},
        }

    nonzero = {m: int(v.numerator) for m, v in r_all.items() if v != 0}
    if not nonzero:
        return {
            "is_exact_eta_quotient": False,
            "reason": "constant_series",
        }

    max_d = max(nonzero.keys())
    tail_zeros = (N - 1) - max_d

    if max_d > d_max:
        return {"is_exact_eta_quotient": False, "reason": f"max_divisor_{max_d}_exceeds_{d_max}"}
    if len(nonzero) > max_factors:
        return {"is_exact_eta_quotient": False, "reason": f"too_many_factors_{len(nonzero)}"}
    if any(abs(e) > max_abs_exponent for e in nonzero.values()):
        return {"is_exact_eta_quotient": False, "reason": "exponent_magnitude_excessive"}
    if tail_zeros < min_overdetermination:
        return {
            "is_exact_eta_quotient": False,
            "reason": f"underdetermined_tail_zeros_{tail_zeros}_lt_{min_overdetermination}",
            "candidate_exponents": nonzero,
        }

    # Forward exact integer verification on ALL N terms
    recomputed = eta_quotient_coeffs(nonzero, N)
    if recomputed != norm:
        return {"is_exact_eta_quotient": False, "reason": "forward_recheck_mismatch"}

    return {
        "is_exact_eta_quotient": True,
        "exponents": nonzero,
        "scale_factor": a0,
        "leading_q_shift": q_shift_terms,
        "terms_verified": N,
        "overdetermination_degree": tail_zeros,
        "verified_coeffs_30": eta_quotient_coeffs(nonzero, 30),
    }


# ---------------------------------------------------------------------------
# Exact Physical, Multi-Cusp & Ono (2004) Theorem 1.64 Invariants
# ---------------------------------------------------------------------------


def _prime_exponents(n: int) -> Dict[int, int]:
    fac: Dict[int, int] = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            fac[d] = fac.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        fac[temp] = fac.get(temp, 0) + 1
    return fac


def compute_eta_invariants(exponents: Dict[int, int], expansion_terms: int = 30) -> Dict[str, Any]:
    """Compute exact rational invariants, multi-cusp c_eff, Ono Thm 1.64 checks, and positivity."""
    if not exponents:
        raise ValueError("exponents must be non-empty")

    level_N = 1
    for d in exponents:
        if d <= 0:
            raise ValueError(f"Divisor must be positive, got {d}")
        level_N = math.lcm(level_N, d)

    weight_k = Fraction(sum(exponents.values()), 2)
    c_eff_0 = -sum((Fraction(r, d) for d, r in exponents.items()), Fraction(0))
    sum_dr = sum(d * r for d, r in exponents.items())
    leading_q_power = Fraction(sum_dr, 24)
    ground_state_E0 = -leading_q_power

    # Multi-cusp c_eff(c) = -(1/c^2) * sum_d (gcd(d, c)^2 / d) * r_d  for all c | N
    cusp_ceffs: Dict[int, Fraction] = {}
    for c in divisors(level_N):
        val = -sum(
            (Fraction(math.gcd(d, c) ** 2 * r, d) for d, r in exponents.items()),
            Fraction(0),
        ) / Fraction(c * c, 1)
        cusp_ceffs[c] = val

    max_cusp_c = max(cusp_ceffs, key=lambda c: cusp_ceffs[c])
    max_cusp_ceff = cusp_ceffs[max_cusp_c]

    # Ono (2004) Theorem 1.64 checks on Gamma_0(N)
    sum_n_over_d_r = sum((level_N // d) * r for d, r in exponents.items())
    ono_cong_1 = (sum_dr % 24 == 0)
    ono_cong_2 = (sum_n_over_d_r % 24 == 0)
    is_integer_weight = (sum(exponents.values()) % 2 == 0)

    # Check if prod d^{r_d} is a rational square (trivial Nebentypus character when integer weight)
    prime_parity: Dict[int, int] = {}
    for d, r in exponents.items():
        for p, e in _prime_exponents(d).items():
            prime_parity[p] = prime_parity.get(p, 0) + e * r
    is_rational_square = all((v % 2 == 0) for v in prime_parity.values())

    ono_164_gamma0_N = ono_cong_1 and ono_cong_2 and is_integer_weight

    # Exact q-expansion positivity / sign analysis
    coeffs = eta_quotient_coeffs(exponents, expansion_terms)
    neg_count = sum(1 for x in coeffs if x < 0)
    pos_count = sum(1 for x in coeffs if x > 0)
    if neg_count == 0 and pos_count > 1:
        sign_class = "non_negative_coefficients"
    elif pos_count == 0 and neg_count > 1:
        sign_class = "non_positive_coefficients"
    else:
        sign_class = "alternating_sign_index"

    return {
        "level_N": level_N,
        "weight_k": str(weight_k),
        "weight_k_float": float(weight_k),
        "c_eff_cusp0": str(c_eff_0),
        "c_eff_cusp0_float": float(c_eff_0),
        "max_cusp_c": max_cusp_c,
        "max_cusp_c_eff": str(max_cusp_ceff),
        "max_cusp_c_eff_float": float(max_cusp_ceff),
        "leading_q_power": str(leading_q_power),
        "ground_state_E0": str(ground_state_E0),
        "ono_sum_dr": sum_dr,
        "ono_sum_N_over_d_r": sum_n_over_d_r,
        "ono_cong_1_mod24": ono_cong_1,
        "ono_cong_2_mod24": ono_cong_2,
        "is_integer_weight": is_integer_weight,
        "prod_d_rd_is_square": is_rational_square,
        "ono_164_modular_gamma0_N": ono_164_gamma0_N,
        "is_weight_half": (weight_k == Fraction(1, 2)),
        "sign_classification": sign_class,
        "negative_terms_in_first_30": neg_count,
        "coeffs_30": coeffs,
    }


# ---------------------------------------------------------------------------
# Analytically Generated Classical Ramanujan q-Series & Mock Theta Catalog
# ---------------------------------------------------------------------------


def _build_classical_catalog(N: int = 30) -> Dict[str, Dict[str, Any]]:
    """Generate exact integer expansions to order N for canonical Ramanujan series."""
    catalog: Dict[str, Dict[str, Any]] = {}

    def add(key: str, name: str, oeis: str, category: str, seq: List[int], formula: str, ref: str):
        catalog[key] = {
            "name": name,
            "oeis": oeis,
            "category": category,
            "coeffs": seq[:N],
            "formula": formula,
            "reference": ref,
        }

    # 1. Fundamental eta-quotients & theta series
    add("euler_eta", "Euler pentagonal / Dedekind eta", "A010815", "eta_quotient",
        eta_quotient_coeffs({1: 1}, N), "prod_{n>=1}(1-q^n)", "Euler (1750); NB1")
    add("partition_p", "Integer partition function p(n)", "A000041", "eta_quotient",
        eta_quotient_coeffs({1: -1}, N), "1/prod_{n>=1}(1-q^n)", "Hardy-Ramanujan (1918)")
    add("distinct_partitions", "Distinct partitions Q(n)", "A000009", "eta_quotient",
        eta_quotient_coeffs({1: -1, 2: 1}, N), "prod(1+q^n) = eta(2t)/eta(t)", "Euler; NB2 Ch.16")
    add("overpartitions", "Overpartitions p_bar(n)", "A015128", "eta_quotient",
        eta_quotient_coeffs({1: -2, 2: 1}, N), "(-q;q)_inf/(q;q)_inf = eta(2t)/eta(t)^2", "Corteel-Lovejoy; NB2 Ch.16")
    add("ramanujan_tau_delta", "Ramanujan tau(n+1) / Delta(q)/q", "A000594", "eta_quotient",
        eta_quotient_coeffs({1: 24}, N), "prod(1-q^n)^24 = Delta(q)/q", "Ramanujan (1916)")
    add("theta_3", "Jacobi theta_3(q) = sum q^(n^2)", "A000122", "theta_function",
        eta_quotient_coeffs({1: -2, 2: 5, 4: -2}, N), "eta(2t)^5 / (eta(t)^2 eta(4t)^2)", "NB2 Ch.16 (Entry 22)")
    add("theta_4", "Jacobi theta_4(q) = sum (-1)^n q^(n^2)", "A002448", "theta_function",
        eta_quotient_coeffs({1: 2, 2: -1}, N), "eta(t)^2 / eta(2t)", "NB2 Ch.16 (Entry 22)")
    add("ramanujan_psi", "Ramanujan psi(q) = sum q^(n(n+1)/2)", "A010054", "theta_function",
        eta_quotient_coeffs({1: -1, 2: 2}, N), "eta(2t)^2 / eta(t)", "NB2 Ch.16 (Entry 22)")
    add("cubic_agm_a", "Borwein/Ramanujan cubic theta a(q)", "A004016", "theta_function",
        [1] + [6 * sum(1 if d % 3 == 1 else (-1 if d % 3 == 2 else 0) for d in divisors(n)) for n in range(1, N)],
        "sum_{m,n} q^(m^2+mn+n^2)", "NB2 Ch.21 / Lost Notebook")

    # 2. Rogers-Ramanujan identities G(q) and H(q)
    G = [0] * N
    H = [0] * N
    for n in range(N):
        if n * n >= N:
            break
        den = q_pochhammer(1, 1, 1, n, N)
        inv_den = poly_inv_int(den, N)
        for k in range(N - n * n):
            G[n * n + k] += inv_den[k]
        if n * n + n < N:
            for k in range(N - (n * n + n)):
                H[n * n + n + k] += inv_den[k]
    add("rogers_ramanujan_G", "Rogers-Ramanujan G(q)", "A003114", "rogers_ramanujan",
        G, "sum_{n>=0} q^(n^2)/(q;q)_n = 1/((q;q^5)_inf(q^4;q^5)_inf)", "NB2 Ch.16; Rogers-Ramanujan")
    add("rogers_ramanujan_H", "Rogers-Ramanujan H(q)", "A003106", "rogers_ramanujan",
        H, "sum_{n>=0} q^(n^2+n)/(q;q)_n = 1/((q^2;q^5)_inf(q^3;q^5)_inf)", "NB2 Ch.16; Rogers-Ramanujan")

    # 3. 3rd-order Mock Theta Functions (Ramanujan Last Letter 1920 & Lost Notebook)
    f3 = [0] * N
    phi3 = [0] * N
    psi3 = [0] * N
    chi3 = [0] * N
    omega3 = [0] * N
    nu3 = [0] * N
    rho3 = [0] * N
    for n in range(N):
        if n * n < N:
            # f(q) = sum q^(n^2) / (-q;q)_n^2
            d_f = poly_pow_int(q_pochhammer(-1, 1, 1, n, N), -2, N)
            for k in range(N - n * n):
                f3[n * n + k] += d_f[k]
            # phi(q) = sum q^(n^2) / (-q^2;q^2)_n
            d_phi = poly_inv_int(q_pochhammer(-1, 2, 2, n, N), N)
            for k in range(N - n * n):
                phi3[n * n + k] += d_phi[k]
            # psi(q) = sum_{n>=1} q^(n^2) / (q;q^2)_n
            if n >= 1:
                d_psi = poly_inv_int(q_pochhammer(1, 2, 1, n, N), N)
                for k in range(N - n * n):
                    psi3[n * n + k] += d_psi[k]
            # chi(q) = sum q^(n^2) * (-q;q)_n / (-q^3;q^3)_n
            num_chi = q_pochhammer(-1, 1, 1, n, N)
            den_chi = poly_inv_int(q_pochhammer(-1, 3, 3, n, N), N)
            t_chi = poly_mul_int(num_chi, den_chi, N)
            for k in range(N - n * n):
                chi3[n * n + k] += t_chi[k]
        # omega(q) = sum_{n>=0} q^(2n^2+2n) / (q;q^2)_{n+1}^2
        p_om = 2 * n * n + 2 * n
        if p_om < N:
            d_om = poly_pow_int(q_pochhammer(1, 2, 1, n + 1, N), -2, N)
            for k in range(N - p_om):
                omega3[p_om + k] += d_om[k]
            # rho(q) = sum q^(2n(n+1)) / prod_{k=0}^n (1 + q^(2k+1) + q^(4k+2))
            den_rho = [0] * N
            den_rho[0] = 1
            for m in range(n + 1):
                fac = [0] * N
                fac[0] = 1
                if 2 * m + 1 < N:
                    fac[2 * m + 1] = 1
                if 4 * m + 2 < N:
                    fac[4 * m + 2] = 1
                den_rho = poly_mul_int(den_rho, fac, N)
            inv_rho = poly_inv_int(den_rho, N)
            for k in range(N - p_om):
                rho3[p_om + k] += inv_rho[k]
        # nu(q) = sum q^(n^2+n) / (-q;q^2)_{n+1}
        p_nu = n * n + n
        if p_nu < N:
            d_nu = poly_inv_int(q_pochhammer(-1, 2, 1, n + 1, N), N)
            for k in range(N - p_nu):
                nu3[p_nu + k] += d_nu[k]

    add("mock3_f", "3rd-order mock theta f(q)", "A000025", "mock_theta_3",
        f3, "sum_{n>=0} q^(n^2)/(-q;q)_n^2", "Ramanujan Last Letter (1920); Andrews-Berndt Part I")
    add("mock3_phi", "3rd-order mock theta phi(q)", "A053250", "mock_theta_3",
        phi3, "sum_{n>=0} q^(n^2)/(-q^2;q^2)_n", "Ramanujan Last Letter (1920)")
    add("mock3_psi", "3rd-order mock theta psi(q)", "A053251", "mock_theta_3",
        psi3, "sum_{n>=1} q^(n^2)/(q;q^2)_n", "Ramanujan Last Letter (1920)")
    add("mock3_chi", "3rd-order mock theta chi(q)", "A053252", "mock_theta_3",
        chi3, "sum_{n>=0} q^(n^2)(-q;q)_n/(-q^3;q^3)_n", "Ramanujan Last Letter (1920)")
    add("mock3_omega", "3rd-order mock theta omega(q)", "A053253", "mock_theta_3",
        omega3, "sum_{n>=0} q^(2n^2+2n)/(q;q^2)_{n+1}^2", "Lost Notebook; Watson (1936)")
    add("mock3_nu", "3rd-order mock theta nu(q)", "A053254", "mock_theta_3",
        nu3, "sum_{n>=0} q^(n^2+n)/(-q;q^2)_{n+1}", "Lost Notebook; Watson (1936)")
    add("mock3_rho", "3rd-order mock theta rho(q)", "A053255", "mock_theta_3",
        rho3, "sum_{n>=0} q^(2n(n+1))/prod(1+q^(2k+1)+q^(4k+2))", "Lost Notebook; Watson (1936)")

    # 4. 5th-order Mock Theta Functions (Last Letter & Lost Notebook)
    f0_5 = [0] * N
    F0_5 = [0] * N
    f1_5 = [0] * N
    phi0_5 = [0] * N
    psi0_5 = [0] * N
    for n in range(N):
        if n * n < N:
            d = poly_inv_int(q_pochhammer(-1, 1, 1, n, N), N)
            for k in range(N - n * n):
                f0_5[n * n + k] += d[k]
            t_phi0 = q_pochhammer(-1, 2, 1, n, N)
            for k in range(N - n * n):
                phi0_5[n * n + k] += t_phi0[k]
        if 2 * n * n < N:
            d = poly_inv_int(q_pochhammer(1, 2, 1, n, N), N)
            for k in range(N - 2 * n * n):
                F0_5[2 * n * n + k] += d[k]
        if n * n + n < N:
            d = poly_inv_int(q_pochhammer(-1, 1, 1, n, N), N)
            for k in range(N - (n * n + n)):
                f1_5[n * n + n + k] += d[k]
        p_psi0 = (n + 1) * (n + 2) // 2
        if p_psi0 < N:
            t_psi0 = q_pochhammer(-1, 1, 1, n, N)
            for k in range(N - p_psi0):
                psi0_5[p_psi0 + k] += t_psi0[k]

    add("mock5_f0", "5th-order mock theta f_0(q)", "A053256", "mock_theta_5",
        f0_5, "sum q^(n^2)/(-q;q)_n", "Lost Notebook; Andrews-Berndt Part I")
    add("mock5_F0", "5th-order mock theta F_0(q)", "A053258", "mock_theta_5",
        F0_5, "sum q^(2n^2)/(q;q^2)_n", "Lost Notebook; Andrews-Berndt Part I")
    add("mock5_f1", "5th-order mock theta f_1(q)", "A053262", "mock_theta_5",
        f1_5, "sum q^(n^2+n)/(-q;q)_n", "Lost Notebook; Andrews-Berndt Part I")
    add("mock5_phi0", "5th-order mock theta phi_0(q)", "A053257", "mock_theta_5",
        phi0_5, "sum q^(n^2)(-q;q^2)_n", "Lost Notebook; Andrews-Berndt Part I")
    add("mock5_psi0", "5th-order mock theta psi_0(q)", "A053259", "mock_theta_5",
        psi0_5, "sum q^((n+1)(n+2)/2)(-q;q)_n", "Lost Notebook; Andrews-Berndt Part I")

    # 5. 6th-order Mock Theta Functions (Lost Notebook, Andrews-Hickerson 1991)
    phi6 = [0] * N
    psi6 = [0] * N
    rho6 = [0] * N
    sigma6 = [0] * N
    for n in range(N):
        if n * n < N:
            num = q_pochhammer(1, 2, 1, n, N)
            den = poly_inv_int(q_pochhammer(-1, 1, 1, 2 * n, N), N)
            term = poly_mul_int(num, den, N)
            sgn = -1 if (n & 1) else 1
            for k in range(N - n * n):
                phi6[n * n + k] += sgn * term[k]
        if (n + 1) * (n + 1) < N:
            num = q_pochhammer(1, 2, 1, n, N)
            den = poly_inv_int(q_pochhammer(-1, 1, 1, 2 * n + 1, N), N)
            term = poly_mul_int(num, den, N)
            sgn = -1 if (n & 1) else 1
            p_p = (n + 1) * (n + 1)
            for k in range(N - p_p):
                psi6[p_p + k] += sgn * term[k]
        p_r = n * (n + 1) // 2
        if p_r < N:
            num = q_pochhammer(-1, 1, 1, n, N)
            den = poly_inv_int(q_pochhammer(1, 2, 1, n + 1, N), N)
            term = poly_mul_int(num, den, N)
            for k in range(N - p_r):
                rho6[p_r + k] += term[k]
        p_s = (n + 1) * (n + 2) // 2
        if p_s < N:
            num = q_pochhammer(-1, 1, 1, n, N)
            den = poly_inv_int(q_pochhammer(1, 2, 1, n + 1, N), N)
            term = poly_mul_int(num, den, N)
            for k in range(N - p_s):
                sigma6[p_s + k] += term[k]

    add("mock6_phi", "6th-order mock theta phi_6(q)", "A053268", "mock_theta_6",
        phi6, "sum (-1)^n q^(n^2) (q;q^2)_n / (-q;q)_{2n}", "Lost Notebook; Andrews-Hickerson (1991)")
    add("mock6_psi", "6th-order mock theta psi_6(q)", "A053269", "mock_theta_6",
        psi6, "sum (-1)^n q^((n+1)^2) (q;q^2)_n / (-q;q)_{2n+1}", "Lost Notebook; Andrews-Hickerson (1991)")
    add("mock6_rho", "6th-order mock theta rho_6(q)", "A053270", "mock_theta_6",
        rho6, "sum q^(n(n+1)/2) (-q;q)_n / (q;q^2)_{n+1}", "Lost Notebook; Andrews-Hickerson (1991)")
    add("mock6_sigma", "6th-order mock theta sigma_6(q)", "A053271", "mock_theta_6",
        sigma6, "sum q^((n+1)(n+2)/2) (-q;q)_n / (q;q^2)_{n+1}", "Lost Notebook; Andrews-Hickerson (1991)")

    # 6. 7th-order Mock Theta Functions (Last Letter)
    F0_7 = [0] * N
    F1_7 = [0] * N
    F2_7 = [0] * N
    for n in range(N):
        if n * n < N:
            den = poly_inv_int(q_pochhammer(1, 1, n + 1, n, N), N)
            for k in range(N - n * n):
                F0_7[n * n + k] += den[k]
        if n >= 1 and n * n < N:
            den = poly_inv_int(q_pochhammer(1, 1, n, n, N), N)
            for k in range(N - n * n):
                F1_7[n * n + k] += den[k]
        if n * n + n < N:
            den = poly_inv_int(q_pochhammer(1, 1, n + 1, n + 1, N), N)
            for k in range(N - (n * n + n)):
                F2_7[n * n + n + k] += den[k]

    add("mock7_F0", "7th-order mock theta F_0(q)", "A053275", "mock_theta_7",
        F0_7, "sum q^(n^2)/(q^{n+1};q)_n", "Ramanujan Last Letter (1920)")
    add("mock7_F1", "7th-order mock theta F_1(q)", "A053276", "mock_theta_7",
        F1_7, "sum_{n>=1} q^(n^2)/(q^n;q)_n", "Ramanujan Last Letter (1920)")
    add("mock7_F2", "7th-order mock theta F_2(q)", "A053277", "mock_theta_7",
        F2_7, "sum q^(n^2+n)/(q^{n+1};q)_{n+1}", "Ramanujan Last Letter (1920)")

    # 7. Eisenstein series E_2, E_4, E_6
    def sigma_k(n: int, k: int) -> int:
        return sum(d ** k for d in divisors(n))

    add("eisenstein_E2", "Eisenstein series E_2(q)", "A006352", "eisenstein_series",
        [1] + [-24 * sigma_k(n, 1) for n in range(1, N)], "1 - 24 sum sigma_1(n) q^n", "Ramanujan (1916); NB2")
    add("eisenstein_E4", "Eisenstein series E_4(q)", "A004009", "eisenstein_series",
        [1] + [240 * sigma_k(n, 3) for n in range(1, N)], "1 + 240 sum sigma_3(n) q^n", "Ramanujan (1916); NB2")
    add("eisenstein_E6", "Eisenstein series E_6(q)", "A013973", "eisenstein_series",
        [1] + [-504 * sigma_k(n, 5) for n in range(1, N)], "1 - 504 sum sigma_5(n) q^n", "Ramanujan (1916); NB2")

    return catalog


CLASSICAL_CATALOG: Dict[str, Dict[str, Any]] = _build_classical_catalog(30)


def match_classical_catalog(coeffs: List[int], min_match_len: int = 6) -> Optional[Dict[str, Any]]:
    """Exact prefix match (up to optional leading-zero shift or overall sign) against CLASSICAL_CATALOG."""
    if len(coeffs) < min_match_len:
        return None
    L = min(len(coeffs), 30)
    prefix = coeffs[:L]
    neg_prefix = [-x for x in prefix]
    for key, entry in CLASSICAL_CATALOG.items():
        ref = entry["coeffs"][:L]
        if prefix == ref or neg_prefix == ref:
            return {
                "catalog_key": key,
                "name": entry["name"],
                "oeis": entry["oeis"],
                "category": entry["category"],
                "formula": entry["formula"],
                "reference": entry["reference"],
                "matched_terms": L,
                "sign_flipped": (prefix != ref),
            }
    return None

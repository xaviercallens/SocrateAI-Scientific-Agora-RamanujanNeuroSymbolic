"""
Project NAMAGIRI — Saddle Point Thermodynamics (WS-8)
Evaluates cusp-0 and multi-cusp effective central charges, modular weight,
ground-state shifts, and Ono (2004) Theorem 1.64 congruence checks using exact
rational arithmetic (`fractions.Fraction`).

Note: Positive `c_eff` is NOT sufficient for unitarity or coefficient positivity
(Tier C heuristic evaluator only).
"""

import math
from fractions import Fraction
from typing import Any, Dict, List, Tuple


def _positive_divisors(n: int) -> List[int]:
    """Return sorted positive divisors of a positive integer `n`."""
    divs = set()
    for i in range(1, math.isqrt(n) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    return sorted(divs)


def _is_product_rational_square(exponents: Dict[int, int]) -> bool:
    """Check whether prod_d d^{r_d} is a rational square (all prime exponents even)."""
    prime_exps: Dict[int, int] = {}
    for d, r in exponents.items():
        if r == 0:
            continue
        rem = d
        p = 2
        while p * p <= rem:
            if rem % p == 0:
                cnt = 0
                while rem % p == 0:
                    rem //= p
                    cnt += 1
                prime_exps[p] = prime_exps.get(p, 0) + cnt * r
            p += 1
        if rem > 1:
            prime_exps[rem] = prime_exps.get(rem, 0) + r
    return all(exp % 2 == 0 for exp in prime_exps.values())


class SaddlePointEvaluator:
    """Tier-C exact-rational saddle point and multi-cusp diagnostic evaluator."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def cusp_c_eff(exponents: Dict[int, int], c: int) -> Fraction:
        """Compute exact effective central charge at cusp 1/c:
        c_eff(c) = -(1/c^2) * sum_d (gcd(d, c)^2 / d) * r_d.
        """
        if c <= 0:
            raise ValueError(f"Cusp order c must be positive, got {c}")
        total = sum(
            Fraction(math.gcd(d, c) ** 2, d) * r
            for d, r in exponents.items()
        )
        return -total / (c * c)

    def evaluate_saddle_point(self, q_shift_24: int, exponents: Dict[int, int]) -> Dict[str, Any]:
        """
        Calculate exact rational invariants (cusp-0 `c_eff`, multi-cusp `max_cusp_c_eff`,
        modular weight `k`, `leading_q_power`, `ground_state_shift`, and Ono Thm 1.64
        checks) plus Cardy scaling at the dominant cusp when `max_cusp_c_eff > 0`.
        """
        for d in exponents:
            if d <= 0:
                raise ValueError(f"Eta-quotient divisor d must be positive, got {d}")

        if not exponents or all(r == 0 for r in exponents.values()):
            return {
                "c_eff": 0.0,
                "c_eff_exact": "0",
                "max_cusp_c_eff": 0.0,
                "max_cusp_c_eff_exact": "0",
                "dominant_cusp_order": 1,
                "level_N": 1,
                "modular_weight": 0.0,
                "modular_weight_exact": "0",
                "leading_q_power": 0.0,
                "leading_q_power_exact": "0",
                "ground_state_shift": 0.0,
                "ground_state_shift_exact": "0",
                "ono_conditions_met": True,
                "ono_details": {
                    "sum_dr": 0,
                    "sum_dr_mod24": True,
                    "sum_n_over_dr": 0,
                    "sum_n_over_dr_mod24": True,
                    "product_d_pow_r_is_square": True,
                },
                "entropy_scaling": 0.0,
                "equilibrium_state": "Marginal (Empty)",
                "epistemic_tier": "C",
                "matrix_applied": {
                    "cardy_prefactor_at_max_cusp": 0.0,
                    "cardy_prefactor_formula": "2 * pi * sqrt(max_cusp_c_eff / 6)",
                },
            }

        # 1. Modular weight k = (1/2) * sum(r_d)
        modular_weight_exact = Fraction(sum(exponents.values()), 2)

        # 2. Cusp-0 effective central charge c_eff(0) = -sum(r_d / d)
        c_eff_cusp0 = -sum(Fraction(r, d) for d, r in exponents.items())

        # 3. Leading q-power = (1/24) * sum(d * r_d) and ground state shift E0 = -leading_q_power
        sum_dr = sum(d * r for d, r in exponents.items())
        leading_q_power_exact = Fraction(sum_dr, 24)
        ground_state_shift_exact = -leading_q_power_exact

        # 4. Multi-cusp dominance over c | N where N = lcm({d : r_d != 0})
        active_divisors = [d for d, r in exponents.items() if r != 0]
        level_n = math.lcm(*active_divisors) if active_divisors else 1
        dominant_cusp_order = 1
        max_cusp_c_eff = self.cusp_c_eff(exponents, 1)
        for c in _positive_divisors(level_n):
            val = self.cusp_c_eff(exponents, c)
            if val > max_cusp_c_eff:
                max_cusp_c_eff = val
                dominant_cusp_order = c

        # 5. Ono (2004) Theorem 1.64 modularity conditions on Gamma_0(N)
        sum_n_over_dr = sum((level_n // d) * r for d, r in exponents.items())
        ono_sum_dr_mod24 = (sum_dr % 24 == 0)
        ono_sum_n_over_dr_mod24 = (sum_n_over_dr % 24 == 0)
        ono_product_square = _is_product_rational_square(exponents)
        ono_conditions_met = bool(
            ono_sum_dr_mod24 and ono_sum_n_over_dr_mod24 and ono_product_square
        )

        # 6. Cardy scaling at max cusp (only well-defined as real exponential growth when max_cusp_c_eff > 0)
        if max_cusp_c_eff > 0:
            entropy_scaling = 2.0 * math.pi * math.sqrt(float(max_cusp_c_eff) / 6.0)
        else:
            entropy_scaling = 0.0

        # 7. Honest classification without false unitarity claims
        if c_eff_cusp0 > 0:
            equilibrium = "Exponential Growth (Cusp-0 Positive; Unitarity Unverified)"
        elif c_eff_cusp0 < 0 and max_cusp_c_eff > 0:
            equilibrium = "Multi-Cusp Oscillatory Candidate (Cusp-0 Negative; Non-Unitary Index)"
        elif c_eff_cusp0 < 0:
            equilibrium = "Sub-Exponential / Decaying"
        elif max_cusp_c_eff > 0:
            equilibrium = "Multi-Cusp Oscillatory Candidate (Cusp-0 Zero; Non-Unitary Index)"
        else:
            equilibrium = "Marginal (Flat Vacuum)"

        return {
            "c_eff": round(float(c_eff_cusp0), 6),
            "c_eff_exact": str(c_eff_cusp0),
            "max_cusp_c_eff": round(float(max_cusp_c_eff), 6),
            "max_cusp_c_eff_exact": str(max_cusp_c_eff),
            "dominant_cusp_order": dominant_cusp_order,
            "level_N": level_n,
            "modular_weight": float(modular_weight_exact),
            "modular_weight_exact": str(modular_weight_exact),
            "leading_q_power": round(float(leading_q_power_exact), 6),
            "leading_q_power_exact": str(leading_q_power_exact),
            "ground_state_shift": round(float(ground_state_shift_exact), 6),
            "ground_state_shift_exact": str(ground_state_shift_exact),
            "ono_conditions_met": ono_conditions_met,
            "ono_details": {
                "sum_dr": sum_dr,
                "sum_dr_mod24": ono_sum_dr_mod24,
                "sum_n_over_dr": sum_n_over_dr,
                "sum_n_over_dr_mod24": ono_sum_n_over_dr_mod24,
                "product_d_pow_r_is_square": ono_product_square,
            },
            "entropy_scaling": round(entropy_scaling, 6),
            "equilibrium_state": equilibrium,
            "epistemic_tier": "C",
            "matrix_applied": {
                "cardy_prefactor_at_max_cusp": round(entropy_scaling, 6),
                "cardy_prefactor_formula": "2 * pi * sqrt(max_cusp_c_eff / 6)",
            },
        }

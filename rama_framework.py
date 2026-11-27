r"""
RAMA: Recursive Aesthetic Modular Approximation Framework
===========================================================
A meta-algorithmic framework modeling Ramanujan-style heuristic discovery
using energy-minimizing local search over symbolic spaces.

Based on:
Jordi Vallverdu (2026). "RAMA: A Meta-Algorithmic Framework for Ramanujan-Style
Heuristic Discovery Using Large Language Models". Algorithms 19(1), 7.
https://doi.org/10.3390/a19010007

Tracks Implemented:
------------------
1. Track A (Tier C): Inverse engineering eta-quotients f_p(q) = q^k \prod_d \eta(q^d)^{r_d}
   from partial q-series coefficient data (e.g. partition numbers, discriminant \Delta).
2. Track B (Tier X synthetic): Designing cyclotomic fingerprints S_m = E_{x~p}[exp(2\pi i |x| / m)]
   and periodic R_z(\pi / m) phase-interference shadow gadgets for toy quantum circuits.
3. Ablation Engine: Toggling aesthetic (\gamma=0) and compression (\alpha=0) terms.
"""

import cmath
import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


# =====================================================================
# Core Data Structures & Base Classes
# =====================================================================


class DomainTrack(Enum):
    TRACK_A_QSERIES = "Track A: q-Series Inverse Engineering"
    TRACK_B_QUANTUM = "Track B: Quantum Cyclotomic Fingerprints"


@dataclass
class EnergyWeights:
    alpha: float = 1.0  # Complexity / description length penalty (C)
    beta: float = 1.0   # Inconsistency / fit error penalty (I)
    gamma: float = 0.2  # Aesthetic deviation penalty (D)


@dataclass
class SymbolicState:
    """Generic state representation for RAMA local search."""

    data: Any
    description_length: float = 0.0
    fit_error: float = 0.0
    aesthetic_penalty: float = 0.0

    def compute_energy(self, weights: EnergyWeights) -> float:
        return (
            weights.alpha * self.description_length
            + weights.beta * self.fit_error
            + weights.gamma * self.aesthetic_penalty
        )


# =====================================================================
# Track A: q-Series & Eta-Quotient Inverse Engineering Engine
# =====================================================================


def compute_eta_q_expansion(N: int) -> np.ndarray:
    r"""
    Compute first N coefficients of Euler's product / Dedekind eta (without q^(1/24) shift):
    \prod_{n=1}^{\infty} (1 - q^n) = 1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + ...
    via Euler's Pentagonal Number Theorem: k(3k +- 1) / 2.
    """
    coeffs = np.zeros(N, dtype=np.float64)
    if N == 0:
        return coeffs
    coeffs[0] = 1.0

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


def polynomial_power_series(coeffs: np.ndarray, power: int, N: int) -> np.ndarray:
    """
    Compute first N coefficients of [A(q)]^power for a truncated power series A(q).
    Uses logarithmic derivative / recurrence relation for fast polynomial power.
    Requires coeffs[0] != 0.
    """
    if N == 0:
        return np.zeros(0, dtype=np.float64)
    if power == 0:
        res = np.zeros(N, dtype=np.float64)
        res[0] = 1.0
        return res
    if len(coeffs) == 0 or coeffs[0] == 0:
        raise ValueError("polynomial_power_series requires non-zero constant term coeffs[0].")

    res = np.zeros(N, dtype=np.float64)
    res[0] = coeffs[0] ** power

    a = coeffs
    for n in range(1, N):
        val = 0.0
        for k in range(1, n + 1):
            ak = a[k] if k < len(a) else 0.0
            term = (power * k - (n - k)) * ak * res[n - k]
            val += term
        res[n] = val / (n * a[0])

    return res


def multiply_series(a: np.ndarray, b: np.ndarray, N: int) -> np.ndarray:
    """Cauchy product of two power series truncated to N terms."""
    res = np.zeros(N, dtype=np.float64)
    for i in range(min(len(a), N)):
        if a[i] == 0:
            continue
        max_j = min(len(b), N - i)
        res[i : i + max_j] += a[i] * b[:max_j]
    return res


@dataclass
class EtaQuotientState:
    r"""
    State representing eta-quotient:
    f(q) = q^(q_shift_24 / 24) * \prod_{d=1}^{d_max} \eta(q^d)^{r_d}
         = q^((q_shift_24 + \sum d r_d) / 24) * \prod_d \prod_{m>=1} (1 - q^{dm})^{r_d}.
    """

    q_shift_24: int  # External shift * 24
    exponents: Dict[int, int]  # d -> r_d

    @property
    def net_q_shift_24(self) -> int:
        """Total numerator of the rational q^{(q_shift_24 + sum d*r_d)/24} prefactor."""
        return self.q_shift_24 + sum(d * r for d, r in self.exponents.items())

    def copy(self) -> "EtaQuotientState":
        return EtaQuotientState(self.q_shift_24, dict(self.exponents))

    def get_q_expansion(self, N: int, include_integer_shift: bool = False) -> np.ndarray:
        r"""
        Compute first N coefficients of the integral product \prod_d \prod_{m>=1} (1 - q^{dm})^{r_d}.

        Note: By default (`include_integer_shift=False`), the rational prefactor
        `q^{net_q_shift_24 / 24}` is omitted (matching stripped integer q-series targets).
        When `include_integer_shift=True` and `net_q_shift_24 >= 0` is divisible by 24,
        the exact integer shift `q^{net_q_shift_24 // 24}` is applied; fractional or negative
        shifts cannot be represented in an integer-indexed Taylor vector `[a_0, ..., a_{N-1}]`.
        """
        res = np.zeros(N, dtype=np.float64)
        if N == 0:
            return res
        res[0] = 1.0

        eta_base = compute_eta_q_expansion(N)

        for d, r in sorted(self.exponents.items()):
            if r == 0:
                continue
            dilated = np.zeros(N, dtype=np.float64)
            for i in range(N):
                if i * d < N:
                    dilated[i * d] = eta_base[i]
                else:
                    break

            powered = polynomial_power_series(dilated, r, N)
            res = multiply_series(res, powered, N)

        if include_integer_shift:
            net_24 = self.net_q_shift_24
            if net_24 > 0 and net_24 % 24 == 0:
                k_int = net_24 // 24
                shifted = np.zeros(N, dtype=np.float64)
                if k_int < N:
                    shifted[k_int:] = res[: N - k_int]
                res = shifted

        return res


class TrackAInverseEngineering:
    """RAMA Track A (Tier C): Inverse Engineering q-Series into Minimal Eta-Quotients."""

    def __init__(self, target_coeffs: np.ndarray, d_max: int = 12):
        self.target_coeffs = target_coeffs
        self.N = len(target_coeffs)
        self.d_max = d_max

    def compute_metrics(self, state: EtaQuotientState) -> Tuple[float, float, float]:
        """Compute normalized C (syntactic complexity), I (fit error), and D (aesthetic penalty)."""
        num_factors = sum(1 for r in state.exponents.values() if r != 0)
        has_shift = 1 if state.q_shift_24 != 0 else 0
        raw_C = num_factors + has_shift
        C = float(raw_C / 4.0)

        series = state.get_q_expansion(self.N)
        target_norm_sq = float(np.sum(self.target_coeffs ** 2)) + 1e-8
        fit_error_sq = float(np.sum((series - self.target_coeffs) ** 2))
        I = float(fit_error_sq / target_norm_sq)

        modulus_penalty = sum(abs(r) * (d ** 1.2) for d, r in state.exponents.items())
        imbalance = abs(sum(state.exponents.values()))
        raw_D = 0.05 * modulus_penalty + 0.5 * imbalance
        D = float(raw_D / 10.0)

        return C, I, D

    def get_neighbors(self, state: EtaQuotientState) -> List[EtaQuotientState]:
        """Generate micro-operator, macro-jump, and coupled alignment neighborhood N(p)."""
        neighbors = []

        # Micro-op 1: Exponent edit (r_d += delta)
        for d in range(1, self.d_max + 1):
            for delta in [-24, -12, -4, -2, -1, 1, 2, 4, 12, 24]:
                ns = state.copy()
                ns.exponents[d] = ns.exponents.get(d, 0) + delta
                if ns.exponents[d] == 0:
                    del ns.exponents[d]
                neighbors.append(ns)

                # Coupled alignment edit (preserves net q-shift)
                ns_coupled = state.copy()
                ns_coupled.exponents[d] = ns_coupled.exponents.get(d, 0) + delta
                if ns_coupled.exponents[d] == 0:
                    del ns_coupled.exponents[d]
                ns_coupled.q_shift_24 -= d * delta
                neighbors.append(ns_coupled)

        # Micro-op 2: Modular shift (q_shift_24 += shift_delta)
        for shift_delta in [-24, -1, 1, 24]:
            ns = state.copy()
            ns.q_shift_24 += shift_delta
            neighbors.append(ns)

        # Micro-op 3: Cyclotomic move (d -> m*d)
        for d, r in list(state.exponents.items()):
            for m in [2, 3]:
                if d * m <= self.d_max:
                    ns = state.copy()
                    del ns.exponents[d]
                    ns.exponents[d * m] = ns.exponents.get(d * m, 0) + r
                    neighbors.append(ns)

        return neighbors


# =====================================================================
# Track B: Quantum Cyclotomic Fingerprints & Shadow Gadgets (Tier X)
# =====================================================================


@dataclass
class CircuitShadowState:
    """State representing a synthetic Quantum Circuit configuration with Shadow Gadgets."""

    num_qubits: int
    depth: int
    gadget_period: int  # Period for R_z(pi/m) insertion
    active_modulus: int  # m in {4, 6, 8}

    def copy(self) -> "CircuitShadowState":
        return CircuitShadowState(
            self.num_qubits, self.depth, self.gadget_period, self.active_modulus
        )


class TrackBCyclotomicFingerprints:
    """
    RAMA Track B (Tier-X synthetic simulation): Cyclotomic Fingerprints & Shadow Gadget Search.
    Applies a diagonal phase oracle followed by a unitary Walsh-Hadamard interference layer
    H^{tensor n} so phase structure measurably alters output bitstring probabilities.
    """

    def __init__(self, num_qubits: int = 8, depth: int = 12, seed: Optional[int] = 42):
        self.num_qubits = num_qubits
        self.depth = depth
        self.seed = seed

    @staticmethod
    def _walsh_hadamard(vec: np.ndarray) -> np.ndarray:
        """Apply normalized n-qubit Walsh-Hadamard transform H^{tensor n}."""
        out = vec.astype(np.complex128, copy=True)
        dim = len(out)
        h = 1
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        while h < dim:
            for i in range(0, dim, h * 2):
                a = out[i : i + h].copy()
                b = out[i + h : i + 2 * h]
                out[i : i + h] = (a + b) * inv_sqrt2
                out[i + h : i + 2 * h] = (a - b) * inv_sqrt2
            h *= 2
        return out

    @staticmethod
    def compute_cyclotomic_moment(probs: np.ndarray, modulus: int) -> complex:
        r"""
        Compute cyclotomic moment S_m = E_{x~p}[exp(2\pi i |x| / m)]
        where |x| is the Hamming weight of bitstring x.
        """
        moment = 0.0 + 0.0j
        for x_int in range(len(probs)):
            p = probs[x_int]
            if p == 0:
                continue
            hamming_weight = bin(x_int).count("1")
            phase = 2.0 * math.pi * hamming_weight / modulus
            moment += p * cmath.exp(1j * phase)

        return moment

    def simulate_quantum_distribution(self, state: CircuitShadowState) -> np.ndarray:
        """
        Simulate output probability distribution using a local deterministic RNG,
        diagonal phase oracle with optional R_z(pi/m) shadow gadget phase alignment,
        and a unitary Walsh-Hadamard interference readout layer.
        """
        dim = 2 ** state.num_qubits
        local_seed = (
            (self.seed if self.seed is not None else 0) * 10007
            + state.num_qubits * 100
            + state.depth
        )
        rng = np.random.default_rng(local_seed)
        raw_phases = rng.uniform(0.0, 2.0 * math.pi, dim)

        if state.gadget_period > 0:
            for x_int in range(dim):
                hw = bin(x_int).count("1")
                gadget_boost = (
                    (hw % state.active_modulus)
                    * (math.pi / state.active_modulus)
                    / state.gadget_period
                )
                raw_phases[x_int] += gadget_boost

        state_vec = np.exp(1j * raw_phases) / math.sqrt(dim)
        # Unitary interference readout converts phase structure into bitstring probabilities
        interfered = self._walsh_hadamard(state_vec)
        probs = np.abs(interfered) ** 2
        probs /= np.sum(probs)
        return probs

    def generate_matched_product_baseline(self, quantum_probs: np.ndarray) -> np.ndarray:
        """Generate matched product-state distribution with identical mean Hamming weight."""
        num_qubits = int(math.log2(len(quantum_probs)))
        dim = len(quantum_probs)

        mean_hw = sum(bin(x).count("1") * quantum_probs[x] for x in range(dim))
        p_single = min(1.0, max(0.0, mean_hw / num_qubits))

        prod_probs = np.zeros(dim, dtype=np.float64)
        for x in range(dim):
            hw = bin(x).count("1")
            prod_probs[x] = (p_single ** hw) * ((1.0 - p_single) ** (num_qubits - hw))

        prod_probs /= np.sum(prod_probs)
        return prod_probs

    def compute_separability_auc(self, state: CircuitShadowState) -> float:
        """
        Compute synthetic separability score (AUC proxy) from genuine |S_m| difference
        between the interfered quantum distribution and its matched product baseline.
        """
        q_probs = self.simulate_quantum_distribution(state)
        c_probs = self.generate_matched_product_baseline(q_probs)

        m = state.active_modulus
        q_moment = abs(self.compute_cyclotomic_moment(q_probs, m))
        c_moment = abs(self.compute_cyclotomic_moment(c_probs, m))

        delta_m = abs(q_moment - c_moment)
        auc = 0.5 + 2.0 * delta_m
        return min(0.99, max(0.50, auc))

    def compute_metrics(self, state: CircuitShadowState) -> Tuple[float, float, float]:
        """Compute normalized C (schedule length ratio), I (-AUC), D (irregularity)."""
        C = float(1.0 / state.gadget_period) if state.gadget_period > 0 else 0.0
        auc = self.compute_separability_auc(state)
        I = -float(auc)
        D = 0.1 * abs(state.gadget_period - 2) if state.gadget_period > 0 else 0.5
        return C, I, D


# =====================================================================
# RAMA Meta-Algorithm Search Engine (Algorithm 1 in Paper)
# =====================================================================


class RAMAMetaEngine:
    """
    Main RAMA Search Engine implementing Algorithm 1: Annealed local search
    over symbolic states under energy functional E = alpha*C + beta*I + gamma*D.
    Uses a local `random.Random` instance without mutating global RNG state.
    """

    def __init__(
        self,
        weights: EnergyWeights = EnergyWeights(),
        seed: Optional[int] = 42,
    ):
        self.weights = weights
        self.rng = random.Random(seed)

    def search(
        self,
        initial_state: Any,
        get_neighbors_fn: Callable[[Any], List[Any]],
        compute_metrics_fn: Callable[[Any], Tuple[float, float, float]],
        max_iterations: int = 250,
        initial_temp: float = 2.0,
        cooling_rate: float = 0.98,
    ) -> Tuple[Any, List[Dict[str, float]]]:
        """
        Execute RAMA Meta-Algorithm stochastic local search with simulated annealing.
        Returns best state found and trajectory log.
        """
        current_state = initial_state
        C, I, D = compute_metrics_fn(current_state)
        current_energy = self.weights.alpha * C + self.weights.beta * I + self.weights.gamma * D

        best_state = current_state
        best_energy = current_energy

        temp = initial_temp
        history = []

        for step in range(max_iterations):
            history.append(
                {
                    "step": step,
                    "energy": current_energy,
                    "C": C,
                    "I": I,
                    "D": D,
                    "temp": temp,
                }
            )

            neighbors = get_neighbors_fn(current_state)
            if not neighbors:
                break

            sample_size = min(20, len(neighbors))
            cand_subset = self.rng.sample(neighbors, sample_size)

            best_cand = None
            best_cand_energy = float("inf")
            best_cand_metrics = None

            for cand in cand_subset:
                cC, cI, cD = compute_metrics_fn(cand)
                c_energy = self.weights.alpha * cC + self.weights.beta * cI + self.weights.gamma * cD
                if c_energy < best_cand_energy:
                    best_cand_energy = c_energy
                    best_cand = cand
                    best_cand_metrics = (cC, cI, cD)

            delta_e = best_cand_energy - current_energy
            accept = False
            if delta_e <= 0:
                accept = True
            else:
                prob = math.exp(-delta_e / max(temp, 1e-5))
                if self.rng.random() < prob:
                    accept = True

            if accept:
                current_state = best_cand
                current_energy = best_cand_energy
                C, I, D = best_cand_metrics

                if current_energy < best_energy:
                    best_energy = current_energy
                    best_state = current_state

            temp *= cooling_rate
            if temp < 1e-4 and delta_e >= 0:
                break

        return best_state, history


# =====================================================================
# Ablation & Validation Suite
# =====================================================================


class RAMAAblationSuite:
    """Suite to run Track A (Tier C) & Track B (Tier X) experiments."""

    @staticmethod
    def run_track_a_partition_experiment() -> Dict[str, Any]:
        """
        Track A Targets:
        1. Partition Generator p(n): 1/eta(q) -> exponents: {1: -1}
        2. Ramanujan Tau Discriminant Delta(q): eta(q)^24 -> exponents: {1: 24}
        3. Short Quotient: eta(q)^2 / eta(q^2) -> exponents: {1: 2, 2: -1}
        """
        N = 40
        eta_base = compute_eta_q_expansion(N)

        targets = [
            ("Partition Generator p(n)", polynomial_power_series(eta_base, -1, N), {1: -1}, 0),
            ("Ramanujan Discriminant Delta(q)", polynomial_power_series(eta_base, 24, N), {1: 24}, 24),
            (
                "Short Quotient eta(q)^2 / eta(q^2)",
                multiply_series(
                    polynomial_power_series(eta_base, 2, N),
                    polynomial_power_series(
                        np.array([eta_base[i // 2] if i % 2 == 0 else 0 for i in range(N)]), -1, N
                    ),
                    N,
                ),
                {1: 2, 2: -1},
                0,
            ),
        ]

        results = []
        for name, coeffs, _expected_exp, _expected_shift in targets:
            track_a = TrackAInverseEngineering(coeffs, d_max=6)
            engine = RAMAMetaEngine(EnergyWeights(alpha=1.0, beta=1.0, gamma=0.2), seed=42)
            init_state = EtaQuotientState(q_shift_24=0, exponents={1: 1})

            best_state, _ = engine.search(
                init_state,
                track_a.get_neighbors,
                track_a.compute_metrics,
                max_iterations=200,
                initial_temp=2.5,
                cooling_rate=0.97,
            )
            c, i, _d = track_a.compute_metrics(best_state)

            results.append(
                {
                    "target": name,
                    "exponents": best_state.exponents,
                    "q_shift_24": best_state.q_shift_24,
                    "fit_error_I": i,
                    "complexity_C": c,
                    "converged": i < 1e-5,
                }
            )

        return {"targets": results}

    @staticmethod
    def run_track_b_quantum_experiment() -> Dict[str, Any]:
        """Track B Target (Tier-X synthetic): Shadow Gadget Optimization for Quantum Circuits."""
        track_b = TrackBCyclotomicFingerprints(num_qubits=8, depth=12, seed=42)

        init_state = CircuitShadowState(num_qubits=8, depth=12, gadget_period=0, active_modulus=4)
        auc_no_shadow = track_b.compute_separability_auc(init_state)

        engine = RAMAMetaEngine(EnergyWeights(alpha=0.1, beta=1.0, gamma=0.1), seed=42)

        def get_quantum_neighbors(st: CircuitShadowState) -> List[CircuitShadowState]:
            neighbors = []
            for p in [0, 1, 2, 3, 4, 6]:
                for m in [4, 6, 8]:
                    ns = st.copy()
                    ns.gadget_period = p
                    ns.active_modulus = m
                    neighbors.append(ns)
            return neighbors

        best_state, _hist = engine.search(
            init_state, get_quantum_neighbors, track_b.compute_metrics, max_iterations=30
        )
        auc_with_shadow = track_b.compute_separability_auc(best_state)

        return {
            "num_qubits": 8,
            "depth": 12,
            "epistemic_tier": "X",
            "AUC_without_shadow": round(auc_no_shadow, 4),
            "AUC_with_RAMA_shadow": round(auc_with_shadow, 4),
            "delta_AUC": round(auc_with_shadow - auc_no_shadow, 4),
            "optimal_gadget_period": best_state.gadget_period,
            "optimal_modulus": best_state.active_modulus,
        }


if __name__ == "__main__":
    print("=================================================================")
    print("      RAMA META-ALGORITHMIC FRAMEWORK DEMONSTRATION")
    print("=================================================================")

    print("\n--- Running Track A: q-Series Inverse Engineering (Multi-Target) ---")
    res_a = RAMAAblationSuite.run_track_a_partition_experiment()
    for item in res_a["targets"]:
        print(f"\nTarget: {item['target']}")
        print(f"  Recovered Form: q^({item['q_shift_24']}/24) * eta(q)^{item['exponents']}")
        print(f"  Fit Error (I): {item['fit_error_I']:.6f} | Complexity (C): {item['complexity_C']:.4f}")
        print(f"  Exact Match Recovered: {item['converged']}")

    print("\n--- Running Track B: Quantum Cyclotomic Fingerprints (Tier-X Synthetic) ---")
    res_b = RAMAAblationSuite.run_track_b_quantum_experiment()
    print(f"AUC Without Shadow Gadget: {res_b['AUC_without_shadow']}")
    print(f"AUC With RAMA Shadow Gadget: {res_b['AUC_with_RAMA_shadow']}")
    print(f"Delta AUC Gain: {res_b['delta_AUC']:+.4f} across modulus m={res_b['optimal_modulus']}")
    print(f"Optimal R_z(pi/{res_b['optimal_modulus']}) Gadget Period: Every {res_b['optimal_gadget_period']} layers")

"""
tests/test_ramanujan_elenchus_canon.py
======================================
Cross-domain exact Python verification and Mathesis-Gate hygiene audit for
`dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean`.
"""

from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.math_engine.exact_qseries import CLASSICAL_CATALOG, eta_quotient_coeffs

LEAN_CANON_PATH = (
    ROOT / "dualscale" / "lean" / "DualScale" / "Discovery" / "RamanujanElenchusCanon.lean"
)
MATHESIS_GATE_PATH = ROOT / "tools" / "mathesis-gate" / "mathesis_gate.py"
AUDIT_LEAN_PATH = ROOT / "dualscale" / "ci" / "audit_lean.py"
MANIFEST_PATH = ROOT / "docs" / "literature" / "corpus_manifest.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _poly_mul(a: list[int], b: list[int], n_terms: int) -> list[int]:
    return [
        sum(
            (a[k] if k < len(a) else 0) * (b[n - k] if n - k < len(b) else 0)
            for k in range(n + 1)
        )
        for n in range(n_terms)
    ]


def _poly_inv(a: list[int], n_terms: int) -> list[int]:
    if n_terms == 0:
        return []
    assert a[0] == 1
    acc = [1]
    for n in range(1, n_terms):
        s = sum((a[n - j] if n - j < len(a) else 0) * acc[j] for j in range(n))
        acc.append(-s)
    return acc


def _poly_add(a: list[int], b: list[int], n_terms: int) -> list[int]:
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n_terms)]


def _poly_sub(a: list[int], b: list[int], n_terms: int) -> list[int]:
    return [(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n_terms)]


def _poly_shift(s: int, a: list[int], n_terms: int) -> list[int]:
    return [(a[i - s] if i >= s and (i - s) < len(a) else 0) for i in range(n_terms)]


def _qpoch_poly(a_coeff: int, step: int, start: int, num_terms: int, n_terms: int) -> list[int]:
    acc = [1] + [0] * (n_terms - 1)
    for j in range(num_terms):
        exp = start + j * step
        if exp < n_terms:
            term = [1 if i == 0 else (a_coeff if i == exp else 0) for i in range(n_terms)]
            acc = _poly_mul(acc, term, n_terms)
    return acc


def _series_neg(a: list[int]) -> list[int]:
    return [v if i % 2 == 0 else -v for i, v in enumerate(a)]


def _partition_table(n_terms: int) -> list[int]:
    p = [0] * n_terms
    if n_terms > 0:
        p[0] = 1
    for n in range(1, n_terms):
        total = 0
        k = 1
        while True:
            p1 = k * (3 * k - 1) // 2
            if p1 > n:
                break
            sgn = 1 if k % 2 == 1 else -1
            t1 = p[n - p1]
            p2 = k * (3 * k + 1) // 2
            t2 = p[n - p2] if p2 <= n else 0
            total += sgn * (t1 + t2)
            k += 1
        p[n] = total
    return p


def _mobius(k: int) -> int:
    if k <= 0:
        return 0
    if k == 1:
        return 1
    d = 2
    sign = 1
    rem = k
    while d * d <= rem:
        if rem % (d * d) == 0:
            return 0
        if rem % d == 0:
            rem //= d
            sign = -sign
        d += 1
    return -sign if rem > 1 else sign


def _ramanujan_sum(q: int, n: int) -> int:
    if q == 0:
        return 0
    return sum(d * _mobius(q // d) for d in range(1, q + 1) if q % d == 0 and n % d == 0)


def _num_divisors(n: int) -> int:
    return sum(1 for d in range(1, n + 1) if n % d == 0)


def _ramanujan_pi_partial(k_max: int, c0: int = 1103) -> Fraction:
    s = Fraction(0, 1)
    for k in range(k_max + 1):
        num = math.factorial(4 * k) * (c0 + 26390 * k)
        den = (math.factorial(k) ** 4) * (396 ** (4 * k))
        s += Fraction(num, den)
    return s / 9801


def _arctan_partial(inv_m: int, terms: int) -> Fraction:
    return sum(
        Fraction((-1) ** j, (2 * j + 1) * (inv_m ** (2 * j + 1)))
        for j in range(terms)
    )


class TestRamanujanCanonCrossConsistency:
    def test_domain1_partitions_euler_and_pentagonal(self):
        p = _partition_table(65)
        eta1 = eta_quotient_coeffs({1: 1}, 65)
        assert p == eta_quotient_coeffs({1: -1}, 65)
        assert _poly_mul(eta1, p, 65) == [1] + [0] * 64

        # Combinatorial odd vs distinct parts for n <= 20
        def count_odd(n: int, m: int = 1) -> int:
            if n == 0:
                return 1
            if m > n:
                return 0
            return count_odd(n - m, m) + count_odd(n, m + 2)

        def count_distinct(n: int, m: int = 1) -> int:
            if n == 0:
                return 1
            if m > n:
                return 0
            return count_distinct(n - m, m + 1) + count_distinct(n, m + 1)

        prod_distinct_21 = [1] + [0] * 20
        for k in range(1, 21):
            prod_distinct_21 = _poly_mul(
                prod_distinct_21,
                [1 if i == 0 else (1 if i == k else 0) for i in range(21)],
                21,
            )
        for n in range(21):
            assert count_odd(n) == count_distinct(n) == prod_distinct_21[n]

    def test_domain2_congruences_and_generating_identities(self):
        p = _partition_table(65)
        assert all(p[5 * n + 4] % 5 == 0 for n in range(13))
        assert all(p[7 * n + 5] % 7 == 0 for n in range(9))
        assert all(p[11 * n + 6] % 11 == 0 for n in range(6))

        rhs5 = [5 * v for v in eta_quotient_coeffs({1: -6, 5: 5}, 12)]
        assert [p[5 * n + 4] for n in range(12)] == rhs5

        t1 = eta_quotient_coeffs({1: -4, 7: 3}, 9)
        t2 = eta_quotient_coeffs({1: -8, 7: 7}, 9)
        rhs7 = [7 * t1[n] + (49 * t2[n - 1] if n >= 1 else 0) for n in range(9)]
        assert [p[7 * n + 5] for n in range(9)] == rhs7

        # Negative controls: mod 5 other residues, mod 13, mod 3 all fail at n=0
        assert all(p[r] % 5 != 0 for r in range(4))
        assert all(p[beta] % 13 != 0 for beta in range(13))
        assert all(p[beta] % 3 != 0 for beta in range(3))

    def test_domain3_ramanujan_tau(self):
        tau_list = eta_quotient_coeffs({1: 24}, 16)
        expected = [
            1, -24, 252, -1472, 4830, -6048, -16744, 84480,
            -113643, -115920, 534612, -370944, -577738, 401856, 1217160, 987136,
        ]
        assert tau_list == expected

        def tau(n: int) -> int:
            return 0 if n == 0 else tau_list[n - 1]

        def sigma11(n: int) -> int:
            return sum(d ** 11 for d in range(1, n + 1) if n % d == 0)

        assert tau(6) == tau(2) * tau(3)
        assert tau(10) == tau(2) * tau(5)
        assert tau(12) == tau(3) * tau(4)
        assert tau(14) == tau(2) * tau(7)
        assert tau(15) == tau(3) * tau(5)
        assert tau(4) != tau(2) * tau(2)  # non-coprime negative control

        assert tau(4) == tau(2) ** 2 - 2 ** 11
        assert tau(9) == tau(3) ** 2 - 3 ** 11
        assert tau(8) == tau(2) * tau(4) - 2 ** 11 * tau(2)
        assert tau(16) == tau(2) * tau(8) - 2 ** 11 * tau(4)

        assert all((tau(n) - sigma11(n)) % 691 == 0 for n in range(1, 17))
        assert (tau(2) + 1 - sigma11(2)) % 691 != 0
        assert all(tau(p) ** 2 <= 4 * (p ** 11) for p in [2, 3, 5, 7, 11, 13])
        assert all(tau(n) != 0 for n in range(1, 17))
        assert all(abs(tau(n)) not in {1, 3, 5, 7, 691} for n in range(2, 17))

    def test_domain4_ramanujan_sums_and_orthogonality(self):
        for p in [2, 3, 5, 7, 11]:
            assert _mobius(p) == -1
            for n in range(15):
                assert _ramanujan_sum(p, n) == (p - 1 if n % p == 0 else -1)

        assert _ramanujan_sum(4, 2) == -2
        assert _ramanujan_sum(4, 1) == 0

        for q in range(2, 13):
            assert sum(_ramanujan_sum(q, n) for n in range(q)) == 0
        assert sum(_ramanujan_sum(1, n) for n in range(1)) == 1

        divs12 = [1, 2, 3, 4, 6, 12]
        for q in divs12:
            phi_q = sum(1 for a in range(q) if math.gcd(a, q) == 1)
            for r in divs12:
                lhs = sum(_ramanujan_sum(q, n) * _ramanujan_sum(r, n) for n in range(12))
                assert lhs == (12 * phi_q if q == r else 0)

    def test_domain5_rogers_ramanujan_and_euler_wallis(self):
        rr_g = [0] * 16
        rr_h = [0] * 16
        for n in range(16):
            inv_q = _poly_inv(_qpoch_poly(-1, 1, 1, n, 16), 16)
            if n * n < 16:
                rr_g = _poly_add(rr_g, _poly_shift(n * n, inv_q, 16), 16)
            if n * (n + 1) < 16:
                rr_h = _poly_add(rr_h, _poly_shift(n * (n + 1), inv_q, 16), 16)

        assert rr_g == CLASSICAL_CATALOG["rogers_ramanujan_G"]["coeffs"][:16]
        assert rr_h == CLASSICAL_CATALOG["rogers_ramanujan_H"]["coeffs"][:16]
        assert rr_g == _poly_inv(
            _poly_mul(_qpoch_poly(-1, 5, 1, 16, 16), _qpoch_poly(-1, 5, 4, 16, 16), 16), 16
        )
        assert rr_h == _poly_inv(
            _poly_mul(_qpoch_poly(-1, 5, 2, 16, 16), _qpoch_poly(-1, 5, 3, 16, 16), 16), 16
        )

        # Convergent P_6 / Q_6 matches H / G up to q^15
        p_prev, q_prev = [1] + [0] * 15, [0] * 16
        p_cur, q_cur = [0] * 16, [1] + [0] * 15
        for k in range(6):
            p_next = _poly_add(p_cur, _poly_shift(k, p_prev, 16), 16)
            q_next = _poly_add(q_cur, _poly_shift(k, q_prev, 16), 16)
            p_prev, q_prev, p_cur, q_cur = p_cur, q_cur, p_next, q_next
        h_over_g = _poly_mul(rr_h, _poly_inv(rr_g, 16), 16)
        assert _poly_mul(p_cur, _poly_inv(q_cur, 16), 16) == h_over_g
        assert h_over_g == [1, -1, 1, 0, -1, 1, -1, 1, 0, -1, 2, -3, 2, 0, -2, 4]

        # Negative control: unshifted eta ratio disagrees at q^1
        wrong_eta = eta_quotient_coeffs({1: -1, 2: 1, 3: 1, 4: -1}, 16)
        assert wrong_eta[1] == 1 and h_over_g[1] == -1 and wrong_eta != h_over_g

    def test_domain6_mock_theta_third_order(self):
        mock_f = [0] * 16
        mock_phi = [0] * 16
        mock_psi = [0] * 16
        for n in range(16):
            if n * n < 16:
                p_f = _qpoch_poly(1, 1, 1, n, 16)
                mock_f = _poly_add(
                    mock_f, _poly_shift(n * n, _poly_inv(_poly_mul(p_f, p_f, 16), 16), 16), 16
                )
                mock_phi = _poly_add(
                    mock_phi, _poly_shift(n * n, _poly_inv(_qpoch_poly(1, 2, 2, n, 16), 16), 16), 16
                )
                if n >= 1:
                    mock_psi = _poly_add(
                        mock_psi, _poly_shift(n * n, _poly_inv(_qpoch_poly(-1, 2, 1, n, 16), 16), 16), 16
                    )

        assert mock_f == CLASSICAL_CATALOG["mock3_f"]["coeffs"][:16]
        assert mock_phi == CLASSICAL_CATALOG["mock3_phi"]["coeffs"][:16]
        assert mock_psi == CLASSICAL_CATALOG["mock3_psi"]["coeffs"][:16]
        assert mock_psi[0] == 0  # falsifies legacy MockTheta.lean stub

        eta3_2 = eta_quotient_coeffs({1: 3, 2: -2}, 16)
        assert _poly_add(mock_f, [4 * v for v in _series_neg(mock_psi)], 16) == eta3_2
        assert _poly_sub([2 * v for v in _series_neg(mock_phi)], mock_f, 16) == eta3_2
        assert _poly_sub(mock_phi, _series_neg(mock_f), 16) == [2 * v for v in mock_psi]
        assert mock_f != eta3_2
        assert _poly_add(mock_f, [2 * v for v in _series_neg(mock_psi)], 16) != eta3_2

    def test_domain7_hcn_and_taxicab_1729(self):
        expected_hcns = [1, 2, 4, 6, 12, 24, 36, 48, 60, 120]
        for n in expected_hcns:
            dn = _num_divisors(n)
            assert all(_num_divisors(m) < dn for m in range(1, n))

        # Non-HCN negative controls
        assert _num_divisors(12) == 6 and _num_divisors(18) == 6
        assert _num_divisors(60) == 12 and _num_divisors(100) == 9

        # Taxicab 1729 minimality and 1728 negative control
        sums: dict[int, list[tuple[int, int]]] = {}
        for a in range(1, 13):
            for b in range(a, 13):
                s = a ** 3 + b ** 3
                sums.setdefault(s, []).append((a, b))
        assert sums[1729] == [(1, 12), (9, 10)]
        assert 1728 not in sums
        assert all(s >= 1729 for s, pairs in sums.items() if len(pairs) >= 2)

    def test_domain8_ramanujan_one_over_pi_series(self):
        s0 = _ramanujan_pi_partial(0)
        s1 = _ramanujan_pi_partial(1)
        s2 = _ramanujan_pi_partial(2)
        s1_pert = _ramanujan_pi_partial(1, c0=1102)

        assert (s0.numerator, s0.denominator) == (1103, 9801)
        assert (s1.numerator, s1.denominator) == (1130173253125, 10042454926944)

        machin_lo = 4 * (4 * _arctan_partial(5, 12) - _arctan_partial(239, 3))
        machin_hi = 4 * (4 * _arctan_partial(5, 13) - _arctan_partial(239, 4))
        assert Fraction(314159265358979, 10 ** 14) < machin_lo
        assert machin_hi < Fraction(314159265358980, 10 ** 14)

        def bracket_ok(s: Fraction, lo: Fraction, hi: Fraction) -> bool:
            return s > 0 and lo > 0 and hi > 0 and (1 / (hi ** 2)) < 8 * (s ** 2) < (1 / (lo ** 2))

        assert bracket_ok(s0, Fraction(3141592, 10 ** 6), Fraction(3141593, 10 ** 6))
        assert bracket_ok(s1, Fraction(314159265358979, 10 ** 14), Fraction(314159265358980, 10 ** 14))
        assert bracket_ok(s2, machin_lo, machin_hi)
        assert 8 * (s1 ** 2) < Fraction(1, 1) / (machin_hi ** 2)

        # Negative controls
        assert not bracket_ok(s0, Fraction(314159265358979, 10 ** 14), Fraction(314159265358980, 10 ** 14))
        assert 8 * (s1_pert ** 2) < Fraction(1, 1) / (Fraction(3142, 1000) ** 2)
        assert not bracket_ok(s1_pert, Fraction(3141, 1000), Fraction(3142, 1000))

        # Convergence rate 4e7 * t_{k+1} < t_k for k = 0..20
        for k in range(21):
            num_k = math.factorial(4 * k) * (1103 + 26390 * k)
            den_k = (math.factorial(k) ** 4) * (396 ** (4 * k))
            num_k1 = math.factorial(4 * (k + 1)) * (1103 + 26390 * (k + 1))
            den_k1 = (math.factorial(k + 1) ** 4) * (396 ** (4 * (k + 1)))
            assert 4 * (10 ** 7) * (num_k1 * den_k) < num_k * den_k1


class TestRamanujanCanonLeanGates:
    def test_contract_hygiene_vacuity_and_negative_controls(self):
        mathesis_gate = _load_module("mathesis_gate", MATHESIS_GATE_PATH)
        text = LEAN_CANON_PATH.read_text(encoding="utf-8")
        stripped = mathesis_gate.strip_comments(text)
        lines = text.splitlines()
        assert lines[0].strip() == "-- MATHESIS-GATE: env=none"
        assert lines[1].strip() == "-- MATHESIS-GATE: allow=propext"

        assert "sorry" not in text
        assert not re.search(r"^\s*import\b", stripped, flags=re.MULTILINE)
        assert "import Mathlib" not in stripped
        assert "native_decide" not in stripped
        assert "Classical.choice" not in stripped
        assert "open Classical" not in stripped
        assert "Quot.lift" not in stripped
        assert ": Prop := True" not in stripped
        assert "by trivial" not in stripped
        assert "by rfl" not in stripped
        assert not re.search(r"^\s*axiom\s+", stripped, flags=re.MULTILINE)

        # Theorem / #print axioms 1-to-1 parity
        thms = re.findall(r"^theorem\s+([A-Za-z0-9_.']+)\b", text, flags=re.MULTILINE)
        prints = re.findall(r"^\s*#print\s+axioms\s+([A-Za-z0-9_.']+)\b", text, flags=re.MULTILINE)
        assert len(thms) >= 75
        assert thms == prints

        # All >= 8 (and all 20 required) neg_ctrl_ theorems present
        neg_ctrls = [t for t in thms if t.startswith("neg_ctrl_")]
        assert len(neg_ctrls) >= 8
        required_neg_ctrls = {
            "neg_ctrl_even_parts_ne_distinct",
            "neg_ctrl_omit_part1_distinct_fails",
            "neg_ctrl_mod5_other_residues_fail",
            "neg_ctrl_mod13_no_linear_congruence",
            "neg_ctrl_mod3_no_linear_congruence",
            "neg_ctrl_tau_noncoprime_fails",
            "neg_ctrl_tau_mod691_perturbed_fails",
            "neg_ctrl_ramanujanSum_composite_4_fails_prime_rule",
            "neg_ctrl_ramanujanSum_q1_nonzero_sum",
            "neg_ctrl_rr_unshifted_eta_ratio_fails",
            "neg_ctrl_euler_wallis_missing_sign_fails",
            "neg_ctrl_rr_G_ne_H",
            "neg_ctrl_mock3_psi_legacy_stub_q0_false",
            "neg_ctrl_mock3_f_not_eta_shadow",
            "neg_ctrl_mock3_f_plus_2psi_neg_fails",
            "neg_ctrl_taxicab_1728_no_pos_cube_sum",
            "neg_ctrl_hcn_18_not_hcn",
            "neg_ctrl_hcn_100_not_hcn",
            "neg_ctrl_pi_S0_fails_14_digits",
            "neg_ctrl_pi_perturbed_1103_to_1102_fails",
        }
        assert required_neg_ctrls.issubset(set(neg_ctrls))

        # Rule R4: every arXiv ID mentioned in the Lean file is verified in corpus_manifest.json
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest_ids = {p["arxiv_id"] for p in manifest["papers"]}
        cited_ids = set(re.findall(r"\b(?:math/\d{7}|\d{4}\.\d{4,5})\b", text))
        assert len(cited_ids) == 10
        assert cited_ids.issubset(manifest_ids)

    def test_mathesis_gate_and_audit_lean_static_checks(self):
        mathesis_gate = _load_module("mathesis_gate", MATHESIS_GATE_PATH)
        audit_lean = _load_module("audit_lean", AUDIT_LEAN_PATH)

        assert mathesis_gate.self_test() == []
        contract = mathesis_gate.parse_contract(LEAN_CANON_PATH)
        assert contract.env == "none"
        assert contract.file_allow == {"propext"}

        assert mathesis_gate.check_hygiene([LEAN_CANON_PATH], LEAN_CANON_PATH.parent, allow_sorry=False) == []
        assert mathesis_gate.check_vacuity([LEAN_CANON_PATH], LEAN_CANON_PATH.parent) == []

        errors, warnings = audit_lean.audit_file(str(LEAN_CANON_PATH))
        assert errors == []
        assert warnings == []

        res = subprocess.run(
            [sys.executable, str(MATHESIS_GATE_PATH), "--skip-footprints", str(LEAN_CANON_PATH)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert res.returncode == 0, res.stdout + res.stderr
        assert "ALL CHECKS PASS" in res.stdout

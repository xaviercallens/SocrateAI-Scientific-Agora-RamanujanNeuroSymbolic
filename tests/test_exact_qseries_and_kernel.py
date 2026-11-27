"""
tests/test_exact_qseries_and_kernel.py
======================================
Unit tests for exact arbitrary-precision q-series arithmetic, deterministic
Möbius inversion (with overdetermination anti-overfitting guard), classical
Ramanujan mock-theta catalog, and standalone zero-custom-axiom Lean 4 kernel prover.
"""

from fractions import Fraction
from pathlib import Path
import re
import pytest

from src.lean.kernel_prover import (
    KERNEL_PRELUDE,
    generate_equation_lean_block,
    verify_single_eta_quotient_lean,
)
from src.math_engine.exact_qseries import (
    CLASSICAL_CATALOG,
    compute_eta_invariants,
    eta_quotient_coeffs,
    invert_eta_quotient_exact,
    match_classical_catalog,
)


class TestExactQSeries:
    def test_classical_oeis_prefixes(self):
        assert CLASSICAL_CATALOG["partition_p"]["coeffs"][:10] == [1, 1, 2, 3, 5, 7, 11, 15, 22, 30]
        assert CLASSICAL_CATALOG["euler_eta"]["coeffs"][:10] == [1, -1, -1, 0, 0, 1, 0, 1, 0, 0]
        assert CLASSICAL_CATALOG["rogers_ramanujan_G"]["coeffs"][:10] == [1, 1, 1, 1, 2, 2, 3, 3, 4, 5]
        assert CLASSICAL_CATALOG["rogers_ramanujan_H"]["coeffs"][:10] == [1, 0, 1, 1, 1, 1, 2, 2, 3, 3]
        assert CLASSICAL_CATALOG["mock3_f"]["coeffs"][:10] == [1, 1, -2, 3, -3, 3, -5, 7, -6, 6]
        assert CLASSICAL_CATALOG["mock3_phi"]["coeffs"][:10] == [1, 1, 0, -1, 1, 1, -1, -1, 0, 2]
        assert CLASSICAL_CATALOG["mock3_psi"]["coeffs"][:10] == [0, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        assert CLASSICAL_CATALOG["mock6_phi"]["coeffs"][:10] == [1, -1, 2, -1, 1, -3, 3, -3, 4, -4]
        assert CLASSICAL_CATALOG["theta_3"]["coeffs"][:10] == [1, 2, 0, 0, 2, 0, 0, 0, 0, 2]

    def test_mobius_inversion_exact_and_anti_overfitting(self):
        # Exact recovery of partition function 1/eta(q)
        res_p = invert_eta_quotient_exact(eta_quotient_coeffs({1: -1}, 12))
        assert res_p["is_exact_eta_quotient"] is True
        assert res_p["exponents"] == {1: -1}
        assert res_p["overdetermination_degree"] >= 3

        # Exact recovery of Jacobi theta_3
        res_t3 = invert_eta_quotient_exact(eta_quotient_coeffs({1: -2, 2: 5, 4: -2}, 15))
        assert res_t3["is_exact_eta_quotient"] is True
        assert res_t3["exponents"] == {1: -2, 2: 5, 4: -2}

        # Genuine 3rd-order mock theta f(q) must NOT be misclassified as finite eta-quotient
        res_f3 = invert_eta_quotient_exact(CLASSICAL_CATALOG["mock3_f"]["coeffs"][:15])
        assert res_f3["is_exact_eta_quotient"] is False
        match = match_classical_catalog(CLASSICAL_CATALOG["mock3_f"]["coeffs"][:10])
        assert match is not None and match["oeis"] == "A000025"

    def test_invariants_sign_and_ono_164(self):
        inv_p = compute_eta_invariants({1: -1})
        assert Fraction(inv_p["c_eff_cusp0"]) == Fraction(1, 1)
        assert Fraction(inv_p["weight_k"]) == Fraction(-1, 2)
        assert inv_p["sign_classification"] == "non_negative_coefficients"

        inv_delta = compute_eta_invariants({1: 24})
        assert Fraction(inv_delta["c_eff_cusp0"]) == Fraction(-24, 1)
        assert Fraction(inv_delta["weight_k"]) == Fraction(12, 1)
        assert inv_delta["ono_164_modular_gamma0_N"] is True
        assert inv_delta["sign_classification"] == "alternating_sign_index"

        # Euler pentagonal eta(q) has negative cusp-0 c_eff = -1
        inv_eta = compute_eta_invariants({1: 1})
        assert Fraction(inv_eta["c_eff_cusp0"]) == Fraction(-1, 1)


class TestLeanKernelProver:
    def test_zero_custom_axiom_kernel_proofs(self):
        ok, _, err = verify_single_eta_quotient_lean("unit_part", {1: -1}, coeff_len=10)
        assert ok, err

        ok_t3, _, err_t3 = verify_single_eta_quotient_lean("unit_theta3", {1: -2, 2: 5, 4: -2}, coeff_len=10)
        assert ok_t3, err_t3

    def test_kernel_prelude_poly_pow_fuel_and_unmerged_equation_factors(self):
        assert "polyPowAux N (e + 1) e a one" in KERNEL_PRELUDE
        assert "polyPowAux N 16 e a one" not in KERNEL_PRELUDE

        # Unmerged factor lists preserve order and multiplicity (no reflexive LHS == RHS collapse)
        block_unmerged, thms = generate_equation_lean_block(
            "eq_test_unmerged",
            [(1, 0, [(1, -1), (2, 3), (4, -1), (1, -1)])],
            [(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])],
            check_len=16,
        )
        assert thms == ["eq_test_unmerged_identity"]
        assert "[(1, 0, [(1, -1), (2, 3), (4, -1), (1, -1)])]" in block_unmerged
        assert "[(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])]" in block_unmerged

        # Dict factor maps remain supported deterministically
        block_dict, _ = generate_equation_lean_block(
            "eq_test_dict",
            [(1, 0, {4: -2, 1: -2, 2: 5})],
            [(2, 0, {16: -2, 4: -2, 8: 5})],
        )
        assert "[(1, 0, [(1, -2), (2, 5), (4, -2)])]" in block_dict
        assert "[(2, 0, [(4, -2), (8, 5), (16, -2)])]" in block_dict

    def test_campaign_v2_verified_unmerged_and_fuel_hygiene(self):
        repo_root = Path(__file__).resolve().parent.parent
        campaign_lean = (
            repo_root / "dualscale" / "lean" / "DualScale" / "Discovery" / "CampaignV2Verified.lean"
        ).read_text(encoding="utf-8")

        assert "polyPowAux N (e + 1) e a one" in campaign_lean
        assert "polyPowAux N 16 e a one" not in campaign_lean

        lhs_defs = dict(
            re.findall(
                r"^def\s+(eq_[A-Za-z0-9_]+)_lhs\s*:[^=]+:=\s*(.+)$",
                campaign_lean,
                flags=re.MULTILINE,
            )
        )
        rhs_defs = dict(
            re.findall(
                r"^def\s+(eq_[A-Za-z0-9_]+)_rhs\s*:[^=]+:=\s*(.+)$",
                campaign_lean,
                flags=re.MULTILINE,
            )
        )
        assert lhs_defs and set(lhs_defs.keys()) == set(rhs_defs.keys())
        for eq_id in lhs_defs:
            assert lhs_defs[eq_id].strip() != rhs_defs[eq_id].strip(), (
                f"{eq_id} has identical lhs and rhs definitions"
            )

        assert lhs_defs["eq_460927b577"].strip() == "[(1, 0, [(1, -1), (2, 3), (4, -1), (1, -1)])]"
        assert rhs_defs["eq_460927b577"].strip() == "[(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])]"
        assert lhs_defs["eq_2847c49f95"].strip() == "[(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])]"
        assert rhs_defs["eq_2847c49f95"].strip() == "[(1, 0, [(1, -1), (2, 2), (4, -1), (1, -1), (2, 1)])]"

    def test_all_n_propositions_exports_nebentypus_jtp_and_deep_burn(self):
        repo_root = Path(__file__).resolve().parent.parent
        all_n_lean = (
            repo_root / "dualscale" / "lean" / "DualScale" / "Discovery" / "AllNAndPropositionsVerified.lean"
        ).read_text(encoding="utf-8")

        required_defs = [
            "def etaNebentypusSqfree12",
            "def IsWeight1Level12EtaComb",
            "def SturmBoundHolomorphicModularEq12",
            "def etaQuot_phi",
            "def etaQuot_phi_neg",
            "def etaQuot_psi",
            "def deepBurnEta",
        ]
        for marker in required_defs:
            assert marker in all_n_lean, f"Missing definition: {marker}"

        comb_match = re.search(
            r"def\s+IsWeight1Level12EtaComb\b.*?def\s+SturmBoundHolomorphicModularEq12\b",
            all_n_lean,
            flags=re.DOTALL,
        )
        assert comb_match is not None
        comb_body = comb_match.group(0)
        assert "t.2.1 == 0" in comb_body
        assert "onoSumDR eq == 0" in comb_body, (
            "IsWeight1Level12EtaComb must enforce onoSumDR eq == 0 to forbid nonzero q^k offsets"
        )

        required_theorems = [
            "dilateFPS_congr",
            "etaFPS_dilate",
            "etaQuot_phi_matches_phiCoeff_16",
            "etaQuot_phi_neg_matches_seriesNeg_phiCoeff_16",
            "etaQuot_psi_matches_psiCoeff_16",
            "eq_d6899de389_eta_all_n_of_jtp",
            "eq_c23aa45585_eta_all_n_of_jtp",
            "eq_0722eebfe8_modular_level12_weight1",
            "eq_0722eebfe8_common_nebentypus_neg3",
            "eq_0722eebfe8_all_n_conditional",
            "deepBurn_ceff_cusp0",
            "deepBurn_weight",
            "deepBurn_E0",
            "deepBurn_ono_false",
            "deepBurn_prefix_10",
            "deepBurn_has_negative_coeff",
        ]
        for thm in required_theorems:
            assert re.search(rf"^theorem\s+{re.escape(thm)}\b", all_n_lean, flags=re.MULTILINE), (
                f"Missing theorem: {thm}"
            )
            assert re.search(rf"^#print\s+axioms\s+{re.escape(thm)}\b", all_n_lean, flags=re.MULTILINE), (
                f"Missing #print axioms for theorem: {thm}"
            )

        # Cross-check Deep Burn invariants against exact Python q-series engine
        deep_burn_exps = {
            1: 24, 2: 23, 3: -14, 4: -24, 5: -24, 6: -24,
            7: -24, 8: -24, 9: -24, 10: -24, 11: -24, 12: -24,
        }
        inv = compute_eta_invariants(deep_burn_exps, expansion_terms=10)
        assert Fraction(inv["c_eff_cusp0"]) == Fraction(-823, 2310)
        assert Fraction(inv["weight_k"]) == Fraction(-183, 2)
        assert Fraction(inv["ground_state_E0"]) == Fraction(425, 6)
        assert inv["ono_cong_1_mod24"] is False
        assert eta_quotient_coeffs(deep_burn_exps, 10) == [
            1, -24, 229, -906, -1048, 24942, -78956, -114576, 1364463, -2221528
        ]


class TestLatexSymbolicParser:
    def test_verified_theta_identities_and_homonym_rejection(self):
        from src.math_engine.latex_symbolic_parser import analyze_latex_identity

        # Authentic Ramanujan Ch.15/16 identity verifies to 30 exact terms
        r1 = analyze_latex_identity(r"\phi(x) + \phi(-x) = 2\phi(x^4)", check_terms=30)
        assert r1["verified_equation"] is not None
        assert r1["verified_equation"]["lean_kernel_ready"] is True
        assert r1["refuted_equation"] is None

        # OCR typo is caught and refuted at q^2
        r_typo = analyze_latex_identity(r"\phi(x)\phi(-x) = \phi^2(x^4)", check_terms=30)
        assert r_typo["verified_equation"] is None
        assert r_typo["refuted_equation"] is not None
        assert r_typo["refuted_equation"]["first_mismatch_power"] == 2

        # Generic f(x) = Taylor series must NOT be misclassified as Ramanujan Ch.16 f(q)
        r_hom = analyze_latex_identity(r"f(x) = \frac{x^2}{2} - \frac{x^3}{12} + \frac{x^4}{48}", check_terms=30)
        assert r_hom["extracted_eta_quotients"] == []

        # Lost Notebook 3rd-order mock theta phi(q) is matched to A053250, NOT Ch.16 theta phi(q)
        r_mock = analyze_latex_identity(
            r"\phi(q) = 1 + \frac{q}{1+q^2} + \frac{q^4}{(1+q^2)(1+q^4)} + \dots", check_terms=30
        )
        assert r_mock["symbolic_catalog_match"] is not None
        assert r_mock["symbolic_catalog_match"]["oeis"] == "A053250"
        assert r_mock["extracted_eta_quotients"] == []

        # Derivatives (phi', d/dx, partial) must NOT be parsed as bare theta atoms
        r_deriv1 = analyze_latex_identity(r"\phi'(x) = x + 1", check_terms=20)
        assert r_deriv1["verified_equation"] is None
        assert r_deriv1["extracted_eta_quotients"] == []

        r_deriv2 = analyze_latex_identity(r"\frac{d}{dx}\phi(x) = x^2", check_terms=20)
        assert r_deriv2["verified_equation"] is None
        assert r_deriv2["extracted_eta_quotients"] == []

        # OCR-corrupted x(x^3) (misread \chi(x^3)) must NOT emit a spurious monomial
        r_ocr_x = analyze_latex_identity(r"x(x^3) = x^4", check_terms=20)
        assert r_ocr_x["verified_equation"] is None
        assert r_ocr_x["extracted_eta_quotients"] == []

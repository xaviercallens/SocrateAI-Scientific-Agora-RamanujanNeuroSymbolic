"""
Project NAMAGIRI — Substantive Lean 4 Code Generator (WS-3)
Generates non-trivial math statements for η-quotient verification:
- Tier A: Exact rational arithmetic verification of physical invariants
  (c_eff, weight, leading_power, ground_state_shift) via `norm_num`.
- Tier C: Heuristic metadata blueprint (no proof of modularity).
"""
from fractions import Fraction
import json
import re
from typing import Any, Dict


def _fmt_rat(f: Fraction) -> str:
    """Format an exact Fraction as a Lean 4 rational (ℚ) literal."""
    if f.denominator == 1:
        return f"({f.numerator} : ℚ)"
    return f"(({f.numerator} : ℚ) / {f.denominator})"


def _sanitize_ident(raw_id: str) -> str:
    """Normalize an identifier fragment for Lean namespaces and struct names."""
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", str(raw_id))
    return cleaned or "unknown"


def _escape_lean_string(value: str) -> str:
    """Escape a Python string for safe embedding inside a Lean 4 string literal."""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


def _sanitize_comment(value: str) -> str:
    """Collapse newlines so comment metadata cannot inject Lean declarations."""
    return " ".join(str(value).splitlines()).strip()


class LeanCodeGenerator:
    """Generates Lean 4 verification modules for candidate Dedekind eta-quotients."""

    _fmt_rat = staticmethod(_fmt_rat)

    def generate_tier_a_eta_quotient_verification(
        self, conjecture_id: str, exponents: Dict[int, int], q_shift: int = 0
    ) -> str:
        """Generate Tier A exact-rational equality theorems proved by `norm_num`."""
        for d, r in exponents.items():
            if isinstance(d, bool) or not isinstance(d, int) or d <= 0:
                raise ValueError(f"Eta-quotient divisor must be a positive int, got {d!r}")
            if isinstance(r, bool) or not isinstance(r, int):
                raise ValueError(f"Eta-quotient exponent must be an int, got {r!r}")

        clean_id = _sanitize_ident(conjecture_id)
        sorted_items = sorted(exponents.items())
        factors = sorted_items if sorted_items else [(1, 0)]
        factors_str = ", ".join(f"({d}, {r})" for d, r in factors)

        # Exact rational invariants using Fraction (aligned with EtaQuotient definitions)
        c_eff_frac = -sum((Fraction(r, d) for d, r in factors), Fraction(0))
        weight_frac = Fraction(sum(r for _, r in factors), 2)
        leading_p_frac = Fraction(sum(d * r for d, r in factors), 24)
        e0_frac = -leading_p_frac

        lines = [
            f"-- Discovery { _sanitize_comment(conjecture_id) }: η-Quotient Verification (Tier A)",
            f"-- q_shift_24 = {int(q_shift)}",
            f"namespace Discovery_{clean_id}",
            "",
            "structure EtaQuotient where",
            "  factors : List (ℕ × ℤ)",
            "",
            "def EtaQuotient.c_eff (eq : EtaQuotient) : ℚ :=",
            "  eq.factors.foldl (fun acc dr => acc - (dr.2 : ℚ) / (dr.1 : ℚ)) 0",
            "",
            "def EtaQuotient.weight (eq : EtaQuotient) : ℚ :=",
            "  (eq.factors.foldl (fun acc dr => acc + (dr.2 : ℚ)) 0) / 2",
            "",
            "def EtaQuotient.leading_power (eq : EtaQuotient) : ℚ :=",
            "  (eq.factors.foldl (fun acc dr => acc + (dr.1 : ℚ) * (dr.2 : ℚ)) 0) / 24",
            "",
            "def EtaQuotient.ground_state_shift (eq : EtaQuotient) : ℚ :=",
            "  -(eq.factors.foldl (fun acc dr => acc + (dr.1 : ℚ) * (dr.2 : ℚ)) 0) / 24",
            "",
            f"def candidate : EtaQuotient := {{ factors := [{factors_str}] }}",
            "",
            f"theorem verify_c_eff : candidate.c_eff = {_fmt_rat(c_eff_frac)} := by",
            "  dsimp [EtaQuotient.c_eff, candidate, List.foldl]",
            "  norm_num",
            "",
            f"theorem verify_weight : candidate.weight = {_fmt_rat(weight_frac)} := by",
            "  dsimp [EtaQuotient.weight, candidate, List.foldl]",
            "  norm_num",
            "",
            f"theorem verify_leading_power : candidate.leading_power = {_fmt_rat(leading_p_frac)} := by",
            "  dsimp [EtaQuotient.leading_power, candidate, List.foldl]",
            "  norm_num",
            "",
            f"theorem verify_ground_state_shift : candidate.ground_state_shift = {_fmt_rat(e0_frac)} := by",
            "  dsimp [EtaQuotient.ground_state_shift, candidate, List.foldl]",
            "  norm_num",
            "",
            f"end Discovery_{clean_id}",
            "",
        ]
        return "\n".join(lines)

    def generate_tier_b_structural_blueprint(
        self, conjecture_id: str, shadow: str, domain: str
    ) -> str:
        """
        Generate a Tier C heuristic metadata blueprint using Lean 4 structures.
        Records shadow/domain metadata only; makes no claim of modularity proof.
        """
        safe_domain = _escape_lean_string(domain)
        safe_shadow = _escape_lean_string(shadow)
        struct_name = f"MockThetaShadow_{_sanitize_ident(conjecture_id)}"

        lines = [
            f"-- Discovery {_sanitize_comment(conjecture_id)}: Heuristic Metadata Blueprint (Tier C)",
            f"-- Expected Shadow: {_sanitize_comment(shadow)}",
            f"-- Physical Domain Mapping: {_sanitize_comment(domain)}",
            f"structure {struct_name} where",
            f'  domain : String := "{safe_domain}"',
            f'  shadow_obstruction : String := "{safe_shadow}"',
            "  is_heuristic_blueprint : Bool := true",
            "",
            f"def {struct_name}_default : {struct_name} := {{}}",
            "",
        ]
        return "\n".join(lines)

    def generate_verification_file(self, conjecture_id: str, data: Dict[str, Any]) -> str:
        """Combine Mathlib imports, Tier A exact rational proofs, and Tier C metadata."""
        exponents = data.get("exponents", {})
        if isinstance(exponents, str):
            exponents = json.loads(exponents) if exponents.strip() else {}
        if not isinstance(exponents, dict):
            raise ValueError(f"exponents must be a mapping or JSON object, got {type(exponents).__name__}")

        normalized_exponents: Dict[int, int] = {}
        for k, v in exponents.items():
            d = int(k) if isinstance(k, str) else k
            r = int(v) if isinstance(v, str) else v
            normalized_exponents[d] = r

        raw_q_shift = data.get("q_shift", 0)
        q_shift = 0 if raw_q_shift is None else int(raw_q_shift)
        shadow = str(data.get("shadow", "Unknown"))
        domain = str(data.get("domain", "Unknown"))

        macros = (
            "import Mathlib.Data.Rat.Init\n"
            "import Mathlib.Tactic.NormNum\n\n"
            "-- Epistemic note: Tier A covers exact rational invariants only; "
            "modularity (Ono Thm 1.64) and positivity/unitarity remain unproved (Tier C).\n"
            "set_option maxHeartbeats 400000\n\n"
        )
        tier_a = self.generate_tier_a_eta_quotient_verification(
            conjecture_id, normalized_exponents, q_shift
        )
        tier_c = self.generate_tier_b_structural_blueprint(conjecture_id, shadow, domain)
        return macros + tier_a + "\n" + tier_c

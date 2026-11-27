"""
Sen Logarithmic Correction vs. RAMA Deep Burn Entropy Comparison (TIER X QUARANTINED)
====================================================================================
QUARANTINE NOTICE (Epistemic Tier X — QUARANTINED_LEGACY_SIGN_INVERTED):
  Exact cusp-0 c_eff for the Deep Burn η-quotient is negative:
      c_eff(0) = -sum(e_d / d) = -823/2310 = -0.3562770562770563 < 0
  and its q-expansion has alternating-sign coefficients, which invalidates the
  unitary Cardy formula S ~ 2π√(c_eff·n/6) and the Sgr A* Kerr mapping derived
  from the legacy sign-inverted +0.3563 value.

This script preserves the archival legacy comparison table strictly under explicit
Tier X quarantine metadata and never emits an unquarantined certificate.

Reference: A. Sen, Gen. Rel. Grav. 44 (2012) 1207–1266, Eq. (1.2)
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CERT_PATH = (
    REPO_ROOT / "dualscale" / "certificates" / "entropy_sen_kerr_comparison.json"
)

# ─── Physical & Exact Arithmetic Constants ────────────────────────────────────
EXPONENTS = [24, 23, -14, -24, -24, -24, -24, -24, -24, -24, -24, -24]
DIVISORS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

C_EFF_BPS = 6.0  # Strominger-Vafa, K3×T², BPS protected
C_EFF_DB_EXACT = -sum(Fraction(e, d) for e, d in zip(EXPONENTS, DIVISORS))  # -823/2310
C_EFF_DB = float(C_EFF_DB_EXACT)  # -0.3562770562770563 (negative cusp-0 value)
C_EFF_DB_LEGACY_SIGN_INVERTED = 0.3563  # Archival sign-inverted legacy constant ONLY
C_EFF_KERR = 3.0  # Near-extremal Kerr (Sen 2012, N=2 gravity)
LOG_COEFF = -3.0 / 2  # Sen logarithmic coefficient for Kerr

EPISTEMIC_TIER = "X"
QUARANTINE_STATUS = "QUARANTINED_LEGACY_SIGN_INVERTED"
QUARANTINE_WARNING = (
    "QUARANTINED: Exact cusp-0 c_eff is negative (-823/2310 = -0.3562770562770563) "
    "and the q-expansion has alternating-sign coefficients, which invalidates the "
    "unitary Cardy formula and Sgr A* Kerr mapping derived from the legacy "
    "sign-inverted +0.3563 value."
)
DEFAULT_LEVELS = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]


# ─── Entropy Formulae ─────────────────────────────────────────────────────────
def S_BPS(n: Any) -> Any:
    """Strominger-Vafa BPS entropy: Cardy with c_eff = 6."""
    return 2 * np.pi * np.sqrt(C_EFF_BPS * n / 6.0)


def S_deep_burn(n: Any) -> Any:
    """
    Exact cusp-0 Deep Burn Cardy evaluation is invalid under Tier X quarantine
    because c_eff(0) = -823/2310 < 0 and coefficients alternate in sign.
    """
    raise ValueError(QUARANTINE_WARNING)


def S_deep_burn_legacy_archival(n: Any) -> Any:
    """Archival comparison ONLY: legacy sign-inverted Cardy formula with +0.3563."""
    return 2 * np.pi * np.sqrt(C_EFF_DB_LEGACY_SIGN_INVERTED * n / 6.0)


def S_kerr_leading(n: Any) -> Any:
    """Sen leading-order Kerr entropy: 2π√(n/2)."""
    return 2 * np.pi * np.sqrt(n / 2.0)


def S_kerr_log_corrected(n: Any) -> Any:
    """Sen Kerr entropy with logarithmic correction: 2π√(n/2) - (3/2)log(n)."""
    return 2 * np.pi * np.sqrt(n / 2.0) + LOG_COEFF * np.log(n)


def S_deviation_legacy_archival(n: Any) -> Any:
    """Archival fractional deviation |S_DB_legacy - S_Kerr_log| / |S_Kerr_log|."""
    db = S_deep_burn_legacy_archival(n)
    kerr = S_kerr_log_corrected(n)
    return np.abs(db - kerr) / np.abs(kerr)


def build_quarantined_certificate(levels: Optional[List[int]] = None) -> Dict[str, Any]:
    """Build the Tier X quarantined comparison certificate JSON object."""
    if C_EFF_DB_EXACT != Fraction(-823, 2310):
        raise AssertionError(f"Expected C_EFF_DB_EXACT == -823/2310, got {C_EFF_DB_EXACT}")

    eval_levels = levels if levels is not None else DEFAULT_LEVELS
    results = []
    for n in eval_levels:
        bps = S_BPS(n)
        db_legacy = S_deep_burn_legacy_archival(n)
        kl = S_kerr_leading(n)
        klc = S_kerr_log_corrected(n)
        dev = S_deviation_legacy_archival(n)
        results.append({
            "n": int(n),
            "S_BPS": round(float(bps), 6),
            "S_DeepBurn": round(float(db_legacy), 6),
            "S_Kerr_leading": round(float(kl), 6),
            "S_Kerr_log_corrected": round(float(klc), 6),
            "fractional_deviation_DB_vs_Kerr": round(float(dev), 6),
        })

    legacy_ratio = float(np.sqrt(C_EFF_DB_LEGACY_SIGN_INVERTED / C_EFF_KERR))
    return {
        "description": "Entropy comparison: RAMA Deep Burn vs Sen Kerr corrections",
        "epistemic_tier": EPISTEMIC_TIER,
        "status": QUARANTINE_STATUS,
        "warning": QUARANTINE_WARNING,
        "parameters": {
            "c_eff_BPS": C_EFF_BPS,
            "c_eff_DeepBurn": C_EFF_DB,
            "c_eff_DeepBurn_cusp0_exact": str(C_EFF_DB_EXACT),
            "c_eff_DeepBurn_legacy_sign_inverted": C_EFF_DB_LEGACY_SIGN_INVERTED,
            "c_eff_Kerr_Sen2012": C_EFF_KERR,
            "log_correction_coefficient": LOG_COEFF,
            "reference": "A. Sen, Gen. Rel. Grav. 44 (2012) 1207-1266",
        },
        "asymptotic_ratio_DB_over_Kerr": round(legacy_ratio, 8),
        "table": results,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit Tier X quarantined Deep Burn vs Sen Kerr archival certificate."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_CERT_PATH,
        help="Destination JSON path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print quarantine summary without writing output file",
    )
    args = parser.parse_args(argv)

    cert = build_quarantined_certificate()
    print("=" * 80)
    print(f"  TIER {EPISTEMIC_TIER} [{QUARANTINE_STATUS}]")
    print(f"  {QUARANTINE_WARNING}")
    print("=" * 80)
    print(
        f"  c_eff_DeepBurn = {cert['parameters']['c_eff_DeepBurn_cusp0_exact']} "
        f"({cert['parameters']['c_eff_DeepBurn']})"
    )
    print(
        f"  archival legacy sign-inverted = "
        f"{cert['parameters']['c_eff_DeepBurn_legacy_sign_inverted']}"
    )

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(cert, indent=2), encoding="utf-8")
        print(f"  Quarantined certificate saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

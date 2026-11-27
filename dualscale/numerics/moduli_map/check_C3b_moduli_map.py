#!/usr/bin/env python3
"""
numerics/moduli_map/check_C3b_moduli_map.py — Task M4.1 (Tier X Quarantined)
=============================================================================
Computes exact rational coefficients of the s12_recurrence sequence in
refs/values.json (Apéry's order-3 ζ(3) sequence, OEIS A005259, u_5 = 819005)
and writes honest Tier X FAIL quarantine certificates because neither a K3
nor an elliptic-curve Picard-Fuchs moduli map has been constructed (the
former J = 1728 comparison was a hardcoded mock proxy).

Exit code: 0 = both quarantined certificates written, 1 = error before writing.
"""
from datetime import datetime, timezone
from fractions import Fraction
import json
import os
import subprocess
import sys

CERT_DIR = "dualscale/certificates/moduli_map"
VALUES_PATH = "dualscale/refs/values.json"

os.makedirs(CERT_DIR, exist_ok=True)


def get_git_commit():
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def load_values():
    with open(VALUES_PATH, encoding="utf-8") as f:
        return {e.get("key", e.get("anchor_id")): e for e in json.load(f)}


def s12_sequence_coefficients(n_terms: int):
    """Return the first ``n_terms`` exact rational coefficients of s12_recurrence (OEIS A005259)."""
    # Recurrence: (n+1)^3 u(n+1) = (34n^3 + 51n^2 + 27n + 5) u(n) - n^3 u(n-1), u(0)=1, u(1)=5
    coeffs = [Fraction(1), Fraction(5)]
    if n_terms <= 2:
        return coeffs[:n_terms]

    for n in range(1, n_terms - 1):
        u_n = coeffs[-1]
        u_n_minus_1 = coeffs[-2]
        term1 = Fraction(34 * n**3 + 51 * n**2 + 27 * n + 5) * u_n
        term2 = Fraction(n**3) * u_n_minus_1
        u_n_plus_1 = (term1 - term2) / Fraction((n + 1) ** 3)
        coeffs.append(u_n_plus_1)

    return coeffs


def moduli_map_k3(coeffs) -> dict:
    """Quarantined Tier X K3 moduli-map check using exact Apéry u_5 = 819005."""
    k3_threshold = Fraction(54000)
    residual = coeffs[5] - k3_threshold
    return {
        "match": False,
        "u_5": str(coeffs[5]),
        "residual": str(residual),
        "oeis": "A005259",
        "epistemic_tier": "X",
        "is_mock_proxy": True,
        "details": (
            "Quarantined Tier X mock-proxy check: values.json s12_recurrence is "
            "Apery's order-3 zeta(3) sequence (OEIS A005259, u_5 = 819005, "
            f"u_5 - 54000 = {residual}), and the former J = 1728 check was a "
            "hardcoded mock proxy, NOT a Picard-Fuchs moduli map."
        ),
    }


def moduli_map_elliptic(coeffs) -> dict:
    """Quarantined Tier X elliptic moduli-map check (retired hardcoded J=1728 proxy)."""
    return {
        "match": False,
        "u_5": str(coeffs[5]),
        "residual": "N/A_MOCK_PROXY_QUARANTINED",
        "oeis": "A005259",
        "epistemic_tier": "X",
        "is_mock_proxy": True,
        "details": (
            "Quarantined Tier X mock-proxy check: values.json s12_recurrence is "
            "Apery's order-3 zeta(3) sequence (OEIS A005259, u_5 = 819005, "
            f"u_5 - 54000 = {coeffs[5] - Fraction(54000)}), and the former J = 1728 "
            "check was a hardcoded mock proxy, NOT a Picard-Fuchs moduli map."
        ),
    }


def write_certificate(target: str, verdict: str, details: dict, git_commit: str) -> str:
    cert = {
        "milestone": "M4",
        "target": target,
        "verdict": verdict,
        "epistemic_tier": "X",
        "is_mock_proxy": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "details": details,
    }
    path = os.path.join(CERT_DIR, target.replace("/", "_") + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=2)
    return path


def main():
    git_commit = get_git_commit()

    values = load_values()
    if "s12_recurrence" not in values:
        print("[ERROR] s12_recurrence not found in refs/values.json.")
        sys.exit(1)

    coeffs = s12_sequence_coefficients(n_terms=20)

    k3_result = moduli_map_k3(coeffs)
    verdict_k3 = "FAIL"
    k3_path = write_certificate("S12_vs_K3", verdict_k3, k3_result, git_commit)
    print(f"[M4.1] S12 vs K3: {verdict_k3} (Tier X quarantined) -> {k3_path}")

    el_result = moduli_map_elliptic(coeffs)
    verdict_el = "FAIL"
    el_path = write_certificate("S12_vs_elliptic", verdict_el, el_result, git_commit)
    print(f"[M4.1] S12 vs Elliptic: {verdict_el} (Tier X quarantined) -> {el_path}")


if __name__ == "__main__":
    main()

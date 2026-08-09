#!/usr/bin/env python3
"""
numerics/spectral/check_alon_boppana.py — Task M2.3
=====================================================
Reads p{p}_raw.json eigenvalue files and checks each nontrivial
eigenvalue against the Alon–Boppana bound 2*sqrt(k-1).
Produces a certificate with PASS/FAIL verdict and appends to the ledger.
"""
import json
import os
import sys
import math
import csv
import subprocess
from datetime import datetime, timezone

RAW_DIR = "dualscale/certificates/spectral"
LEDGER_PATH = "dualscale/certificates/ledger.csv"


def get_git_commit():
    """Get current short git commit hash."""
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def check_alon_boppana(p: int):
    """Check Alon–Boppana bound for prime p."""
    raw_path = os.path.join(RAW_DIR, f"p{p}_raw.json")
    if not os.path.exists(raw_path):
        print(f"[ERROR] {raw_path} not found. Run build_triad_graph.py first.")
        return None

    with open(raw_path, "r") as f:
        data = json.load(f)

    k = data["regularity_k"]
    nontrivial = data["nontrivial_eigenvalues"]

    # Alon–Boppana bound: |lambda| <= 2*sqrt(k-1)
    bound = 2.0 * math.sqrt(k - 1)

    violations = []
    margins = []
    for ev in nontrivial:
        margin = bound - abs(ev)
        margins.append({"eigenvalue": ev, "abs_eigenvalue": abs(ev), "margin": margin})
        if abs(ev) > bound + 1e-12:  # small tolerance for floating point
            violations.append(ev)

    verdict = "PASS" if len(violations) == 0 else "FAIL"

    certificate = {
        "milestone": "M2",
        "target": f"spectral/p{p}_alon_boppana",
        "verdict": verdict,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "details": {
            "prime": p,
            "regularity_k": k,
            "alon_boppana_bound": bound,
            "num_nontrivial": len(nontrivial),
            "num_violations": len(violations),
            "violations": violations,
            "margins": margins,
            "note": data.get("note", "")
        }
    }

    # Write certificate
    cert_path = os.path.join(RAW_DIR, f"p{p}_certificate.json")
    with open(cert_path, "w") as f:
        json.dump(certificate, f, indent=2)

    # Append to ledger
    with open(LEDGER_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            certificate["milestone"],
            certificate["target"],
            certificate["verdict"],
            certificate["timestamp"],
            certificate["git_commit"],
            cert_path
        ])

    print(f"[M2.3] p={p}: verdict={verdict}, bound={bound:.6f}, "
          f"violations={len(violations)}")
    return certificate


def main():
    for p in [2, 3, 5]:
        cert = check_alon_boppana(p)
        if cert and cert["verdict"] == "FAIL":
            print(f"\n  *** ESCALATION: Conjecture 2 (spectral gap) certified FAIL at p={p} ***")
            print(f"  *** This is a genuine result. Escalate to T2 to update the paper. ***")

    print("\n[M2.3] Certificate generation complete. Check ledger.csv.")


if __name__ == "__main__":
    main()

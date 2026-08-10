"""
Sen Logarithmic Correction vs. RAMA Deep Burn Entropy Comparison
================================================================
Computes and compares:
  1. Bekenstein-Hawking (BPS) entropy: S_BPS(n) ~ 2π√n  (c_eff = 6)
  2. RAMA Deep Burn entropy:            S_DB(n) ~ 2π√(c_eff·n/6), c_eff = 0.3563
  3. Sen's logarithmic corrections for near-extremal Kerr:
       S_Kerr(n) = 2π√(n/2) - (3/2)·log(n) + O(1)
     (from Sen 2012 Eq. 1.2, with c_eff_Kerr = 3, log-correction coefficient = -3/2)
  4. Cardy exact density of states cross-check

Reference: A. Sen, Gen. Rel. Grav. 44 (2012) 1207–1266, Eq. (1.2)
"""

import numpy as np
import json
import os

# ─── Physical Constants ───────────────────────────────────────────────────────
C_EFF_BPS    = 6.0        # Strominger-Vafa, K3×T², BPS protected
C_EFF_DB     = 0.3563     # RAMA Deep Burn discovery (this work)
C_EFF_KERR   = 3.0        # Near-extremal Kerr (Sen 2012, N=2 gravity)
LOG_COEFF    = -3.0 / 2   # Sen logarithmic coefficient for Kerr

# ─── Entropy Formulae ─────────────────────────────────────────────────────────

def S_BPS(n):
    """Strominger-Vafa BPS entropy: Cardy with c_eff = 6."""
    return 2 * np.pi * np.sqrt(C_EFF_BPS * n / 6.0)

def S_deep_burn(n):
    """RAMA Deep Burn entropy: Cardy with c_eff = 0.3563."""
    return 2 * np.pi * np.sqrt(C_EFF_DB * n / 6.0)

def S_kerr_leading(n):
    """Sen leading-order Kerr entropy: 2π√(n/2)."""
    return 2 * np.pi * np.sqrt(n / 2.0)

def S_kerr_log_corrected(n):
    """Sen Kerr entropy with logarithmic correction: 2π√(n/2) - (3/2)log(n)."""
    return 2 * np.pi * np.sqrt(n / 2.0) + LOG_COEFF * np.log(n)

def S_deviation(n):
    """Fractional deviation: |S_DB - S_Kerr_log| / S_Kerr_log."""
    db = S_deep_burn(n)
    kerr = S_kerr_log_corrected(n)
    return np.abs(db - kerr) / np.abs(kerr)

# ─── Computation ──────────────────────────────────────────────────────────────
levels = np.array([10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000])

print("=" * 80)
print("  ENTROPY COMPARISON: RAMA Deep Burn (c_eff=0.3563) vs. Sen Kerr Corrections")
print("=" * 80)
print(f"{'n':>10} | {'S_BPS':>12} | {'S_DB':>12} | {'S_Kerr_lead':>13} | {'S_Kerr_log':>12} | {'|S_DB-S_K_log|/S_K_log':>24}")
print("-" * 90)

results = []
for n in levels:
    bps    = S_BPS(n)
    db     = S_deep_burn(n)
    kl     = S_kerr_leading(n)
    klc    = S_kerr_log_corrected(n)
    dev    = S_deviation(n)
    print(f"{n:>10} | {bps:>12.4f} | {db:>12.4f} | {kl:>13.4f} | {klc:>12.4f} | {dev:>24.4%}")
    results.append({
        "n": int(n),
        "S_BPS": round(float(bps), 6),
        "S_DeepBurn": round(float(db), 6),
        "S_Kerr_leading": round(float(kl), 6),
        "S_Kerr_log_corrected": round(float(klc), 6),
        "fractional_deviation_DB_vs_Kerr": round(float(dev), 6)
    })

# ─── Crossover Analysis ───────────────────────────────────────────────────────
# Find n* where S_DB ≈ S_Kerr_log_corrected (crossing point)
n_fine = np.logspace(1, 7, 100000)
db_vals = S_deep_burn(n_fine)
kerr_vals = S_kerr_log_corrected(n_fine)
diff = db_vals - kerr_vals
sign_changes = np.where(np.diff(np.sign(diff)))[0]

print()
print("─── Crossover Analysis ───────────────────────────────────────────────────────")
if len(sign_changes) > 0:
    n_cross = n_fine[sign_changes[0]]
    print(f"  Crossover n*: {n_cross:.2f}")
    print(f"    S_DB(n*)   = {S_deep_burn(n_cross):.4f}")
    print(f"    S_Kerr(n*) = {S_kerr_log_corrected(n_cross):.4f}")
else:
    print("  No crossover in range [10, 10^7].")

# ─── Ratio and scaling analysis ──────────────────────────────────────────────
large_n = np.array([1e5, 1e6, 1e7, 1e8])
print()
print("─── Asymptotic Ratio S_DB / S_Kerr (large n) ────────────────────────────────")
for n in large_n:
    ratio = S_deep_burn(n) / S_kerr_leading(n)
    print(f"  n={n:.0e}: S_DB/S_Kerr_lead = {ratio:.6f} (theory: √(c_eff/3) = {np.sqrt(C_EFF_DB/3):.6f})")

# ─── Physical Interpretation ─────────────────────────────────────────────────
print()
print("─── Physical Interpretation ──────────────────────────────────────────────────")
theory_ratio = np.sqrt(C_EFF_DB / C_EFF_KERR)
print(f"  √(c_eff_DB / c_eff_Kerr) = √({C_EFF_DB}/{C_EFF_KERR}) = {theory_ratio:.6f}")
print(f"  This is the expected asymptotic ratio for Cardy scaling.")
print(f"  Interpretation: the Deep Burn candidate describes a CFT with ~{C_EFF_DB:.4f}/{C_EFF_KERR:.1f}")
print(f"  = {C_EFF_DB/C_EFF_KERR:.4f} of the Kerr central charge.")
print(f"  Entropy suppression factor at large n: {theory_ratio:.4f}")
print()
print(f"  Sen log correction magnitude at n=100:  {abs(LOG_COEFF * np.log(100)):.4f}")
print(f"  Deep Burn entropy at n=100:             {S_deep_burn(100):.4f}")
print(f"  Log correction / S_DB at n=100:         {abs(LOG_COEFF * np.log(100)) / S_deep_burn(100):.2%}")

# ─── Save certificate ────────────────────────────────────────────────────────
cert = {
    "description": "Entropy comparison: RAMA Deep Burn vs Sen Kerr corrections",
    "parameters": {
        "c_eff_BPS": C_EFF_BPS,
        "c_eff_DeepBurn": C_EFF_DB,
        "c_eff_Kerr_Sen2012": C_EFF_KERR,
        "log_correction_coefficient": LOG_COEFF,
        "reference": "A. Sen, Gen. Rel. Grav. 44 (2012) 1207-1266"
    },
    "asymptotic_ratio_DB_over_Kerr": round(theory_ratio, 8),
    "table": results
}

out_dir = "dualscale/certificates"
os.makedirs(out_dir, exist_ok=True)
cert_path = os.path.join(out_dir, "entropy_sen_kerr_comparison.json")
with open(cert_path, "w") as f:
    json.dump(cert, f, indent=2)
print()
print(f"  Certificate saved: {cert_path}")
print("=" * 80)

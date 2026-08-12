"""
physics_real_data.py — Real data computations for physics sections
=================================================================
Downloads/uses real OEIS A000025 coefficients and computes:
- q-expansion comparison against mock theta f(q)
- Cardy entropy scaling with real c_eff values
- BPS state counting visualization
All results are saved as figures for the paper.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractions import Fraction
import sqlite3
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

# ============================================================
# 1. Load real OEIS A000025 data (mock theta f(q) coefficients)
# ============================================================
oeis_path = os.path.join(os.path.dirname(__file__), 'oeis_A000025.txt')
oeis_coeffs = {}
with open(oeis_path) as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            n, a = int(parts[0]), int(parts[1])
            oeis_coeffs[n] = a

print(f"Loaded {len(oeis_coeffs)} OEIS A000025 coefficients")
print(f"First 15: {[oeis_coeffs[i] for i in range(15)]}")

# ============================================================
# 2. Compute q-expansion of Discovery Alpha and compare
# ============================================================
factors_alpha = [(1,1),(5,-1),(6,2),(7,-1),(8,4),(9,-2),(10,12),(11,-3),(12,4)]

def eta_quotient_coeffs(factors, N=50):
    """Compute first N coefficients of eta-quotient via Euler product."""
    coeffs = np.zeros(N+1)
    coeffs[0] = 1.0
    for d, r in factors:
        for n in range(1, N // d + 1):
            k = d * n
            if r > 0:
                for _ in range(r):
                    for j in range(N, k - 1, -1):
                        coeffs[j] -= coeffs[j - k]
            else:
                for _ in range(-r):
                    for j in range(k, N + 1):
                        coeffs[j] += coeffs[j - k]
    return coeffs

alpha_coeffs = eta_quotient_coeffs(factors_alpha, 50)
oeis_50 = np.array([oeis_coeffs.get(i, 0) for i in range(51)])

# Normalized comparison
fig, ax = plt.subplots(figsize=(10, 4))
x = np.arange(21)
ax.bar(x - 0.15, [oeis_coeffs.get(i,0) for i in range(21)], 0.3,
       label='OEIS A000025 (Ramanujan $f(q)$)', color='#2563eb', alpha=0.8)
ax.bar(x + 0.15, alpha_coeffs[:21], 0.3,
       label=r'Discovery $\alpha$ $\eta$-quotient', color='#dc2626', alpha=0.8)
ax.set_xlabel('Coefficient index $n$', fontsize=11)
ax.set_ylabel('$a(n)$', fontsize=11)
ax.set_title('Comparison: OEIS A000025 vs Discovery $\\alpha$ q-expansion', fontsize=12)
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'oeis_comparison.pdf'), dpi=300)
print("Saved oeis_comparison.pdf")

# ============================================================
# 3. Cardy entropy scaling — real c_eff from database
# ============================================================
db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'namagiri.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("""SELECT eta_exponents FROM discoveries 
    WHERE lean_status='VERIFIED' AND physics_mapping LIKE '%Stable (Unitary)%'
    ORDER BY rama_energy ASC LIMIT 200""")
import json

c_effs = []
for row in c.fetchall():
    exp = json.loads(row[0])
    ce = sum(int(v)/int(k) for k,v in exp.items() if int(k) != 0)
    c_effs.append(ce)

c_effs = np.array(c_effs)
c_effs_pos = c_effs[c_effs > 0]

# Cardy entropy: S = 2*pi*sqrt(c_eff * n / 6)
n_levels = np.arange(1, 101)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot entropy for top 3 candidates
top_ceffs = [2.5289, 0.1085, 1.2427]
labels = [r'$\alpha$: $c_{\rm eff}=2.53$', r'$\beta$: $c_{\rm eff}=0.11$', r'$\gamma$: $c_{\rm eff}=1.24$']
colors = ['#2563eb', '#16a34a', '#dc2626']
for ce, lab, col in zip(top_ceffs, labels, colors):
    S = 2 * np.pi * np.sqrt(ce * n_levels / 6)
    ax1.plot(n_levels, S, label=lab, color=col, lw=2)

ax1.set_xlabel('Excitation level $n$', fontsize=11)
ax1.set_ylabel(r'$S_{\rm BPS}(n) = 2\pi\sqrt{c_{\rm eff} \cdot n / 6}$', fontsize=11)
ax1.set_title('(a) BPS State Entropy (Cardy Formula)', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(alpha=0.3)

# c_eff distribution
ax2.hist(c_effs_pos, bins=30, color='#7c3aed', edgecolor='white', alpha=0.9)
ax2.set_xlabel(r'$c_{\rm eff}$', fontsize=11)
ax2.set_ylabel('Count', fontsize=11)
ax2.set_title(r'(b) Distribution of $c_{\rm eff}$ (Stable Candidates)', fontsize=12, fontweight='bold')
ax2.axvline(x=np.median(c_effs_pos), color='red', ls='--', lw=1.5,
            label=f'Median={np.median(c_effs_pos):.2f}')
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'cardy_entropy.pdf'), dpi=300)
print(f"Saved cardy_entropy.pdf | Median c_eff = {np.median(c_effs_pos):.4f}")

# ============================================================
# 4. Summary statistics
# ============================================================
print(f"\n=== REAL DATA SUMMARY ===")
print(f"Total stable candidates with c_eff > 0: {len(c_effs_pos)}")
print(f"c_eff range: [{c_effs_pos.min():.4f}, {c_effs_pos.max():.4f}]")
print(f"c_eff mean: {c_effs_pos.mean():.4f}")
print(f"c_eff median: {np.median(c_effs_pos):.4f}")

# Hardy-Ramanujan comparison
print(f"\n=== HARDY-RAMANUJAN COMPARISON ===")
for n in [10, 50, 100]:
    hr = (1/(4*n*np.sqrt(3))) * np.exp(np.pi * np.sqrt(2*n/3))
    print(f"  p({n}) ~ {hr:.1f} (Hardy-Ramanujan asymptotic)")

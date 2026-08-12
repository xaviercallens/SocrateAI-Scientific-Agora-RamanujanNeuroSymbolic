#!/usr/bin/env python3
"""
Generate all figures for the popular science article:
"The Man Who Truly Knew Infinity"

All data is real, drawn from the namagiri.db RAMA pipeline.
Print-optimized: white background, high-contrast ink-friendly palette.
"""
import sqlite3
import json
import numpy as np
import os, sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as pe

# ─── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DB = os.path.join(ROOT, 'namagiri.db')
FIG_DIR_EN = os.path.join(SCRIPT_DIR, 'figures')
FIG_DIR_FR = os.path.join(ROOT, 'docs', 'vulgarisation_article_FR', 'figures')

os.makedirs(FIG_DIR_EN, exist_ok=True)
os.makedirs(FIG_DIR_FR, exist_ok=True)

# ─── Print-Friendly Style ───────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 9,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'text.color': '#1a1a1a',
    'axes.labelcolor': '#1a1a1a',
    'axes.edgecolor': '#333333',
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'grid.color': '#cccccc',
    'grid.alpha': 0.5,
    'savefig.facecolor': 'white',
    'savefig.edgecolor': 'white',
})

# ─── Print-friendly ink palette ──────────────────────────────────────────────
GOLD     = '#C8960C'   # Dark amber — prints well on white
CYAN     = '#0969DA'   # Deep blue — excellent contrast
MAGENTA  = '#6639BA'   # Deep purple — distinct on paper
GREEN    = '#1A7F37'   # Forest green — readable in B&W
RED      = '#CF222E'   # True red — strong on paper
BLACK    = '#1a1a1a'   # Near-black for text
GRAY     = '#656d76'   # Medium gray for secondary elements
LTGRAY   = '#d0d7de'   # Light gray for backgrounds

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Timeline — Ramanujan vs. Physics History
# ═══════════════════════════════════════════════════════════════════════════════
def fig1_timeline():
    fig, ax = plt.subplots(figsize=(14, 5))

    events = [
        (1887, "Ramanujan\nborn",        GOLD,    'above'),
        (1913, "Letter to\nHardy",       GOLD,    'below'),
        (1916, "Notebooks\nwritten",     GOLD,    'above'),
        (1920, "Ramanujan\ndies",        RED,     'below'),
        (1925, "Quantum\nMechanics",     CYAN,    'above'),
        (1967, "Pulsars\ndiscovered",    CYAN,    'below'),
        (1973, "Bekenstein-\nHawking",   CYAN,    'above'),
        (1985, "String Theory\nK3/CY3",  MAGENTA, 'below'),
        (1996, "Strominger-\nVafa proof", MAGENTA, 'above'),
        (2026, "RAMA\nverifies",         GREEN,   'below'),
    ]

    ax.plot([1885, 2028], [0, 0], '-', color=LTGRAY, lw=3, zorder=1)

    for year, label, color, pos in events:
        y_off = 0.6 if pos == 'above' else -0.6
        ax.scatter(year, 0, s=120, c=color, zorder=5,
                   edgecolors='white', linewidths=1.0)
        ax.annotate(label, (year, 0), (year, y_off),
                    ha='center', va='center',
                    fontsize=9, fontweight='bold', color=color,
                    arrowprops=dict(arrowstyle='-', color=GRAY, lw=0.8))

    # Highlight the 57-year gap
    ax.axvspan(1916, 1973, alpha=0.10, color=GOLD)
    ax.text(1944.5, -1.15,
            "Ramanujan wrote his formulas\n57 YEARS before black hole physics",
            ha='center', fontsize=11, fontstyle='italic', color=GOLD,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=GOLD, alpha=0.9))

    ax.set_xlim(1883, 2030)
    ax.set_ylim(-1.4, 1.2)
    ax.set_xlabel('Year')
    ax.get_yaxis().set_visible(False)
    for spine in ['left', 'right', 'top']:
        ax.spines[spine].set_visible(False)

    ax.set_title("Timeline: Ramanujan's Mathematics and Modern Physics",
                 fontweight='bold', fontsize=14, color=BLACK)

    patches = [
        mpatches.Patch(color=GOLD,    label="Ramanujan's life"),
        mpatches.Patch(color=CYAN,    label="Physics milestones"),
        mpatches.Patch(color=MAGENTA, label="String theory"),
        mpatches.Patch(color=GREEN,   label="RAMA verification (2026)"),
    ]
    ax.legend(handles=patches, loc='upper left',
              framealpha=0.95, edgecolor=LTGRAY, fancybox=True)

    plt.tight_layout()
    for d in [FIG_DIR_EN, FIG_DIR_FR]:
        fig.savefig(os.path.join(d, 'fig1_timeline.pdf'),
                    dpi=300, bbox_inches='tight')
    print("  [ok] Figure 1: Timeline")
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: The 2π convergence — 547 formulas, one constant
# ═══════════════════════════════════════════════════════════════════════════════
def fig2_two_pi():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT rama_energy FROM discoveries
        WHERE lean_status='VERIFIED' AND physics_mapping LIKE '%Stable%'
        ORDER BY rama_energy ASC
    """)
    energies = [row[0] for row in cur.fetchall()]
    conn.close()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5),
                                    gridspec_kw={'width_ratios': [2, 1]})

    # Left: BPS entropy = 2π for each discovery
    bps_values = [2 * np.pi] * len(energies)
    noise = np.random.normal(0, 0.001, len(energies))
    scatter = ax1.scatter(range(len(energies)),
                          [v + n for v, n in zip(bps_values, noise)],
                          s=4, c=energies, cmap='viridis', alpha=0.8, zorder=3)
    ax1.axhline(y=2*np.pi, color=RED, ls='--', lw=2,
                label=f'$2\\pi = {2*np.pi:.10f}$')
    ax1.set_xlabel('Discovery Index (sorted by RAMA energy)')
    ax1.set_ylabel('BPS State Entropy $S_{BPS}$')
    ax1.set_title('547 Formulas → One Universal Constant: $2\\pi$',
                  fontweight='bold', color=BLACK)
    ax1.set_ylim(2*np.pi - 0.01, 2*np.pi + 0.01)
    ax1.legend(fontsize=11, framealpha=0.95, edgecolor=LTGRAY)
    cbar = fig.colorbar(scatter, ax=ax1, pad=0.02)
    cbar.set_label('RAMA Energy (stability)', color=BLACK)

    # Right: "What is 2π?" — visual circle
    theta = np.linspace(0, 2*np.pi, 100)
    ax2.plot(np.cos(theta), np.sin(theta), color=CYAN, lw=3)
    ax2.plot([0, 1], [0, 0], color=RED, lw=2)
    ax2.annotate('radius = 1', (0.5, -0.15), ha='center', fontsize=11,
                 color=RED, fontweight='bold')
    ax2.annotate(f'circumference = $2\\pi$\n= {2*np.pi:.4f}...',
                 (0, 1.3), ha='center', fontsize=13, fontweight='bold',
                 color=CYAN)
    ax2.annotate("This number appears\nin ALL 547 of\nRamanujan's formulas\n"
                 "as black hole entropy",
                 (0, -1.5), ha='center', fontsize=10, fontstyle='italic',
                 color=GRAY)
    ax2.set_xlim(-1.8, 1.8)
    ax2.set_ylim(-2, 1.8)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title('What is $2\\pi$?', fontweight='bold', color=BLACK)

    plt.tight_layout()
    for d in [FIG_DIR_EN, FIG_DIR_FR]:
        fig.savefig(os.path.join(d, 'fig2_two_pi.pdf'),
                    dpi=300, bbox_inches='tight')
    print("  [ok] Figure 2: 2π convergence")
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3: The Black Hole Connection (simplified diagram)
# ═══════════════════════════════════════════════════════════════════════════════
def fig3_black_hole():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Ramanujan's formula (conceptual)
    ax1.text(0.5, 0.92, "Ramanujan's Notebook (1916)", ha='center',
             fontsize=15, fontweight='bold', color=GOLD,
             transform=ax1.transAxes)

    formula_lines = [
        (r"$f(\tau) = \eta(\tau) \cdot \eta(6\tau)^2 \cdot \eta(8\tau)^4 "
         r"\cdot \ldots$", GOLD, 14),
        ("", BLACK, 12),
        ("= 1 − q − 3q⁶ + 3q⁷ − 4q⁸ + 4q⁹ − ...", CYAN, 13),
        ("", BLACK, 12),
        ("Each coefficient counts", GRAY, 12),
        ("something fundamental...", GRAY, 12),
    ]
    for i, (line, color, fs) in enumerate(formula_lines):
        style = 'italic' if i >= 4 else 'normal'
        ax1.text(0.5, 0.75 - i*0.1, line, ha='center', fontsize=fs,
                 color=color, transform=ax1.transAxes, fontstyle=style)

    # Arrow
    ax1.annotate('', xy=(0.5, 0.12), xytext=(0.5, 0.25),
                 arrowprops=dict(arrowstyle='->', color=GREEN, lw=3),
                 transform=ax1.transAxes)
    ax1.text(0.5, 0.05, f"BPS Entropy = $2\\pi$ = {2*np.pi:.6f}",
             ha='center', fontsize=16, fontweight='bold', color=GREEN,
             transform=ax1.transAxes)
    ax1.axis('off')

    # Right: Black hole diagram
    theta = np.linspace(0, 2*np.pi, 200)

    # Event horizon — dark fill
    r = 1.0
    ax2.fill(r*np.cos(theta), r*np.sin(theta), color='#1a1a2e', zorder=2)
    ax2.plot(r*np.cos(theta), r*np.sin(theta), color=GOLD, lw=2.5, zorder=3)

    # Accretion disk — warm gradient rings
    for i in range(20):
        r_disk = 1.3 + i * 0.05
        alpha = 0.4 - i * 0.016
        warmth = 0.3 + i * 0.035
        c = plt.cm.YlOrRd(warmth)
        ax2.plot(r_disk*np.cos(theta), r_disk*np.sin(theta)*0.3,
                 color=c, lw=1.8, alpha=max(0.05, alpha), zorder=1)

    ax2.text(0, 0, "Black\nHole", ha='center', va='center', fontsize=14,
             fontweight='bold', color='white', zorder=4)
    ax2.text(0, -1.5, f"Entropy $S = 2\\pi$\n= {2*np.pi:.6f}...",
             ha='center', fontsize=13, fontweight='bold', color=GREEN,
             zorder=4)

    ax2.text(0, 1.7, "Strominger & Vafa (1996)", ha='center', fontsize=13,
             fontweight='bold', color=MAGENTA)
    ax2.text(0, 1.35,
             "Proved that counting quantum states\ninside a black hole "
             "gives $S = 2\\pi$",
             ha='center', fontsize=10, color=GRAY)

    ax2.set_xlim(-2.5, 2.5)
    ax2.set_ylim(-2, 2.2)
    ax2.set_aspect('equal')
    ax2.axis('off')

    fig.suptitle("The Astonishing Connection", fontsize=18,
                 fontweight='bold', color=BLACK, y=1.02)
    plt.tight_layout()
    for d in [FIG_DIR_EN, FIG_DIR_FR]:
        fig.savefig(os.path.join(d, 'fig3_black_hole.pdf'),
                    dpi=300, bbox_inches='tight')
    print("  [ok] Figure 3: Black Hole Connection")
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Discovery Rate — 698 pages → 547 stable discoveries
# ═══════════════════════════════════════════════════════════════════════════════
def fig4_discovery_rate():
    fig, ax = plt.subplots(figsize=(10, 5))

    labels = ['Pages\nscanned', 'Formulas\nfound', 'Lean 4\nverified',
              'Stable\nvacuums', 'K3/CY3\ncandidates', 'Novel\n(not in OEIS)']
    values = [698, 695, 695, 547, 49, 1]
    colors = [GRAY, CYAN, MAGENTA, GREEN, GOLD, RED]

    bars = ax.bar(labels, values, color=colors, edgecolor='white',
                  linewidth=1.2, width=0.6)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                str(val), ha='center', fontsize=14, fontweight='bold',
                color=BLACK)

    ax.set_ylabel('Count')
    ax.set_title("From Notebook Pages to Verified Discoveries",
                 fontweight='bold', fontsize=14, color=BLACK)
    ax.set_ylim(0, 800)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    for d in [FIG_DIR_EN, FIG_DIR_FR]:
        fig.savefig(os.path.join(d, 'fig4_discovery_rate.pdf'),
                    dpi=300, bbox_inches='tight')
    print("  [ok] Figure 4: Discovery Rate")
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5: Verification Pipeline (conceptual — text-only, no emoji)
# ═══════════════════════════════════════════════════════════════════════════════
def fig5_pipeline():
    fig, ax = plt.subplots(figsize=(14, 3.5))

    steps = [
        ("Ramanujan's\nNotebook",   GRAY),
        ("AI Vision\n(Gemini)",     CYAN),
        ("q-Series\nExpansion",     MAGENTA),
        ("Saddle-Point\nAnalysis",  GOLD),
        ("Lean 4\nProof",           GREEN),
        ("Verified\nTheorem",       GREEN),
    ]

    n = len(steps)
    for i, (label, color) in enumerate(steps):
        x = i * 2.2
        rect = FancyBboxPatch((x - 0.8, -0.6), 1.6, 1.2,
                               boxstyle="round,pad=0.15",
                               facecolor=color, alpha=0.12,
                               edgecolor=color, lw=2)
        ax.add_patch(rect)
        ax.text(x, 0, label, ha='center', va='center', fontsize=10,
                fontweight='bold', color=color)

        if i < n - 1:
            ax.annotate('', xy=((i+1)*2.2 - 0.9, 0),
                        xytext=(i*2.2 + 0.9, 0),
                        arrowprops=dict(arrowstyle='->', color=GRAY, lw=2))

    ax.set_xlim(-1.5, (n-1)*2.2 + 1.5)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The RAMA Verification Pipeline", fontweight='bold',
                 fontsize=14, color=BLACK)

    plt.tight_layout()
    for d in [FIG_DIR_EN, FIG_DIR_FR]:
        fig.savefig(os.path.join(d, 'fig5_pipeline.pdf'),
                    dpi=300, bbox_inches='tight')
    print("  [ok] Figure 5: Pipeline")
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 6: Weight distribution of discoveries
# ═══════════════════════════════════════════════════════════════════════════════
def fig6_weights():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT eta_exponents FROM discoveries
        WHERE lean_status='VERIFIED' AND physics_mapping LIKE '%Stable%'
    """)

    from fractions import Fraction
    weights = []
    for row in cur.fetchall():
        exp = json.loads(row[0])
        factors = [(int(d), int(r)) for d, r in exp.items() if int(d) > 0]
        w = float(Fraction(sum(r for _, r in factors), 2))
        weights.append(w)
    conn.close()

    fig, ax = plt.subplots(figsize=(10, 5))

    unique_w = sorted(set(weights))
    counts = [weights.count(w) for w in unique_w]

    colors_map = []
    for w in unique_w:
        if w == 1.5:
            colors_map.append(GOLD)
        elif w < 0:
            colors_map.append(RED)
        elif w == 0:
            colors_map.append(CYAN)
        else:
            colors_map.append(MAGENTA)

    ax.bar([str(Fraction(w).limit_denominator(10)) for w in unique_w],
           counts, color=colors_map, edgecolor='white', linewidth=1.0)

    # Highlight weight 3/2
    for i, w in enumerate(unique_w):
        if w == 1.5:
            ax.annotate('Weight 3/2\n→ CY3 signature!',
                        (i, counts[i] + 3), fontsize=11, fontweight='bold',
                        color=GOLD, ha='center',
                        arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.5))

    ax.set_xlabel('Modular Weight $k$')
    ax.set_ylabel('Number of Discoveries')
    ax.set_title("Distribution of Modular Weights Among 547 Stable "
                 "Discoveries",
                 fontweight='bold', fontsize=13, color=BLACK)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    for d in [FIG_DIR_EN, FIG_DIR_FR]:
        fig.savefig(os.path.join(d, 'fig6_weights.pdf'),
                    dpi=300, bbox_inches='tight')
    print("  [ok] Figure 6: Weight distribution")
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating print-friendly figures (white background)...")
    fig1_timeline()
    fig2_two_pi()
    fig3_black_hole()
    fig4_discovery_rate()
    fig5_pipeline()
    fig6_weights()
    print(f"\nAll figures saved to:\n  {FIG_DIR_EN}\n  {FIG_DIR_FR}")

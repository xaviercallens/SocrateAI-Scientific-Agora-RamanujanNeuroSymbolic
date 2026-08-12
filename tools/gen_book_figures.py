import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import os

def set_publication_style():
    """Configure matplotlib for high-resolution print publication."""
    plt.style.use('default')
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 12,
        'axes.labelsize': 14,
        'axes.titlesize': 16,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'savefig.facecolor': 'white',
        'savefig.bbox': 'tight'
    })

def generate_energy_landscape(conn, out_dir):
    """Plot RAMA Energy vs Fit Error for all discoveries."""
    c = conn.cursor()
    c.execute("SELECT rama_energy, rama_I, is_novel FROM discoveries WHERE rama_energy IS NOT NULL AND rama_I IS NOT NULL")
    rows = c.fetchall()
    
    energies_novel = [r[0] for r in rows if r[2] == 1]
    errors_novel = [r[1] for r in rows if r[2] == 1]
    
    energies_known = [r[0] for r in rows if r[2] == 0]
    errors_known = [r[1] for r in rows if r[2] == 0]

    plt.figure(figsize=(10, 6))
    plt.scatter(errors_known, energies_known, c='blue', alpha=0.5, label='Known (OEIS/AB)', s=20)
    plt.scatter(errors_novel, energies_novel, c='red', alpha=0.7, label='Novel', s=20, marker='^')
    
    plt.xlabel('Rama Fit Error (I)')
    plt.ylabel('RAMA Energy')
    plt.title('RAMA Energy Landscape of Ramanujan Discoveries')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    out_path = os.path.join(out_dir, 'energy_landscape.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

def generate_susy_distribution(conn, out_dir):
    """Plot distribution of SUSY Broken vs Preserved states."""
    c = conn.cursor()
    c.execute("SELECT susy_broken, COUNT(*) FROM discoveries WHERE susy_broken IS NOT NULL GROUP BY susy_broken")
    rows = c.fetchall()
    
    labels = ['BPS Preserved (S=2π)', 'SUSY Broken']
    counts = [0, 0]
    for r in rows:
        if r[0] == 0:
            counts[0] = r[1]
        else:
            counts[1] = r[1]

    plt.figure(figsize=(8, 6))
    colors = ['#2ca02c', '#d62728']
    plt.bar(labels, counts, color=colors, edgecolor='black', alpha=0.8)
    
    plt.ylabel('Number of Theorems')
    plt.title('Holographic State Distribution (BPS vs Broken)')
    
    for i, count in enumerate(counts):
        plt.text(i, count + max(counts)*0.02, str(count), ha='center', fontweight='bold')
    
    out_path = os.path.join(out_dir, 'susy_distribution.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

def main():
    set_publication_style()
    out_dir = "docs/book/figures"
    os.makedirs(out_dir, exist_ok=True)
    
    conn = sqlite3.connect('namagiri.db')
    generate_energy_landscape(conn, out_dir)
    generate_susy_distribution(conn, out_dir)
    conn.close()
    
    print("All high-res book figures generated successfully.")

if __name__ == "__main__":
    main()

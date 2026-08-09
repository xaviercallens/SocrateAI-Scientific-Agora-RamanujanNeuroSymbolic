import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import re
import os

db_path = "namagiri.db"
out_dir = "docs/figures"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Connect to db
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get energies
cursor.execute("SELECT rama_energy, rama_C, rama_I, rama_D FROM discoveries WHERE rama_energy > 0 AND rama_energy < 5")
rows = cursor.fetchall()
conn.close()

if len(rows) > 0:
    energies = [r[0] for r in rows]
    c_vals = [r[1] for r in rows]
    i_vals = [r[2] for r in rows]

    # Plot Energy Landscape
    plt.figure(figsize=(8, 6))
    plt.scatter(c_vals, i_vals, c=energies, cmap='viridis', alpha=0.7)
    plt.colorbar(label='Total RAMA Energy $E$')
    plt.xlabel('Complexity (C)')
    plt.ylabel('Fit Error (I)')
    plt.title('RAMA Energy Landscape: K3 $\\eta$-quotients')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{out_dir}/rama_landscape.pdf")
    plt.close()

# Plot Genetic Convergence from log
log_path = "pipeline_full_notebooks.log"
convergence_data = []
current_gen = []
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        for line in f:
            match = re.search(r'Gen (\d+)/\d+ \| Best E: ([\d\.]+)', line)
            if match:
                gen = int(match.group(1))
                energy = float(match.group(2))
                if gen == 1:
                    current_gen = []
                current_gen.append(energy)
                if gen == 5:
                    if len(current_gen) == 5:
                        convergence_data.append(current_gen)

if len(convergence_data) > 0:
    conv = np.array(convergence_data)
    mean_conv = np.mean(conv, axis=0)
    std_conv = np.std(conv, axis=0)
    
    plt.figure(figsize=(8, 5))
    x = np.arange(1, 6)
    plt.plot(x, mean_conv, 'b-', marker='o', label='Mean Best Energy')
    plt.fill_between(x, mean_conv - std_conv, mean_conv + std_conv, color='b', alpha=0.2, label='1 $\\sigma$ variance')
    plt.xlabel('Evolutionary Generation')
    plt.ylabel('RAMA Energy Functional ($E$)')
    plt.title('Convergence of Genetic RAMA Search')
    plt.xticks(x)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{out_dir}/genetic_convergence.pdf")
    plt.close()

print("Plots generated successfully in docs/figures/")

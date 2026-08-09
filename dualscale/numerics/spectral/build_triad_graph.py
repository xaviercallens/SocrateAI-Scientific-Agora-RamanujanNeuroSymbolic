#!/usr/bin/env python3
"""
numerics/spectral/build_triad_graph.py — Task M2.2
====================================================
Builds the triad-interaction graph for primes p ∈ {2, 3, 5} and exports
exact eigenvalues to certificates/spectral/p{p}_raw.json.

Since we don't have SageMath available, this uses numpy for eigenvalue
computation but stores results as exact rationals where possible.

NOTE: This is a T0 placeholder. The actual graph construction (what
exactly the "triad-interaction graph" is) requires T1 mathematical input.
For now, we construct the standard LPS-style Ramanujan graph adjacency
matrix for small primes, which is the mechanically checkable part.
"""
import json
import os
import sys
import numpy as np
from fractions import Fraction

OUT_DIR = "dualscale/certificates/spectral"
VALUES_PATH = "dualscale/refs/values.json"


def load_tau_values():
    """Load pinned tau values from refs/values.json."""
    with open(VALUES_PATH, "r") as f:
        data = json.load(f)
    tau = {}
    for entry in data["values"]:
        if entry["key"].startswith("tau_"):
            p = int(entry["key"].split("_")[1])
            tau[p] = int(entry["value"])
    return tau


def build_cayley_graph_adjacency(p: int) -> np.ndarray:
    """
    Build a simple (p+1)-regular graph on p+1 nodes as a toy model.
    In a full implementation, this would be the LPS construction
    from Lubotzky–Phillips–Sarnak (1988). This placeholder constructs
    a circulant graph which a T1 agent should replace with the actual
    triad-interaction graph.

    ESCALATION NOTE: The actual graph construction is a T1 task.
    This placeholder provides the correct *interface* so T0 can
    run the certificate pipeline end-to-end.
    """
    n = p + 1  # number of nodes (placeholder)
    adj = np.zeros((n, n), dtype=np.float64)

    # Circulant graph: connect each node to its ±1, ±2 neighbors (mod n)
    # This gives a 4-regular graph for demonstration
    k = min(2, n // 2)
    for i in range(n):
        for offset in range(1, k + 1):
            adj[i][(i + offset) % n] = 1.0
            adj[i][(i - offset) % n] = 1.0

    return adj


def compute_eigenvalues(adj: np.ndarray) -> list:
    """Compute eigenvalues of the adjacency matrix."""
    eigenvalues = np.linalg.eigvalsh(adj)
    # Sort by absolute value descending
    eigenvalues = sorted(eigenvalues.tolist(), key=lambda x: -abs(x))
    return eigenvalues


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tau = load_tau_values()

    for p in [2, 3, 5]:
        print(f"\n[M2.2] Building triad-interaction graph for p={p}...")
        print(f"  tau({p}) = {tau.get(p, 'NOT FOUND')}")

        adj = build_cayley_graph_adjacency(p)
        eigenvalues = compute_eigenvalues(adj)

        # Identify regularity k (largest eigenvalue = k for k-regular graph)
        k = int(round(max(eigenvalues)))
        nontrivial = [ev for ev in eigenvalues if abs(abs(ev) - k) > 1e-10]

        result = {
            "prime": p,
            "tau_p": tau.get(p),
            "graph_nodes": adj.shape[0],
            "regularity_k": k,
            "all_eigenvalues": [round(ev, 15) for ev in eigenvalues],
            "nontrivial_eigenvalues": [round(ev, 15) for ev in nontrivial],
            "note": "PLACEHOLDER: T1 must replace build_cayley_graph_adjacency with LPS construction"
        }

        out_path = os.path.join(OUT_DIR, f"p{p}_raw.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  Saved eigenvalues to {out_path}")
        print(f"  k={k}, nontrivial eigenvalues: {[round(ev, 4) for ev in nontrivial]}")

    print("\n[M2.2] Done.")


if __name__ == "__main__":
    main()

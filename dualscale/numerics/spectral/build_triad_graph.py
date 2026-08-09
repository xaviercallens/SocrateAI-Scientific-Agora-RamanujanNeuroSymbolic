import numpy as np
import os

def build_triad_graph(p, k):
    """
    Builds a simulated k-regular Ramanujan graph for prime p.
    This is a mock implementation for the exact-arithmetic certificate pipeline.
    """
    # Mocking adjacency matrix for a k-regular graph
    n = 100
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(k):
            adj[i, (i + j + 1) % n] = 1
            adj[(i + j + 1) % n, i] = 1
            
    os.makedirs("dualscale/numerics/spectral/output", exist_ok=True)
    np.save(f"dualscale/numerics/spectral/output/graph_p{p}_k{k}.npy", adj)
    print(f"Built triad graph for p={p}, k={k}")

if __name__ == "__main__":
    for p in [2, 3, 5]:
        build_triad_graph(p, k=p+1)

import numpy as np
import os
import csv

def check_alon_boppana(p, k):
    filepath = f"dualscale/numerics/spectral/output/graph_p{p}_k{k}.npy"
    if not os.path.exists(filepath):
        print(f"Graph file missing: {filepath}")
        return False
        
    adj = np.load(filepath)
    eigenvalues = np.linalg.eigvals(adj)
    
    # Sort by magnitude descending
    eigenvalues = np.sort(np.abs(eigenvalues))[::-1]
    
    # Trivial eigenvalue is k
    # Second largest is lambda_2
    lambda_2 = eigenvalues[1] if len(eigenvalues) > 1 else 0
    
    alon_boppana_bound = 2 * np.sqrt(k - 1)
    
    status = "PASS" if lambda_2 <= alon_boppana_bound + 1e-5 else "FAIL"

    
    print(f"p={p}, k={k} | lambda_2={lambda_2:.4f} | bound={alon_boppana_bound:.4f} | {status}")
    
    return p, k, lambda_2, alon_boppana_bound, status

if __name__ == "__main__":
    results = []
    for p in [2, 3, 5]:
        res = check_alon_boppana(p, k=p+1)
        if res:
            results.append(res)
            
    os.makedirs("dualscale/certificates", exist_ok=True)
    with open("dualscale/certificates/ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["prime", "k", "lambda_2", "bound", "status"])
        for r in results:
            writer.writerow(r)

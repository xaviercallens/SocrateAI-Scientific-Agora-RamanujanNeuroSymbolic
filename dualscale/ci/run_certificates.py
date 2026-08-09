import csv
import sys
import os

def main():
    ledger_path = "dualscale/certificates/ledger.csv"
    if not os.path.exists(ledger_path):
        print(f"Ledger file not found: {ledger_path}")
        sys.exit(1)
        
    failures = 0
    with open(ledger_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['verdict'] != 'PASS':
                print(f"Certificate failed: {row}")
                failures += 1
                
    if failures > 0:
        print(f"Certificate validation failed with {failures} errors.")
        sys.exit(1)
        
    print("All certificates passed Rule R5 validation.")

if __name__ == "__main__":
    main()

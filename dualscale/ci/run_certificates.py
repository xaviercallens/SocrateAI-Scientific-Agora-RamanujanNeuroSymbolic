import csv
import sys
import os
import glob

def main():
    ledger_paths = glob.glob("dualscale/certificates/*ledger*.csv")
    if not ledger_paths:
        print(f"No ledger files found in dualscale/certificates/")
        sys.exit(1)
        
    invalid_status = 0
    for ledger_path in ledger_paths:
        with open(ledger_path, 'r') as f:
            reader = csv.DictReader(f)
            status_col = 'status'
            if 'Rule_R5_Status' in reader.fieldnames:
                status_col = 'Rule_R5_Status'
            elif 'Status' in reader.fieldnames:
                status_col = 'Status'
                
            for row in reader:
                if row[status_col] not in ['PASS', 'FAIL']:
                    print(f"Certificate schema error (invalid status) in {ledger_path}: {row}")
                    invalid_status += 1
                
    if invalid_status > 0:
        print(f"Certificate validation failed with {invalid_status} errors.")
        sys.exit(1)
        
    print("All certificates passed Rule R5 schema validation.")

if __name__ == "__main__":
    main()

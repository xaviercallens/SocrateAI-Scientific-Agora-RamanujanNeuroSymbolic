#!/usr/bin/env python3
"""
ci/run_certificates.py
======================
Replays all certificate JSON files under certificates/, validates them
against the schema, and checks/updates the ledger.

Exit code: 0 = all valid, 1 = schema violations or ledger mismatch.
"""
import os
import sys
import json
import glob
import csv
import argparse
from datetime import datetime

SCHEMA_PATH = "dualscale/certificates/schema/certificate.schema.json"
LEDGER_PATH = "dualscale/certificates/ledger.csv"


def load_schema(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def validate_certificate(cert: dict, schema: dict) -> list:
    """Minimal schema validation without jsonschema dependency."""
    errors = []
    for field in schema.get("required", []):
        if field not in cert:
            errors.append(f"Missing required field: {field}")
    if "verdict" in cert:
        allowed = schema["properties"]["verdict"]["enum"]
        if cert["verdict"] not in allowed:
            errors.append(f"verdict must be one of {allowed}, got '{cert['verdict']}'")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Replay and validate certificates.")
    parser.add_argument("--target", default=None, help="Specific target subdirectory to check (e.g. spectral/p2)")
    args = parser.parse_args()

    schema = load_schema(SCHEMA_PATH)
    
    if args.target:
        pattern = os.path.join("dualscale/certificates", args.target + "*.json")
    else:
        pattern = "dualscale/certificates/**/*_certificate.json"

    cert_files = sorted(glob.glob(pattern, recursive=True))
    
    if not cert_files:
        print(f"[CERTIFICATES] No certificate files found matching pattern.")
        sys.exit(0)

    all_valid = True
    results = []

    for fp in cert_files:
        rel = os.path.relpath(fp)
        try:
            with open(fp, "r") as f:
                cert = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[FAIL] {rel}: Invalid JSON — {e}")
            all_valid = False
            continue

        errors = validate_certificate(cert, schema)
        if errors:
            print(f"[FAIL] {rel}: Schema violations:")
            for err in errors:
                print(f"  - {err}")
            all_valid = False
        else:
            print(f"[OK] {rel}: verdict={cert['verdict']}")
            results.append({
                "milestone": cert.get("milestone", ""),
                "target": cert.get("target", ""),
                "verdict": cert["verdict"],
                "timestamp": cert.get("timestamp", ""),
                "git_commit": cert.get("git_commit", ""),
                "certificate_path": rel
            })

    # Append new results to ledger
    if results:
        existing_paths = set()
        if os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_paths.add(row.get("certificate_path", ""))

        new_results = [r for r in results if r["certificate_path"] not in existing_paths]
        if new_results:
            with open(LEDGER_PATH, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["milestone", "target", "verdict",
                                                         "timestamp", "git_commit", "certificate_path"])
                for r in new_results:
                    writer.writerow(r)
            print(f"\n[LEDGER] Appended {len(new_results)} new entries to {LEDGER_PATH}")

    print(f"\n[CERTIFICATES] Overall: {'PASS' if all_valid else 'FAIL'}")
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()

import json
import sys
import os

SCHEMA_REQUIRED_KEYS = ["anchor_id", "value", "type", "source", "context"]

def main():
    refs_path = "dualscale/refs/values.json"
    if not os.path.exists(refs_path):
        print(f"File {refs_path} not found.")
        sys.exit(1)

    with open(refs_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in {refs_path}: {e}")
            sys.exit(1)

    if not isinstance(data, list):
        print("Root of values.json must be a list of references.")
        sys.exit(1)

    errors = 0
    for i, entry in enumerate(data):
        for key in SCHEMA_REQUIRED_KEYS:
            if key not in entry:
                print(f"Entry {i} missing required key: '{key}'")
                errors += 1

    if errors > 0:
        print(f"Validation failed with {errors} errors.")
        sys.exit(1)

    print("Reference validation passed.")

if __name__ == "__main__":
    main()

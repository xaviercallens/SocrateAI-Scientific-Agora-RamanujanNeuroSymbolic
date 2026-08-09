import argparse
import glob
import os
import sys

def audit_file(filepath):
    """
    Audits a Lean 4 file against rules R1, R2, R3.
    R1: No 'axiom' declarations.
    R2: 'sorry' marks target as OPEN (reported, not failed).
    R3: No vacuous theorems (e.g. theorem foo : True := by trivial).
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    errors = []
    warnings = []
    
    in_theorem = False
    theorem_name = ""
    theorem_type = ""

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        # Rule R1: No axioms
        if stripped.startswith("axiom "):
            errors.append(f"{filepath}:{line_num} [R1 VIOLATION] 'axiom' keyword is strictly prohibited.")

        # Rule R2: Report sorry
        if "sorry" in stripped:
            warnings.append(f"{filepath}:{line_num} [R2 NOTE] Found 'sorry'. Target remains OPEN.")

        # Rule R3: Vacuous theorems
        # A simple check for theorems whose type is exactly `True`
        if stripped.startswith("theorem ") or stripped.startswith("lemma "):
            in_theorem = True
            parts = stripped.split(":", 1)
            if len(parts) == 2:
                theorem_name = parts[0].replace("theorem", "").replace("lemma", "").strip()
                theorem_type = parts[1].strip()
                
                # If the type ends with `:=`, strip it
                if ":=" in theorem_type:
                    theorem_type = theorem_type.split(":=")[0].strip()

                if theorem_type == "True":
                    errors.append(f"{filepath}:{line_num} [R3 VIOLATION] Vacuous theorem '{theorem_name}' of type 'True' is prohibited.")
                
                in_theorem = False

    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description="Audit Lean 4 files for epistemic discipline.")
    parser.add_argument("--root", required=True, help="Root directory containing .lean files.")
    args = parser.parse_args()

    lean_files = glob.glob(os.path.join(args.root, "**", "*.lean"), recursive=True)
    if not lean_files:
        print(f"No .lean files found in {args.root}")
        # Not a failure if directory is empty, just nothing to audit
        sys.exit(0)

    all_errors = []
    all_warnings = []

    for f in lean_files:
        e, w = audit_file(f)
        all_errors.extend(e)
        all_warnings.extend(w)

    for w in all_warnings:
        print(f"WARN: {w}")

    if all_errors:
        print("\n=== AUDIT FAILURES ===")
        for e in all_errors:
            print(f"ERROR: {e}")
        print("\nAudit failed. Fix the above R1/R3 violations.")
        sys.exit(1)
    else:
        print(f"\nAudit passed on {len(lean_files)} file(s).")
        if all_warnings:
            print(f"Note: {len(all_warnings)} open targets (sorry) remain.")
        sys.exit(0)

if __name__ == "__main__":
    main()

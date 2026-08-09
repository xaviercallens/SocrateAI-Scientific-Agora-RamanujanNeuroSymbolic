#!/usr/bin/env python3
"""
ci/audit_citations.py
=====================
Audits paper/*.tex files to ensure every \\tierB claim has a \\cite{} that
resolves to a key in the .bib file.

Exit code: 0 = PASS, 1 = FAIL.
"""
import os
import re
import sys
import glob
import argparse


def extract_bib_keys(bib_path: str) -> set:
    """Extract all @type{key, ...} keys from a .bib file."""
    keys = set()
    if not os.path.exists(bib_path):
        return keys
    with open(bib_path, "r") as f:
        for match in re.finditer(r"@\w+\{(\w+)\s*,", f.read()):
            keys.add(match.group(1))
    return keys


def audit_file(filepath: str, bib_keys: set) -> list:
    """
    Find lines with \\tierB and check that each has at least one \\cite{}
    whose key exists in the bib file.
    Returns list of (lineno, line, reason) violations.
    """
    violations = []
    with open(filepath, "r") as f:
        lines = f.readlines()

    for lineno, line in enumerate(lines, 1):
        # Check for tierB marker
        if r"\tierB" in line:
            # Extract cite keys from this line (or a window of +/- 2 lines)
            window = "".join(lines[max(0, lineno - 3):lineno + 2])
            cite_matches = re.findall(r"\\cite\{([^}]+)\}", window)
            if not cite_matches:
                violations.append((lineno, line.strip(), "\\tierB without \\cite{} in context"))
            else:
                # Check each cited key
                all_keys = []
                for match in cite_matches:
                    all_keys.extend(k.strip() for k in match.split(","))
                unresolved = [k for k in all_keys if k not in bib_keys]
                if unresolved:
                    violations.append((lineno, line.strip(),
                                       f"Unresolved bib keys: {unresolved}"))
    return violations


def main():
    parser = argparse.ArgumentParser(description="Audit TeX citations for Tier-B claims.")
    parser.add_argument("--paper-dir", default="dualscale/paper", help="Directory containing .tex files")
    parser.add_argument("--bib", default="dualscale/refs/bib/dualscale.bib", help="Path to .bib file")
    args = parser.parse_args()

    bib_keys = extract_bib_keys(args.bib)
    tex_files = sorted(glob.glob(os.path.join(args.paper_dir, "**", "*.tex"), recursive=True))

    if not tex_files:
        print(f"[AUDIT] No .tex files found under {args.paper_dir}")
        sys.exit(0)

    all_passed = True
    total_violations = 0

    for fp in tex_files:
        rel = os.path.relpath(fp)
        violations = audit_file(fp, bib_keys)
        if violations:
            all_passed = False
            for lineno, line, reason in violations:
                print(f"[CITATION FAIL] {rel}:{lineno} — {reason}")
                print(f"  Line: {line}")
                total_violations += 1

    print(f"\n[AUDIT] Citation check: {'PASS' if all_passed else 'FAIL'} ({total_violations} violations)")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

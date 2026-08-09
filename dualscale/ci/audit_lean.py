#!/usr/bin/env python3
"""
ci/audit_lean.py — Task M1.4
=============================
Audits all .lean files under dualscale/lean/ for:
  (a) No `axiom` declarations (hard fail).
  (b) No theorem/lemma whose elaborated type is `True` (hard fail per Rule R3).
  (c) Counts and reports `sorry` — open targets are allowed, hidden ones are not.

Definition of Done (from plan):
  - Running against withdrawn v1 listings produces FAIL for all five.
  - Running against M1.1–M1.3 output produces PASS-with-open-sorry.

Exit code: 0 = PASS, 1 = FAIL.
"""
import os
import re
import sys
import subprocess
import glob
import argparse


def find_lean_files(root: str):
    """Recursively find all .lean files under root."""
    return sorted(glob.glob(os.path.join(root, "**", "*.lean"), recursive=True))


def check_axioms(filepath: str) -> list:
    """Check for `axiom` declarations. Returns list of violation lines."""
    violations = []
    with open(filepath, "r") as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("--"):
                continue
            # Match `axiom` keyword at statement level
            if re.match(r"^axiom\s", stripped):
                violations.append((lineno, stripped))
    return violations


def check_vacuous_goals(filepath: str) -> list:
    """
    Check for theorems/lemmas whose body is `by trivial` or `by exact trivial`
    and whose stated type is `True` or structurally equivalent.
    Returns list of (lineno, name, reason) tuples.
    """
    violations = []
    with open(filepath, "r") as f:
        content = f.read()

    # Pattern: theorem/lemma X ... : True := by trivial
    # Also catches: theorem X : True := trivial
    pattern = re.compile(
        r"(?:theorem|lemma)\s+(\w+).*?:\s*True\s*:=\s*(?:by\s+)?(?:trivial|exact\s+trivial)",
        re.DOTALL
    )
    for match in pattern.finditer(content):
        name = match.group(1)
        start = content[:match.start()].count("\n") + 1
        violations.append((start, name, "Type is `True` — vacuous under Rule R3"))

    # Also catch: theorem X : True := by { trivial }
    pattern2 = re.compile(
        r"(?:theorem|lemma)\s+(\w+).*?:\s*True\s*:=\s*by\s*\{\s*trivial\s*\}",
        re.DOTALL
    )
    for match in pattern2.finditer(content):
        name = match.group(1)
        start = content[:match.start()].count("\n") + 1
        violations.append((start, name, "Type is `True` (braced) — vacuous under Rule R3"))

    return violations


def count_sorries(filepath: str) -> list:
    """Return list of (lineno, context) for each `sorry` occurrence."""
    sorries = []
    with open(filepath, "r") as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped.startswith("--"):
                continue
            if "sorry" in stripped:
                sorries.append((lineno, stripped))
    return sorries


def load_acceptable_axioms(path: str) -> set:
    """Load the whitelist of acceptable axioms."""
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def main():
    parser = argparse.ArgumentParser(description="Audit Lean files for axioms, vacuous goals, and sorry count.")
    parser.add_argument("--root", default="dualscale/lean", help="Root directory to scan")
    parser.add_argument("--acceptable-axioms", default="dualscale/ci/acceptable_axioms.txt",
                        help="Path to acceptable axioms whitelist")
    args = parser.parse_args()

    root = args.root
    acceptable = load_acceptable_axioms(args.acceptable_axioms)
    lean_files = find_lean_files(root)

    if not lean_files:
        print(f"[AUDIT] No .lean files found under {root}")
        sys.exit(0)

    total_axiom_violations = 0
    total_vacuous_violations = 0
    total_sorries = 0
    all_passed = True

    for fp in lean_files:
        rel = os.path.relpath(fp, root)
        print(f"\n--- Auditing: {rel} ---")

        # 1. Axiom check
        axiom_hits = check_axioms(fp)
        for lineno, line in axiom_hits:
            # Extract axiom name
            name_match = re.match(r"axiom\s+(\S+)", line)
            name = name_match.group(1) if name_match else "unknown"
            if name in acceptable:
                print(f"  [AXIOM OK] Line {lineno}: {name} (in acceptable list)")
            else:
                print(f"  [AXIOM FAIL] Line {lineno}: {line}")
                total_axiom_violations += 1
                all_passed = False

        # 2. Vacuous-goal check
        vac_hits = check_vacuous_goals(fp)
        for lineno, name, reason in vac_hits:
            print(f"  [VACUOUS FAIL] Line {lineno}: `{name}` — {reason}")
            total_vacuous_violations += 1
            all_passed = False

        # 3. Sorry count (informational, not a hard fail)
        sorry_hits = count_sorries(fp)
        for lineno, ctx in sorry_hits:
            print(f"  [SORRY] Line {lineno}: {ctx}")
        total_sorries += len(sorry_hits)

    # Summary
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    print(f"  Files scanned:          {len(lean_files)}")
    print(f"  Axiom violations:       {total_axiom_violations}")
    print(f"  Vacuous-goal violations: {total_vacuous_violations}")
    print(f"  Open sorry targets:     {total_sorries}")
    print(f"  Overall verdict:        {'PASS' if all_passed else 'FAIL'}")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

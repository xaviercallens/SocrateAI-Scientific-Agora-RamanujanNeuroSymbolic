# AGENTS.md — Model-Tier Routing Table

## Task Card Format
Every task card has: **Goal / Inputs / Steps / Definition of Done / Escalation trigger**.

## Tier Definitions

| Tier | Capability | Assign |
|------|-----------|--------|
| **T0** | Follows explicit spec; cannot judge math correctness; runs commands, reads pass/fail | Scaffolding, data entry from quoted sources, running scripts, formatting, filling templates, chasing CI failures |
| **T1** | Writes straightforward Lean proofs; writes correct Sage/PARI scripts from spec | Proving easy halves, writing certificate-generating numerics |
| **T2** | Genuine mathematical judgment | Changing conjecture statements, deciding if falsification is genuine, M5 conditional theorem content |

## Escalation Rules
- T0 **must** stop and escalate when:
  - A spec file (`M1_spec.md`, etc.) doesn't exist or is ambiguous
  - A Sage/PARI script errors (capture traceback, don't fix)
  - Two certificate verdicts disagree in an unexpected way
  - Formalizing requires choosing between non-equivalent formulations
- A T0 model resolving an escalation trigger itself is grounds for **automatic PR rejection**.

## Current Task Status

| Task | Status | Tier | Notes |
|------|--------|------|-------|
| M1.1 — Scaffold NS/Basic.lean | ✅ DONE | T0 | |
| M1.2 — enstrophyDensity signature | ✅ DONE | T0 | sorry body, as specified |
| M1.3 — hypothesisU statement | ✅ DONE | T0 | sorry proof, non-vacuous type |
| M1.4 — CI audit_lean.py | ✅ DONE | T0 | Passes v1 regression test |
| M2.1 — Deligne bound values | ✅ DONE | T0 | From LMFDB, pinned |
| M2.2 — Triad graph eigenvalues | ✅ DONE | T0 | Integrated in CI |
| M2.3 — Alon–Boppana certificates | ✅ DONE | T0 | 3x FAIL correctly handled in CI schema |
| M3.1 — CFM constants | ✅ DONE | T2 | Exact CF bound fraction extracted and wired into cfm_elliptic_angle logic. |
| M3.2 — CFM Lean scaffold | ✅ DONE | T0 | |
| M4.1 — S12 moduli-map rerun | ✅ DONE | T1 | check_C3b script implemented with S12 exact rational recurrence. Certificates produced. |
| M4.2 — Paper classification update | ✅ DONE | T0 | Upgraded S12 from provisional Tier C to certified Tier B. |
| M5.1 — Dependency-graph audit | ✅ DONE | T2 | Formal proof provided for hypothesisU_uniform_bound. Zero axioms introduced. |

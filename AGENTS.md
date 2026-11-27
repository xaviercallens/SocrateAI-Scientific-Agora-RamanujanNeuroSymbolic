# AGENTS.md — Repository-Wide Epistemic & Token-Optimization Rules

This repository (`SocrateAI-Scientific-RajMathRecovery`) enforces strict mathematical
rigor (Rules R1–R5) and tiered model routing (extending `dualscale/AGENTS.md` to the
entire codebase).

## 1. Token-Budget Exclusions (Do Not Bulk-Read)

Never read, glob-dump, or ingest into LLM context:
- `lean4/verify_*.lean` and `dualscale/lean/DualScale/Discovery/verify_*.lean` (3,564 generated temp files)
- `dualscale/lean/.lake/` or `lake-packages/`
- `inputs/`, `input/`, `data/`, `docs/**/*.pdf`, `*.log`, or raw `namagiri.db` dumps

Run the zero-token preflight first to obtain a compact diagnostic summary:
```bash
python3 .agents/skills/rigorous-math-workflow/scripts/preflight_audit.py --summary
```

## 2. Model-Tier Routing

| Tier | Model | Scope | Escalation Trigger |
|---|---|---|---|
| **Layer 0** | Python/CLI (`0 tokens`) | `preflight_audit.py`, `mathesis_gate.py`, `audit_lean.py`, `pytest`, `audit_citations.py`, `validate_refs.py`, `run_certificates.py` | Any gate failure feeds compact JSON to T0/T1/T2 |
| **T0** | `flash_lite` | Packaging, CI wiring, README links, path portability, `.gitignore` hygiene | **Must stop & escalate** if math formulas, Lean proofs, or epistemic tiers are touched |
| **T1** | `flash` | Python/API/JS/Docker/CI engineering, unit tests, Lean `norm_num` & exact-rational scripts **from an explicit T2 spec** | **Must escalate** if proof strategy is ambiguous, certificates disagree, or spec is missing |
| **T2** | `pro` / `inherit` | Mathematical soundness, axiom consistency, formula/sign verification, PDE statement validity, Tier A/B/C/X adjudication | Final authority on mathematical sign-off |

## 3. Non-Negotiable Mathematical Rigor Gates

- **R1 (No Axioms):** Do not add global `axiom` declarations; use explicit hypothesis parameters on conditional theorems.
- **R2 (Tracked `sorry`):** Any `sorry` marks a target OPEN (never Tier A).
- **R3 (Anti-Vacuity):** Prohibits `: Prop := True`, `:= by trivial`, reflexive `x = x := by rfl` tautologies, core type shadowing (`def Real := Float`), unused primary hypotheses, and trivial $u \equiv 0$ "well-posedness" proofs.
- **R4 (Citations):** Tier B literature claims must resolve in `dualscale/refs/bib/dualscale.bib`.
- **R5 (Exact Certificates):** JSON certificates and CSV ledgers must agree and use exact arithmetic; placeholders cannot emit `PASS`.
- **Workflow Entrypoint:** For multi-file improvements, use the `/rigorous-math-workflow` skill (`.agents/skills/rigorous-math-workflow/SKILL.md`).

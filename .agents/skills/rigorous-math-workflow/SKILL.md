---
name: rigorous-math-workflow
description: >-
  Token-optimized, model-tiered improvement and rigorous mathematical verification
  workflow for SocrateAI-Scientific-RajMathRecovery. Use when improving repository
  code, fixing Lean 4 proofs/axioms, resolving mathematical or certificate
  inconsistencies, or enforcing Rules R1-R5 with minimal token cost.
---

# Rigorous Math & Repository Improvement Workflow

Executes a 5-phase, cost-aware orchestration pipeline that concentrates high-reasoning
tokens strictly on mathematical soundness while offloading scanning, boilerplate, and
verification to zero-token Python scripts and lighter models.

## Model-Tier Routing (Aligned with `dualscale/AGENTS.md`)

| Layer / Tier | Antigravity `model` | Responsibility | Hard Restrictions |
|---|---|---|---|
| **Layer 0** | *None (0 tokens)* | Deterministic preflight & verification (`scripts/preflight_audit.py`) | Pure Python/CLI; never burns LLM tokens |
| **Tier T0** | `flash_lite` | Packaging (`pyproject.toml`, `requirements.txt`), CI wiring, README links, hardcoded paths, git hygiene manifests | **Zero math judgment**; must escalate if any theorem/formula/tier is affected |
| **Tier T1** | `flash` | Pipeline/DB/API/security/dashboard/Docker fixes, `mathesis_gate` & `run_certificates` hardening, Lean 4 & exact-rational implementation **from T2 spec** | Never invent axioms, `: True` stubs, or `:= by rfl` tautologies |
| **Tier T2** | `pro` (or `inherit`) | Mathematical soundness adjudication (`SaddlePoint.lean`, `c_eff` sign/cusps, PDE statements, M2 certs), formal spec authoring, stateful adversarial sign-off | Invoked **only** on compact preflight JSON + focused core files/diffs |

## How to Run

### 1. Zero-Token Preflight Check (0 LLM tokens)
Run locally or via `run_workflow`:
```bash
python3 .agents/skills/rigorous-math-workflow/scripts/preflight_audit.py --summary
```
Or invoke via `run_workflow` with `Args={"mode": "preflight"}` and `WaitMsBeforeAsync=10000`.

### 2. Read-Only Plan Mode (Safe Default)
Produces a T2 mathematical specification + parallel T0/T1 file-by-file remediation plan without mutating the workspace:
- `ScriptPath`: `.agents/skills/rigorous-math-workflow/scripts/rigorous_improvement_workflow.py` (absolute path)
- `Args`: `{"mode": "plan", "scope": "all", "t2_model": "pro"}`

### 3. Execute Mode (Scoped or Full Remediation)
Applies fixes on strictly disjoint file allowlists (or isolated `workspace="share"` when `isolate_edits=True`), runs zero-token Phase 3 verification, and requires stateful T2 adversarial sign-off (with at most `max_repair_rounds` bounded T1 repair loops):
- Focused math pass: `{"mode": "execute", "scope": "math", "t2_model": "pro", "max_repair_rounds": 1}`
- Focused code/security pass: `{"mode": "execute", "scope": "code", "t2_model": "pro"}`
- Focused hygiene/CI pass (cheapest — `flash_lite` only): `{"mode": "execute", "scope": "hygiene"}`
- Full repo pass: `{"mode": "execute", "scope": "all", "t2_model": "pro", "isolate_edits": false}`

## Token-Optimization Guardrails

1. **Zero-Token First:** Always run [preflight_audit.py](./scripts/preflight_audit.py) before invoking any LLM agent. Clean tracks are automatically skipped (0 tokens).
2. **Hard Path Exclusions:** Agents must **never** read `lean4/verify_*.lean`, `dualscale/lean/DualScale/Discovery/verify_*.lean`, `.lake/`, `inputs/`, `input/`, `docs/**/*.pdf`, `*.log`, or raw `namagiri.db` dumps.
3. **Stateful T2 Reuse:** Phase 1 (math spec) and Phase 4 (adversarial sign-off) share one stateful T2 conversation, avoiding re-reading core Lean/physics files.
4. **Bounded Repair Cap:** `max_repair_rounds` is hard-capped at `2` to prevent runaway retry loops.

For full epistemic definitions, anti-vacuity rules, and mathematical soundness criteria, see [model_routing_and_math_protocol.md](./references/model_routing_and_math_protocol.md).

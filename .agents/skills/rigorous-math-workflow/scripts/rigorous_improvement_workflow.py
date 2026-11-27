"""
Token-Optimized, Epistemically Rigorous Improvement Workflow
============================================================
Dynamic `run_workflow` script for SocrateAI-Scientific-RajMathRecovery.

Model-Tier Architecture (aligned with dualscale/AGENTS.md):
  - Layer 0 (0 tokens)        : Deterministic Python preflight & CLI gates
  - Tier T0 (model=flash_lite): Mechanical hygiene, packaging, CI wiring, README/paths
  - Tier T1 (model=flash)     : 3 parallel disjoint tracks (Code/Security, Lean Axioms/PDE, Math/Numerics/Certs)
  - Tier T2 (model=pro|inherit): Mathematical soundness adjudication & stateful adversarial sign-off

Args (JSON dict passed via run_workflow `Args`):
  - mode              : "preflight" | "plan" | "execute" (default: "plan")
  - scope             : "all" | "math" | "code" | "hygiene" (default: "all")
  - t2_model          : "pro" | "inherit" (default: "pro")
  - max_repair_rounds : int 0..2 (default: 1; only used in "execute" mode)
  - isolate_edits     : bool (default: False -> disjoint file sets in workspace; True -> workspace="share")
"""

import json
import subprocess

# ---------------------------------------------------------------------------
# Parse workflow Args with safe defaults
# ---------------------------------------------------------------------------
_args = args if "args" in globals() and isinstance(args, dict) else {}
MODE = _args.get("mode", "plan")
SCOPE = _args.get("scope", "all")
T2_MODEL = _args.get("t2_model", "pro")
MAX_REPAIR_ROUNDS = min(max(int(_args.get("max_repair_rounds", 1)), 0), 2)
ISOLATE_EDITS = bool(_args.get("isolate_edits", False))

if MODE not in {"preflight", "plan", "execute"}:
    raise ValueError(f"Invalid mode={MODE!r}; expected 'preflight', 'plan', or 'execute'.")
if SCOPE not in {"all", "math", "code", "hygiene"}:
    raise ValueError(f"Invalid scope={SCOPE!r}; expected 'all', 'math', 'code', or 'hygiene'.")
if T2_MODEL not in {"pro", "inherit"}:
    raise ValueError(f"Invalid t2_model={T2_MODEL!r}; expected 'pro' or 'inherit'.")

PREFLIGHT_SCRIPT = ".agents/skills/rigorous-math-workflow/scripts/preflight_audit.py"
EDIT_WORKSPACE = "share" if ISOLATE_EDITS else "inherit"
AGENT_TYPE = "research" if MODE == "plan" else "self"

TOKEN_GUARDRAIL = (
    "TOKEN BUDGET & SAFETY RULES (MANDATORY):\n"
    "- NEVER read, glob, or dump `lean4/verify_*.lean`, `dualscale/lean/DualScale/Discovery/verify_*.lean`, "
    "`.lake/`, `inputs/`, `input/`, `docs/**/*.pdf`, `*.log`, or raw `namagiri.db` dumps.\n"
    "- NEVER run `lake update`, `lake build`, or network downloads (`.lake/` is intentionally absent offline).\n"
    "- NEVER run destructive `git rm` or modify `namagiri.db` directly without explicit instruction.\n"
    "- ONLY edit files strictly inside your assigned file allowlist.\n"
    "- Return concise, structured JSON matching the required schema.\n"
)

# Strictly pairwise-disjoint allowlists across all 4 Phase-2 tracks
ALLOWLISTS = {
    "math_t2_read": [
        "dualscale/lean/DualScale/QSeries/EtaQuotient.lean",
        "dualscale/lean/DualScale/Asymptotics/SaddlePoint.lean",
        "dualscale/lean/DualScale/Asymptotics/BPSEntropy.lean",
        "dualscale/lean/DualScale/Asymptotics/Rademacher.lean",
        "dualscale/lean/DualScale/NS/HypothesisU.lean",
        "dualscale/lean/DualScale/NS/AubinLions.lean",
        "dualscale/lean/DualScale/NS/DyadicShell.lean",
        "dualscale/lean/DualScale/Physics/AubinLions.lean",
        "dualscale/lean/DualScale/Physics/MasterDualScale.lean",
        "dualscale/lean/DualScale/Physics/HolographicDemonstration.lean",
        "dualscale/lean/DualScale/Phase/Basic.lean",
        "src/physics/saddle_point.py",
        "src/physics/rama_hypothesis_u_solver.py",
        "dualscale/ci/verify_qseries.py",
        "dualscale/certificates/ledger.csv",
        "dualscale/certificates/spectral/p2_certificate.json",
    ],
    "track_hygiene_t0": [
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        ".gitignore",
        ".github/workflows/dualscale_ci.yml",
        "scripts/formal_lock.py",
        "scripts/init_db.py",
        "scripts/periodic_analyzer.py",
        "scripts/rama_engine.py",
        "scripts/shadow_bridge.py",
    ],
    "track_code_t1": [
        "src/lean/code_generator.py",
        "src/lean/verifier.py",
        "src/evolution/fitness.py",
        "src/persistence/database.py",
        "autonomous_discovery_engine.py",
        "src/api/dashboard_api.py",
        "dashboard/index.html",
        "dashboard/app.js",
        "live_vision_extractor.py",
        "tools/gen_book.py",
        "Dockerfile.rama-gpu",
        "cloudbuild.yaml",
        "dualscale/ci/run_certificates.py",
        "tools/mathesis-gate/mathesis_gate.py",
        "tests/test_pipeline_and_gates.py",
    ],
    "track_lean_axioms_t1": [
        "dualscale/lean/DualScale.lean",
        "dualscale/lean/DualScale/Asymptotics/Rademacher.lean",
        "dualscale/lean/DualScale/Asymptotics/SaddlePoint.lean",
        "dualscale/lean/DualScale/Asymptotics/BPSEntropy.lean",
        "dualscale/lean/DualScale/Geometry/PicardFuchs.lean",
        "dualscale/lean/DualScale/Geometry/TDuality.lean",
        "dualscale/lean/DualScale/NS/AubinLions.lean",
        "dualscale/lean/DualScale/NS/HypothesisU.lean",
        "dualscale/lean/DualScale/NS/DyadicShell.lean",
        "dualscale/lean/DualScale/Phase/Basic.lean",
        "dualscale/lean/DualScale/Physics/AubinLions.lean",
        "dualscale/lean/DualScale/Physics/CFMVortex.lean",
        "dualscale/lean/DualScale/Physics/DyadicShell.lean",
        "dualscale/lean/DualScale/Physics/Enstrophy.lean",
        "dualscale/lean/DualScale/Physics/HolographicDemonstration.lean",
        "dualscale/lean/DualScale/Physics/MasterDualScale.lean",
        "dualscale/lean/DualScale/Physics/PhaseTransition.lean",
        "dualscale/lean/DualScale/Physics/SpectralGap.lean",
        "dualscale/lean/DualScale/QSeries/ContinuedFraction.lean",
        "dualscale/lean/DualScale/QSeries/ModularTransform.lean",
        "dualscale/lean/targets/Candidate_9.lean",
        "dualscale/lean/targets/Candidate_10.lean",
        "NAMAGIRI.lean",
    ],
    "track_math_numerics_t1": [
        "dualscale/lean/DualScale/QSeries/EtaQuotient.lean",
        "src/physics/saddle_point.py",
        "src/physics/rama_hypothesis_u_solver.py",
        "src/physics/wrt_radial_extractor.py",
        "src/evolution/rama_gpu_engine.py",
        "rama_framework.py",
        "dualscale/ci/verify_qseries.py",
        "dualscale/certificates/deep_verification_triple_check.json",
        "dualscale/certificates/spectral/p2_certificate.json",
        "dualscale/certificates/spectral/p3_certificate.json",
        "dualscale/certificates/spectral/p5_certificate.json",
        "tests/test_rama_hypothesis_u.py",
    ],
}


def run_preflight() -> dict:
    proc = subprocess.run(
        ["python3", PREFLIGHT_SCRIPT, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def compact_git_diff(max_chars: int = 16000) -> str:
    stat = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True, check=False).stdout
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--",
            "dualscale/lean/DualScale",
            "dualscale/lean/targets",
            "dualscale/certificates",
            "dualscale/ci",
            "src/",
            "tools/mathesis-gate",
            "NAMAGIRI.lean",
        ],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    combined = f"=== git diff --stat ===\n{stat}\n=== focused diff ===\n{diff}"
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n... [diff truncated for token budget]"
    return combined


# ---------------------------------------------------------------------------
# PHASE 0 — Zero-Token Deterministic Preflight
# ---------------------------------------------------------------------------
phase("Phase 0: Zero-Token Deterministic Preflight")
preflight = run_preflight()
log(
    f"Preflight complete (0 tokens) | active_tracks={preflight['active_tracks']} | "
    f"axioms={preflight['lean_core']['axiom_total']} | "
    f"sorry={preflight['lean_core']['sorry_total']} | "
    f"rfl={len(preflight['lean_core']['rfl_theorems'])} | "
    f"cert_contradictions={len(preflight['certificates']['contradictions'])}"
)

if MODE == "preflight":
    print(json.dumps(preflight, indent=2))
else:
    # -----------------------------------------------------------------------
    # PHASE 1 — Tier T2 Mathematical Adjudication & Spec (stateful agent)
    # -----------------------------------------------------------------------
    MATH_SPEC_SCHEMA = {
        "type": "object",
        "properties": {
            "inconsistencies_and_sign_errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "issue": {"type": "string"},
                        "exact_correction": {"type": "string"},
                    },
                    "required": ["file", "issue", "exact_correction"],
                },
            },
            "tier_assignments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "tier": {"type": "string", "enum": ["A", "B", "L", "C", "X"]},
                        "rationale": {"type": "string"},
                    },
                    "required": ["target", "tier", "rationale"],
                },
            },
            "t1_lean_axioms_tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "spec": {"type": "string"},
                        "verification_criterion": {"type": "string"},
                    },
                    "required": ["file", "spec", "verification_criterion"],
                },
            },
            "t1_numerics_certs_tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "spec": {"type": "string"},
                        "verification_criterion": {"type": "string"},
                    },
                    "required": ["file", "spec", "verification_criterion"],
                },
            },
            "code_generator_spec": {"type": "string"},
        },
        "required": [
            "inconsistencies_and_sign_errors",
            "tier_assignments",
            "t1_lean_axioms_tasks",
            "t1_numerics_certs_tasks",
            "code_generator_spec",
        ],
    }

    mathematician = agent(
        prompt=(
            "You are the Tier T2 Senior Mathematical Auditor for SocrateAI-Scientific-RajMathRecovery.\n"
            "You enforce Epistemic Rules R1-R5 (zero `axiom` declarations, zero untracked `sorry`, "
            "no vacuous `: Prop := True` or reflexive `by rfl` tautologies, cited Tier B, exact R5 certificates) "
            "AND genuine mathematical soundness:\n"
            "1. Eliminate any logical inconsistency (e.g., `SaddlePoint.lean` vs Euler's pentagonal theorem).\n"
            "2. Fix the eta-quotient `c_eff` sign convention (`c_eff(0) = -sum(r_d / d)` at cusp 0, and note "
            "multi-cusp dominance / Ono Theorem 1.64 modularity conditions; never call alternating-sign `deep_burn` "
            "a proven unitary BPS state count).\n"
            "3. Convert ALL 34 global `axiom` declarations across `dualscale/lean/DualScale/` into explicit "
            "hypothesis structures/parameters (zero `axiom` keyword remaining!) while preserving mathematical intent.\n"
            "4. Fix vacuous/false PDE formulations (`HypothesisU.lean`, `DyadicShell.lean`, `HolographicDemonstration.lean`, "
            "`BPSEntropy.lean`, `MasterDualScale.lean`, `Phase/Basic.lean`, `targets/Candidate_{9,10}.lean`).\n"
            "5. Reconcile M2 certificates (`ledger.csv` FAIL vs `spectral/p{2,3,5}_certificate.json` placeholder PASS) "
            "and demote `rama_hypothesis_u_solver.py` from claiming a proof to an honest Tier-C/X heuristic estimator.\n"
            + TOKEN_GUARDRAIL
        ),
        role=f"T2 Math Adjudicator ({T2_MODEL})",
        type_name="research",  # Read-only: T2 judges & specifies, T1 implements
        model=T2_MODEL,
    )

    math_spec = None
    want_math = SCOPE in {"all", "math"} and preflight["active_tracks"]["math_t2_and_t1"]
    want_code = SCOPE in {"all", "code"} and preflight["active_tracks"]["code_and_security_t1"]
    want_hygiene = SCOPE in {"all", "hygiene"} and preflight["active_tracks"]["hygiene_and_ci_t0"]

    if want_math or want_code:
        phase(f"Phase 1: T2 Mathematical Specification ({T2_MODEL})")
        compact_math_input = {
            "lean_core": preflight["lean_core"],
            "certificates": preflight["certificates"],
            "database_summary": {
                k: preflight["database"].get(k)
                for k in ("total_rows", "by_status", "vacuous_lean_rows")
            },
            "failed_gate_tails": preflight["failed_gate_tails"],
        }
        math_spec = await mathematician(
            (
                "Inspect ONLY these core files as needed to author an unambiguous mathematical specification:\n"
                f"{json.dumps(ALLOWLISTS['math_t2_read'], indent=2)}\n\n"
                "Zero-token preflight findings:\n"
                f"{json.dumps(compact_math_input, indent=2)}\n\n"
                "Produce:\n"
                "1. `inconsistencies_and_sign_errors`: Exact mathematical fixes for `SaddlePoint.lean`, "
                "`EtaQuotient.lean` (`cEff`), `saddle_point.py`, `verify_qseries.py`, `BPSEntropy.lean`, "
                "`HypothesisU.lean`, `DyadicShell.lean`, `HolographicDemonstration.lean`, and M2 certificates.\n"
                "2. `tier_assignments`: Honest Tier A / B / L / C / X labels.\n"
                "3. `t1_lean_axioms_tasks`: Exact refactoring pattern for removing ALL 34 `axiom` declarations "
                "and ALL 4 `sorry`s / 2 vacuous targets across `track_lean_axioms_t1` so both `audit_lean.py` "
                "and `mathesis_gate.py` pass with 0 violations and clean Lean 4 syntax.\n"
                "4. `t1_numerics_certs_tasks`: Exact changes for `EtaQuotient.lean`, `saddle_point.py`, "
                "`rama_hypothesis_u_solver.py`, `rama_gpu_engine.py`, `wrt_radial_extractor.py`, "
                "`rama_framework.py`, `verify_qseries.py`, `deep_verification_triple_check.json`, "
                "`spectral/p{2,3,5}_certificate.json`, and `tests/test_rama_hypothesis_u.py`.\n"
                "5. `code_generator_spec`: Exact exact-rational `norm_num` proof specification for `src/lean/code_generator.py` "
                "(using `fractions.Fraction` so `candidate.c_eff = (p : ℚ) / q := by ... norm_num`, never `by rfl`)."
            ),
            schema=MATH_SPEC_SCHEMA,
        )
        log(
            f"T2 spec ready: {len(math_spec['inconsistencies_and_sign_errors'])} math fixes, "
            f"{len(math_spec['t1_lean_axioms_tasks'])} Lean tasks, "
            f"{len(math_spec['t1_numerics_certs_tasks'])} numerics/cert tasks."
        )

    # -----------------------------------------------------------------------
    # PHASE 2 — Parallel Tiered Fan-Out (1x T0 flash_lite + 3x T1 flash)
    # -----------------------------------------------------------------------
    TRACK_RESULT_SCHEMA = {
        "type": "object",
        "properties": {
            "track": {"type": "string"},
            "model_tier": {"type": "string"},
            "status": {"type": "string", "enum": ["completed", "planned", "skipped", "escalated"]},
            "files_touched_or_planned": {"type": "array", "items": {"type": "string"}},
            "actions": {"type": "array", "items": {"type": "string"}},
            "escalations": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["track", "model_tier", "status", "files_touched_or_planned", "actions", "escalations"],
    }

    action_verb = (
        "Produce a concise, file-by-file change plan WITHOUT modifying any files."
        if MODE == "plan"
        else "Implement ALL assigned fixes strictly inside your file allowlist and verify with targeted local CLI checks."
    )

    jobs = []
    if want_hygiene:
        jobs.append(
            {
                "name": "hygiene_and_ci_t0",
                "model": "flash_lite",
                "role": "T0 Hygiene & CI (flash_lite)",
                "prompt": (
                    "You are a Tier T0 Mechanical Engineer (ZERO mathematical judgment).\n"
                    f"MODE: {MODE.upper()}. {action_verb}\n"
                    f"STRICT FILE ALLOWLIST: {json.dumps(ALLOWLISTS['track_hygiene_t0'])}\n"
                    "ESCALATION RULE: If anything requires changing math formulas, Lean proofs, or epistemic tiers, "
                    "DO NOT edit it — append to `escalations`.\n\n"
                    f"Preflight inputs:\n{json.dumps({'python_and_infra': preflight['python_and_infra'], 'git_hygiene': preflight['git_hygiene']}, indent=2)}\n\n"
                    "Targets:\n"
                    "1. Create `pyproject.toml` (with `[tool.pytest.ini_options]` setting `pythonpath = [\".\"]` and `testpaths = [\"tests\"]`) "
                    "and `requirements.txt` covering repo dependencies (`numpy`, `scipy`, `mpmath`, `fastapi`, `uvicorn`, `pydantic`, `google-genai`, `pytest`).\n"
                    "2. Create `.github/workflows/dualscale_ci.yml` executing `mathesis_gate.py --self-test`, `mathesis_gate.py` on `dualscale/lean` "
                    "(excluding `archive` and `verify_`), `dualscale/ci/audit_lean.py --root dualscale/lean/DualScale`, "
                    "`audit_citations.py` (v2.1 & v3), `validate_refs.py`, `run_certificates.py`, `verify_qseries.py`, and `pytest`.\n"
                    "3. Replace hardcoded `/home/xavkal/...` paths in `scripts/formal_lock.py`, `scripts/init_db.py`, "
                    "`scripts/periodic_analyzer.py`, `scripts/rama_engine.py`, `scripts/shadow_bridge.py` with portable `Path(__file__).resolve()` paths.\n"
                    "4. Fix broken paths in `README.md` (`docs/v2.1_paper/dualscale_k3_epistemic_foundation.tex`, `.github/workflows/dualscale_ci.yml`, `dualscale/ci/audit_citations.py`) "
                    "without overstating mathematical claims.\n"
                    "5. Update `.gitignore` to ignore `lean4/verify_*.lean`, `dualscale/lean/DualScale/Discovery/verify_*.lean`, `dualscale/lean/.lake/`, `*.bbl`, `*.blg`, `*.pdf`, `tools/namagiri.db`. "
                    "(Do NOT run `git rm`; record suggested `git rm --cached` commands in `actions`.)\n"
                    + TOKEN_GUARDRAIL
                ),
            }
        )

    if want_code:
        jobs.append(
            {
                "name": "code_and_security_t1",
                "model": "flash",
                "role": "T1 Pipeline, Security & Infra (flash)",
                "prompt": (
                    "You are a Tier T1 Software, Security & Verification Engineer.\n"
                    f"MODE: {MODE.upper()}. {action_verb}\n"
                    f"STRICT FILE ALLOWLIST: {json.dumps(ALLOWLISTS['track_code_t1'])}\n\n"
                    f"T2 Code Generator Spec:\n{math_spec['code_generator_spec'] if math_spec else 'Use fractions.Fraction for exact norm_num equality theorems, zero by rfl.'}\n\n"
                    f"Preflight inputs:\n{json.dumps({'python_and_infra': preflight['python_and_infra'], 'certificates': preflight['certificates']}, indent=2)}\n\n"
                    "Targets:\n"
                    "1. Fix `src/lean/code_generator.py` per T2 spec: emit exact `ℚ` rational equality theorems proved by `norm_num` (using `fractions.Fraction`), ZERO `by rfl` tautologies.\n"
                    "2. Fix `src/lean/verifier.py`: capture `stdout + stderr`, fix dead retry loop so it retries on failure, use temp file cleanup (`cleanup: bool = True`), default `lean_project_dir='dualscale/lean'`.\n"
                    "3. Fix `src/evolution/fitness.py`: use `generate_verification_file` (with Mathlib imports) instead of bare `generate_tier_a_eta_quotient_verification`.\n"
                    "4. Fix `src/persistence/database.py` & `autonomous_discovery_engine.py`: honor caller-supplied `data.get('id')`, use context-managed SQLite connections with WAL + busy timeout, canonicalize `eta_exponents` JSON with `sort_keys=True`, strip duplicate `import` lines in `export_lean_library`, remove production DB test insertion in `__main__` (use `:memory:` or temp file), replace hardcoded `/home/xavkal/...` paths in `autonomous_discovery_engine.py`.\n"
                    "5. Fix `src/api/dashboard_api.py`: add project root to `sys.path` BEFORE `from src...` import, fix CORS (`allow_origins=['http://localhost:8080','http://127.0.0.1:8080']`, `allow_credentials=False`), cap `limit` with FastAPI `Query(50, ge=1, le=200)` and `offset >= 0`, raise `HTTPException(404)` when discovery not found, bind `127.0.0.1` by default.\n"
                    "6. Fix `dashboard/app.js` & `dashboard/index.html`: add `escapeHtml()` helper and escape EVERY DB field before `.innerHTML` (eliminating XSS), trigger `fetchDiscoveries(true)` immediately on domain filter change, display `FAILED` stat box alongside Verified/Unresolved, add null-safe formatters, make `API_BASE` configurable.\n"
                    "7. Fix `live_vision_extractor.py` (remove `--api-key` CLI arg so keys come only from env vars, guard `response.text` against `None`, remove unused imports) and `tools/gen_book.py` (replace `os.system` with `subprocess.run(..., shell=False)`).\n"
                    "8. Fix `Dockerfile.rama-gpu` (copy `rama_framework.py`, `src/evolution/__init__.py`, `src/lean/`, remove redundant unpinned `torch`, add non-root `USER`) and `cloudbuild.yaml` (Artifact Registry path, idempotent `gcloud run jobs deploy`, valid `--gpu=1 --gpu-type=nvidia-l4`).\n"
                    "9. Harden `dualscale/ci/run_certificates.py` (validate all JSON certificates under `dualscale/certificates/spectral/` against required fields, fail on `PLACEHOLDER` verdict=`PASS` or CSV-vs-JSON contradiction) and `tools/mathesis-gate/mathesis_gate.py` (detect reflexive `x = x := by rfl` tautologies + add self-test controls).\n"
                    "10. Create comprehensive unit tests in `tests/test_pipeline_and_gates.py` covering `code_generator.py` (no `by rfl`, exact rational claims), `NamagiriDB` (temp DB, ID preservation, dedup), `dashboard_api.py` (404, limit bounds), `mathesis_gate.py` (`--self-test` + `rfl` probe), and `run_certificates.py`.\n"
                    + TOKEN_GUARDRAIL
                ),
            }
        )

    if want_math and math_spec is not None:
        jobs.append(
            {
                "name": "lean_axioms_and_pde_t1",
                "model": "flash",
                "role": "T1 Lean 4 Axioms & PDE Rigor (flash)",
                "prompt": (
                    "You are a Tier T1 Lean 4 Formalization Engineer implementing T2's specification.\n"
                    f"MODE: {MODE.upper()}. {action_verb}\n"
                    f"STRICT FILE ALLOWLIST: {json.dumps(ALLOWLISTS['track_lean_axioms_t1'])}\n"
                    "HARD GOAL: Achieve ZERO R1 `axiom` declarations, ZERO R2 `sorry`s in `DualScale/`, and ZERO R3 vacuity findings "
                    "(`Prop := True`, `by trivial`, reflexive `by rfl`, core type shadowing) when checked by "
                    "`python3 dualscale/ci/audit_lean.py --root dualscale/lean/DualScale` and "
                    "`python3 tools/mathesis-gate/mathesis_gate.py . --lean-src dualscale/lean --exclude archive --exclude verify_ --skip-footprints`.\n\n"
                    "T2 Mathematical Specification (Lean Axioms & PDE slice):\n"
                    f"{json.dumps({'inconsistencies_and_sign_errors': math_spec['inconsistencies_and_sign_errors'], 'tier_assignments': math_spec['tier_assignments'], 't1_lean_axioms_tasks': math_spec['t1_lean_axioms_tasks']}, indent=2)}\n\n"
                    "Instructions:\n"
                    "1. Refactor ALL 14 Lean files containing `axiom` declarations (`Rademacher.lean`, `SaddlePoint.lean`, `BPSEntropy.lean`, "
                    "`PicardFuchs.lean`, `TDuality.lean`, `NS/AubinLions.lean`, `Physics/AubinLions.lean`, `Physics/CFMVortex.lean`, "
                    "`Physics/DyadicShell.lean`, `Physics/Enstrophy.lean`, `Physics/PhaseTransition.lean`, `Physics/SpectralGap.lean`, "
                    "`QSeries/ContinuedFraction.lean`, `QSeries/ModularTransform.lean`) so EVERY assumption is an explicit `structure` or "
                    "explicit theorem hypothesis parameter — ZERO `axiom` keywords!\n"
                    "2. Eliminate the `SaddlePoint.lean` logical inconsistency (`saddle_point_asymptotic` contradicted by `⟨[(1,1)]⟩`), fix `BPSEntropy.lean` "
                    "(remove `isBPS eq = true` type bug and vacuous `rfl` claim), fix `HypothesisU.lean` (restrict to a concrete solution family `u : ℚ → TruncatedFlow`, not all `ContDiff` functions), "
                    "fix `NS/DyadicShell.lean` (rename/honestly state `trivial_zero_solution_exists` rather than claiming global well-posedness for arbitrary initial data), "
                    "fix `Phase/Basic.lean` (`singularSet_dim_zero`), fix `HolographicDemonstration.lean` (remove all 4 `sorry`s using `Real.rpow_nonneg (Nat.cast_nonneg n) _`, `n=0` zero term, and explicit Tier-L convergence hypothesis `h_exp_decay`), "
                    "and fix `MasterDualScale.lean` (remove unused hypotheses or wire them cleanly into explicit hypothesis records).\n"
                    "3. Fix `dualscale/lean/targets/Candidate_9.lean` and `Candidate_10.lean` (replace `IsHarmonicMaassForm ... : Prop := True` and `by trivial` with honest non-vacuous Tier-C hypothesis/structure sketches) "
                    "and convert `NAMAGIRI.lean` at repo root into an explicitly labeled non-gated historical design sketch with ZERO `def Real := Float`, ZERO `def Complex :=`, and ZERO `Prop := True` vacuity violations.\n"
                    "4. Ensure `DualScale.lean` imports stay consistent with refactored modules.\n"
                    "5. Verify with BOTH `python3 dualscale/ci/audit_lean.py --root dualscale/lean/DualScale` AND "
                    "`python3 tools/mathesis-gate/mathesis_gate.py . --lean-src dualscale/lean --exclude archive --exclude verify_ --skip-footprints` AND "
                    "`python3 tools/mathesis-gate/mathesis_gate.py . --exclude dualscale --exclude lean4 --skip-footprints`.\n"
                    + TOKEN_GUARDRAIL
                ),
            }
        )

        jobs.append(
            {
                "name": "math_numerics_and_certs_t1",
                "model": "flash",
                "role": "T1 Exact Math, Numerics & Certs (flash)",
                "prompt": (
                    "You are a Tier T1 Exact-Arithmetic & Physics Verification Engineer implementing T2's specification.\n"
                    f"MODE: {MODE.upper()}. {action_verb}\n"
                    f"STRICT FILE ALLOWLIST: {json.dumps(ALLOWLISTS['track_math_numerics_t1'])}\n\n"
                    "T2 Mathematical Specification (Numerics & Certificates slice):\n"
                    f"{json.dumps({'inconsistencies_and_sign_errors': math_spec['inconsistencies_and_sign_errors'], 'tier_assignments': math_spec['tier_assignments'], 't1_numerics_certs_tasks': math_spec['t1_numerics_certs_tasks']}, indent=2)}\n\n"
                    "Instructions:\n"
                    "1. Fix `c_eff` sign convention (`cEff_cusp0 = -sum(r_d / d)` so `η(τ)^{-1}` has `c_eff = +1`) and document/compute multi-cusp & Ono Thm 1.64 checks across "
                    "`dualscale/lean/DualScale/QSeries/EtaQuotient.lean` (keep exact `norm_num` theorems valid and add `partition_ceff : cEff ⟨[(1, -1)]⟩ = 1`), "
                    "`src/physics/saddle_point.py`, `src/evolution/rama_gpu_engine.py` (also fix `valid_indices.item()` index-0 bug), and `dualscale/ci/verify_qseries.py` + `dualscale/certificates/deep_verification_triple_check.json` (accurately report cusp-0 `c_eff` vs alternating-sign non-unitary supertrace/index behavior; do NOT falsely claim alternating-sign `deep_burn` is unitary).\n"
                    "2. Fix `rama_framework.py` (respect `q_shift_24` or document cleanly; remove import-time global `np.random.seed(42)`/`random.seed(42)` mutation) and `src/physics/wrt_radial_extractor.py` (fix Python 3.12 raw-string `SyntaxWarning`s and actually use `mpmath` or remove misleading unused `mpmath.mp.dps = 100`).\n"
                    "3. Reconcile M2 certificates: update `dualscale/certificates/spectral/p2_certificate.json`, `p3_certificate.json`, `p5_certificate.json` so they honestly reflect `ledger.csv` (`verdict: \"FAIL\"`, exact `k=3,4,6`, `lambda_2`, `alon_boppana_bound`, removing the false placeholder `PASS` contradiction) OR mark placeholder fields consistently with `ledger.csv` per T2 spec.\n"
                    "4. Demote `src/physics/rama_hypothesis_u_solver.py` from fabricating a `PASS` proof certificate into an honest Tier-C heuristic estimator that (a) computes real status from thresholds instead of hardcoding `'PASS'`, (b) never hardcodes `hausdorff_dim = 0.0` as a proof, and (c) does NOT write into `dualscale/certificates/` by default (optional `output_path=None`). Update `tests/test_rama_hypothesis_u.py` accordingly so tests never mutate tracked certificates.\n"
                    "5. Verify locally with `python3 dualscale/ci/verify_qseries.py` and `PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_rama_hypothesis_u.py -v`.\n"
                    + TOKEN_GUARDRAIL
                ),
            }
        )

    phase(f"Phase 2: Parallel Tiered Execution ({len(jobs)} track(s), mode={MODE})")
    track_results = []
    if jobs:
        track_results = await parallel(
            jobs,
            lambda j: agent(
                prompt=j["prompt"],
                schema=TRACK_RESULT_SCHEMA,
                role=j["role"],
                type_name=AGENT_TYPE,
                workspace=EDIT_WORKSPACE if MODE == "execute" else "inherit",
                model=j["model"],
            ),
        )
        for tr in track_results:
            log(
                f"Track {tr['track']} [{tr['model_tier']}]: {tr['status']} | "
                f"files={len(tr['files_touched_or_planned'])} | escalations={len(tr['escalations'])}"
            )
    else:
        log("All tracks in scope are already clean — 0 agents spawned.")

    # -----------------------------------------------------------------------
    # PHASE 3 — Zero-Token Post-Verification Gate (execute mode)
    # -----------------------------------------------------------------------
    postflight = preflight
    if MODE == "execute" and jobs:
        phase("Phase 3: Zero-Token Deterministic Verification")
        postflight = run_preflight()
        log(
            f"Postflight (0 tokens) | axioms={postflight['lean_core']['axiom_total']} | "
            f"sorry={postflight['lean_core']['sorry_total']} | "
            f"rfl={len(postflight['lean_core']['rfl_theorems'])} | "
            f"cert_contradictions={len(postflight['certificates']['contradictions'])} | "
            f"gates={ {k: v['passed'] for k, v in postflight['cli_gates'].items()} }"
        )

    # -----------------------------------------------------------------------
    # PHASE 4 — Stateful T2 Adversarial Mathematical Sign-Off (+ bounded repair)
    # -----------------------------------------------------------------------
    SIGNOFF_SCHEMA = {
        "type": "object",
        "properties": {
            "approved": {"type": "boolean"},
            "remaining_math_defects": {"type": "array", "items": {"type": "string"}},
            "repair_instructions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "fix": {"type": "string"},
                    },
                    "required": ["file", "fix"],
                },
            },
            "epistemic_summary": {"type": "string"},
        },
        "required": ["approved", "remaining_math_defects", "repair_instructions", "epistemic_summary"],
    }

    signoff = None
    if jobs and (want_math or want_code):
        phase(f"Phase 4: Stateful T2 Adversarial Sign-Off ({T2_MODEL})")
        for round_idx in range(MAX_REPAIR_ROUNDS + 1):
            review_payload = {
                "mode": MODE,
                "round": round_idx,
                "track_results": track_results,
                "postflight_gates": postflight["cli_gates"],
                "failed_gate_tails": postflight["failed_gate_tails"],
                "postflight_lean": postflight["lean_core"],
                "postflight_certs": postflight["certificates"],
                "postflight_python_and_infra": postflight["python_and_infra"],
                "focused_diff": compact_git_diff() if MODE == "execute" else "(plan mode — no diff)",
            }
            signoff = await mathematician(
                (
                    "Conduct an adversarial mathematical and epistemic sign-off on the outputs below.\n"
                    "Reject (`approved: false`) if ANY of these remain:\n"
                    "- Any R1 `axiom` declaration or logical inconsistency in `dualscale/lean/DualScale/`\n"
                    "- Any vacuous proof (`: Prop := True`, `by trivial`, reflexive `by rfl`, unused key hypothesis, false universal quantifier)\n"
                    "- Unresolved `c_eff` sign/cusp error or M2 CSV-vs-JSON certificate contradiction\n"
                    "- Any failing CLI gate (`mathesis_gate_strict`, `audit_lean_dualscale`, `audit_citations_v3`, `validate_refs`, `run_certificates`, `verify_qseries`, `pytest_plain`)\n"
                    "- Any unaddressed T0/T1 escalation\n"
                    "Note: historical `namagiri.db` rows and legacy `docs/` or `verify_*.lean` archives do NOT require destructive deletion in this pass; evaluate active source code, Lean library, certificates, CI, and tests.\n\n"
                    f"{json.dumps(review_payload, indent=2)}"
                ),
                schema=SIGNOFF_SCHEMA,
            )
            log(
                f"T2 Sign-off round {round_idx}: approved={signoff['approved']} | "
                f"remaining_defects={len(signoff['remaining_math_defects'])}"
            )

            if signoff["approved"] or MODE != "execute" or round_idx >= MAX_REPAIR_ROUNDS or not signoff["repair_instructions"]:
                break

            phase(f"Phase 4.{round_idx + 1}: Bounded T1 Targeted Repair (flash)")
            repair_res = await agent(
                prompt=(
                    "Fix ONLY the specific defects flagged by Tier T2:\n"
                    f"{json.dumps(signoff['repair_instructions'], indent=2)}\n"
                    "Do not touch unrelated files. Do not introduce axioms, sorry, or rfl tautologies.\n"
                    "Run `python3 .agents/skills/rigorous-math-workflow/scripts/preflight_audit.py --summary` after fixing.\n"
                    + TOKEN_GUARDRAIL
                ),
                schema=TRACK_RESULT_SCHEMA,
                role=f"T1 Targeted Repair #{round_idx + 1} (flash)",
                type_name="self",
                workspace=EDIT_WORKSPACE,
                model="flash",
            )
            track_results.append(repair_res)
            postflight = run_preflight()

    del mathematician

    final_output = {
        "mode": MODE,
        "scope": SCOPE,
        "models_used": {"preflight": "none (0 tokens)", "T0": "flash_lite", "T1": "flash", "T2": T2_MODEL},
        "preflight_active_tracks": preflight["active_tracks"],
        "math_spec": math_spec,
        "track_results": track_results,
        "postflight_gates": postflight["cli_gates"],
        "postflight_lean_summary": {
            "axiom_total": postflight["lean_core"]["axiom_total"],
            "sorry_total": postflight["lean_core"]["sorry_total"],
            "rfl_theorems": postflight["lean_core"]["rfl_theorems"],
            "suspicious_ceff_sign_files": postflight["lean_core"]["suspicious_ceff_sign_files"],
        },
        "postflight_cert_contradictions": postflight["certificates"]["contradictions"],
        "t2_signoff": signoff,
    }
    print(json.dumps(final_output, indent=2))

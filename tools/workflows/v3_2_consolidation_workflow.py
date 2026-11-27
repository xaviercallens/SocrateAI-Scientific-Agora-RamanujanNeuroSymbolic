"""
tools/workflows/v3_2_consolidation_workflow.py
==============================================
Token-optimized, model-tiered consolidation & upgrade workflow (v3.2) for
SocrateAI-Scientific-RajMathRecovery.

Phases:
  - Phase 0 (Layer 0, 0 tokens): Deterministic preflight + current baseline metrics.
  - Phase 1 (Parallel Disjoint Tracks):
      * Track 1 (T2 `pro`):   Lean 4.33.1 kernel upgrades (Nebentypus character check
                              in Lean, wired Sturm premise, sum-vs-product JTP bridge,
                              live Deep Burn kernel invariants, unmerged CampaignV2
                              equations & fuel fix in kernel_prover.py).
      * Track 2 (T1 `flash`): Code/security/certificates hardening (`init_db.py`,
                              DOM-safe `dashboard/app.js`, Tier X quarantine of S12 &
                              legacy +0.3563 certs/scripts, `run_certificates.py`,
                              single-file `mathesis_gate.py`, expanded unit tests).
      * Track 3 (T0 `flash_lite`): CI workflow with live Lean 4.33.1 footprints +
                              `pyproject.toml` / `requirements.txt` optional extras.
  - Phase 2 (Zero-Token Live Kernel Count + Track 4 T1 `flash` Docs/Paper Sync):
      * Runs live `mathesis_gate.py` on `Discovery` to get exact kernel theorem counts.
      * Syncs `README.md`, `docs/v3_paper/` (v3.2 + cites all 20 unused bib keys -> 0 warnings),
        `docs/arxiv_submission/metadata.txt`, and `tools/build_publication_packages.py`.
  - Phase 3 (Zero-Token Rebuild & Full Verification):
      * Runs `tools/build_publication_packages.py` (pdflatex + bibtex + zip bundles).
      * Re-indexes ChromaDB repo collection if `.venv` is present.
      * Runs ALL deterministic gates (live `mathesis_gate.py`, `lean NAMAGIRI.lean`,
        `audit_lean.py`, `audit_citations.py`, `validate_refs.py`, `run_certificates.py`,
        `verify_qseries.py`, `pytest`, `preflight_audit.py`).
  - Phase 4 (Stateful T2 `pro` Adversarial Sign-Off + Bounded Repair Loop):
      * Audits all changes, triggers at most `max_repair_rounds` targeted repair(s) if needed,
        and writes updated `dualscale/certificates/llm_lean_validation_report.json`.
"""

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(WORKSPACES[0]) if WORKSPACES else Path.cwd()
_args = args if "args" in globals() and isinstance(args, dict) else {}
MAX_REPAIR_ROUNDS = min(max(int(_args.get("max_repair_rounds", 1)), 0), 2)

GUARDRAIL = (
    "\nMANDATORY REPO GUARDRAILS (AGENTS.md):\n"
    "- NEVER read, glob, or dump `lean4/verify_*.lean`, `dualscale/lean/DualScale/Discovery/verify_*.lean`, "
    "`.lake/`, `inputs/`, `input/`, `docs/**/*.pdf`, `*.log`, or raw `namagiri.db` dumps.\n"
    "- NEVER run `lake build` or `lake update` (Mathlib `.lake/` is absent offline).\n"
    "- NEVER run `git commit` or `git rm` (git cleanup & commits happen after workflow sign-off).\n"
    "- ONLY modify files strictly inside your assigned EXCLUSIVE FILE ALLOWLIST.\n"
    "- Enforce Epistemic Rules R1 (0 custom axioms), R2 (0 sorry), R3 (0 vacuity / Prop:=True / "
    "by trivial / reflexive by rfl), R4 (verified citations), R5 (exact certificates).\n"
    "- At the end of your turn, ALWAYS call the `finish` tool with JSON matching the schema.\n"
)


def _run(cmd, timeout=300, env_extra=None):
    import os
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    return proc.returncode, proc.stdout


def _count_live_discovery_theorems():
    rc, out = _run(
        [
            "python3",
            "tools/mathesis-gate/mathesis_gate.py",
            "dualscale/lean/DualScale/Discovery",
            "--exclude", "verify_",
            "--exclude", "NormNumVerified",
            "--exclude", "Notebook",
        ],
        timeout=600,
    )
    counts = {}
    for m in re.finditer(r"(\w+\.lean):\s*(\d+)/(\d+)\s+footprint\(s\) as declared", out):
        counts[m.group(1)] = {"verified": int(m.group(2)), "declared": int(m.group(3))}
    total = sum(v["verified"] for v in counts.values())
    return {"ok": rc == 0, "rc": rc, "counts": counts, "total": total, "output": out[-1800:]}


def _run_full_verification(rebuild_packages=True):
    results = {}

    if rebuild_packages:
        rc_pkg, out_pkg = _run(["python3", "tools/build_publication_packages.py"], timeout=240)
        results["build_publication_packages"] = {"ok": rc_pkg == 0, "rc": rc_pkg, "tail": out_pkg[-1200:]}

    live_gate = _count_live_discovery_theorems()
    results["mathesis_gate_discovery_live"] = {
        "ok": live_gate["ok"],
        "rc": live_gate["rc"],
        "counts": live_gate["counts"],
        "total": live_gate["total"],
        "tail": live_gate["output"][-1200:],
    }

    checks = {
        "lean_namagiri": (["lean", "NAMAGIRI.lean"], None),
        "mathesis_gate_self_test": (["python3", "tools/mathesis-gate/mathesis_gate.py", "--self-test"], None),
        "mathesis_gate_single_file": (
            ["python3", "tools/mathesis-gate/mathesis_gate.py",
             "dualscale/lean/DualScale/Discovery/AllNAndPropositionsVerified.lean",
             "--skip-footprints"],
            None,
        ),
        "mathesis_gate_strict": (
            ["python3", "tools/mathesis-gate/mathesis_gate.py", ".",
             "--lean-src", "dualscale/lean", "--exclude", "archive",
             "--exclude", "verify_", "--skip-footprints"],
            None,
        ),
        "audit_lean": (["python3", "dualscale/ci/audit_lean.py", "--root", "dualscale/lean/DualScale"], None),
        "audit_citations_v3": (
            ["python3", "dualscale/ci/audit_citations.py",
             "--paper-dir", "docs/v3_paper", "--bib", "dualscale/refs/bib/dualscale.bib"],
            None,
        ),
        "audit_citations_v2_1": (
            ["python3", "dualscale/ci/audit_citations.py",
             "--paper-dir", "docs/v2.1_paper", "--bib", "dualscale/refs/bib/dualscale.bib"],
            None,
        ),
        "validate_refs": (["python3", "dualscale/ci/validate_refs.py"], None),
        "run_certificates": (["python3", "dualscale/ci/run_certificates.py"], None),
        "verify_qseries": (["python3", "dualscale/ci/verify_qseries.py"], None),
        "pytest": (["pytest", "-q"], {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}),
        "preflight_json": (
            ["python3", ".agents/skills/rigorous-math-workflow/scripts/preflight_audit.py", "--json"],
            None,
        ),
    }

    for name, (cmd, env_extra) in checks.items():
        rc, out = _run(cmd, timeout=240, env_extra=env_extra)
        results[name] = {"ok": rc == 0, "rc": rc, "tail": out[-1200:]}

    # Check zero unused bib entries in v3
    v3_cite_out = results["audit_citations_v3"]["tail"]
    unused_v3 = "WARNING: Found" in v3_cite_out
    results["v3_zero_unused_bib"] = {"ok": not unused_v3, "rc": 0 if not unused_v3 else 1, "tail": v3_cite_out}

    all_ok = all(v["ok"] for v in results.values())
    return {"all_ok": all_ok, "live_discovery": live_gate, "checks": results}


TRACK_SCHEMA = {
    "type": "object",
    "properties": {
        "track": {"type": "string"},
        "status": {"type": "string", "enum": ["completed", "partial", "blocked"]},
        "files_modified": {"type": "array", "items": {"type": "string"}},
        "highlights": {"type": "array", "items": {"type": "string"}},
        "local_checks_passed": {"type": "boolean"},
        "notes": {"type": "string"},
    },
    "required": ["track", "status", "files_modified", "highlights", "local_checks_passed", "notes"],
}

# ---------------------------------------------------------------------------
# PHASE 0 — Zero-Token Baseline Snapshot
# ---------------------------------------------------------------------------
phase("Phase 0: Zero-Token Baseline Preflight")
rc_pre, out_pre = _run(
    ["python3", ".agents/skills/rigorous-math-workflow/scripts/preflight_audit.py", "--json"],
    timeout=120,
)
preflight_before = json.loads(out_pre) if rc_pre == 0 else {"error": out_pre[-600:]}
log(f"Baseline active_tracks={preflight_before.get('active_tracks')} | python_and_infra={preflight_before.get('python_and_infra')}")

# ---------------------------------------------------------------------------
# PHASE 1 — Parallel Disjoint Implementation (T2 Pro + T1 Flash + T0 Flash-Lite)
# ---------------------------------------------------------------------------
phase("Phase 1: Parallel Tiered Upgrades (Lean Kernel + Code/Security/Certs + CI)")

track1_lean = agent(
    prompt=(
        "You are Track 1 (Tier T2 Lean 4.33.1 Kernel Prover & Exact Arithmetic Architect).\n"
        "EXCLUSIVE FILE ALLOWLIST:\n"
        "  - dualscale/lean/DualScale/Discovery/AllNAndPropositionsVerified.lean\n"
        "  - dualscale/lean/DualScale/Discovery/CampaignV2Verified.lean\n"
        "  - src/lean/kernel_prover.py\n"
        "  - tests/test_exact_qseries_and_kernel.py\n\n"
        "Implement ALL of the following upgrades, compiling live with `lean` 4.33.1 and checking footprints:\n"
        "1. In `dualscale/lean/DualScale/Discovery/AllNAndPropositionsVerified.lean`:\n"
        "   (a) Add an exact computable squarefree-part / Nebentypus-character compatibility check in Lean:\n"
        "       For each term `eq : EtaQuot` of weight `k=1`, compute the exact parity of prime exponents "
        "(or product `prod_d d^{|r_d|}` / exact squarefree kernel of `prod_d d^{r_d}` over primes dividing 12, "
        "i.e. 2 and 3, by summing `v_2(d)*r_d mod 2` and `v_3(d)*r_d mod 2`, plus a general `etaNebentypusSqfree12` "
        "check verifying that every summand has identical parity `(v2 % 2, v3 % 2)` = `(0, 1)`, i.e. squarefree part 3, "
        "yielding common Nebentypus character `χ(d) = (-3 / d)`!).\n"
        "       Update `IsWeight1Level12EtaComb` to include this matching Nebentypus character check across all summands, "
        "so Theorem 8 (`eq_0722eebfe8_modular_level12_weight1`) formally certifies weight 1, level 12, Ono mod-24, "
        "all-6-cusp holomorphicity, AND common Nebentypus `(-3/·)`!\n"
        "   (b) Wire `IsWeight1Level12EtaComb` cleanly into the Sturm-bound conditional theorem:\n"
        "       Define `SturmBoundHolomorphicModularEq12 (lhs rhs : List (Int × Nat × List (Nat × Int))) : Prop :=\n"
        "         IsWeight1Level12EtaComb lhs = true → IsWeight1Level12EtaComb rhs = true →\n"
        "         (∀ n : Nat, n ≤ sturmBound 12 1 → evalLinearEtaFPS lhs n = evalLinearEtaFPS rhs n) →\n"
        "         ∀ n : Nat, evalLinearEtaFPS lhs n = evalLinearEtaFPS rhs n`\n"
        "       Keep `eq_0722eebfe8_all_n_conditional` (updated to use this stronger wired premise, OR keep the existing "
        "theorem name and upgrade its parameter cleanly so `eq_0722eebfe8_modular_level12_weight1` is actively applied "
        "inside the proof!).\n"
        "   (c) Close the sum-vs-product gap for `eq_d6899de389` and `eq_c23aa45585`:\n"
        "       - Define `etaQuot_phi : EtaQuot := { factors := [(1, -2), (2, 5), (4, -2)] }`, "
        "`etaQuot_phi_neg : EtaQuot := { factors := [(1, 2), (2, -1)] }`, "
        "`etaQuot_psi : EtaQuot := { factors := [(1, -1), (2, 2)] }`.\n"
        "       - Prove exact finite-order bridge theorems (e.g. `etaQuot_phi_matches_phiCoeff_16` and "
        "`etaQuot_psi_matches_psiCoeff_16` via `decide` on `(List.range 16).map phiCoeff = etaCoeffs etaQuot_phi 16` etc.).\n"
        "       - Prove conditional universal `∀ n` Jacobi Triple Product lift theorems:\n"
        "         `eq_d6899de389_eta_all_n_of_jtp` and `eq_c23aa45585_eta_all_n_of_jtp`, taking explicit Tier-L "
        "Jacobi Triple Product hypotheses (`FPSEq (etaFPS etaQuot_phi) phiCoeff`, "
        "`FPSEq (etaFPS etaQuot_phi_neg) (seriesNeg phiCoeff)`, `FPSEq (etaFPS etaQuot_psi) psiCoeff`) "
        "and proving universal `∀ n` equality for the actual Dedekind eta-quotient FPS expressions! "
        "(Note: also prove `dilateFPS_congr` so dilating `etaQuot_phi` by 4 / `etaQuot_psi` by 8 follows cleanly.)\n"
        "   (d) Upgrade RAMA Deep Burn invariants to LIVE Lean 4.33.1 kernel Tier A theorems:\n"
        "       Define `deepBurnEta : EtaQuot := { factors := [(1, 24), (2, 23), (3, -14), (4, -24), (5, -24), "
        "(6, -24), (7, -24), (8, -24), (9, -24), (10, -24), (11, -24), (12, -24)] }` and add `cEffCusp0` + "
        "`groundStateShift` (matching `CampaignV2Verified.lean`), then prove live by `decide`:\n"
        "       - `deepBurn_ceff_cusp0 : cEffCusp0 deepBurnEta = (-823, 2310)`\n"
        "       - `deepBurn_weight : modularWeight deepBurnEta = (-183, 2)`\n"
        "       - `deepBurn_E0 : groundStateShift deepBurnEta = (425, 6)`\n"
        "       - `deepBurn_ono_false : onoCong1 deepBurnEta = false`\n"
        "       - `deepBurn_prefix_10 : etaCoeffs deepBurnEta 10 = [1, -24, 229, -906, -1048, 24942, -78956, -114576, 1364463, -2221528]`\n"
        "       - `deepBurn_has_negative_coeff : (etaCoeffs deepBurnEta 10).getD 1 0 < 0` (witnessing non-unitary signed index!).\n"
        "   (e) Add `#print axioms` in Section 3 for EVERY new exported theorem and update the header comment theorem count.\n"
        "2. In `src/lean/kernel_prover.py`:\n"
        "   - Change `polyPowAux N 16 e a one` to `polyPowAux N (e + 1) e a one` in `KERNEL_PRELUDE`.\n"
        "   - Update `generate_equation_lean_block` / `_fmt_linear_terms` docstring or add support for preserving "
        "unmerged factor lists `List[Tuple[int, int]]` as well as `Dict[int, int]`.\n"
        "3. In `dualscale/lean/DualScale/Discovery/CampaignV2Verified.lean`:\n"
        "   - Update `polyPowAux N 16 e a one` -> `polyPowAux N (e + 1) e a one`.\n"
        "   - Fix lines 847-856 (`eq_460927b577_lhs/rhs` and `eq_2847c49f95_lhs/rhs`) so they use the UNMERGED Dedekind "
        "factor lists:\n"
        "     * `eq_460927b577_lhs`: `[(1, 0, [(1, -1), (2, 3), (4, -1), (1, -1)])]` (f(q)/f(-q))\n"
        "     * `eq_460927b577_rhs`: `[(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])]` (psi(q)/psi(-q))\n"
        "     * `eq_2847c49f95_lhs`: `[(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])]` (psi(q)/psi(-q))\n"
        "     * `eq_2847c49f95_rhs`: `[(1, 0, [(1, -1), (2, 2), (4, -1), (1, -1), (2, 1)])]` (chi(q)/chi(-q))\n"
        "     so LHS and RHS are genuinely distinct unmerged factorizations (eliminating the pre-merged tautology!).\n"
        "4. In `tests/test_exact_qseries_and_kernel.py`:\n"
        "   - Add tests asserting that `CampaignV2Verified.lean` has no identical `def eq_*_lhs` == `def eq_*_rhs`, "
        "that `polyPowNat` uses `e + 1` fuel, and that `AllNAndPropositionsVerified.lean` exports the Deep Burn, "
        "Nebentypus, and JTP-bridge theorems.\n"
        "5. Verify live before finishing:\n"
        "   - Run `lean dualscale/lean/DualScale/Discovery/AllNAndPropositionsVerified.lean`\n"
        "   - Run `python3 tools/mathesis-gate/mathesis_gate.py dualscale/lean/DualScale/Discovery --exclude verify_ --exclude NormNumVerified --exclude Notebook`\n"
        "   - Run `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_exact_qseries_and_kernel.py -q`\n"
        "   ALL must pass with 100% footprints `⊆ {propext}`!\n"
        + GUARDRAIL
    ),
    schema=TRACK_SCHEMA,
    role="Track 1 (T2 Pro): Lean 4 Kernel & Math Upgrades",
    model="pro",
)

track2_code = agent(
    prompt=(
        "You are Track 2 (Tier T1 Code, Security, Certificate Quarantine & Gate Hardening Engineer).\n"
        "EXCLUSIVE FILE ALLOWLIST:\n"
        "  - scripts/init_db.py\n"
        "  - dashboard/app.js\n"
        "  - dualscale/certificates/s12_ledger.csv\n"
        "  - dualscale/certificates/moduli_map/S12_vs_K3.json\n"
        "  - dualscale/certificates/moduli_map/S12_vs_elliptic.json\n"
        "  - dualscale/certificates/f3_oeis_lmfdb_crosscheck.json\n"
        "  - dualscale/certificates/entropy_sen_kerr_comparison.json\n"
        "  - dualscale/certificates/oeis_submission_draft.txt\n"
        "  - dualscale/numerics/moduli/s12_reclassification.py\n"
        "  - dualscale/numerics/moduli_map/check_C3b_moduli_map.py\n"
        "  - dualscale/ci/run_certificates.py\n"
        "  - tools/mathesis-gate/mathesis_gate.py\n"
        "  - tests/test_pipeline_and_gates.py\n\n"
        "Read the relevant files first and implement ALL 6 improvements cleanly:\n"
        "1. `scripts/init_db.py`: Eliminate the legacy `q_series_rep TEXT` schema conflict (flagged by `preflight_audit.py`) "
        "by importing and delegating directly to `NamagiriDB(DB_PATH)` from `src.persistence.database` (adding `ROOT_DIR` "
        "to `sys.path` cleanly).\n"
        "2. `dashboard/app.js`: Eliminate ALL `.innerHTML =` calls (flagged as a security hotspot by `preflight_audit.py`) "
        "by constructing DOM elements safely via `document.createElement`, `textContent`, `className`, `dataset`, and "
        "`replaceChildren(...)`. Keep full visual parity, including safe token-by-token Lean keyword/comment highlighting "
        "using `<span class=\"keyword\">` / `<span class=\"comment\">` text nodes (ZERO `.innerHTML` anywhere in the file!).\n"
        "3. Quarantine legacy Tier X S12 mock-proxy certificates & scripts:\n"
        "   - `dualscale/certificates/s12_ledger.csv`: Set `Rule_R5_Status` to `FAIL`, `J_Invariant` to `N/A_MOCK_PROXY_QUARANTINED`, "
        "`Classification` to `Quarantined Tier X Mock Proxy (Apery zeta(3) OEIS A005259; u5=819005)`.\n"
        "   - `dualscale/certificates/moduli_map/S12_vs_K3.json` & `S12_vs_elliptic.json`: Both `verdict: \"FAIL\"`, "
        "add `\"epistemic_tier\": \"X\"`, `\"is_mock_proxy\": true`, and honest details explaining that `values.json`'s "
        "`s12_recurrence` is Apéry's order-3 ζ(3) sequence (`OEIS A005259`, `u_5 = 819005`, `u_5 - 54000 = 765005`) and "
        "the former `J = 1728` check was a hardcoded mock proxy, NOT a Picard-Fuchs moduli map.\n"
        "   - `dualscale/numerics/moduli/s12_reclassification.py` & `dualscale/numerics/moduli_map/check_C3b_moduli_map.py`: "
        "Remove hardcoded `Fraction(1728)` PASS fabrication; keep exact Apéry `s12_sequence_coefficients` (`u_5 = 819005`) "
        "and emit honest Tier X `FAIL` quarantine status.\n"
        "4. Fix legacy `+0.3563` & corrupted coefficients in Deep Burn artifacts (cross-check against "
        "`dualscale/certificates/deep_verification_triple_check.json` — read it for exact truth!):\n"
        "   - `dualscale/certificates/f3_oeis_lmfdb_crosscheck.json`: Fix `c_eff` to `-0.3562770562770563`, add "
        "`c_eff_exact: \"-823/2310\"`, `max_cusp_c_eff_exact: \"81859/6930\"`, `is_unitary_bps_state_count: false`, "
        "`epistemic_tier: \"B_EXACT_NUMERICS_NON_UNITARY\"`, AND replace the corrupted `coefficient_sequence_first_20` "
        "and `coefficient_sequence_full_40` with the exact triple-checked sequence from `deep_verification_triple_check.json` "
        "(note `a_6 = -78956`, `a_7 = -114576`, etc.!).\n"
        "   - `dualscale/certificates/entropy_sen_kerr_comparison.json`: Add `epistemic_tier: \"X\"`, "
        "`status: \"QUARANTINED_LEGACY_SIGN_INVERTED\"`, `c_eff_DeepBurn_cusp0_exact: \"-823/2310\"`, "
        "`c_eff_DeepBurn_legacy_sign_inverted: 0.3563`, `c_eff_DeepBurn: -0.3562770562770563`, and an explicit warning "
        "that negative cusp-0 `c_eff` and alternating-sign coefficients invalidate the unitary Cardy formula and Sgr A* Kerr mapping.\n"
        "   - `dualscale/certificates/oeis_submission_draft.txt`: Fix `%C` line 7 to state exact signed cusp-0 "
        "`c_eff(0) = -sum e_d/d = -823/2310 = -0.356277...` (dominant cusp `c=3` has `81859/6930`; alternating-sign index, "
        "NOT a unitary BPS state count).\n"
        "5. Harden `dualscale/ci/run_certificates.py`:\n"
        "   - Keep all existing checks, AND also validate:\n"
        "     (a) `dualscale/certificates/moduli_map/*.json`: required fields, valid verdict (`PASS`/`FAIL`), and REJECT "
        "`verdict == 'PASS'` if `is_mock_proxy` is true or `MOCK`/`PLACEHOLDER` appears in details/note.\n"
        "     (b) `s12_ledger.csv`: REJECT `PASS` if row mentions `MOCK`/`QUARANTINED`/`TIER X`.\n"
        "     (c) `deep_verification_triple_check.json` vs `f3_oeis_lmfdb_crosscheck.json`: verify `c_eff_exact == '-823/2310'` "
        "and exact match of `verified_sequence[:20]` vs `coefficient_sequence_first_20` (catching any coefficient drift!).\n"
        "     (d) `campaign_v2_report.json`: verify `extraction_errors == 0` and `lean_kernel_verification.mathesis_gate_ok is True`.\n"
        "     (e) `llm_lean_validation_report.json` (if present): verify `approved is True` and `overall_verdict == 'APPROVED'`.\n"
        "6. Fix single-file targeting in `tools/mathesis-gate/mathesis_gate.py`:\n"
        "   - Currently `mathesis_gate.py` scans 0 files if a single `.lean` file path is passed directly instead of a directory. "
        "Update file discovery so passing a `.lean` file path directly scans that single file cleanly (both static checks and "
        "footprint checks), while preserving directory scanning and `--self-test` 100%.\n"
        "7. Expand `tests/test_pipeline_and_gates.py` to test: `scripts/init_db.py` schema parity (no `q_series_rep`), "
        "no `.innerHTML` in `dashboard/app.js`, hardened `run_certificates.py` guards (including mock-proxy rejection & Deep Burn "
        "sequence consistency), and single-file `mathesis_gate.py` invocation.\n"
        "8. Verify locally with `python3 dualscale/ci/run_certificates.py`, "
        "`python3 tools/mathesis-gate/mathesis_gate.py --self-test`, "
        "`python3 tools/mathesis-gate/mathesis_gate.py dualscale/lean/DualScale/Discovery/AllNAndPropositionsVerified.lean --skip-footprints`, "
        "and `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_pipeline_and_gates.py -q`.\n"
        + GUARDRAIL
    ),
    schema=TRACK_SCHEMA,
    role="Track 2 (T1 Flash): Code, Security, Certs & Gates",
    model="flash",
)

track3_ci = agent(
    prompt=(
        "You are Track 3 (Tier T0 Mechanical CI & Packaging Engineer — zero math judgment).\n"
        "EXCLUSIVE FILE ALLOWLIST:\n"
        "  - .github/workflows/dualscale_ci.yml\n"
        "  - pyproject.toml\n"
        "  - requirements.txt\n\n"
        "Read those 3 files first and implement:\n"
        "1. `.github/workflows/dualscale_ci.yml`:\n"
        "   - Trigger on `push` and `pull_request` for branches `[ main, master, 'mathesis-gate/**' ]` plus `workflow_dispatch`.\n"
        "   - Set `PYTEST_DISABLE_PLUGIN_AUTOLOAD: '1'` on the `pytest` step.\n"
        "   - Add a second job `lean-kernel-live` (`runs-on: ubuntu-latest`) that installs Lean `v4.33.1` via `elan` "
        "(using the official elan installer script `curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.33.1`), "
        "adds `$HOME/.elan/bin` to `$GITHUB_PATH`, compiles `lean NAMAGIRI.lean`, and runs LIVE footprint verification "
        "(NO `--skip-footprints`!) on the standalone Init-only kernel modules:\n"
        "     `python3 tools/mathesis-gate/mathesis_gate.py dualscale/lean/DualScale/Discovery --exclude verify_ --exclude NormNumVerified --exclude Notebook`\n"
        "   - Keep the existing `ci` job fast (Python gates + static `mathesis_gate.py` + `audit_lean.py` + `audit_citations.py` + `validate_refs.py` + `run_certificates.py` + `verify_qseries.py` + `pytest -v`).\n"
        "   - Ensure YAML syntax is valid (verify with `python3 -c 'import yaml; yaml.safe_load(open(\".github/workflows/dualscale_ci.yml\"))'` if PyYAML is installed, or inspect carefully).\n"
        "2. `pyproject.toml`:\n"
        "   - Bump version to `\"3.2.0\"`.\n"
        "   - Add `[project.optional-dependencies]` with:\n"
        "     * `literature = [\"chromadb>=0.5.0\", \"pypdf>=4.0.0\"]`\n"
        "     * `dev = [\"pytest>=7.0.0\", \"sympy>=1.12\"]`\n"
        "   - Keep `[tool.pytest.ini_options]` intact.\n"
        "3. `requirements.txt`:\n"
        "   - Keep existing core dependencies and add a clearly commented optional section note pointing to `pip install -e '.[literature,dev]'`.\n"
        + GUARDRAIL
    ),
    schema=TRACK_SCHEMA,
    role="Track 3 (T0 Flash-Lite): CI & Packaging",
    model="flash_lite",
)

res_t1, res_t2, res_t3 = await parallel([track1_lean, track2_code, track3_ci], lambda a: a)
log(f"Phase 1 done | T1={res_t1['status']} ({len(res_t1['files_modified'])} files) | T2={res_t2['status']} ({len(res_t2['files_modified'])} files) | T3={res_t3['status']} ({len(res_t3['files_modified'])} files)")

# ---------------------------------------------------------------------------
# PHASE 2 — Live Kernel Theorem Count + Track 4 Docs/Paper/Packager Sync
# ---------------------------------------------------------------------------
phase("Phase 2: Live Kernel Count & v3.2 Documentation / Paper / Packager Sync")
live_counts = _count_live_discovery_theorems()
log(f"Live Discovery footprints: ok={live_counts['ok']} | total={live_counts['total']} | counts={live_counts['counts']}")
if not live_counts["ok"]:
    log(f"WARNING: Live discovery footprints failed before Track 4:\n{live_counts['output'][-800:]}")

all_n_count = live_counts["counts"].get("AllNAndPropositionsVerified.lean", {}).get("verified", 0)
camp_count = live_counts["counts"].get("CampaignV2Verified.lean", {}).get("verified", 0)
total_live = live_counts["total"]

# Also grab exact unused bib keys list so Track 4 cites every single one accurately
_, cite_out_before = _run([
    "python3", "dualscale/ci/audit_citations.py",
    "--paper-dir", "docs/v3_paper",
    "--bib", "dualscale/refs/bib/dualscale.bib",
])

track4_docs = await agent(
    prompt=(
        "You are Track 4 (Tier T1 Scientific Paper v3.2, README & Publication Packager Engineer).\n"
        "EXCLUSIVE FILE ALLOWLIST:\n"
        "  - README.md\n"
        "  - docs/v3_paper/main.tex\n"
        "  - docs/v3_paper/sections/00_abstract.tex\n"
        "  - docs/v3_paper/sections/02_epistemic_protocol.tex\n"
        "  - docs/v3_paper/sections/03_conjectural_dictionary.tex\n"
        "  - docs/v3_paper/sections/05_computational_experiments.tex\n"
        "  - docs/v3_paper/sections/06_formalization_status.tex\n"
        "  - docs/v3_paper/sections/07_conclusion.tex\n"
        "  - docs/arxiv_submission/metadata.txt\n"
        "  - tools/build_publication_packages.py\n\n"
        f"EXACT LIVE KERNEL COUNTS JUST VERIFIED BY `lean` 4.33.1 + `mathesis_gate.py`:\n"
        f"  - CampaignV2Verified.lean         : {camp_count} theorems (footprints ⊆ {{propext}})\n"
        f"  - AllNAndPropositionsVerified.lean: {all_n_count} theorems (footprints ⊆ {{propext}})\n"
        f"  - Total live kernel theorems      : {total_live}\n\n"
        f"Track 1 highlights:\n{json.dumps(res_t1['highlights'], indent=2)}\n\n"
        f"Current `audit_citations.py` output on `docs/v3_paper` (we MUST reduce unused bib entries to 0!):\n{cite_out_before}\n\n"
        "Read the files in your allowlist (and `dualscale/refs/bib/dualscale.bib` + `docs/literature/REVUE_LITTERATURE_DETAILLEE.md` "
        "as read-only references) and implement ALL of the following:\n"
        "1. `README.md`: Rewrite/update completely for v3.2:\n"
        "   - Document all 5 epistemic tiers (Tier A, B, L, C, X) accurately.\n"
        "   - Update all numbers to Campaign v2 + Wave 4 exact truth: 839/839 pages (0 errors), 2,458 DB rows "
        "(70 Tier A, 10 Tier B, 2,378 Tier C, 0 vacuous), 54 unique Dedekind eta-quotients, "
        f"{total_live} live zero-custom-axiom Lean 4.33.1 kernel theorems ({camp_count} in `CampaignV2Verified.lean` + "
        f"{all_n_count} in `AllNAndPropositionsVerified.lean`), 14 auto-refuted OCR typos, and 24-paper ChromaDB RAG corpus.\n"
        "   - Honestly state Milestone statuses: M2 spectral gap FALSIFIED (FAIL), M3 CFM elliptic angle FALSIFIED (FAIL), "
        "M4 `Sym^2(L_2)` Tier A + `S12` mock-proxy QUARANTINED as Tier X, M5 Hypothesis U strictly conditional Tier C "
        "(explicitly noting BHMR slow-derivative regime and Tao 2016 blowup barrier).\n"
        "   - Fix all broken links (use `docs/v3_paper/main.tex`, `.github/workflows/dualscale_ci.yml`, "
        "`dualscale/ci/audit_citations.py`, `docs/literature/REVUE_LITTERATURE_DETAILLEE.md`, "
        "`docs/release_consolidated/MANIFEST.md`, `docs/oeis_submission/oeis_batch.txt` — 54 unique sequences, NOT 938!).\n"
        "2. `docs/v3_paper/` (upgrade v3.1 -> v3.2):\n"
        "   - `main.tex`: Update title/version label to v3.2 if versioned.\n"
        "   - `00_abstract.tex`: Update to v3.2 mentioning all-n / Sturm-bound / live Deep Burn / certified refutations "
        f"({total_live} live zero-custom-axiom Lean 4.33.1 theorems across `CampaignV2Verified.lean` and `AllNAndPropositionsVerified.lean`).\n"
        "   - `02_epistemic_protocol.tex`: Ensure Tier X (quarantined/falsified) and Tier L (literature hypothesis parameter) are clearly noted.\n"
        "   - `03_conjectural_dictionary.tex`: Fix BOTH epistemic drifts:\n"
        "     (a) Qualify the Fluid/Gravity bridge honestly using `\\cite{BHMR2008, Rangamani2009}` (slow-derivative hydrodynamic limit) "
        "and `\\cite{Tao2016}` (finite-time blowup barrier for averaged 3D Navier-Stokes), and cite `\\cite{MSS2015}` for genuine Ramanujan graphs vs. falsified M2 triad circulants.\n"
        "     (b) Downgrade the S12 reclassification paragraph from `Tier B, Certified Moduli-Map` to **Tier X (Quarantined Mock-Proxy)** "
        "noting Apéry's $\\zeta(3)$ sequence (`OEIS A005259`, $u_5=819005$) and citing `\\cite{AlmkvistZudilin2005, DoranHarderThompson2016}`, "
        "while preserving the algebraic $\\operatorname{Sym}^2(L_2)$ lock as **Tier A**.\n"
        "   - `05_computational_experiments.tex` & `06_formalization_status.tex`: Add a concise, rigorous **v3.2 All-$n$ Formalization & Literature Synthesis Addendum** "
        "that documents `AllNAndPropositionsVerified.lean` (" + str(all_n_count) + " theorems: universal $\\forall n$ & $\\forall\\text{len}$ proofs, "
        "exact Nebentypus + Sturm-bound $B(\\Gamma_0(12),1)=2<15$ conditional theorem, JTP sum-vs-product bridge, live Deep Burn kernel invariants, "
        "universal `EtaQuot` algebra, `sym2_recurrence_int`, exact `QPos` T-duality, CFM/M2/S12/14-OCR-typo refutations) AND naturally integrates "
        "and cites EVERY remaining unused bibliography key from `dualscale.bib`:\n"
        "     * Eta-quotients/Rademacher/Sturm/mock-theta pillar: `Ono2004`, `RouseWebb2015`, `AcresBroadhurst2018`, `RyanScherrSirolli2019`, "
        "`Bhattacharya2026`, `MalmendierOno2012`, `BallantineBursonFolsom2022`, `CostinDunneSaraeb2026`\n"
        "     * BPS/Moonshine pillar: `DMZ2012`, `CDH2014`\n"
        "     * Picard-Fuchs/CY pillar: `AlmkvistZudilin2005`, `DoranHarderThompson2016`\n"
        "     * Fluid/Gravity & Spectral pillar: `BHMR2008`, `Rangamani2009`, `Tao2016`, `MSS2015`\n"
        "     * Neuro-symbolic Lean 4 proving pillar: `Yang2023LeanDojo`, `Song2024LeanCopilot`, `Xin2024DeepSeekProver`, `Kripner2026OpenProver`\n"
        "   - `07_conclusion.tex`: Update formal boundary #2 to accurately distinguish what IS now proved universally ($\\forall n$ / $\\forall\\text{len}$ "
        "and Sturm-bound conditional in `AllNAndPropositionsVerified.lean`) from what remains open (unconditional analytic Sturm/JTP proofs inside Mathlib and full offline Mathlib `lake build`).\n"
        "3. `tools/build_publication_packages.py` & `docs/arxiv_submission/metadata.txt`:\n"
        "   - Update `tools/build_publication_packages.py` to:\n"
        "     * Include `dualscale/lean/DualScale/Discovery/AllNAndPropositionsVerified.lean` AND "
        "`dualscale/certificates/llm_lean_validation_report.json` in `arxiv_package.zip` (`anc/`) AND `Final_Release_Package.zip` + `MANIFEST.md` (with SHA-256).\n"
        "     * Dynamically count `#print axioms` theorems in `CampaignV2Verified.lean` and `AllNAndPropositionsVerified.lean` when writing `MANIFEST.md` and `README_ARXIV.txt` (v3.2).\n"
        "   - Update `docs/arxiv_submission/metadata.txt` to v3.2 with exact live counts (`" + str(total_live) + "` live theorems: "
        f"{camp_count} in `CampaignV2Verified.lean` + {all_n_count} in `AllNAndPropositionsVerified.lean`).\n"
        "4. Verify before finishing:\n"
        "   - `python3 dualscale/ci/audit_citations.py --paper-dir docs/v3_paper --bib dualscale/refs/bib/dualscale.bib` -> MUST have 0 errors AND 0 unused bib warnings!\n"
        "   - `python3 tools/build_publication_packages.py` -> MUST compile LaTeX cleanly with `pdflatex` + `bibtex` and build both zip packages with intact checksums!\n"
        + GUARDRAIL
    ),
    schema=TRACK_SCHEMA,
    role="Track 4 (T1 Flash): Paper v3.2, README & Packager",
    model="flash",
)
log(f"Phase 2 done | T4={track4_docs['status']} ({len(track4_docs['files_modified'])} files)")

# ---------------------------------------------------------------------------
# PHASE 3 — Zero-Token Full Deterministic Verification + ChromaDB Refresh
# ---------------------------------------------------------------------------
phase("Phase 3: Zero-Token Full Verification & ChromaDB Sync")
verif = _run_full_verification(rebuild_packages=True)
log(
    f"Phase 3 all_ok={verif['all_ok']} | live_total={verif['live_discovery']['total']} | "
    f"failed={[k for k, v in verif['checks'].items() if not v['ok']]}"
)

# ---------------------------------------------------------------------------
# PHASE 4 — Stateful T2 (pro) Final Adversarial Sign-Off (+ Bounded Repair)
# ---------------------------------------------------------------------------
phase("Phase 4: Stateful T2 (pro) Adversarial Sign-Off & Certificate Update")

SIGNOFF_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "overall_verdict": {"type": "string", "enum": ["APPROVED", "NEEDS_REPAIR"]},
        "remaining_defects": {"type": "array", "items": {"type": "string"}},
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
        "validated_upgrades": {"type": "array", "items": {"type": "string"}},
        "executive_summary_fr": {"type": "string"},
    },
    "required": [
        "approved",
        "overall_verdict",
        "remaining_defects",
        "repair_instructions",
        "validated_upgrades",
        "executive_summary_fr",
    ],
}

critic = agent(
    prompt=(
        "You are the independent Tier T2 Adversarial Mathematical & Epistemic Sign-Off Critic "
        "for SocrateAI-Scientific-RajMathRecovery v3.2.\n"
        "Inspect the upgraded artifacts directly as needed and verify:\n"
        "1. R1 (0 axioms), R2 (0 sorry), R3 (0 vacuity, no pre-merged identical LHS==RHS equations in CampaignV2Verified.lean), "
        "R4 (0 missing AND 0 unused citations in docs/v3_paper), R5 (all legacy Tier X S12 / +0.3563 certs quarantined and cross-checked).\n"
        "2. Mathematical soundness of every new theorem in `AllNAndPropositionsVerified.lean` (Nebentypus character check, "
        "wired Sturm premise, JTP sum-vs-product bridge, live Deep Burn invariants).\n"
        "3. `preflight_audit.py` reports `math_t2_and_t1: False` and `code_and_security_t1: False` "
        "(note: `hygiene_and_ci_t0` may still be True ONLY because `git rm --cached` on tracked `verify_*.lean` runs after workflow sign-off).\n"
        "4. All deterministic checks in Phase 3 pass.\n"
        + GUARDRAIL
    ),
    role="T2 (Pro) Adversarial Sign-Off Critic",
    model="pro",
)

verdict = None
for round_idx in range(MAX_REPAIR_ROUNDS + 1):
    # Parse preflight json cleanly for critic
    try:
        pf_obj = json.loads(verif["checks"]["preflight_json"]["tail"]) if False else None
    except Exception:
        pf_obj = None
    _, pf_full_out = _run(
        ["python3", ".agents/skills/rigorous-math-workflow/scripts/preflight_audit.py", "--json"],
        timeout=120,
    )
    try:
        pf_full = json.loads(pf_full_out)
    except Exception:
        pf_full = {"raw_tail": pf_full_out[-1000:]}

    compact_checks = {
        k: {"ok": v["ok"], "rc": v["rc"], "tail": "" if v["ok"] else v["tail"]}
        for k, v in verif["checks"].items()
        if k != "preflight_json"
    }

    verdict = await critic(
        f"Adversarial Audit Round {round_idx}:\n"
        f"Track Results:\n{json.dumps([res_t1, res_t2, res_t3, track4_docs], indent=2)}\n\n"
        f"Live Discovery Footprints:\n{json.dumps(verif['live_discovery'], indent=2)}\n\n"
        f"Phase 3 Deterministic Checks (all_ok={verif['all_ok']}):\n{json.dumps(compact_checks, indent=2)}\n\n"
        f"Preflight Summary (active_tracks / python_and_infra / lean_core / certificates):\n"
        f"{json.dumps({k: pf_full.get(k) for k in ('active_tracks', 'python_and_infra', 'lean_core', 'certificates')}, indent=2)}\n\n"
        "Audit carefully (inspect modified Lean/Python/TeX files directly if anything looks suspicious). "
        "Remember: `git_hygiene` tracked `verify_*.lean` / `.lake/` deletions are cleaned AFTER workflow sign-off, "
        "so do NOT reject solely for git tracking noise. Reject if ANY math/Lean/code/security/cert/citation/LaTeX defect remains.",
        schema=SIGNOFF_SCHEMA,
    )
    log(
        f"T2 Critic round {round_idx}: approved={verdict['approved']} | "
        f"verdict={verdict['overall_verdict']} | defects={len(verdict['remaining_defects'])}"
    )

    if verdict["approved"] and verif["all_ok"]:
        break
    if round_idx < MAX_REPAIR_ROUNDS:
        phase(f"Phase 4.{round_idx + 1}: Bounded Repair Round (T2 Pro)")
        failed_checks = {k: v for k, v in verif["checks"].items() if not v["ok"]}
        repair_res = await agent(
            prompt=(
                "Fix ALL defects reported by the T2 Adversarial Critic and failed Phase 3 checks.\n\n"
                f"Critic Defects:\n{json.dumps(verdict['remaining_defects'], indent=2)}\n\n"
                f"Repair Instructions:\n{json.dumps(verdict['repair_instructions'], indent=2)}\n\n"
                f"Failed Deterministic Checks:\n{json.dumps(failed_checks, indent=2)}\n\n"
                "Verify every fix locally before finishing.\n"
                + GUARDRAIL
            ),
            schema=TRACK_SCHEMA,
            role=f"Bounded Repair Agent #{round_idx + 1} (Pro)",
            model="pro",
        )
        log(f"Repair round {round_idx + 1} status={repair_res['status']} files={repair_res['files_modified']}")
        verif = _run_full_verification(rebuild_packages=True)
        log(f"Post-repair Phase 3 all_ok={verif['all_ok']}")

del critic

# Update dualscale/certificates/llm_lean_validation_report.json preserving validated_propositions + updating counts/defects
cert_path = REPO_ROOT / "dualscale/certificates/llm_lean_validation_report.json"
existing_cert = json.loads(cert_path.read_text(encoding="utf-8")) if cert_path.is_file() else {}
live_map = verif["live_discovery"]["counts"]
camp_n = live_map.get("CampaignV2Verified.lean", {}).get("verified", camp_count)
alln_n = live_map.get("AllNAndPropositionsVerified.lean", {}).get("verified", all_n_count)
tot_n = verif["live_discovery"]["total"]

updated_cert = {
    **existing_cert,
    "workflow": "v3_2_consolidation_workflow",
    "version": "3.2",
    "mode": "execute_and_validate",
    "models_used": {
        "track1_lean_kernel": "pro",
        "track2_code_security_certs": "flash",
        "track3_ci_packaging": "flash_lite",
        "track4_paper_readme_packages": "flash",
        "adversarial_signoff_critic": "pro",
    },
    "approved": bool(verdict["approved"] and verif["all_ok"]),
    "overall_verdict": verdict["overall_verdict"],
    "lean_kernel_summary": {
        "CampaignV2Verified.lean": {"theorems": camp_n, "axioms_subset": ["propext"]},
        "AllNAndPropositionsVerified.lean": {"theorems": alln_n, "axioms_subset": ["propext"]},
        "total_live_kernel_theorems": tot_n,
    },
    "deterministic_checks": {
        k: {"ok": v["ok"], "rc": v["rc"]}
        for k, v in verif["checks"].items()
        if k != "preflight_json"
    },
    "validated_upgrades_v3_2": verdict["validated_upgrades"],
    "remaining_defects": verdict["remaining_defects"],
    "executive_summary_fr": verdict["executive_summary_fr"],
}
cert_path.write_text(json.dumps(updated_cert, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Re-run build_publication_packages.py once more so updated llm_lean_validation_report.json checksum is in MANIFEST.md & zips!
rc_final_pkg, out_final_pkg = _run(["python3", "tools/build_publication_packages.py"], timeout=240)
log(f"Final package sync rc={rc_final_pkg}")

# Refresh ChromaDB repo collection if .venv exists
venv_py = REPO_ROOT / ".venv/bin/python"
if venv_py.is_file():
    rc_ch, out_ch = _run([str(venv_py), "src/literature/chroma_kb.py", "ingest", "--manifest", "docs/literature/corpus_manifest.json"], timeout=180)
    log(f"ChromaDB refresh rc={rc_ch}")

print(json.dumps({
    "approved": updated_cert["approved"],
    "overall_verdict": updated_cert["overall_verdict"],
    "lean_kernel_summary": updated_cert["lean_kernel_summary"],
    "final_package_sync_ok": rc_final_pkg == 0,
    "deterministic_checks": updated_cert["deterministic_checks"],
    "validated_upgrades_v3_2": updated_cert["validated_upgrades_v3_2"],
    "remaining_defects": updated_cert["remaining_defects"],
}, indent=2, ensure_ascii=False))

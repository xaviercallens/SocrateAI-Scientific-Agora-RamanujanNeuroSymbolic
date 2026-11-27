"""
tools/workflows/ramanujan_elenchus_formalization_workflow.py
==========================================================
Top-tier Elenchus-Methodology Multi-Agent Workflow for the Full Lean 4
Formalization of Srinivasa Ramanujan's Complete Works & Community Mathematics.

Methodology — Socratic Elenchus Prover–Skeptic–Negative-Control–Kernel-Gate:
  - Stage 0 (Layer 0, 0 tokens): Cross-collection ChromaDB RAG retrieval across:
      * `ramanujan_primary_works_v1` (Andrews-Berndt Lost Notebook Parts I-IV +
        Campaign v2 839-page DB records)
      * `ramanujan_literature_v1` (44 curated arXiv papers across 8 pillars)
      * `rama_repo_artifacts` (v3.2 paper, BibTeX, validation certificates)
  - Stage 1 (T2 `pro` — Prover / Thesis Architect): Formulates the 10-domain
    Lean 4 formalization architecture + exact theorem spec for
    `dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean`.
  - Stage 2 (T2 `pro` — Independent Socratic Elenchus Skeptic): Cross-examines
    the thesis BEFORE coding, attacks hidden assumptions / edge cases / vacuity
    risks, and mandates concrete executable Negative Controls for every domain.
  - Stage 3 (Parallel T2 `pro` Disjoint Execution):
      * Worker A (`pro`): Implements & live-compiles `RamanujanElenchusCanon.lean`
        (standalone `Init`-only Lean 4.33.1, `MATHESIS-GATE: allow=propext`,
        universal theorems + exact canon + mandatory Negative Controls) and
        `tests/test_ramanujan_elenchus_canon.py`.
      * Worker B (`pro`): Authors `docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md`
        (complete 10-domain Lean 4 formalization roadmap, Mathlib mapping,
        M1-M12 milestones, Elenchus audit protocol, grounded in ChromaDB).
  - Stage 4 (Layer 0, 0 tokens): Deterministic verification (`mathesis_gate.py`
    LIVE footprints on ALL `Discovery` modules, `audit_lean.py`, `run_certificates.py`,
    `pytest`, `preflight_audit.py`).
  - Stage 5 (T2 `pro` — Independent Blind Elenchus Auditor + Bounded Repair):
    Audits both the Lean canon module and the Roadmap, triggers a bounded `pro`
    repair round if any defect is found, and emits the Owner's Epistemic Ledger
    `dualscale/certificates/ramanujan_elenchus_audit_ledger.json`.
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(WORKSPACES[0]) if WORKSPACES else Path.cwd()
_args = args if "args" in globals() and isinstance(args, dict) else {}
MAX_REPAIR_ROUNDS = min(max(int(_args.get("max_repair_rounds", 1)), 0), 2)

GUARDRAIL = (
    "\nMANDATORY REPO & ELENCHUS GUARDRAILS (AGENTS.md + Rules R1-R5):\n"
    "- NEVER read, glob, or dump `lean4/verify_*.lean`, `dualscale/lean/DualScale/Discovery/verify_*.lean`, "
    "`.lake/`, `inputs/`, `input/`, `docs/**/*.pdf`, `*.log`, or raw `namagiri.db` dumps.\n"
    "- NEVER run `lake build` or `lake update` (Mathlib `.lake/` is absent offline).\n"
    "- NEVER run `git commit` or `git rm`.\n"
    "- ONLY modify files strictly inside your assigned EXCLUSIVE FILE ALLOWLIST.\n"
    "- Enforce Epistemic Rules R1 (0 custom axioms), R2 (0 sorry), R3 (0 vacuity / Prop:=True / "
    "by trivial / bare by rfl tautologies / unused hypotheses), R4 (verified citations only — NEVER invent arXiv IDs!), "
    "R5 (exact arithmetic certificates).\n"
    "- At the end of EVERY turn, ALWAYS call the `finish` tool with JSON matching the requested schema.\n"
)


def _run(cmd, timeout=300, env_extra=None):
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


def _query_chroma(query: str, n: int = 4, collection: str = "all") -> list:
    venv_py = REPO_ROOT / ".venv/bin/python"
    if not venv_py.is_file():
        return [{"error": ".venv/bin/python not found"}]
    rc, out = _run(
        [str(venv_py), "src/literature/chroma_kb.py", "query", query, "--n", str(n), "--collection", collection],
        timeout=60,
    )
    if rc != 0:
        return [{"error": out[-300:]}]
    try:
        return json.loads(out)
    except Exception:
        return [{"raw": out[-300:]}]


def _chroma_stats() -> dict:
    venv_py = REPO_ROOT / ".venv/bin/python"
    if not venv_py.is_file():
        return {}
    rc, out = _run([str(venv_py), "src/literature/chroma_kb.py", "stats"], timeout=60)
    if rc != 0:
        return {"error": out[-300:]}
    try:
        return json.loads(out)
    except Exception:
        return {"raw": out[-300:]}


def _verify_all() -> dict:
    checks = {}
    rc_gate, out_gate = _run(
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
    for m in re.finditer(r"(\w+\.lean):\s*(\d+)/(\d+)\s+footprint\(s\) as declared", out_gate):
        counts[m.group(1)] = {"verified": int(m.group(2)), "declared": int(m.group(3))}
    total_live = sum(v["verified"] for v in counts.values())
    checks["mathesis_gate_discovery_live"] = {
        "ok": rc_gate == 0 and "RamanujanElenchusCanon.lean" in counts,
        "rc": rc_gate,
        "counts": counts,
        "total_live": total_live,
        "tail": out_gate[-1400:],
    }

    cmds = {
        "lean_canon_direct": (["lean", "dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean"], None),
        "audit_lean": (["python3", "dualscale/ci/audit_lean.py", "--root", "dualscale/lean/DualScale"], None),
        "mathesis_gate_strict": (
            ["python3", "tools/mathesis-gate/mathesis_gate.py", ".",
             "--lean-src", "dualscale/lean", "--exclude", "archive",
             "--exclude", "verify_", "--skip-footprints"],
            None,
        ),
        "run_certificates": (["python3", "dualscale/ci/run_certificates.py"], None),
        "verify_qseries": (["python3", "dualscale/ci/verify_qseries.py"], None),
        "pytest": (["pytest", "-q"], {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}),
    }
    for name, (cmd, env_extra) in cmds.items():
        rc, out = _run(cmd, timeout=300, env_extra=env_extra)
        checks[name] = {"ok": rc == 0, "rc": rc, "tail": out[-1200:]}

    all_ok = all(v["ok"] for v in checks.values())
    return {"all_ok": all_ok, "counts": counts, "total_live": total_live, "checks": checks}


# ---------------------------------------------------------------------------
# STAGE 0 — Cross-Collection ChromaDB RAG Grounding (0 LLM tokens)
# ---------------------------------------------------------------------------
phase("Stage 0: Cross-Collection ChromaDB RAG Grounding (Primary + Community + Repo)")
stats = _chroma_stats()
manifest = json.loads((REPO_ROOT / "docs/literature/corpus_manifest.json").read_text(encoding="utf-8"))
manifest_catalog = [
    {
        "arxiv_id": p["arxiv_id"],
        "year": str(p.get("published", ""))[:4],
        "pillar": p.get("pillar", ""),
        "title": p.get("title", ""),
        "authors": ", ".join(p.get("authors", [])[:3]),
        "url": p.get("url", ""),
    }
    for p in manifest.get("papers", [])
]

rag_topics = [
    ("partitions_congruences_rank_crank", "Ramanujan partition congruences mod 5 7 11 Dyson rank crank Rademacher formula"),
    ("rogers_ramanujan_cf", "Rogers-Ramanujan identities continued fraction R(q) Bailey lemma Kanade Russell"),
    ("mock_theta_quantum", "mock theta functions harmonic Maass forms Zwegers quantum modular forms resurgence"),
    ("eta_quotients_modular", "Dedekind eta-quotients Ono Sturm bound modular equations cusp vanishing"),
    ("one_over_pi_pf", "Ramanujan series for 1/pi Ramanujan-Sato Picard-Fuchs K3 Calabi-Yau Sym^2"),
    ("tau_lehmer_hecke", "Ramanujan tau function Delta Lehmer conjecture Hecke eigenvalues Deligne mod 691"),
    ("hcn_ramanujan_sums", "highly composite numbers Ramanujan sums c_q(n) Robin Riemann hypothesis"),
    ("lean4_formalization", "Lean 4 Mathlib formalization modular forms Fermat Last Theorem schemes OpenProver LeanDojo"),
]

rag_packets = {}
for key, q in rag_topics:
    rag_packets[key] = {
        "literature_hits": _query_chroma(q, n=3, collection="ramanujan_literature_v1"),
        "primary_hits": _query_chroma(q, n=2, collection="ramanujan_primary_works_v1"),
    }

log(
    f"ChromaDB grounded: stats={json.dumps(stats)} | "
    f"manifest_papers={len(manifest_catalog)} | rag_topics={len(rag_packets)}"
)

# Compact RAG digest for top-tier agents
rag_digest = {}
for key, val in rag_packets.items():
    rag_digest[key] = {
        "literature": [
            {
                "id": h.get("metadata", {}).get("arxiv_id"),
                "title": h.get("metadata", {}).get("title"),
                "year": h.get("metadata", {}).get("year"),
                "page": h.get("metadata", {}).get("page"),
                "excerpt": h.get("excerpt", "")[:320],
            }
            for h in val["literature_hits"]
        ],
        "primary": [
            {
                "source": h.get("metadata", {}).get("title"),
                "page": h.get("metadata", {}).get("page"),
                "excerpt": h.get("excerpt", "")[:320],
            }
            for h in val["primary_hits"]
        ],
    }

# ---------------------------------------------------------------------------
# STAGE 1 — Prover / Architect Thesis Formulation (T2 Pro)
# ---------------------------------------------------------------------------
phase("Stage 1 (Elenchus Thesis): T2 Pro Formalization Architect")

THESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "ten_domain_architecture": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "domain_id": {"type": "string"},
                    "title": {"type": "string"},
                    "ramanujan_sources": {"type": "string"},
                    "community_papers": {"type": "array", "items": {"type": "string"}},
                    "mathlib_readiness": {"type": "string"},
                    "key_theorems_and_tiers": {"type": "string"},
                    "proposed_negative_controls": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "domain_id", "title", "ramanujan_sources", "community_papers",
                    "mathlib_readiness", "key_theorems_and_tiers", "proposed_negative_controls",
                ],
            },
        },
        "canon_lean_module_spec": {"type": "string"},
        "open_risks_and_boundaries": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["ten_domain_architecture", "canon_lean_module_spec", "open_risks_and_boundaries"],
}

thesis = await agent(
    prompt=(
        "You are the Stage 1 Elenchus Prover & Chief Formalization Architect (T2 Pro).\n"
        "Using ONLY the grounded ChromaDB RAG corpus below (44 downloaded arXiv papers + Andrews-Berndt "
        "Lost Notebook Parts I-IV + Campaign v2 839-page DB + existing 338 live Lean 4.33.1 theorems), formulate:\n"
        "1. `ten_domain_architecture`: A complete 10-domain Lean 4 formalization architecture for Srinivasa Ramanujan's "
        "complete mathematical oeuvre (1911–1920 Papers, Notebooks I–III, Letters to Hardy, Lost Notebook 1988) AND "
        "its major mathematical community extensions (partitions/congruences/rank/crank/Rademacher; Rogers-Ramanujan & "
        "q-hypergeometric; continued fractions R(q); mock theta / Zwegers Maass / quantum modular forms; Dedekind eta-quotients "
        "& modular equations; 1/pi Ramanujan-Sato & Picard-Fuchs/K3/Sym^2; Ramanujan tau/Delta/Hecke/Deligne/Lehmer; "
        "multiplicative NT: Ramanujan sums c_q(n) & Highly Composite Numbers; classical analysis: Master Theorem/elliptic integrals; "
        "physics dualities K3xT2/Moonshine/Fluid-Gravity & Lean 4 neuro-symbolic Elenchus tooling).\n"
        "   - Cite ONLY verified arXiv IDs from the manifest below or Andrews-Berndt Lost Notebook Parts I-IV.\n"
        "2. `canon_lean_module_spec`: An exact, self-contained specification for a NEW live-compiled standalone "
        "Lean 4.33.1 (`Init`-only, `MATHESIS-GATE: env=none`, `MATHESIS-GATE: allow=propext`, ZERO custom axioms, "
        "ZERO `sorry`, ZERO vacuity) benchmark module `dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean` "
        "proving ~45+ genuine theorems across 8 core Ramanujan domains:\n"
        "   (1) **Euler's Partition Theorem (Odd = Distinct) UNIVERSALLY `∀ len : Nat`** via exact FPS algebra + "
        "Euler Pentagonal recurrence check + Negative Control;\n"
        "   (2) **Ramanujan Partition Congruences** `p(5n+4) ≡ 0 (mod 5)`, `p(7n+5) ≡ 0 (mod 7)`, `p(11n+6) ≡ 0 (mod 11)` "
        "(exact kernel verification + Ramanujan's `mod 5` generating identity `∑ p(5n+4) q^n = 5 η(5τ)^5/η(τ)^6` in exact "
        "truncated FPS + R1-compliant conditional all-n lift parameterized by Ramanujan's generating identity + Negative Controls);\n"
        "   (3) **Ramanujan's τ-function (`Δ(q)/q = η(τ)^24`)**: exact values `τ(1)..τ(16)`, coprime multiplicativity, "
        "Hecke prime-power identities `τ(p^2) = τ(p)^2 - p^11` (`p=2,3`) & `τ(8) = τ(2)τ(4) - 2^11 τ(2)`, Ramanujan's "
        "`τ(n) ≡ σ_11(n) (mod 691)` (`n=1..12`), Deligne squared bounds `τ(p)^2 ≤ 4 p^11` (`p ∈ {2,3,5,7,11,13}`), "
        "+ Negative Control (`τ(4) ≠ τ(2)*τ(2)` non-coprime failure!);\n"
        "   (4) **Ramanujan Sums `c_q(n)` (1918)** via exact computable Möbius/divisor sum: UNIVERSAL `∀ n, c_1(n) = 1`, "
        "UNIVERSAL `∀ p n` theorem for prime `p` (`isPrimeBool p = true` or explicit divisor-free prime predicate: "
        "`c_p(n) = p - 1` if `p ∣ n` else `-1`), exact orthogonality `∑_{n=0}^{q-1} c_q(n) = 0` witnesses + Negative Control;\n"
        "   (5) **Continued Fractions & Rogers-Ramanujan `R(q)`**: UNIVERSAL `∀ k : Nat` Euler-Wallis determinant identity "
        "`P_{k+1} Q_k - P_k Q_{k+1} = (-1)^k ∏ a_i` for arbitrary integer/rational convergents + exact truncated Rogers-Ramanujan "
        "`G(q)` and `H(q)` series = Euler products to `q^15` + Negative Control;\n"
        "   (6) **3rd-Order Mock Theta Functions (Last Letter 1920)**: exact rational/integer series `f(q)` (OEIS A000025) "
        "and `φ(q)` (OEIS A053250) matching Ramanujan's definitions + Watson/Ramanujan mock relation witness + Negative Control;\n"
        "   (7) **Highly Composite Numbers (1915) & Minimal Taxicab `1729`**: UNIVERSAL minimality proof of `1729` over ALL "
        "`n < 1729` (`1729 = 1^3+12^3 = 9^3+10^3` and `∀ n < 1729, cubeSumWays n ≤ 1` proved in kernel!) + Highly Composite "
        "Number verification `isHCN n` (`∀ m, 0 < m → m < n → numDivisors m < numDivisors n`) for `1,2,4,6,12,24,36,48,60,120` "
        "+ Negative Controls (`1728` fails, `18` fails `isHCN` since `d(12)=6=d(18)`);\n"
        "   (8) **Ramanujan's 1914 Series for `1/π`**: exact integer-squared bracket proving the `k=0,1` partial sum of "
        "`(2√2/9801) ∑ (4k)!(1103+26390k)/((k!)^4 396^{4k})` approximates `1/π` accurately (exact rational bounds matching "
        "`314159265358979/10^14 < π < 314159265358980/10^14`!) + Negative Control (perturbing `1103 → 1102` breaks the bracket).\n\n"
        f"Verified ChromaDB Corpus Manifest ({len(manifest_catalog)} papers):\n{json.dumps(manifest_catalog, indent=2)}\n\n"
        f"Cross-Collection RAG Excerpts:\n{json.dumps(rag_digest, indent=2)[:12000]}\n"
        + GUARDRAIL
    ),
    schema=THESIS_SCHEMA,
    role="Stage 1 (T2 Pro): Elenchus Thesis Architect",
    model="pro",
    type_name="research",
)
log(f"Stage 1 thesis complete: {len(thesis['ten_domain_architecture'])} domains architected.")

# ---------------------------------------------------------------------------
# STAGE 2 — Independent Socratic Elenchus Skeptic (T2 Pro, Adversarial Attack)
# ---------------------------------------------------------------------------
phase("Stage 2 (Elenchus Cross-Examination): Independent T2 Pro Skeptic")

ELENCHUS_CRITIQUE_SCHEMA = {
    "type": "object",
    "properties": {
        "elenchus_challenges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "hidden_assumption_or_flaw": {"type": "string"},
                    "required_hardening": {"type": "string"},
                    "mandatory_negative_control": {"type": "string"},
                },
                "required": ["target", "hidden_assumption_or_flaw", "required_hardening", "mandatory_negative_control"],
            },
        },
        "hardened_canon_spec": {"type": "string"},
        "mandatory_negative_controls_list": {"type": "array", "items": {"type": "string"}},
        "epistemic_boundaries_enforced": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "elenchus_challenges",
        "hardened_canon_spec",
        "mandatory_negative_controls_list",
        "epistemic_boundaries_enforced",
    ],
}

skeptic_critique = await agent(
    prompt=(
        "You are the Stage 2 Independent Socratic Elenchus Skeptic (T2 Pro).\n"
        "Your job under the **Elenchus Methodology** is to CROSS-EXAMINE and ATTACK Stage 1's thesis and Lean spec "
        "*before* a single line of Lean or Roadmap is written.\n\n"
        "Attack relentlessly:\n"
        "1. Expose any subtle scope overclaim (e.g., claiming 'full proof of Ramanujan mod 5' when only finite order or "
        "conditional lift is proved; claiming Euler odd=distinct universally without proving infinite product convergence "
        "vs. formal power series coefficient stabilization for all `N`; claiming `1/π` approximation without exact rational "
        "Archimedes/Machin witness vs. hardcoded decimal constant!).\n"
        "   - IMPORTANT for `1/π`: check whether comparing against a hardcoded rational bracket of `π` proves a genuine "
        "algebraic property of the partial sums (exact rational partial sum `S_0 = 1103/9801`, `S_1 = ...`, exact squared "
        "comparison against `1/π_hi^2 < 8 * S_1^2 < 1/π_lo^2` with explicit Tier-B π-bracket note, PLUS exact ratio/convergence "
        "rate `t_{k+1}/t_k < 1/10^7` proved universally `∀ k : Nat`!! THAT is an unconditional universal Tier A theorem!).\n"
        "2. Check computability & performance in Lean 4.33.1 `Init`-only (no Mathlib, no `Quot.sound` / `Classical.choice`):\n"
        "   - Ensure `taxicab_1729_minimal` is fast in Lean kernel (`decide` over `n < 1729` or smart pair-enumeration `a, b ≤ 12` "
        "checking `a^3 + b^3 = c^3 + d^3` with `1 ≤ a < c ≤ d < b ≤ 12` → `a^3+b^3 ≥ 1729`, which is O(12^4) / instant in kernel!).\n"
        "   - Ensure Euler's odd=distinct proof over `FPS` (`∀ len : Nat`) is genuinely clean and avoids huge term blowups.\n"
        "   - Ensure mock theta `f(q)` / `φ(q)` computation uses exact integer power series (since `1/(-q;q)_n^2` has integer "
        "coefficients via `polyInv`!) — NO floats, NO rational denominator explosions!\n"
        "   - Ensure `ramanujanSum` universal prime theorem (`∀ p n`) has a clean, crystal-clear mathematical definition of "
        "primality (`p ≥ 2 ∧ ∀ d, 1 < d → d < p → p % d ≠ 0`) so there is ZERO ambiguity or circularity!\n"
        "3. Mandate at least **8 genuine, non-vacuous Negative Controls** that MUST be kernel-proved as refutations inside "
        "`RamanujanElenchusCanon.lean`.\n\n"
        f"Stage 1 Thesis:\n{json.dumps(thesis, indent=2)[:15000]}\n"
        + GUARDRAIL
    ),
    schema=ELENCHUS_CRITIQUE_SCHEMA,
    role="Stage 2 (T2 Pro): Socratic Elenchus Skeptic",
    model="pro",
    type_name="research",
)
log(
    f"Stage 2 Elenchus cross-examination complete: {len(skeptic_critique['elenchus_challenges'])} challenges, "
    f"{len(skeptic_critique['mandatory_negative_controls_list'])} mandatory negative controls."
)

# ---------------------------------------------------------------------------
# STAGE 3 — Parallel Disjoint Execution (Worker A: Lean Canon + Worker B: Roadmap)
# ---------------------------------------------------------------------------
phase("Stage 3 (Prover Execution): Parallel Lean 4 Canon Kernel + Full Elenchus Roadmap")

WORKER_A_SCHEMA = {
    "type": "object",
    "properties": {
        "lean_file": {"type": "string"},
        "test_file": {"type": "string"},
        "theorem_count": {"type": "integer"},
        "negative_control_count": {"type": "integer"},
        "universal_theorem_names": {"type": "array", "items": {"type": "string"}},
        "negative_control_names": {"type": "array", "items": {"type": "string"}},
        "lean_compiled_ok": {"type": "boolean"},
        "mathesis_gate_ok": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": [
        "lean_file", "test_file", "theorem_count", "negative_control_count",
        "universal_theorem_names", "negative_control_names",
        "lean_compiled_ok", "mathesis_gate_ok", "summary",
    ],
}

WORKER_B_SCHEMA = {
    "type": "object",
    "properties": {
        "roadmap_file": {"type": "string"},
        "domains_covered": {"type": "integer"},
        "milestones_defined": {"type": "integer"},
        "papers_referenced_count": {"type": "integer"},
        "summary": {"type": "string"},
    },
    "required": ["roadmap_file", "domains_covered", "milestones_defined", "papers_referenced_count", "summary"],
}

worker_a = agent(
    prompt=(
        "You are Worker A (Tier T2 Pro — Lean 4.33.1 Elenchus Canon Kernel Prover).\n"
        "EXCLUSIVE FILE ALLOWLIST:\n"
        "  - dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean\n"
        "  - tests/test_ramanujan_elenchus_canon.py\n\n"
        "Create `dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean` following EVERY requirement from the "
        "Stage 2 Elenchus-Hardened Spec below:\n"
        "- Standalone `Init`-only Lean 4.33.1 (ZERO `import Mathlib.*`).\n"
        "- Top-of-file Mathesis-Gate contract:\n"
        "    -- MATHESIS-GATE: env=none\n"
        "    -- MATHESIS-GATE: allow=propext\n"
        "- ZERO `axiom`, ZERO `sorry`, ZERO `: Prop := True`, ZERO `:= by trivial`, ZERO bare `:= by rfl` tautologies.\n"
        "- Note on axioms: avoid `Quot.sound` and `Classical.choice` (use explicit structural proofs like in "
        "`AllNAndPropositionsVerified.lean` — you may inspect lines 1–60 of `AllNAndPropositionsVerified.lean` for conventions "
        "and keep `namespace DualScale.RamanujanElenchusCanon`).\n"
        "- Cover ALL 8 Ramanujan domains with genuine universal (`∀`) theorems, exact canonical theorems, AND at least "
        "**8 explicit kernel-verified Negative Controls** (named `neg_ctrl_*` so they are auditable!).\n"
        "- Emit `#print axioms <thm>` at the bottom for EVERY exported theorem (positive AND `neg_ctrl_*`).\n"
        "- Create `tests/test_ramanujan_elenchus_canon.py` verifying:\n"
        "  1. Cross-consistency of key computed values (`p(n)`, `τ(n)`, `c_q(n)`, Rogers-Ramanujan `G(q), H(q)`, "
        "3rd-order mock theta `f(q), φ(q)`, Highly Composite Numbers, `1729` minimality, `1/π` exact partial sums) in Python.\n"
        "  2. That `RamanujanElenchusCanon.lean` has `MATHESIS-GATE: allow=propext`, >= 8 `neg_ctrl_` theorems, "
        "0 custom axioms, 0 `sorry`, and passes `mathesis_gate.py` single-file static check.\n"
        "- Compile & verify LIVE before finishing:\n"
        "  * `lean dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean`\n"
        "  * `python3 tools/mathesis-gate/mathesis_gate.py dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean`\n"
        "  * `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_ramanujan_elenchus_canon.py -q`\n\n"
        f"Stage 2 Hardened Canon Spec:\n{skeptic_critique['hardened_canon_spec']}\n\n"
        f"Mandatory Negative Controls:\n{json.dumps(skeptic_critique['mandatory_negative_controls_list'], indent=2)}\n\n"
        f"Epistemic Boundaries Enforced:\n{json.dumps(skeptic_critique['epistemic_boundaries_enforced'], indent=2)}\n"
        + GUARDRAIL
    ),
    schema=WORKER_A_SCHEMA,
    role="Worker A (T2 Pro): RamanujanElenchusCanon.lean",
    model="pro",
)

worker_b = agent(
    prompt=(
        "You are Worker B (Tier T2 Pro — Full Lean 4 Formalization Roadmap & Elenchus Blueprint Architect).\n"
        "EXCLUSIVE FILE ALLOWLIST:\n"
        "  - docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md\n\n"
        "Author a comprehensive, authoritative, publication-grade engineering & mathematical roadmap at "
        "`docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md` proposing the **Full Lean 4 Formalization of Srinivasa Ramanujan's "
        "Complete Works & Related Mathematical Community Literature under the Elenchus Methodology**.\n\n"
        "Required structure and rigor:\n"
        "1. **Executive Overview & Current Verified Baseline (v3.2 → v4.0):**\n"
        "   - Grounded in the multi-collection ChromaDB vector KB (`ramanujan_primary_works_v1`: Andrews-Berndt Lost Notebook "
        "Parts I–IV + Campaign v2 839-page DB; `ramanujan_literature_v1`: 44 curated arXiv papers across 8 pillars; "
        "`rama_repo_artifacts`), plus the existing 338 live Lean 4.33.1 kernel theorems (`CampaignV2Verified.lean` + "
        "`AllNAndPropositionsVerified.lean`) and the new `RamanujanElenchusCanon.lean` benchmark module.\n"
        "2. **The Socratic Elenchus Formalization & Audit Methodology (5-Stage Protocol):**\n"
        "   - Detailed specification of Stage 0 (Zero-Token ChromaDB RAG Grounding), Stage 1 (Prover Thesis Formulation), "
        "Stage 2 (Independent Skeptic Cross-Examination), Stage 3 (Negative Control Suite — mandatory falsification witnesses), "
        "Stage 4 (Tier-A Lean 4 Kernel + `mathesis-gate` `#print axioms` verification), and Stage 5 (Owner's Epistemic Ledger).\n"
        "   - Include a clean Mermaid flowchart (`flowchart TD`, quoting labels with special chars!) showing the prover-skeptic "
        "dialectic, negative-control kill switch, bounded repair loop, and model-tier routing (Layer 0 / T0 / T1 / T2).\n"
        "3. **Complete 10-Domain Lean 4 Formalization Architecture (`RamanujanLean/` + `DualScale/`):**\n"
        "   - Detailed dependency graph (Mermaid `flowchart LR`) and exact Lean 4 namespace/module hierarchy covering ALL 10 domains "
        "of Ramanujan's works (1911–1920 Papers, Notebooks I–III, Letters to Hardy, Lost Notebook 1988) and community breakthroughs "
        "(Hardy–Ramanujan–Rademacher, Dyson–Andrews–Garvan rank/crank, Ahlgren–Ono congruences, Zwegers harmonic Maass forms, "
        "Zagier quantum modular forms, Griffin–Ono–Warnaar & Kanade–Russell Rogers–Ramanujan, Guillera–Almkvist–Baruah–Berndt–Chan "
        "$1/\\pi$ & Ramanujan–Sato series, Doran $\\operatorname{Sym}^2(L_2)$, Deligne–Serre–Balakrishnan–Ono $\\tau(n)$/Lehmer, "
        "Nicolas–Sondow HCN/RH, Dabholkar–Murthy–Zagier / EOT / Gannon / Umbral Moonshine, BHMR/Tao/MSS boundaries).\n"
        "   - For EVERY domain: primary sources, verified arXiv papers (ONLY from the manifest below — include clickable arXiv URLs!), "
        "current Mathlib 4 API readiness vs. exact missing Mathlib lemmas (citing Best–Birkbeck–Brasca 2024 & Buzzard–Hughes–Lau 2021), "
        "concrete Lean 4 theorem signatures (distinguishing Tier A vs. Tier B/L vs. Tier C vs. Tier X), and mandatory Elenchus Negative Controls!\n"
        "4. **Phased 12-Milestone Implementation Roadmap (M1–M12, 4 Horizons):**\n"
        "   - Horizon 1 (Foundation & Standalone Kernel Canon — NOW / v3.3): Init-only algebraic & arithmetic theorems + negative controls.\n"
        "   - Horizon 2 (Mathlib 4 Analytic Modular Forms & $q$-Series Core — v4.0): Connecting to `Mathlib.NumberTheory.ModularForms.*`, "
        "`UpperHalfPlane`, Dedekind $\\eta$, Ono Thm 1.64–1.65, Sturm bound, Jacobi Triple Product, Euler/Pentagonal, Rogers–Ramanujan.\n"
        "   - Horizon 3 (Harmonic Maass Forms, Rank/Crank, $1/\\pi$ & Hecke Theory — v4.5): Zwegers Appell–Lerch completion, "
        "Rademacher circle method (Pribitkin–Williams short proof!), Ramanujan–Sato $1/\\pi$, Hecke eigenform theory for $\\Delta$, "
        "$\\tau(n) \\equiv \\sigma_{11}(n) \\pmod{691}$, HCN/Robin criteria.\n"
        "   - Horizon 4 (Community Research Frontiers & Physics Dualities — v5.0): Quantum modular forms, Kanade–Russell identities, "
        "Picard–Fuchs $\\operatorname{Sym}^2(L_2)$ differential operators, Mathieu/Umbral Moonshine characters, conditional PDE boundaries.\n"
        "5. **Reproducible CLI & Workflow Operations Guide:**\n"
        "   - Exact commands to query ChromaDB (`src/literature/chroma_kb.py`), invoke `ramanujan_elenchus_formalization_workflow.py`, "
        "run live `mathesis_gate.py`, and audit the Owner's Epistemic Ledger (`ramanujan_elenchus_audit_ledger.json`).\n"
        "6. **Complete Verified Bibliography Table** referencing ALL 44 arXiv papers (with exact URLs and arXiv compliance note) "
        "+ Andrews–Berndt Lost Notebook Parts I–IV.\n\n"
        f"ChromaDB Live Stats:\n{json.dumps(stats, indent=2)}\n\n"
        f"Stage 1 10-Domain Architecture:\n{json.dumps(thesis['ten_domain_architecture'], indent=2)[:14000]}\n\n"
        f"Stage 2 Elenchus Challenges & Boundaries:\n{json.dumps({'challenges': skeptic_critique['elenchus_challenges'], 'boundaries': skeptic_critique['epistemic_boundaries_enforced']}, indent=2)[:10000]}\n\n"
        f"Verified 44-Paper Manifest (cite ONLY these exact IDs/URLs):\n{json.dumps(manifest_catalog, indent=2)}\n"
        + GUARDRAIL
    ),
    schema=WORKER_B_SCHEMA,
    role="Worker B (T2 Pro): Full Lean 4 Elenchus Roadmap",
    model="pro",
)

res_a, res_b = await parallel([worker_a, worker_b], lambda a: a)
log(
    f"Stage 3 done | Worker A: {res_a['theorem_count']} thms ({res_a['negative_control_count']} neg ctrls, "
    f"lean={res_a['lean_compiled_ok']}, gate={res_a['mathesis_gate_ok']}) | "
    f"Worker B: {res_b['domains_covered']} domains, {res_b['milestones_defined']} milestones"
)

# ---------------------------------------------------------------------------
# STAGE 4 — Zero-Token Deterministic Verification & Live Kernel Footprints
# ---------------------------------------------------------------------------
phase("Stage 4 (Kernel Gate): Zero-Token Live Footprints & Regression Suite")
verif = _verify_all()
log(
    f"Stage 4 all_ok={verif['all_ok']} | total_live_theorems={verif['total_live']} | "
    f"counts={verif['counts']} | failed={[k for k, v in verif['checks'].items() if not v['ok']]}"
)

# ---------------------------------------------------------------------------
# STAGE 5 — Independent Blind Elenchus Audit Agent (+ Bounded Repair + Ledger)
# ---------------------------------------------------------------------------
phase("Stage 5 (Elenchus Audit): Independent Blind Skeptic & Owner's Ledger")

AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "overall_verdict": {"type": "string", "enum": ["APPROVED", "NEEDS_REPAIR"]},
        "elenchus_audit_scores": {
            "type": "object",
            "properties": {
                "r1_zero_custom_axioms": {"type": "boolean"},
                "r2_zero_sorry": {"type": "boolean"},
                "r3_anti_vacuity_and_non_tautology": {"type": "boolean"},
                "r4_grounded_citations_no_hallucinations": {"type": "boolean"},
                "r5_exact_arithmetic_and_negative_controls": {"type": "boolean"},
                "elenchus_prover_skeptic_compliance": {"type": "boolean"},
            },
            "required": [
                "r1_zero_custom_axioms", "r2_zero_sorry", "r3_anti_vacuity_and_non_tautology",
                "r4_grounded_citations_no_hallucinations", "r5_exact_arithmetic_and_negative_controls",
                "elenchus_prover_skeptic_compliance",
            ],
        },
        "audited_theorem_domains": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "positive_theorems": {"type": "array", "items": {"type": "string"}},
                    "negative_controls": {"type": "array", "items": {"type": "string"}},
                    "epistemic_tier": {"type": "string", "enum": ["A", "B", "L", "C", "X"]},
                    "audit_verdict": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["domain", "positive_theorems", "negative_controls", "epistemic_tier", "audit_verdict", "notes"],
            },
        },
        "defects_found": {"type": "array", "items": {"type": "string"}},
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
        "executive_audit_summary": {"type": "string"},
    },
    "required": [
        "approved", "overall_verdict", "elenchus_audit_scores",
        "audited_theorem_domains", "defects_found", "repair_instructions",
        "executive_audit_summary",
    ],
}

auditor = agent(
    prompt=(
        "You are the Stage 5 Independent Blind Elenchus Auditor (T2 Pro).\n"
        "You did NOT write `RamanujanElenchusCanon.lean` or `docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md`.\n"
        "Apply the Socratic Elenchus methodology ruthlessly:\n"
        "1. Read `dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean` directly and inspect EVERY theorem "
        "statement and proof (checking for disguised vacuity, weak definitions, fake universal quantifiers, "
        "missing edge cases, or trivial negative controls).\n"
        "2. Inspect `docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md` to verify every claim matches verified repo facts, "
        "epistemic tiers are honest (no Tier C/X inflated to Tier A), and arXiv citations match the manifest.\n"
        "3. Verify Stage 4 deterministic checks (`mathesis_gate_discovery_live`, `lean_canon_direct`, `audit_lean`, "
        "`run_certificates`, `verify_qseries`, `pytest`).\n"
        "Reject (`approved: false`, `overall_verdict: 'NEEDS_REPAIR'`) if ANY genuine mathematical, formalization, "
        "negative-control, or citation defect exists.\n"
        + GUARDRAIL
    ),
    role="Stage 5 (T2 Pro): Independent Blind Elenchus Auditor",
    model="pro",
    type_name="research",
)

audit = None
for round_idx in range(MAX_REPAIR_ROUNDS + 1):
    compact_checks = {
        k: {"ok": v["ok"], "rc": v["rc"], "tail": "" if v["ok"] else v["tail"]}
        for k, v in verif["checks"].items()
    }
    audit = await auditor(
        f"Elenchus Independent Audit Round {round_idx}:\n"
        f"Worker A Summary:\n{json.dumps(res_a, indent=2)}\n\n"
        f"Worker B Summary:\n{json.dumps(res_b, indent=2)}\n\n"
        f"Stage 4 Deterministic Verification (all_ok={verif['all_ok']}, total_live={verif['total_live']}):\n"
        f"{json.dumps({'counts': verif['counts'], 'checks': compact_checks}, indent=2)}\n\n"
        f"Verified Manifest IDs (for citation cross-check):\n{json.dumps([p['arxiv_id'] for p in manifest_catalog])}\n",
        schema=AUDIT_SCHEMA,
    )
    log(
        f"Stage 5 Elenchus Auditor round {round_idx}: approved={audit['approved']} | "
        f"verdict={audit['overall_verdict']} | defects={len(audit['defects_found'])}"
    )

    if audit["approved"] and verif["all_ok"]:
        break
    if round_idx < MAX_REPAIR_ROUNDS:
        phase(f"Stage 5.{round_idx + 1}: Bounded Elenchus Repair Round (T2 Pro)")
        failed = {k: v for k, v in verif["checks"].items() if not v["ok"]}
        repair_res = await agent(
            prompt=(
                "Fix ALL defects raised by the Independent Blind Elenchus Auditor and any failed Stage 4 checks.\n"
                "EXCLUSIVE FILE ALLOWLIST:\n"
                "  - dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean\n"
                "  - tests/test_ramanujan_elenchus_canon.py\n"
                "  - docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md\n\n"
                f"Defects:\n{json.dumps(audit['defects_found'], indent=2)}\n\n"
                f"Repair Instructions:\n{json.dumps(audit['repair_instructions'], indent=2)}\n\n"
                f"Failed Checks:\n{json.dumps(failed, indent=2)}\n\n"
                "Verify live with `lean`, `mathesis_gate.py`, and `pytest` before finishing.\n"
                + GUARDRAIL
            ),
            schema={"type": "object", "properties": {"files_modified": {"type": "array", "items": {"type": "string"}}, "summary": {"type": "string"}}, "required": ["files_modified", "summary"]},
            role=f"Elenchus Bounded Repair #{round_idx + 1} (T2 Pro)",
            model="pro",
        )
        log(f"Repair round {round_idx + 1} complete: {repair_res['files_modified']}")
        verif = _verify_all()
        log(f"Post-repair Stage 4 all_ok={verif['all_ok']} | total_live={verif['total_live']}")

del auditor

# Emit Owner's Epistemic Ledger Certificate
ledger_path = REPO_ROOT / "dualscale/certificates/ramanujan_elenchus_audit_ledger.json"
ledger_payload = {
    "workflow": "ramanujan_elenchus_formalization_workflow",
    "methodology": "Socratic Elenchus (Prover -> Independent Skeptic -> Negative Controls -> Lean 4.33.1 Kernel & Mathesis-Gate -> Blind Auditor)",
    "approved": bool(audit["approved"] and verif["all_ok"]),
    "overall_verdict": audit["overall_verdict"],
    "chromadb_corpus": {
        "collections": stats,
        "arxiv_papers_total": len(manifest_catalog),
        "andrews_berndt_lost_notebook_volumes": 4,
        "campaign_v2_manuscript_pages": 839,
    },
    "live_lean_kernel_summary": {
        "modules": verif["counts"],
        "total_live_kernel_theorems": verif["total_live"],
        "axioms_subset": ["propext"],
        "canon_negative_controls_count": res_a["negative_control_count"],
    },
    "roadmap_artifact": "docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md",
    "canon_lean_artifact": "dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean",
    "elenchus_audit_scores": audit["elenchus_audit_scores"],
    "audited_theorem_domains": audit["audited_theorem_domains"],
    "deterministic_checks": {k: {"ok": v["ok"], "rc": v["rc"]} for k, v in verif["checks"].items()},
    "defects_found": audit["defects_found"],
    "executive_audit_summary": audit["executive_audit_summary"],
}
ledger_path.write_text(json.dumps(ledger_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
log(f"Wrote Owner's Elenchus Audit Ledger to {ledger_path} (approved={ledger_payload['approved']})")

# Fast incremental ChromaDB update so the new Roadmap & Ledger are indexed into rama_repo_artifacts
venv_py = REPO_ROOT / ".venv/bin/python"
if venv_py.is_file():
    rc_ch, out_ch = _run(
        [str(venv_py), "src/literature/chroma_kb.py", "ingest", "--manifest", "docs/literature/corpus_manifest.json", "--no-primary"],
        timeout=120,
    )
    log(f"Incremental ChromaDB repo refresh rc={rc_ch}")

print(json.dumps({
    "approved": ledger_payload["approved"],
    "overall_verdict": ledger_payload["overall_verdict"],
    "live_lean_kernel_summary": ledger_payload["live_lean_kernel_summary"],
    "elenchus_audit_scores": ledger_payload["elenchus_audit_scores"],
    "defects_found": ledger_payload["defects_found"],
}, indent=2, ensure_ascii=False))

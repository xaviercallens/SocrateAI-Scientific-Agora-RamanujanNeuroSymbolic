# DualScale / Ramanujan Neuro-Symbolic Mathematics
## Improvement Plan: From Position Paper to Tier-A Rigor

**Version:** 1.0
**Scope:** Turns the five Tier-C conjectures in *Ramanujan Neuro-Symbolic
Mathematics v2* into a pipeline that can only produce Tier-A claims by
construction — no axioms, no vacuous goals, exact-arithmetic certificates,
CI-enforced.

**Design constraint driving this whole plan:** every task below must be
executable by a **low-tier model** (a fast, cheap LLM agent with weak
mathematical judgment — call it T0) without that model needing to exercise
mathematical taste. This is achieved by making tasks *mechanical*: narrow
scope, explicit inputs, and a Definition of Done that a script — not a human,
not a smarter model — can check automatically. Anywhere real mathematical
judgment is required, the task is explicitly routed to T1/T2 instead, and
the T0 task is redefined as "prepare inputs for T1/T2" or "verify T1/T2's
output against a checker."

---

## 1. Guiding Principles (recap + hardening)

1. **The checker is the boss, not the model.** No task's Definition of Done
   may read "looks correct." It must read "command X exits 0" or "value
   matches literature constant Y to within tolerance Z."
2. **Tier discipline is enforced in CI, not in prose.** A GitHub Action
   rejects any PR that introduces an `axiom`, a `sorry`-free theorem whose
   statement type-checks as `True` or `Prop` with no discriminating content,
   or an uncited Tier-B claim.
3. **Small, reversible, atomic tasks.** Every task changes one file or one
   well-defined unit. Low-tier models fail on multi-file, multi-step,
   judgment-heavy tasks; they succeed on "fill in this one definition
   against this one spec."
4. **Literature values are locked before code is written.** A task that
   needs a citation's numeric value pulls it from a pinned source file
   (`refs/values.json`), never from the model's memory.
5. **Every artifact is falsifiable.** Each milestone (M1–M5, per the paper)
   ends in a PASS/FAIL certificate file, not a narrative conclusion.

---

## 2. Repository Architecture

Move from "three loosely-related repos" to a **monorepo with enforced
boundaries**, so a low-tier model can be pointed at one subfolder and
cannot accidentally touch another workstream's invariants.

```
dualscale/
├── lean/                        # Formal core (Lean 4 + mathlib4)
│   ├── DualScale/
│   │   ├── NS/                  # M1, M5: Hydrodynamic limits
│   │   ├── SpectralGap/         # M2: Ramanujan graphs
│   │   ├── CFM/                 # M3: Vortex direction / elliptic integrals
│   │   ├── Phase/               # Singular set / continued fractions
│   │   └── K3Lock/              # M4: Picard-Fuchs Sym^2 lock
│   ├── lakefile.lean
│   └── lean-toolchain
├── certificates/                # M2, M4, M5: exact-arithmetic PASS/FAIL
│   ├── schema/certificate.schema.json
│   ├── moduli_map/              # K3 vs elliptic-curve moduli checks
│   ├── spectral/                # Ramanujan-graph eigenvalue checks
│   └── ledger.csv               # append-only, one row per certificate
├── refs/                        # Locked literature values (Tier B inputs)
│   ├── values.json              # {key, value, source_bibkey, page, retrieved_by}
│   └── bib/dualscale.bib
├── numerics/                    # SageMath / PARI-GP scripts feeding certificates
├── ci/
│   ├── audit_lean.py            # rejects axioms / vacuous goals
│   ├── audit_citations.py       # rejects uncited Tier-B claims
│   └── run_certificates.py      # replays certificates/, checks ledger
├── paper/                       # LaTeX source, one .tex per milestone status
└── AGENTS.md                    # task-card format + model-tier routing table
```

**Why monorepo:** cross-references between Lean targets, certificates, and
the paper are exactly the failure mode that caused v1's vacuous theorems and
inconsistent claims (per the Errata). A single CI pipeline over one repo can
refuse to merge a paper claim that isn't backed by a certificate or a Lean
target in the same PR.

### CI Gate (conceptual)

```yaml
on: [pull_request]
jobs:
  audit:
    steps:
      - run: lake build                          # Lean must compile
      - run: python ci/audit_lean.py              # no axiom; no `:= by trivial`
                                                    #   on non-Prop-trivial goals;
                                                    #   sorry count reported, not hidden
      - run: python ci/audit_citations.py          # every \tierB claim in paper/
                                                    #   has a \cite{} resolving in dualscale.bib
      - run: python ci/run_certificates.py          # replays certificates/, diffs
                                                    #   against certificates/ledger.csv
```

Any PR failing a step is blocked, full stop — including PRs authored by
Claude or any other model.

---

## 3. External Repos and Tools to Leverage

Do not reimplement infrastructure that already exists and is trusted by the
formal-math community. Pin versions; don't chase `main`.

| Need | Repo / Tool | Use |
|---|---|---|
| Lean 4 core math library (elliptic curves, modular arithmetic, number theory) | [`leanprover-community/mathlib4`](https://github.com/leanprover-community/mathlib4) | Formal target definitions should reuse mathlib4 structures instead of ad hoc stubs (`Rat`, `ModularForm`, etc. exist there). |
| Searching mathlib4 for existing lemmas before writing new ones | [`leanprover-community/LeanSearch`](https://github.com/leanprover-community/leansearch) or the Loogle web tool | T0 task: "does mathlib4 already have X" — mechanical search, no judgment needed. |
| Exact rational / algebraic arithmetic for certificates (Rule R5) | [`sagemath/sage`](https://github.com/sagemath/sage) or [PARI/GP](https://pari.math.u-bordeaux.fr/) (`gp` CLI) | Numerics scripts in `numerics/` compute moduli maps and spectral data in exact arithmetic, exporting JSON that `certificates/` consumes. |
| Ramanujan-graph / spectral-gap computation | [`networkx/networkx`](https://github.com/networkx/networkx) (adjacency spectra) + exact eigenvalue check via Sage/PARI for the certificate step (floating point alone is not R5-compliant) | M2 certificates. |
| Modular forms / L-function reference data (to populate `refs/values.json` instead of trusting model memory) | [LMFDB](https://www.lmfdb.org) (data via its [GitHub org](https://github.com/LMFDB)) | Pull $\tau(p)$ values, elliptic curve conductors, etc. as pinned JSON, with page/URL provenance. |
| Calabi–Yau / K3 moduli and Picard–Fuchs computation | [`LiamMcAllisterGroup/cytools`](https://github.com/LiamMcAllisterGroup/cytools) | Candidate source for automating parts of the K3-vs-elliptic-curve moduli map (M4), rather than hand-deriving. |
| 3-manifold / quantum invariant cross-checks (for the homological-blocks anchor, §3.5 of the paper) | [`3-manifolds/SnapPy`](https://github.com/3-manifolds/SnapPy) | Optional, only if M4 is extended toward the GPPV homological-blocks direction. |
| Continuous integration for Lean | [`leanprover/lean4-cli`](https://github.com/leanprover/lean4-cli) actions, or plain `lake build` in GitHub Actions | `ci/` folder above. |
| Bibliography management / citation resolution | [`citation-style-language/styles`](https://github.com/citation-style-language) + `biblatex` | `ci/audit_citations.py` parses `.bib` keys, not prose. |

**Rule:** any of the above that a task depends on must be pinned to a commit
hash in `flake.lock` / `requirements.txt` / `lakefile.lean`, so a low-tier
model re-running a task later gets identical behavior.

---

## 4. Model-Tier Routing

| Tier | Capability assumed | Assign these task types |
|---|---|---|
| **T0** (low-tier) | Follows an explicit spec; cannot judge mathematical correctness; can run commands and read pass/fail output | Scaffolding, type signatures with no proof content, data entry into `refs/values.json` from a *quoted* source, running existing scripts, formatting, filling in `certificates/` templates whose logic already exists, chasing CI failures back to a specific line |
| **T1** | Can write straightforward Lean proofs from a stated lemma, can write correct Sage/PARI scripts from a spec | Proving the "easy half" of formalization tasks (definitions that unfold routinely), writing new certificate-generating numerics scripts |
| **T2** | Can make genuine mathematical judgment calls: is this conjecture even formalizable as stated, does this derivation actually establish the claimed identity | Anything that could change a Tier-C conjecture's *statement*, deciding whether a falsification result is genuine or a bug, writing the mathematical content of Milestone M5's conditional theorem |

The task cards below are written **for T0**, with an explicit "if this
requires judgment, stop and escalate to T1/T2" clause baked into each one —
this is itself the safety mechanism: a T0 model is expected to recognize
"I cannot mechanically check this" and hand off, not guess.

---

## 5. Task Cards

Each card is atomic. Format: **Goal / Inputs / Steps / Definition of Done /
Escalation trigger**.

### Workstream M1 — Formalize statements (Hypothesis U family)

**Task M1.1 — Scaffold `DualScale/NS/Basic.lean`**
- *Goal:* Create the file with `namespace DualScale.NS`, importing
  `Mathlib.Data.Rat.Basic` and `Mathlib.Analysis.SpecialFunctions.Pow.Real`
  only (no other imports).
- *Steps:* 1) `lake new` file at the given path if absent. 2) Add the
  namespace and imports. 3) Add `def alphaPrime : ℚ := 1 / 100`. 4) Run
  `lake build`.
- *Definition of Done:* `lake build` exits 0. `git diff` touches only the
  one file. No `axiom`, no `sorry` (there is no theorem yet, so none is
  expected).
- *Escalation trigger:* none — this task has no judgment content.

**Task M1.2 — Type the enstrophy-density definition (signature only)**
- *Goal:* Add `def enstrophyDensity (a : ℚ) (t : ℝ) : ℝ := sorry` — i.e. the
  **signature** is fixed, the **body** is explicitly left as `sorry` and
  tracked as OPEN.
- *Inputs:* the exact signature is specified in
  `paper/targets/M1_spec.md` (written once by T2, then frozen).
- *Steps:* Copy the signature verbatim from `M1_spec.md`. Do not alter
  argument types.
- *Definition of Done:* `lake build` exits 0; `python ci/audit_lean.py`
  reports exactly one new open `sorry` at this definition and zero new
  axioms; PR description links `M1_spec.md` line number as source of the
  signature.
- *Escalation trigger:* if `M1_spec.md` doesn't exist yet or is ambiguous
  about a type, stop and escalate to T2 — do not guess a type.

**Task M1.3 — State `hypothesisU_uniform_bound` with `sorry`**
- *Goal:* Transcribe the theorem statement from the paper (Section 6,
  Conjecture 3.1 in v2) into Lean syntax, proof body `sorry`.
- *Definition of Done:* Statement type-checks; `ci/audit_lean.py` confirms
  the statement is **not** of the form `True` or a tautology (script checks
  the elaborated type isn't defeq to `True`); exactly one `sorry`.
- *Escalation trigger:* if transcribing the English statement into Lean
  requires choosing between two non-equivalent formalizations, stop and
  escalate to T2 with both candidate statements listed.

**Task M1.4 — CI script: reject vacuous goals**
- *Goal:* Write `ci/audit_lean.py` that (a) runs `lake env lean --run` on
  changed files, (b) for every `theorem`/`lemma`, extracts the elaborated
  type via `#print` output, (c) fails if the type is `True` or unifies with
  `True` with no other content, (d) fails if any `axiom` keyword appears,
  (e) counts and reports `sorry`.
- *Definition of Done:* Running the script against the withdrawn v1
  listings (kept in `paper/errata/v1_lean_listings.lean` for regression
  testing) produces FAIL for all five; running it against `M1.1`–`M1.3`
  output produces PASS-with-open-sorry.
- *Escalation trigger:* none for the mechanical parts; if the "unifies with
  True" check needs to handle a tricky edge case (e.g. a theorem that's
  trivially true but non-vacuously stated), escalate to T1.

### Workstream M2 — Spectral certificates (Ramanujan graphs)

**Task M2.1 — Populate `refs/values.json` with Deligne bound test values**
- *Goal:* Add entries for $\tau(p)$ at $p \in \{2,3,5\}$ with exact integer
  values, sourced from LMFDB, with URL and retrieval date.
- *Steps:* Fetch from `https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/1/12/a/a/`
  (weight-12 level-1 form) or equivalent; record exact values only, no
  rounding.
- *Definition of Done:* JSON validates against `refs/schema/values.schema.json`;
  each entry has non-null `source_url`; `git diff` touches only
  `refs/values.json`.
- *Escalation trigger:* if LMFDB's page structure has changed and the value
  can't be located mechanically, stop and escalate to T1.

**Task M2.2 — Build triad-interaction graph and export adjacency spectrum**
- *Goal:* Run the (already-specified, T1-authored) script
  `numerics/spectral/build_triad_graph.sage` for $p \in \{2,3,5\}$ and save
  raw eigenvalues to `certificates/spectral/p{p}_raw.json`.
- *Definition of Done:* File exists, is valid JSON, contains a list of
  algebraic numbers in Sage's exact representation (not floats); `sage -c`
  invocation exits 0.
- *Escalation trigger:* if the script errors, capture the traceback verbatim
  in the PR and escalate to T1 — do not attempt to fix Sage code.

**Task M2.3 — Certificate check against Alon–Boppana window**
- *Goal:* Run `ci/run_certificates.py --target spectral/p{p}` which compares
  `p{p}_raw.json` eigenvalues against $2\sqrt{k-1}$ (computed exactly where
  possible, else to a locked precision of 50 digits) and writes
  `certificates/spectral/p{p}_certificate.json` with a `PASS`/`FAIL` verdict
  and the actual numeric margin.
- *Definition of Done:* certificate file has `"verdict"` field equal to
  `"PASS"` or `"FAIL"` (both are valid outcomes — a FAIL is a successful,
  informative task, not an error); the same run is appended as a new row to
  `certificates/ledger.csv` with timestamp and git commit hash.
- *Escalation trigger:* if the verdict is FAIL, this is a genuine result —
  flag it in the PR body as "Conjecture 2 (spectral gap) certified FAIL at
  p={p}" and escalate to T2 to update the paper's conjecture status. Do not
  silently drop a FAIL.

### Workstream M3 — CFM / elliptic-integral identity

**Task M3.1 — Extract CF(M) criterion constants into `refs/values.json`**
- *Goal:* Same pattern as M2.1, sourcing the Constantin–Fefferman (1993) and
  CFM (1996) papers' stated constants (page-cited, exact fractions where the
  paper gives them, else stated as "not exact in source" explicitly).
- *Definition of Done:* Same schema check as M2.1; additionally, any value
  the source paper states only as an inequality (not an exact constant) must
  be recorded with `"exact": false` — never silently converted to a point
  value.
- *Escalation trigger:* if a constant's derivation in the source paper spans
  multiple lemmas and isn't stated as a single number, escalate to T2 rather
  than reading off an approximation.

**Task M3.2 — Scaffold the elliptic-angle identity as an open Lean target**
- Same pattern as M1.2/M1.3, targeting `DualScale/CFM/Basic.lean`.
- *Definition of Done:* identical structure to M1.3's DoD.

### Workstream M4 — K3 moduli-map certificate (S₁₂ reclassification)

**Task M4.1 — Re-run the existing moduli-map checker for S₁₂**
- *Goal:* Invoke `check_C3b_moduli_map.py` (already exists per program
  history) with the S₁₂ sequence against both the K3 family and the
  elliptic-curve background, in exact rational arithmetic.
- *Definition of Done:* Two certificate files produced
  (`certificates/moduli_map/S12_vs_K3.json`,
  `certificates/moduli_map/S12_vs_elliptic.json`), each with a `PASS`/`FAIL`
  verdict, appended to the ledger.
- *Escalation trigger:* if the script requires a parameter (e.g. a
  precision cutoff or candidate embedding) not already pinned in a config
  file, stop and escalate to T1 rather than choosing a value.

**Task M4.2 — Update the paper's provisional classification**
- *Goal:* Purely mechanical text edit: if M4.1 produced a clean PASS/FAIL
  split (one PASS, one FAIL), update `paper/*.tex` Section on K3 geometry to
  change "provisional" to "certified" and cite the certificate file by path
  and ledger row number.
- *Definition of Done:* `ci/audit_citations.py` passes; the sentence
  changed is exactly the classification sentence, nothing else in the
  paper changes in this PR.
- *Escalation trigger:* if the two certificates disagree in a way that
  doesn't cleanly decide the classification (e.g. both PASS, or both FAIL),
  stop — this is a judgment call for T2, not a T0 text edit.

### Workstream M5 — Conditional theorem (Hypothesis U ⇒ uniform smoothness)

This entire milestone is **T2-only** for its mathematical content. T0's role
is limited to:

**Task M5.1 — Dependency-graph audit**
- *Goal:* Once T2 produces a candidate proof of the conditional theorem,
  run `lake build` and `#print axioms DualScale.NS.conditional_regularity`
  and paste the raw output into the PR.
- *Definition of Done:* Output captured verbatim; `ci/audit_lean.py`
  confirms zero axioms and zero `sorry` in the dependency cone (this is a
  mechanical graph traversal, well within T0's ability).
- *Escalation trigger:* if `#print axioms` lists anything beyond
  `[propext, Classical.choice, Quot.sound]` (mathlib4's standard trio), flag
  immediately — a low-tier model does not need to know why that's
  suspicious, only that the ledger's "acceptable axioms" list
  (`ci/acceptable_axioms.txt`) is the sole source of truth to diff against.

---

## 6. General Definition of Done (applies to every task above)

A task is **Done** only if all of the following are true — checked by
script, not read by a human:

1. `lake build` (or the relevant `sage`/`gp`/`python` invocation) exits 0.
2. `git diff --stat` touches only the files named in the task card.
3. `ci/audit_lean.py` reports no new axioms and an accurate `sorry` count
   (open targets are fine; *hidden* ones are not).
4. Every new numeric or literature value has a `source_url` (or bibkey +
   page) in `refs/values.json` or the `.bib` file — no value is typed from
   model memory.
5. Every certificate produced has an explicit `verdict` field; a FAIL is a
   valid, complete Definition-of-Done outcome and must be surfaced in the
   PR body, not treated as task failure.
6. The PR description states, in one line, which task card it closes and
   quotes the exact escalation clause if one was triggered.

## 7. Anti-Patterns (grounds for automatic PR rejection)

- A theorem statement that elaborates to `True` or any goal independent of
  its named hypotheses (this is what sank v1).
- An `axiom` declaration anywhere outside `ci/acceptable_axioms.txt`.
- A "certificate" with no machine-checkable verdict field — prose
  conclusions are not certificates.
- A numeric constant with no traceable source in `refs/values.json`.
- A model (of any tier) resolving an escalation trigger itself instead of
  stopping.

## 8. Suggested Sequencing

1. Stand up `ci/` (M1.4-style scripts) **before** any formalization work —
   otherwise there is nothing stopping a repeat of v1.
2. M2 and M4 (certificates) can run in parallel with M1 (statements); they
   don't depend on each other.
3. M3 depends on M1's scaffolding conventions but not its content.
4. M5 is gated on M1 reaching "statement compiles, `sorry` at theorem level
   only" — it is the only milestone that should not start early.

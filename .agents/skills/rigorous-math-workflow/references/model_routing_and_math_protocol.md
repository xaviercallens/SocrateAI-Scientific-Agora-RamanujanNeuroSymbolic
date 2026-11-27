# Model Routing, Token Optimization & Mathematical Rigor Protocol

## 1. Why Tiered Routing Saves 70–85% of Tokens Without Sacrificing Rigor

In a mixed scientific repository (~5,500 tracked files, 3,564 auto-generated Lean stubs, PDFs, logs, SQLite DBs), naive single-model sessions burn most tokens reading non-authoritative artifacts and applying frontier reasoning models to boilerplate edits.

This workflow splits work across **4 strictly bounded layers**:

1. **Layer 0 — Deterministic Python/CLI (`0 tokens`)**
   - Scans ASTs, Lean comments/axioms/sorries/`by rfl` tautologies, SQLite DB row counts, CSV-vs-JSON certificate mismatches, and git hygiene.
   - Emits a ~2–4 KB structured JSON summary (`preflight_audit.py --json`).
   - Short-circuits clean tracks completely.

2. **Tier T0 — `flash_lite` (Mechanical & Hygiene)**
   - Owns: `pyproject.toml`, `requirements.txt`, `.github/workflows/dualscale_ci.yml`, `README.md` link repair, hardcoded `/home/...` path removal, `.gitignore` cleanup plans.
   - **Never** touches mathematical formulas, Lean theorems/axioms, or epistemic tier classifications. Any mathematical ambiguity triggers `escalations`.

3. **Tier T1 — `flash` (Engineering, Security & Guided Formalization)**
   - Owns two strictly disjoint tracks:
     - **Track B (Code/Security/Infra):** `code_generator.py`, `verifier.py`, `fitness.py`, `database.py`, `dashboard_api.py`, `dashboard/`, `Dockerfile.rama-gpu`, `cloudbuild.yaml`, `run_certificates.py`, `mathesis_gate.py`, `tests/`.
     - **Track C (Lean/Numerics from Spec):** Executes the exact `math_spec` written by T2, adds `MATHESIS-GATE:` contracts + `#print axioms`, writes `norm_num`/`ring`/exact-rational proofs and Python checks.

4. **Tier T2 — `pro` or `inherit` (Mathematical Adjudication & Adversarial Gate)**
   - Runs **only** twice per workflow (reusing one stateful conversation):
     - **Phase 1:** Audits compact preflight + core math files (~14 files max) and produces an exact JSON `math_spec`.
     - **Phase 4:** Reviews the compact `git diff` + Phase 3 deterministic verification output and approves or issues targeted repair tickets.

---

## 2. Mathematical Rigor Checklist (Mandatory for T2 Sign-Off)

Every mathematical or Lean 4 change MUST pass all 7 checks before Tier A/B admission:

1. **Consistency Check (No Derivable `False`):**
   - No custom `axiom` may contradict known concrete instances (e.g., `SaddlePoint.lean`'s `saddle_point_asymptotic` is contradicted by Euler's pentagonal function `⟨[(1, 1)]⟩`).
   - Convert domain assumptions from global `axiom` declarations to explicit hypothesis parameters on theorems, making conditionality transparent in the type signature.
2. **Formula & Sign Verification (Exact Arithmetic, Rule R5):**
   - For an eta-quotient $f(\tau) = \prod_d \eta(d\tau)^{r_d}$:
     - As $\tau = i t \to 0^+$, $\log f(i t) \sim \frac{\pi}{12 t}\left(-\sum_d \frac{r_d}{d}\right)$, so the cusp-0 effective central charge is $c_{\text{eff}}(0) = -\sum_d r_d/d$ (giving $+1$ for $\eta(\tau)^{-1} = \sum p(n) q^{n-1/24}$).
     - For level-$N$ quotients, asymptotic growth is controlled by the **maximum** effective central charge across **all cusps** $a/c$ of $\Gamma_0(N)$, and modularity requires Ono's Theorem 1.64 conditions ($\sum d r_d \equiv 0 \pmod{24}$, $\sum (N/d) r_d \equiv 0 \pmod{24}$, $\prod d^{r_d} \in \mathbb{Q}^{\times 2}$).
     - Alternating-sign Fourier coefficients cannot be labeled unitary BPS state counts without proving positivity or distinguishing a supertrace/index from state degeneracy.
3. **Anti-Vacuity Check (Strengthened Rule R3):**
   - Reject `: Prop := True` predicates and `by trivial` proofs.
   - Reject reflexive tautologies (`candidate.c_eff = candidate.c_eff := by rfl` or `f x = g x := by rfl` where `f` and `g` are copy-pasted definitions).
   - Reject core numeric type shadowing (`def Real := Float`, `def Complex := Float × Float`).
   - Reject theorems that ignore their main hypothesis (e.g., `_hU : HypothesisU` unused).
4. **Quantifier & Domain Soundness:**
   - PDE/regularity hypotheses must quantify over actual solutions (with initial data, domain, and PDE constraints), not over all `ContDiff ℝ ⊤` functions on $\mathbb{R}^3$.
   - "Global well-posedness" requires arbitrary initial data $u(0) = u_0$ (existence + uniqueness), never merely exhibiting $u \equiv 0$.
5. **Kernel Footprint Verification:**
   - Every Tier A Lean module must declare `MATHESIS-GATE: allow=propext,Classical.choice,Quot.sound` (or narrower) and include `#print axioms <theorem>` for every exported theorem.
6. **Certificate Cross-Consistency (Rule R5):**
   - CSV ledgers and JSON certificates must agree on every target verdict and pass `certificate.schema.json`.
   - Placeholder constructions (e.g., non-LPS Cayley graphs) must be tagged Tier C/X and never emit `PASS` for M2.
7. **Epistemic Tier Honesty:**
   - **Tier A:** Kernel-checked Lean 4 proof, clean `#print axioms`, non-vacuous statement, zero `sorry`.
   - **Tier B:** Exact arithmetic certificate over $\mathbb{Q}/\mathbb{Z}$ or peer-reviewed citation pinned in `dualscale.bib` (Rule R4).
   - **Tier L:** Established literature theorem imported as an explicit hypothesis parameter (never an unparameterized global `axiom`).
   - **Tier C:** Conjecture, heuristic search candidate, or conditional scaffold.
   - **Tier X:** Falsified, stubbed, placeholder, or numerically unverified output (may never be cited to support higher tiers).

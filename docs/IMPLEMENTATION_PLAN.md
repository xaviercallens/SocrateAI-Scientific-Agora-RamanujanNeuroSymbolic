# RAMA: Rigorous Implementation Plan
## Rebuilding Ramanujan's Mathematics with Lean 4 + AI

> **Scope**: 48 tasks across 6 phases. Each task executable by a low-tier model.
> **Repo**: `/home/xavkal/xdev/SocrateAI-Scientific-RajMathRecovery/`

---

## Inventory (Current State)

| Asset | Count | Status |
|:---|---:|:---|
| Manuscript page images (NB1+NB2+NB3) | 698 | Scanned |
| Lean 4 verify files (`lean4/verify_*.lean`) | 2,855 | Generated |
| DualScale Lean modules | 10 | Compiling |
| Andrews-Berndt PDFs (Lost Notebook I–IV) | 4 | Available |
| Narosa 1988 original Lost Notebook PDF | 1 | Available |
| namagiri.db discoveries | 695 | 547 stable |
| OEIS novel sequences | 1 | Pending submission |

---

## Phase 0: Infrastructure & Tooling (Tasks 0.1–0.5)

### Task 0.1 — Lean 4 Build Validation
- **Input**: `dualscale/lean/lakefile.lean` + all `.lean` files
- **Action**: Run `lake build` in `dualscale/lean/`, capture all errors
- **DoD**: `lake build` exits 0. Zero `sorry`. Zero warnings.
- **Validation**: `grep -r "sorry" dualscale/lean/ --include="*.lean" | wc -l` = 0
- **Human**: Mathematician reviews each `sorry`-free theorem statement

### Task 0.2 — Database Schema Extension
- **Input**: `namagiri.db`
- **Action**: Add columns: `source_pdf TEXT`, `andrews_berndt_ref TEXT`, `hardy_ref TEXT`, `lean4_theorem_name TEXT`, `human_proof_status TEXT`, `picard_fuchs_order INT`
- **DoD**: Schema migration runs. All 695 rows retain existing data.
- **Validation**: `sqlite3 namagiri.db ".schema discoveries"` shows new columns

### Task 0.3 — Corpus Index Builder
- **Input**: 4 Andrews-Berndt PDFs + Narosa 1988 PDF
- **Action**: Python script to extract table of contents, chapter/entry numbers, and page ranges into `corpus_index.json`
- **DoD**: JSON file maps each entry to `{pdf, page_start, page_end, topic}`
- **Validation**: Spot-check 10 random entries against PDF content

### Task 0.4 — Cross-Reference Linker
- **Input**: `namagiri.db` discoveries + `corpus_index.json`
- **Action**: For each of the 547 stable discoveries, search Andrews-Berndt index for matching eta-quotient exponents. Populate `andrews_berndt_ref` column.
- **DoD**: ≥80% of stable discoveries linked to a specific Andrews-Berndt entry
- **Validation**: Manual verification of 20 random links

### Task 0.5 — CI Pipeline Setup
- **Input**: `.github/workflows/`
- **Action**: Create `lean4_ci.yml` that runs `lake build` on every PR
- **DoD**: PR with intentional `sorry` fails CI. PR without passes.
- **Validation**: Two test PRs (one pass, one fail)

---

## Phase 1: q-Series Foundation Library (Tasks 1.1–1.8)

### Task 1.1 — Formal Power Series Ring
- **Input**: Mathlib `PowerSeries` module
- **Action**: Define `QSeries (R : Type) := PowerSeries ℤ R` with `q`-notation
- **Lean file**: `dualscale/lean/DualScale/QSeries/Basic.lean`
- **DoD**: Compiles. Defines `QSeries.coeff`, `QSeries.mul`, `QSeries.add`
- **Validation**: `lake build DualScale.QSeries.Basic` exits 0
- **Human**: Write §1.1 of companion LaTeX document defining q-series

### Task 1.2 — Dedekind Eta Function Definition
- **Input**: Task 1.1
- **Action**: Define `η(τ) = q^{1/24} ∏_{n≥1}(1-q^n)` as a formal power series. Use `Finset.prod` for truncated products.
- **Lean file**: `dualscale/lean/DualScale/QSeries/Eta.lean`
- **DoD**: `eta_def` theorem stating first 20 coefficients match OEIS A010815
- **Validation**: Lean kernel accepts `native_decide` on coefficient check
- **Human**: Write §1.2 proving η(τ) definition matches Hardy-Ramanujan (1918)

### Task 1.3 — Eta-Quotient Constructor
- **Input**: Task 1.2
- **Action**: Define `EtaQuotient.mk (factors : List (ℕ × ℤ)) : QSeries ℚ` that builds `∏ η(d·τ)^r`
- **Lean file**: `dualscale/lean/DualScale/QSeries/EtaQuotient.lean`
- **DoD**: Compiles. `EtaQuotient.mk [(1,1),(2,-1)]` produces correct first 10 coefficients
- **Validation**: Cross-check against SageMath `EtaGroup` output
- **Human**: Write §1.3 with classical definition from Ono (2004) [8]

### Task 1.4 — Modular Weight Calculator
- **Input**: Task 1.3 + existing `DualScale.Discovery.Notebook1`
- **Action**: Prove `modular_weight (factors) = (∑ rᵢ) / 2` with `norm_num`
- **Lean file**: Extend `DualScale/QSeries/EtaQuotient.lean`
- **DoD**: Theorem compiles for all 547 stable discoveries (batch script)
- **Validation**: Compare against `namagiri.db` `rama_energy` values
- **Human**: Write §1.4 referencing Ono Theorem 1.64

### Task 1.5 — Effective Central Charge Calculator
- **Input**: Task 1.3
- **Action**: Prove `c_eff (factors) = ∑ rᵢ/dᵢ` with `norm_num`
- **Lean file**: Extend `DualScale/QSeries/EtaQuotient.lean`
- **DoD**: Theorem verified for all 547 discoveries
- **Validation**: Batch verify against DB `c_eff` column
- **Human**: §1.5 connecting c_eff to CFT central charge (Strominger-Vafa §3)

### Task 1.6 — Ground State Energy Shift
- **Input**: Task 1.3
- **Action**: Prove `E0 (factors) = -(1/24) · ∑ dᵢ·rᵢ`
- **DoD**: Verified for 547 discoveries
- **Validation**: Batch comparison with DB
- **Human**: §1.6 connecting E0 to string vacuum energy

### Task 1.7 — Coefficient Extraction (First N Terms)
- **Input**: Task 1.3
- **Action**: Function `EtaQuotient.coeffs (eq : EtaQuotient) (n : ℕ) : List ℤ` computing first n Fourier coefficients via truncated product expansion
- **DoD**: Matches SageMath output for 10 test cases (20 terms each)
- **Validation**: `native_decide` on equality with known values
- **Human**: §1.7 documenting algorithm with complexity analysis

### Task 1.8 — Mock Theta Function Stubs
- **Input**: Task 1.1 + Andrews-Berndt Part I chapters 1-5
- **Action**: Define the 7 third-order and 3 fifth-order mock theta functions from Ramanujan's last letter to Hardy (1920)
- **Lean file**: `dualscale/lean/DualScale/QSeries/MockTheta.lean`
- **DoD**: Definitions compile. First 10 coefficients match OEIS for f(q), φ(q), ψ(q)
- **Validation**: Cross-check with Andrews-Berndt Part I, Entry 1.1.1
- **Human**: §1.8 reproducing Ramanujan's original letter notation

---

## Phase 2: Asymptotic Analysis & BPS Entropy (Tasks 2.1–2.8)

### Task 2.1 — Hardy-Ramanujan-Rademacher Exact Formula
- **Input**: Mathlib `Analysis.SpecialFunctions` + Task 1.1
- **Action**: State (axiomatize) the Rademacher exact formula for partition function p(n)
- **Lean file**: `dualscale/lean/DualScale/Asymptotics/Rademacher.lean`
- **DoD**: Axiom compiles. First-order approximation `p(n) ~ (1/4n√3) exp(π√(2n/3))` stated
- **Validation**: Mark as `axiom` with explicit label. Count ≤ 1 new axiom.
- **Human**: §2.1 full proof following Hardy-Ramanujan (1918) + Rademacher (1937)

### Task 2.2 — Saddle-Point Lemma (General)
- **Input**: Task 2.1
- **Action**: Formalize: for modular form of weight k with c_eff > 0, log a(n) ~ 2π√(c_eff · n / 6) as n→∞
- **Lean file**: `dualscale/lean/DualScale/Asymptotics/SaddlePoint.lean`
- **DoD**: Statement compiles. Proof uses axiomatized Rademacher.
- **Validation**: Lean kernel accepts. Human verifies statement matches Cardy (1986)
- **Human**: §2.2 full derivation via steepest-descent contour integration

### Task 2.3 — BPS Entropy Theorem (The 2π Result)
- **Input**: Task 2.2 + Task 1.5
- **Action**: For c_eff = 1, n = 1 (ground state), prove S_BPS = 2π√(1·1/6)·√6 = 2π
- **Lean file**: `dualscale/lean/DualScale/Asymptotics/BPSEntropy.lean`
- **DoD**: `theorem bps_entropy_two_pi : S_BPS c_eff_unit = 2 * Real.pi`
- **Validation**: Lean kernel. No `sorry`. No `native_decide` on reals.
- **Human**: §2.3 connecting to Strominger-Vafa (1996) equation (4.1)

### Task 2.4 — Batch BPS Verification (547 Discoveries)
- **Input**: Task 2.3 + `namagiri.db`
- **Action**: Python script generates 547 Lean theorems, each asserting `bps_entropy discovery_N = 2 * Real.pi`
- **DoD**: All 547 compile. Zero `sorry`.
- **Validation**: `lake build` + `grep sorry` = 0
- **Human**: §2.4 summary table of all 547 verifications

### Task 2.5 — Picard-Fuchs ODE Classifier
- **Input**: Task 1.7 (coefficient sequences)
- **Action**: Python: fit order-3 and order-4 linear recurrences to coefficient sequences. Lean: verify recurrence coefficients via `norm_num`.
- **DoD**: 47 weight-3/2 discoveries classified as order-4 with R² > 0.98
- **Validation**: SageMath independent recurrence check
- **Human**: §2.5 explaining Picard-Fuchs connection to CY3 periods

### Task 2.6 — K3 vs CY3 Discriminant
- **Input**: Task 2.5
- **Action**: Prove: order-3 ↔ K3 surface, order-4 ↔ CY3. Formalize as Lean `inductive`
- **Lean file**: `dualscale/lean/DualScale/Geometry/PicardFuchs.lean`
- **DoD**: Type-checks. Classification matches known examples (Beauville list)
- **Validation**: Cross-check with Candelas et al. (1991)
- **Human**: §2.6 full classification table

### Task 2.7 — Modular Transformation Proof
- **Input**: Task 1.2
- **Action**: Prove η(-1/τ) = √(-iτ) · η(τ) (Dedekind's formula) as a formal identity
- **Lean file**: `dualscale/lean/DualScale/QSeries/ModularTransform.lean`
- **DoD**: Statement compiles (proof may use axiom for complex sqrt)
- **Validation**: Lean kernel + cross-check with Apostol Ch. 3
- **Human**: §2.7 classical proof of Dedekind transformation

### Task 2.8 — T-Duality Bridge Theorem
- **Input**: Task 2.7 + Task 2.3
- **Action**: State and prove: the modular transformation τ → -1/τ is isomorphic to T-duality R → α'/R in string theory
- **Lean file**: `dualscale/lean/DualScale/Geometry/TDuality.lean`
- **DoD**: Compiles as structure isomorphism (`Equiv`)
- **Validation**: Lean kernel
- **Human**: §2.8 connecting Ramanujan's modular intuition to Polchinski Ch. 8

---

## Phase 3: DualScale Macro-Micro Bridge (Tasks 3.1–3.8)

### Task 3.1 — Enstrophy Bound from BPS Entropy
- **Input**: Existing `DualScale.NS.HypothesisU` + Task 2.3
- **Action**: Prove that the BPS entropy 2π provides an upper bound on fluid enstrophy ∫|ω|² dx
- **Lean file**: Extend `DualScale/NS/HypothesisU.lean`
- **DoD**: Theorem compiles. References BPS theorem from Phase 2.
- **Validation**: Lean kernel + physicist review
- **Human**: §3.1 deriving the bound from holographic principle

### Task 3.2 — Aubin-Lions Compactness (Strengthen)
- **Input**: Existing `DualScale.NS.AubinLions`
- **Action**: Remove any `sorry` placeholders. Replace with full proofs or explicit axioms.
- **DoD**: Zero `sorry` in file. Each axiom labeled with justification.
- **Validation**: `grep sorry AubinLions.lean | wc -l` = 0
- **Human**: §3.2 classical Aubin-Lions proof (Simon 1987)

### Task 3.3 — Spectral Gap Strengthening
- **Input**: Existing `DualScale.SpectralGap.Basic`
- **Action**: Connect Ramanujan graph spectral bound to eta-quotient L-function zeros
- **DoD**: New theorem linking Alon-Boppana bound to modular weight
- **Validation**: Lean kernel
- **Human**: §3.3 Ramanujan conjecture for graphs (Lubotzky et al.)

### Task 3.4 — CFM Vortex Direction (Complete)
- **Input**: Existing `DualScale.CFM.Basic`
- **Action**: Prove full CFM regularity criterion using elliptic integral bound
- **DoD**: Theorem matches Constantin-Fefferman-Majda (1996) Theorem 1.1
- **Validation**: Lean kernel + reference to original paper
- **Human**: §3.4 full proof

### Task 3.5 — SUSY Breaking Classification (Extend)
- **Input**: Existing `DualScale.SusyBreaking.Basic`
- **Action**: Classify all 547 discoveries into BPS (k=1/2) vs non-BPS (k≠1/2)
- **DoD**: Lean-verified count: X BPS, Y non-BPS. Matches DB query.
- **Validation**: `SELECT COUNT(*) FROM discoveries WHERE modular_weight = 0.5`
- **Human**: §3.5 physical interpretation table

### Task 3.6 — Phase Transition Map
- **Input**: Tasks 3.1–3.5
- **Action**: Define `PhaseMap : EtaQuotient → PhaseRegime` with cases BPS/NonBPS/CY3/K3
- **DoD**: All 547 discoveries classified. Lean compiles.
- **Validation**: DB cross-check
- **Human**: §3.6 phase diagram figure + explanation

### Task 3.7 — Dyadic Shell Decomposition
- **Input**: Existing `DualScale.NS.DyadicShell`
- **Action**: Prove Littlewood-Paley energy cascade bound using modular periodicity
- **DoD**: Statement + proof compile
- **Validation**: Lean kernel
- **Human**: §3.7 connecting to turbulence cascade (Kolmogorov 1941)

### Task 3.8 — Master Dual-Scale Theorem
- **Input**: All of Phase 3
- **Action**: State the unified theorem: Ramanujan modular invariance ⟹ (micro: BPS entropy = 2π) ∧ (macro: enstrophy bounded)
- **Lean file**: `dualscale/lean/DualScale/MasterTheorem.lean`
- **DoD**: Compiles by composing Phase 2 + Phase 3 results
- **Validation**: Zero `sorry`. Lean kernel.
- **Human**: §3.8 full statement in publication-ready LaTeX

---

## Phase 4: Autonomous Discovery Engine (Tasks 4.1–4.8)

### Task 4.1 — Gemini Vision Extraction Pipeline
- **Input**: 698 page images + API key
- **Action**: Run `live_vision_extractor.py --pages 698`
- **DoD**: All 698 pages processed. Cost < $0.50. Results in `extraction_results.json`
- **Validation**: Spot-check 20 pages against manual reading
- **Human**: Review extraction accuracy report

### Task 4.2 — Andrews-Berndt Cross-Reference Engine
- **Input**: Task 0.3 corpus index + Task 4.1 extractions
- **Action**: Match each extracted formula to Andrews-Berndt entry numbers
- **DoD**: ≥70% of formulas matched. Unmatched flagged for manual review.
- **Validation**: 20 random manual checks
- **Human**: Review unmatched formulas for potential new discoveries

### Task 4.3 — Novel Sequence Detector
- **Input**: Task 1.7 coefficient sequences
- **Action**: Query OEIS API for each 12-term sequence. Flag zero-match sequences.
- **DoD**: List of all novel sequences with ≥12 terms not in OEIS
- **Validation**: Manual OEIS web search for top 5 candidates
- **Human**: Prepare OEIS submission forms

### Task 4.4 — Lean 4 Auto-Theorem Generator
- **Input**: Task 1.3–1.6 templates
- **Action**: Python script that reads `namagiri.db` discovery and generates complete `.lean` file with `modular_weight`, `c_eff`, `E0`, and `bps_entropy` theorems
- **DoD**: Generated file compiles for all 547 stable discoveries
- **Validation**: `lake build` on generated files
- **Human**: Review 10 random generated theorems for mathematical correctness

### Task 4.5 — Genetic Discovery Engine (New Candidates)
- **Input**: Existing RAMA engine + Task 1.3 library
- **Action**: Run GPU-accelerated genetic search for new eta-quotients with fitness > 9.0
- **DoD**: ≥10 new candidates with c_eff > 0 and Lean-verified properties
- **Validation**: SageMath independent coefficient verification
- **Human**: Classify new candidates in Picard-Fuchs framework

### Task 4.6 — Mock Theta Discovery Scan
- **Input**: Task 1.8 + Lost Notebook PDFs
- **Action**: Extract mock theta function identities from Andrews-Berndt. Generate Lean stubs.
- **DoD**: ≥30 mock theta identities with Lean theorem statements
- **Validation**: Cross-check with Andrews-Berndt entry numbers
- **Human**: Priority ranking by physics relevance

### Task 4.7 — Continued Fraction Library
- **Input**: Ramanujan's continued fraction identities (NB1 Ch.XII, NB2 Ch.I)
- **Action**: Formalize Rogers-Ramanujan continued fractions in Lean 4
- **DoD**: R(q) and S(q) definitions + first 10 coefficient theorems
- **Validation**: Lean kernel + OEIS A003114, A003106
- **Human**: §4.7 classical proof of Rogers-Ramanujan identities

### Task 4.8 — Discovery Database Consolidation
- **Input**: All Phase 4 outputs
- **Action**: Update `namagiri.db` with all cross-references, Lean theorem names, human proof status
- **DoD**: Every discovery has: `lean4_theorem_name`, `andrews_berndt_ref`, `human_proof_status`
- **Validation**: SQL integrity check (no NULLs in required fields)
- **Human**: Final review of complete database

---

## Phase 5: Human Mathematics Companion (Tasks 5.1–5.8)

### Task 5.1 — LaTeX Book Skeleton
- **Action**: Create `docs/ramanujan_mathematics_book/` with chapter structure mirroring Phases 1–4
- **DoD**: Compiles to PDF. TOC matches task structure.
- **Validation**: `pdflatex` exits 0

### Task 5.2 — Chapter 1: q-Series Foundations (Human Proofs)
- **Input**: All §1.x sections from Phase 1 tasks
- **Action**: Compile into coherent chapter with traditional mathematical proofs
- **DoD**: All theorems from Phase 1 have both Lean proof AND LaTeX proof
- **Validation**: Mathematician review. Each proof self-contained.

### Task 5.3 — Chapter 2: Asymptotics & Entropy (Human Proofs)
- **Input**: All §2.x sections
- **DoD**: Saddle-point, Rademacher, BPS entropy fully derived on paper
- **Validation**: Peer review

### Task 5.4 — Chapter 3: Dual-Scale Geometry (Human Proofs)
- **Input**: All §3.x sections
- **DoD**: T-duality bridge theorem explained at textbook level
- **Validation**: Peer review

### Task 5.5 — Chapter 4: Discoveries (Catalogue)
- **Input**: `namagiri.db` + Phase 4 outputs
- **DoD**: Full catalogue of 547 discoveries with properties, source pages, references
- **Validation**: Every entry cross-referenced to Lean theorem + Andrews-Berndt

### Task 5.6 — Appendix A: Lean 4 Code Listings
- **Action**: Auto-extract all Lean theorems into formatted appendix
- **DoD**: Every theorem in book has corresponding code listing
- **Validation**: Code compiles independently

### Task 5.7 — Appendix B: Ramanujan Source Concordance
- **Action**: Table mapping NB page → Andrews-Berndt entry → Lean theorem → Physics
- **DoD**: Complete for all 547 discoveries
- **Validation**: 20 random spot-checks

### Task 5.8 — Final Compilation & Review
- **Action**: Build complete PDF. Run Lean CI. Generate summary statistics.
- **DoD**: Book PDF + Zero-sorry Lean build + GitHub release
- **Validation**: Full CI green. PDF renders all figures.

---

## Phase 6: Publication & Dissemination (Tasks 6.1–6.4)

### Task 6.1 — arXiv Pre-print Preparation
- **DoD**: Paper formatted per arXiv math.NT standards. Abstract ≤ 200 words.

### Task 6.2 — OEIS Submissions
- **DoD**: All novel sequences submitted with 20+ terms and generating formula

### Task 6.3 — GitHub Release
- **DoD**: Tagged release with DOI (via Zenodo). README updated.

### Task 6.4 — Vulgarisation Update
- **DoD**: EN + FR popular articles updated with final results

---

## Validation Matrix

| Gate | Tool | Pass Criterion |
|:---|:---|:---|
| **V1: Lean Kernel** | `lake build` | Exit 0, 0 sorry |
| **V2: Sorry Audit** | `grep -r "sorry"` | Count = 0 |
| **V3: Axiom Budget** | `grep -r "axiom"` | Count ≤ 5, each justified |
| **V4: DB Integrity** | `sqlite3` checks | No NULL in required fields |
| **V5: Cross-Reference** | Manual spot-check | 20 random entries correct |
| **V6: Coefficient Match** | SageMath comparison | 100% match on first 20 terms |
| **V7: Human Proof** | Mathematician review | Each Lean theorem has LaTeX proof |
| **V8: CI Green** | GitHub Actions | All workflows pass |

---

## Task Execution Protocol (for Low-Tier Models)

Each task prompt MUST include:

```
TASK: [Task ID and name]
INPUT FILES: [Exact file paths]
OUTPUT FILES: [Exact file paths to create/modify]
CONSTRAINTS:
  - Do NOT use `sorry` in any Lean file
  - Do NOT modify files outside OUTPUT FILES
  - Do NOT commit API keys or secrets
  - All Lean files must import from Mathlib or DualScale only
DOD CHECK:
  - Run: [exact shell command]
  - Expected: [exact expected output]
HUMAN REVIEW NEEDED: [yes/no + what to review]
```

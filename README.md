# Ramanujan Neuro-Symbolic Mathematics: Dual-Scale Geometry & $K3 \times T^2$ (v3.3 — Elenchus Canon)

Welcome to the **Ramanujan Neuro-Symbolic Mathematics** pipeline (`SocrateAI-Scientific-RajMathRecovery`). This repository implements an auditable neuro-symbolic verification program connecting Srinivasa Ramanujan's complete mathematical works ($q$-series, partitions, continued fractions, mock modular forms, $\tau(n)$, $1/\pi$ series, Ramanujan sums, highly composite numbers), $K3 \times T^2$ dual-scale geometry, and regularized hydrodynamic models under strict Lean 4.33.1 kernel verification, ChromaDB RAG grounding, and the **Socratic Elenchus** prover–skeptic–negative-control methodology.

---

## Epistemic Protocol (Tiers A, B, L, C, X)

Every mathematical assertion, database entry, and theorem in this repository carries one of **five explicit epistemic tiers**, enforced by [docs/v3_paper/main.tex](docs/v3_paper/main.tex), [docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md](docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md), and [dualscale/ci/audit_lean.py](dualscale/ci/audit_lean.py):

| Tier | Classification | Admission Criterion |
|---|---|---|
| **Tier A** | Machine-checked | Lean 4 proof with `#print axioms` strictly within `{propext, Classical.choice, Quot.sound}` ($\subseteq \{\texttt{propext}\}$ for all **591** live kernel theorems); zero `sorry`, zero custom `axiom`, zero vacuity. |
| **Tier B** | Established literature / Catalog match | Peer-reviewed theorem cited in `dualscale/refs/bib/dualscale.bib`, or exact 30-term $\mathbb{Q}[[q]]$ classical catalog match (mock theta functions, Rogers–Ramanujan $G(q)$). |
| **Tier L** | Literature hypothesis parameter | Established external theorem (e.g., Aubin–Lions compactness, Rademacher asymptotics, Sturm bound, Jacobi Triple Product) passed explicitly as a theorem hypothesis parameter rather than declared as a global `axiom`. |
| **Tier C** | Conjecture / Open heuristic | Automated search candidates, unverified manuscript transcriptions (`TRANSCRIBED_OPEN`), or open conditional targets (e.g., Hypothesis U, `FractureConjecture`). |
| **Tier X** | Falsified / Quarantined | Explicitly refuted conjectures (M2 spectral gap, M3 CFM elliptic angle, 14 Campaign v2 OCR typos) or quarantined mock-proxy checks (legacy $S_{12}$ moduli-map reclassification). |

### Strict CI Rules (R1–R5)

Continuous integration ([.github/workflows/dualscale_ci.yml](.github/workflows/dualscale_ci.yml)) enforces five automated epistemic gates:

- **Rule R1 (No Custom Axioms):** Global `axiom` declarations are prohibited in active `.lean` files (`audit_lean.py`, `mathesis_gate.py`).
- **Rule R2 (Tracked `sorry`):** Any `sorry` marks a target OPEN (never Tier A) and fails the R1–R3 CI gate (`0` `sorry` in the active tree).
- **Rule R3 (Anti-Vacuity):** Prohibits `Prop := True`, `:= by trivial`, reflexive `x = x := by rfl`, core type shadowing (`def Real := Float`), pinned physical constants (`alpha_prime := 1`), and zero-stub operators (`:= 0`).
- **Rule R4 (Citation Audit):** [dualscale/ci/audit_citations.py](dualscale/ci/audit_citations.py) verifies that all citations in `docs/v3_paper` and `docs/v2.1_paper` resolve in [dualscale/refs/bib/dualscale.bib](dualscale/refs/bib/dualscale.bib) with **0 unused bibliography entries**.
- **Rule R5 (Exact Certificates):** `run_certificates.py` and `verify_qseries.py` enforce exact-arithmetic agreement over $\mathbb{Z}/\mathbb{Q}$ between JSON certificates, CSV ledgers, and Lean 4 kernel theorems.

---

## Campaign v2 + Wave 4 Exact Verification Truth

Campaign v2 and Wave 4 regenerated the entire Ramanujan manuscript extraction and formalization pipeline in exact $\mathbb{Z}/\mathbb{Q}$ arithmetic with live Lean 4.33.1 kernel verification:

- **Complete Manuscript Corpus:** **839 / 839** pages processed with **0** extraction errors (133 Narosa 1988 *Lost Notebook* facsimile sheets, 8 Ramanujan letters from Ono, and 698 pages of Notebooks 1–3).
- **Structured Database (`namagiri.db`):** **2,458** rows (**70** Tier A verified occurrences, **10** Tier B exact classical catalog matches for 3rd/5th/6th-order mock theta functions and Rogers–Ramanujan $G(q)$, **2,378** Tier C `TRANSCRIBED_OPEN` entries, **0** vacuous rows).
- **Unique Dedekind $\eta$-Quotients:** **54** unique exact $\eta$-quotients verified in 30-term $\mathbb{Q}[[q]]$ arithmetic (25 satisfying Ono's Theorem 1.64 congruences on $\Gamma_0(N)$, 37 with non-negative Fourier coefficients, 17 alternating-sign indices).
- **Live Zero-Custom-Axiom Lean 4.33.1 Kernel Theorems:** **591** live theorems verified with `#print axioms` $\subseteq \{\texttt{propext}\}$ via `lean` v4.33.1 + `mathesis_gate.py`:
  - `dualscale/lean/DualScale/Discovery/CampaignV2Verified.lean`: **275** theorems covering all 54 unique $\eta$-quotients (weight, $c_{\text{eff}}(0)$, $E_0$, Ono congruences, 12-term $q$-series) and 5 unmerged finite-order $q^{15}$ Ramanujan `LHS = RHS` identities.
  - `dualscale/lean/DualScale/Discovery/AllNAndPropositionsVerified.lean`: **63** exported theorems covering universal $\forall n$ proofs (`eq_d6899de389_all_n`, `eq_c23aa45585_all_n`) and conditional JTP lifts (`eq_d6899de389_eta_all_n_of_jtp`, `eq_c23aa45585_eta_all_n_of_jtp`), universal $\forall\text{len}$ unmerged Dedekind factorization proofs (`eq_460927b577_all_len`, `eq_2847c49f95_all_len`), exact level-12 weight-1 Nebentypus $\chi(d)=(-3/d)$ compatibility and Sturm-bound conditional upgrade $B(\Gamma_0(12),1)=2<15$ (`eq_0722eebfe8_all_n_conditional`), universal `EtaQuot` algebra, live RAMA Deep Burn kernel invariants (`deepBurn_ceff_cusp0`, `deepBurn_weight`, `deepBurn_E0`, `deepBurn_ono_false`, `deepBurn_prefix_10`, `deepBurn_has_negative_coeff`), `sym2_recurrence_int`, exact `QPos` T-duality, and certified refutations.
  - `dualscale/lean/DualScale/Discovery/RamanujanElenchusCanon.lean`: **253** theorems (including **20** executable `neg_ctrl_*` Elenchus negative controls) across 8 core Ramanujan domains: universal Euler Odd=Distinct partition theorem (`∀ n`, `∀ len`) & pentagonal recurrence, Ramanujan mod 5/7/11 partition congruences & conditional generating lifts, Ramanujan $\tau(n)$ (`Δ(q)/q`, multiplicativity, Hecke recurrences, $\bmod 691$, Deligne bounds), universal prime Ramanujan sums $c_p(n)$, universal Euler–Wallis continued-fraction determinants & Rogers–Ramanujan $R(q)/G(q)/H(q)$, 3rd-order mock theta functions ($f, \phi, \psi$ + Watson/Ramanujan identities), universal minimality of Taxicab `1729` & first 10 Highly Composite Numbers, and Ramanujan's 1914 $1/\pi$ 14/15-digit rational brackets + universal `< 10^{-7}` term-ratio convergence bound.
- **Auto-Refuted OCR Typos:** **14** OCR-corrupted equations (`typo01`–`typo14`) automatically refuted by exact coefficient mismatch in $\mathbb{Q}[[q]]$ and live-verified in the Lean 4.33.1 kernel.
- **Multi-Collection ChromaDB RAG Corpus (`data/chromadb/`):** **6,706** indexed vector chunks across three persistent collections (`src/literature/chroma_kb.py`):
  - `ramanujan_literature_v1` (**3,870** chunks): **44** curated arXiv papers across 8 pillars (`docs/literature/corpus_manifest.json`).
  - `ramanujan_primary_works_v1` (**2,732** chunks): Andrews & Berndt *Ramanujan's Lost Notebook* Parts I–IV (1,730 pages) + Campaign v2 839-page DB primary records.
  - `rama_repo_artifacts` (**104** chunks): v3.2 paper, BibTeX, literature review, Elenchus roadmap, and validation ledgers.

---

## Milestones & Honest Epistemic Status

| Milestone | Scope | Current Status |
|---|---|---|
| **M1** | Conjectural Dictionary (Conjectures 1–5) | **Scaffolded (R1–R3 clean)** — formalized with explicit hypothesis parameters; no global `axiom` or `sorry`. |
| **M2** | Triad Circulant Spectral Gap | **FALSIFIED (`FAIL` / Tier X)** — tested circulants ($p \in \{2,3,5\}$, nominal $k \in \{3,4,6\}$, actual regularity $2k \in \{6,8,12\}$) violate Alon–Boppana ($\lambda_2 > 2\sqrt{k-1}$). Exact squared-integer refutations kernel-proved in `AllNAndPropositionsVerified.lean`. |
| **M3** | CFM Elliptic-Angle Proxy | **FALSIFIED (`FAIL` / Tier X)** — Constantin–Fefferman–Majda Lipschitz constant $\frac{4}{3}\pi$ strictly mismatches the elliptic proxy $\frac{16}{9}\pi$ (gap $\frac{4}{9}\pi \neq 0$). Kernel-proved in `AllNAndPropositionsVerified.lean` and `DualScale/CFM/Basic.lean`. |
| **M4** | $\operatorname{Sym}^2(L_2)$ Lock & $S_{12}$ Provenance | **Split: $\operatorname{Sym}^2(L_2)$ Tier A / $S_{12}$ proxy Tier X** — `sym2_recurrence_int` (over $\mathbb{Z}$) and constant/variable-coefficient $\mathbb{R}$ versions (`DualScale/K3Lock/Basic.lean`) are Tier A. Legacy $S_{12}$ reclassification (`S12_vs_K3.json`, `S12_vs_elliptic.json`, `s12_ledger.csv`) is **quarantined as Tier X**: `s12_recurrence` in `values.json` is Apéry's $\zeta(3)$ sequence (`OEIS A005259`, $u_5 = 819\,005$, residual $765\,005 \neq 0$). |
| **M5** | Hypothesis U $\implies$ Smoothness | **Strictly Conditional Tier C** — `DualScale/NS/HypothesisU.lean` and `DualScale/Physics/MasterDualScale.lean` prove only conditional deductions taking Hypothesis U (Tier C) and Aubin–Lions (Tier L) as explicit hypotheses. The Fluid/Gravity correspondence operates strictly in the slow-derivative hydrodynamic regime (BHMR 2008) which breaks down at diverging gradients/enstrophy, and Tao's (2016) finite-time blowup barrier for averaged 3D Navier–Stokes rules out generic energy/dyadic regularity proofs. |
| **M6** | Campaign v2 & Wave 4 Regeneration | **Completed (Tier A Kernel Verified)** — 839/839 pages, 2,458 DB rows, 54 unique $\eta$-quotients, 338 live zero-custom-axiom Lean 4.33.1 theorems, 14 OCR typo refutations. |
| **M7** | Publication & Release Packages | **Completed (v3.2)** — Bilingual compendia, v3.2 research paper, arXiv source tarball, consolidated release zip with SHA-256 manifest, and 54-sequence OEIS payload. |
| **M8** | Socratic Elenchus Full-Formalization Canon & Roadmap | **Completed & Blind-Audited (`APPROVED`, 0 defects)** — 6,706-chunk ChromaDB KB (44 arXiv papers + Andrews–Berndt Lost Notebook Parts I–IV), 253 new live Lean 4.33.1 theorems incl. 20 negative controls (`RamanujanElenchusCanon.lean`, **591** total live theorems), 10-domain / 12-milestone roadmap (`docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md`), and Owner's Epistemic Ledger (`dualscale/certificates/ramanujan_elenchus_audit_ledger.json`). |

---

## Verification Commands (Zero-Token Local Gates)

```bash
# 1. Live Lean 4.33.1 kernel & #print axioms footprint verification (591 theorems)
python3 tools/mathesis-gate/mathesis_gate.py dualscale/lean/DualScale/Discovery --exclude verify_ --exclude NormNumVerified --exclude Notebook

# 2. Static R1-R3 checks on Mathlib-importing modules (offline .lake/ absent)
python3 dualscale/ci/audit_lean.py --root dualscale/lean/DualScale

# 3. Rule R4 citations & bibliography completeness (0 errors, 0 unused entries)
python3 dualscale/ci/audit_citations.py --paper-dir docs/v3_paper --bib dualscale/refs/bib/dualscale.bib

# 4. Rule R5 exact certificates, q-series arithmetic, and unit tests (39/39)
python3 dualscale/ci/validate_refs.py
python3 dualscale/ci/run_certificates.py
python3 dualscale/ci/verify_qseries.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -v

# 5. Cross-collection ChromaDB RAG query (6,706 chunks)
.venv/bin/python src/literature/chroma_kb.py query "Ramanujan partition congruences mod 5 crank" --n 5 --collection all

# 6. Rebuild v3.2 LaTeX paper, arXiv package, and SHA-256 release bundle
python3 tools/build_publication_packages.py
```

---

## Publications, Documentation & Releases

- **Full Lean 4 Formalization Roadmap & Elenchus Blueprint (10 Domains, 12 Milestones):** [docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md](docs/RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md).
- **Elenchus Workflow & Owner's Audit Ledger:** [tools/workflows/ramanujan_elenchus_formalization_workflow.py](tools/workflows/ramanujan_elenchus_formalization_workflow.py) and [dualscale/certificates/ramanujan_elenchus_audit_ledger.json](dualscale/certificates/ramanujan_elenchus_audit_ledger.json).
- **Research Paper (v3.2):** [docs/v3_paper/main.tex](docs/v3_paper/main.tex) (compiled PDF synced to `docs/release_consolidated/v3_paper_main.pdf`).
- **Literature Review & Epistemic Map:** [docs/literature/REVUE_LITTERATURE_DETAILLEE.md](docs/literature/REVUE_LITTERATURE_DETAILLEE.md) and [docs/literature/corpus_manifest.json](docs/literature/corpus_manifest.json) (44 arXiv papers).
- **arXiv Submission Package:** [docs/arxiv_submission/metadata.txt](docs/arxiv_submission/metadata.txt) and `docs/arxiv_submission/arxiv_package.zip`.
- **Consolidated Release Manifest (SHA-256):** [docs/release_consolidated/MANIFEST.md](docs/release_consolidated/MANIFEST.md) and `docs/release_consolidated/Final_Release_Package.zip`.
- **OEIS Exact 30-Term Payload (54 Unique Sequences):** [docs/oeis_submission/oeis_batch.txt](docs/oeis_submission/oeis_batch.txt).

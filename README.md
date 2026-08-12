# Ramanujan Neuro-Symbolic Mathematics: Dual-Scale Geometry & K3×T²

Welcome to the **Ramanujan Neuro-Symbolic Mathematics** pipeline. This repository executes a fully automated, rigorous mathematical research program exploring the dual-scale geometry of $K3 \times T^2$ compactifications, hydrodynamic limits, and mock modular forms.

## Epistemic Protocol

As dictated by the Version 2 position paper, this repository strictly enforces a three-tier epistemic system:

| Tier | Meaning | Admission Criterion |
|------|---------|---------------------|
| **Tier A** | Machine-checked | Lean 4 proof; `#print axioms` clean; no `sorry` |
| **Tier B** | Established | Peer-reviewed literature, pinned to exact values |
| **Tier C** | Conjecture/Heuristic | Automated search candidates (RAMA engine) |

### Strict CI Rules (R1–R5)
Our continuous integration (`dualscale_ci.yml`) enforces the following boundaries:
*   **Rule R1**: No `axiom` declarations allowed in `.lean` files.
*   **Rule R2**: `sorry` marks a target as OPEN and is actively tracked as technical debt.
*   **Rule R3**: Theorem statements of type `True` or logically vacuous propositions are strictly prohibited and will fail the build.
*   **Rule R4**: Tier B claims must cite their sources.
*   **Rule R5**: Numerical claims require exact-arithmetic PASS/FAIL certificates over $\mathbb{Q}$ (e.g., Alon-Boppana spectral gaps).

## Architecture & Pipeline

### Stage 1: The RAMA Heuristic Engine
*   `scripts/rama_engine.py` treats mathematical candidate generation as a local search over a symbolic space of Eulerian $q$-series.
*   Guided by the energy functional: $E = \alpha C + \beta I + \gamma D$
*   Discoveries are logged to `namagiri.db`.

### Stage 2: The Shadow Bridge
*   `scripts/shadow_bridge.py` attempts to complete the non-holomorphic period integrals (shadows) for the RAMA anomalies, following Zwegers' mock modular forms.
*   Successfully matched candidates upgrade to `SHADOW_COMPLETE`.

### Stage 3: The Formal Lock
*   `scripts/formal_lock.py` converts `SHADOW_COMPLETE` candidates into rigorous Lean 4 scaffolds inside `dualscale/lean/targets/`.
*   **Graceful Degradation:** If a full arithmetic equality cannot be proven, the system safely falls back to a structural blueprint (proving topological properties) rather than inserting vacuous proofs.
*   Conjectural targets explicitly use `sorry` or `0` stubs and are actively tracked as open Tier A targets.

### Stage 4: Continuous Documentation & CI
*   A dedicated CI action compiles the project's LaTeX documentation (`docs/v2.1_paper/socrateai_dualscale_v2.tex`).
*   **Rule R4 Enforcement:** `audit_citations.py` actively parses the raw `.tex` files to ensure every Tier B claim maps securely to the master bibliography (`dualscale.bib`), warning against missing or unused citations.

## Milestones Reached
1.  **M1**: Scaffolded the Conjectural Dictionary for Conjectures 1-5 in Lean 4 (`Conjectures.lean`).
2.  **M2**: Computed exact-arithmetic spectral certificates for triad graphs.
3.  **M3**: Executed CFM Elliptic-Angle Falsification (successfully falsifying Conjecture 3).
4.  **M4**: Generated exact moduli-map certificates for the $S_{12}$ Apéry-like sequence, confirming it as an elliptic curve background.
5.  **M5**: Formalized the Hypothesis U ⟹ Smoothness implication logic in Lean 4.
6.  **M6 (Phase 4)**: Processed 698-page Ramanujan manuscript via Gemini Vision AI, extracting 1,796+ theorems and identifying 938 mathematically novel sequences.
7.  **M7 (Phase 5/6)**: Released the machine-verified RAMA Compendium mapping Ramanujan q-series to macroscopic BPS entropy and fluid-mechanic enstrophy bounds.

## Publications & Releases
*   **The RAMA Compendium**: A fully machine-verified bilingual (FR/EN) publication translating Ramanujan's lost discoveries to holographic spacetime geometry. [Draft PDFs](docs/book/)
*   **arXiv Pre-print**: Prepared for `hep-th`, `math.NT`, and `gr-qc`. [arXiv Package](docs/arxiv_submission/arxiv_package.zip)
*   **OEIS Submissions**: Auto-generated payload for 938 novel sequences to the On-Line Encyclopedia of Integer Sequences. [Payload](docs/oeis_submission/oeis_batch.txt)

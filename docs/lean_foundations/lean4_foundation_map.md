# Phase 0 Lean 4 Foundation Map: External Repositories & Modules

> **Status**: Completed  
> **Source Repositories**: Cloned locally in `docs/lean_foundations/`  
> **Purpose**: Map out existing Lean 4 definitions and theorems ($q$-series, $q$-Pochhammer, Rogers-Ramanujan, Dyson Ranks) to build upon for Phase 1 formalization.

---

## 1. Local Cloned Repositories Overview

| Repository Path | Origin | Main Topics Formalized |
| :--- | :--- | :--- |
| `docs/lean_foundations/RogersRamanujan` | [`AxiomMath/RogersRamanujan`](https://github.com/AxiomMath/RogersRamanujan) | $q$-integers, $q$-factorials, $q$-binomials, $q$-Pochhammer symbols $(a; q)_n$, infinite $q$-Pochhammer $(a; q)_\infty$, Jacobi Triple Product, Bailey pairs, Rogers-Ramanujan identities. |
| `docs/lean_foundations/HigherDyson` | [`AxiomMath/HigherDyson`](https://github.com/AxiomMath/HigherDyson) | Higher Dyson ranks, partition rank differentials, mock theta asymptotics, modular transformation bounds. |

---

## 2. Key Lean 4 Definitions & Modules to Leverage

### A. $q$-Pochhammer & Series Definitions (`RogersRamanujan/NumberTheory/QTheory/Basic.lean`)
```lean
-- q-Pochhammer symbol (a; q)_n
def qPochhammer (a q : R) : ℕ → R
| 0     => 1
| n + 1 => qPochhammer a q n * (1 - a * q ^ n)

-- Infinite q-Pochhammer symbol (a; q)_∞
def qPochhammerInf (a q : R) : R := ...
```

### B. Jacobi Triple Product Identity (`RogersRamanujan/NumberTheory/QTheory/JacobiTripleProduct/PowerSeriesIdentity.lean`)
```lean
-- Jacobi Triple Product Identity in Lean 4:
-- ∑_{n=-∞}^∞ (-1)^n q^{(n^2-n)/2} z^n = (z; q)_∞ (q/z; q)_∞ (q; q)_∞
theorem jacobi_triple_product_power_series (z q : R) : ...
```

### C. Pentagonal Number Theorem (`RogersRamanujan/NumberTheory/QTheory/Pentagonal.lean`)
```lean
-- Euler's Pentagonal Number Theorem:
-- (q; q)_∞ = ∑_{k=-∞}^∞ (-1)^k q^{(3k^2 - k)/2}
theorem euler_pentagonal_identity (q : R) : ...
```

---

## 3. Integration Plan for Phase 1
1. **Direct Re-use**: Import `qPochhammer`, `qPochhammerInf`, and `jacobi_triple_product_power_series` directly into `DualScale/Math/EtaQuotient.lean`.
2. **Eta Quotient Construction**: Define Dedekind eta quotient $\eta(\tau) = q^{1/24} (q; q)_\infty$ building on `qPochhammerInf`.
3. **Automated Verification**: Use `jacobi_triple_product_power_series` as an explicit Lean 4 tactic to verify $q$-series extractions from Ramanujan manuscript pages.

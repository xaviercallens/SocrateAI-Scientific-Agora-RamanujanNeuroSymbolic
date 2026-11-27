-- DualScale/QSeries/EtaQuotient.lean — Tasks 1.2–1.6: Eta-Quotient Computations
-- =================================================================================
-- Provides computable functions for modular weight (k), cusp-0 effective central
-- charge (c_eff(0)), general cusp effective central charge c_eff(c), ground state
-- energy shift (E₀), and Ono Theorem 1.64 modularity checks from an eta-quotient's
-- discrete factor list. All proofs use `norm_num` for machine-verified arithmetic.
--
-- IMPORTANT EPSTEMIC NOTE:
--   `cEff`, `cuspCEff`, `modularWeight`, `groundStateShift`, and Ono congruence
--   checks are Tier-A exact rational/integer invariants of the factor list.
--   They do NOT by themselves prove modularity, coefficient positivity, or
--   unitarity as BPS state counts: alternating-sign forms such as `deep_burn`
--   and `nb3_vacuum` are signed indices / supertraces, not unitary BPS counts.
--
-- References:
--   Ono (2004) Theorem 1.64 — modularity conditions for eta-quotients
--   Strominger-Vafa (1996) §3 — c_eff and BPS entropy
--   Hardy-Ramanujan (1918) — asymptotic partition formula

import Mathlib.Data.Rat.Init
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import DualScale.QSeries.Basic

namespace DualScale.QSeries.EtaQuotient

open DualScale.QSeries

/-! ## Eta-Quotient Abstract Syntax Tree

An eta-quotient is represented as a list of `(divisor, exponent)` pairs:
  f(τ) = ∏ η(dᵢ·τ)^{rᵢ}

All physical quantities (k, c_eff, E₀) are computable from this list alone,
without expanding the infinite product.
-/

/-- An η-quotient represented as a list of (divisor d, exponent r) pairs. -/
structure EtaQuot where
  factors : List (ℕ × ℤ)
  deriving Repr

-- ═══════════════════════════════════════════════════════════════════════════════
-- Task 1.4: Modular Weight
-- k = (1/2) · ∑ rᵢ
-- ═══════════════════════════════════════════════════════════════════════════════

/-- Compute the modular weight k = (∑ rᵢ) / 2 as a rational number. -/
def modularWeight (eq : EtaQuot) : ℚ :=
  (eq.factors.foldl (fun acc dr => acc + (dr.2 : ℚ)) 0) / 2

-- ═══════════════════════════════════════════════════════════════════════════════
-- Task 1.5: Effective Central Charge (Cusp-0 and General Cusp c | N)
-- c_eff(0) = -∑ rᵢ / dᵢ
-- c_eff(c) = -(1/c²) · ∑ (gcd(dᵢ, c)² / dᵢ) · rᵢ
-- ═══════════════════════════════════════════════════════════════════════════════

/-- Compute the cusp-0 effective central charge `c_eff(0) = -∑ (rᵢ / dᵢ)`.
    With this sign convention, `1/η(τ)` (`[(1, -1)]`) has `c_eff = +1` and
    `η(τ)` (`[(1, 1)]`) has `c_eff = -1`. -/
def cEff (eq : EtaQuot) : ℚ :=
  eq.factors.foldl (fun acc dr => acc - (dr.2 : ℚ) / (dr.1 : ℚ)) 0

/-- Compute the effective central charge at cusp `1/c` (for `c ≥ 1`):
    `c_eff(c) = -(1 / c²) · ∑ (gcd(dᵢ, c)² / dᵢ) · rᵢ`.
    When `c = 1`, `gcd(dᵢ, 1) = 1`, recovering `cEff eq`. -/
def cuspCEff (eq : EtaQuot) (c : ℕ) : ℚ :=
  -(eq.factors.foldl
    (fun acc dr => acc + ((Nat.gcd dr.1 c : ℚ) ^ 2 / (dr.1 : ℚ)) * (dr.2 : ℚ))
    0) / ((c : ℚ) ^ 2)

-- ═══════════════════════════════════════════════════════════════════════════════
-- Task 1.6: Ground State Energy Shift & Ono (2004) Theorem 1.64 Checks
-- E₀ = -(1/24) · ∑ dᵢ · rᵢ
-- ═══════════════════════════════════════════════════════════════════════════════

/-- Compute the ground state energy shift E₀ = -(1/24) · ∑ (dᵢ · rᵢ). -/
def groundStateShift (eq : EtaQuot) : ℚ :=
  -(eq.factors.foldl (fun acc dr => acc + (dr.1 : ℚ) * (dr.2 : ℚ)) 0) / 24

/-- First Ono (2004) Theorem 1.64 congruence sum: `∑ dᵢ · rᵢ` (must be `≡ 0 mod 24`). -/
def onoSumDR (eq : EtaQuot) : ℤ :=
  eq.factors.foldl (fun acc dr => acc + (dr.1 : ℤ) * dr.2) 0

/-- Second Ono (2004) Theorem 1.64 congruence sum at level `N`:
    `∑ (N / dᵢ) · rᵢ` (must be `≡ 0 mod 24`, alongside `dᵢ ∣ N`). -/
def onoSumNOverDR (eq : EtaQuot) (N : ℕ) : ℤ :=
  eq.factors.foldl (fun acc dr => acc + ((N / dr.1 : ℕ) : ℤ) * dr.2) 0

/-- Level divisibility precondition for Ono Theorem 1.64 on `Γ₀(N)`. -/
def onoLevelDivisible (eq : EtaQuot) (N : ℕ) : Prop :=
  0 < N ∧ ∀ dr ∈ eq.factors, 0 < dr.1 ∧ dr.1 ∣ N

/-- Necessary Ono Theorem 1.64 modulo-24 congruence conditions on `Γ₀(N)`.
    (Full modularity also requires `∏ dᵢ^{rᵢ}` to be a rational square.) -/
def onoModularityCongruences (eq : EtaQuot) (N : ℕ) : Prop :=
  onoLevelDivisible eq N ∧ onoSumDR eq % 24 = 0 ∧ onoSumNOverDR eq N % 24 = 0

-- ═══════════════════════════════════════════════════════════════════════════════
-- BPS Classification
-- ═══════════════════════════════════════════════════════════════════════════════

/-- A discovery has weight 1/2 iff its modular weight is exactly 1/2.
    Note: `isBPS` checks weight only; unitarity/positivity must be checked separately. -/
def isBPS (eq : EtaQuot) : Prop := modularWeight eq = 1 / 2

/-- A discovery breaks SUSY weight iff its modular weight differs from 1/2. -/
def isSUSYBroken (eq : EtaQuot) : Prop := modularWeight eq ≠ 1 / 2

-- ═══════════════════════════════════════════════════════════════════════════════
-- Canonical Benchmarks & Verified Examples from namagiri.db
-- ═══════════════════════════════════════════════════════════════════════════════

/-- Generating function for integer partitions `1/η(τ)` (up to `q^{1/24}`): `c_eff = +1`. -/
theorem partition_ceff : cEff ⟨[(1, -1)]⟩ = 1 := by
  unfold cEff
  norm_num

/-- Dedekind eta `η(τ)` (Euler's pentagonal series, up to `q^{1/24}`): `c_eff = -1`. -/
theorem pentagonal_ceff : cEff ⟨[(1, 1)]⟩ = -1 := by
  unfold cEff
  norm_num

/-- Notebook 1, Chapter I — first extracted eta-quotient.
    Factors: η(q³)¹ · η(q⁸)¹ · η(q⁹)⁻¹ (signed index; not a positive BPS count). -/
def nb1_ch1_discovery : EtaQuot := ⟨[(3, 1), (8, 1), (9, -1)]⟩

theorem nb1_ch1_weight : modularWeight nb1_ch1_discovery = 1 / 2 := by
  unfold modularWeight nb1_ch1_discovery
  norm_num

theorem nb1_ch1_is_bps : isBPS nb1_ch1_discovery := by
  unfold isBPS
  exact nb1_ch1_weight

/-- Notebook 3 — Alternating-sign weight-1/2 signed-index discovery (NOT a unitary BPS count).
    Factors: η(q⁸)⁶ · η(q¹⁰)³ · η(q¹¹)⁻³ · η(q¹²)⁻⁵. -/
def nb3_vacuum : EtaQuot := ⟨[(8, 6), (10, 3), (11, -3), (12, -5)]⟩

theorem nb3_vacuum_weight : modularWeight nb3_vacuum = 1 / 2 := by
  unfold modularWeight nb3_vacuum
  norm_num

theorem nb3_vacuum_ceff : cEff nb3_vacuum = -119 / 330 := by
  unfold cEff nb3_vacuum
  norm_num

theorem nb3_vacuum_cusp3_ceff : cuspCEff nb3_vacuum 3 = 109 / 330 := by
  unfold cuspCEff nb3_vacuum
  norm_num

theorem nb3_vacuum_E0 : groundStateShift nb3_vacuum = 5 / 8 := by
  unfold groundStateShift nb3_vacuum
  norm_num

theorem nb3_vacuum_is_bps : isBPS nb3_vacuum := by
  unfold isBPS; exact nb3_vacuum_weight

/-- Deep Burn SUSY-breaking candidate (alternating-sign signed index, NOT a unitary BPS count).
    Factors: [(1,24),(2,23),(3,-14),(4,-24),(5,-24),(6,-24),
              (7,-24),(8,-24),(9,-24),(10,-24),(11,-24),(12,-24)].
    Note: Cusp-0 `c_eff(0) = -823/2310 < 0`, while the dominant cusp `c = 3` has
    `cuspCEff deep_burn 3 = 81859/6930 > 0`, and `onoSumDR deep_burn = -1700 ≢ 0 (mod 24)`. -/
def deep_burn : EtaQuot :=
  ⟨[(1, 24), (2, 23), (3, -14), (4, -24), (5, -24), (6, -24),
    (7, -24), (8, -24), (9, -24), (10, -24), (11, -24), (12, -24)]⟩

theorem deep_burn_weight : modularWeight deep_burn = -183 / 2 := by
  unfold modularWeight deep_burn
  norm_num

theorem deep_burn_susy_broken : isSUSYBroken deep_burn := by
  unfold isSUSYBroken
  rw [deep_burn_weight]
  norm_num

theorem deep_burn_ceff : cEff deep_burn = -823 / 2310 := by
  unfold cEff deep_burn
  norm_num

theorem deep_burn_ceff_cusp0_negative : cEff deep_burn < 0 := by
  rw [deep_burn_ceff]
  norm_num

theorem deep_burn_cusp3_ceff : cuspCEff deep_burn 3 = 81859 / 6930 := by
  unfold cuspCEff deep_burn
  norm_num

theorem deep_burn_E0 : groundStateShift deep_burn = 425 / 6 := by
  unfold groundStateShift deep_burn
  norm_num

theorem deep_burn_ono_sum_dr : onoSumDR deep_burn = -1700 := by
  unfold onoSumDR deep_burn
  norm_num

theorem deep_burn_fails_ono_mod24 : onoSumDR deep_burn % 24 ≠ 0 := by
  rw [deep_burn_ono_sum_dr]
  norm_num

-- ═══════════════════════════════════════════════════════════════════════════════
-- Batch verification utility
-- ═══════════════════════════════════════════════════════════════════════════════

/-- Given a list of factors, compute all three physical quantities at once. -/
def physicsData (eq : EtaQuot) : ℚ × ℚ × ℚ :=
  (modularWeight eq, cEff eq, groundStateShift eq)

/-- Notebook 1 Chapter I — full physics data. -/
theorem nb1_ch1_physics :
    physicsData nb1_ch1_discovery = (1/2, -25/72, -1/12) := by
  unfold physicsData modularWeight cEff groundStateShift nb1_ch1_discovery
  norm_num

-- ═══════════════════════════════════════════════════════════════════════════════
-- Task 1.7: Coefficient Extraction via Pentagonal Number Theorem
-- ═══════════════════════════════════════════════════════════════════════════════

/-- Euler's pentagonal number expansion for ∏_{n≥1}(1-q^n).
    Coefficients up to q^{len-1}. -/
def baseEta (len : ℕ) : TruncQSeries :=
  List.ofFn fun i : Fin len =>
    let n : ℤ := i.val
    let ks := List.range (i.val + 1)
    let pos_k := ks.find? (fun (k : ℕ) => (k : ℤ) * (3 * (k : ℤ) - 1) / 2 == n)
    let neg_k := ks.find? (fun (k : ℕ) => k > 0 ∧ (k : ℤ) * (3 * (k : ℤ) + 1) / 2 == n)
    match pos_k, neg_k with
    | some k, _ => if k % 2 == 0 then (1 : ℤ) else -1
    | _, some k => if k % 2 == 0 then (1 : ℤ) else -1
    | _, _ => 0

/-- Computes the first `len` Fourier coefficients of the η-quotient
    using truncated power series multiplication and inversion.
    Note: This excludes the fractional q-power (q^{k}). -/
def coeffs (eq : EtaQuot) (len : ℕ) : TruncQSeries :=
  eq.factors.foldl (fun acc dr =>
    let d := dr.1
    let r := dr.2
    if r == 0 then acc
    else
      let base := baseEta len
      let spaced := List.ofFn fun i : Fin len =>
        if i.val % d == 0 then DualScale.QSeries.coeff base (i.val / d) else 0
      if r > 0 then
        mul acc (pow spaced r.toNat len) len
      else
        mul acc (pow (inv spaced len) (-r).toNat len) len
  ) (one len)

-- Verification: nb1_ch1_discovery first 10 terms
#eval coeffs nb1_ch1_discovery 10 -- expected: [1, 0, 0, -1, 0, 0, -1, 0, -1, 1]

-- Verification: nb3_vacuum first 10 terms
#eval coeffs nb3_vacuum 10 -- expected: [1, 0, 0, 0, 0, 0, 0, 0, -6, 0]

-- Verification: Euler's Pentagonal Number Theorem for ∏(1-q^n)
#eval coeffs ⟨[(1, 1)]⟩ 10 -- expected: [1, -1, -1, 0, 0, 1, 0, 1, 0, 0]

-- Verification: Partition function p(n) for 1/∏(1-q^n)
#eval coeffs ⟨[(1, -1)]⟩ 10 -- expected: [1, 1, 2, 3, 5, 7, 11, 15, 22, 30]

end DualScale.QSeries.EtaQuotient

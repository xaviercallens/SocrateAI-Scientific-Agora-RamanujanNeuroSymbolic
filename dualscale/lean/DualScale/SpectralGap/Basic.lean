-- DualScale/SpectralGap/Basic.lean — Task M2: Spectral Gap & Falsification
-- ============================================================================
-- Definitions for Deligne's Ramanujan–Petersson bound on τ(p), the
-- Alon–Boppana spectral bound, and formal Milestone M2 falsification theorems
-- matching `dualscale/certificates/spectral/p{2,3,5}_certificate.json` and
-- `dualscale/certificates/ledger.csv`.

import Mathlib.Data.Rat.Init
import Mathlib.Data.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

namespace DualScale.SpectralGap

/-! ## Deligne's Ramanujan–Petersson Bound on τ(p) -/

/-- Deligne's bound `|τ(p)| ≤ 2 p^(11/2)` squared to exact integer arithmetic:
    `tau_p ^ 2 ≤ 4 * p ^ 11`. -/
def SatisfiesDeligneTauBound (p : ℕ) (tau_p : ℤ) : Prop :=
  tau_p ^ 2 ≤ 4 * (p : ℤ) ^ 11

/-- Certified Deligne bound instance for `p = 2, τ(2) = -24`. -/
theorem deligne_tau_p2 : SatisfiesDeligneTauBound 2 (-24) := by
  unfold SatisfiesDeligneTauBound
  norm_num

/-- Certified Deligne bound instance for `p = 3, τ(3) = 252`. -/
theorem deligne_tau_p3 : SatisfiesDeligneTauBound 3 252 := by
  unfold SatisfiesDeligneTauBound
  norm_num

/-- Certified Deligne bound instance for `p = 5, τ(5) = 4830`. -/
theorem deligne_tau_p5 : SatisfiesDeligneTauBound 5 4830 := by
  unfold SatisfiesDeligneTauBound
  norm_num

/-! ## Alon–Boppana Spectral Bound & M2 Falsification -/

/-- Alon–Boppana spectral radius bound for a `k`-regular graph: `2√(k-1)`. -/
noncomputable def alonBoppanaBound (k : ℕ) : ℝ := 2 * Real.sqrt (k - 1 : ℝ)

/-- A graph spectrum (list of eigenvalues) is Ramanujan for degree `k` if all
    elements satisfy `|x| ≤ 2√(k-1)`. -/
def isRamanujanSpectrum (k : ℕ) (eigenvalues : List ℝ) : Prop :=
  ∀ x ∈ eigenvalues, abs x ≤ alonBoppanaBound k

/-- Strict positivity of `alonBoppanaBound k` for all `k ≥ 2`. -/
theorem alonBoppanaBound_pos (k : ℕ) (hk : 2 ≤ k) :
    0 < alonBoppanaBound k := by
  unfold alonBoppanaBound
  have h_two_pos : (0 : ℝ) < 2 := by norm_num
  have h_k_cast : (2 : ℝ) ≤ (k : ℝ) := by exact Nat.cast_le.mpr hk
  have h_inside : (0 : ℝ) < (k : ℝ) - 1 := by linarith
  have h_sqrt_pos : 0 < Real.sqrt ((k : ℝ) - 1) := Real.sqrt_pos.mpr h_inside
  exact mul_pos h_two_pos h_sqrt_pos

/-- General refutation criterion: if some eigenvalue `x ∈ eigenvalues` satisfies
    `x^2 > 4(k - 1)` for `k ≥ 1`, the spectrum is not Ramanujan of degree `k`. -/
theorem not_isRamanujanSpectrum_of_sq_gt
    (k : ℕ) (hk : 1 ≤ k) (x : ℝ) (eigenvalues : List ℝ)
    (hx : x ∈ eigenvalues) (hgt : 4 * ((k : ℝ) - 1) < x ^ 2) :
    ¬ isRamanujanSpectrum k eigenvalues := by
  intro hram
  have h_abs : abs x ≤ 2 * Real.sqrt ((k : ℝ) - 1) := hram x hx
  have hk_nat : ((1 : ℕ) : ℝ) ≤ (k : ℝ) := Nat.cast_le.mpr hk
  rw [Nat.cast_one] at hk_nat
  have h_sub_nonneg : (0 : ℝ) ≤ (k : ℝ) - 1 := by linarith
  have h_sq_sqrt : (Real.sqrt ((k : ℝ) - 1)) ^ 2 = (k : ℝ) - 1 := Real.sq_sqrt h_sub_nonneg
  have h_bounds := abs_le.mp h_abs
  nlinarith [h_bounds.1, h_bounds.2, h_sq_sqrt]

private theorem not_isRamanujan_singleton_rat (k : ℕ) (hk : 1 ≤ k) (q : ℚ)
    (hgt : 4 * ((k : ℚ) - 1) < q ^ 2) :
    ¬ isRamanujanSpectrum k [(q : ℝ)] := by
  apply not_isRamanujanSpectrum_of_sq_gt k hk (q : ℝ) [(q : ℝ)] (by simp)
  exact_mod_cast hgt

/-- Exact rational `λ_2` for the `p = 2` circulant triad mock graph
    (`dualscale/certificates/spectral/p2_certificate.json`: `5.944857360942876`). -/
def triadLambda2_p2 : ℚ := 1486214340235719 / 250000000000000

/-- Exact rational `λ_2` for the `p = 3` circulant triad mock graph
    (`dualscale/certificates/spectral/p3_certificate.json`: `7.882023683200145`). -/
def triadLambda2_p3 : ℚ := 1576404736640029 / 200000000000000

/-- Exact rational `λ_2` for the `p = 5` circulant triad mock graph
    (`dualscale/certificates/spectral/p5_certificate.json`: `11.643689687566926`). -/
def triadLambda2_p5 : ℚ := 5821844843783463 / 500000000000000

/-- M2 falsification (`p = 2`, nominal degree `k = p + 1 = 3`). -/
theorem m2_triad_not_ramanujan_p2_k3 :
    ¬ isRamanujanSpectrum 3 [(triadLambda2_p2 : ℝ)] := by
  refine not_isRamanujan_singleton_rat 3 (by decide) triadLambda2_p2 ?_
  unfold triadLambda2_p2
  norm_num

/-- M2 falsification (`p = 3`, nominal degree `k = p + 1 = 4`). -/
theorem m2_triad_not_ramanujan_p3_k4 :
    ¬ isRamanujanSpectrum 4 [(triadLambda2_p3 : ℝ)] := by
  refine not_isRamanujan_singleton_rat 4 (by decide) triadLambda2_p3 ?_
  unfold triadLambda2_p3
  norm_num

/-- M2 falsification (`p = 5`, nominal degree `k = p + 1 = 6`). -/
theorem m2_triad_not_ramanujan_p5_k6 :
    ¬ isRamanujanSpectrum 6 [(triadLambda2_p5 : ℝ)] := by
  refine not_isRamanujan_singleton_rat 6 (by decide) triadLambda2_p5 ?_
  unfold triadLambda2_p5
  norm_num

/-- M2 falsification (`p = 2`, actual circulant regularity `2k = 6`). -/
theorem m2_triad_not_ramanujan_p2_reg6 :
    ¬ isRamanujanSpectrum 6 [(triadLambda2_p2 : ℝ)] := by
  refine not_isRamanujan_singleton_rat 6 (by decide) triadLambda2_p2 ?_
  unfold triadLambda2_p2
  norm_num

/-- M2 falsification (`p = 3`, actual circulant regularity `2k = 8`). -/
theorem m2_triad_not_ramanujan_p3_reg8 :
    ¬ isRamanujanSpectrum 8 [(triadLambda2_p3 : ℝ)] := by
  refine not_isRamanujan_singleton_rat 8 (by decide) triadLambda2_p3 ?_
  unfold triadLambda2_p3
  norm_num

/-- M2 falsification (`p = 5`, actual circulant regularity `2k = 12`). -/
theorem m2_triad_not_ramanujan_p5_reg12 :
    ¬ isRamanujanSpectrum 12 [(triadLambda2_p5 : ℝ)] := by
  refine not_isRamanujan_singleton_rat 12 (by decide) triadLambda2_p5 ?_
  unfold triadLambda2_p5
  norm_num

end DualScale.SpectralGap

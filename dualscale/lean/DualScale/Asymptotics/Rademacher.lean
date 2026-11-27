-- DualScale/Asymptotics/Rademacher.lean — Task 2.1: Rademacher Exact Formula
-- ============================================================================
-- Tier L hypothesis encoding of the Hardy-Ramanujan-Rademacher asymptotic
-- formula for the integer partition function p(n).
--
-- References:
--   Hardy & Ramanujan (1918), "Asymptotic Formulae in Combinatory Analysis"
--   Rademacher (1937), "On the Partition Function p(n)"

import Mathlib.Data.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import DualScale.QSeries.EtaQuotient

namespace DualScale.Asymptotics

open Real

/-! ## The Partition Function -/

/-- The classical partition function p(n), representing the number of ways
    to write n as a sum of positive integers. Extracted from the
    η-quotient 1/η(q) without the q^{1/24} shift. -/
def p (n : ℕ) : ℤ :=
  DualScale.QSeries.EtaQuotient.coeffs ⟨[(1, -1)]⟩ (n + 1) |>.getD n 0

/-! ## Hardy-Ramanujan First-Order Approximation -/

/-- The continuous first-order asymptotic approximation to p(n).
    Formula: f(n) = (1 / (4 * n * √3)) * exp(π * √(2n/3)) -/
noncomputable def partitionApprox (n : ℝ) : ℝ :=
  (1 / (4 * n * sqrt 3)) * exp (Real.pi * sqrt (2 * n / 3))

/-! ## Rademacher Exact Formula (Tier L Hypothesis) -/

/-- Tier L literature hypothesis (Hardy-Ramanujan 1918 / Rademacher 1937):
    p(n) is asymptotically equivalent to the first-order Hardy-Ramanujan
    approximation as n → ∞, i.e., lim_{n→∞} p(n) / partitionApprox(n) = 1. -/
def RademacherFirstOrderHypothesis : Prop :=
  ∀ ε > 0, ∃ N : ℝ, ∀ n : ℕ, (n : ℝ) > N →
    |((p n : ℝ) / partitionApprox (n : ℝ)) - 1| < ε

/-- Conditional Tier A corollary: under the Hardy-Ramanujan-Rademacher
    asymptotic hypothesis, p(n) is eventually strictly positive. -/
theorem partition_eventually_pos (h_rad : RademacherFirstOrderHypothesis) :
    ∃ N : ℝ, ∀ n : ℕ, (n : ℝ) > N → (0 : ℝ) < (p n : ℝ) := by
  obtain ⟨N, hN⟩ := h_rad (1 / 2) (by norm_num)
  refine ⟨max N 0, fun n hn => ?_⟩
  have hnN : (n : ℝ) > N := lt_of_le_of_lt (le_max_left N 0) hn
  have hn0 : (0 : ℝ) < (n : ℝ) := lt_of_le_of_lt (le_max_right N 0) hn
  have h_approx_pos : 0 < partitionApprox (n : ℝ) := by
    unfold partitionApprox
    apply mul_pos
    · apply div_pos zero_lt_one
      apply mul_pos (mul_pos (by norm_num) hn0)
      exact Real.sqrt_pos.mpr (by norm_num)
    · exact Real.exp_pos _
  have h_abs := hN n hnN
  rw [abs_sub_lt_iff] at h_abs
  have h_gt : (1 / 2 : ℝ) < (p n : ℝ) / partitionApprox (n : ℝ) := by
    linarith [h_abs.1]
  have h_mul : (1 / 2 : ℝ) * partitionApprox (n : ℝ) <
      ((p n : ℝ) / partitionApprox (n : ℝ)) * partitionApprox (n : ℝ) :=
    mul_lt_mul_of_pos_right h_gt h_approx_pos
  rw [div_mul_cancel₀ _ h_approx_pos.ne'] at h_mul
  have h_half_pos : (0 : ℝ) < (1 / 2 : ℝ) * partitionApprox (n : ℝ) :=
    mul_pos (by norm_num) h_approx_pos
  exact lt_trans h_half_pos h_mul

end DualScale.Asymptotics

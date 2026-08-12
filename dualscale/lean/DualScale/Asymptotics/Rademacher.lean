-- DualScale/Asymptotics/Rademacher.lean — Task 2.1: Rademacher Exact Formula
-- ============================================================================
-- Axiomatization of the Hardy-Ramanujan-Rademacher exact formula for the
-- partition function p(n). This forms the basis for the saddle-point entropy
-- bound (S_BPS = 2π) at the micro-scale.
--
-- References:
--   Hardy & Ramanujan (1918), "Asymptotic Formulae in Combinatory Analysis"
--   Rademacher (1937), "On the Partition Function p(n)"

import Mathlib.Data.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
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

/-! ## Rademacher Exact Formula Axiomatization -/

/-- Rademacher's theorem guarantees that p(n) is asymptotically equivalent
    to the first-order Hardy-Ramanujan approximation as n → ∞.
    Specifically, lim_{n→∞} p(n) / partitionApprox(n) = 1.
    We axiomatize this physical limit to bridge the discrete q-series
    with the continuous BPS entropy scaling. -/
axiom rademacher_first_order :
  ∀ ε > 0, ∃ N : ℝ, ∀ n : ℕ, (n : ℝ) > N → 
    |((p n : ℝ) / partitionApprox (n : ℝ)) - 1| < ε

end DualScale.Asymptotics

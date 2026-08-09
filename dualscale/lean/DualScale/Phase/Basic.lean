-- DualScale/Phase/Basic.lean — Singular set / continued fractions scaffold
-- =========================================================================
-- Definitions for Conjecture 4: singular-set dimension and
-- continued-fraction topological states.

import Mathlib.Data.Rat.Basic

namespace DualScale.Phase

/-- Hausdorff dimension of the singular set of suitable weak solutions.
    CKN (1982) proves dim ≤ 1. Conjecture 4(i) claims dim = 0.
    OPEN: requires T2 for proper measure-theoretic formalization. -/
noncomputable def singularSetDimension : ℝ := 0

/-- Conjecture 4(i): the singular set has Hausdorff dimension zero.
    OPEN TARGET — strictly stronger than CKN. -/
theorem singularSet_dim_zero :
    singularSetDimension = 0 := by
  sorry

/-- Number of non-communicating topological states selected by the
    truncated flow as α' → 0, indexed by continued-fraction limit classes.
    OPEN: requires T2 for the Rogers–Ramanujan limit theory. -/
noncomputable def numTopologicalStates : ℕ := 0

/-- Conjecture 4(ii): finitely many discrete states, not a blow-up continuum.
    OPEN TARGET. -/
theorem finitely_many_limit_states :
    0 < numTopologicalStates := by
  sorry

end DualScale.Phase

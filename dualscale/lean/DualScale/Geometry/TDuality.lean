-- DualScale/Geometry/TDuality.lean — Task 2.8: T-Duality Bridge
-- ============================================================================
-- Formalizes the T-duality involution R ↔ α'/R on circle compactifications
-- with an explicit positive Regge slope parameter `alpha_prime > 0`, and
-- defines T-duality invariance as an explicit Tier C hypothesis predicate on
-- observables rather than pinning `alpha_prime := 1` or asserting global axioms.

import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp

namespace DualScale.Geometry

/-! ## T-Duality Target Space Geometry -/

/-- The target space topology containing the compactification radius `R > 0`. -/
structure StringVacuum where
  radius : ℝ
  h_rad  : radius > 0

/-- T-duality maps a string vacuum on a circle of radius `R`
    to a dual vacuum on a circle of radius `alpha_prime / R`
    for an explicit Regge slope parameter `alpha_prime > 0`. -/
noncomputable def tDual (alpha_prime : ℝ) (h_alpha : 0 < alpha_prime)
    (v : StringVacuum) : StringVacuum :=
  ⟨alpha_prime / v.radius, div_pos h_alpha v.h_rad⟩

/-- Tier A involution: applying `tDual alpha_prime h_alpha` twice
    restores the original compactification radius. -/
theorem tDual_involutive (alpha_prime : ℝ) (h_alpha : 0 < alpha_prime)
    (v : StringVacuum) :
    (tDual alpha_prime h_alpha (tDual alpha_prime h_alpha v)).radius = v.radius := by
  have ha : alpha_prime ≠ 0 := ne_of_gt h_alpha
  have hr : v.radius ≠ 0 := ne_of_gt v.h_rad
  dsimp [tDual]
  field_simp [ha, hr] <;> first | rfl | exact mul_comm _ _

/-- Explicit Tier C hypothesis predicate expressing that a physical observable
    `obs` is invariant under the T-duality map `v ↦ tDual alpha_prime h_alpha v`.
    Physical spectrum invariance under T-duality is modeled as an explicit
    hypothesis parameter (Tier C), never as a global axiom. -/
def IsTDualInvariant (alpha_prime : ℝ) (h_alpha : 0 < alpha_prime)
    (obs : StringVacuum → ℝ) : Prop :=
  ∀ v : StringVacuum, obs (tDual alpha_prime h_alpha v) = obs v

/-- Tier A invariance of the symmetric radius-momentum combination
    `R + alpha_prime / R` under `tDual alpha_prime h_alpha`. -/
theorem symmetric_radius_invariant (alpha_prime : ℝ) (h_alpha : 0 < alpha_prime) :
    IsTDualInvariant alpha_prime h_alpha (fun v => v.radius + alpha_prime / v.radius) := by
  intro v
  have h_inv := tDual_involutive alpha_prime h_alpha v
  dsimp [tDual] at h_inv ⊢
  rw [h_inv, add_comm]

/-- Tier A self-dual radius characterization: a vacuum is fixed in radius by
    `tDual alpha_prime h_alpha` if and only if `R ^ 2 = alpha_prime`. -/
theorem tDual_self_dual_iff (alpha_prime : ℝ) (h_alpha : 0 < alpha_prime)
    (v : StringVacuum) :
    (tDual alpha_prime h_alpha v).radius = v.radius ↔ v.radius ^ 2 = alpha_prime := by
  have _ := h_alpha
  dsimp [tDual]
  rw [div_eq_iff (ne_of_gt v.h_rad), ← sq, eq_comm]

end DualScale.Geometry

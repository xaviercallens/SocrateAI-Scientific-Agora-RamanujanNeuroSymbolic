-- DualScale/Physics/PhaseTransition.lean — Task 3.6: Phase Transition Map
-- ============================================================================
-- Models the Hagedorn divergence as an explicit structure `HagedornSystem`
-- with a concrete analytic witness `canonicalHagedornSystem` proving
-- non-emptiness without global axioms.
--
-- References:
--   Hagedorn (1965), "Statistical thermodynamics of strong interactions at high energies"

import Mathlib.Data.Real.Basic
import DualScale.Physics.Enstrophy

namespace DualScale.Physics

open DualScale.Asymptotics

/-! ## Thermodynamics & Hagedorn Temperature -/

/-- Parameterized thermodynamic system exhibiting Hagedorn entropy divergence
    as temperature `T` approaches `T_H > 0` from below. -/
structure HagedornSystem where
  T_H : ℝ
  t_h_pos : 0 < T_H
  entropy_at_temp : ℝ → ℝ
  hagedorn_divergence :
    ∀ M : ℝ, ∃ δ > 0, ∀ T < T_H, T_H - T < δ → entropy_at_temp T > M

/-- Concrete analytic witness (`S(T) = 1 / (T_H - T)`) proving that
    `HagedornSystem` is inhabited for any `T_H > 0`. -/
noncomputable def canonicalHagedornSystem (T_H : ℝ) (hT : 0 < T_H) : HagedornSystem where
  T_H := T_H
  t_h_pos := hT
  entropy_at_temp := fun T => 1 / (T_H - T)
  hagedorn_divergence := by
    intro M
    have h_max_pos : 0 < max M 1 := lt_of_lt_of_le zero_lt_one (le_max_right M 1)
    refine ⟨1 / max M 1, div_pos zero_lt_one h_max_pos, ?_⟩
    intro T hT_lt h_diff
    have h_pos_diff : 0 < T_H - T := sub_pos.mpr hT_lt
    have h_mul : (T_H - T) * max M 1 < 1 := (lt_div_iff₀ h_max_pos).mp h_diff
    have h_inv : max M 1 < 1 / (T_H - T) := by
      refine (lt_div_iff₀ h_pos_diff).mpr ?_
      rw [mul_comm]
      exact h_mul
    exact lt_of_le_of_lt (le_max_left M 1) h_inv

end DualScale.Physics

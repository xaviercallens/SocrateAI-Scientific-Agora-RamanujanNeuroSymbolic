import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Summable
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum

namespace RAMA.Holography

open Real

/-!
# Holographic Fourier-Decay Ansatz (Tier C Model + Tier A Comparison Step)

NOTE: `IsHolographicallyDual` is a Tier C physical ansatz positing exponential
Fourier mode decay `v_hat(n)^2 ≤ 1 / BPS_Microstate_Growth c_eff n` rather than
an unconditional proof of Navier-Stokes regularity. Given this ansatz and an
explicit summability hypothesis `h_exp_decay`, the comparison step proving
`HasFiniteEnstrophy v_hat` is Tier A real analysis.
-/

/-- Continuous Rademacher-like bounding envelope for microstate growth at `c_eff > 0`. -/
noncomputable def BPS_Microstate_Growth (c_eff : ℝ) (n : ℕ) : ℝ :=
  Real.exp (2 * Real.pi * Real.sqrt (c_eff * (n : ℝ) / 6))

/-- Tier C holographic Fourier-decay ansatz: the n-th mode energy is bounded
    by the inverse of the bulk microstate growth envelope. -/
def IsHolographicallyDual (v_hat : ℕ → ℝ) (c_eff : ℝ) : Prop :=
  ∀ n > 0, (v_hat n)^2 ≤ 1 / BPS_Microstate_Growth c_eff n

/-- Enstrophy-like weighted Fourier series convergence predicate. -/
def HasFiniteEnstrophy (v_hat : ℕ → ℝ) : Prop :=
  Summable (fun n ↦ ((n : ℝ) ^ (3 / 2 : ℝ)) * (v_hat n)^2)

/-- Conditional Tier A comparison theorem:
    assuming the Tier C ansatz `IsHolographicallyDual v_hat c_eff` with `c_eff > 0`
    and the explicit analytic summability hypothesis `h_exp_decay`, the weighted
    mode-energy series `HasFiniteEnstrophy v_hat` is summable. -/
theorem bps_halts_kolmogorov_cascade
    (v_hat : ℕ → ℝ) (c_eff : ℝ)
    (hc : c_eff > 0)
    (h_dual : IsHolographicallyDual v_hat c_eff)
    (h_exp_decay : 0 < c_eff →
      Summable (fun n : ℕ => ((n : ℝ) ^ (3 / 2 : ℝ)) / BPS_Microstate_Growth c_eff n)) :
    HasFiniteEnstrophy v_hat := by
  have h_sum := h_exp_decay hc
  apply summable_of_nonneg_of_le
  · intro n
    have hn_nonneg : (n : ℝ) ^ (3 / 2 : ℝ) ≥ 0 :=
      Real.rpow_nonneg (Nat.cast_nonneg n) (3 / 2 : ℝ)
    exact mul_nonneg hn_nonneg (sq_nonneg (v_hat n))
  · intro n
    by_cases hn : n = 0
    · subst hn
      simp [Real.zero_rpow (by norm_num : (3 / 2 : ℝ) ≠ 0)]
    · have hn_pos : n > 0 := Nat.pos_of_ne_zero hn
      have hn_nonneg : (n : ℝ) ^ (3 / 2 : ℝ) ≥ 0 :=
        Real.rpow_nonneg (Nat.cast_nonneg n) (3 / 2 : ℝ)
      calc
        ((n : ℝ) ^ (3 / 2 : ℝ)) * (v_hat n)^2
          _ ≤ ((n : ℝ) ^ (3 / 2 : ℝ)) * (1 / BPS_Microstate_Growth c_eff n)
              := mul_le_mul_of_nonneg_left (h_dual n hn_pos) hn_nonneg
          _ = ((n : ℝ) ^ (3 / 2 : ℝ)) / BPS_Microstate_Growth c_eff n
              := mul_one_div ((n : ℝ) ^ (3 / 2 : ℝ)) (BPS_Microstate_Growth c_eff n)
  exact h_sum

end RAMA.Holography

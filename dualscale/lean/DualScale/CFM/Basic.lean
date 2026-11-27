-- DualScale/CFM/Basic.lean — Task M3.2: CFM Vortex Direction Constraint
-- =======================================================================
-- Definitions for the Constantin–Fefferman–Majda (CFM) vortex direction
-- constraint and exact Milestone M3 refutation matching
-- `dualscale/certificates/cfm_ledger.csv` and
-- `dualscale/numerics/elliptic/cfm_elliptic_angle.py`.

import Mathlib.Data.Rat.Init
import Mathlib.Data.Real.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

namespace DualScale.CFM

/-- Truncation angle of the incomplete elliptic integral attached
    to the fiber, determined by the T-dual cutoff `alphaPrime`. -/
noncomputable def truncationAngle (alphaPrime : ℚ) : ℝ :=
  (alphaPrime : ℝ) * Real.pi / 2

/-- Lipschitz modulus of the vorticity direction field under Galerkin truncation,
    parameterized by the fiber geometric constant `C`. -/
noncomputable def lipschitzModulus_xi (C : ℝ) (alphaPrime : ℚ) : ℝ :=
  C * truncationAngle alphaPrime

/-- Positivity of `truncationAngle alphaPrime` for positive T-dual cutoff `alphaPrime > 0`. -/
theorem truncationAngle_pos (alphaPrime : ℚ) (hpos : 0 < alphaPrime) :
    0 < truncationAngle alphaPrime := by
  unfold truncationAngle
  exact div_pos (mul_pos (Rat.cast_pos.mpr hpos) Real.pi_pos) (by norm_num)

/-- Leading-order rational coefficient `4/3` for the Constantin–Fefferman–Majda
    vorticity direction bound (`cfm_ledger.csv`: `4/3*pi`). -/
def cfmLeadingCoeff : ℚ := 4 / 3

/-- Leading-order rational coefficient `16/9` from the fiber elliptic-angle
    expansion (`cfm_ledger.csv`: `16/9*pi`). -/
def ellipticLeadingCoeff : ℚ := 16 / 9

/-- Real leading-order CFM constant `(4/3) * π`. -/
noncomputable def cfmLeadingReal : ℝ :=
  (cfmLeadingCoeff : ℝ) * Real.pi

/-- Real leading-order elliptic-angle constant `(16/9) * π`. -/
noncomputable def ellipticLeadingReal : ℝ :=
  (ellipticLeadingCoeff : ℝ) * Real.pi

/-- Exact rational mismatch between the CFM coefficient and the elliptic fiber coefficient. -/
theorem cfm_coeff_ne_elliptic_coeff :
    cfmLeadingCoeff ≠ ellipticLeadingCoeff := by
  unfold cfmLeadingCoeff ellipticLeadingCoeff
  norm_num

/-- Milestone M3 exact refutation: the elliptic-angle constant `(16/9) * π`
    exceeds the CFM leading-order constant `(4/3) * π` by `(4/9) * π ≠ 0`,
    reconciling with `dualscale/certificates/cfm_ledger.csv` (`Status=FAIL`). -/
theorem cfm_elliptic_angle_refuted :
    ellipticLeadingReal - cfmLeadingReal = ((4 / 9 : ℚ) : ℝ) * Real.pi ∧
      ellipticLeadingReal ≠ cfmLeadingReal := by
  have h_coeff_diff : ellipticLeadingCoeff - cfmLeadingCoeff = (4 / 9 : ℚ) := by
    unfold ellipticLeadingCoeff cfmLeadingCoeff
    norm_num
  have h_diff : ellipticLeadingReal - cfmLeadingReal = ((4 / 9 : ℚ) : ℝ) * Real.pi := by
    unfold ellipticLeadingReal cfmLeadingReal
    rw [← sub_mul, ← Rat.cast_sub, h_coeff_diff]
  have hq_pos : (0 : ℚ) < (4 / 9 : ℚ) := by norm_num
  have h_ne_zero : ellipticLeadingReal - cfmLeadingReal ≠ 0 := by
    rw [h_diff]
    exact mul_ne_zero (Rat.cast_pos.mpr hq_pos).ne' Real.pi_pos.ne'
  exact ⟨h_diff, sub_ne_zero.mp h_ne_zero⟩

/-- Any fiber geometric constant `C` matching the elliptic leading-order angle
    `ellipticLeadingReal` at `alphaPrime` fails to match `cfmLeadingReal`. -/
theorem lipschitzModulus_ne_cfm_of_elliptic
    (alphaPrime : ℚ) (C : ℝ)
    (h_match : lipschitzModulus_xi C alphaPrime = ellipticLeadingReal) :
    lipschitzModulus_xi C alphaPrime ≠ cfmLeadingReal := by
  rw [h_match]
  exact cfm_elliptic_angle_refuted.2

/-- Witness existence: for any positive T-dual cutoff `alphaPrime > 0`, there
    exists a positive fiber geometric constant `C > 0` realizing
    `ellipticLeadingReal`, and any such realization fails to equal `cfmLeadingReal`. -/
theorem exists_pos_lipschitzModulus_eq_elliptic_ne_cfm
    (alphaPrime : ℚ) (hpos : 0 < alphaPrime) :
    ∃ C : ℝ, 0 < C ∧
      lipschitzModulus_xi C alphaPrime = ellipticLeadingReal ∧
      lipschitzModulus_xi C alphaPrime ≠ cfmLeadingReal := by
  have h_ang_pos : 0 < truncationAngle alphaPrime := truncationAngle_pos alphaPrime hpos
  have h_ell_coeff_pos : (0 : ℚ) < ellipticLeadingCoeff := by
    unfold ellipticLeadingCoeff
    norm_num
  have h_ell_pos : 0 < ellipticLeadingReal := by
    unfold ellipticLeadingReal
    exact mul_pos (Rat.cast_pos.mpr h_ell_coeff_pos) Real.pi_pos
  have h_eq :
      lipschitzModulus_xi (ellipticLeadingReal / truncationAngle alphaPrime) alphaPrime =
        ellipticLeadingReal := by
    unfold lipschitzModulus_xi
    exact div_mul_cancel₀ ellipticLeadingReal (ne_of_gt h_ang_pos)
  exact ⟨ellipticLeadingReal / truncationAngle alphaPrime,
    div_pos h_ell_pos h_ang_pos, h_eq,
    lipschitzModulus_ne_cfm_of_elliptic alphaPrime _ h_eq⟩

end DualScale.CFM

import Mathlib.Analysis.Calculus.FDeriv.Basic
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Data.Complex.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

namespace DualScale.NS.DyadicShell

/-!
# Dyadic Shell Model (Katz-Pavlović / Desnyansky-Novikov)
This file defines the dyadic shell ODE system modeling the energy cascade
along a 1D dyadic lattice, proves the Tier A UV-cutoff and telescoping
energy-dissipation identities for truncated states, and states arbitrary-data
global well-posedness (`GlobalWellPosednessRegularized`) as an OPEN Tier C target.
-/

/-- Wave number of the n-th dyadic shell. -/
noncomputable def k_n (n : ℕ) : ℝ := (2 : ℝ) ^ n

/-- Viscosity of the fluid. -/
noncomputable def nu : ℝ := 1 / 100

/-- The state of the shell model is a sequence of real numbers (velocities). -/
def ShellState := ℕ → ℝ

/-- The unregularized Katz-Pavlović dyadic shell ODE right-hand side. -/
noncomputable def shell_rhs (u : ShellState) (n : ℕ) : ℝ :=
  if n = 0 then
    - k_n 1 * u 0 * u 1 - nu * (k_n 0)^2 * u 0
  else
    k_n n * (u (n - 1))^2 - k_n (n + 1) * u n * u (n + 1) - nu * (k_n n)^2 * u n

/-- The T-dual regularization operator applied to the shell model. -/
noncomputable def regularize (alphaPrime : ℝ) (u : ShellState) (n : ℕ) : ℝ :=
  if (k_n n) > (1 / Real.sqrt alphaPrime) then 0 else u n

/-- TIER A PROOF: Finite Active Modes (UV Cutoff).
    The T-dual regularization zeros out all shell modes with `k_n n > 1 / √α'`. -/
theorem regularize_uv_cutoff (alphaPrime : ℝ) (u : ShellState) (n : ℕ)
    (h_cutoff : k_n n > 1 / Real.sqrt alphaPrime) :
    regularize alphaPrime u n = 0 := by
  dsimp [regularize]
  rw [if_pos h_cutoff]

/-- The regularized ODE system for the dyadic shell model. -/
def IsRegularizedSolution (alphaPrime : ℝ) (u : ℝ → ShellState) : Prop :=
  ∀ (t : ℝ) (n : ℕ),
    HasDerivAt (fun t' => u t' n) (regularize alphaPrime (shell_rhs (u t)) n) t

/-- Finite-energy / UV-truncated initial data compatible with `alphaPrime`. -/
def IsFiniteEnergyInitialData (alphaPrime : ℝ) (u0 : ShellState) : Prop :=
  ∀ n, k_n n > 1 / Real.sqrt alphaPrime → u0 n = 0

/-- OPEN Tier C target: global existence and uniqueness of regularized dyadic-shell
    solutions for arbitrary UV-truncated initial data `u0`. -/
def GlobalWellPosednessRegularized (alphaPrime : ℝ) : Prop :=
  ∀ u0 : ShellState, IsFiniteEnergyInitialData alphaPrime u0 →
    ∃! u : ℝ → ShellState, u 0 = u0 ∧ IsRegularizedSolution alphaPrime u

/-- TIER A (Trivial Zero Equilibrium Only):
    Exhibits the identically zero steady state `u ≡ 0` as a solution to the
    regularized shell system. Does NOT establish existence or uniqueness for
    arbitrary initial data `u0`. -/
theorem trivial_zero_solution_exists (alphaPrime : ℝ) (_h_alpha : 0 < alphaPrime) :
    ∃ (u : ℝ → ShellState), IsRegularizedSolution alphaPrime u := by
  use fun _ _ => 0
  intro t n
  have h_rhs_zero : regularize alphaPrime (shell_rhs (fun _ => 0)) n = 0 := by
    unfold regularize
    split_ifs
    · rfl
    · unfold shell_rhs
      split_ifs
      · ring
      · ring
  rw [h_rhs_zero]
  exact hasDerivAt_const t 0

/-- General Tier A telescoping identity for the dyadic shell nonlinear flux up to shell `N`. -/
lemma telescoping_energy_identity (u : ShellState) (N : ℕ) :
    (Finset.range (N + 1)).sum (fun n => u n * shell_rhs u n) =
      - k_n (N + 1) * (u N)^2 * u (N + 1) -
        nu * (Finset.range (N + 1)).sum (fun n => (k_n n)^2 * (u n)^2) := by
  induction N with
  | zero =>
    simp [Finset.sum_range_succ, shell_rhs]
    ring
  | succ N ih =>
    rw [Finset.sum_range_succ, Finset.sum_range_succ, ih]
    have h_rhs : shell_rhs u (N + 1) =
        k_n (N + 1) * (u N)^2 - k_n (N + 2) * u (N + 1) * u (N + 2) -
          nu * (k_n (N + 1))^2 * u (N + 1) := by
      simp [shell_rhs]
    rw [h_rhs]
    ring

/-- TIER A PROOF: Exact telescoping energy dissipation for any UV-truncated shell
    state vanishing above shell `N`. Nonlinear flux cancels pairwise, leaving pure
    viscous dissipation `-nu * ∑_{n≤N} k_n^2 u_n^2`. -/
theorem telescoping_energy_dissipation (u : ShellState) (N : ℕ)
    (h_cut : ∀ n, N < n → u n = 0) :
    (Finset.range (N + 1)).sum (fun n => u n * shell_rhs u n) =
      - nu * (Finset.range (N + 1)).sum (fun n => (k_n n)^2 * (u n)^2) := by
  rw [telescoping_energy_identity u N, h_cut (N + 1) (Nat.lt_succ_self N)]
  ring

/-- TIER A COROLLARY: Energy dissipation rate is non-positive for UV-truncated states. -/
theorem telescoping_energy_dissipation_nonpos (u : ShellState) (N : ℕ)
    (h_cut : ∀ n, N < n → u n = 0) :
    (Finset.range (N + 1)).sum (fun n => u n * shell_rhs u n) ≤ 0 := by
  rw [telescoping_energy_dissipation u N h_cut]
  have h_sum_nonneg : 0 ≤ (Finset.range (N + 1)).sum (fun n => (k_n n)^2 * (u n)^2) :=
    Finset.sum_nonneg (fun n _ => mul_nonneg (sq_nonneg _) (sq_nonneg _))
  have h_nu_nonneg : (0 : ℝ) ≤ nu := by unfold nu; norm_num
  nlinarith

end DualScale.NS.DyadicShell

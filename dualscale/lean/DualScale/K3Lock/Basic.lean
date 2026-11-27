-- DualScale/K3Lock/Basic.lean — Task M4: Sym^2 Recurrence Lock & S12 Audit
-- ==========================================================================
-- Formalizes second- and third-order linear recurrence operators and their
-- Sym^2(L2) bridge, preserves the Tier A constant- and variable-coefficient
-- Sym^2 recurrence lock theorems, and records exact rational values for the
-- S12 Apéry ζ(3) sequence alongside explicit Tier X provenance notes.

import Mathlib.Data.Rat.Init
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum

namespace DualScale.K3Lock

/-! ## Second-Order and Third-Order Recurrence Operators -/

/-- A variable-coefficient second-order linear recurrence operator
    `L2(u)_n = u_{n+2} + coeff1(n) * u_{n+1} + coeff0(n) * u_n`. -/
structure SecondOrderRecurrence where
  coeff1 : ℕ → ℝ
  coeff0 : ℕ → ℝ

/-- Predicate stating that `L2` annihilates a sequence `u : ℕ → ℝ` for all `n`. -/
def SecondOrderRecurrence.Annihilates (L2 : SecondOrderRecurrence) (u : ℕ → ℝ) : Prop :=
  ∀ n, u (n + 2) + L2.coeff1 n * u (n + 1) + L2.coeff0 n * u n = 0

/-- A variable-coefficient third-order linear recurrence operator
    `L3(v)_n = v_{n+3} + coeff2(n) * v_{n+2} + coeff1(n) * v_{n+1} + coeff0(n) * v_n`. -/
structure ThirdOrderRecurrence where
  coeff2 : ℕ → ℝ
  coeff1 : ℕ → ℝ
  coeff0 : ℕ → ℝ

/-- Predicate stating that `L3` annihilates a sequence `v : ℕ → ℝ` for all `n`. -/
def ThirdOrderRecurrence.Annihilates (L3 : ThirdOrderRecurrence) (v : ℕ → ℝ) : Prop :=
  ∀ n, v (n + 3) + L3.coeff2 n * v (n + 2) + L3.coeff1 n * v (n + 1) + L3.coeff0 n * v n = 0

/-- The symmetric-square third-order recurrence operator `Sym^2(L2)` attached
    to a second-order recurrence `L2` (well-defined wherever `L2.coeff1 n ≠ 0`). -/
noncomputable def symSquareRecurrence (L2 : SecondOrderRecurrence) : ThirdOrderRecurrence :=
  { coeff2 := fun n =>
      -L2.coeff1 (n + 1) * (L2.coeff1 (n + 1) * L2.coeff1 n - L2.coeff0 (n + 1)) / L2.coeff1 n
    coeff1 := fun n =>
      L2.coeff1 (n + 1) * L2.coeff1 n * L2.coeff0 (n + 1) - (L2.coeff0 (n + 1)) ^ 2
    coeff0 := fun n =>
      -L2.coeff1 (n + 1) * L2.coeff0 (n + 1) * (L2.coeff0 n) ^ 2 / L2.coeff1 n }

/--
  Operator-form Sym^2 Recurrence Lock (Tier A).
  If `L2` annihilates `u` and `L2.coeff1 n ≠ 0` for all `n`, then
  `symSquareRecurrence L2` annihilates the squared sequence `n ↦ (u n)^2`.
-/
theorem symSquareRecurrence_annihilates_sq (L2 : SecondOrderRecurrence) (u : ℕ → ℝ)
    (ha : ∀ n, L2.coeff1 n ≠ 0) (hu : L2.Annihilates u) :
    (symSquareRecurrence L2).Annihilates (fun n => (u n) ^ 2) := by
  intro n
  dsimp [ThirdOrderRecurrence.Annihilates, symSquareRecurrence]
  have h1 : u (n + 2) = -L2.coeff1 n * u (n + 1) - L2.coeff0 n * u n := by
    linarith [hu n]
  have h2 : u (n + 3) = -L2.coeff1 (n + 1) * u (n + 2) - L2.coeff0 (n + 1) * u (n + 1) := by
    linarith [hu (n + 1)]
  have han : L2.coeff1 n ≠ 0 := ha n
  have h_sub : u (n + 3) =
      -L2.coeff1 (n + 1) * (-L2.coeff1 n * u (n + 1) - L2.coeff0 n * u n) -
        L2.coeff0 (n + 1) * u (n + 1) := by
    rw [h2, h1]
  rw [h_sub, h1]
  have h_mul : L2.coeff1 n *
      ((-L2.coeff1 (n + 1) * (-L2.coeff1 n * u (n + 1) - L2.coeff0 n * u n) -
          L2.coeff0 (n + 1) * u (n + 1)) ^ 2 +
        -L2.coeff1 (n + 1) * (L2.coeff1 (n + 1) * L2.coeff1 n - L2.coeff0 (n + 1)) /
          L2.coeff1 n * (-L2.coeff1 n * u (n + 1) - L2.coeff0 n * u n) ^ 2 +
        (L2.coeff1 (n + 1) * L2.coeff1 n * L2.coeff0 (n + 1) - (L2.coeff0 (n + 1)) ^ 2) *
          u (n + 1) ^ 2 +
        -L2.coeff1 (n + 1) * L2.coeff0 (n + 1) * L2.coeff0 n ^ 2 / L2.coeff1 n *
          u n ^ 2) = 0 := by
    field_simp [han]
    ring
  exact (mul_eq_zero.mp h_mul).resolve_left han

/--
  The generalized Sym^2 Recurrence Lock (Tier A Foundation).
  If a sequence `u_n` satisfies a second-order linear recurrence `L2` with
  constant coefficients `a` and `b`:
    `u_{n+2} + a * u_{n+1} + b * u_n = 0`
  then `v_n = (u_n)^2` satisfies a third-order recurrence `L3 = Sym^2(L2)`:
    `v_{n+3} + A * v_{n+2} + B * v_{n+1} + C * v_n = 0`.
-/
theorem sym2_recurrence (a b : ℝ) (u : ℕ → ℝ)
    (hL2 : ∀ n, u (n + 2) + a * u (n + 1) + b * u n = 0) :
    ∃ (A B C : ℝ), ∀ n,
      (u (n + 3))^2 + A * (u (n + 2))^2 + B * (u (n + 1))^2 + C * (u n)^2 = 0 := by
  use (b - a^2), (a^2 * b - b^2), (-b^3)
  intro n
  have h1 : u (n + 2) = -a * u (n + 1) - b * u n := by
    linarith [hL2 n]
  have h2 : u (n + 3) = -a * u (n + 2) - b * u (n + 1) := by
    linarith [hL2 (n + 1)]
  rw [h2, h1]
  ring

/--
  Variable-Coefficient Sym^2 Recurrence Lock (Tier A Extension).
  Extends `sym2_recurrence` from constant coefficients to variable polynomial
  coefficients `a(n)` and `b(n)`, directly modeling the Picard–Fuchs operators
  of Cooper's sequences (`s_7`, `s_10`, `S_22`).
-/
theorem sym2_recurrence_variable (a b : ℕ → ℝ) (u : ℕ → ℝ) (ha : ∀ n, a n ≠ 0)
    (hL2 : ∀ n, u (n + 2) + a n * u (n + 1) + b n * u n = 0) :
    ∃ (A B C : ℕ → ℝ), ∀ n,
      (u (n + 3))^2 + A n * (u (n + 2))^2 + B n * (u (n + 1))^2 + C n * (u n)^2 = 0 := by
  let L2 : SecondOrderRecurrence := { coeff1 := a, coeff0 := b }
  exact ⟨(symSquareRecurrence L2).coeff2, (symSquareRecurrence L2).coeff1,
    (symSquareRecurrence L2).coeff0, symSquareRecurrence_annihilates_sq L2 u ha hL2⟩

/-! ## S12 Apéry Recurrence & Order Bookkeeping (Tier X Provenance Warning) -/

private def s12AperyPair : ℕ → ℚ × ℚ
  | 0 => (1, 5)
  | n + 1 =>
    ((s12AperyPair n).2,
      ((34 * ((n + 1 : ℕ) : ℚ) ^ 3 + 51 * ((n + 1 : ℕ) : ℚ) ^ 2 +
          27 * ((n + 1 : ℕ) : ℚ) + 5) * (s12AperyPair n).2 -
        ((n + 1 : ℕ) : ℚ) ^ 3 * (s12AperyPair n).1) / ((n + 2 : ℕ) : ℚ) ^ 3)

/-- Exact rational coefficients `u_n` of the Apéry `ζ(3)` sequence (`OEIS A005259`)
    recorded in `dualscale/refs/values.json` under `s12_recurrence`:
      `(n + 1)^3 u_{n+1} = (34 n^3 + 51 n^2 + 27 n + 5) u_n - n^3 u_{n-1}`
    with `u_0 = 1, u_1 = 5`.
    WARNING: `values.json`'s `s12_recurrence` is Apéry's order-3 sequence, and
    `dualscale/certificates/moduli_map/S12_vs_K3.json` and `S12_vs_elliptic.json`
    are Tier X mock-proxy checks generated by `check_C3b_moduli_map.py`, NOT an
    algebraic-geometric identification of `S12` with an order-2 elliptic ODE. -/
def s12AperyRecurrenceCoeff (n : ℕ) : ℚ :=
  (s12AperyPair n).1

/-- Exact 5th Apéry coefficient `u_5 = 819005` matching `check_C3b_moduli_map.py`. -/
theorem s12Apery_u5_eq :
    s12AperyRecurrenceCoeff 5 = 819005 := by
  simp only [s12AperyRecurrenceCoeff, s12AperyPair]
  norm_num

/-- Exact mock residual `u_5 - 54000 = 765005 ≠ 0` matching
    `dualscale/certificates/moduli_map/S12_vs_K3.json` (`residual: "765005"`). -/
theorem s12Apery_k3_mock_residual :
    s12AperyRecurrenceCoeff 5 - 54000 = 765005 ∧
      s12AperyRecurrenceCoeff 5 - 54000 ≠ 0 := by
  rw [s12Apery_u5_eq]
  norm_num

/-- Nominal Picard–Fuchs ODE order of a second-order elliptic curve family. -/
def ellipticPfOrder : ℕ := 2

/-- Nominal Picard–Fuchs ODE order of a third-order K3 Calabi–Yau 2-fold family. -/
def k3PfOrder : ℕ := 3

/-- Nominal ODE-order inequality `2 ≠ 3` between second-order elliptic and
    third-order K3 Picard–Fuchs operators.
    WARNING: This purely compares the nominal integers `ellipticPfOrder` and
    `k3PfOrder`; `values.json`'s `s12_recurrence` is Apéry's order-3 sequence
    and `S12_vs_K3.json` / `S12_vs_elliptic.json` are Tier X mock-proxy checks
    (`check_C3b_moduli_map.py`), so this lemma makes no claim about `S12`. -/
theorem elliptic_pf_order_ne_k3 :
    ellipticPfOrder ≠ k3PfOrder := by
  decide

end DualScale.K3Lock

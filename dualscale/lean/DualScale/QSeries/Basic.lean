-- DualScale/QSeries/Basic.lean — Task 1.1: Formal Power Series Ring
-- ====================================================================
-- Foundation: q-series as formal power series over ℤ (or ℚ).
-- This provides the algebraic substrate for all eta-quotient computations
-- WITHOUT requiring convergence proofs (formal power series are algebraic,
-- not analytic objects).
--
-- Reference: Ono (2004) §1.1, Hardy-Ramanujan (1918)

import Mathlib.Data.Rat.Init
import Mathlib.Data.Int.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Data.List.Basic

namespace DualScale.QSeries

/-! ## Truncated q-Series Representation

We represent q-series as finite lists of coefficients (truncated formal
power series). This is computationally effective and avoids the need for
Mathlib's `PowerSeries` infrastructure, which is not yet fully mature for
concrete coefficient extraction.

A q-series `f(q) = ∑_{n=0}^{N-1} a(n) q^n` is represented as `List ℤ`
where the i-th element is `a(i)`.
-/

/-- A truncated q-series: the list `[a₀, a₁, ..., a_{N-1}]` represents
    `a₀ + a₁q + a₂q² + ... + a_{N-1}q^{N-1}`. -/
abbrev TruncQSeries := List ℤ

/-- Extract the n-th coefficient from a truncated q-series. Returns 0 if
    the index is out of bounds. -/
def coeff (f : TruncQSeries) (n : ℕ) : ℤ :=
  f.getD n 0

/-- The zero q-series. -/
def zero (len : ℕ) : TruncQSeries :=
  List.replicate len 0

/-- The identity q-series `1 + 0q + 0q² + ...`. -/
def one (len : ℕ) : TruncQSeries :=
  1 :: List.replicate (len - 1) 0

/-- Add two truncated q-series coefficient-wise. -/
def add (f g : TruncQSeries) : TruncQSeries :=
  let n := max f.length g.length
  List.ofFn fun i : Fin n => coeff f i.val + coeff g i.val

/-- Negate a truncated q-series. -/
def neg (f : TruncQSeries) : TruncQSeries :=
  f.map (· * (-1))

/-- Multiply two truncated q-series (convolution of coefficients).
    Result is truncated to length `len`. -/
def mul (f g : TruncQSeries) (len : ℕ) : TruncQSeries :=
  List.ofFn fun k : Fin len =>
    (List.range (k.val + 1)).foldl
      (fun acc j => acc + coeff f j * coeff g (k.val - j)) 0

/-- Scale a q-series by an integer constant. -/
def scale (c : ℤ) (f : TruncQSeries) : TruncQSeries :=
  f.map (· * c)

/-- Shift a q-series by multiplying by q^n (prepend n zeros). -/
def qShift (n : ℕ) (f : TruncQSeries) : TruncQSeries :=
  List.replicate n 0 ++ f

/-- The total number of terms in the truncated series. -/
def numTerms (f : TruncQSeries) : ℕ := f.length

-- ═══════════════════════════════════════════════════════════════════════════════
-- Verification: basic algebraic properties
-- ═══════════════════════════════════════════════════════════════════════════════

/-- The zero series has all zero coefficients. -/
theorem coeff_zero (len : ℕ) (n : ℕ) (hn : n < len) :
    coeff (zero len) n = 0 := by
  unfold coeff zero
  simp [List.getD_replicate hn]

/-- The identity series has a₀ = 1. -/
theorem coeff_one_zero (len : ℕ) (hlen : 0 < len) :
    coeff (one len) 0 = 1 := by
  unfold coeff one
  simp

/-- Negation flips signs. -/
theorem coeff_neg (f : TruncQSeries) (n : ℕ) (hn : n < f.length) :
    coeff (neg f) n = -(coeff f n) := by
  unfold coeff neg
  simp [List.getD_map, hn]
  ring

end DualScale.QSeries

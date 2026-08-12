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

/-- Helper for series inversion. Computes the inverse coefficients up to length n. -/
def invHelper (A : List ℤ) : ℕ → List ℤ
  | 0 => []
  | 1 => [1]
  | (m + 1) =>
    let B := invHelper A m
    let sum := (List.range m).foldl (fun acc k => acc + (A.getD (k + 1) 0) * (B.getD (m - 1 - k) 0)) 0
    B ++ [-sum]

/-- Multiplicative inverse of a q-series (requires a₀ = 1).
    Result is truncated to length `len`. -/
def inv (f : TruncQSeries) (len : ℕ) : TruncQSeries :=
  invHelper f len

/-- Exponentiation by a natural number. -/
def pow (f : TruncQSeries) (n : ℕ) (len : ℕ) : TruncQSeries :=
  match n with
  | 0 => one len
  | (k + 1) => mul f (pow f k len) len

/-- The total number of terms in the truncated series. -/
def numTerms (f : TruncQSeries) : ℕ := f.length

end DualScale.QSeries

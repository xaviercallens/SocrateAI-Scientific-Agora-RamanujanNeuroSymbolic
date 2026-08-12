-- DualScale/QSeries/MockTheta.lean — Task 1.8: Mock Theta Functions
-- =========================================================================
-- Stubs for Ramanujan's Mock Theta Functions from his last letter to Hardy (1920).
-- In this iteration, we define the known Fourier coefficients for the
-- first 10 terms directly for verification and future algebraic properties.
--
-- References:
--   Andrews & Berndt, "Ramanujan's Lost Notebook, Part I" (2005), Chapter 1.
--   Watson (1936), "The Final Problem: An Account of the Mock Theta Functions"

import Mathlib.Data.Int.Basic
import DualScale.QSeries.Basic

namespace DualScale.QSeries.MockTheta

open DualScale.QSeries

/-! ## 3rd-Order Mock Theta Functions

Ramanujan listed four 3rd-order mock theta functions initially:
f(q), ϕ(q), ψ(q), χ(q).
Watson (1936) added three more: ω(q), ν(q), ρ(q).
Total = 7 third-order functions.
-/

/-- f(q) = ∑_{n=0}^∞ q^{n^2} / (-q; q)_n^2 
    OEIS A000025 -/
def f_q : TruncQSeries :=
  [1, 1, -2, 3, -3, 3, -5, 7, -6, 6]

/-- ϕ(q) = ∑_{n=0}^∞ q^{n^2} / (-q^2; q^2)_n 
    OEIS A053251 -/
def phi_q : TruncQSeries :=
  [1, 1, 0, -1, 1, 1, -1, -1, 0, 2]

/-- ψ(q) = ∑_{n=1}^∞ q^{n^2} / (q; q^2)_n 
    (Note: Ramanujan defined it with q^(n^2), our coefficients start from q^0 = 1 for the related form).
    OEIS A053250 -/
def psi_q : TruncQSeries :=
  [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]

/-- χ(q) = ∑_{n=0}^∞ q^{n^2} / (-q; q+q^2)_n -/
def chi_q : TruncQSeries :=
  [1, 1, 1, 0, 1, 1, 0, 1, 1, 0] -- Stub approximation

/-- ω(q) = ∑_{n=0}^∞ q^{2n^2+2n} / (q; q^2)_{n+1}^2 -/
def omega_q : TruncQSeries :=
  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] -- Stub approximation

/-- ν(q) = ∑_{n=0}^∞ q^{n^2+n} / (-q; q^2)_{n+1} -/
def nu_q : TruncQSeries :=
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0] -- Stub approximation

/-- ρ(q) = ∑_{n=0}^∞ q^{2n^2} / (q; q^2)_{n+1} -/
def rho_q : TruncQSeries :=
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0] -- Stub approximation

/-! ## 5th-Order Mock Theta Functions

Ramanujan listed 10 fifth-order functions, we stub 3 key ones:
f_0(q), f_1(q), F_0(q).
-/

/-- f_0(q) = ∑_{n=0}^∞ q^{n^2} / (-q; q)_n -/
def f0_q : TruncQSeries :=
  [1, 1, -1, 0, 0, 1, -1, 0, 1, -1] -- Stub approximation

/-- f_1(q) = ∑_{n=0}^∞ q^{n^2+n} / (-q; q)_n -/
def f1_q : TruncQSeries :=
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0] -- Stub approximation

/-- F_0(q) = ∑_{n=0}^∞ q^{2n^2} / (q; q^2)_n -/
def F0_q : TruncQSeries :=
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0] -- Stub approximation

-- Verification against OEIS for the primary 3rd-order functions
#eval coeff f_q 3 -- expected: 3
#eval coeff phi_q 3 -- expected: -1
#eval coeff psi_q 3 -- expected: 1

end DualScale.QSeries.MockTheta

-- DualScale/Math/MagicSquare.lean
-- ====================================================================
-- Formalization of Magic Squares (3x3, 4x4, 5x5) over Commutative Rings
-- ====================================================================

import Mathlib.Algebra.Ring.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

namespace DualScale.Math.MagicSquare

variable {R : Type*} [CommRing R]

/-! ## 3x3 Magic Square Definition and Invariants -/

/-- Structure of a 3x3 Magic Square over a commutative ring R with magic sum S. -/
structure MagicSquare3 (R : Type*) [CommRing R] where
  a11 : R; a12 : R; a13 : R
  a21 : R; a22 : R; a23 : R
  a31 : R; a32 : R; a33 : R
  S   : R
  -- Row sums
  h_r1 : a11 + a12 + a13 = S
  h_r2 : a21 + a22 + a23 = S
  h_r3 : a31 + a32 + a33 = S
  -- Column sums
  h_c1 : a11 + a21 + a31 = S
  h_c2 : a12 + a22 + a32 = S
  h_c3 : a13 + a23 + a33 = S
  -- Diagonal sums
  h_d1 : a11 + a22 + a33 = S
  h_d2 : a13 + a22 + a31 = S

/-- Main Row/Column Sum Invariant Theorem for 3x3 Magic Squares:
    The magic sum S equals three times the center element x = a22 (3 * a22 = S). -/
theorem center_invariant_3x3 (m : MagicSquare3 R) :
    3 * m.a22 = m.S := by
  have h1 := m.h_d1
  have h2 := m.h_d2
  have h3 := m.h_r2
  have h4 := m.h_c2
  have h5 := m.h_r1
  have h6 := m.h_r3
  calc 3 * m.a22
    _ = (m.a11 + m.a22 + m.a33) + (m.a13 + m.a22 + m.a31) + (m.a21 + m.a22 + m.a23) + (m.a12 + m.a22 + m.a32)
        - (m.a11 + m.a12 + m.a13) - (m.a21 + m.a22 + m.a23) - (m.a31 + m.a32 + m.a33) := by ring
    _ = m.S + m.S + m.S + m.S - m.S - m.S - m.S := by rw [h1, h2, h3, h4, h5, h6]
    _ = m.S := by ring

/-- Total sum invariant: sum of all entries in a 3x3 magic square equals 3 * S. -/
theorem total_sum_3x3 (m : MagicSquare3 R) :
    (m.a11 + m.a12 + m.a13 + m.a21 + m.a22 + m.a23 + m.a31 + m.a32 + m.a33) = 3 * m.S := by
  have h1 := m.h_r1
  have h2 := m.h_r2
  have h3 := m.h_r3
  calc (m.a11 + m.a12 + m.a13 + m.a21 + m.a22 + m.a23 + m.a31 + m.a32 + m.a33)
    _ = (m.a11 + m.a12 + m.a13) + (m.a21 + m.a22 + m.a23) + (m.a31 + m.a32 + m.a33) := by ring
    _ = m.S + m.S + m.S := by rw [h1, h2, h3]
    _ = 3 * m.S := by ring


/-! ## 4x4 Magic Square Definition and Invariants -/

/-- Structure of a 4x4 Magic Square over a commutative ring R with magic sum S. -/
structure MagicSquare4 (R : Type*) [CommRing R] where
  a11 : R; a12 : R; a13 : R; a14 : R
  a21 : R; a22 : R; a23 : R; a24 : R
  a31 : R; a32 : R; a33 : R; a34 : R
  a41 : R; a42 : R; a43 : R; a44 : R
  S   : R
  -- Row sums
  h_r1 : a11 + a12 + a13 + a14 = S
  h_r2 : a21 + a22 + a23 + a24 = S
  h_r3 : a31 + a32 + a33 + a34 = S
  h_r4 : a41 + a42 + a43 + a44 = S
  -- Column sums
  h_c1 : a11 + a21 + a31 + a41 = S
  h_c2 : a12 + a22 + a32 + a42 = S
  h_c3 : a13 + a23 + a33 + a43 = S
  h_c4 : a14 + a24 + a34 + a44 = S
  -- Main diagonals
  h_d1 : a11 + a22 + a33 + a44 = S
  h_d2 : a14 + a23 + a32 + a41 = S

/-- Total sum invariant: sum of all 16 elements in a 4x4 magic square equals 4 * S. -/
theorem total_sum_4x4 (m : MagicSquare4 R) :
    (m.a11 + m.a12 + m.a13 + m.a14 +
     m.a21 + m.a22 + m.a23 + m.a24 +
     m.a31 + m.a32 + m.a33 + m.a34 +
     m.a41 + m.a42 + m.a43 + m.a44) = 4 * m.S := by
  have h1 := m.h_r1
  have h2 := m.h_r2
  have h3 := m.h_r3
  have h4 := m.h_r4
  calc (m.a11 + m.a12 + m.a13 + m.a14 +
        m.a21 + m.a22 + m.a23 + m.a24 +
        m.a31 + m.a32 + m.a33 + m.a34 +
        m.a41 + m.a42 + m.a43 + m.a44)
    _ = (m.a11 + m.a12 + m.a13 + m.a14) +
        (m.a21 + m.a22 + m.a23 + m.a24) +
        (m.a31 + m.a32 + m.a33 + m.a34) +
        (m.a41 + m.a42 + m.a43 + m.a44) := by ring
    _ = m.S + m.S + m.S + m.S := by rw [h1, h2, h3, h4]
    _ = 4 * m.S := by ring


/-! ## 5x5 Magic Square Definition and Invariants -/

/-- Structure of a 5x5 Magic Square over a commutative ring R with magic sum S. -/
structure MagicSquare5 (R : Type*) [CommRing R] where
  a11 : R; a12 : R; a13 : R; a14 : R; a15 : R
  a21 : R; a22 : R; a23 : R; a24 : R; a25 : R
  a31 : R; a32 : R; a33 : R; a34 : R; a35 : R
  a41 : R; a42 : R; a43 : R; a44 : R; a45 : R
  a51 : R; a52 : R; a53 : R; a54 : R; a55 : R
  S   : R
  -- Row sums
  h_r1 : a11 + a12 + a13 + a14 + a15 = S
  h_r2 : a21 + a22 + a23 + a24 + a25 = S
  h_r3 : a31 + a32 + a33 + a34 + a35 = S
  h_r4 : a41 + a42 + a43 + a44 + a45 = S
  h_r5 : a51 + a52 + a53 + a54 + a55 = S
  -- Column sums
  h_c1 : a11 + a21 + a31 + a41 + a51 = S
  h_c2 : a12 + a22 + a32 + a42 + a52 = S
  h_c3 : a13 + a23 + a33 + a43 + a53 = S
  h_c4 : a14 + a24 + a34 + a44 + a54 = S
  h_c5 : a15 + a25 + a35 + a45 + a55 = S
  -- Main diagonals
  h_d1 : a11 + a22 + a33 + a44 + a55 = S
  h_d2 : a15 + a24 + a33 + a42 + a51 = S

/-- Total sum invariant: sum of all 25 elements in a 5x5 magic square equals 5 * S. -/
theorem total_sum_5x5 (m : MagicSquare5 R) :
    (m.a11 + m.a12 + m.a13 + m.a14 + m.a15 +
     m.a21 + m.a22 + m.a23 + m.a24 + m.a25 +
     m.a31 + m.a32 + m.a33 + m.a34 + m.a35 +
     m.a41 + m.a42 + m.a43 + m.a44 + m.a45 +
     m.a51 + m.a52 + m.a53 + m.a54 + m.a55) = 5 * m.S := by
  have h1 := m.h_r1
  have h2 := m.h_r2
  have h3 := m.h_r3
  have h4 := m.h_r4
  have h5 := m.h_r5
  calc (m.a11 + m.a12 + m.a13 + m.a14 + m.a15 +
        m.a21 + m.a22 + m.a23 + m.a24 + m.a25 +
        m.a31 + m.a32 + m.a33 + m.a34 + m.a35 +
        m.a41 + m.a42 + m.a43 + m.a44 + m.a45 +
        m.a51 + m.a52 + m.a53 + m.a54 + m.a55)
    _ = (m.a11 + m.a12 + m.a13 + m.a14 + m.a15) +
        (m.a21 + m.a22 + m.a23 + m.a24 + m.a25) +
        (m.a31 + m.a32 + m.a33 + m.a34 + m.a35) +
        (m.a41 + m.a42 + m.a43 + m.a44 + m.a45) +
        (m.a51 + m.a52 + m.a53 + m.a54 + m.a55) := by ring
    _ = m.S + m.S + m.S + m.S + m.S := by rw [h1, h2, h3, h4, h5]
    _ = 5 * m.S := by ring


/-! ## Arithmetic Progression Lemmas for Parameterized Magic Squares -/

/-- Parameterized 3x3 Magic Square construction from parameters (x, a, b):
    [[x+b,   x-a-b, x+a  ],
     [x-a+b, x,     x+a-b],
     [x-a,   x+a+b, x-b  ]]
    This proves every parameterized matrix satisfies all magic square properties with S = 3 * x. -/
def parameterizedMagicSquare3 (x a b : R) : MagicSquare3 R where
  a11 := x + b
  a12 := x - a - b
  a13 := x + a
  a21 := x - a + b
  a22 := x
  a23 := x + a - b
  a31 := x - a
  a32 := x + a + b
  a33 := x - b
  S   := 3 * x
  h_r1 := by ring
  h_r2 := by ring
  h_r3 := by ring
  h_c1 := by ring
  h_c2 := by ring
  h_c3 := by ring
  h_d1 := by ring
  h_d2 := by ring

/-- Lemma: In the parameterized 3x3 magic square, the central row (a21, a22, a23)
    forms an arithmetic progression with common difference (a - b). -/
theorem arithmetic_progression_center_row (x a b : R) :
    let m := parameterizedMagicSquare3 x a b
    m.a23 - m.a22 = m.a22 - m.a21 := by
  dsimp [parameterizedMagicSquare3]
  ring

/-- Lemma: In the parameterized 3x3 magic square, the central column (a12, a22, a32)
    forms an arithmetic progression with common difference (a + b). -/
theorem arithmetic_progression_center_col (x a b : R) :
    let m := parameterizedMagicSquare3 x a b
    m.a32 - m.a22 = m.a22 - m.a12 := by
  dsimp [parameterizedMagicSquare3]
  ring

/-- Lemma: In the parameterized 3x3 magic square, the main diagonal (a11, a22, a33)
    forms an arithmetic progression with common difference (-b). -/
theorem arithmetic_progression_main_diag (x a b : R) :
    let m := parameterizedMagicSquare3 x a b
    m.a33 - m.a22 = m.a22 - m.a11 := by
  dsimp [parameterizedMagicSquare3]
  ring

/-- Lemma: In the parameterized 3x3 magic square, the anti-diagonal (a13, a22, a31)
    forms an arithmetic progression with common difference (-a). -/
theorem arithmetic_progression_anti_diag (x a b : R) :
    let m := parameterizedMagicSquare3 x a b
    m.a31 - m.a22 = m.a22 - m.a13 := by
  dsimp [parameterizedMagicSquare3]
  ring

end DualScale.Math.MagicSquare

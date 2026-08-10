import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring

theorem test_ring (q : ℝ) : (q + 1)^2 - 2*q - 1 = q^2 := by ring

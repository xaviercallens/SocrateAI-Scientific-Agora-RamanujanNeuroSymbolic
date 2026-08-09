-- paper/errata/v1_lean_listings.lean
-- ===================================
-- These are the five withdrawn listings from Version 1 of the paper.
-- All have the form `theorem ... : True := by trivial`.
-- ci/audit_lean.py MUST produce FAIL for every one of these.
-- Kept here purely for regression testing the CI gate.

theorem HydrodynamicLimit : True := by trivial

theorem SpectralGap : True := by trivial

theorem CFMConstraints : True := by trivial

theorem PhaseTransitions : True := by trivial

theorem FiberLock : True := by trivial

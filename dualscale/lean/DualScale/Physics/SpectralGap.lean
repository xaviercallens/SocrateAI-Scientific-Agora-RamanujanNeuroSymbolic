-- DualScale/Physics/SpectralGap.lean — Task 3.3: Spectral Gap Strengthening
-- ============================================================================
-- Parameterizes Hamiltonian spectral gaps via `SpectralSystem` and an explicit
-- Tier C hypothesis `BPSSpectralGapHypothesis`, removing all global axioms and
-- the classical tautology `¬P ∨ P`.

import Mathlib.Data.Real.Basic
import DualScale.QSeries.EtaQuotient

namespace DualScale.Physics

open DualScale.QSeries.EtaQuotient

/-! ## Hamiltonian Spectral Gap -/

/-- Parameterized Hamiltonian spectrum indexed by eta-quotients. -/
structure SpectralSystem where
  E_0 : EtaQuot → ℝ
  E_1 : EtaQuot → ℝ

/-- A system has a strict spectral gap at `eq` when `E_1 eq > E_0 eq`. -/
def HasSpectralGap (sys : SpectralSystem) (eq : EtaQuot) : Prop :=
  sys.E_1 eq > sys.E_0 eq

/-- Tier C holographic hypothesis: every BPS eta-quotient (`isBPS eq`)
    exhibits a strict spectral gap in `sys`. -/
def BPSSpectralGapHypothesis (sys : SpectralSystem) : Prop :=
  ∀ eq : EtaQuot, isBPS eq → HasSpectralGap sys eq

/-- Conditional Tier A deduction: under `BPSSpectralGapHypothesis sys`, any BPS
    eta-quotient has strictly positive gap `E_1 eq - E_0 eq > 0`. -/
theorem gap_pos_of_bps
    (sys : SpectralSystem) (h_hyp : BPSSpectralGapHypothesis sys)
    (eq : EtaQuot) (h_bps : isBPS eq) :
    0 < sys.E_1 eq - sys.E_0 eq :=
  sub_pos.mpr (h_hyp eq h_bps)

end DualScale.Physics

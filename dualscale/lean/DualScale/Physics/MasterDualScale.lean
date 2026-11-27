-- DualScale/Physics/MasterDualScale.lean
import Mathlib.Data.Real.Basic
import DualScale.QSeries.EtaQuotient
import DualScale.Asymptotics.BPSEntropy
import DualScale.Physics.Enstrophy
import DualScale.Physics.AubinLions

namespace DualScale.Physics

open DualScale.QSeries.EtaQuotient
open DualScale.Asymptotics

/-- Conditional Master Dual-Scale Theorem (Tier C):
    IF an explicit `AubinLionsPrinciple` holds for `sys`, the eta-quotient `eq`
    is BPS (`isBPS eq`) with non-negative `cEff eq`, and the fluid ensemble `S`
    satisfies the holographic enstrophy bound `κ * macroscopicEntropy (cEff eq) n`
    plus a uniform kinetic energy bound, THEN `IsL2Precompact S ∧ isBPS eq`.

    All hypotheses are actively used; decouples pure analysis from Tier C
    holographic ansätze without artificial `cEff eq = 1` assumptions. -/
theorem master_dual_scale_conditional {V : Type*}
    (sys : FluidSystem V) (IsL2Precompact : Set V → Prop)
    (h_al : AubinLionsPrinciple sys IsL2Precompact)
    {S : Set V} (eq : EtaQuot) (h_bps : isBPS eq) (n κ : ℝ)
    (h_kappa : 0 < κ) (hc_nonneg : 0 ≤ (cEff eq : ℝ)) (hn_nonneg : 0 ≤ n)
    (h_holo_ansatz : ∀ v ∈ S, sys.enstrophy_of v ≤ κ * macroscopicEntropy (cEff eq : ℝ) n)
    (h_ke_bound : ∃ E, ∀ v ∈ S, sys.kinetic_energy v ≤ E) :
    IsL2Precompact S ∧ isBPS eq := by
  have h_comp := aubin_lions_enstrophy_compactness sys IsL2Precompact h_al
    (cEff eq : ℝ) n κ h_kappa hc_nonneg hn_nonneg h_holo_ansatz h_ke_bound
  exact ⟨h_comp.1, h_bps⟩

end DualScale.Physics

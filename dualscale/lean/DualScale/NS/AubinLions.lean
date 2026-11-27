-- DualScale/NS/AubinLions.lean — Aubin–Lions Compactness Lemma for Galerkin Truncations
-- ====================================================================================
-- Formalization of the Aubin–Lions compactness framework for a concrete bounded-domain
-- Galerkin solution family `GalerkinFamily`, replacing the former global axiom and
-- unconstrained `ContDiff` quantification on ℝ³ with explicit Tier-L / Tier-C
-- hypothesis predicates and an actual subsequence `seq k → 0`.
--
-- References:
--   J.-L. Lions (1969), "Quelques méthodes de résolution des problèmes aux limites non linéaires"
--   J. Simon (1987), "Compact sets in the space L^p(0,T;B)"

import Mathlib.Data.Rat.Init
import Mathlib.Analysis.Calculus.FDeriv.Basic
import Mathlib.Analysis.Calculus.ContDiff.Basic
import Mathlib.MeasureTheory.Measure.Lebesgue.Basic
import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Order.Filter.Basic
import Mathlib.Topology.Basic
import Mathlib.Tactic.NormNum

namespace DualScale.NS.AubinLions

open Classical

/-- Truncation scale (exact rational per R5). -/
def alphaPrime : ℚ := 1 / 100

/-- Velocity field of a truncated Galerkin mode (smooth by finite truncation). -/
def TruncatedFlow (_a : ℚ) : Type :=
  { u : ℝ × ℝ × ℝ → ℝ × ℝ × ℝ // ContDiff ℝ ⊤ u }

/-- The Effective Central Charge (`c_eff`) parameter (Tier C heuristic). -/
def CentralCharge : Type := ℝ

/-- Tier C heuristic central-charge parameters. -/
noncomputable def c_eff_vacuum : CentralCharge := (4141 : ℝ) / 10000
noncomputable def c_eff_shadow : CentralCharge := (6667 : ℝ) / 10000
noncomputable def c_eff_resonance : CentralCharge := (17000 : ℝ) / 10000

/-- Tier C heuristic scaling weights associated with each central-charge parameter. -/
noncomputable def bps_scaling (c : CentralCharge) : ℝ :=
  if c = c_eff_shadow then Real.pi / Real.sqrt 3
  else if c = c_eff_vacuum then (11672 : ℝ) / 10000
  else if c = c_eff_resonance then (9655 : ℝ) / 10000
  else (1 : ℝ)

/-- The 3D vorticity field ω = curl u of a truncated flow via `fderiv`. -/
noncomputable def vorticityField (a : ℚ) (u : TruncatedFlow a) (x : ℝ × ℝ × ℝ) : ℝ × ℝ × ℝ :=
  let D := fderiv ℝ u.val x
  let v1 := D (1, 0, 0)
  let v2 := D (0, 1, 0)
  let v3 := D (0, 0, 1)
  (v2.2.2 - v3.2.1, v3.1 - v1.2.2, v1.2.1 - v2.1)

/-- Pointwise squared vorticity magnitude |ω(x)|². -/
noncomputable def vorticityNormSq (a : ℚ) (u : TruncatedFlow a) (x : ℝ × ℝ × ℝ) : ℝ :=
  let ω := vorticityField a u x
  ω.1 ^ 2 + ω.2.1 ^ 2 + ω.2.2 ^ 2

/-- Concrete Galerkin solution family on a spatial domain `Ω` and time interval `[0, T_max]`,
    carrying explicit integrability hypotheses for velocity and vorticity on `Ω`. -/
structure GalerkinFamily where
  Ω : Set (ℝ × ℝ × ℝ)
  T_max : ℝ
  hT : 0 < T_max
  flow : (a : ℚ) → 0 < a → a ≤ alphaPrime → ℝ → TruncatedFlow a
  integrable_vel : ∀ (a : ℚ) (ha1 : 0 < a) (ha2 : a ≤ alphaPrime) (t : ℝ),
    0 ≤ t → t ≤ T_max →
    MeasureTheory.IntegrableOn (fun x => (flow a ha1 ha2 t).val x) Ω MeasureTheory.volume
  integrable_vort : ∀ (a : ℚ) (ha1 : 0 < a) (ha2 : a ≤ alphaPrime) (t : ℝ),
    0 ≤ t → t ≤ T_max →
    MeasureTheory.IntegrableOn (fun x => vorticityNormSq a (flow a ha1 ha2 t) x) Ω MeasureTheory.volume

/-- Weighted enstrophy of the Galerkin family `fam` on `Ω` at time `t`. -/
noncomputable def enstrophyDensityOn (fam : GalerkinFamily)
    (a : ℚ) (ha1 : 0 < a) (ha2 : a ≤ alphaPrime) (c : CentralCharge) (t : ℝ) : ℝ :=
  bps_scaling c * MeasureTheory.integral (MeasureTheory.volume.restrict fam.Ω)
    (fun x => vorticityNormSq a (fam.flow a ha1 ha2 t) x)

/-- Tier C Hypothesis U restricted to a concrete `GalerkinFamily` on `fam.Ω × [0, fam.T_max]`:
    uniform enstrophy bound independent of the truncation parameter `a`. -/
def HypothesisUOn (fam : GalerkinFamily) : Prop :=
  ∃ C : ℝ, 0 < C ∧
    ∀ (a : ℚ) (ha1 : 0 < a) (ha2 : a ≤ alphaPrime) (c : CentralCharge),
      (c = c_eff_vacuum ∨ c = c_eff_shadow ∨ c = c_eff_resonance) →
      ∀ t : ℝ, 0 ≤ t → t ≤ fam.T_max →
        enstrophyDensityOn fam a ha1 ha2 c t ≤ C

/-- Uniform kinetic energy bound in `L²(fam.Ω)` over `0 ≤ t ≤ fam.T_max`. -/
def KineticEnergyBound (fam : GalerkinFamily) : Prop :=
  ∃ E : ℝ, 0 ≤ E ∧
    ∀ (a : ℚ) (ha1 : 0 < a) (ha2 : a ≤ alphaPrime) (t : ℝ),
      0 ≤ t → t ≤ fam.T_max →
      MeasureTheory.integral (MeasureTheory.volume.restrict fam.Ω)
        (fun x =>
          let v := (fam.flow a ha1 ha2 t).val x
          v.1 ^ 2 + v.2.1 ^ 2 + v.2.2 ^ 2) ≤ E

/-- Time-derivative regularity proxy (negative-Sobolev / H⁻¹-type increment bound)
    over `0 ≤ t ≤ fam.T_max`. -/
def TimeDerivNegativeSobolevBound (fam : GalerkinFamily) : Prop :=
  ∃ B : ℝ, 0 ≤ B ∧
    ∀ (a : ℚ) (ha1 : 0 < a) (ha2 : a ≤ alphaPrime) (t : ℝ),
      0 ≤ t → t ≤ fam.T_max →
      MeasureTheory.integral (MeasureTheory.volume.restrict fam.Ω)
        (fun x =>
          let u0 := (fam.flow a ha1 ha2 0).val x
          let ut := (fam.flow a ha1 ha2 t).val x
          (ut.1 - u0.1) ^ 2 + (ut.2.1 - u0.2.1) ^ 2 + (ut.2.2 - u0.2.2) ^ 2) ≤ B * t

/-- Existence of a subsequence `seq k → 0` converging strongly in `L²(fam.Ω)` to
    a limit field `u₀`. -/
def AdmitsStrongL2SubsequenceLimit (fam : GalerkinFamily) : Prop :=
  ∃ (seq : ℕ → ℚ) (h1 : ∀ k, 0 < seq k) (h2 : ∀ k, seq k ≤ alphaPrime)
    (u₀ : ℝ → ℝ × ℝ × ℝ → ℝ × ℝ × ℝ),
    Filter.Tendsto (fun k => (seq k : ℝ)) Filter.atTop (nhds 0) ∧
    ∀ ε : ℝ, 0 < ε →
      ∃ K : ℕ, ∀ k ≥ K, ∀ t : ℝ, 0 ≤ t → t ≤ fam.T_max →
        MeasureTheory.integral (MeasureTheory.volume.restrict fam.Ω)
          (fun x =>
            let v := (fam.flow (seq k) (h1 k) (h2 k) t).val x
            let w := u₀ t x
            (v.1 - w.1) ^ 2 + (v.2.1 - w.2.1) ^ 2 + (v.2.2 - w.2.2) ^ 2) < ε ^ 2

/-- Tier L hypothesis parameter (Lions 1969 / Simon 1987):
    Aubin–Lions compactness embedding for bounded-domain Galerkin families
    satisfying uniform kinetic energy, time-derivative, and enstrophy bounds. -/
def AubinLionsCompactnessPrinciple (fam : GalerkinFamily) : Prop :=
  (KineticEnergyBound fam ∧ TimeDerivNegativeSobolevBound fam ∧ HypothesisUOn fam) →
    AdmitsStrongL2SubsequenceLimit fam

/-- Conditional compactness theorem: under an explicit `AubinLionsCompactnessPrinciple`
    hypothesis and uniform kinetic energy, time-derivative, and Hypothesis U bounds,
    `fam` admits a strongly `L²`-convergent subsequence `seq k → 0`. -/
theorem aubin_lions_subsequence_of_hypothesisU
    (fam : GalerkinFamily)
    (h_al : AubinLionsCompactnessPrinciple fam)
    (h_ke : KineticEnergyBound fam)
    (h_dt : TimeDerivNegativeSobolevBound fam)
    (hU : HypothesisUOn fam) :
    AdmitsStrongL2SubsequenceLimit fam :=
  h_al ⟨h_ke, h_dt, hU⟩

end DualScale.NS.AubinLions

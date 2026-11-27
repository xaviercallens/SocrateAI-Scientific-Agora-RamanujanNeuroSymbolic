-- DualScale/NS/HypothesisU.lean — Hypothesis U Conditional Enstrophy & Compactness
-- ====================================================================================
-- Reuses `DualScale.NS.AubinLions` definitions without duplicating `TruncatedFlow` or
-- `vorticityField`, and proves genuine conditional consequences of `HypothesisUOn`.

import DualScale.NS.AubinLions
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

namespace DualScale.NS

open Classical
open DualScale.NS.AubinLions

/-- Tier A conditional consequence of `HypothesisUOn`:
    any Galerkin family satisfying `HypothesisUOn` has a uniform `L²(fam.Ω)`
    vorticity bound `M > 0` independent of `a` and `t ∈ [0, fam.T_max]`,
    obtained by specializing to `c_eff_vacuum` where `bps_scaling = 11672/10000 > 0`. -/
theorem vorticity_l2_bound_of_hypothesisU
    (fam : GalerkinFamily) (hU : HypothesisUOn fam) :
    ∃ M : ℝ, 0 < M ∧
      ∀ (a : ℚ) (ha1 : 0 < a) (ha2 : a ≤ alphaPrime) (t : ℝ),
        0 ≤ t → t ≤ fam.T_max →
        MeasureTheory.integral (MeasureTheory.volume.restrict fam.Ω)
          (fun x => vorticityNormSq a (fam.flow a ha1 ha2 t) x) ≤ M := by
  obtain ⟨C, hC_pos, hC⟩ := hU
  have h_vac_ne_shadow : c_eff_vacuum ≠ c_eff_shadow := by
    unfold c_eff_vacuum c_eff_shadow
    norm_num
  have h_vac_scale : bps_scaling c_eff_vacuum = (11672 : ℝ) / 10000 := by
    unfold bps_scaling
    rw [if_neg h_vac_ne_shadow, if_pos rfl]
  refine ⟨C / ((11672 : ℝ) / 10000), div_pos hC_pos (by norm_num),
    fun a ha1 ha2 t ht0 htT => ?_⟩
  have h_ens := hC a ha1 ha2 c_eff_vacuum (Or.inl rfl) t ht0 htT
  unfold enstrophyDensityOn at h_ens
  rw [h_vac_scale] at h_ens
  exact (le_div_iff₀ (by norm_num : (0 : ℝ) < (11672 : ℝ) / 10000)).mpr (by linarith)

/-- Conditional Aubin–Lions compactness step (Tier L + Tier C):
    given `AubinLionsCompactnessPrinciple fam`, uniform kinetic energy,
    negative-Sobolev time-derivative regularity, and `HypothesisUOn fam`,
    `fam` admits a strongly `L²(fam.Ω)`-convergent subsequence `seq k → 0`. -/
lemma compactness_step_is_open
    (fam : GalerkinFamily)
    (h_al : AubinLionsCompactnessPrinciple fam)
    (h_ke : KineticEnergyBound fam)
    (h_dt : TimeDerivNegativeSobolevBound fam)
    (hU : HypothesisUOn fam) :
    AdmitsStrongL2SubsequenceLimit fam :=
  aubin_lions_subsequence_of_hypothesisU fam h_al h_ke h_dt hU

end DualScale.NS

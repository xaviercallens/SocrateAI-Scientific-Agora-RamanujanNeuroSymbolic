-- Notebook3_Discovery.lean (Archived / Updated for Campaign v2 Sign Convention)
-- Mathematical Blueprint for the Notebook 3 Candidate Eta-Quotient
-- Superseded as a standalone zero-custom-axiom catalog by
-- `dualscale/lean/DualScale/Discovery/CampaignV2Verified.lean`.
--
-- EPISTEMIC NOTE (Campaign v2 sign correction):
--   Under the physically consistent cusp-0 Cardy convention c_eff(0) = -∑ r_d / d
--   (so 1/η(τ) has c_eff(0) = +1), `ramanujan_nb3` has c_eff(0) = -119/330 < 0
--   and alternating-sign Fourier coefficients (signed index, not a unitary BPS count).

import Mathlib.Data.Rat.Init
import Mathlib.Tactic.NormNum

namespace StringVacua.EtaQuotients

/-- Abstract Syntax Tree (AST) for an η-quotient represented as `(divisor, exponent)` pairs. -/
structure EtaQuotient where
  factors : List (ℕ × ℤ)

/-- Cusp-0 effective central charge: c_eff(0) = -∑ (r_d / d). -/
def EtaQuotient.c_eff (eq : EtaQuotient) : ℚ :=
  eq.factors.foldl (fun acc dr => acc - (dr.2 : ℚ) / (dr.1 : ℚ)) 0

/-- Modular weight: k = (1/2) ∑ r_d. -/
def EtaQuotient.weight (eq : EtaQuotient) : ℚ :=
  (eq.factors.foldl (fun acc dr => acc + (dr.2 : ℚ)) 0) / 2

/-- Natural leading q-power: P = (1/24) ∑ (d * r_d). -/
def EtaQuotient.leading_power (eq : EtaQuotient) : ℚ :=
  (eq.factors.foldl (fun acc dr => acc + (dr.1 : ℚ) * (dr.2 : ℚ)) 0) / 24

/-- Historical Notebook 3 candidate eta-quotient. -/
def ramanujan_nb3 : EtaQuotient :=
  { factors := [(8, 6), (10, 3), (11, -3), (12, -5)] }

theorem c_eff_is_neg_119_330 : ramanujan_nb3.c_eff = -119 / 330 := by
  dsimp [EtaQuotient.c_eff, ramanujan_nb3, List.foldl]
  norm_num

theorem c_eff_cusp0_is_negative : ramanujan_nb3.c_eff < 0 := by
  rw [c_eff_is_neg_119_330]
  norm_num

theorem weight_is_half : ramanujan_nb3.weight = 1 / 2 := by
  dsimp [EtaQuotient.weight, ramanujan_nb3, List.foldl]
  norm_num

theorem native_q_power : ramanujan_nb3.leading_power = -5 / 8 := by
  dsimp [EtaQuotient.leading_power, ramanujan_nb3, List.foldl]
  norm_num

end StringVacua.EtaQuotients

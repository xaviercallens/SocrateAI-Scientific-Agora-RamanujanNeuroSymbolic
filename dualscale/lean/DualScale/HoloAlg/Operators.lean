-- DualScale/HoloAlg/Operators.lean
import Mathlib.Data.Rat.Init
import Mathlib.Tactic.NormNum
import DualScale.HoloAlg.Basic

namespace DualScale.HoloAlg

/-- 
  The Supersymmetry Operator Ŵ acting on |Ω_r⟩.
  Ŵ |Ω_r⟩ = k |Ω_r⟩, where k = (1/2) ∑ r_d.
-/
def OpW (state : RamanujanState) : ℚ :=
  state.weight

/-- 
  The Central Charge Operator Ĉ acting on |Ω_r⟩.
  Ĉ |Ω_r⟩ = c_eff |Ω_r⟩, where c_eff = ∑ (r_d / d).
-/
def OpC (state : RamanujanState) : ℚ :=
  state.c_eff

/-- 
  The Ground Energy Operator Ê_0 acting on |Ω_r⟩.
  Ê_0 |Ω_r⟩ = E_0 |Ω_r⟩, where E_0 = (1/24) ∑ (d * r_d).
-/
def OpE0 (state : RamanujanState) : ℚ :=
  state.ground_energy

/-- 
  A Ramanujan state is BPS-protected if and only if it is an eigenvector
  of the Supersymmetry Operator Ŵ with eigenvalue 1/2.
-/
def isBPSProtected (state : RamanujanState) : Prop :=
  OpW state = 1 / 2

/-- 
  A state is unitary if its central charge eigenvalue is strictly positive.
-/
def isUnitary (state : RamanujanState) : Prop :=
  OpC state > 0

/-- 
  Eigenvalue Theorem: Applying Ŵ extracts the exact rational modular weight.
-/
theorem opW_eigenvalue (state : RamanujanState) :
    OpW state = state.weight := by
  rfl

/-- 
  Eigenvalue Theorem: Applying Ĉ extracts the exact rational central charge.
-/
theorem opC_eigenvalue (state : RamanujanState) :
    OpC state = state.c_eff := by
  rfl

end DualScale.HoloAlg

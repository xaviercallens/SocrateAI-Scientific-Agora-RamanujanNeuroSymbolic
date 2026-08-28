-- DualScale/HoloAlg.lean
/-!
# Project NAMAGIRI: HoloAlg Master Library
=========================================

Consolidated formalization of the Ramanujan Neuro-Symbolic Discovery Engine,
Holographic Operator Algebras, Newman Modular Forms, and Arnold Hydrodynamics.

## Modules:
- `DualScale.HoloAlg.Basic`: RamanujanState, Dirac Bra-Ket projections ⟨τ | Ω_r⟩.
- `DualScale.HoloAlg.Operators`: Modular weight, central charge, ground energy.
- `DualScale.HoloAlg.Functors`: Categorical functor mapping to physical domains.
- `DualScale.HoloAlg.NewmanModular`: Newman (1956/1959) modular form theorems on Γ₀(N).
- `DualScale.HoloAlg.VertexOperatorAlgebra`: Ramanujan-Moonshine VOA characters ch_{V_r}(q).
- `DualScale.HoloAlg.ArnoldHydrodynamics`: Arnold symplectic diffeomorphism-Virasoro duality.
- `DualScale.HoloAlg.F1Falsification`: Formal microstate ratio against Kerr Wald entropy.
-/

import DualScale.HoloAlg.Basic
import DualScale.HoloAlg.Operators
import DualScale.HoloAlg.Functors
import DualScale.HoloAlg.NewmanModular
import DualScale.HoloAlg.VertexOperatorAlgebra
import DualScale.HoloAlg.ArnoldHydrodynamics
import DualScale.HoloAlg.F1Falsification
import DualScale.HoloAlg.Act1_TDuality
import DualScale.HoloAlg.Act2_Dictionary
import DualScale.HoloAlg.Act3_Resolution

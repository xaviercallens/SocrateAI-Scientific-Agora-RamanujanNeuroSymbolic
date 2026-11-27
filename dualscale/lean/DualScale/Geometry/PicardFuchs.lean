-- DualScale/Geometry/PicardFuchs.lean — Task 2.6: K3 vs CY3 Discriminant
-- ============================================================================
-- Heuristic topological classifier mapping modular weight and effective central
-- charge of an eta-quotient to nominal Picard-Fuchs ODE orders.
-- NOTE: `classifyTopology` is a Tier C heuristic classifier, NOT a theorem
-- of algebraic geometry.

import DualScale.QSeries.EtaQuotient

namespace DualScale.Geometry

open DualScale.QSeries.EtaQuotient

/-! ## Topological Classifications (Tier C Heuristic Classifier) -/

inductive Topology
| K3_Surface
| CY3_Topology
| Singular
deriving Repr, DecidableEq

/-- Nominal Picard-Fuchs ODE order associated with each heuristic class.
    K3 surfaces yield order 2 (hypergeometric) Picard-Fuchs ODEs;
    Calabi-Yau 3-folds yield order 4. -/
def Topology.pfOrder : Topology → ℕ
| K3_Surface => 2
| CY3_Topology => 4
| Singular => 3

/-- Tier C heuristic classifier: assigns a nominal target-space topology from
    modular weight and cusp-0 effective central charge alone. -/
def classifyTopology (eq : EtaQuot) : Topology :=
  if modularWeight eq == 1 / 2 then
    if cEff eq > 0 then Topology.K3_Surface
    else Topology.Singular
  else
    Topology.CY3_Topology

/-! ## Proved Classifier Consistency (Tier A on Heuristic Definition) -/

/-- Consistency of the heuristic classifier `classifyTopology` with the
    `isBPS` and `isSUSYBroken` weight predicates (by case analysis on `modularWeight eq`). -/
theorem pf_order_topology_map (eq : EtaQuot) :
    let top := classifyTopology eq
    (top = Topology.K3_Surface → isBPS eq) ∧
    (top = Topology.CY3_Topology → isSUSYBroken eq) := by
  dsimp [classifyTopology, isBPS, isSUSYBroken]
  cases h_beq : (modularWeight eq == 1 / 2)
  · have h_ne : modularWeight eq ≠ 1 / 2 := fun h => by
      rw [beq_iff_eq.mpr h] at h_beq
      cases h_beq
    simp only [Bool.false_eq_true, ↓reduceIte]
    exact ⟨fun h => absurd h (by decide), fun _ => h_ne⟩
  · have h_eq : modularWeight eq = 1 / 2 := beq_iff_eq.mp h_beq
    simp only [↓reduceIte]
    by_cases h_c : cEff eq > 0
    · rw [if_pos h_c]
      exact ⟨fun _ => h_eq, fun h => absurd h (by decide)⟩
    · rw [if_neg h_c]
      exact ⟨fun h => absurd h (by decide), fun h => absurd h (by decide)⟩

end DualScale.Geometry

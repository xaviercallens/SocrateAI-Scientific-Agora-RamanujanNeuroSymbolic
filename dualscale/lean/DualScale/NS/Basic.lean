-- DualScale/NS/Basic.lean — Task M1.1
-- =====================================
-- Scaffolds the namespace and core definitions for Milestone M1.
-- No theorems yet; this file should have zero open targets and zero axioms.

import Mathlib.Data.Rat.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace DualScale.NS

/-- Truncation scale; exact rational, per audit rule R5.
    The value 1/100 is a design choice, not a physical claim. -/
def alphaPrime : ℚ := 1 / 100

end DualScale.NS

-- MATHESIS-GATE: env=none
-- MATHESIS-GATE: allow=propext
/-!
  Standalone Zero-Custom-Axiom Lean 4 Kernel Arithmetic for Dedekind η-Quotients
  Verified purely by the Lean 4 kernel (`by decide`, at most foundational `propext`).
-/

namespace DualScale.CampaignKernel

set_option maxRecDepth 50000
set_option maxHeartbeats 1000000

structure EtaQuot where
  factors : List (Nat × Int)
  deriving Repr, DecidableEq

/-- Exact reduced rational `(num, den)` with `den > 0`. -/
def ratNorm (num : Int) (den : Nat) : Int × Nat :=
  if den == 0 then (0, 1)
  else
    let g := Nat.gcd num.natAbs den
    if g == 0 then (0, 1) else (num / (g : Int), den / g)

def ratAdd (a b : Int × Nat) : Int × Nat :=
  ratNorm (a.1 * (b.2 : Int) + b.1 * (a.2 : Int)) (a.2 * b.2)

/-- Cusp-0 effective central charge `c_eff(0) = -∑ (r_d / d)`. -/
def cEffCusp0 (eq : EtaQuot) : Int × Nat :=
  eq.factors.foldl (fun acc dr => ratAdd acc (-dr.2, dr.1)) (0, 1)

/-- Modular weight `k = (∑ r_d) / 2`. -/
def modularWeight (eq : EtaQuot) : Int × Nat :=
  let s := eq.factors.foldl (fun acc dr => acc + dr.2) 0
  ratNorm s 2

/-- Ground state shift `E_0 = -(∑ d * r_d) / 24`. -/
def groundStateShift (eq : EtaQuot) : Int × Nat :=
  let s := eq.factors.foldl (fun acc dr => acc + (dr.1 : Int) * dr.2) 0
  ratNorm (-s) 24

/-- First Ono (2004) Theorem 1.64 congruence: `∑ d * r_d ≡ 0 (mod 24)`. -/
def onoCong1 (eq : EtaQuot) : Bool :=
  let s := eq.factors.foldl (fun acc dr => acc + (dr.1 : Int) * dr.2) 0
  s % 24 == 0

/-- Second Ono (2004) Theorem 1.64 congruence at level `N`: `∑ (N / d) * r_d ≡ 0 (mod 24)`. -/
def onoCong2 (eq : EtaQuot) (N : Nat) : Bool :=
  let s := eq.factors.foldl (fun acc dr => acc + ((N / dr.1 : Nat) : Int) * dr.2) 0
  s % 24 == 0

/-- Exact truncated Cauchy product of integer power series up to length `N`. -/
def polyMul (a b : List Int) (N : Nat) : List Int :=
  (List.range N).map fun n =>
    (List.range (n + 1)).foldl (fun acc k =>
      acc + a.getD k 0 * b.getD (n - k) 0) 0

/-- Exact inversion of an integer power series with `a[0] = 1` up to length `N`. -/
def polyInvAux (a : List Int) : Nat → List Int → List Int
  | 0, acc => acc
  | fuel + 1, acc =>
    let n := acc.length
    let s := (List.range n).foldl (fun sum j =>
      let k := n - j
      sum + a.getD k 0 * acc.getD j 0) 0
    polyInvAux a fuel (acc ++ [-s])

def polyInv (a : List Int) (N : Nat) : List Int :=
  if N == 0 then [] else polyInvAux a (N - 1) [1]

def polyPowAux (N : Nat) : Nat → Nat → List Int → List Int → List Int
  | 0, _, _, acc => acc
  | fuel + 1, e, base, acc =>
    if e == 0 then acc
    else if e == 1 then polyMul acc base N
    else
      let acc' := if e % 2 == 1 then polyMul acc base N else acc
      polyPowAux N fuel (e / 2) (polyMul base base N) acc'

def polyPowNat (a : List Int) (e N : Nat) : List Int :=
  let one := if N == 0 then [] else 1 :: List.replicate (N - 1) 0
  polyPowAux N (e + 1) e a one

def polyPowInt (a : List Int) (e : Int) (N : Nat) : List Int :=
  if e ≥ 0 then polyPowNat a e.toNat N
  else polyPowNat (polyInv a N) (-e).toNat N

/-- Euler pentagonal number expansion of `∏_{m≥1}(1 - q^m)` up to length `N`. -/
def eulerPentCoeff (n : Nat) : Int :=
  let rec go (k : Nat) (fuel : Nat) : Int :=
    match fuel with
    | 0 => 0
    | fuel' + 1 =>
      let p1 := k * (3 * k - 1) / 2
      let p2 := k * (3 * k + 1) / 2
      if p1 == n || p2 == n then
        if k % 2 == 1 then -1 else 1
      else if p1 > n then 0
      else go (k + 1) fuel'
  if n == 0 then 1 else go 1 (n + 2)

def baseEta (N : Nat) : List Int :=
  (List.range N).map eulerPentCoeff

def dilate (a : List Int) (d N : Nat) : List Int :=
  (List.range N).map fun i =>
    if d != 0 && i % d == 0 then a.getD (i / d) 0 else 0

/-- Exact truncated Fourier expansion of `∏_d (∏_{m≥1}(1 - q^{d*m}))^{r_d}`. -/
def etaCoeffs (eq : EtaQuot) (N : Nat) : List Int :=
  let base := baseEta N
  let init := if N == 0 then [] else 1 :: List.replicate (N - 1) 0
  eq.factors.foldl (fun acc dr =>
    if dr.2 == 0 then acc
    else polyMul acc (polyPowInt (dilate base dr.1 N) dr.2 N) N) init

/-- Exact truncated expansion of a linear combination of shifted η-quotients:
    `∑ (c_i * q^{s_i} * ∏_d η(dτ)^{r_d})` up to length `N`. -/
def evalLinearEta (terms : List (Int × Nat × List (Nat × Int))) (N : Nat) : List Int :=
  terms.foldl (fun acc t =>
    let s := etaCoeffs { factors := t.2.2 } N
    let shifted := List.replicate t.2.1 0 ++ s.take (N - t.2.1)
    let scaled := shifted.map (fun v => t.1 * v)
    (List.range N).map (fun i => acc.getD i 0 + scaled.getD i 0)
  ) (List.replicate N 0)


-- Entry eta_1e9a4949f6: LostNotebook_1988/LostNotebook_Sheets/p19 | Ramanujan psi(q) = sum q^(n(n+1)/2)
def eta_1e9a4949f6 : EtaQuot := { factors := [(1, -1), (2, 2)] }
theorem eta_1e9a4949f6_ceff : cEffCusp0 eta_1e9a4949f6 = (0, 1) := by decide
theorem eta_1e9a4949f6_weight : modularWeight eta_1e9a4949f6 = (1, 2) := by decide
theorem eta_1e9a4949f6_E0 : groundStateShift eta_1e9a4949f6 = (-1, 8) := by decide
theorem eta_1e9a4949f6_ono : (onoCong1 eta_1e9a4949f6, onoCong2 eta_1e9a4949f6 2) = (false, true) := by decide
theorem eta_1e9a4949f6_qseries : etaCoeffs eta_1e9a4949f6 12 = [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0] := by decide
#print axioms eta_1e9a4949f6_ceff
#print axioms eta_1e9a4949f6_weight
#print axioms eta_1e9a4949f6_E0
#print axioms eta_1e9a4949f6_ono
#print axioms eta_1e9a4949f6_qseries

-- Entry eta_ae942fea45: LostNotebook_1988/LostNotebook_Sheets/p47 | symbolic_latex_eta
def eta_ae942fea45 : EtaQuot := { factors := [(1, -2), (2, 3), (4, -1)] }
theorem eta_ae942fea45_ceff : cEffCusp0 eta_ae942fea45 = (3, 4) := by decide
theorem eta_ae942fea45_weight : modularWeight eta_ae942fea45 = (0, 1) := by decide
theorem eta_ae942fea45_E0 : groundStateShift eta_ae942fea45 = (0, 1) := by decide
theorem eta_ae942fea45_ono : (onoCong1 eta_ae942fea45, onoCong2 eta_ae942fea45 4) = (true, false) := by decide
theorem eta_ae942fea45_qseries : etaCoeffs eta_ae942fea45 12 = [1, 2, 2, 4, 6, 8, 12, 16, 22, 30, 40, 52] := by decide
#print axioms eta_ae942fea45_ceff
#print axioms eta_ae942fea45_weight
#print axioms eta_ae942fea45_E0
#print axioms eta_ae942fea45_ono
#print axioms eta_ae942fea45_qseries

-- Entry eta_7a7c2f5c3d: LostNotebook_1988/LostNotebook_Sheets/p53 | explicit_eta_transcription
def eta_7a7c2f5c3d : EtaQuot := { factors := [(1, -2), (3, 2), (5, -2), (15, 2)] }
theorem eta_7a7c2f5c3d_ceff : cEffCusp0 eta_7a7c2f5c3d = (8, 5) := by decide
theorem eta_7a7c2f5c3d_weight : modularWeight eta_7a7c2f5c3d = (0, 1) := by decide
theorem eta_7a7c2f5c3d_E0 : groundStateShift eta_7a7c2f5c3d = (-1, 1) := by decide
theorem eta_7a7c2f5c3d_ono : (onoCong1 eta_7a7c2f5c3d, onoCong2 eta_7a7c2f5c3d 15) = (true, true) := by decide
theorem eta_7a7c2f5c3d_qseries : etaCoeffs eta_7a7c2f5c3d 12 = [1, 2, 5, 8, 16, 28, 48, 78, 124, 194, 302, 454] := by decide
#print axioms eta_7a7c2f5c3d_ceff
#print axioms eta_7a7c2f5c3d_weight
#print axioms eta_7a7c2f5c3d_E0
#print axioms eta_7a7c2f5c3d_ono
#print axioms eta_7a7c2f5c3d_qseries

-- Entry eta_2b5f369eb9: LostNotebook_1988/LostNotebook_Sheets/p54 | Integer partition function p(n)
def eta_2b5f369eb9 : EtaQuot := { factors := [(1, -1)] }
theorem eta_2b5f369eb9_ceff : cEffCusp0 eta_2b5f369eb9 = (1, 1) := by decide
theorem eta_2b5f369eb9_weight : modularWeight eta_2b5f369eb9 = (-1, 2) := by decide
theorem eta_2b5f369eb9_E0 : groundStateShift eta_2b5f369eb9 = (1, 24) := by decide
theorem eta_2b5f369eb9_ono : (onoCong1 eta_2b5f369eb9, onoCong2 eta_2b5f369eb9 1) = (false, false) := by decide
theorem eta_2b5f369eb9_qseries : etaCoeffs eta_2b5f369eb9 12 = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56] := by decide
#print axioms eta_2b5f369eb9_ceff
#print axioms eta_2b5f369eb9_weight
#print axioms eta_2b5f369eb9_E0
#print axioms eta_2b5f369eb9_ono
#print axioms eta_2b5f369eb9_qseries

-- Entry eta_ac6556b216: LostNotebook_1988/LostNotebook_Sheets/p56 | Jacobi theta_3(q) = sum q^(n^2)
def eta_ac6556b216 : EtaQuot := { factors := [(1, -2), (2, 5), (4, -2)] }
theorem eta_ac6556b216_ceff : cEffCusp0 eta_ac6556b216 = (0, 1) := by decide
theorem eta_ac6556b216_weight : modularWeight eta_ac6556b216 = (1, 2) := by decide
theorem eta_ac6556b216_E0 : groundStateShift eta_ac6556b216 = (0, 1) := by decide
theorem eta_ac6556b216_ono : (onoCong1 eta_ac6556b216, onoCong2 eta_ac6556b216 4) = (true, true) := by decide
theorem eta_ac6556b216_qseries : etaCoeffs eta_ac6556b216 12 = [1, 2, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0] := by decide
#print axioms eta_ac6556b216_ceff
#print axioms eta_ac6556b216_weight
#print axioms eta_ac6556b216_E0
#print axioms eta_ac6556b216_ono
#print axioms eta_ac6556b216_qseries

-- Entry eta_abbf298e76: LostNotebook_1988/LostNotebook_Sheets/p56 | symbolic_latex_eta
def eta_abbf298e76 : EtaQuot := { factors := [(7, -2), (14, 5), (28, -2)] }
theorem eta_abbf298e76_ceff : cEffCusp0 eta_abbf298e76 = (0, 1) := by decide
theorem eta_abbf298e76_weight : modularWeight eta_abbf298e76 = (1, 2) := by decide
theorem eta_abbf298e76_E0 : groundStateShift eta_abbf298e76 = (0, 1) := by decide
theorem eta_abbf298e76_ono : (onoCong1 eta_abbf298e76, onoCong2 eta_abbf298e76 28) = (true, true) := by decide
theorem eta_abbf298e76_qseries : etaCoeffs eta_abbf298e76 12 = [1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0] := by decide
#print axioms eta_abbf298e76_ceff
#print axioms eta_abbf298e76_weight
#print axioms eta_abbf298e76_E0
#print axioms eta_abbf298e76_ono
#print axioms eta_abbf298e76_qseries

-- Entry eta_ad893d5cab: LostNotebook_1988/LostNotebook_Sheets/p56 | symbolic_latex_eta
def eta_ad893d5cab : EtaQuot := { factors := [(2, -1), (4, 2)] }
theorem eta_ad893d5cab_ceff : cEffCusp0 eta_ad893d5cab = (0, 1) := by decide
theorem eta_ad893d5cab_weight : modularWeight eta_ad893d5cab = (1, 2) := by decide
theorem eta_ad893d5cab_E0 : groundStateShift eta_ad893d5cab = (-1, 4) := by decide
theorem eta_ad893d5cab_ono : (onoCong1 eta_ad893d5cab, onoCong2 eta_ad893d5cab 4) = (false, true) := by decide
theorem eta_ad893d5cab_qseries : etaCoeffs eta_ad893d5cab 12 = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0] := by decide
#print axioms eta_ad893d5cab_ceff
#print axioms eta_ad893d5cab_weight
#print axioms eta_ad893d5cab_E0
#print axioms eta_ad893d5cab_ono
#print axioms eta_ad893d5cab_qseries

-- Entry eta_e0f67c30fe: LostNotebook_1988/LostNotebook_Sheets/p56 | symbolic_latex_eta
def eta_e0f67c30fe : EtaQuot := { factors := [(10, -1), (20, 2)] }
theorem eta_e0f67c30fe_ceff : cEffCusp0 eta_e0f67c30fe = (0, 1) := by decide
theorem eta_e0f67c30fe_weight : modularWeight eta_e0f67c30fe = (1, 2) := by decide
theorem eta_e0f67c30fe_E0 : groundStateShift eta_e0f67c30fe = (-5, 4) := by decide
theorem eta_e0f67c30fe_ono : (onoCong1 eta_e0f67c30fe, onoCong2 eta_e0f67c30fe 20) = (false, true) := by decide
theorem eta_e0f67c30fe_qseries : etaCoeffs eta_e0f67c30fe 12 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0] := by decide
#print axioms eta_e0f67c30fe_ceff
#print axioms eta_e0f67c30fe_weight
#print axioms eta_e0f67c30fe_E0
#print axioms eta_e0f67c30fe_ono
#print axioms eta_e0f67c30fe_qseries

-- Entry eta_0deca53b34: LostNotebook_1988/LostNotebook_Sheets/p59 | Euler pentagonal / Dedekind eta
def eta_0deca53b34 : EtaQuot := { factors := [(1, 1)] }
theorem eta_0deca53b34_ceff : cEffCusp0 eta_0deca53b34 = (-1, 1) := by decide
theorem eta_0deca53b34_weight : modularWeight eta_0deca53b34 = (1, 2) := by decide
theorem eta_0deca53b34_E0 : groundStateShift eta_0deca53b34 = (-1, 24) := by decide
theorem eta_0deca53b34_ono : (onoCong1 eta_0deca53b34, onoCong2 eta_0deca53b34 1) = (false, false) := by decide
theorem eta_0deca53b34_qseries : etaCoeffs eta_0deca53b34 12 = [1, -1, -1, 0, 0, 1, 0, 1, 0, 0, 0, 0] := by decide
#print axioms eta_0deca53b34_ceff
#print axioms eta_0deca53b34_weight
#print axioms eta_0deca53b34_E0
#print axioms eta_0deca53b34_ono
#print axioms eta_0deca53b34_qseries

-- Entry eta_e11141e770: LostNotebook_1988/HardyLetters_And_Sheets/p133 | Ramanujan tau(n+1) / Delta(q)/q
def eta_e11141e770 : EtaQuot := { factors := [(1, 24)] }
theorem eta_e11141e770_ceff : cEffCusp0 eta_e11141e770 = (-24, 1) := by decide
theorem eta_e11141e770_weight : modularWeight eta_e11141e770 = (12, 1) := by decide
theorem eta_e11141e770_E0 : groundStateShift eta_e11141e770 = (-1, 1) := by decide
theorem eta_e11141e770_ono : (onoCong1 eta_e11141e770, onoCong2 eta_e11141e770 1) = (true, true) := by decide
theorem eta_e11141e770_qseries : etaCoeffs eta_e11141e770 12 = [1, -24, 252, -1472, 4830, -6048, -16744, 84480, -113643, -115920, 534612, -370944] := by decide
#print axioms eta_e11141e770_ceff
#print axioms eta_e11141e770_weight
#print axioms eta_e11141e770_E0
#print axioms eta_e11141e770_ono
#print axioms eta_e11141e770_qseries

-- Entry eta_2f4b7679e7: NoteBook1/chapterVIII/p20 | symbolic_latex_eta
def eta_2f4b7679e7 : EtaQuot := { factors := [(1, -4), (2, 10), (4, -4)] }
theorem eta_2f4b7679e7_ceff : cEffCusp0 eta_2f4b7679e7 = (0, 1) := by decide
theorem eta_2f4b7679e7_weight : modularWeight eta_2f4b7679e7 = (1, 1) := by decide
theorem eta_2f4b7679e7_E0 : groundStateShift eta_2f4b7679e7 = (0, 1) := by decide
theorem eta_2f4b7679e7_ono : (onoCong1 eta_2f4b7679e7, onoCong2 eta_2f4b7679e7 4) = (true, true) := by decide
theorem eta_2f4b7679e7_qseries : etaCoeffs eta_2f4b7679e7 12 = [1, 4, 4, 0, 4, 8, 0, 0, 4, 4, 8, 0] := by decide
#print axioms eta_2f4b7679e7_ceff
#print axioms eta_2f4b7679e7_weight
#print axioms eta_2f4b7679e7_E0
#print axioms eta_2f4b7679e7_ono
#print axioms eta_2f4b7679e7_qseries

-- Entry eta_2a2c724a6d: NoteBook1/chapterVIII/p20 | symbolic_latex_eta
def eta_2a2c724a6d : EtaQuot := { factors := [(5, -4), (10, 10), (20, -4)] }
theorem eta_2a2c724a6d_ceff : cEffCusp0 eta_2a2c724a6d = (0, 1) := by decide
theorem eta_2a2c724a6d_weight : modularWeight eta_2a2c724a6d = (1, 1) := by decide
theorem eta_2a2c724a6d_E0 : groundStateShift eta_2a2c724a6d = (0, 1) := by decide
theorem eta_2a2c724a6d_ono : (onoCong1 eta_2a2c724a6d, onoCong2 eta_2a2c724a6d 20) = (true, true) := by decide
theorem eta_2a2c724a6d_qseries : etaCoeffs eta_2a2c724a6d 12 = [1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 4, 0] := by decide
#print axioms eta_2a2c724a6d_ceff
#print axioms eta_2a2c724a6d_weight
#print axioms eta_2a2c724a6d_E0
#print axioms eta_2a2c724a6d_ono
#print axioms eta_2a2c724a6d_qseries

-- Entry eta_792698eb06: NoteBook1/chapterXI/p11 | Jacobi theta_4(q) = sum (-1)^n q^(n^2)
def eta_792698eb06 : EtaQuot := { factors := [(1, 2), (2, -1)] }
theorem eta_792698eb06_ceff : cEffCusp0 eta_792698eb06 = (-3, 2) := by decide
theorem eta_792698eb06_weight : modularWeight eta_792698eb06 = (1, 2) := by decide
theorem eta_792698eb06_E0 : groundStateShift eta_792698eb06 = (0, 1) := by decide
theorem eta_792698eb06_ono : (onoCong1 eta_792698eb06, onoCong2 eta_792698eb06 2) = (true, false) := by decide
theorem eta_792698eb06_qseries : etaCoeffs eta_792698eb06 12 = [1, -2, 0, 0, 2, 0, 0, 0, 0, -2, 0, 0] := by decide
#print axioms eta_792698eb06_ceff
#print axioms eta_792698eb06_weight
#print axioms eta_792698eb06_E0
#print axioms eta_792698eb06_ono
#print axioms eta_792698eb06_qseries

-- Entry eta_df7425cf53: NoteBook1/chapterXI/p25 | symbolic_latex_eta
def eta_df7425cf53 : EtaQuot := { factors := [(1, 1), (2, -1), (4, 1)] }
theorem eta_df7425cf53_ceff : cEffCusp0 eta_df7425cf53 = (-3, 4) := by decide
theorem eta_df7425cf53_weight : modularWeight eta_df7425cf53 = (1, 2) := by decide
theorem eta_df7425cf53_E0 : groundStateShift eta_df7425cf53 = (-1, 8) := by decide
theorem eta_df7425cf53_ono : (onoCong1 eta_df7425cf53, onoCong2 eta_df7425cf53 4) = (false, false) := by decide
theorem eta_df7425cf53_qseries : etaCoeffs eta_df7425cf53 12 = [1, -1, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0] := by decide
#print axioms eta_df7425cf53_ceff
#print axioms eta_df7425cf53_weight
#print axioms eta_df7425cf53_E0
#print axioms eta_df7425cf53_ono
#print axioms eta_df7425cf53_qseries

-- Entry eta_cc0ca45397: NoteBook1/chapterXIV/p14 | symbolic_latex_eta
def eta_cc0ca45397 : EtaQuot := { factors := [(1, -3), (2, 6), (5, -1), (10, 2)] }
theorem eta_cc0ca45397_ceff : cEffCusp0 eta_cc0ca45397 = (0, 1) := by decide
theorem eta_cc0ca45397_weight : modularWeight eta_cc0ca45397 = (2, 1) := by decide
theorem eta_cc0ca45397_E0 : groundStateShift eta_cc0ca45397 = (-1, 1) := by decide
theorem eta_cc0ca45397_ono : (onoCong1 eta_cc0ca45397, onoCong2 eta_cc0ca45397 10) = (true, true) := by decide
theorem eta_cc0ca45397_qseries : etaCoeffs eta_cc0ca45397 12 = [1, 3, 3, 4, 6, 4, 9, 12, 7, 13, 12, 12] := by decide
#print axioms eta_cc0ca45397_ceff
#print axioms eta_cc0ca45397_weight
#print axioms eta_cc0ca45397_E0
#print axioms eta_cc0ca45397_ono
#print axioms eta_cc0ca45397_qseries

-- Entry eta_ac8dc71ec9: NoteBook1/chapterXIV/p14 | symbolic_latex_eta
def eta_ac8dc71ec9 : EtaQuot := { factors := [(1, -1), (2, 2), (5, -3), (10, 6)] }
theorem eta_ac8dc71ec9_ceff : cEffCusp0 eta_ac8dc71ec9 = (0, 1) := by decide
theorem eta_ac8dc71ec9_weight : modularWeight eta_ac8dc71ec9 = (2, 1) := by decide
theorem eta_ac8dc71ec9_E0 : groundStateShift eta_ac8dc71ec9 = (-2, 1) := by decide
theorem eta_ac8dc71ec9_ono : (onoCong1 eta_ac8dc71ec9, onoCong2 eta_ac8dc71ec9 10) = (true, true) := by decide
theorem eta_ac8dc71ec9_qseries : etaCoeffs eta_ac8dc71ec9 12 = [1, 1, 0, 1, 0, 3, 4, 0, 3, 0, 4, 6] := by decide
#print axioms eta_ac8dc71ec9_ceff
#print axioms eta_ac8dc71ec9_weight
#print axioms eta_ac8dc71ec9_E0
#print axioms eta_ac8dc71ec9_ono
#print axioms eta_ac8dc71ec9_qseries

-- Entry eta_717ff51153: NoteBook1/chapterXIV/p14 | symbolic_latex_eta
def eta_717ff51153 : EtaQuot := { factors := [(1, -2), (2, 5), (4, -2), (5, -6), (10, 15), (20, -6)] }
theorem eta_717ff51153_ceff : cEffCusp0 eta_717ff51153 = (0, 1) := by decide
theorem eta_717ff51153_weight : modularWeight eta_717ff51153 = (2, 1) := by decide
theorem eta_717ff51153_E0 : groundStateShift eta_717ff51153 = (0, 1) := by decide
theorem eta_717ff51153_ono : (onoCong1 eta_717ff51153, onoCong2 eta_717ff51153 20) = (true, true) := by decide
theorem eta_717ff51153_qseries : etaCoeffs eta_717ff51153 12 = [1, 2, 0, 0, 2, 6, 12, 0, 0, 14, 12, 24] := by decide
#print axioms eta_717ff51153_ceff
#print axioms eta_717ff51153_weight
#print axioms eta_717ff51153_E0
#print axioms eta_717ff51153_ono
#print axioms eta_717ff51153_qseries

-- Entry eta_65a5fd6d86: NoteBook1/chapterXIV/p14 | symbolic_latex_eta
def eta_65a5fd6d86 : EtaQuot := { factors := [(1, -4), (2, 10), (4, -4), (5, -2), (10, 5), (20, -2)] }
theorem eta_65a5fd6d86_ceff : cEffCusp0 eta_65a5fd6d86 = (0, 1) := by decide
theorem eta_65a5fd6d86_weight : modularWeight eta_65a5fd6d86 = (3, 2) := by decide
theorem eta_65a5fd6d86_E0 : groundStateShift eta_65a5fd6d86 = (0, 1) := by decide
theorem eta_65a5fd6d86_ono : (onoCong1 eta_65a5fd6d86, onoCong2 eta_65a5fd6d86 20) = (true, true) := by decide
theorem eta_65a5fd6d86_qseries : etaCoeffs eta_65a5fd6d86 12 = [1, 4, 4, 0, 4, 10, 8, 8, 4, 12, 24, 0] := by decide
#print axioms eta_65a5fd6d86_ceff
#print axioms eta_65a5fd6d86_weight
#print axioms eta_65a5fd6d86_E0
#print axioms eta_65a5fd6d86_ono
#print axioms eta_65a5fd6d86_qseries

-- Entry eta_47e6725676: NoteBook1/chapterXIV/p14 | symbolic_latex_eta
def eta_47e6725676 : EtaQuot := { factors := [(1, -10), (2, 25), (4, -10), (5, 2), (10, -5), (20, 2)] }
theorem eta_47e6725676_ceff : cEffCusp0 eta_47e6725676 = (0, 1) := by decide
theorem eta_47e6725676_weight : modularWeight eta_47e6725676 = (2, 1) := by decide
theorem eta_47e6725676_E0 : groundStateShift eta_47e6725676 = (0, 1) := by decide
theorem eta_47e6725676_ono : (onoCong1 eta_47e6725676, onoCong2 eta_47e6725676 20) = (true, true) := by decide
theorem eta_47e6725676_qseries : etaCoeffs eta_47e6725676 12 = [1, 10, 40, 80, 90, 110, 220, 240, 40, 70, 340, 120] := by decide
#print axioms eta_47e6725676_ceff
#print axioms eta_47e6725676_weight
#print axioms eta_47e6725676_E0
#print axioms eta_47e6725676_ono
#print axioms eta_47e6725676_qseries

-- Entry eta_4ebfb72cae: NoteBook1/chapterXIV/p16 | symbolic_latex_eta
def eta_4ebfb72cae : EtaQuot := { factors := [(7, -1), (9, -1), (14, 2), (18, 2)] }
theorem eta_4ebfb72cae_ceff : cEffCusp0 eta_4ebfb72cae = (0, 1) := by decide
theorem eta_4ebfb72cae_weight : modularWeight eta_4ebfb72cae = (1, 1) := by decide
theorem eta_4ebfb72cae_E0 : groundStateShift eta_4ebfb72cae = (-2, 1) := by decide
theorem eta_4ebfb72cae_ono : (onoCong1 eta_4ebfb72cae, onoCong2 eta_4ebfb72cae 126) = (true, true) := by decide
theorem eta_4ebfb72cae_qseries : etaCoeffs eta_4ebfb72cae 12 = [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0] := by decide
#print axioms eta_4ebfb72cae_ceff
#print axioms eta_4ebfb72cae_weight
#print axioms eta_4ebfb72cae_E0
#print axioms eta_4ebfb72cae_ono
#print axioms eta_4ebfb72cae_qseries

-- Entry eta_cf4ef6b7b2: NoteBook1/chapterXIV/p16 | symbolic_latex_eta
def eta_cf4ef6b7b2 : EtaQuot := { factors := [(7, 1), (9, 1), (14, -1), (18, -1), (28, 1), (36, 1)] }
theorem eta_cf4ef6b7b2_ceff : cEffCusp0 eta_cf4ef6b7b2 = (-4, 21) := by decide
theorem eta_cf4ef6b7b2_weight : modularWeight eta_cf4ef6b7b2 = (1, 1) := by decide
theorem eta_cf4ef6b7b2_E0 : groundStateShift eta_cf4ef6b7b2 = (-2, 1) := by decide
theorem eta_cf4ef6b7b2_ono : (onoCong1 eta_cf4ef6b7b2, onoCong2 eta_cf4ef6b7b2 252) = (true, true) := by decide
theorem eta_cf4ef6b7b2_qseries : etaCoeffs eta_cf4ef6b7b2 12 = [1, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0] := by decide
#print axioms eta_cf4ef6b7b2_ceff
#print axioms eta_cf4ef6b7b2_weight
#print axioms eta_cf4ef6b7b2_E0
#print axioms eta_cf4ef6b7b2_ono
#print axioms eta_cf4ef6b7b2_qseries

-- Entry eta_5ece260497: NoteBook1/chapterXIV/p16 | symbolic_latex_eta
def eta_5ece260497 : EtaQuot := { factors := [(5, -1), (10, 2), (11, -1), (22, 2)] }
theorem eta_5ece260497_ceff : cEffCusp0 eta_5ece260497 = (0, 1) := by decide
theorem eta_5ece260497_weight : modularWeight eta_5ece260497 = (1, 1) := by decide
theorem eta_5ece260497_E0 : groundStateShift eta_5ece260497 = (-2, 1) := by decide
theorem eta_5ece260497_ono : (onoCong1 eta_5ece260497, onoCong2 eta_5ece260497 110) = (true, true) := by decide
theorem eta_5ece260497_qseries : etaCoeffs eta_5ece260497 12 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1] := by decide
#print axioms eta_5ece260497_ceff
#print axioms eta_5ece260497_weight
#print axioms eta_5ece260497_E0
#print axioms eta_5ece260497_ono
#print axioms eta_5ece260497_qseries

-- Entry eta_e9faef62c9: NoteBook1/chapterXIV/p16 | symbolic_latex_eta
def eta_e9faef62c9 : EtaQuot := { factors := [(3, -1), (6, 2), (13, -1), (26, 2)] }
theorem eta_e9faef62c9_ceff : cEffCusp0 eta_e9faef62c9 = (0, 1) := by decide
theorem eta_e9faef62c9_weight : modularWeight eta_e9faef62c9 = (1, 1) := by decide
theorem eta_e9faef62c9_E0 : groundStateShift eta_e9faef62c9 = (-2, 1) := by decide
theorem eta_e9faef62c9_ono : (onoCong1 eta_e9faef62c9, onoCong2 eta_e9faef62c9 78) = (true, true) := by decide
theorem eta_e9faef62c9_qseries : etaCoeffs eta_e9faef62c9 12 = [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0] := by decide
#print axioms eta_e9faef62c9_ceff
#print axioms eta_e9faef62c9_weight
#print axioms eta_e9faef62c9_E0
#print axioms eta_e9faef62c9_ono
#print axioms eta_e9faef62c9_qseries

-- Entry eta_51aa54adf8: NoteBook1/chapterXV/p14 | symbolic_latex_eta
def eta_51aa54adf8 : EtaQuot := { factors := [(9, -1), (18, 2)] }
theorem eta_51aa54adf8_ceff : cEffCusp0 eta_51aa54adf8 = (0, 1) := by decide
theorem eta_51aa54adf8_weight : modularWeight eta_51aa54adf8 = (1, 2) := by decide
theorem eta_51aa54adf8_E0 : groundStateShift eta_51aa54adf8 = (-9, 8) := by decide
theorem eta_51aa54adf8_ono : (onoCong1 eta_51aa54adf8, onoCong2 eta_51aa54adf8 18) = (false, true) := by decide
theorem eta_51aa54adf8_qseries : etaCoeffs eta_51aa54adf8 12 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0] := by decide
#print axioms eta_51aa54adf8_ceff
#print axioms eta_51aa54adf8_weight
#print axioms eta_51aa54adf8_E0
#print axioms eta_51aa54adf8_ono
#print axioms eta_51aa54adf8_qseries

-- Entry eta_17afcd1cd2: NoteBook1/chapterXV/p18 | symbolic_latex_eta
def eta_17afcd1cd2 : EtaQuot := { factors := [(4, -2), (8, 5), (16, -2)] }
theorem eta_17afcd1cd2_ceff : cEffCusp0 eta_17afcd1cd2 = (0, 1) := by decide
theorem eta_17afcd1cd2_weight : modularWeight eta_17afcd1cd2 = (1, 2) := by decide
theorem eta_17afcd1cd2_E0 : groundStateShift eta_17afcd1cd2 = (0, 1) := by decide
theorem eta_17afcd1cd2_ono : (onoCong1 eta_17afcd1cd2, onoCong2 eta_17afcd1cd2 16) = (true, true) := by decide
theorem eta_17afcd1cd2_qseries : etaCoeffs eta_17afcd1cd2 12 = [1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0] := by decide
#print axioms eta_17afcd1cd2_ceff
#print axioms eta_17afcd1cd2_weight
#print axioms eta_17afcd1cd2_E0
#print axioms eta_17afcd1cd2_ono
#print axioms eta_17afcd1cd2_qseries

-- Entry eta_c073397801: NoteBook1/chapterXV/p19 | symbolic_latex_eta
def eta_c073397801 : EtaQuot := { factors := [(8, -1), (16, 2)] }
theorem eta_c073397801_ceff : cEffCusp0 eta_c073397801 = (0, 1) := by decide
theorem eta_c073397801_weight : modularWeight eta_c073397801 = (1, 2) := by decide
theorem eta_c073397801_E0 : groundStateShift eta_c073397801 = (-1, 1) := by decide
theorem eta_c073397801_ono : (onoCong1 eta_c073397801, onoCong2 eta_c073397801 16) = (true, true) := by decide
theorem eta_c073397801_qseries : etaCoeffs eta_c073397801 12 = [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0] := by decide
#print axioms eta_c073397801_ceff
#print axioms eta_c073397801_weight
#print axioms eta_c073397801_E0
#print axioms eta_c073397801_ono
#print axioms eta_c073397801_qseries

-- Entry eta_ec6e5fe6a7: NoteBook1/chapterXV/p4 | symbolic_latex_eta
def eta_ec6e5fe6a7 : EtaQuot := { factors := [(1, -4), (2, 6), (4, 6), (8, -4)] }
theorem eta_ec6e5fe6a7_ceff : cEffCusp0 eta_ec6e5fe6a7 = (0, 1) := by decide
theorem eta_ec6e5fe6a7_weight : modularWeight eta_ec6e5fe6a7 = (2, 1) := by decide
theorem eta_ec6e5fe6a7_E0 : groundStateShift eta_ec6e5fe6a7 = (0, 1) := by decide
theorem eta_ec6e5fe6a7_ono : (onoCong1 eta_ec6e5fe6a7, onoCong2 eta_ec6e5fe6a7 8) = (true, true) := by decide
theorem eta_ec6e5fe6a7_qseries : etaCoeffs eta_ec6e5fe6a7 12 = [1, 4, 8, 16, 24, 24, 32, 32, 24, 52, 48, 48] := by decide
#print axioms eta_ec6e5fe6a7_ceff
#print axioms eta_ec6e5fe6a7_weight
#print axioms eta_ec6e5fe6a7_E0
#print axioms eta_ec6e5fe6a7_ono
#print axioms eta_ec6e5fe6a7_qseries

-- Entry eta_aa59c343e7: NoteBook1/chapterXV/p4 | symbolic_latex_eta
def eta_aa59c343e7 : EtaQuot := { factors := [(1, -2), (2, 5), (4, -2), (7, -2), (14, 5), (28, -2)] }
theorem eta_aa59c343e7_ceff : cEffCusp0 eta_aa59c343e7 = (0, 1) := by decide
theorem eta_aa59c343e7_weight : modularWeight eta_aa59c343e7 = (1, 1) := by decide
theorem eta_aa59c343e7_E0 : groundStateShift eta_aa59c343e7 = (0, 1) := by decide
theorem eta_aa59c343e7_ono : (onoCong1 eta_aa59c343e7, onoCong2 eta_aa59c343e7 28) = (true, true) := by decide
theorem eta_aa59c343e7_qseries : etaCoeffs eta_aa59c343e7 12 = [1, 2, 0, 0, 2, 0, 0, 2, 4, 2, 0, 4] := by decide
#print axioms eta_aa59c343e7_ceff
#print axioms eta_aa59c343e7_weight
#print axioms eta_aa59c343e7_E0
#print axioms eta_aa59c343e7_ono
#print axioms eta_aa59c343e7_qseries

-- Entry eta_7e274cac26: NoteBook1/chapterXVI/p14 | symbolic_latex_eta
def eta_7e274cac26 : EtaQuot := { factors := [(1, -8), (2, 20), (4, -8)] }
theorem eta_7e274cac26_ceff : cEffCusp0 eta_7e274cac26 = (0, 1) := by decide
theorem eta_7e274cac26_weight : modularWeight eta_7e274cac26 = (2, 1) := by decide
theorem eta_7e274cac26_E0 : groundStateShift eta_7e274cac26 = (0, 1) := by decide
theorem eta_7e274cac26_ono : (onoCong1 eta_7e274cac26, onoCong2 eta_7e274cac26 4) = (true, true) := by decide
theorem eta_7e274cac26_qseries : etaCoeffs eta_7e274cac26 12 = [1, 8, 24, 32, 24, 48, 96, 64, 24, 104, 144, 96] := by decide
#print axioms eta_7e274cac26_ceff
#print axioms eta_7e274cac26_weight
#print axioms eta_7e274cac26_E0
#print axioms eta_7e274cac26_ono
#print axioms eta_7e274cac26_qseries

-- Entry eta_435be90a7f: NoteBook1/chapterXVI/p21 | symbolic_latex_eta
def eta_435be90a7f : EtaQuot := { factors := [(1, 16), (2, -8)] }
theorem eta_435be90a7f_ceff : cEffCusp0 eta_435be90a7f = (-12, 1) := by decide
theorem eta_435be90a7f_weight : modularWeight eta_435be90a7f = (4, 1) := by decide
theorem eta_435be90a7f_E0 : groundStateShift eta_435be90a7f = (0, 1) := by decide
theorem eta_435be90a7f_ono : (onoCong1 eta_435be90a7f, onoCong2 eta_435be90a7f 2) = (true, true) := by decide
theorem eta_435be90a7f_qseries : etaCoeffs eta_435be90a7f 12 = [1, -16, 112, -448, 1136, -2016, 3136, -5504, 9328, -12112, 14112, -21312] := by decide
#print axioms eta_435be90a7f_ceff
#print axioms eta_435be90a7f_weight
#print axioms eta_435be90a7f_E0
#print axioms eta_435be90a7f_ono
#print axioms eta_435be90a7f_qseries

-- Entry eta_088b826f53: NoteBook1/chapterXVI/p21 | symbolic_latex_eta
def eta_088b826f53 : EtaQuot := { factors := [(1, -8), (2, 16)] }
theorem eta_088b826f53_ceff : cEffCusp0 eta_088b826f53 = (0, 1) := by decide
theorem eta_088b826f53_weight : modularWeight eta_088b826f53 = (4, 1) := by decide
theorem eta_088b826f53_E0 : groundStateShift eta_088b826f53 = (-1, 1) := by decide
theorem eta_088b826f53_ono : (onoCong1 eta_088b826f53, onoCong2 eta_088b826f53 2) = (true, true) := by decide
theorem eta_088b826f53_qseries : etaCoeffs eta_088b826f53 12 = [1, 8, 28, 64, 126, 224, 344, 512, 757, 1008, 1332, 1792] := by decide
#print axioms eta_088b826f53_ceff
#print axioms eta_088b826f53_weight
#print axioms eta_088b826f53_E0
#print axioms eta_088b826f53_ono
#print axioms eta_088b826f53_qseries

-- Entry eta_5d05c315b4: NoteBook1/chapterXVI/p32 | symbolic_latex_eta
def eta_5d05c315b4 : EtaQuot := { factors := [(1, -3), (2, 6), (3, 1), (6, -2)] }
theorem eta_5d05c315b4_ceff : cEffCusp0 eta_5d05c315b4 = (0, 1) := by decide
theorem eta_5d05c315b4_weight : modularWeight eta_5d05c315b4 = (1, 1) := by decide
theorem eta_5d05c315b4_E0 : groundStateShift eta_5d05c315b4 = (0, 1) := by decide
theorem eta_5d05c315b4_ono : (onoCong1 eta_5d05c315b4, onoCong2 eta_5d05c315b4 6) = (true, true) := by decide
theorem eta_5d05c315b4_qseries : etaCoeffs eta_5d05c315b4 12 = [1, 3, 3, 3, 3, 0, 3, 6, 3, 3, 0, 0] := by decide
#print axioms eta_5d05c315b4_ceff
#print axioms eta_5d05c315b4_weight
#print axioms eta_5d05c315b4_E0
#print axioms eta_5d05c315b4_ono
#print axioms eta_5d05c315b4_qseries

-- Entry eta_fb94e42026: NoteBook1/chapterXVI/p32 | symbolic_latex_eta
def eta_fb94e42026 : EtaQuot := { factors := [(1, -6), (2, 15), (3, 2), (4, -6), (6, -5), (12, 2)] }
theorem eta_fb94e42026_ceff : cEffCusp0 eta_fb94e42026 = (0, 1) := by decide
theorem eta_fb94e42026_weight : modularWeight eta_fb94e42026 = (1, 1) := by decide
theorem eta_fb94e42026_E0 : groundStateShift eta_fb94e42026 = (0, 1) := by decide
theorem eta_fb94e42026_ono : (onoCong1 eta_fb94e42026, onoCong2 eta_fb94e42026 12) = (true, true) := by decide
theorem eta_fb94e42026_qseries : etaCoeffs eta_fb94e42026 12 = [1, 6, 12, 6, -6, 0, 12, 12, 12, 6, 0, 0] := by decide
#print axioms eta_fb94e42026_ceff
#print axioms eta_fb94e42026_weight
#print axioms eta_fb94e42026_E0
#print axioms eta_fb94e42026_ono
#print axioms eta_fb94e42026_qseries

-- Entry eta_2bc7179b10: NoteBook1/chapterXVI/p35 | symbolic_latex_eta
def eta_2bc7179b10 : EtaQuot := { factors := [(1, 3), (2, -3), (3, -1), (4, 3), (6, 1), (12, -1)] }
theorem eta_2bc7179b10_ceff : cEffCusp0 eta_2bc7179b10 = (-2, 1) := by decide
theorem eta_2bc7179b10_weight : modularWeight eta_2bc7179b10 = (1, 1) := by decide
theorem eta_2bc7179b10_E0 : groundStateShift eta_2bc7179b10 = (0, 1) := by decide
theorem eta_2bc7179b10_ono : (onoCong1 eta_2bc7179b10, onoCong2 eta_2bc7179b10 12) = (true, true) := by decide
theorem eta_2bc7179b10_qseries : etaCoeffs eta_2bc7179b10 12 = [1, -3, 3, -3, 3, 0, 3, -6, 3, -3, 0, 0] := by decide
#print axioms eta_2bc7179b10_ceff
#print axioms eta_2bc7179b10_weight
#print axioms eta_2bc7179b10_E0
#print axioms eta_2bc7179b10_ono
#print axioms eta_2bc7179b10_qseries

-- Entry eta_d9a72e375e: NoteBook1/chapterXVI/p35 | symbolic_latex_eta
def eta_d9a72e375e : EtaQuot := { factors := [(2, -3), (4, 6), (6, 1), (12, -2)] }
theorem eta_d9a72e375e_ceff : cEffCusp0 eta_d9a72e375e = (0, 1) := by decide
theorem eta_d9a72e375e_weight : modularWeight eta_d9a72e375e = (1, 1) := by decide
theorem eta_d9a72e375e_E0 : groundStateShift eta_d9a72e375e = (0, 1) := by decide
theorem eta_d9a72e375e_ono : (onoCong1 eta_d9a72e375e, onoCong2 eta_d9a72e375e 12) = (true, true) := by decide
theorem eta_d9a72e375e_qseries : etaCoeffs eta_d9a72e375e 12 = [1, 0, 3, 0, 3, 0, 3, 0, 3, 0, 0, 0] := by decide
#print axioms eta_d9a72e375e_ceff
#print axioms eta_d9a72e375e_weight
#print axioms eta_d9a72e375e_E0
#print axioms eta_d9a72e375e_ono
#print axioms eta_d9a72e375e_qseries

-- Entry eta_abad4155c2: NoteBook1/chapterXVI/p44 | symbolic_latex_eta
def eta_abad4155c2 : EtaQuot := { factors := [(3, -2), (5, -2), (6, 5), (10, 5), (12, -2), (20, -2)] }
theorem eta_abad4155c2_ceff : cEffCusp0 eta_abad4155c2 = (0, 1) := by decide
theorem eta_abad4155c2_weight : modularWeight eta_abad4155c2 = (1, 1) := by decide
theorem eta_abad4155c2_E0 : groundStateShift eta_abad4155c2 = (0, 1) := by decide
theorem eta_abad4155c2_ono : (onoCong1 eta_abad4155c2, onoCong2 eta_abad4155c2 60) = (true, true) := by decide
theorem eta_abad4155c2_qseries : etaCoeffs eta_abad4155c2 12 = [1, 0, 0, 2, 0, 2, 0, 0, 4, 0, 0, 0] := by decide
#print axioms eta_abad4155c2_ceff
#print axioms eta_abad4155c2_weight
#print axioms eta_abad4155c2_E0
#print axioms eta_abad4155c2_ono
#print axioms eta_abad4155c2_qseries

-- Entry eta_86befb65d8: NoteBook1/chapterXVI/p45 | symbolic_latex_eta
def eta_86befb65d8 : EtaQuot := { factors := [(1, -2), (2, 4)] }
theorem eta_86befb65d8_ceff : cEffCusp0 eta_86befb65d8 = (0, 1) := by decide
theorem eta_86befb65d8_weight : modularWeight eta_86befb65d8 = (1, 1) := by decide
theorem eta_86befb65d8_E0 : groundStateShift eta_86befb65d8 = (-1, 4) := by decide
theorem eta_86befb65d8_ono : (onoCong1 eta_86befb65d8, onoCong2 eta_86befb65d8 2) = (false, true) := by decide
theorem eta_86befb65d8_qseries : etaCoeffs eta_86befb65d8 12 = [1, 2, 1, 2, 2, 0, 3, 2, 0, 2, 2, 2] := by decide
#print axioms eta_86befb65d8_ceff
#print axioms eta_86befb65d8_weight
#print axioms eta_86befb65d8_E0
#print axioms eta_86befb65d8_ono
#print axioms eta_86befb65d8_qseries

-- Entry eta_db89732997: NoteBook1/chapterXVI/p71 | symbolic_latex_eta
def eta_db89732997 : EtaQuot := { factors := [(5, 1)] }
theorem eta_db89732997_ceff : cEffCusp0 eta_db89732997 = (-1, 5) := by decide
theorem eta_db89732997_weight : modularWeight eta_db89732997 = (1, 2) := by decide
theorem eta_db89732997_E0 : groundStateShift eta_db89732997 = (-5, 24) := by decide
theorem eta_db89732997_ono : (onoCong1 eta_db89732997, onoCong2 eta_db89732997 5) = (false, false) := by decide
theorem eta_db89732997_qseries : etaCoeffs eta_db89732997 12 = [1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1, 0] := by decide
#print axioms eta_db89732997_ceff
#print axioms eta_db89732997_weight
#print axioms eta_db89732997_E0
#print axioms eta_db89732997_ono
#print axioms eta_db89732997_qseries

-- Entry eta_45f4012a55: NoteBook1/chapterXVI/p75 | symbolic_latex_eta
def eta_45f4012a55 : EtaQuot := { factors := [(4, -1), (7, 1), (8, 3), (14, -3), (16, -1), (28, 1)] }
theorem eta_45f4012a55_ceff : cEffCusp0 eta_45f4012a55 = (-3, 112) := by decide
theorem eta_45f4012a55_weight : modularWeight eta_45f4012a55 = (0, 1) := by decide
theorem eta_45f4012a55_E0 : groundStateShift eta_45f4012a55 = (1, 8) := by decide
theorem eta_45f4012a55_ono : (onoCong1 eta_45f4012a55, onoCong2 eta_45f4012a55 112) = (false, false) := by decide
theorem eta_45f4012a55_qseries : etaCoeffs eta_45f4012a55 12 = [1, 0, 0, 0, 1, 0, 0, -1, -1, 0, 0, -1] := by decide
#print axioms eta_45f4012a55_ceff
#print axioms eta_45f4012a55_weight
#print axioms eta_45f4012a55_E0
#print axioms eta_45f4012a55_ono
#print axioms eta_45f4012a55_qseries

-- Entry eta_03622e4460: NoteBook1/chapterXVI/p75 | symbolic_latex_eta
def eta_03622e4460 : EtaQuot := { factors := [(4, 1), (11, -1)] }
theorem eta_03622e4460_ceff : cEffCusp0 eta_03622e4460 = (-7, 44) := by decide
theorem eta_03622e4460_weight : modularWeight eta_03622e4460 = (0, 1) := by decide
theorem eta_03622e4460_E0 : groundStateShift eta_03622e4460 = (7, 24) := by decide
theorem eta_03622e4460_ono : (onoCong1 eta_03622e4460, onoCong2 eta_03622e4460 44) = (false, false) := by decide
theorem eta_03622e4460_qseries : etaCoeffs eta_03622e4460 12 = [1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 1] := by decide
#print axioms eta_03622e4460_ceff
#print axioms eta_03622e4460_weight
#print axioms eta_03622e4460_E0
#print axioms eta_03622e4460_ono
#print axioms eta_03622e4460_qseries

-- Entry eta_839199316b: NoteBook2/chapterXIX/p1 | symbolic_latex_eta
def eta_839199316b : EtaQuot := { factors := [(1, 1), (2, -3), (4, 2)] }
theorem eta_839199316b_ceff : cEffCusp0 eta_839199316b = (0, 1) := by decide
theorem eta_839199316b_weight : modularWeight eta_839199316b = (0, 1) := by decide
theorem eta_839199316b_E0 : groundStateShift eta_839199316b = (-1, 8) := by decide
theorem eta_839199316b_ono : (onoCong1 eta_839199316b, onoCong2 eta_839199316b 4) = (false, true) := by decide
theorem eta_839199316b_qseries : etaCoeffs eta_839199316b 12 = [1, -1, 2, -3, 4, -6, 9, -12, 16, -22, 29, -38] := by decide
#print axioms eta_839199316b_ceff
#print axioms eta_839199316b_weight
#print axioms eta_839199316b_E0
#print axioms eta_839199316b_ono
#print axioms eta_839199316b_qseries

-- Entry eta_33cc69d257: NoteBook2/chapterXIX/p1 | symbolic_latex_eta
def eta_33cc69d257 : EtaQuot := { factors := [(1, -2), (2, 5), (3, -2), (4, -2), (6, 5), (12, -2)] }
theorem eta_33cc69d257_ceff : cEffCusp0 eta_33cc69d257 = (0, 1) := by decide
theorem eta_33cc69d257_weight : modularWeight eta_33cc69d257 = (1, 1) := by decide
theorem eta_33cc69d257_E0 : groundStateShift eta_33cc69d257 = (0, 1) := by decide
theorem eta_33cc69d257_ono : (onoCong1 eta_33cc69d257, onoCong2 eta_33cc69d257 12) = (true, true) := by decide
theorem eta_33cc69d257_qseries : etaCoeffs eta_33cc69d257 12 = [1, 2, 0, 2, 6, 0, 0, 4, 0, 2, 0, 0] := by decide
#print axioms eta_33cc69d257_ceff
#print axioms eta_33cc69d257_weight
#print axioms eta_33cc69d257_E0
#print axioms eta_33cc69d257_ono
#print axioms eta_33cc69d257_qseries

-- Entry eta_377542ab0e: NoteBook2/chapterXIX/p11 | symbolic_latex_eta
def eta_377542ab0e : EtaQuot := { factors := [(1, -1), (2, 2), (7, -1), (14, 2)] }
theorem eta_377542ab0e_ceff : cEffCusp0 eta_377542ab0e = (0, 1) := by decide
theorem eta_377542ab0e_weight : modularWeight eta_377542ab0e = (1, 1) := by decide
theorem eta_377542ab0e_E0 : groundStateShift eta_377542ab0e = (-1, 1) := by decide
theorem eta_377542ab0e_ono : (onoCong1 eta_377542ab0e, onoCong2 eta_377542ab0e 14) = (true, true) := by decide
theorem eta_377542ab0e_qseries : etaCoeffs eta_377542ab0e 12 = [1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 2, 0] := by decide
#print axioms eta_377542ab0e_ceff
#print axioms eta_377542ab0e_weight
#print axioms eta_377542ab0e_E0
#print axioms eta_377542ab0e_ono
#print axioms eta_377542ab0e_qseries

-- Entry eta_0e6f734e68: NoteBook2/chapterXIX/p11 | symbolic_latex_eta
def eta_0e6f734e68 : EtaQuot := { factors := [(1, -1), (7, 1)] }
theorem eta_0e6f734e68_ceff : cEffCusp0 eta_0e6f734e68 = (6, 7) := by decide
theorem eta_0e6f734e68_weight : modularWeight eta_0e6f734e68 = (0, 1) := by decide
theorem eta_0e6f734e68_E0 : groundStateShift eta_0e6f734e68 = (-1, 4) := by decide
theorem eta_0e6f734e68_ono : (onoCong1 eta_0e6f734e68, onoCong2 eta_0e6f734e68 7) = (false, false) := by decide
theorem eta_0e6f734e68_qseries : etaCoeffs eta_0e6f734e68 12 = [1, 1, 2, 3, 5, 7, 11, 14, 21, 28, 39, 51] := by decide
#print axioms eta_0e6f734e68_ceff
#print axioms eta_0e6f734e68_weight
#print axioms eta_0e6f734e68_E0
#print axioms eta_0e6f734e68_ono
#print axioms eta_0e6f734e68_qseries

-- Entry eta_bf9d59df69: NoteBook2/chapterXIX/p5 | symbolic_latex_eta
def eta_bf9d59df69 : EtaQuot := { factors := [(1, -1), (2, 2), (5, -2), (10, 4)] }
theorem eta_bf9d59df69_ceff : cEffCusp0 eta_bf9d59df69 = (0, 1) := by decide
theorem eta_bf9d59df69_weight : modularWeight eta_bf9d59df69 = (3, 2) := by decide
theorem eta_bf9d59df69_E0 : groundStateShift eta_bf9d59df69 = (-11, 8) := by decide
theorem eta_bf9d59df69_ono : (onoCong1 eta_bf9d59df69, onoCong2 eta_bf9d59df69 10) = (false, true) := by decide
theorem eta_bf9d59df69_qseries : etaCoeffs eta_bf9d59df69 12 = [1, 1, 0, 1, 0, 2, 3, 0, 2, 0, 2, 3] := by decide
#print axioms eta_bf9d59df69_ceff
#print axioms eta_bf9d59df69_weight
#print axioms eta_bf9d59df69_E0
#print axioms eta_bf9d59df69_ono
#print axioms eta_bf9d59df69_qseries

-- Entry eta_698e93c72a: NoteBook2/chapterXIX/p6 | symbolic_latex_eta
def eta_698e93c72a : EtaQuot := { factors := [(7, -4), (14, 10), (28, -4)] }
theorem eta_698e93c72a_ceff : cEffCusp0 eta_698e93c72a = (0, 1) := by decide
theorem eta_698e93c72a_weight : modularWeight eta_698e93c72a = (1, 1) := by decide
theorem eta_698e93c72a_E0 : groundStateShift eta_698e93c72a = (0, 1) := by decide
theorem eta_698e93c72a_ono : (onoCong1 eta_698e93c72a, onoCong2 eta_698e93c72a 28) = (true, true) := by decide
theorem eta_698e93c72a_qseries : etaCoeffs eta_698e93c72a 12 = [1, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0] := by decide
#print axioms eta_698e93c72a_ceff
#print axioms eta_698e93c72a_weight
#print axioms eta_698e93c72a_E0
#print axioms eta_698e93c72a_ono
#print axioms eta_698e93c72a_qseries

-- Entry eta_e0f4183a86: NoteBook2/chapterXIX/p6 | symbolic_latex_eta
def eta_e0f4183a86 : EtaQuot := { factors := [(1, -5), (2, 15), (4, -5), (7, 1), (14, -3), (28, 1)] }
theorem eta_e0f4183a86_ceff : cEffCusp0 eta_e0f4183a86 = (-17, 14) := by decide
theorem eta_e0f4183a86_weight : modularWeight eta_e0f4183a86 = (2, 1) := by decide
theorem eta_e0f4183a86_E0 : groundStateShift eta_e0f4183a86 = (1, 12) := by decide
theorem eta_e0f4183a86_ono : (onoCong1 eta_e0f4183a86, onoCong2 eta_e0f4183a86 28) = (false, false) := by decide
theorem eta_e0f4183a86_qseries : etaCoeffs eta_e0f4183a86 12 = [1, 5, 5, -10, -15, 6, -5, -26, 10, 15, 19, 60] := by decide
#print axioms eta_e0f4183a86_ceff
#print axioms eta_e0f4183a86_weight
#print axioms eta_e0f4183a86_E0
#print axioms eta_e0f4183a86_ono
#print axioms eta_e0f4183a86_qseries

-- Entry eta_b5b074eef6: NoteBook2/chapterXIX/p6 | symbolic_latex_eta
def eta_b5b074eef6 : EtaQuot := { factors := [(1, -5), (2, 10), (7, 1), (14, -2)] }
theorem eta_b5b074eef6_ceff : cEffCusp0 eta_b5b074eef6 = (0, 1) := by decide
theorem eta_b5b074eef6_weight : modularWeight eta_b5b074eef6 = (2, 1) := by decide
theorem eta_b5b074eef6_E0 : groundStateShift eta_b5b074eef6 = (1, 4) := by decide
theorem eta_b5b074eef6_ono : (onoCong1 eta_b5b074eef6, onoCong2 eta_b5b074eef6 14) = (false, true) := by decide
theorem eta_b5b074eef6_qseries : etaCoeffs eta_b5b074eef6 12 = [1, 5, 10, 15, 25, 31, 35, 54, 55, 50, 75, 65] := by decide
#print axioms eta_b5b074eef6_ceff
#print axioms eta_b5b074eef6_weight
#print axioms eta_b5b074eef6_E0
#print axioms eta_b5b074eef6_ono
#print axioms eta_b5b074eef6_qseries

-- Entry eta_a136f1ebfa: NoteBook2/chapterXX/p1 | symbolic_latex_eta
def eta_a136f1ebfa : EtaQuot := { factors := [(3, 1), (6, -2)] }
theorem eta_a136f1ebfa_ceff : cEffCusp0 eta_a136f1ebfa = (0, 1) := by decide
theorem eta_a136f1ebfa_weight : modularWeight eta_a136f1ebfa = (-1, 2) := by decide
theorem eta_a136f1ebfa_E0 : groundStateShift eta_a136f1ebfa = (3, 8) := by decide
theorem eta_a136f1ebfa_ono : (onoCong1 eta_a136f1ebfa, onoCong2 eta_a136f1ebfa 6) = (false, true) := by decide
theorem eta_a136f1ebfa_qseries : etaCoeffs eta_a136f1ebfa 12 = [1, 0, 0, -1, 0, 0, 1, 0, 0, -2, 0, 0] := by decide
#print axioms eta_a136f1ebfa_ceff
#print axioms eta_a136f1ebfa_weight
#print axioms eta_a136f1ebfa_E0
#print axioms eta_a136f1ebfa_ono
#print axioms eta_a136f1ebfa_qseries

-- Entry eta_fd778a638b: NoteBook2/chapterXX/p1 | symbolic_latex_eta
def eta_fd778a638b : EtaQuot := { factors := [(5, -1), (10, 2)] }
theorem eta_fd778a638b_ceff : cEffCusp0 eta_fd778a638b = (0, 1) := by decide
theorem eta_fd778a638b_weight : modularWeight eta_fd778a638b = (1, 2) := by decide
theorem eta_fd778a638b_E0 : groundStateShift eta_fd778a638b = (-5, 8) := by decide
theorem eta_fd778a638b_ono : (onoCong1 eta_fd778a638b, onoCong2 eta_fd778a638b 10) = (false, true) := by decide
theorem eta_fd778a638b_qseries : etaCoeffs eta_fd778a638b 12 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0] := by decide
#print axioms eta_fd778a638b_ceff
#print axioms eta_fd778a638b_weight
#print axioms eta_fd778a638b_E0
#print axioms eta_fd778a638b_ono
#print axioms eta_fd778a638b_qseries

-- Entry eta_12de842a07: NoteBook2/chapterXXI/p100 | symbolic_latex_eta
def eta_12de842a07 : EtaQuot := { factors := [(1, -1), (2, 2), (3, -1), (4, -1), (6, 2), (8, 2)] }
theorem eta_12de842a07_ceff : cEffCusp0 eta_12de842a07 = (0, 1) := by decide
theorem eta_12de842a07_weight : modularWeight eta_12de842a07 = (3, 2) := by decide
theorem eta_12de842a07_E0 : groundStateShift eta_12de842a07 = (-1, 1) := by decide
theorem eta_12de842a07_ono : (onoCong1 eta_12de842a07, onoCong2 eta_12de842a07 24) = (true, true) := by decide
theorem eta_12de842a07_qseries : etaCoeffs eta_12de842a07 12 = [1, 1, 0, 2, 2, 1, 2, 2, 1, 2, 4, 0] := by decide
#print axioms eta_12de842a07_ceff
#print axioms eta_12de842a07_weight
#print axioms eta_12de842a07_E0
#print axioms eta_12de842a07_ono
#print axioms eta_12de842a07_qseries

-- Entry eta_19302a9e44: NoteBook2/chapterXXI/p100 | symbolic_latex_eta
def eta_19302a9e44 : EtaQuot := { factors := [(3, -4), (6, 11), (12, -6)] }
theorem eta_19302a9e44_ceff : cEffCusp0 eta_19302a9e44 = (0, 1) := by decide
theorem eta_19302a9e44_weight : modularWeight eta_19302a9e44 = (1, 2) := by decide
theorem eta_19302a9e44_E0 : groundStateShift eta_19302a9e44 = (3, 4) := by decide
theorem eta_19302a9e44_ono : (onoCong1 eta_19302a9e44, onoCong2 eta_19302a9e44 12) = (false, true) := by decide
theorem eta_19302a9e44_qseries : etaCoeffs eta_19302a9e44 12 = [1, 0, 0, 4, 0, 0, 3, 0, 0, -4, 0, 0] := by decide
#print axioms eta_19302a9e44_ceff
#print axioms eta_19302a9e44_weight
#print axioms eta_19302a9e44_E0
#print axioms eta_19302a9e44_ono
#print axioms eta_19302a9e44_qseries

-- Entry eta_e7eb2c90c7: NoteBook2/chapterXXI/p12 | symbolic_latex_eta
def eta_e7eb2c90c7 : EtaQuot := { factors := [(1, 4), (2, -2)] }
theorem eta_e7eb2c90c7_ceff : cEffCusp0 eta_e7eb2c90c7 = (-3, 1) := by decide
theorem eta_e7eb2c90c7_weight : modularWeight eta_e7eb2c90c7 = (1, 1) := by decide
theorem eta_e7eb2c90c7_E0 : groundStateShift eta_e7eb2c90c7 = (0, 1) := by decide
theorem eta_e7eb2c90c7_ono : (onoCong1 eta_e7eb2c90c7, onoCong2 eta_e7eb2c90c7 2) = (true, false) := by decide
theorem eta_e7eb2c90c7_qseries : etaCoeffs eta_e7eb2c90c7 12 = [1, -4, 4, 0, 4, -8, 0, 0, 4, -4, 8, 0] := by decide
#print axioms eta_e7eb2c90c7_ceff
#print axioms eta_e7eb2c90c7_weight
#print axioms eta_e7eb2c90c7_E0
#print axioms eta_e7eb2c90c7_ono
#print axioms eta_e7eb2c90c7_qseries

-- Entry eta_ad84460504: NoteBook2/chapterXXI/p12 | symbolic_latex_eta
def eta_ad84460504 : EtaQuot := { factors := [(1, -3), (2, 7), (4, -2)] }
theorem eta_ad84460504_ceff : cEffCusp0 eta_ad84460504 = (0, 1) := by decide
theorem eta_ad84460504_weight : modularWeight eta_ad84460504 = (1, 1) := by decide
theorem eta_ad84460504_E0 : groundStateShift eta_ad84460504 = (-1, 8) := by decide
theorem eta_ad84460504_ono : (onoCong1 eta_ad84460504, onoCong2 eta_ad84460504 4) = (false, true) := by decide
theorem eta_ad84460504_qseries : etaCoeffs eta_ad84460504 12 = [1, 3, 2, 1, 4, 2, 1, 4, 0, 2, 5, 2] := by decide
#print axioms eta_ad84460504_ceff
#print axioms eta_ad84460504_weight
#print axioms eta_ad84460504_E0
#print axioms eta_ad84460504_ono
#print axioms eta_ad84460504_qseries

-- Ramanujan Manuscript Identity eq_d6899de389: NoteBook1/chapterXV/p19 | \phi(x) + \phi(-x) = 2\phi(x^4)
def eq_d6899de389_lhs : List (Int × Nat × List (Nat × Int)) := [(1, 0, [(1, -2), (2, 5), (4, -2)]), (1, 0, [(1, 2), (2, -1)])]
def eq_d6899de389_rhs : List (Int × Nat × List (Nat × Int)) := [(2, 0, [(4, -2), (8, 5), (16, -2)])]
theorem eq_d6899de389_identity : evalLinearEta eq_d6899de389_lhs 16 = evalLinearEta eq_d6899de389_rhs 16 := by decide
#print axioms eq_d6899de389_identity

-- Ramanujan Manuscript Identity eq_c23aa45585: NoteBook1/chapterXV/p19 | \phi(x) - \phi(-x) = 4x\psi(x^8)
def eq_c23aa45585_lhs : List (Int × Nat × List (Nat × Int)) := [(1, 0, [(1, -2), (2, 5), (4, -2)]), (-1, 0, [(1, 2), (2, -1)])]
def eq_c23aa45585_rhs : List (Int × Nat × List (Nat × Int)) := [(4, 1, [(8, -1), (16, 2)])]
theorem eq_c23aa45585_identity : evalLinearEta eq_c23aa45585_lhs 16 = evalLinearEta eq_c23aa45585_rhs 16 := by decide
#print axioms eq_c23aa45585_identity

-- Ramanujan Manuscript Identity eq_0722eebfe8: NoteBook1/chapterXVI/p35 | \frac{\psi^3(x)}{\psi(x^3)} + \frac{\psi^3(-x)}{\psi(-x^3)} = 2 \frac{\psi^3(x^2)}{\psi(x^
def eq_0722eebfe8_lhs : List (Int × Nat × List (Nat × Int)) := [(1, 0, [(1, -3), (2, 6), (3, 1), (6, -2)]), (1, 0, [(1, 3), (2, -3), (3, -1), (4, 3), (6, 1), (12, -1)])]
def eq_0722eebfe8_rhs : List (Int × Nat × List (Nat × Int)) := [(2, 0, [(2, -3), (4, 6), (6, 1), (12, -2)])]
theorem eq_0722eebfe8_identity : evalLinearEta eq_0722eebfe8_lhs 16 = evalLinearEta eq_0722eebfe8_rhs 16 := by decide
#print axioms eq_0722eebfe8_identity

-- Ramanujan Manuscript Identity eq_460927b577: NoteBook2/chapterXVI/p6 | \frac{f(x)}{f(-x)} = \frac{\psi(x)}{\psi(-x)}
def eq_460927b577_lhs : List (Int × Nat × List (Nat × Int)) := [(1, 0, [(1, -1), (2, 3), (4, -1), (1, -1)])]
def eq_460927b577_rhs : List (Int × Nat × List (Nat × Int)) := [(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])]
theorem eq_460927b577_identity : evalLinearEta eq_460927b577_lhs 16 = evalLinearEta eq_460927b577_rhs 16 := by decide
#print axioms eq_460927b577_identity

-- Ramanujan Manuscript Identity eq_2847c49f95: NoteBook2/chapterXVI/p6 | \frac{\psi(x)}{\psi(-x)} = \frac{\chi(x)}{\chi(-x)}
def eq_2847c49f95_lhs : List (Int × Nat × List (Nat × Int)) := [(1, 0, [(1, -1), (2, 2), (1, -1), (2, 1), (4, -1)])]
def eq_2847c49f95_rhs : List (Int × Nat × List (Nat × Int)) := [(1, 0, [(1, -1), (2, 2), (4, -1), (1, -1), (2, 1)])]
theorem eq_2847c49f95_identity : evalLinearEta eq_2847c49f95_lhs 16 = evalLinearEta eq_2847c49f95_rhs 16 := by decide
#print axioms eq_2847c49f95_identity

end DualScale.CampaignKernel

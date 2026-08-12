import Mathlib.Data.Int.Basic
import Mathlib.Data.List.Basic
import DualScale.QSeries.Basic
import DualScale.QSeries.EtaQuotient

namespace DualScale.QSeries.EtaQuotient

open DualScale.QSeries

def baseEta (len : ℕ) : TruncQSeries :=
  List.ofFn fun i : Fin len =>
    let n : ℤ := i.val
    let ks := List.range (i.val + 1)
    let pos_k := ks.find? (fun (k : ℕ) => (k : ℤ) * (3 * (k : ℤ) - 1) / 2 == n)
    let neg_k := ks.find? (fun (k : ℕ) => k > 0 ∧ (k : ℤ) * (3 * (k : ℤ) + 1) / 2 == n)
    match pos_k, neg_k with
    | some k, _ => if k % 2 == 0 then (1 : ℤ) else -1
    | _, some k => if k % 2 == 0 then (1 : ℤ) else -1
    | _, _ => 0

def coeffs (eq : EtaQuot) (len : ℕ) : TruncQSeries :=
  eq.factors.foldl (fun acc dr =>
    let d := dr.1
    let r := dr.2
    if r == 0 then acc
    else
      let base := baseEta len
      let spaced := List.ofFn fun i : Fin len =>
        if i.val % d == 0 then base.getD (i.val / d) 0 else 0
      if r > 0 then
        mul acc (pow spaced r.toNat len) len
      else
        mul acc (pow (inv spaced len) (-r).toNat len) len
  ) (one len)

#eval coeffs nb1_ch1_discovery 20
#eval coeffs nb3_vacuum 20
#eval coeffs deep_burn 20
#eval coeffs ⟨[(1, 1)]⟩ 20
#eval coeffs ⟨[(1, -1)]⟩ 20

end DualScale.QSeries.EtaQuotient

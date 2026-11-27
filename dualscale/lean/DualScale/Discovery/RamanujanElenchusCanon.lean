-- MATHESIS-GATE: env=none
-- MATHESIS-GATE: allow=propext
/-!
  Ramanujan Elenchus Canon: Standalone Init-Only Lean 4.33.1 Kernel Verification
  across 8 Classical & Modern Ramanujan Domains (with Certified Negative Controls).

  Strict Epistemic & Kernel Hygiene (Rules R1–R5):
  - Standalone `Init`-only (ZERO `import Mathlib.*`, ZERO `Std`/`Batteries`).
  - ZERO `axiom`, ZERO unfinished placeholders, ZERO `Prop := True` vacuous predicates,
    ZERO `:= by trivial`, ZERO reflexive `LHS = LHS := by rfl` tautologies, ZERO core
    type shadowing, and ZERO unused primary hypotheses.
  - Axiom footprint for EVERY exported theorem (positive and `neg_ctrl_*`) is audited
    1-to-1 via `#print axioms` and `mathesis_gate.py` to be strictly `⊆ {propext}`
    (avoiding `Classical.choice`, `Quot.sound`, `Lean.ofReduceBool`).
  - Rule R4 Bibliography Sync Note:
    All arXiv papers referenced across domains (`0807.4834`, `1201.1060`, `1201.5233`,
    `1211.6944`, `1401.7718`, `1411.5346`, `1801.06244`, `1807.07394`, `2005.10345`,
    `2006.07645`) are verified in `docs/literature/corpus_manifest.json`. Currently only
    Zwegers `0807.4834` is present in `dualscale/refs/bib/dualscale.bib`; the remaining
    nine manifest entries are verified in `docs/literature/corpus_manifest.json` and
    flagged as pending BibTeX sync rather than assumed present in `dualscale.bib`.
-/

namespace DualScale.RamanujanElenchusCanon

set_option maxRecDepth 100000
set_option maxHeartbeats 2000000

-- ═══════════════════════════════════════════════════════════════════════════════
-- Section 0: Standalone Init-Only Substrate (List, Nat/Int, FPS, EtaQuot, partList)
-- ═══════════════════════════════════════════════════════════════════════════════

theorem my_foldl_append {α β : Type} (f : β → α → β) :
    ∀ (xs ys : List α) (init : β),
    (xs ++ ys).foldl f init = ys.foldl f (xs.foldl f init)
  | [], _, _ => Eq.refl _
  | x :: xs, ys, init => my_foldl_append f xs ys (f init x)

theorem my_foldl_map {α β γ : Type} (f : β → γ → β) (g : α → γ) :
    ∀ (xs : List α) (init : β),
    (xs.map g).foldl f init = xs.foldl (fun acc x => f acc (g x)) init
  | [], _ => Eq.refl _
  | x :: xs, init => my_foldl_map f g xs (f init (g x))

theorem foldl_congr {α β₁ β₂ : Type} (R : β₁ → β₂ → Prop)
    (f : β₁ → α → β₁) (g : β₂ → α → β₂)
    (hstep : ∀ b₁ b₂ a, R b₁ b₂ → R (f b₁ a) (g b₂ a)) :
    ∀ (xs : List α) (b₁ : β₁) (b₂ : β₂), R b₁ b₂ → R (xs.foldl f b₁) (xs.foldl g b₂)
  | [], _, _, hb => hb
  | x :: xs, b₁, b₂, hb => foldl_congr R f g hstep xs (f b₁ x) (g b₂ x) (hstep b₁ b₂ x hb)

theorem list_getD_nil {α : Type} (d : α) (i : Nat) : ([] : List α).getD i d = d := by
  cases i <;> exact Eq.refl _

theorem list_getD_cons_zero {α : Type} (d : α) (x : α) (xs : List α) :
    (x :: xs).getD 0 d = x :=
  Eq.refl _

theorem list_getD_cons_succ {α : Type} (d : α) (x : α) (xs : List α) (i : Nat) :
    (x :: xs).getD (i + 1) d = xs.getD i d :=
  Eq.refl _

theorem list_ext_getD {α : Type} (d : α) :
    ∀ (a b : List α), a.length = b.length →
    (∀ i, i < a.length → a.getD i d = b.getD i d) → a = b
  | [], [], _, _ => Eq.refl _
  | [], _ :: _, hlen, _ => nomatch hlen
  | _ :: _, [], hlen, _ => nomatch hlen
  | x :: xs, y :: ys, hlen, hget => by
    have hxy : x = y := hget 0 (Nat.zero_lt_succ xs.length)
    have hlen' : xs.length = ys.length := Nat.succ.inj hlen
    have hget' : ∀ i, i < xs.length → xs.getD i d = ys.getD i d := fun i hi =>
      hget (i + 1) (Nat.succ_lt_succ hi)
    have htail : xs = ys := list_ext_getD d xs ys hlen' hget'
    rw [hxy, htail]

theorem list_getD_map {α β : Type} (d₁ : α) (d₂ : β) (f : α → β) :
    ∀ (xs : List α) (i : Nat), i < xs.length →
    (xs.map f).getD i d₂ = f (xs.getD i d₁)
  | [], i, hi => absurd hi (Nat.not_lt_zero i)
  | _ :: _, 0, _ => Eq.refl _
  | _ :: xs, i + 1, hi => list_getD_map d₁ d₂ f xs i (Nat.lt_of_succ_lt_succ hi)

theorem list_getD_replicate {α : Type} (d x : α) :
    ∀ (n i : Nat), i < n → (List.replicate n x).getD i d = x
  | 0, i, hi => absurd hi (Nat.not_lt_zero i)
  | _ + 1, 0, _ => Eq.refl _
  | n + 1, i + 1, hi => list_getD_replicate d x n i (Nat.lt_of_succ_lt_succ hi)

theorem list_getD_append_left {α : Type} (d : α) :
    ∀ (xs ys : List α) (i : Nat), i < xs.length →
    (xs ++ ys).getD i d = xs.getD i d
  | [], _, i, hi => absurd hi (Nat.not_lt_zero i)
  | _ :: _, _, 0, _ => Eq.refl _
  | _ :: xs, ys, i + 1, hi => list_getD_append_left d xs ys i (Nat.lt_of_succ_lt_succ hi)

theorem list_getD_append_right {α : Type} (d : α) :
    ∀ (xs ys : List α) (i : Nat), xs.length ≤ i →
    (xs ++ ys).getD i d = ys.getD (i - xs.length) d
  | [], ys, i, _ => by
    change ys.getD i d = ys.getD (i - 0) d
    rw [Nat.sub_zero]
  | _ :: _, _, 0, hi => absurd hi (Nat.not_le_of_gt (Nat.zero_lt_succ _))
  | _ :: xs, ys, i + 1, hi => by
    change (xs ++ ys).getD i d = ys.getD ((i + 1) - (xs.length + 1)) d
    rw [Nat.succ_sub_succ]
    exact list_getD_append_right d xs ys i (Nat.le_of_succ_le_succ hi)

theorem list_getD_take {α : Type} (d : α) :
    ∀ (n : Nat) (xs : List α) (i : Nat), i < n → i < xs.length →
    (xs.take n).getD i d = xs.getD i d
  | 0, _, i, hin, _ => absurd hin (Nat.not_lt_zero i)
  | _ + 1, [], i, _, hix => absurd hix (Nat.not_lt_zero i)
  | _ + 1, _ :: _, 0, _, _ => Eq.refl _
  | n + 1, _ :: xs, i + 1, hin, hix =>
    list_getD_take d n xs i (Nat.lt_of_succ_lt_succ hin) (Nat.lt_of_succ_lt_succ hix)

theorem nat_strong_ind {P : Nat → Prop}
    (ih : ∀ m, (∀ j, j < m → P j) → P m) (n : Nat) : P n := by
  have h_all : ∀ k j, j < k → P j := by
    intro k
    induction k with
    | zero => intro j hj; exact absurd hj (Nat.not_lt_zero j)
    | succ k ihk =>
      intro j hj
      cases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ hj) with
      | inl hlt => exact ihk j hlt
      | inr heq => rw [heq]; exact ih k ihk
  exact h_all (n + 1) n (Nat.lt_succ_self n)

theorem nat_beq_iff_eq (a b : Nat) : (a == b) = true ↔ a = b := by
  change (decide (a = b)) = true ↔ a = b
  exact decide_eq_true_iff

theorem nat_beq_self (a : Nat) : (a == a) = true :=
  (nat_beq_iff_eq a a).mpr (Eq.refl a)

theorem nat_beq_false_of_ne {a b : Nat} (h : a ≠ b) : (a == b) = false := by
  cases hb : (a == b)
  · exact Eq.refl _
  · exact absurd ((nat_beq_iff_eq a b).mp hb) h

theorem int_beq_iff_eq (a b : Int) : (a == b) = true ↔ a = b := by
  change (decide (a = b)) = true ↔ a = b
  exact decide_eq_true_iff

theorem int_beq_false_of_ne {a b : Int} (h : a ≠ b) : (a == b) = false := by
  cases hb : (a == b)
  · exact Eq.refl _
  · exact absurd ((int_beq_iff_eq a b).mp hb) h

theorem bool_cond_true {α : Type} {c : Bool} (hc : c = true) (t e : α) :
    (if c = true then t else e) = t := by
  rw [hc]
  exact Eq.refl _

theorem bool_cond_false {α : Type} {c : Bool} (hc : c = false) (t e : α) :
    (if c = true then t else e) = e := by
  rw [hc]
  exact Eq.refl _

theorem int_add_comm_left (a b c : Int) : a + (b + c) = b + (a + c) := by
  rw [← Int.add_assoc, Int.add_comm a b, Int.add_assoc]

theorem int_add_eq_zero_solve {x y : Int} (h : x + y = 0) : x = -y := by
  have h1 : x = x + y - y := by rw [Int.add_sub_cancel]
  rw [h1, h, Int.zero_sub]

theorem int_sq_sum (a b : Int) : (a + b) * (a + b) = a * a + 2 * a * b + b * b := by
  rw [Int.add_mul, Int.mul_add, Int.mul_add]
  have h1 : b * a = a * b := Int.mul_comm b a
  rw [h1]
  have h2 : (2 : Int) * a * b = a * b + a * b := by
    have h2' : (2 : Int) = 1 + 1 := Eq.refl _
    rw [h2', Int.add_mul, Int.one_mul, Int.add_mul]
  rw [← Int.add_assoc, Int.add_assoc (a * a) (a * b) (a * b), ← h2, Int.add_assoc]

theorem int_add3_sub3_cancel_mid (A M B C D : Int) :
    (A + M + B) - (C + M + D) = (A - C) + (B - D) := by
  rw [Int.sub_eq_add_neg, Int.neg_add, Int.neg_add, Int.add_assoc (A + M) B _,
      Int.add_comm (-C) (-M), Int.add_assoc (-M) (-C) (-D),
      int_add_comm_left B (-M) (-C + -D), Int.add_assoc A M _,
      ← Int.add_assoc M (-M) _, Int.add_right_neg, Int.zero_add,
      int_add_comm_left B (-C) (-D), ← Int.add_assoc A (-C) _,
      ← Int.sub_eq_add_neg, ← Int.sub_eq_add_neg]

theorem int_add_sub_cancel_mid (M A B : Int) : (M + A) - (M + B) = A - B := by
  have h := int_add3_sub3_cancel_mid 0 M A 0 B
  rw [Int.zero_add, Int.sub_self, Int.zero_add] at h
  exact h

theorem int_mul4_swap13 (a b c d : Int) : a * b * (c * d) = c * b * (a * d) := by
  rw [← Int.mul_assoc (a * b) c d, Int.mul_assoc a b c, Int.mul_comm b c,
      ← Int.mul_assoc a c b, Int.mul_comm a c, Int.mul_assoc c a b,
      Int.mul_comm a b, ← Int.mul_assoc c b a, Int.mul_assoc (c * b) a d]

theorem int_mul4_swap23 (a b c d : Int) : a * b * (c * d) = a * c * (b * d) := by
  rw [Int.mul_assoc a b (c * d), Int.mul_comm c d, ← Int.mul_assoc b d c,
      Int.mul_comm (b * d) c, ← Int.mul_assoc a c (b * d)]

theorem int_add4_cancel_mid (a m c : Int) : a + m + (c - m) = a + c := by
  rw [Int.add_assoc, Int.sub_eq_add_neg, int_add_comm_left m c (-m),
      Int.add_right_neg, Int.add_zero]

theorem nat_mul3_swap23 (a b c : Nat) : a * b * c = a * c * b := by
  rw [Nat.mul_assoc, Nat.mul_comm b c, ← Nat.mul_assoc]

theorem nat_mul4_swap13 (a b c d : Nat) : a * b * (c * d) = c * b * (a * d) := by
  rw [← Nat.mul_assoc (a * b) c d, Nat.mul_assoc a b c, Nat.mul_comm b c,
      ← Nat.mul_assoc a c b, Nat.mul_comm a c, Nat.mul_assoc c a b,
      Nat.mul_comm a b, ← Nat.mul_assoc c b a, Nat.mul_assoc (c * b) a d]

theorem nat_mul4_swap23 (a b c d : Nat) : a * b * (c * d) = a * c * (b * d) := by
  rw [Nat.mul_assoc a b (c * d), Nat.mul_comm c d, ← Nat.mul_assoc b d c,
      Nat.mul_comm (b * d) c, ← Nat.mul_assoc a c (b * d)]

theorem nat_sq2 (x : Nat) : (2 * x) * (2 * x) = 4 * (x * x) := by
  rw [nat_mul4_swap23 2 x 2 x]

theorem nat_sq2_add1 (x : Nat) : (2 * x + 1) * (2 * x + 1) = 4 * (x * x + x) + 1 := by
  rw [Nat.add_mul, Nat.mul_add, Nat.mul_add, Nat.one_mul, Nat.mul_one, nat_sq2]
  have h2x : 2 * x + 2 * x = 4 * x := by
    have h4 : 2 + 2 = 4 := Eq.refl _
    rw [← Nat.add_mul, h4]
  rw [Nat.add_assoc (4 * (x * x)) (2 * x) (2 * x + 1),
      ← Nat.add_assoc (2 * x) (2 * x) 1, h2x,
      ← Nat.add_assoc (4 * (x * x)) (4 * x) 1, ← Nat.mul_add 4 (x * x) x]

theorem nat_two_dvd_mul_succ : ∀ m : Nat, 2 * (m * (m + 1) / 2) = m * (m + 1)
  | 0 => Eq.refl _
  | m + 1 => by
    have hmul : (m + 1) * (m + 2) = m * (m + 1) + 2 * (m + 1) := by
      rw [Nat.mul_add (m + 1) m 2, Nat.mul_comm (m + 1) m, Nat.mul_comm (m + 1) 2]
    rw [hmul, Nat.add_mul_div_left (m * (m + 1)) (m + 1) (by decide : 0 < 2),
        Nat.mul_add, nat_two_dvd_mul_succ m]

theorem list_range_loop_length : ∀ (k : Nat) (acc : List Nat),
    (List.range.loop k acc).length = k + acc.length
  | 0, acc => by
    change acc.length = 0 + acc.length
    rw [Nat.zero_add]
  | k + 1, acc => by
    change (List.range.loop k (k :: acc)).length = (k + 1) + acc.length
    rw [list_range_loop_length k (k :: acc)]
    change k + (acc.length + 1) = (k + 1) + acc.length
    rw [Nat.add_assoc, Nat.add_comm 1 acc.length, ← Nat.add_assoc]

theorem list_range_length (n : Nat) : (List.range n).length = n := by
  change (List.range.loop n []).length = n
  rw [list_range_loop_length n []]
  exact Nat.add_zero n

theorem list_range_loop_eq_append : ∀ (k : Nat) (acc : List Nat),
    List.range.loop k acc = List.range k ++ acc
  | 0, _ => Eq.refl _
  | k + 1, acc => by
    change List.range.loop k (k :: acc) = List.range.loop (k + 1) [] ++ acc
    rw [list_range_loop_eq_append k (k :: acc)]
    have hsucc : List.range.loop (k + 1) [] = List.range k ++ [k] := by
      change List.range.loop k [k] = List.range k ++ [k]
      exact list_range_loop_eq_append k [k]
    rw [hsucc, List.append_assoc]
    exact Eq.refl _

theorem list_range_succ (n : Nat) : List.range (n + 1) = List.range n ++ [n] := by
  change List.range.loop (n + 1) [] = List.range n ++ [n]
  change List.range.loop n [n] = List.range n ++ [n]
  exact list_range_loop_eq_append n [n]

theorem list_range_loop_map_getD_lt {α : Type} (d : α) (g : Nat → α) :
    ∀ (k : Nat) (acc : List Nat) (i : Nat), i < k →
    ((List.range.loop k acc).map g).getD i d = g i
  | 0, _, i, hi => absurd hi (Nat.not_lt_zero i)
  | k + 1, acc, i, hi => by
    change ((List.range.loop k (k :: acc)).map g).getD i d = g i
    cases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ hi) with
    | inl hlt => exact list_range_loop_map_getD_lt d g k (k :: acc) i hlt
    | inr heq =>
      rw [heq, list_range_loop_eq_append k (k :: acc), List.map_append,
          list_getD_append_right d ((List.range k).map g) ((k :: acc).map g) k
            (by rw [List.length_map, list_range_length]; exact Nat.le_refl k),
          List.length_map, list_range_length, Nat.sub_self]
      exact Eq.refl _

theorem getD_map_range {α : Type} (d : α) (g : Nat → α) (N i : Nat) (hi : i < N) :
    ((List.range N).map g).getD i d = g i := by
  change ((List.range.loop N []).map g).getD i d = g i
  exact list_range_loop_map_getD_lt d g N [] i hi

theorem list_mem_of_all {α : Type} (p : α → Bool) :
    ∀ (xs : List α), xs.all p = true → ∀ x, x ∈ xs → p x = true
  | [], _, _, h => nomatch h
  | a :: xs, hall, x, hmem => by
    have hcons : (p a && xs.all p) = true := hall
    cases hpa : p a
    · rw [hpa] at hcons; cases hcons
    · rw [hpa] at hcons
      cases hmem with
      | head => exact hpa
      | tail _ htail => exact list_mem_of_all p xs hcons x htail

theorem mem_list_range {i : Nat} : ∀ {n : Nat}, i < n → i ∈ List.range n
  | 0, hi => absurd hi (Nat.not_lt_zero i)
  | m + 1, hi => by
    rw [list_range_succ]
    cases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ hi) with
    | inl hlt => exact List.mem_append_left [m] (mem_list_range hlt)
    | inr heq => rw [heq]; exact List.mem_append_right (List.range m) List.mem_cons_self

-- -------------------------------------------------------------------------------
-- Formal Power Series Ring (`FPS := Nat → Int`)
-- -------------------------------------------------------------------------------

def FPS : Type := Nat → Int

def FPSEq (f g : FPS) : Prop := ∀ n : Nat, f n = g n

theorem FPSEq.refl (f : FPS) : FPSEq f f := fun _ => Eq.refl _

theorem FPSEq.symm {f g : FPS} (h : FPSEq f g) : FPSEq g f := fun n => (h n).symm

theorem FPSEq.trans {f g h : FPS} (h₁ : FPSEq f g) (h₂ : FPSEq g h) : FPSEq f h :=
  fun n => (h₁ n).trans (h₂ n)

def sumRange : Nat → (Nat → Int) → Int
  | 0, _ => 0
  | n + 1, g => sumRange n g + g n

theorem sumRange_congr {n : Nat} {f g : Nat → Int}
    (h : ∀ k, k < n → f k = g k) : sumRange n f = sumRange n g := by
  induction n with
  | zero => exact Eq.refl _
  | succ m ihm =>
    have hm : sumRange m f = sumRange m g :=
      ihm (fun k hk => h k (Nat.lt_succ_of_lt hk))
    have hlast : f m = g m := h m (Nat.lt_succ_self m)
    change sumRange m f + f m = sumRange m g + g m
    rw [hm, hlast]

theorem sumRange_add (n : Nat) (f g : Nat → Int) :
    sumRange n (fun k => f k + g k) = sumRange n f + sumRange n g := by
  induction n with
  | zero => exact Eq.refl _
  | succ m ihm =>
    change (sumRange m (fun k => f k + g k) + (f m + g m)) =
      (sumRange m f + f m) + (sumRange m g + g m)
    rw [ihm, Int.add_assoc, int_add_comm_left (sumRange m g) (f m) (g m), ← Int.add_assoc]

theorem sumRange_neg (n : Nat) (f : Nat → Int) :
    sumRange n (fun k => -f k) = -sumRange n f := by
  induction n with
  | zero => exact Eq.refl _
  | succ m ihm =>
    change sumRange m (fun k => -f k) + (-f m) = -(sumRange m f + f m)
    rw [ihm, Int.neg_add]

theorem sumRange_sub (n : Nat) (f g : Nat → Int) :
    sumRange n (fun k => f k - g k) = sumRange n f - sumRange n g := by
  have h1 : sumRange n (fun k => f k - g k) = sumRange n (fun k => f k + -g k) :=
    sumRange_congr (fun k _ => Int.sub_eq_add_neg)
  rw [h1, sumRange_add, sumRange_neg, ← Int.sub_eq_add_neg]

theorem sumRange_mul_left (c : Int) (n : Nat) (g : Nat → Int) :
    c * sumRange n g = sumRange n (fun k => c * g k) := by
  induction n with
  | zero => exact Int.mul_zero c
  | succ m ihm =>
    change c * (sumRange m g + g m) = sumRange m (fun k => c * g k) + c * g m
    rw [Int.mul_add, ihm]

theorem sumRange_mul_right (c : Int) (n : Nat) (g : Nat → Int) :
    sumRange n g * c = sumRange n (fun k => g k * c) := by
  induction n with
  | zero => exact Int.zero_mul c
  | succ m ihm =>
    change (sumRange m g + g m) * c = sumRange m (fun k => g k * c) + g m * c
    rw [Int.add_mul, ihm]

theorem sumRange_zero_of {n : Nat} {g : Nat → Int}
    (h : ∀ k, k < n → g k = 0) : sumRange n g = 0 := by
  induction n with
  | zero => exact Eq.refl _
  | succ m ihm =>
    have hm : sumRange m g = 0 := ihm (fun k hk => h k (Nat.lt_succ_of_lt hk))
    have hlast : g m = 0 := h m (Nat.lt_succ_self m)
    change sumRange m g + g m = 0
    rw [hm, hlast, Int.add_zero]

theorem sumRange_succ_shift (n : Nat) (g : Nat → Int) :
    sumRange (n + 1) g = g 0 + sumRange n (fun k => g (k + 1)) := by
  induction n with
  | zero =>
    change (0 + g 0) = g 0 + 0
    rw [Int.zero_add, Int.add_zero]
  | succ m ihm =>
    change sumRange (m + 1) g + g (m + 1) =
      g 0 + (sumRange m (fun k => g (k + 1)) + g (m + 1))
    rw [ihm, Int.add_assoc]

theorem sumRange_rev (n : Nat) (g : Nat → Int) :
    sumRange (n + 1) (fun j => g (n - j)) = sumRange (n + 1) g := by
  induction n generalizing g with
  | zero => exact Eq.refl _
  | succ m ihm =>
    change sumRange (m + 1) (fun j => g (m + 1 - j)) + g (m + 1 - (m + 1)) =
      sumRange (m + 2) g
    have hsub0 : g (m + 1 - (m + 1)) = g 0 := by rw [Nat.sub_self]
    have hcongr : sumRange (m + 1) (fun j => g (m + 1 - j)) =
        sumRange (m + 1) (fun j => g ((m - j) + 1)) := by
      apply sumRange_congr
      intro j hj
      rw [Nat.succ_sub (Nat.le_of_lt_succ hj)]
    rw [hsub0, hcongr, ihm (fun t => g (t + 1)), Int.add_comm, ← sumRange_succ_shift]

theorem sumRange_triangle (n : Nat) (F : Nat → Nat → Int) :
    sumRange (n + 1) (fun m => sumRange (m + 1) (fun i => F m i)) =
    sumRange (n + 1) (fun i => sumRange (n - i + 1) (fun j => F (i + j) i)) := by
  induction n with
  | zero =>
    change 0 + (0 + F 0 0) = 0 + (0 + F 0 0)
    exact Eq.refl _
  | succ k ihk =>
    change sumRange (k + 1) (fun m => sumRange (m + 1) (fun i => F m i)) +
        sumRange (k + 2) (fun i => F (k + 1) i) =
      sumRange (k + 2) (fun i => sumRange (k + 1 - i + 1) (fun j => F (i + j) i))
    rw [ihk]
    have hsplit : sumRange (k + 2) (fun i => F (k + 1) i) =
        sumRange (k + 1) (fun i => F (k + 1) i) + F (k + 1) (k + 1) := Eq.refl _
    rw [hsplit, ← Int.add_assoc, ← sumRange_add]
    have hmain : sumRange (k + 1) (fun i =>
        sumRange (k - i + 1) (fun j => F (i + j) i) + F (k + 1) i) =
        sumRange (k + 1) (fun i => sumRange (k + 1 - i + 1) (fun j => F (i + j) i)) := by
      apply sumRange_congr
      intro i hi
      have hle : i ≤ k := Nat.le_of_lt_succ hi
      have hsub : k + 1 - i = (k - i) + 1 := Nat.succ_sub hle
      have hidx : i + (k - i + 1) = k + 1 := by
        rw [← Nat.add_assoc, Nat.add_sub_of_le hle]
      rw [hsub]
      change sumRange (k - i + 1) (fun j => F (i + j) i) + F (k + 1) i =
        sumRange (k - i + 1) (fun j => F (i + j) i) + F (i + (k - i + 1)) i
      rw [hidx]
    have hcorner : F (k + 1) (k + 1) =
        sumRange (k + 1 - (k + 1) + 1) (fun j => F ((k + 1) + j) (k + 1)) := by
      rw [Nat.sub_self]
      change F (k + 1) (k + 1) = 0 + F (k + 1 + 0) (k + 1)
      rw [Int.zero_add, Nat.add_zero]
    rw [hmain, hcorner]
    exact Eq.refl _

theorem sumRange_add_right (a b : Nat) (F : Nat → Int) :
    sumRange (a + b) F = sumRange a F + sumRange b (fun r => F (a + r)) := by
  induction b with
  | zero =>
    change sumRange a F = sumRange a F + 0
    rw [Int.add_zero]
  | succ b ih =>
    change sumRange ((a + b) + 1) F = sumRange a F + (sumRange b (fun r => F (a + r)) + F (a + b))
    change sumRange (a + b) F + F (a + b) = _
    rw [ih, Int.add_assoc]

theorem sumRange_split_at (n k : Nat) (hk : k ≤ n) (g : Nat → Int) :
    sumRange (n + 1) g = sumRange k g + g k + sumRange (n - k) (fun r => g (k + 1 + r)) := by
  have hn : n + 1 = (k + 1) + (n - k) := by
    rw [Nat.add_comm k 1, Nat.add_assoc, Nat.add_sub_of_le hk, Nat.add_comm 1 n]
  rw [hn, sumRange_add_right (k + 1) (n - k) g]
  exact Eq.refl _

theorem foldl_range_sumRange (n : Nat) (g : Nat → Int) :
    (List.range n).foldl (fun acc k => acc + g k) 0 = sumRange n g := by
  induction n with
  | zero => exact Eq.refl _
  | succ m ihm =>
    rw [list_range_succ, my_foldl_append]
    change (List.range m).foldl (fun acc k => acc + g k) 0 + g m = sumRange m g + g m
    rw [ihm]

def fpsOne : FPS := fun n => if n == 0 then 1 else 0
def fpsZero : FPS := fun _ => 0
def fpsAdd (f g : FPS) : FPS := fun n => f n + g n
def fpsNeg (f : FPS) : FPS := fun n => -f n
def fpsSub (f g : FPS) : FPS := fun n => f n - g n
def fpsMul (f g : FPS) : FPS :=
  fun n => sumRange (n + 1) (fun k => f k * g (n - k))

theorem fpsAdd_congr {f₁ f₂ g₁ g₂ : FPS} (hf : FPSEq f₁ f₂) (hg : FPSEq g₁ g₂) :
    FPSEq (fpsAdd f₁ g₁) (fpsAdd f₂ g₂) :=
  fun n => by dsimp [fpsAdd]; rw [hf n, hg n]

theorem fpsNeg_congr {f g : FPS} (h : FPSEq f g) : FPSEq (fpsNeg f) (fpsNeg g) :=
  fun n => by dsimp [fpsNeg]; rw [h n]

theorem fpsSub_congr {f₁ f₂ g₁ g₂ : FPS} (hf : FPSEq f₁ f₂) (hg : FPSEq g₁ g₂) :
    FPSEq (fpsSub f₁ g₁) (fpsSub f₂ g₂) :=
  fun n => by dsimp [fpsSub]; rw [hf n, hg n]

theorem fpsAdd_comm (f g : FPS) : FPSEq (fpsAdd f g) (fpsAdd g f) :=
  fun n => Int.add_comm (f n) (g n)

theorem fpsAdd_assoc (f g h : FPS) :
    FPSEq (fpsAdd (fpsAdd f g) h) (fpsAdd f (fpsAdd g h)) :=
  fun n => Int.add_assoc (f n) (g n) (h n)

theorem fpsAdd_zero_left (f : FPS) : FPSEq (fpsAdd fpsZero f) f :=
  fun n => Int.zero_add (f n)

theorem fpsAdd_zero_right (f : FPS) : FPSEq (fpsAdd f fpsZero) f :=
  fun n => Int.add_zero (f n)

theorem fpsAdd_neg_right (f : FPS) : FPSEq (fpsAdd f (fpsNeg f)) fpsZero :=
  fun n => Int.add_right_neg (f n)

theorem fpsNeg_neg (f : FPS) : FPSEq (fpsNeg (fpsNeg f)) f :=
  fun n => Int.neg_neg (f n)

theorem fpsSub_eq_add_neg (f g : FPS) : FPSEq (fpsSub f g) (fpsAdd f (fpsNeg g)) :=
  fun _ => Int.sub_eq_add_neg

theorem fpsMul_congr {f₁ f₂ g₁ g₂ : FPS} (hf : FPSEq f₁ f₂) (hg : FPSEq g₁ g₂) :
    FPSEq (fpsMul f₁ g₁) (fpsMul f₂ g₂) := by
  intro n
  apply sumRange_congr
  intro k _
  rw [hf k, hg (n - k)]

theorem fpsMul_comm (f g : FPS) : FPSEq (fpsMul f g) (fpsMul g f) := by
  intro n
  change sumRange (n + 1) (fun k => f k * g (n - k)) =
    sumRange (n + 1) (fun k => g k * f (n - k))
  rw [← sumRange_rev n (fun k => g k * f (n - k))]
  apply sumRange_congr
  intro k hk
  have hle : k ≤ n := Nat.le_of_lt_succ hk
  rw [Nat.sub_sub_self hle, Int.mul_comm]

theorem fpsMul_assoc (f g h : FPS) :
    FPSEq (fpsMul (fpsMul f g) h) (fpsMul f (fpsMul g h)) := by
  intro n
  change sumRange (n + 1) (fun m => sumRange (m + 1) (fun i => f i * g (m - i)) * h (n - m)) =
    sumRange (n + 1) (fun i => f i * sumRange (n - i + 1) (fun j => g j * h (n - i - j)))
  have hL : sumRange (n + 1) (fun m => sumRange (m + 1) (fun i => f i * g (m - i)) * h (n - m)) =
      sumRange (n + 1) (fun m => sumRange (m + 1) (fun i => f i * g (m - i) * h (n - m))) :=
    sumRange_congr (fun m _ => sumRange_mul_right _ _ _)
  rw [hL, sumRange_triangle]
  apply sumRange_congr
  intro i _
  rw [sumRange_mul_left]
  apply sumRange_congr
  intro j _
  rw [Nat.add_sub_cancel_left, ← Nat.sub_sub, Int.mul_assoc]

theorem fpsMul_one_left (f : FPS) : FPSEq (fpsMul fpsOne f) f := by
  intro n
  change sumRange (n + 1) (fun k => fpsOne k * f (n - k)) = f n
  rw [sumRange_succ_shift]
  have h0 : fpsOne 0 * f (n - 0) = f n := by
    change 1 * f (n - 0) = f n
    rw [Int.one_mul, Nat.sub_zero]
  have hrest : sumRange n (fun k => fpsOne (k + 1) * f (n - (k + 1))) = 0 := by
    apply sumRange_zero_of
    intro k _
    have hne : (k + 1 == 0) = false := nat_beq_false_of_ne (Nat.succ_ne_zero k)
    change (if (k + 1 == 0) = true then (1 : Int) else 0) * f (n - (k + 1)) = 0
    rw [bool_cond_false hne, Int.zero_mul]
  rw [h0, hrest, Int.add_zero]

theorem fpsMul_one_right (f : FPS) : FPSEq (fpsMul f fpsOne) f :=
  FPSEq.trans (fpsMul_comm f fpsOne) (fpsMul_one_left f)

theorem fpsMul_zero_left (f : FPS) : FPSEq (fpsMul fpsZero f) fpsZero := by
  intro n
  apply sumRange_zero_of
  intro k _
  exact Int.zero_mul (f (n - k))

theorem fpsMul_zero_right (f : FPS) : FPSEq (fpsMul f fpsZero) fpsZero :=
  FPSEq.trans (fpsMul_comm f fpsZero) (fpsMul_zero_left f)

theorem fpsMul_add_left (f g h : FPS) :
    FPSEq (fpsMul (fpsAdd f g) h) (fpsAdd (fpsMul f h) (fpsMul g h)) := by
  intro n
  change sumRange (n + 1) (fun k => (f k + g k) * h (n - k)) =
    sumRange (n + 1) (fun k => f k * h (n - k)) + sumRange (n + 1) (fun k => g k * h (n - k))
  rw [sumRange_congr (fun k _ => Int.add_mul (f k) (g k) (h (n - k))), sumRange_add]

theorem fpsMul_add_right (f g h : FPS) :
    FPSEq (fpsMul f (fpsAdd g h)) (fpsAdd (fpsMul f g) (fpsMul f h)) :=
  FPSEq.trans (fpsMul_comm f (fpsAdd g h))
    (FPSEq.trans (fpsMul_add_left g h f) (fpsAdd_congr (fpsMul_comm g f) (fpsMul_comm h f)))

theorem fpsMul_neg_left (f g : FPS) :
    FPSEq (fpsMul (fpsNeg f) g) (fpsNeg (fpsMul f g)) := by
  intro n
  change sumRange (n + 1) (fun k => (-f k) * g (n - k)) =
    -sumRange (n + 1) (fun k => f k * g (n - k))
  rw [sumRange_congr (fun k _ => Int.neg_mul (f k) (g (n - k))), sumRange_neg]

theorem fpsMul_neg_right (f g : FPS) :
    FPSEq (fpsMul f (fpsNeg g)) (fpsNeg (fpsMul f g)) :=
  FPSEq.trans (fpsMul_comm f (fpsNeg g))
    (FPSEq.trans (fpsMul_neg_left g f) (fpsNeg_congr (fpsMul_comm g f)))

theorem fpsMul_sub_left (f g h : FPS) :
    FPSEq (fpsMul (fpsSub f g) h) (fpsSub (fpsMul f h) (fpsMul g h)) := by
  intro n
  change sumRange (n + 1) (fun k => (f k - g k) * h (n - k)) =
    sumRange (n + 1) (fun k => f k * h (n - k)) - sumRange (n + 1) (fun k => g k * h (n - k))
  rw [sumRange_congr (fun k _ => Int.sub_mul (f k) (g k) (h (n - k))), sumRange_sub]

theorem fpsMul_sub_right (f g h : FPS) :
    FPSEq (fpsMul f (fpsSub g h)) (fpsSub (fpsMul f g) (fpsMul f h)) :=
  FPSEq.trans (fpsMul_comm f (fpsSub g h))
    (FPSEq.trans (fpsMul_sub_left g h f) (fpsSub_congr (fpsMul_comm g f) (fpsMul_comm h f)))

def fpsInvPrefix (f : FPS) : Nat → List Int
  | 0 => []
  | m + 1 =>
    if m == 0 then [1]
    else
      let acc := fpsInvPrefix f m
      let s := sumRange m (fun j => f (m - j) * acc.getD j 0)
      acc ++ [-s]

theorem fpsInvPrefix_length (f : FPS) : ∀ m : Nat, (fpsInvPrefix f m).length = m
  | 0 => Eq.refl _
  | 1 => Eq.refl _
  | k + 2 => by
    change (fpsInvPrefix f (k + 1) ++
      [-sumRange (k + 1) (fun j => f (k + 1 - j) * (fpsInvPrefix f (k + 1)).getD j 0)]).length = k + 2
    rw [List.length_append, List.length_singleton, fpsInvPrefix_length f (k + 1)]

theorem fpsInvPrefix_step_getD_lt (f : FPS) (m j : Nat) (hj : j < m) :
    (fpsInvPrefix f (m + 1)).getD j 0 = (fpsInvPrefix f m).getD j 0 := by
  cases m with
  | zero => exact absurd hj (Nat.not_lt_zero j)
  | succ k =>
    change (fpsInvPrefix f (k + 1) ++
      [-sumRange (k + 1) (fun j => f (k + 1 - j) * (fpsInvPrefix f (k + 1)).getD j 0)]).getD j 0 =
      (fpsInvPrefix f (k + 1)).getD j 0
    exact list_getD_append_left 0 (fpsInvPrefix f (k + 1)) _ j
      (by rw [fpsInvPrefix_length f (k + 1)]; exact hj)

theorem fpsInvPrefix_getD_le (f : FPS) :
    ∀ (m j : Nat), j < m → (fpsInvPrefix f m).getD j 0 = (fpsInvPrefix f (j + 1)).getD j 0
  | 0, j, hj => absurd hj (Nat.not_lt_zero j)
  | m + 1, j, hj => by
    cases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ hj) with
    | inl hlt =>
      rw [fpsInvPrefix_step_getD_lt f m j hlt]
      exact fpsInvPrefix_getD_le f m j hlt
    | inr heq => rw [heq]

def fpsInv (f : FPS) (n : Nat) : Int :=
  (fpsInvPrefix f (n + 1)).getD n 0

theorem fpsInv_zero (f : FPS) : fpsInv f 0 = 1 := Eq.refl _

theorem fpsInv_succ (f : FPS) (n : Nat) :
    fpsInv f (n + 1) = - sumRange (n + 1) (fun j => f (n + 1 - j) * fpsInv f j) := by
  change (fpsInvPrefix f (n + 1) ++
    [-sumRange (n + 1) (fun j => f (n + 1 - j) * (fpsInvPrefix f (n + 1)).getD j 0)]).getD (n + 1) 0 =
    - sumRange (n + 1) (fun j => f (n + 1 - j) * fpsInv f j)
  rw [list_getD_append_right 0 (fpsInvPrefix f (n + 1)) _ (n + 1)
        (by rw [fpsInvPrefix_length f (n + 1)]; exact Nat.le_refl (n + 1)),
      fpsInvPrefix_length f (n + 1), Nat.sub_self, list_getD_cons_zero]
  apply congrArg Neg.neg
  apply sumRange_congr
  intro j hj
  rw [fpsInvPrefix_getD_le f (n + 1) j hj]
  exact Eq.refl _

theorem fpsMul_inv_left (f : FPS) (hf0 : f 0 = 1) :
    FPSEq (fpsMul (fpsInv f) f) fpsOne := by
  intro n
  cases n with
  | zero =>
    change (0 + fpsInv f 0 * f 0) = 1
    rw [fpsInv_zero, hf0]
    exact Eq.refl _
  | succ m =>
    change sumRange (m + 2) (fun k => fpsInv f k * f (m + 1 - k)) = 0
    have hsplit : sumRange (m + 2) (fun k => fpsInv f k * f (m + 1 - k)) =
        sumRange (m + 1) (fun k => fpsInv f k * f (m + 1 - k)) +
        fpsInv f (m + 1) * f (m + 1 - (m + 1)) := Eq.refl _
    rw [hsplit, Nat.sub_self, hf0, Int.mul_one, fpsInv_succ]
    have hcongr : sumRange (m + 1) (fun k => fpsInv f k * f (m + 1 - k)) =
        sumRange (m + 1) (fun k => f (m + 1 - k) * fpsInv f k) := by
      apply sumRange_congr
      intro k _
      exact Int.mul_comm _ _
    rw [hcongr, Int.add_right_neg]

theorem fpsMul_inv_right (f : FPS) (hf0 : f 0 = 1) :
    FPSEq (fpsMul f (fpsInv f)) fpsOne :=
  FPSEq.trans (fpsMul_comm f (fpsInv f)) (fpsMul_inv_left f hf0)

theorem fpsInv_unique (f g : FPS) (hf0 : f 0 = 1) (hg : FPSEq (fpsMul f g) fpsOne) :
    FPSEq g (fpsInv f) := by
  have h1 : FPSEq g (fpsMul fpsOne g) := (fpsMul_one_left g).symm
  have h2 : FPSEq (fpsMul fpsOne g) (fpsMul (fpsMul (fpsInv f) f) g) :=
    fpsMul_congr (fpsMul_inv_left f hf0).symm (FPSEq.refl g)
  have h3 : FPSEq (fpsMul (fpsMul (fpsInv f) f) g) (fpsMul (fpsInv f) (fpsMul f g)) :=
    fpsMul_assoc (fpsInv f) f g
  have h4 : FPSEq (fpsMul (fpsInv f) (fpsMul f g)) (fpsMul (fpsInv f) fpsOne) :=
    fpsMul_congr (FPSEq.refl (fpsInv f)) hg
  have h5 : FPSEq (fpsMul (fpsInv f) fpsOne) (fpsInv f) :=
    fpsMul_one_right (fpsInv f)
  exact FPSEq.trans h1 (FPSEq.trans h2 (FPSEq.trans h3 (FPSEq.trans h4 h5)))

theorem fpsInv_inv (f : FPS) (hf0 : f 0 = 1) : FPSEq (fpsInv (fpsInv f)) f := by
  have h := fpsInv_unique (fpsInv f) f (fpsInv_zero f) (fpsMul_inv_left f hf0)
  exact h.symm

theorem fpsInv_congr {f g : FPS} (hf0 : f 0 = 1) (h : FPSEq f g) :
    FPSEq (fpsInv f) (fpsInv g) := by
  have hg0 : g 0 = 1 := (h 0).symm.trans hf0
  have hmul : FPSEq (fpsMul g (fpsInv f)) fpsOne :=
    FPSEq.trans (fpsMul_congr h.symm (FPSEq.refl (fpsInv f))) (fpsMul_inv_right f hf0)
  exact fpsInv_unique g (fpsInv f) hg0 hmul

theorem fpsMul_eq_on_le {N : Nat} {f₁ f₂ g₁ g₂ : FPS}
    (hf : ∀ j, j ≤ N → f₁ j = f₂ j) (hg : ∀ j, j ≤ N → g₁ j = g₂ j) :
    ∀ j, j ≤ N → fpsMul f₁ g₁ j = fpsMul f₂ g₂ j := by
  intro j hj
  apply sumRange_congr
  intro k hk
  have hkj : k ≤ j := Nat.le_of_lt_succ hk
  have hkN : k ≤ N := Nat.le_trans hkj hj
  have hjkN : j - k ≤ N := Nat.le_trans (Nat.sub_le j k) hj
  rw [hf k hkN, hg (j - k) hjkN]

theorem fpsInv_eq_on_le {N : Nat} {f₁ f₂ : FPS}
    (hf : ∀ j, j ≤ N → f₁ j = f₂ j) :
    ∀ j, j ≤ N → fpsInv f₁ j = fpsInv f₂ j := by
  intro j
  refine nat_strong_ind (P := fun m => m ≤ N → fpsInv f₁ m = fpsInv f₂ m) ?_ j
  intro m ih hmN
  cases m with
  | zero => exact Eq.refl 1
  | succ k =>
    rw [fpsInv_succ f₁ k, fpsInv_succ f₂ k]
    apply congrArg Neg.neg
    apply sumRange_congr
    intro r hr
    have hrk : r ≤ k := Nat.le_of_lt_succ hr
    have hrm : r < k + 1 := hr
    have hrN : r ≤ N := Nat.le_trans (Nat.le_of_lt hrm) hmN
    have hsubN : k + 1 - r ≤ N := Nat.le_trans (Nat.sub_le (k + 1) r) hmN
    rw [hf (k + 1 - r) hsubN, ih r hrm hrN]

theorem fpsInv_unique_lt (N : Nat) (f g : FPS) (hf0 : f 0 = 1)
    (hg : ∀ n, n < N → fpsMul f g n = fpsOne n) :
    ∀ n, n < N → g n = fpsInv f n := by
  intro n hn
  have h1 : g n = fpsMul fpsOne g n := (fpsMul_one_left g n).symm
  have h2 : fpsMul fpsOne g n = fpsMul (fpsMul (fpsInv f) f) g n :=
    fpsMul_congr (fpsMul_inv_left f hf0).symm (FPSEq.refl g) n
  have h3 : fpsMul (fpsMul (fpsInv f) f) g n = fpsMul (fpsInv f) (fpsMul f g) n :=
    fpsMul_assoc (fpsInv f) f g n
  have h4 : fpsMul (fpsInv f) (fpsMul f g) n = fpsMul (fpsInv f) fpsOne n :=
    fpsMul_eq_on_le (N := n) (fun j _ => Eq.refl _)
      (fun j hj => hg j (Nat.lt_of_le_of_lt hj hn)) n (Nat.le_refl n)
  have h5 : fpsMul (fpsInv f) fpsOne n = fpsInv f n := fpsMul_one_right (fpsInv f) n
  exact h1.trans (h2.trans (h3.trans (h4.trans h5)))

def fpsPowNat (f : FPS) : Nat → FPS
  | 0 => fpsOne
  | e + 1 => fpsMul (fpsPowNat f e) f

theorem fpsPowNat_congr {f g : FPS} (h : FPSEq f g) :
    ∀ e : Nat, FPSEq (fpsPowNat f e) (fpsPowNat g e)
  | 0 => FPSEq.refl fpsOne
  | e + 1 => fpsMul_congr (fpsPowNat_congr h e) h

theorem fpsPowNat_add (f : FPS) (a : Nat) :
    ∀ b : Nat, FPSEq (fpsPowNat f (a + b)) (fpsMul (fpsPowNat f a) (fpsPowNat f b))
  | 0 => (fpsMul_one_right (fpsPowNat f a)).symm
  | b + 1 => by
    change FPSEq (fpsMul (fpsPowNat f (a + b)) f)
      (fpsMul (fpsPowNat f a) (fpsMul (fpsPowNat f b) f))
    exact FPSEq.trans (fpsMul_congr (fpsPowNat_add f a b) (FPSEq.refl f))
      (fpsMul_assoc (fpsPowNat f a) (fpsPowNat f b) f)

theorem fpsPowNat_mul_two (f : FPS) :
    ∀ q : Nat, FPSEq (fpsPowNat f (q + q)) (fpsPowNat (fpsMul f f) q)
  | 0 => FPSEq.refl fpsOne
  | q + 1 => by
    have hidx : (q + 1) + (q + 1) = (q + q) + 2 := by
      rw [← Nat.add_assoc (q + 1) q 1, Nat.add_assoc q 1 q, Nat.add_comm 1 q,
          ← Nat.add_assoc q q 1, Nat.add_assoc (q + q) 1 1]
    rw [hidx]
    change FPSEq (fpsMul (fpsMul (fpsPowNat f (q + q)) f) f)
      (fpsMul (fpsPowNat (fpsMul f f) q) (fpsMul f f))
    exact FPSEq.trans (fpsMul_assoc (fpsPowNat f (q + q)) f f)
      (fpsMul_congr (fpsPowNat_mul_two f q) (FPSEq.refl (fpsMul f f)))

def fpsPowInt (f : FPS) (e : Int) : FPS :=
  if e ≥ 0 then fpsPowNat f e.toNat
  else fpsPowNat (fpsInv f) (-e).toNat

theorem fpsPowInt_congr {f g : FPS} (hf0 : f 0 = 1) (h : FPSEq f g) (e : Int) :
    FPSEq (fpsPowInt f e) (fpsPowInt g e) := by
  dsimp [fpsPowInt]
  by_cases he : e ≥ 0
  · rw [if_pos he, if_pos he]
    exact fpsPowNat_congr h e.toNat
  · rw [if_neg he, if_neg he]
    exact fpsPowNat_congr (fpsInv_congr hf0 h) (-e).toNat

-- -------------------------------------------------------------------------------
-- Memoized Truncated Polynomials & Eta-Quotients (`List Int`)
-- -------------------------------------------------------------------------------

structure EtaQuot where
  factors : List (Nat × Int)
  deriving Repr, DecidableEq

def ratNorm (num : Int) (den : Nat) : Int × Nat :=
  if den == 0 then (0, 1)
  else
    let g := Nat.gcd num.natAbs den
    if g == 0 then (0, 1) else (num / (g : Int), den / g)

def ratSub (a b : Int × Nat) : Int × Nat :=
  ratNorm (a.1 * (b.2 : Int) - b.1 * (a.2 : Int)) (a.2 * b.2)

def ratAdd (a b : Int × Nat) : Int × Nat :=
  ratNorm (a.1 * (b.2 : Int) + b.1 * (a.2 : Int)) (a.2 * b.2)

def ratMul (a b : Int × Nat) : Int × Nat :=
  ratNorm (a.1 * b.1) (a.2 * b.2)

def cEffCusp0 (eq : EtaQuot) : Int × Nat :=
  eq.factors.foldl (fun acc dr => ratAdd acc (-dr.2, dr.1)) (0, 1)

def modularWeight (eq : EtaQuot) : Int × Nat :=
  let s := eq.factors.foldl (fun acc dr => acc + dr.2) 0
  ratNorm s 2

def groundStateShift (eq : EtaQuot) : Int × Nat :=
  let s := eq.factors.foldl (fun acc dr => acc + (dr.1 : Int) * dr.2) 0
  ratNorm (-s) 24

def weight2 (eq : EtaQuot) : Int :=
  eq.factors.foldl (fun acc dr => acc + dr.2) 0

def onoSumDR (eq : EtaQuot) : Int :=
  eq.factors.foldl (fun acc dr => acc + (dr.1 : Int) * dr.2) 0

def onoSumNOverDR (eq : EtaQuot) (N : Nat) : Int :=
  eq.factors.foldl (fun acc dr => acc + ((N / dr.1 : Nat) : Int) * dr.2) 0

def onoCong1 (eq : EtaQuot) : Bool :=
  onoSumDR eq % 24 == 0

def onoCong2 (eq : EtaQuot) (N : Nat) : Bool :=
  onoSumNOverDR eq N % 24 == 0

def etaInvert (eq : EtaQuot) : EtaQuot :=
  { factors := eq.factors.map (fun dr => (dr.1, -dr.2)) }

def etaMul (a b : EtaQuot) : EtaQuot :=
  { factors := a.factors ++ b.factors }

def etaDiv (a b : EtaQuot) : EtaQuot :=
  etaMul a (etaInvert b)

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

def baseEtaFPS : FPS := eulerPentCoeff

def dilateFPS (f : FPS) (d : Nat) : FPS :=
  fun n => if d != 0 && n % d == 0 then f (n / d) else 0

def etaFactorFPS (dr : Nat × Int) : FPS :=
  fpsPowInt (dilateFPS baseEtaFPS dr.1) dr.2

def etaFPS (eq : EtaQuot) : FPS :=
  eq.factors.foldl (fun acc dr =>
    if dr.2 == 0 then acc else fpsMul acc (etaFactorFPS dr)) fpsOne

def listToFPS (a : List Int) : FPS :=
  fun i => a.getD i 0

def polyAdd (a b : List Int) (N : Nat) : List Int :=
  (List.range N).map (fun i => a.getD i 0 + b.getD i 0)

def polySub (a b : List Int) (N : Nat) : List Int :=
  (List.range N).map (fun i => a.getD i 0 - b.getD i 0)

def polyNeg (a : List Int) (N : Nat) : List Int :=
  (List.range N).map (fun i => -(a.getD i 0))

def polyScale (c : Int) (a : List Int) (N : Nat) : List Int :=
  (List.range N).map (fun i => c * a.getD i 0)

def polyShift (s : Nat) (a : List Int) (N : Nat) : List Int :=
  (List.range N).map (fun i => if i ≥ s then a.getD (i - s) 0 else 0)

def polyMul (a b : List Int) (N : Nat) : List Int :=
  (List.range N).map fun n =>
    (List.range (n + 1)).foldl (fun acc k =>
      acc + a.getD k 0 * b.getD (n - k) 0) 0

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

def baseEta (N : Nat) : List Int :=
  (List.range N).map eulerPentCoeff

def dilate (a : List Int) (d N : Nat) : List Int :=
  (List.range N).map fun i =>
    if d != 0 && i % d == 0 then a.getD (i / d) 0 else 0

def etaCoeffs (eq : EtaQuot) (N : Nat) : List Int :=
  let base := baseEta N
  let init := if N == 0 then [] else 1 :: List.replicate (N - 1) 0
  eq.factors.foldl (fun acc dr =>
    if dr.2 == 0 then acc
    else polyMul acc (polyPowInt (dilate base dr.1 N) dr.2 N) N) init

def evalLinearEtaStep (N : Nat) (acc : List Int) (t : Int × Nat × List (Nat × Int)) : List Int :=
  let s := etaCoeffs { factors := t.2.2 } N
  let shifted := List.replicate t.2.1 0 ++ s.take (N - t.2.1)
  let scaled := shifted.map (fun v => t.1 * v)
  (List.range N).map (fun i => acc.getD i 0 + scaled.getD i 0)

def evalLinearEta (terms : List (Int × Nat × List (Nat × Int))) (N : Nat) : List Int :=
  terms.foldl (evalLinearEtaStep N) (List.replicate N 0)

def evalLinearEtaFPSStep (acc : FPS) (t : Int × Nat × List (Nat × Int)) : FPS :=
  fun n => acc n + t.1 * (if n ≥ t.2.1 then etaFPS { factors := t.2.2 } (n - t.2.1) else 0)

def evalLinearEtaFPS (terms : List (Int × Nat × List (Nat × Int))) : FPS :=
  terms.foldl evalLinearEtaFPSStep (fun _ => 0)

theorem polyAdd_length (a b : List Int) (N : Nat) : (polyAdd a b N).length = N := by
  dsimp [polyAdd]; rw [List.length_map, list_range_length]

theorem polyAdd_getD (a b : List Int) (f g : FPS) (N i : Nat) (hi : i < N)
    (ha : ∀ k, k < N → a.getD k 0 = f k)
    (hb : ∀ k, k < N → b.getD k 0 = g k) :
    (polyAdd a b N).getD i 0 = fpsAdd f g i := by
  dsimp [polyAdd, fpsAdd]
  rw [getD_map_range 0 _ N i hi, ha i hi, hb i hi]

theorem polySub_length (a b : List Int) (N : Nat) : (polySub a b N).length = N := by
  dsimp [polySub]; rw [List.length_map, list_range_length]

theorem polySub_getD (a b : List Int) (f g : FPS) (N i : Nat) (hi : i < N)
    (ha : ∀ k, k < N → a.getD k 0 = f k)
    (hb : ∀ k, k < N → b.getD k 0 = g k) :
    (polySub a b N).getD i 0 = fpsSub f g i := by
  dsimp [polySub, fpsSub]
  rw [getD_map_range 0 _ N i hi, ha i hi, hb i hi]

theorem polyShift_length (s : Nat) (a : List Int) (N : Nat) : (polyShift s a N).length = N := by
  dsimp [polyShift]; rw [List.length_map, list_range_length]

theorem polyShift_getD (s : Nat) (a : List Int) (f : FPS) (N i : Nat) (hi : i < N)
    (ha : ∀ k, k < N → a.getD k 0 = f k) :
    (polyShift s a N).getD i 0 = (if i ≥ s then f (i - s) else 0) := by
  dsimp [polyShift]
  rw [getD_map_range 0 _ N i hi]
  by_cases h : i ≥ s
  · rw [if_pos h, if_pos h, ha (i - s) (Nat.lt_of_le_of_lt (Nat.sub_le i s) hi)]
  · rw [if_neg h, if_neg h]

theorem polyMul_length (a b : List Int) (N : Nat) : (polyMul a b N).length = N := by
  dsimp [polyMul]
  rw [List.length_map, list_range_length]

theorem polyMul_getD (a b : List Int) (f g : FPS) (N i : Nat) (hi : i < N)
    (ha : ∀ k, k < N → a.getD k 0 = f k)
    (hb : ∀ k, k < N → b.getD k 0 = g k) :
    (polyMul a b N).getD i 0 = fpsMul f g i := by
  dsimp [polyMul]
  rw [getD_map_range 0 _ N i hi, foldl_range_sumRange]
  apply sumRange_congr
  intro k hk
  have hki : k ≤ i := Nat.le_of_lt_succ hk
  have hkN : k < N := Nat.lt_of_le_of_lt hki hi
  have hnikN : i - k < N := Nat.lt_of_le_of_lt (Nat.sub_le i k) hi
  rw [ha k hkN, hb (i - k) hnikN]

theorem listToFPS_eq_on (a : List Int) (N : Nat) :
    ∀ k, k < N → a.getD k 0 = listToFPS a k :=
  fun _ _ => Eq.refl _

theorem oneList_length (N : Nat) :
    (if N == 0 then ([] : List Int) else 1 :: List.replicate (N - 1) 0).length = N := by
  cases N with
  | zero => exact Eq.refl _
  | succ m =>
    change (1 :: List.replicate ((m + 1) - 1) 0).length = m + 1
    rw [Nat.add_sub_cancel, List.length_cons, List.length_replicate]

theorem oneList_getD (N i : Nat) (hi : i < N) :
    (if N == 0 then ([] : List Int) else 1 :: List.replicate (N - 1) 0).getD i 0 = fpsOne i := by
  cases N with
  | zero => exact absurd hi (Nat.not_lt_zero i)
  | succ m =>
    change (1 :: List.replicate ((m + 1) - 1) 0).getD i 0 = fpsOne i
    rw [Nat.add_sub_cancel]
    cases i with
    | zero => exact Eq.refl _
    | succ k =>
      have hk : k < m := Nat.lt_of_succ_lt_succ hi
      have hne : (k + 1 == 0) = false := nat_beq_false_of_ne (Nat.succ_ne_zero k)
      change (List.replicate m 0).getD k 0 = if (k + 1 == 0) = true then (1 : Int) else 0
      rw [list_getD_replicate 0 0 m k hk, bool_cond_false hne]

theorem polyInvAux_spec (a : List Int) (f : FPS) (N : Nat)
    (ha : ∀ k, k < N → a.getD k 0 = f k) :
    ∀ (fuel : Nat) (acc : List Int),
    acc.length + fuel = N → 1 ≤ acc.length →
    (∀ j, j < acc.length → acc.getD j 0 = fpsInv f j) →
    (polyInvAux a fuel acc).length = N ∧
    (∀ j, j < N → (polyInvAux a fuel acc).getD j 0 = fpsInv f j)
  | 0, acc, hlen, _, hacc => by
    rw [Nat.add_zero] at hlen
    rw [hlen] at hacc
    exact ⟨hlen, hacc⟩
  | fuel + 1, acc, hlen, hpos, hacc => by
    have hlt : acc.length < N := by
      have h1 : acc.length + 1 ≤ acc.length + (fuel + 1) :=
        Nat.add_le_add_left (Nat.succ_le_succ (Nat.zero_le fuel)) acc.length
      rw [hlen] at h1
      exact h1
    cases hlen_eq : acc.length with
    | zero => rw [hlen_eq] at hpos; exact absurd hpos (Nat.not_le_of_gt (Nat.zero_lt_one))
    | succ m =>
      let s := (List.range acc.length).foldl (fun sum j =>
        sum + a.getD (acc.length - j) 0 * acc.getD j 0) 0
      have hs_eq : -s = fpsInv f (m + 1) := by
        dsimp [s]
        rw [hlen_eq, foldl_range_sumRange, fpsInv_succ]
        apply congrArg Neg.neg
        apply sumRange_congr
        intro j hj
        have hsub_lt : m + 1 - j < N := by
          have h1 : m + 1 - j ≤ acc.length := by rw [hlen_eq]; exact Nat.sub_le (m + 1) j
          exact Nat.lt_of_le_of_lt h1 hlt
        have hj_acc : j < acc.length := by rw [hlen_eq]; exact hj
        rw [ha (m + 1 - j) hsub_lt, hacc j hj_acc]
      have hlen' : (acc ++ [-s]).length + fuel = N := by
        rw [List.length_append, List.length_singleton, Nat.add_assoc, Nat.add_comm 1 fuel, ← Nat.add_assoc]
        exact hlen
      have hpos' : 1 ≤ (acc ++ [-s]).length := by
        rw [List.length_append, List.length_singleton]
        exact Nat.le_add_left 1 acc.length
      have hacc' : ∀ j, j < (acc ++ [-s]).length → (acc ++ [-s]).getD j 0 = fpsInv f j := by
        intro j hj
        rw [List.length_append, List.length_singleton] at hj
        cases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ hj) with
        | inl hjm =>
          rw [list_getD_append_left 0 acc [-s] j hjm]
          exact hacc j hjm
        | inr heq =>
          rw [heq, list_getD_append_right 0 acc [-s] acc.length (Nat.le_refl acc.length),
              Nat.sub_self, list_getD_cons_zero, hs_eq, hlen_eq]
      exact polyInvAux_spec a f N ha fuel (acc ++ [-s]) hlen' hpos' hacc'

theorem polyInv_length (a : List Int) (N : Nat) : (polyInv a N).length = N := by
  dsimp [polyInv]
  cases N with
  | zero => exact Eq.refl _
  | succ m =>
    have hne : (m + 1 == 0) = false := nat_beq_false_of_ne (Nat.succ_ne_zero m)
    rw [bool_cond_false hne, Nat.add_sub_cancel]
    have hspec := polyInvAux_spec a (listToFPS a) (m + 1) (listToFPS_eq_on a (m + 1)) m [1]
      (by change 1 + m = m + 1; rw [Nat.add_comm])
      (Nat.le_refl 1)
      (fun j hj => by
        cases j with
        | zero => exact Eq.refl _
        | succ k => exact absurd hj (Nat.not_lt_of_ge (Nat.succ_le_succ (Nat.zero_le k))))
    exact hspec.1

theorem polyInv_getD (a : List Int) (f : FPS) (N i : Nat) (hi : i < N)
    (ha : ∀ k, k < N → a.getD k 0 = f k) :
    (polyInv a N).getD i 0 = fpsInv f i := by
  dsimp [polyInv]
  cases N with
  | zero => exact absurd hi (Nat.not_lt_zero i)
  | succ m =>
    have hne : (m + 1 == 0) = false := nat_beq_false_of_ne (Nat.succ_ne_zero m)
    rw [bool_cond_false hne, Nat.add_sub_cancel]
    have hspec := polyInvAux_spec a f (m + 1) ha m [1]
      (by change 1 + m = m + 1; rw [Nat.add_comm])
      (Nat.le_refl 1)
      (fun j hj => by
        cases j with
        | zero => exact Eq.refl _
        | succ k => exact absurd hj (Nat.not_lt_of_ge (Nat.succ_le_succ (Nat.zero_le k))))
    exact hspec.2 i hi

theorem polyPowAux_spec (N : Nat) :
    ∀ (fuel e : Nat) (base acc : List Int) (f g : FPS),
    e ≤ fuel →
    (∀ k, k < N → base.getD k 0 = f k) →
    acc.length = N →
    (∀ k, k < N → acc.getD k 0 = g k) →
    (polyPowAux N fuel e base acc).length = N ∧
    (∀ k, k < N → (polyPowAux N fuel e base acc).getD k 0 = fpsMul g (fpsPowNat f e) k)
  | 0, e, _, acc, f, g, he, _, hlen, hacc => by
    have he0 : e = 0 := Nat.eq_zero_of_le_zero he
    rw [he0]
    refine ⟨hlen, fun k hk => ?_⟩
    change acc.getD k 0 = fpsMul g fpsOne k
    rw [hacc k hk]
    exact (fpsMul_one_right g k).symm
  | fuel + 1, e, base, acc, f, g, he, hbase, hlen, hacc => by
    cases e with
    | zero =>
      refine ⟨hlen, fun k hk => ?_⟩
      change acc.getD k 0 = fpsMul g fpsOne k
      rw [hacc k hk]
      exact (fpsMul_one_right g k).symm
    | succ e' =>
      cases e' with
      | zero =>
        refine ⟨polyMul_length acc base N, fun k hk => ?_⟩
        change (polyMul acc base N).getD k 0 = fpsMul g (fpsPowNat f 1) k
        rw [polyMul_getD acc base g f N k hk hacc hbase]
        have h1 : FPSEq (fpsPowNat f 1) f := fpsMul_one_left f
        exact (fpsMul_congr (FPSEq.refl g) h1 k).symm
      | succ e'' =>
        have he2 : 2 ≤ e'' + 2 := Nat.succ_le_succ (Nat.succ_le_succ (Nat.zero_le e''))
        have hq_lt : (e'' + 2) / 2 < e'' + 2 :=
          Nat.div_lt_self (Nat.lt_of_lt_of_le (by decide : 0 < 2) he2) (by decide : 1 < 2)
        have hq_le : (e'' + 2) / 2 ≤ fuel := Nat.le_of_lt_succ (Nat.lt_of_lt_of_le hq_lt he)
        have hbase2 : ∀ k, k < N → (polyMul base base N).getD k 0 = fpsMul f f k :=
          fun k hk => polyMul_getD base base f f N k hk hbase hbase
        have hdivmod : 2 * ((e'' + 2) / 2) + (e'' + 2) % 2 = e'' + 2 :=
          Nat.div_add_mod (e'' + 2) 2
        have h2mul : 2 * ((e'' + 2) / 2) = (e'' + 2) / 2 + (e'' + 2) / 2 :=
          Nat.two_mul ((e'' + 2) / 2)
        have hunfold : polyPowAux N (fuel + 1) (e'' + 2) base acc =
            polyPowAux N fuel ((e'' + 2) / 2) (polyMul base base N)
              (if (e'' + 2) % 2 == 1 then polyMul acc base N else acc) := Eq.refl _
        rw [hunfold]
        cases hmod : (e'' + 2) % 2 with
        | zero =>
          change (polyPowAux N fuel ((e'' + 2) / 2) (polyMul base base N) acc).length = N ∧
            ∀ k, k < N → (polyPowAux N fuel ((e'' + 2) / 2) (polyMul base base N) acc).getD k 0 =
              fpsMul g (fpsPowNat f (e'' + 2)) k
          have hspec := polyPowAux_spec N fuel ((e'' + 2) / 2) (polyMul base base N) acc
            (fpsMul f f) g hq_le hbase2 hlen hacc
          refine ⟨hspec.1, fun k hk => ?_⟩
          rw [hspec.2 k hk]
          have heq : (e'' + 2) = (e'' + 2) / 2 + (e'' + 2) / 2 := by
            rw [← h2mul, ← Nat.add_zero (2 * ((e'' + 2) / 2)), ← hmod, hdivmod]
          conv => rhs; rw [heq]
          exact (fpsMul_congr (FPSEq.refl g) (fpsPowNat_mul_two f ((e'' + 2) / 2)) k).symm
        | succ r =>
          have hr_lt : (e'' + 2) % 2 < 2 := Nat.mod_lt (e'' + 2) (by decide : 0 < 2)
          rw [hmod] at hr_lt
          have hr0 : r = 0 := Nat.eq_zero_of_le_zero (Nat.le_of_lt_succ (Nat.lt_of_succ_lt_succ hr_lt))
          rw [hr0]
          rw [hr0] at hmod
          change (polyPowAux N fuel ((e'' + 2) / 2) (polyMul base base N) (polyMul acc base N)).length = N ∧
            ∀ k, k < N → (polyPowAux N fuel ((e'' + 2) / 2) (polyMul base base N) (polyMul acc base N)).getD k 0 =
              fpsMul g (fpsPowNat f (e'' + 2)) k
          have hacc' : ∀ k, k < N → (polyMul acc base N).getD k 0 = fpsMul g f k :=
            fun k hk => polyMul_getD acc base g f N k hk hacc hbase
          have hspec := polyPowAux_spec N fuel ((e'' + 2) / 2) (polyMul base base N)
            (polyMul acc base N) (fpsMul f f) (fpsMul g f) hq_le hbase2
            (polyMul_length acc base N) hacc'
          refine ⟨hspec.1, fun k hk => ?_⟩
          rw [hspec.2 k hk]
          have hmod1 : (e'' + 2) % 2 = 1 := hmod
          have heq : (e'' + 2) = ((e'' + 2) / 2 + (e'' + 2) / 2) + 1 := by
            rw [← h2mul, ← hmod1, hdivmod]
          have hpow : FPSEq (fpsMul (fpsMul g f) (fpsPowNat (fpsMul f f) ((e'' + 2) / 2)))
              (fpsMul g (fpsPowNat f (e'' + 2))) := by
            have ha1 := fpsMul_assoc g f (fpsPowNat (fpsMul f f) ((e'' + 2) / 2))
            have ha2 := fpsMul_comm f (fpsPowNat (fpsMul f f) ((e'' + 2) / 2))
            have ha3 := fpsMul_congr (fpsPowNat_mul_two f ((e'' + 2) / 2)).symm (FPSEq.refl f)
            have ha4 : FPSEq (fpsMul (fpsPowNat f ((e'' + 2) / 2 + (e'' + 2) / 2)) f)
                (fpsPowNat f (e'' + 2)) := by
              conv => rhs; rw [heq]
              exact FPSEq.refl _
            exact FPSEq.trans ha1 (fpsMul_congr (FPSEq.refl g) (FPSEq.trans ha2 (FPSEq.trans ha3 ha4)))
          exact hpow k

theorem polyPowNat_length (a : List Int) (e N : Nat) : (polyPowNat a e N).length = N := by
  dsimp [polyPowNat]
  exact (polyPowAux_spec N (e + 1) e a _ (listToFPS a) fpsOne
    (Nat.le_succ e) (listToFPS_eq_on a N) (oneList_length N) (oneList_getD N)).1

theorem polyPowNat_getD (a : List Int) (f : FPS) (e N i : Nat) (hi : i < N)
    (ha : ∀ k, k < N → a.getD k 0 = f k) :
    (polyPowNat a e N).getD i 0 = fpsPowNat f e i := by
  dsimp [polyPowNat]
  have hspec := polyPowAux_spec N (e + 1) e a _ f fpsOne
    (Nat.le_succ e) ha (oneList_length N) (oneList_getD N)
  rw [hspec.2 i hi]
  exact fpsMul_one_left (fpsPowNat f e) i

theorem polyPowInt_length (a : List Int) (e : Int) (N : Nat) : (polyPowInt a e N).length = N := by
  dsimp [polyPowInt]
  by_cases h : e ≥ 0
  · rw [if_pos h]; exact polyPowNat_length a e.toNat N
  · rw [if_neg h]; exact polyPowNat_length (polyInv a N) (-e).toNat N

theorem polyPowInt_getD (a : List Int) (f : FPS) (e : Int) (N i : Nat) (hi : i < N)
    (ha : ∀ k, k < N → a.getD k 0 = f k) :
    (polyPowInt a e N).getD i 0 = fpsPowInt f e i := by
  dsimp [polyPowInt, fpsPowInt]
  by_cases h : e ≥ 0
  · rw [if_pos h, if_pos h]
    exact polyPowNat_getD a f e.toNat N i hi ha
  · rw [if_neg h, if_neg h]
    exact polyPowNat_getD (polyInv a N) (fpsInv f) (-e).toNat N i hi
      (fun k hk => polyInv_getD a f N k hk ha)

theorem dilate_baseEta_getD (d N i : Nat) (hi : i < N) :
    (dilate (baseEta N) d N).getD i 0 = dilateFPS baseEtaFPS d i := by
  dsimp [dilate, baseEta, dilateFPS, baseEtaFPS]
  rw [getD_map_range 0 _ N i hi]
  cases hd : (d != 0 && i % d == 0)
  · exact Eq.refl 0
  · have hdiv : i / d < N := by
      cases d with
      | zero => cases hd
      | succ d' => exact Nat.lt_of_le_of_lt (Nat.div_le_self i (d' + 1)) hi
    exact getD_map_range 0 eulerPentCoeff N (i / d) hdiv

theorem etaCoeffs_spec (eq : EtaQuot) (N : Nat) :
    (etaCoeffs eq N).length = N ∧
    (∀ i, i < N → (etaCoeffs eq N).getD i 0 = etaFPS eq i) := by
  dsimp [etaCoeffs, etaFPS]
  let R : List Int → FPS → Prop := fun xs f =>
    xs.length = N ∧ ∀ i, i < N → xs.getD i 0 = f i
  apply foldl_congr R
  · intro accL accF dr hR
    cases h0 : (dr.2 == 0)
    · change R (polyMul accL (polyPowInt (dilate (baseEta N) dr.1 N) dr.2 N) N)
        (fpsMul accF (etaFactorFPS dr))
      have hpow : ∀ k, k < N → (polyPowInt (dilate (baseEta N) dr.1 N) dr.2 N).getD k 0 =
          etaFactorFPS dr k :=
        fun k hk => polyPowInt_getD (dilate (baseEta N) dr.1 N) (dilateFPS baseEtaFPS dr.1)
          dr.2 N k hk (fun j hj => dilate_baseEta_getD dr.1 N j hj)
      refine ⟨polyMul_length _ _ N, fun i hi => ?_⟩
      exact polyMul_getD _ _ accF (etaFactorFPS dr) N i hi hR.2 hpow
    · change R accL accF
      exact hR
  · exact ⟨oneList_length N, oneList_getD N⟩

theorem etaCoeffs_length (eq : EtaQuot) (N : Nat) : (etaCoeffs eq N).length = N :=
  (etaCoeffs_spec eq N).1

theorem etaCoeffs_getD (eq : EtaQuot) (N i : Nat) (hi : i < N) :
    (etaCoeffs eq N).getD i 0 = etaFPS eq i :=
  (etaCoeffs_spec eq N).2 i hi

theorem replicate_getD_zero (N i : Nat) (hi : i < N) :
    (List.replicate N (0 : Int)).getD i 0 = 0 :=
  list_getD_replicate 0 0 N i hi

theorem evalLinearEtaStep_getD (N : Nat) (accL : List Int) (accF : FPS)
    (t : Int × Nat × List (Nat × Int))
    (hacc : ∀ i, i < N → accL.getD i 0 = accF i) :
    (evalLinearEtaStep N accL t).length = N ∧
    (∀ i, i < N → (evalLinearEtaStep N accL t).getD i 0 = evalLinearEtaFPSStep accF t i) := by
  dsimp [evalLinearEtaStep, evalLinearEtaFPSStep]
  refine ⟨by rw [List.length_map, list_range_length], fun i hi => ?_⟩
  rw [getD_map_range 0 _ N i hi, hacc i hi]
  let s := etaCoeffs { factors := t.2.2 } N
  let shifted := List.replicate t.2.1 (0 : Int) ++ s.take (N - t.2.1)
  have hs_len : s.length = N := etaCoeffs_length { factors := t.2.2 } N
  have hsh_len : i < shifted.length := by
    dsimp [shifted]
    rw [List.length_append, List.length_replicate, List.length_take, hs_len]
    by_cases hle : t.2.1 ≤ N
    · have hmin : min (N - t.2.1) N = N - t.2.1 := Nat.min_eq_left (Nat.sub_le N t.2.1)
      rw [hmin, Nat.add_sub_of_le hle]
      exact hi
    · have hgt : N < t.2.1 := Nat.lt_of_not_le hle
      exact Nat.lt_of_lt_of_le hi (Nat.le_trans (Nat.le_of_lt hgt) (Nat.le_add_right t.2.1 _))
  rw [list_getD_map 0 0 (fun v => t.1 * v) shifted i hsh_len]
  by_cases hge : i ≥ t.2.1
  · rw [if_pos hge]
    have hge_len : (List.replicate t.2.1 (0 : Int)).length ≤ i := by
      rw [List.length_replicate]; exact hge
    dsimp [shifted]
    rw [list_getD_append_right 0 _ _ i hge_len, List.length_replicate]
    have hsub_lt1 : i - t.2.1 < N - t.2.1 := Nat.sub_lt_sub_right hge hi
    have hsub_lt2 : i - t.2.1 < s.length := by
      rw [hs_len]; exact Nat.lt_of_le_of_lt (Nat.sub_le i t.2.1) hi
    rw [list_getD_take 0 (N - t.2.1) s (i - t.2.1) hsub_lt1 hsub_lt2,
        etaCoeffs_getD { factors := t.2.2 } N (i - t.2.1)
          (Nat.lt_of_le_of_lt (Nat.sub_le i t.2.1) hi)]
  · rw [if_neg hge]
    have hlt_len : i < (List.replicate t.2.1 (0 : Int)).length := by
      rw [List.length_replicate]; exact Nat.lt_of_not_le hge
    dsimp [shifted]
    rw [list_getD_append_left 0 _ _ i hlt_len,
        replicate_getD_zero t.2.1 i (Nat.lt_of_not_le hge), Int.mul_zero]

theorem evalLinearEta_getD_eq_FPS (terms : List (Int × Nat × List (Nat × Int))) (N : Nat) :
    ∀ i, i < N → (evalLinearEta terms N).getD i 0 = evalLinearEtaFPS terms i := by
  dsimp [evalLinearEta, evalLinearEtaFPS]
  let R : List Int → FPS → Prop := fun xs f =>
    ∀ i, i < N → xs.getD i 0 = f i
  have hfold : R (terms.foldl (evalLinearEtaStep N) (List.replicate N 0))
      (terms.foldl evalLinearEtaFPSStep (fun _ => 0)) := by
    apply foldl_congr R
    · intro accL accF t hR
      exact (evalLinearEtaStep_getD N accL accF t hR).2
    · exact replicate_getD_zero N
  exact hfold

-- -------------------------------------------------------------------------------
-- Fast Structural Partition Table (`partList : Nat → List Int`)
-- -------------------------------------------------------------------------------

def pentStepGo (n : Nat) (rev : List Int) : Nat → Int → Nat → Int
  | 0, acc, _ => acc
  | fuel + 1, acc, k =>
    let p1 := k * (3 * k - 1) / 2
    if p1 > n then acc
    else
      let sgn : Int := if k % 2 == 1 then 1 else -1
      let t1 := rev.getD (p1 - 1) 0
      let p2 := k * (3 * k + 1) / 2
      let t2 := if p2 ≤ n then rev.getD (p2 - 1) 0 else 0
      pentStepGo n rev fuel (acc + sgn * (t1 + t2)) (k + 1)

def partRevAux : Nat → Nat → List Int → List Int
  | 0, _, rev => rev
  | rem + 1, n, rev =>
    let pn : Int := if n == 0 then 1 else pentStepGo n rev (n + 2) 0 1
    partRevAux rem (n + 1) (pn :: rev)

def partList (N : Nat) : List Int :=
  (partRevAux N 0 []).reverse

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 1: Euler's Partition Theorem (Odd = Distinct) & Pentagonal Recurrence
-- ═══════════════════════════════════════════════════════════════════════════════

def oneSubQPow (k : Nat) : FPS :=
  fun n => if n == 0 then 1 else if k > 0 && n == k then -1 else 0

def oneAddQPow (k : Nat) : FPS :=
  fun n => if n == 0 then 1 else if k > 0 && n == k then 1 else 0

def prodAllMinus : Nat → FPS
  | 0 => fpsOne
  | m + 1 => fpsMul (prodAllMinus m) (oneSubQPow (m + 1))

def prodDistinct : Nat → FPS
  | 0 => fpsOne
  | m + 1 => fpsMul (prodDistinct m) (oneAddQPow (m + 1))

def prodOddMinus : Nat → FPS
  | 0 => fpsOne
  | m + 1 => fpsMul (prodOddMinus m) (oneSubQPow (2 * m + 1))

def prodEvenMinus : Nat → FPS
  | 0 => fpsOne
  | m + 1 => fpsMul (prodEvenMinus m) (oneSubQPow (2 * m + 2))

def polyBinom (c : Int) (k N : Nat) : List Int :=
  (List.range N).map (fun n => if n == 0 then 1 else if k > 0 && n == k then c else 0)

def prodAllMinusList : Nat → Nat → List Int
  | 0, N => if N == 0 then [] else 1 :: List.replicate (N - 1) 0
  | m + 1, N => polyMul (prodAllMinusList m N) (polyBinom (-1) (m + 1) N) N

def prodDistinctList : Nat → Nat → List Int
  | 0, N => if N == 0 then [] else 1 :: List.replicate (N - 1) 0
  | m + 1, N => polyMul (prodDistinctList m N) (polyBinom 1 (m + 1) N) N

def prodOddMinusList : Nat → Nat → List Int
  | 0, N => if N == 0 then [] else 1 :: List.replicate (N - 1) 0
  | m + 1, N => polyMul (prodOddMinusList m N) (polyBinom (-1) (2 * m + 1) N) N

def distinctPartsFPS (n : Nat) : Int := prodDistinct n n
def oddPartsFPS (n : Nat) : Int := fpsInv (prodOddMinus (n + 1)) n
def eulerProductFPS (n : Nat) : Int := prodAllMinus n n
def distinctPartsList (len : Nat) : List Int := (List.range len).map distinctPartsFPS
def oddPartsList (len : Nat) : List Int := (List.range len).map oddPartsFPS

def countOddPartsMinAux : Nat → Nat → Nat → Nat
  | 0, _, _ => 0
  | fuel + 1, n, m =>
    if n == 0 then 1
    else if m == 0 || m > n then 0
    else if m % 2 == 0 then countOddPartsMinAux fuel n (m + 1)
    else countOddPartsMinAux fuel (n - m) m + countOddPartsMinAux fuel n (m + 2)

def countOddPartsMin (n minOdd : Nat) : Nat :=
  countOddPartsMinAux (n + 1) n minOdd

def countDistinctPartsMinAux : Nat → Nat → Nat → Nat
  | 0, _, _ => 0
  | fuel + 1, n, m =>
    if n == 0 then 1
    else if m == 0 || m > n then 0
    else countDistinctPartsMinAux fuel (n - m) (m + 1) + countDistinctPartsMinAux fuel n (m + 1)

def countDistinctPartsMin (n minPart : Nat) : Nat :=
  countDistinctPartsMinAux (n + 1) n minPart

def countEvenPartsMinAux : Nat → Nat → Nat → Nat
  | 0, _, _ => 0
  | fuel + 1, n, m =>
    if n == 0 then 1
    else if m == 0 || m > n then 0
    else if m % 2 == 1 then countEvenPartsMinAux fuel n (m + 1)
    else countEvenPartsMinAux fuel (n - m) m + countEvenPartsMinAux fuel n (m + 2)

def countEvenPartsMin (n minEven : Nat) : Nat :=
  countEvenPartsMinAux (n + 1) n minEven

theorem oneSubQPow_zero (k : Nat) : oneSubQPow k 0 = 1 := Eq.refl _
theorem oneAddQPow_zero (k : Nat) : oneAddQPow k 0 = 1 := Eq.refl _

theorem prodAllMinus_zero : ∀ M : Nat, prodAllMinus M 0 = 1
  | 0 => Eq.refl _
  | m + 1 => by
    change sumRange 1 (fun k => prodAllMinus m k * oneSubQPow (m + 1) (0 - k)) = 1
    change 0 + prodAllMinus m 0 * oneSubQPow (m + 1) 0 = 1
    rw [Int.zero_add, prodAllMinus_zero m, oneSubQPow_zero, Int.mul_one]

theorem prodOddMinus_zero : ∀ M : Nat, prodOddMinus M 0 = 1
  | 0 => Eq.refl _
  | m + 1 => by
    change 0 + prodOddMinus m 0 * oneSubQPow (2 * m + 1) 0 = 1
    rw [Int.zero_add, prodOddMinus_zero m, oneSubQPow_zero, Int.mul_one]

theorem polyBinom_getD (c : Int) (k N i : Nat) (hi : i < N) :
    (polyBinom c k N).getD i 0 = (if i == 0 then 1 else if k > 0 && i == k then c else 0) := by
  dsimp [polyBinom]
  exact getD_map_range 0 _ N i hi

theorem prodAllMinusList_getD : ∀ (M N i : Nat), i < N →
    (prodAllMinusList M N).getD i 0 = prodAllMinus M i
  | 0, N, i, hi => oneList_getD N i hi
  | m + 1, N, i, hi =>
    polyMul_getD (prodAllMinusList m N) (polyBinom (-1) (m + 1) N) (prodAllMinus m) (oneSubQPow (m + 1)) N i hi
      (fun k hk => prodAllMinusList_getD m N k hk)
      (fun k hk => polyBinom_getD (-1) (m + 1) N k hk)

theorem prodDistinctList_getD : ∀ (M N i : Nat), i < N →
    (prodDistinctList M N).getD i 0 = prodDistinct M i
  | 0, N, i, hi => oneList_getD N i hi
  | m + 1, N, i, hi =>
    polyMul_getD (prodDistinctList m N) (polyBinom 1 (m + 1) N) (prodDistinct m) (oneAddQPow (m + 1)) N i hi
      (fun k hk => prodDistinctList_getD m N k hk)
      (fun k hk => polyBinom_getD 1 (m + 1) N k hk)

theorem prodOddMinusList_getD : ∀ (M N i : Nat), i < N →
    (prodOddMinusList M N).getD i 0 = prodOddMinus M i
  | 0, N, i, hi => oneList_getD N i hi
  | m + 1, N, i, hi =>
    polyMul_getD (prodOddMinusList m N) (polyBinom (-1) (2 * m + 1) N) (prodOddMinus m) (oneSubQPow (2 * m + 1)) N i hi
      (fun k hk => prodOddMinusList_getD m N k hk)
      (fun k hk => polyBinom_getD (-1) (2 * m + 1) N k hk)

theorem oneSubQPow_of_pos_ne {k j : Nat} (hj0 : j ≠ 0) (hjk : j ≠ k) :
    oneSubQPow k j = 0 := by
  dsimp [oneSubQPow]
  rw [bool_cond_false (nat_beq_false_of_ne hj0)]
  have hbf : (k > 0 && j == k) = false := by
    change (decide (k > 0) && (j == k)) = false
    rw [nat_beq_false_of_ne hjk]
    cases decide (k > 0) <;> exact Eq.refl _
  rw [bool_cond_false hbf]

theorem oneAddQPow_of_pos_ne {k j : Nat} (hj0 : j ≠ 0) (hjk : j ≠ k) :
    oneAddQPow k j = 0 := by
  dsimp [oneAddQPow]
  rw [bool_cond_false (nat_beq_false_of_ne hj0)]
  have hbf : (k > 0 && j == k) = false := by
    change (decide (k > 0) && (j == k)) = false
    rw [nat_beq_false_of_ne hjk]
    cases decide (k > 0) <;> exact Eq.refl _
  rw [bool_cond_false hbf]

theorem oneSubQPow_at_self {k : Nat} (hk : 0 < k) : oneSubQPow k k = -1 := by
  dsimp [oneSubQPow]
  have hk0 : (k == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt hk)
  have hkpos : decide (k > 0) = true := decide_eq_true hk
  have hks : (k == k) = true := nat_beq_self k
  have hbt : (k > 0 && k == k) = true := by
    change (decide (k > 0) && (k == k)) = true
    rw [hkpos, hks]; exact Eq.refl _
  rw [bool_cond_false hk0, bool_cond_true hbt]

theorem oneAddQPow_at_self {k : Nat} (hk : 0 < k) : oneAddQPow k k = 1 := by
  dsimp [oneAddQPow]
  have hk0 : (k == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt hk)
  have hkpos : decide (k > 0) = true := decide_eq_true hk
  have hks : (k == k) = true := nat_beq_self k
  have hbt : (k > 0 && k == k) = true := by
    change (decide (k > 0) && (k == k)) = true
    rw [hkpos, hks]; exact Eq.refl _
  rw [bool_cond_false hk0, bool_cond_true hbt]

theorem oneSub_mul_oneAdd_eq_two (k : Nat) (hk : 0 < k) :
    FPSEq (fpsMul (oneSubQPow k) (oneAddQPow k)) (oneSubQPow (2 * k)) := by
  intro n
  cases n with
  | zero =>
    change 0 + oneSubQPow k 0 * oneAddQPow k 0 = oneSubQPow (2 * k) 0
    rw [oneSubQPow_zero, oneAddQPow_zero, oneSubQPow_zero, Int.zero_add, Int.mul_one]
  | succ m =>
    by_cases hlt : m + 1 < k
    · have hm1_ne0 : m + 1 ≠ 0 := Nat.succ_ne_zero m
      have hm1_nek : m + 1 ≠ k := Nat.ne_of_lt hlt
      have hm1_ne2k : m + 1 ≠ 2 * k := by
        have hle2 : k ≤ 2 * k := Nat.le_mul_of_pos_left k (by decide : 0 < 2)
        exact Nat.ne_of_lt (Nat.lt_of_lt_of_le hlt hle2)
      change sumRange (m + 2) (fun j => oneSubQPow k j * oneAddQPow k (m + 1 - j)) =
        oneSubQPow (2 * k) (m + 1)
      rw [sumRange_succ_shift (m + 1), oneSubQPow_zero, Nat.sub_zero, Int.one_mul,
          oneAddQPow_of_pos_ne hm1_ne0 hm1_nek]
      have hrest : sumRange (m + 1) (fun j => oneSubQPow k (j + 1) * oneAddQPow k (m + 1 - (j + 1))) = 0 := by
        apply sumRange_zero_of
        intro j hj
        have hjk : j + 1 ≠ k := Nat.ne_of_lt (Nat.lt_of_le_of_lt (Nat.le_of_lt_succ (Nat.succ_lt_succ hj)) hlt)
        rw [oneSubQPow_of_pos_ne (Nat.succ_ne_zero j) hjk, Int.zero_mul]
      rw [hrest, Int.add_zero, oneSubQPow_of_pos_ne hm1_ne0 hm1_ne2k]
    · have hle : k ≤ m + 1 := Nat.le_of_not_lt hlt
      change sumRange (m + 2) (fun j => oneSubQPow k j * oneAddQPow k (m + 1 - j)) =
        oneSubQPow (2 * k) (m + 1)
      rw [sumRange_split_at (m + 1) k hle]
      have hfirst : sumRange k (fun j => oneSubQPow k j * oneAddQPow k (m + 1 - j)) = oneAddQPow k (m + 1) := by
        cases k with
        | zero => exact absurd hk (Nat.not_lt_zero 0)
        | succ k' =>
          rw [sumRange_succ_shift k', oneSubQPow_zero, Nat.sub_zero, Int.one_mul]
          have hzr : sumRange k' (fun j => oneSubQPow (k' + 1) (j + 1) * oneAddQPow (k' + 1) (m + 1 - (j + 1))) = 0 := by
            apply sumRange_zero_of
            intro j hj
            have hjk : j + 1 ≠ k' + 1 := Nat.ne_of_lt (Nat.succ_lt_succ hj)
            rw [oneSubQPow_of_pos_ne (Nat.succ_ne_zero j) hjk, Int.zero_mul]
          rw [hzr, Int.add_zero]
      have htail : sumRange (m + 1 - k) (fun r => oneSubQPow k (k + 1 + r) * oneAddQPow k (m + 1 - (k + 1 + r))) = 0 := by
        apply sumRange_zero_of
        intro r _
        have hpos : k + 1 + r ≠ 0 := by
          rw [Nat.add_assoc, Nat.add_comm 1 r, ← Nat.add_assoc]
          exact Nat.succ_ne_zero (k + r)
        have hgt : k < k + 1 + r := by
          rw [Nat.add_assoc]
          exact Nat.lt_add_of_pos_right (Nat.add_comm 1 r ▸ Nat.zero_lt_succ r)
        rw [oneSubQPow_of_pos_ne hpos (Nat.ne_of_gt hgt), Int.zero_mul]
      rw [hfirst, htail, Int.add_zero, oneSubQPow_at_self hk]
      have hneg1 : ∀ x : Int, (-1 : Int) * x = -x := fun x => by
        have h : (-1 : Int) = -(1 : Int) := Eq.refl _
        rw [h, Int.neg_mul, Int.one_mul]
      rw [hneg1, ← Int.sub_eq_add_neg]
      by_cases heqk : m + 1 = k
      · rw [heqk, Nat.sub_self, oneAddQPow_at_self hk, oneAddQPow_zero, Int.sub_self]
        have hne2 : k ≠ 2 * k := by
          intro h
          have h0 : k + 0 = k + k := by
            rw [Nat.add_zero, ← Nat.two_mul]; exact h
          exact Nat.ne_of_gt hk (Nat.add_left_cancel h0).symm
        exact (oneSubQPow_of_pos_ne (Nat.ne_of_gt hk) hne2).symm
      · by_cases heq2k : m + 1 = 2 * k
        · have hsubk : m + 1 - k = k := by
            rw [heq2k, Nat.two_mul, Nat.add_sub_cancel]
          have h2kne : 2 * k ≠ k := by
            intro h
            have h0 : k + k = k + 0 := by rw [← Nat.two_mul, Nat.add_zero]; exact h
            exact Nat.ne_of_gt hk (Nat.add_left_cancel h0)
          have h2k_pos : 0 < 2 * k := Nat.mul_pos (by decide : 0 < 2) hk
          rw [hsubk, oneAddQPow_at_self hk, heq2k,
              oneAddQPow_of_pos_ne (Nat.ne_of_gt h2k_pos) h2kne,
              oneSubQPow_at_self h2k_pos]
          exact Eq.refl _
        · have hsub_ne0 : m + 1 - k ≠ 0 := by
            intro h0
            have h1 : m + 1 = k := by
              have hle' := Nat.add_sub_of_le hle
              rw [h0, Nat.add_zero] at hle'
              exact hle'.symm
            exact heqk h1
          have hsub_nek : m + 1 - k ≠ k := by
            intro hk'
            have h1 : m + 1 = 2 * k := by
              have hle' := Nat.add_sub_of_le hle
              rw [hk', ← Nat.two_mul] at hle'
              exact hle'.symm
            exact heq2k h1
          rw [oneAddQPow_of_pos_ne (Nat.succ_ne_zero m) heqk,
              oneAddQPow_of_pos_ne hsub_ne0 hsub_nek, Int.sub_self,
              oneSubQPow_of_pos_ne (Nat.succ_ne_zero m) heq2k]

theorem prodAllMinus_two_mul : ∀ M : Nat,
    FPSEq (prodAllMinus (2 * M)) (fpsMul (prodOddMinus M) (prodEvenMinus M))
  | 0 => (fpsMul_one_left fpsOne).symm
  | m + 1 => by
    have h2 : 2 * (m + 1) = (2 * m + 1) + 1 := Eq.refl _
    rw [h2]
    change FPSEq
      (fpsMul (fpsMul (prodAllMinus (2 * m)) (oneSubQPow (2 * m + 1))) (oneSubQPow (2 * m + 2)))
      (fpsMul (fpsMul (prodOddMinus m) (oneSubQPow (2 * m + 1)))
              (fpsMul (prodEvenMinus m) (oneSubQPow (2 * m + 2))))
    have hih := prodAllMinus_two_mul m
    have h1 := fpsMul_congr (fpsMul_congr hih (FPSEq.refl (oneSubQPow (2 * m + 1)))) (FPSEq.refl (oneSubQPow (2 * m + 2)))
    have h2' := fpsMul_assoc (prodOddMinus m) (prodEvenMinus m) (oneSubQPow (2 * m + 1))
    have h3 := fpsMul_congr (FPSEq.refl (prodOddMinus m)) (fpsMul_comm (prodEvenMinus m) (oneSubQPow (2 * m + 1)))
    have h4 := (fpsMul_assoc (prodOddMinus m) (oneSubQPow (2 * m + 1)) (prodEvenMinus m)).symm
    have h5 := fpsMul_congr (FPSEq.trans h2' (FPSEq.trans h3 h4)) (FPSEq.refl (oneSubQPow (2 * m + 2)))
    have h6 := fpsMul_assoc (fpsMul (prodOddMinus m) (oneSubQPow (2 * m + 1))) (prodEvenMinus m) (oneSubQPow (2 * m + 2))
    exact FPSEq.trans h1 (FPSEq.trans h5 h6)

theorem prodEvenMinus_eq_mul_distinct : ∀ M : Nat,
    FPSEq (prodEvenMinus M) (fpsMul (prodAllMinus M) (prodDistinct M))
  | 0 => (fpsMul_one_left fpsOne).symm
  | m + 1 => by
    change FPSEq (fpsMul (prodEvenMinus m) (oneSubQPow (2 * m + 2)))
      (fpsMul (fpsMul (prodAllMinus m) (oneSubQPow (m + 1)))
              (fpsMul (prodDistinct m) (oneAddQPow (m + 1))))
    have h2m2 : 2 * m + 2 = 2 * (m + 1) := Eq.refl _
    have htwo : FPSEq (oneSubQPow (2 * m + 2)) (fpsMul (oneSubQPow (m + 1)) (oneAddQPow (m + 1))) := by
      rw [h2m2]; exact (oneSub_mul_oneAdd_eq_two (m + 1) (Nat.zero_lt_succ m)).symm
    have hih := prodEvenMinus_eq_mul_distinct m
    have h1 := fpsMul_congr hih htwo
    have hA := (fpsMul_assoc (fpsMul (prodAllMinus m) (prodDistinct m)) (oneSubQPow (m + 1)) (oneAddQPow (m + 1))).symm
    have hB := fpsMul_assoc (prodAllMinus m) (prodDistinct m) (oneSubQPow (m + 1))
    have hC := fpsMul_congr (FPSEq.refl (prodAllMinus m)) (fpsMul_comm (prodDistinct m) (oneSubQPow (m + 1)))
    have hD := (fpsMul_assoc (prodAllMinus m) (oneSubQPow (m + 1)) (prodDistinct m)).symm
    have hBC := fpsMul_congr (FPSEq.trans hB (FPSEq.trans hC hD)) (FPSEq.refl (oneAddQPow (m + 1)))
    have hE := fpsMul_assoc (fpsMul (prodAllMinus m) (oneSubQPow (m + 1))) (prodDistinct m) (oneAddQPow (m + 1))
    exact FPSEq.trans h1 (FPSEq.trans hA (FPSEq.trans hBC hE))

theorem fpsMul_tail_one_lt (f g : FPS) (K : Nat)
    (hg0 : g 0 = 1) (hgz : ∀ j, 1 ≤ j → j < K → g j = 0) :
    ∀ n, n < K → fpsMul f g n = f n := by
  intro n hn
  change sumRange (n + 1) (fun k => f k * g (n - k)) = f n
  change sumRange n (fun k => f k * g (n - k)) + f n * g (n - n) = f n
  rw [Nat.sub_self, hg0, Int.mul_one]
  have hzr : sumRange n (fun k => f k * g (n - k)) = 0 := by
    apply sumRange_zero_of
    intro k hk
    have h1 : 1 ≤ n - k := Nat.sub_pos_of_lt hk
    have h2 : n - k < K := Nat.lt_of_le_of_lt (Nat.sub_le n k) hn
    rw [hgz (n - k) h1 h2, Int.mul_zero]
  rw [hzr, Int.zero_add]

theorem prodAllMinus_step_stabilizes (M n : Nat) (hn : n ≤ M) :
    prodAllMinus (M + 1) n = prodAllMinus M n := by
  apply fpsMul_tail_one_lt (prodAllMinus M) (oneSubQPow (M + 1)) (M + 1) (oneSubQPow_zero (M + 1))
  · intro j hj1 hjM
    exact oneSubQPow_of_pos_ne (Nat.ne_of_gt hj1) (Nat.ne_of_lt hjM)
  · exact Nat.lt_succ_of_le hn

theorem prodAllMinus_stabilizes_all : ∀ M n d : Nat,
    n ≤ M → prodAllMinus (M + d) n = prodAllMinus M n
  | _, _, 0, _ => Eq.refl _
  | M, n, d + 1, hn => by
    have hstep : prodAllMinus (M + d + 1) n = prodAllMinus (M + d) n :=
      prodAllMinus_step_stabilizes (M + d) n (Nat.le_trans hn (Nat.le_add_right M d))
    have hadd : M + (d + 1) = (M + d) + 1 := (Nat.add_assoc M d 1).symm
    rw [hadd, hstep]
    exact prodAllMinus_stabilizes_all M n d hn

theorem prodDistinct_step_stabilizes (M n : Nat) (hn : n ≤ M) :
    prodDistinct (M + 1) n = prodDistinct M n := by
  apply fpsMul_tail_one_lt (prodDistinct M) (oneAddQPow (M + 1)) (M + 1) (oneAddQPow_zero (M + 1))
  · intro j hj1 hjM
    exact oneAddQPow_of_pos_ne (Nat.ne_of_gt hj1) (Nat.ne_of_lt hjM)
  · exact Nat.lt_succ_of_le hn

theorem prodDistinct_stabilizes_add : ∀ n d : Nat,
    prodDistinct (n + d) n = distinctPartsFPS n
  | _, 0 => Eq.refl _
  | n, d + 1 => by
    have hadd : n + (d + 1) = (n + d) + 1 := (Nat.add_assoc n d 1).symm
    rw [hadd, prodDistinct_step_stabilizes (n + d) n (Nat.le_add_right n d)]
    exact prodDistinct_stabilizes_add n d

theorem prodDistinct_stabilizes_all : ∀ M n : Nat,
    n ≤ M → prodDistinct M n = distinctPartsFPS n := by
  intro M n hn
  have hM : M = n + (M - n) := (Nat.add_sub_of_le hn).symm
  rw [hM]
  exact prodDistinct_stabilizes_add n (M - n)

theorem prodOddMinus_step_stabilizes (M n : Nat) (hn : n ≤ 2 * M) :
    prodOddMinus (M + 1) n = prodOddMinus M n := by
  apply fpsMul_tail_one_lt (prodOddMinus M) (oneSubQPow (2 * M + 1)) (2 * M + 1) (oneSubQPow_zero (2 * M + 1))
  · intro j hj1 hjM
    exact oneSubQPow_of_pos_ne (Nat.ne_of_gt hj1) (Nat.ne_of_lt hjM)
  · exact Nat.lt_succ_of_le hn

theorem prodOddMinus_stabilizes_add : ∀ M n d : Nat,
    n ≤ 2 * M → prodOddMinus (M + d) n = prodOddMinus M n
  | _, _, 0, _ => Eq.refl _
  | M, n, d + 1, hn => by
    have hadd : M + (d + 1) = (M + d) + 1 := (Nat.add_assoc M d 1).symm
    have hle : n ≤ 2 * (M + d) := by
      have h2le : 2 * M ≤ 2 * (M + d) := Nat.mul_le_mul_left 2 (Nat.le_add_right M d)
      exact Nat.le_trans hn h2le
    rw [hadd, prodOddMinus_step_stabilizes (M + d) n hle]
    exact prodOddMinus_stabilizes_add M n d hn

theorem oddParts_stabilizes_all : ∀ M n : Nat,
    n ≤ 2 * M → fpsInv (prodOddMinus M) n = oddPartsFPS n := by
  intro M n hn
  dsimp [oddPartsFPS]
  apply fpsInv_eq_on_le (N := n)
  · intro j hj
    have hjM : j ≤ 2 * M := Nat.le_trans hj hn
    have hjN1 : j ≤ 2 * (n + 1) := by
      have h1 : n ≤ 2 * (n + 1) := by
        rw [Nat.mul_add, Nat.two_mul]
        exact Nat.le_add_right n (n + 2 * 1)
      exact Nat.le_trans hj h1
    have hL : prodOddMinus (M + (n + 1)) j = prodOddMinus M j :=
      prodOddMinus_stabilizes_add M j (n + 1) hjM
    have hR : prodOddMinus (n + 1 + M) j = prodOddMinus (n + 1) j :=
      prodOddMinus_stabilizes_add (n + 1) j M hjN1
    rw [← hL, Nat.add_comm M (n + 1), hR]
  · exact Nat.le_refl n

theorem euler_odd_eq_distinct_all_n : ∀ n : Nat, oddPartsFPS n = distinctPartsFPS n := by
  intro n
  let M := n + 1
  have hnM : n ≤ M := Nat.le_succ n
  have hprod : ∀ j, j ≤ M → fpsMul (prodOddMinus M) (prodDistinct M) j = fpsOne j := by
    have hA_prod : ∀ j, j ≤ M →
        fpsMul (prodAllMinus M) (fpsMul (prodOddMinus M) (prodDistinct M)) j =
        fpsMul (prodAllMinus M) fpsOne j := by
      intro j hj
      have hcomm1 := fpsMul_comm (prodOddMinus M) (prodDistinct M) j
      have hassoc := (fpsMul_assoc (prodAllMinus M) (prodDistinct M) (prodOddMinus M) j).symm
      have heven := (prodEvenMinus_eq_mul_distinct M).symm
      have h2 := fpsMul_congr heven (FPSEq.refl (prodOddMinus M)) j
      have hcomm2 := fpsMul_comm (prodEvenMinus M) (prodOddMinus M) j
      have htwo := (prodAllMinus_two_mul M j).symm
      have hstab : prodAllMinus (2 * M) j = prodAllMinus M j := by
        rw [Nat.two_mul]; exact prodAllMinus_stabilizes_all M j M hj
      have h1r := (fpsMul_one_right (prodAllMinus M) j).symm
      calc fpsMul (prodAllMinus M) (fpsMul (prodOddMinus M) (prodDistinct M)) j
          = fpsMul (prodAllMinus M) (fpsMul (prodDistinct M) (prodOddMinus M)) j := by
            exact fpsMul_congr (FPSEq.refl _) (fpsMul_comm _ _) j
        _ = fpsMul (fpsMul (prodAllMinus M) (prodDistinct M)) (prodOddMinus M) j := hassoc
        _ = fpsMul (prodEvenMinus M) (prodOddMinus M) j := h2
        _ = fpsMul (prodOddMinus M) (prodEvenMinus M) j := hcomm2
        _ = prodAllMinus (2 * M) j := htwo
        _ = prodAllMinus M j := hstab
        _ = fpsMul (prodAllMinus M) fpsOne j := h1r
    intro j hj
    let A := prodAllMinus M
    let X := fpsMul (prodOddMinus M) (prodDistinct M)
    have hA0 : A 0 = 1 := prodAllMinus_zero M
    have h1 : X j = fpsMul fpsOne X j := (fpsMul_one_left X j).symm
    have h2 : fpsMul fpsOne X j = fpsMul (fpsMul (fpsInv A) A) X j :=
      fpsMul_congr (fpsMul_inv_left A hA0).symm (FPSEq.refl X) j
    have h3 : fpsMul (fpsMul (fpsInv A) A) X j = fpsMul (fpsInv A) (fpsMul A X) j :=
      fpsMul_assoc (fpsInv A) A X j
    have h4 : fpsMul (fpsInv A) (fpsMul A X) j = fpsMul (fpsInv A) (fpsMul A fpsOne) j :=
      fpsMul_eq_on_le (N := j) (fun k _ => Eq.refl _)
        (fun k hk => hA_prod k (Nat.le_trans hk hj)) j (Nat.le_refl j)
    have h5 : fpsMul (fpsInv A) (fpsMul A fpsOne) j =
        fpsMul (fpsMul (fpsInv A) A) fpsOne j := (fpsMul_assoc (fpsInv A) A fpsOne j).symm
    have h6 : fpsMul (fpsMul (fpsInv A) A) fpsOne j = fpsMul fpsOne fpsOne j :=
      fpsMul_congr (fpsMul_inv_left A hA0) (FPSEq.refl fpsOne) j
    have h7 : fpsMul fpsOne fpsOne j = fpsOne j := fpsMul_one_left fpsOne j
    exact h1.trans (h2.trans (h3.trans (h4.trans (h5.trans (h6.trans h7)))))
  have hinv : prodDistinct M n = fpsInv (prodOddMinus M) n :=
    fpsInv_unique_lt (M + 1) (prodOddMinus M) (prodDistinct M) (prodOddMinus_zero M)
      (fun m hm => hprod m (Nat.le_of_lt_succ hm)) n (Nat.lt_succ_of_le hnM)
  have hd : prodDistinct M n = distinctPartsFPS n := prodDistinct_stabilizes_all M n hnM
  change fpsInv (prodOddMinus M) n = distinctPartsFPS n
  exact hinv.symm.trans hd

theorem euler_odd_eq_distinct_all_len : ∀ len : Nat, oddPartsList len = distinctPartsList len := by
  intro len
  apply list_ext_getD 0
  · dsimp [oddPartsList, distinctPartsList]; rw [List.length_map, List.length_map]
  · intro i hi
    dsimp [oddPartsList] at hi
    rw [List.length_map, list_range_length] at hi
    dsimp [oddPartsList, distinctPartsList]
    rw [getD_map_range 0 oddPartsFPS len i hi, getD_map_range 0 distinctPartsFPS len i hi]
    exact euler_odd_eq_distinct_all_n i

theorem pentagonal_product_matches_baseEta_20 :
    prodAllMinusList 20 20 = baseEta 20 ∧ (∀ n, n < 20 → eulerProductFPS n = eulerPentCoeff n) := by
  have hdec : prodAllMinusList 20 20 = baseEta 20 := by decide
  refine ⟨hdec, fun n hn => ?_⟩
  have hstab : eulerProductFPS n = prodAllMinus 20 n := by
    dsimp [eulerProductFPS]
    have hle : n ≤ 20 := Nat.le_of_lt hn
    have hadd : n + (20 - n) = 20 := Nat.add_sub_of_le hle
    have hs := prodAllMinus_stabilizes_all n n (20 - n) (Nat.le_refl n)
    rw [hadd] at hs
    exact hs.symm
  rw [hstab, ← prodAllMinusList_getD 20 20 n hn, hdec]
  exact getD_map_range 0 eulerPentCoeff 20 n hn

theorem partition_pentagonal_recurrence_all_n : ∀ n : Nat,
    sumRange (n + 1) (fun k => eulerPentCoeff k * fpsInv baseEtaFPS (n - k)) =
    if n == 0 then 1 else 0 := by
  intro n
  have hmul : sumRange (n + 1) (fun k => eulerPentCoeff k * fpsInv baseEtaFPS (n - k)) =
      fpsMul baseEtaFPS (fpsInv baseEtaFPS) n := Eq.refl _
  rw [hmul]
  exact fpsMul_inv_right baseEtaFPS (Eq.refl 1) n

theorem partList_matches_fpsInv_65 :
    polyMul (baseEta 65) (partList 65) 65 = 1 :: List.replicate 64 0 := by decide

theorem partList_eq_fpsInv_lt_65 : ∀ n : Nat, n < 65 →
    (partList 65).getD n 0 = fpsInv baseEtaFPS n := by
  apply fpsInv_unique_lt 65 baseEtaFPS (listToFPS (partList 65)) (Eq.refl 1)
  intro n hn
  have hm := polyMul_getD (baseEta 65) (partList 65) baseEtaFPS (listToFPS (partList 65)) 65 n hn
    (fun k hk => getD_map_range 0 eulerPentCoeff 65 k hk)
    (fun k _ => Eq.refl _)
  rw [← hm, partList_matches_fpsInv_65]
  exact oneList_getD 65 n hn

theorem euler_combinatorial_odd_eq_distinct_20 :
    (List.range 21).all (fun n =>
      countOddPartsMin n 1 == countDistinctPartsMin n 1 &&
      (countOddPartsMin n 1 : Int) == (prodDistinctList n (n + 1)).getD n 0) = true := by decide

theorem euler_combinatorial_eq_oddPartsFPS_le_20 : ∀ n : Nat, n ≤ 20 →
    (countOddPartsMin n 1 : Int) = oddPartsFPS n ∧
    (countDistinctPartsMin n 1 : Int) = distinctPartsFPS n := by
  intro n hn
  have hm : n ∈ List.range 21 := mem_list_range (Nat.lt_succ_of_le hn)
  have hall := list_mem_of_all _ (List.range 21) euler_combinatorial_odd_eq_distinct_20 n hm
  cases hc1 : (countOddPartsMin n 1 == countDistinctPartsMin n 1)
  · rw [hc1] at hall; cases hall
  · rw [hc1] at hall
    have heq1 : countOddPartsMin n 1 = countDistinctPartsMin n 1 := (nat_beq_iff_eq _ _).mp hc1
    have heq2 : (countOddPartsMin n 1 : Int) = (prodDistinctList n (n + 1)).getD n 0 :=
      (int_beq_iff_eq _ _).mp hall
    have hd : (prodDistinctList n (n + 1)).getD n 0 = distinctPartsFPS n :=
      prodDistinctList_getD n (n + 1) n (Nat.lt_succ_self n)
    rw [heq2, hd, ← euler_odd_eq_distinct_all_n n]
    refine ⟨Eq.refl _, ?_⟩
    rw [← heq1, heq2, hd, euler_odd_eq_distinct_all_n n]

theorem neg_ctrl_even_parts_ne_distinct :
    fpsInv (prodEvenMinus 2) 1 = 0 ∧ distinctPartsFPS 1 = 1 ∧
    countEvenPartsMin 3 2 ≠ countDistinctPartsMin 3 1 := by decide

theorem neg_ctrl_omit_part1_distinct_fails :
    (fpsMul (oneAddQPow 2) (oneAddQPow 3)) 1 ≠ oddPartsFPS 1 := by decide

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 2: Ramanujan Partition Congruences (mod 5, 7, 11) & Generating Identities
-- ═══════════════════════════════════════════════════════════════════════════════

def mod5QuotEta : List (Nat × Int) := [(1, -6), (5, 5)]
def mod7Term1Eta : List (Nat × Int) := [(1, -4), (7, 3)]
def mod7Term2Eta : List (Nat × Int) := [(1, -8), (7, 7)]

def RamanujanMod5GenId : Prop :=
  ∀ n : Nat, fpsInv baseEtaFPS (5 * n + 4) = 5 * etaFPS { factors := mod5QuotEta } n

def RamanujanMod7GenId : Prop :=
  ∀ n : Nat, fpsInv baseEtaFPS (7 * n + 5) =
    evalLinearEtaFPS [(7, 0, mod7Term1Eta), (49, 1, mod7Term2Eta)] n

theorem ramanujan_mod5_prefix_13 :
    (List.range 13).all (fun n => (partList 65).getD (5 * n + 4) 0 % 5 == 0) = true := by decide

theorem ramanujan_mod7_prefix_9 :
    (List.range 9).all (fun n => (partList 65).getD (7 * n + 5) 0 % 7 == 0) = true := by decide

theorem ramanujan_mod11_prefix_6 :
    (List.range 6).all (fun n => (partList 65).getD (11 * n + 6) 0 % 11 == 0) = true := by decide

theorem ramanujan_mod5_gen_identity_12 :
    (List.range 12).map (fun n => (partList 65).getD (5 * n + 4) 0) =
    (etaCoeffs { factors := mod5QuotEta } 12).map (5 * ·) := by decide

theorem ramanujan_mod5_gen_fps_lt_12 : ∀ n : Nat, n < 12 →
    fpsInv baseEtaFPS (5 * n + 4) = 5 * etaFPS { factors := mod5QuotEta } n := by
  intro n hn
  have h65 : 5 * n + 4 < 65 := by
    have h1 : 5 * n ≤ 5 * 11 := Nat.mul_le_mul_left 5 (Nat.le_of_lt_succ hn)
    exact Nat.lt_of_le_of_lt (Nat.add_le_add_right h1 4) (by decide : 5 * 11 + 4 < 65)
  rw [← partList_eq_fpsInv_lt_65 (5 * n + 4) h65]
  have hL : (partList 65).getD (5 * n + 4) 0 =
      ((List.range 12).map (fun k => (partList 65).getD (5 * k + 4) 0)).getD n 0 :=
    (getD_map_range 0 (fun k => (partList 65).getD (5 * k + 4) 0) 12 n hn).symm
  have hlen : n < (etaCoeffs { factors := mod5QuotEta } 12).length := by
    rw [etaCoeffs_length]; exact hn
  have hR : ((etaCoeffs { factors := mod5QuotEta } 12).map (5 * ·)).getD n 0 =
      5 * etaFPS { factors := mod5QuotEta } n := by
    rw [list_getD_map 0 0 (5 * ·) _ n hlen, etaCoeffs_getD _ 12 n hn]
  rw [hL, ramanujan_mod5_gen_identity_12, hR]

theorem ramanujan_mod7_gen_identity_9 :
    (List.range 9).map (fun n => (partList 65).getD (7 * n + 5) 0) =
    evalLinearEta [(7, 0, mod7Term1Eta), (49, 1, mod7Term2Eta)] 9 := by decide

theorem ramanujan_mod7_gen_fps_lt_9 : ∀ n : Nat, n < 9 →
    fpsInv baseEtaFPS (7 * n + 5) =
    evalLinearEtaFPS [(7, 0, mod7Term1Eta), (49, 1, mod7Term2Eta)] n := by
  intro n hn
  have h65 : 7 * n + 5 < 65 := by
    have h1 : 7 * n ≤ 7 * 8 := Nat.mul_le_mul_left 7 (Nat.le_of_lt_succ hn)
    exact Nat.lt_of_le_of_lt (Nat.add_le_add_right h1 5) (by decide : 7 * 8 + 5 < 65)
  rw [← partList_eq_fpsInv_lt_65 (7 * n + 5) h65]
  have hL : (partList 65).getD (7 * n + 5) 0 =
      ((List.range 9).map (fun k => (partList 65).getD (7 * k + 5) 0)).getD n 0 :=
    (getD_map_range 0 (fun k => (partList 65).getD (7 * k + 5) 0) 9 n hn).symm
  rw [hL, ramanujan_mod7_gen_identity_9, evalLinearEta_getD_eq_FPS _ 9 n hn]

theorem ramanujan_mod5_all_n_conditional (h_gen : RamanujanMod5GenId) :
    ∀ n : Nat, fpsInv baseEtaFPS (5 * n + 4) % 5 = 0 := by
  intro n
  rw [h_gen n]
  exact Int.mul_emod_right 5 (etaFPS { factors := mod5QuotEta } n)

theorem ramanujan_mod7_all_n_conditional (h_gen : RamanujanMod7GenId) :
    ∀ n : Nat, fpsInv baseEtaFPS (7 * n + 5) % 7 = 0 := by
  intro n
  rw [h_gen n]
  change ((0 + 7 * (if n ≥ 0 then etaFPS { factors := mod7Term1Eta } (n - 0) else 0)) +
      49 * (if n ≥ 1 then etaFPS { factors := mod7Term2Eta } (n - 1) else 0)) % 7 = 0
  have h49 : (49 : Int) = 7 * 7 := Eq.refl _
  rw [Int.zero_add, h49, Int.mul_assoc 7 7 _, Int.add_emod,
      Int.mul_emod_right 7 _, Int.mul_emod_right 7 _]
  exact Eq.refl _

theorem mod5_other_residues_nz_check :
    (List.range 4).all (fun r => (partList 65).getD r 0 % 5 != 0) = true := by decide

theorem neg_ctrl_mod5_other_residues_fail :
    ∀ r : Nat, r < 4 → ¬ (∀ n : Nat, fpsInv baseEtaFPS (5 * n + r) % 5 = 0) := by
  intro r hr hall
  have h0 := hall 0
  rw [Nat.mul_zero, Nat.zero_add] at h0
  have h65 : r < 65 := Nat.lt_trans hr (by decide : 4 < 65)
  rw [← partList_eq_fpsInv_lt_65 r h65] at h0
  have hb := list_mem_of_all _ (List.range 4) mod5_other_residues_nz_check r (mem_list_range hr)
  rw [h0] at hb
  cases hb

theorem mod13_residues_nz_check :
    (List.range 13).all (fun β => (partList 65).getD β 0 % 13 != 0) = true := by decide

theorem neg_ctrl_mod13_no_linear_congruence :
    ∀ β : Nat, β < 13 → ¬ (∀ n : Nat, fpsInv baseEtaFPS (13 * n + β) % 13 = 0) := by
  intro β hβ hall
  have h0 := hall 0
  rw [Nat.mul_zero, Nat.zero_add] at h0
  have h65 : β < 65 := Nat.lt_trans hβ (by decide : 13 < 65)
  rw [← partList_eq_fpsInv_lt_65 β h65] at h0
  have hb := list_mem_of_all _ (List.range 13) mod13_residues_nz_check β (mem_list_range hβ)
  rw [h0] at hb
  cases hb

theorem mod3_residues_nz_check :
    (List.range 3).all (fun β => (partList 65).getD β 0 % 3 != 0) = true := by decide

theorem neg_ctrl_mod3_no_linear_congruence :
    ∀ β : Nat, β < 3 → ¬ (∀ n : Nat, fpsInv baseEtaFPS (3 * n + β) % 3 = 0) := by
  intro β hβ hall
  have h0 := hall 0
  rw [Nat.mul_zero, Nat.zero_add] at h0
  have h65 : β < 65 := Nat.lt_trans hβ (by decide : 3 < 65)
  rw [← partList_eq_fpsInv_lt_65 β h65] at h0
  have hb := list_mem_of_all _ (List.range 3) mod3_residues_nz_check β (mem_list_range hβ)
  rw [h0] at hb
  cases hb

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 3: Ramanujan's τ-Function (Δ(q)/q = η(τ)^24)
-- ═══════════════════════════════════════════════════════════════════════════════

def IsPrime (p : Nat) : Prop :=
  2 ≤ p ∧ ∀ d : Nat, 1 < d → d < p → p % d ≠ 0

def tauEta : EtaQuot := { factors := [(1, 24)] }
def tauList16 : List Int := polyPowNat (baseEta 16) 24 16
def tau16 (n : Nat) : Int := if n == 0 then 0 else tauList16.getD (n - 1) 0
def tauFPS (n : Nat) : Int := if n == 0 then 0 else etaFPS tauEta (n - 1)

def sigmaK (k n : Nat) : Int :=
  if n == 0 then 0
  else sumRange n (fun d0 =>
    let d := d0 + 1
    if n % d == 0 then ((d ^ k : Nat) : Int) else 0)

theorem tau_exact_1_to_16 :
    tauList16 = [1, -24, 252, -1472, 4830, -6048, -16744, 84480,
      -113643, -115920, 534612, -370944, -577738, 401856, 1217160, 987136] := by decide

theorem dilateFPS_one_id (f : FPS) : FPSEq (dilateFPS f 1) f := by
  intro n
  dsimp [dilateFPS]
  rw [Nat.mod_one, Nat.div_one]
  exact Eq.refl _

theorem tau16_eq_tauFPS_le_16 : ∀ n : Nat, 1 ≤ n → n ≤ 16 → tau16 n = tauFPS n := by
  intro n hn1 hn16
  have hne0 : (n == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt hn1)
  dsimp [tau16, tauFPS]
  rw [bool_cond_false hne0, bool_cond_false hne0]
  have hlt16 : n - 1 < 16 := Nat.lt_of_lt_of_le (Nat.sub_lt hn1 (by decide : 0 < 1)) hn16
  dsimp [tauList16]
  rw [polyPowNat_getD (baseEta 16) baseEtaFPS 24 16 (n - 1) hlt16
    (fun k hk => getD_map_range 0 eulerPentCoeff 16 k hk)]
  have heta : FPSEq (etaFPS tauEta) (fpsPowNat baseEtaFPS 24) := by
    dsimp [tauEta, etaFPS, etaFactorFPS, fpsPowInt]
    change FPSEq (fpsMul fpsOne (fpsPowNat (dilateFPS baseEtaFPS 1) 24)) (fpsPowNat baseEtaFPS 24)
    exact FPSEq.trans (fpsMul_one_left _) (fpsPowNat_congr (dilateFPS_one_id baseEtaFPS) 24)
  exact (heta (n - 1)).symm

theorem tau_ono_level1_weight12 :
    modularWeight tauEta = (12, 1) ∧ onoCong1 tauEta = true ∧ onoCong2 tauEta 1 = true := by decide

theorem sumRange_pred_split (n : Nat) (hn : 2 ≤ n) (F : Nat → Int) :
    sumRange n F = F 0 + sumRange (n - 2) (fun r => F (r + 1)) + F (n - 1) := by
  have h1 : n = (n - 1) + 1 := (Nat.sub_add_cancel (Nat.le_trans (by decide : 1 ≤ 2) hn)).symm
  have h2 : n - 1 = (n - 2) + 1 := by
    have hle : 1 ≤ n - 1 := by
      have := Nat.sub_le_sub_right hn 1
      exact this
    have := (Nat.sub_add_cancel hle).symm
    rw [Nat.sub_sub] at this
    exact this
  conv => lhs; rw [h1]
  change sumRange (n - 1) F + F (n - 1) = _
  conv => lhs; arg 1; rw [h2]
  rw [sumRange_succ_shift (n - 2) F]

theorem sigmaK_prime_all_p : ∀ k p : Nat, IsPrime p →
    sigmaK k p = 1 + ((p ^ k : Nat) : Int) := by
  intro k p ⟨hp2, hprime⟩
  have hp0 : (p == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt (Nat.lt_of_lt_of_le (by decide : 0 < 2) hp2))
  dsimp [sigmaK]
  rw [bool_cond_false hp0]
  let F : Nat → Int := fun d0 => if p % (d0 + 1) == 0 then (((d0 + 1) ^ k : Nat) : Int) else 0
  change sumRange p F = 1 + ((p ^ k : Nat) : Int)
  rw [sumRange_pred_split p hp2 F]
  have hfirst : F 0 = 1 := by
    dsimp [F]
    have hm : (p % (0 + 1) == 0) = true := by rw [Nat.zero_add, Nat.mod_one]; exact Eq.refl _
    rw [bool_cond_true hm, Int.one_pow]
  have hmid : sumRange (p - 2) (fun r => F (r + 1)) = 0 := by
    apply sumRange_zero_of
    intro r hr
    dsimp [F]
    have h1lt : 1 < r + 2 := Nat.succ_lt_succ (Nat.zero_lt_succ r)
    have hltp : r + 2 < p := by
      have := Nat.add_lt_add_right hr 2
      rw [Nat.sub_add_cancel hp2] at this
      exact this
    have hndvd : p % (r + 2) ≠ 0 := hprime (r + 2) h1lt hltp
    rw [bool_cond_false (nat_beq_false_of_ne hndvd)]
  have hp1 : p - 1 + 1 = p := Nat.sub_add_cancel (Nat.le_trans (by decide : 1 ≤ 2) hp2)
  have hlast : F (p - 1) = ((p ^ k : Nat) : Int) := by
    dsimp [F]
    have hm : (p % (p - 1 + 1) == 0) = true := by rw [hp1, Nat.mod_self]; exact Eq.refl _
    have hp1' : (p - 1).succ = p := hp1
    rw [bool_cond_true hm, ← Int.natCast_succ (p - 1), hp1']
  rw [hfirst, hmid, Int.add_zero, hlast]

theorem tau_coprime_multiplicative_witnesses :
    tau16 6 = tau16 2 * tau16 3 ∧ tau16 10 = tau16 2 * tau16 5 ∧
    tau16 12 = tau16 3 * tau16 4 ∧ tau16 14 = tau16 2 * tau16 7 ∧
    tau16 15 = tau16 3 * tau16 5 := by decide

theorem tau_hecke_prime_power_witnesses :
    tau16 4 = tau16 2 * tau16 2 - (2 : Int) ^ 11 ∧
    tau16 9 = tau16 3 * tau16 3 - (3 : Int) ^ 11 ∧
    tau16 8 = tau16 2 * tau16 4 - (2 : Int) ^ 11 * tau16 2 ∧
    tau16 16 = tau16 2 * tau16 8 - (2 : Int) ^ 11 * tau16 4 := by decide

theorem tau_mod_691_witnesses_16 :
    (List.range 16).all (fun k => let n := k + 1; (tau16 n - sigmaK 11 n) % 691 == 0) = true := by decide

theorem tau_deligne_squared_bounds :
    ([2, 3, 5, 7, 11, 13] : List Nat).all (fun p => tau16 p * tau16 p ≤ 4 * (p : Int) ^ 11) = true := by decide

theorem tau_nonzero_and_avoids_forbidden_16 :
    (List.range 16).all (fun k => tau16 (k + 1) != 0) = true ∧
    (List.range 15).all (fun k =>
      let v := (tau16 (k + 2)).natAbs
      v != 1 && v != 3 && v != 5 && v != 7 && v != 691) = true := by decide

theorem neg_ctrl_tau_noncoprime_fails : tau16 4 ≠ tau16 2 * tau16 2 := by decide

theorem neg_ctrl_tau_mod691_perturbed_fails : (tau16 2 + 1 - sigmaK 11 2) % 691 ≠ 0 := by decide

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 4: Ramanujan Sums c_q(n) (1918)
-- ═══════════════════════════════════════════════════════════════════════════════

def mobiusGo (k d : Nat) : Nat → Int
  | 0 => 0
  | fuel + 1 =>
    if k ≤ 1 then 1
    else if d * d > k then -1
    else if k % (d * d) == 0 then 0
    else if k % d == 0 then -mobiusGo (k / d) (d + 1) fuel
    else mobiusGo k (d + 1) fuel

def mobius (k : Nat) : Int :=
  if k == 0 then 0 else if k == 1 then 1 else mobiusGo k 2 (k + 2)

def ramanujanSum (q n : Nat) : Int :=
  if q == 0 then 0
  else sumRange q (fun d0 =>
    let d := d0 + 1
    if q % d == 0 && n % d == 0 then (d : Int) * mobius (q / d) else 0)

def eulerTotient (q : Nat) : Nat :=
  (List.range q).foldl (fun acc a => if Nat.gcd a q == 1 then acc + 1 else acc) 0

theorem ramanujanSum_zero_all_n : ∀ n : Nat, ramanujanSum 0 n = 0 :=
  fun _ => Eq.refl _

theorem ramanujanSum_one_all_n : ∀ n : Nat, ramanujanSum 1 n = 1 := by
  intro n
  change 0 + (if 1 % 1 == 0 && n % 1 == 0 then (1 : Int) * mobius (1 / 1) else 0) = 1
  rw [Nat.mod_one, Nat.mod_one, Nat.div_one]
  exact Eq.refl _

theorem mobiusGo_prime_aux : ∀ (fuel p d : Nat),
    IsPrime p → 2 ≤ d → d ≤ p → p + 1 ≤ d + fuel → mobiusGo p d fuel = -1
  | 0, p, d, _, _, hdp, hsum => by
    rw [Nat.add_zero] at hsum
    exact absurd (Nat.lt_of_lt_of_le (Nat.lt_succ_self p) hsum) (Nat.not_lt_of_ge hdp)
  | fuel + 1, p, d, hprime, hd2, hdp, hsum => by
    have hp2 : 2 ≤ p := hprime.1
    have hp_nle1 : ¬ (p ≤ 1) := Nat.not_le_of_gt (Nat.lt_of_lt_of_le (by decide : 1 < 2) hp2)
    dsimp [mobiusGo]
    rw [if_neg hp_nle1]
    by_cases hgt : d * d > p
    · rw [if_pos hgt]
    · rw [if_neg hgt]
      have hdd_le : d * d ≤ p := Nat.le_of_not_lt hgt
      have h1d : 1 < d := Nat.lt_of_lt_of_le (by decide : 1 < 2) hd2
      have hdp_lt : d < p := by
        have h2d : 2 * d ≤ d * d := Nat.mul_le_mul_right d hd2
        have hd_lt_2d : d < 2 * d := by
          rw [Nat.two_mul]
          exact Nat.lt_add_of_pos_left (Nat.lt_trans (by decide : 0 < 1) h1d)
        exact Nat.lt_of_lt_of_le (Nat.lt_of_lt_of_le hd_lt_2d h2d) hdd_le
      have hndvd : p % d ≠ 0 := hprime.2 d h1d hdp_lt
      have hndvd2 : p % (d * d) ≠ 0 := by
        intro h0
        have hdvd1 : d * d ∣ p := Nat.dvd_of_mod_eq_zero h0
        have hdvd2 : d ∣ d * d := Nat.dvd_mul_left d d
        exact hndvd (Nat.mod_eq_zero_of_dvd (Nat.dvd_trans hdvd2 hdvd1))
      rw [if_neg (by rw [nat_beq_false_of_ne hndvd2]; exact Bool.false_ne_true),
          if_neg (by rw [nat_beq_false_of_ne hndvd]; exact Bool.false_ne_true)]
      have hsum' : p + 1 ≤ (d + 1) + fuel := by
        rw [Nat.add_assoc, Nat.add_comm 1 fuel, ← Nat.add_assoc]
        exact hsum
      exact mobiusGo_prime_aux fuel p (d + 1) hprime (Nat.le_succ_of_le hd2) hdp_lt hsum'

theorem mobius_prime_eq_neg_one : ∀ p : Nat, IsPrime p → mobius p = -1 := by
  intro p hp
  have hp2 : 2 ≤ p := hp.1
  have hp0 : (p == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt (Nat.lt_of_lt_of_le (by decide : 0 < 2) hp2))
  have hp1 : (p == 1) = false := nat_beq_false_of_ne (Nat.ne_of_gt (Nat.lt_of_lt_of_le (by decide : 1 < 2) hp2))
  dsimp [mobius]
  rw [bool_cond_false hp0, bool_cond_false hp1]
  have hsum : p + 1 ≤ 2 + (p + 2) := by
    rw [Nat.add_comm 2 (p + 2), Nat.add_assoc]
    exact Nat.add_le_add_left (by decide : 1 ≤ 4) p
  exact mobiusGo_prime_aux (p + 2) p 2 hp (Nat.le_refl 2) hp2 hsum

theorem ramanujanSum_prime_all_n : ∀ p n : Nat, IsPrime p →
    ramanujanSum p n = if n % p == 0 then (p : Int) - 1 else -1 := by
  intro p n hp
  have hp2 : 2 ≤ p := hp.1
  have hp0 : (p == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt (Nat.lt_of_lt_of_le (by decide : 0 < 2) hp2))
  dsimp [ramanujanSum]
  rw [bool_cond_false hp0]
  let F : Nat → Int := fun d0 =>
    if p % (d0 + 1) == 0 && n % (d0 + 1) == 0 then ((d0 + 1 : Nat) : Int) * mobius (p / (d0 + 1)) else 0
  change sumRange p F = if n % p == 0 then (p : Int) - 1 else -1
  rw [sumRange_pred_split p hp2 F]
  have hfirst : F 0 = -1 := by
    dsimp [F]
    have hm : (p % (0 + 1) == 0 && n % (0 + 1) == 0) = true := by
      rw [Nat.zero_add, Nat.mod_one, Nat.mod_one]; exact Eq.refl _
    rw [bool_cond_true hm, Nat.div_one, mobius_prime_eq_neg_one p hp]
    exact Eq.refl _
  have hmid : sumRange (p - 2) (fun r => F (r + 1)) = 0 := by
    apply sumRange_zero_of
    intro r hr
    dsimp [F]
    have h1lt : 1 < r + 2 := Nat.succ_lt_succ (Nat.zero_lt_succ r)
    have hltp : r + 2 < p := by
      have := Nat.add_lt_add_right hr 2
      rw [Nat.sub_add_cancel hp2] at this
      exact this
    have hndvd : p % (r + 2) ≠ 0 := hp.2 (r + 2) h1lt hltp
    have hbf : (p % (r + 1 + 1) == 0 && n % (r + 1 + 1) == 0) = false := by
      rw [nat_beq_false_of_ne hndvd]; exact Eq.refl _
    rw [bool_cond_false hbf]
  have hp_pos : 0 < p := Nat.lt_of_lt_of_le (by decide : 0 < 2) hp2
  have hp1 : p - 1 + 1 = p := Nat.sub_add_cancel (Nat.le_trans (by decide : 1 ≤ 2) hp2)
  have hlast : F (p - 1) = if n % p == 0 then (p : Int) else 0 := by
    dsimp [F]
    cases hnp : (n % p == 0)
    · have hbf : (p % (p - 1 + 1) == 0 && n % (p - 1 + 1) == 0) = false := by
        rw [hp1, Nat.mod_self, hnp]; exact Eq.refl _
      rw [bool_cond_false hbf]; exact Eq.refl _
    · have hbt : (p % (p - 1 + 1) == 0 && n % (p - 1 + 1) == 0) = true := by
        rw [hp1, Nat.mod_self, hnp]; exact Eq.refl _
      have hp1' : (p - 1).succ = p := hp1
      rw [bool_cond_true hbt, hp1, Nat.div_self hp_pos, ← Int.natCast_succ (p - 1), hp1']
      change (p : Int) * 1 = if true = true then (p : Int) else 0
      rw [Int.mul_one]
      exact Eq.refl _
  rw [hfirst, hmid, Int.add_zero, hlast]
  cases (n % p == 0)
  · exact Eq.refl _
  · rw [Int.add_comm, ← Int.sub_eq_add_neg]; exact Eq.refl _

theorem ramanujanSum_orthogonality_zero_sum :
    (List.range 11).all (fun k => let q := k + 2; sumRange q (fun n => ramanujanSum q n) == 0) = true := by decide

theorem ramanujanSum_orthogonality_zero_sum_prop : ∀ q : Nat, 2 ≤ q → q ≤ 12 →
    sumRange q (fun n => ramanujanSum q n) = 0 := by
  intro q hq2 hq12
  have hk11 : q - 2 < 11 := by
    have := Nat.sub_le_sub_right hq12 2
    exact Nat.lt_succ_of_le this
  have hall := list_mem_of_all _ (List.range 11) ramanujanSum_orthogonality_zero_sum (q - 2) (mem_list_range hk11)
  have hadd : q - 2 + 2 = q := Nat.sub_add_cancel hq2
  dsimp at hall
  rw [hadd] at hall
  exact (int_beq_iff_eq _ 0).mp hall

theorem ramanujanSum_superchar_orthogonality_12 :
    ([1, 2, 3, 4, 6, 12] : List Nat).all (fun q =>
      ([1, 2, 3, 4, 6, 12] : List Nat).all (fun r =>
        sumRange 12 (fun n => ramanujanSum q n * ramanujanSum r n) ==
        (if q == r then 12 * (eulerTotient q : Int) else 0))) = true := by decide

theorem neg_ctrl_ramanujanSum_composite_4_fails_prime_rule :
    ramanujanSum 4 2 = -2 ∧ ramanujanSum 4 1 = 0 ∧ ¬ IsPrime 4 ∧ ramanujanSum 4 2 ≠ -1 := by
  refine ⟨by decide, by decide, ?_, by decide⟩
  intro ⟨_, hd⟩
  exact hd 2 (by decide) (by decide) (by decide)

theorem neg_ctrl_ramanujanSum_q1_nonzero_sum :
    sumRange 1 (fun n => ramanujanSum 1 n) = 1 ∧
    sumRange 1 (fun n => ramanujanSum 1 n) ≠ 0 := by decide

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 5: Continued Fractions, Euler–Wallis Identity, & Rogers–Ramanujan R(q)
-- ═══════════════════════════════════════════════════════════════════════════════

def cfStepInt (a b : Nat → Int) : Nat → Int × Int × Int × Int
  | 0 => (1, 0, b 0, 1)
  | k + 1 =>
    let st := cfStepInt a b k
    (st.2.2.1, st.2.2.2, b (k + 1) * st.2.2.1 + a (k + 1) * st.1,
     b (k + 1) * st.2.2.2 + a (k + 1) * st.2.1)

def cfP (a b : Nat → Int) (k : Nat) : Int := (cfStepInt a b k).2.2.1
def cfQ (a b : Nat → Int) (k : Nat) : Int := (cfStepInt a b k).2.2.2

def prodRange1 : Nat → (Nat → Int) → Int
  | 0, _ => 1
  | k + 1, a => prodRange1 k a * a (k + 1)

def altSign (k : Nat) : Int :=
  if k % 2 == 0 then 1 else -1

def cfStepFPS (a b : Nat → FPS) : Nat → FPS × FPS × FPS × FPS
  | 0 => (fpsOne, fpsZero, b 0, fpsOne)
  | k + 1 =>
    let st := cfStepFPS a b k
    (st.2.2.1, st.2.2.2,
     fpsAdd (fpsMul (b (k + 1)) st.2.2.1) (fpsMul (a (k + 1)) st.1),
     fpsAdd (fpsMul (b (k + 1)) st.2.2.2) (fpsMul (a (k + 1)) st.2.1))

def cfPFPS (a b : Nat → FPS) (k : Nat) : FPS := (cfStepFPS a b k).2.2.1
def cfQFPS (a b : Nat → FPS) (k : Nat) : FPS := (cfStepFPS a b k).2.2.2

def prodRange1FPS : Nat → (Nat → FPS) → FPS
  | 0, _ => fpsOne
  | k + 1, a => fpsMul (prodRange1FPS k a) (a (k + 1))

def fpsAltSign (k : Nat) : FPS :=
  fun n => if n == 0 then altSign k else 0

def fpsQPow (d : Nat) : FPS :=
  fun n => if n == d then 1 else 0

def rrA (k : Nat) : FPS :=
  if k == 1 then fpsOne else fun n => if n == k - 1 then 1 else 0

def rrB (k : Nat) : FPS :=
  if k == 0 then fpsZero else fpsOne

def qPochList (aCoeff : Int) (step startExp numTerms N : Nat) : List Int :=
  let one := if N == 0 then [] else 1 :: List.replicate (N - 1) 0
  (List.range numTerms).foldl (fun acc j =>
    polyMul acc (polyBinom aCoeff (startExp + j * step) N) N) one

def rrGList (N : Nat) : List Int :=
  (List.range N).foldl (fun acc n =>
    if n * n < N then
      polyAdd acc (polyShift (n * n) (polyInv (qPochList (-1) 1 1 n N) N) N) N
    else acc) (List.replicate N 0)

def rrHList (N : Nat) : List Int :=
  (List.range N).foldl (fun acc n =>
    if n * (n + 1) < N then
      polyAdd acc (polyShift (n * (n + 1)) (polyInv (qPochList (-1) 1 1 n N) N) N) N
    else acc) (List.replicate N 0)

def rrCFState (N : Nat) : Nat → List Int × List Int × List Int × List Int
  | 0 =>
    let one := if N == 0 then [] else 1 :: List.replicate (N - 1) 0
    let zero := List.replicate N 0
    (one, zero, zero, one)
  | k + 1 =>
    let st := rrCFState N k
    let pNext := polyAdd st.2.2.1 (polyShift k st.1 N) N
    let qNext := polyAdd st.2.2.2 (polyShift k st.2.1 N) N
    (st.2.2.1, st.2.2.2, pNext, qNext)

def rrCFPoly (kMax N : Nat) : List Int × List Int :=
  let st := rrCFState N kMax
  (st.2.2.1, st.2.2.2)

theorem altSign_succ (k : Nat) : -altSign k = altSign (k + 1) := by
  dsimp [altSign]
  have hk2 : k % 2 = 0 ∨ k % 2 = 1 := by
    have hlt := Nat.mod_lt k (by decide : 0 < 2)
    cases h : k % 2 with
    | zero => exact Or.inl (Eq.refl 0)
    | succ r =>
      rw [h] at hlt
      have hr0 : r = 0 := Nat.eq_zero_of_le_zero (Nat.le_of_lt_succ (Nat.lt_of_succ_lt_succ hlt))
      rw [hr0]; exact Or.inr (Eq.refl 1)
  cases hk2 with
  | inl h0 =>
    have h1 : (k + 1) % 2 = 1 := by rw [Nat.add_mod, h0]
    rw [h0, h1]; exact Eq.refl _
  | inr h1 =>
    have h0 : (k + 1) % 2 = 0 := by rw [Nat.add_mod, h1]
    rw [h1, h0]; exact Eq.refl _

theorem int_cf_alg_step (B A P1 Q1 P0 Q0 : Int) :
    (B * P1 + A * P0) * Q1 - P1 * (B * Q1 + A * Q0) = -(A * (P1 * Q0 - P0 * Q1)) := by
  rw [Int.add_mul, Int.mul_add, Int.mul_assoc B P1 Q1, ← Int.mul_assoc P1 B Q1,
      Int.mul_comm P1 B, Int.mul_assoc B P1 Q1,
      int_add_sub_cancel_mid (B * (P1 * Q1)) (A * P0 * Q1) (P1 * (A * Q0)),
      Int.mul_assoc A P0 Q1, Int.mul_comm P1 (A * Q0), Int.mul_assoc A Q0 P1,
      Int.mul_comm Q0 P1, ← Int.mul_sub, ← Int.neg_sub (P1 * Q0) (P0 * Q1), Int.mul_neg]

theorem euler_wallis_det_int_all_k : ∀ (a b : Nat → Int) (k : Nat),
    cfP a b (k + 1) * cfQ a b k - cfP a b k * cfQ a b (k + 1) = altSign k * prodRange1 (k + 1) a
  | a, b, 0 => by
    change (b 1 * b 0 + a 1 * 1) * 1 - b 0 * (b 1 * 1 + a 1 * 0) = 1 * (1 * a 1)
    rw [Int.mul_one, Int.mul_zero, Int.add_zero, Int.mul_one, Int.mul_one,
        Int.mul_comm (b 0) (b 1), Int.add_comm (b 1 * b 0) (a 1), Int.add_sub_cancel,
        Int.one_mul, Int.one_mul]
  | a, b, k + 1 => by
    have hih := euler_wallis_det_int_all_k a b k
    change (b (k + 2) * cfP a b (k + 1) + a (k + 2) * cfP a b k) * cfQ a b (k + 1) -
        cfP a b (k + 1) * (b (k + 2) * cfQ a b (k + 1) + a (k + 2) * cfQ a b k) =
      altSign (k + 1) * (prodRange1 (k + 1) a * a (k + 2))
    rw [int_cf_alg_step, hih, ← altSign_succ k,
        Int.mul_comm (a (k + 2)) (altSign k * prodRange1 (k + 1) a),
        Int.mul_assoc (altSign k) (prodRange1 (k + 1) a) (a (k + 2)),
        Int.neg_mul, ← Int.neg_mul]

theorem fps_cf_alg_step (B A P1 Q1 P0 Q0 : FPS) :
    FPSEq
      (fpsSub (fpsMul (fpsAdd (fpsMul B P1) (fpsMul A P0)) Q1)
              (fpsMul P1 (fpsAdd (fpsMul B Q1) (fpsMul A Q0))))
      (fpsMul (fpsNeg A) (fpsSub (fpsMul P1 Q0) (fpsMul P0 Q1))) := by
  intro n
  have h1 := fpsMul_add_left (fpsMul B P1) (fpsMul A P0) Q1 n
  have h2 := fpsMul_add_right P1 (fpsMul B Q1) (fpsMul A Q0) n
  have hbp : fpsMul (fpsMul B P1) Q1 n = fpsMul P1 (fpsMul B Q1) n := by
    have ha : FPSEq (fpsMul (fpsMul B P1) Q1) (fpsMul P1 (fpsMul B Q1)) :=
      FPSEq.trans (fpsMul_congr (fpsMul_comm B P1) (FPSEq.refl Q1)) (fpsMul_assoc P1 B Q1)
    exact ha n
  have ha0 : fpsMul (fpsMul A P0) Q1 n = fpsMul A (fpsMul P0 Q1) n :=
    fpsMul_assoc A P0 Q1 n
  have ha1 : fpsMul P1 (fpsMul A Q0) n = fpsMul A (fpsMul P1 Q0) n := by
    have ha : FPSEq (fpsMul P1 (fpsMul A Q0)) (fpsMul A (fpsMul P1 Q0)) :=
      FPSEq.trans (fpsMul_assoc P1 A Q0).symm
        (FPSEq.trans (fpsMul_congr (fpsMul_comm P1 A) (FPSEq.refl Q0)) (fpsMul_assoc A P1 Q0))
    exact ha n
  have hsub := fpsMul_sub_right A (fpsMul P1 Q0) (fpsMul P0 Q1) n
  have hneg := fpsMul_neg_left A (fpsSub (fpsMul P1 Q0) (fpsMul P0 Q1)) n
  dsimp [fpsSub, fpsAdd, fpsNeg] at h1 h2 hsub hneg ⊢
  rw [h1, h2, hbp, ha0, ha1, hneg, hsub, int_add_sub_cancel_mid, Int.neg_sub]

theorem fpsAltSign_mul_neg (k : Nat) (f : FPS) :
    FPSEq (fpsNeg (fpsMul (fpsAltSign k) f)) (fpsMul (fpsAltSign (k + 1)) f) := by
  intro n
  have hsum : ∀ (g : FPS), fpsMul (fpsAltSign k) g n = altSign k * g n := by
    intro g
    change sumRange (n + 1) (fun j => fpsAltSign k j * g (n - j)) = altSign k * g n
    rw [sumRange_succ_shift]
    have h0 : fpsAltSign k 0 * g (n - 0) = altSign k * g n := by
      rw [Nat.sub_zero]; exact Eq.refl _
    have hr : sumRange n (fun j => fpsAltSign k (j + 1) * g (n - (j + 1))) = 0 := by
      apply sumRange_zero_of
      intro j _
      dsimp [fpsAltSign]
      exact Int.zero_mul _
    rw [h0, hr, Int.add_zero]
  have hsum1 : fpsMul (fpsAltSign (k + 1)) f n = altSign (k + 1) * f n := by
    change sumRange (n + 1) (fun j => fpsAltSign (k + 1) j * f (n - j)) = altSign (k + 1) * f n
    rw [sumRange_succ_shift]
    have h0 : fpsAltSign (k + 1) 0 * f (n - 0) = altSign (k + 1) * f n := by
      rw [Nat.sub_zero]; exact Eq.refl _
    have hr : sumRange n (fun j => fpsAltSign (k + 1) (j + 1) * f (n - (j + 1))) = 0 := by
      apply sumRange_zero_of
      intro j _
      dsimp [fpsAltSign]
      exact Int.zero_mul _
    rw [h0, hr, Int.add_zero]
  dsimp [fpsNeg]
  rw [hsum f, hsum1, ← Int.neg_mul, altSign_succ k]

theorem euler_wallis_det_fps_all_k : ∀ (a b : Nat → FPS) (k : Nat),
    FPSEq
      (fpsSub (fpsMul (cfPFPS a b (k + 1)) (cfQFPS a b k))
              (fpsMul (cfPFPS a b k) (cfQFPS a b (k + 1))))
      (fpsMul (fpsAltSign k) (prodRange1FPS (k + 1) a))
  | a, b, 0 => by
    have hP1 : FPSEq (cfPFPS a b 1) (fpsAdd (fpsMul (b 1) (b 0)) (a 1)) :=
      fpsAdd_congr (FPSEq.refl _) (fpsMul_one_right (a 1))
    have hQ1 : FPSEq (cfQFPS a b 1) (b 1) :=
      FPSEq.trans (fpsAdd_congr (fpsMul_one_right (b 1)) (fpsMul_zero_right (a 1)))
        (fpsAdd_zero_right (b 1))
    have hL : FPSEq
        (fpsSub (fpsMul (cfPFPS a b 1) (cfQFPS a b 0)) (fpsMul (cfPFPS a b 0) (cfQFPS a b 1)))
        (fpsSub (fpsAdd (fpsMul (b 1) (b 0)) (a 1)) (fpsMul (b 0) (b 1))) :=
      fpsSub_congr (FPSEq.trans (fpsMul_congr hP1 (FPSEq.refl fpsOne)) (fpsMul_one_right _))
        (fpsMul_congr (FPSEq.refl (b 0)) hQ1)
    have hcancel : FPSEq (fpsSub (fpsAdd (fpsMul (b 1) (b 0)) (a 1)) (fpsMul (b 0) (b 1))) (a 1) := by
      intro n
      dsimp [fpsSub, fpsAdd]
      rw [fpsMul_comm (b 0) (b 1) n, Int.add_comm (fpsMul (b 1) (b 0) n) (a 1 n), Int.add_sub_cancel]
    have hR : FPSEq (fpsMul (fpsAltSign 0) (prodRange1FPS 1 a)) (a 1) :=
      FPSEq.trans (fpsMul_one_left (prodRange1FPS 1 a)) (fpsMul_one_left (a 1))
    exact FPSEq.trans hL (FPSEq.trans hcancel hR.symm)
  | a, b, k + 1 => by
    have hih := euler_wallis_det_fps_all_k a b k
    have hstep := fps_cf_alg_step (b (k + 2)) (a (k + 2))
      (cfPFPS a b (k + 1)) (cfQFPS a b (k + 1)) (cfPFPS a b k) (cfQFPS a b k)
    have hmul_neg := FPSEq.trans (fpsMul_neg_left (a (k + 2)) _)
      (fpsNeg_congr (fpsMul_congr (FPSEq.refl (a (k + 2))) hih))
    have hswap : FPSEq
        (fpsMul (a (k + 2)) (fpsMul (fpsAltSign k) (prodRange1FPS (k + 1) a)))
        (fpsMul (fpsAltSign k) (fpsMul (prodRange1FPS (k + 1) a) (a (k + 2)))) :=
      FPSEq.trans (fpsMul_assoc (a (k + 2)) (fpsAltSign k) (prodRange1FPS (k + 1) a)).symm
        (FPSEq.trans (fpsMul_congr (fpsMul_comm (a (k + 2)) (fpsAltSign k)) (FPSEq.refl _))
          (FPSEq.trans (fpsMul_assoc (fpsAltSign k) (a (k + 2)) (prodRange1FPS (k + 1) a))
            (fpsMul_congr (FPSEq.refl (fpsAltSign k)) (fpsMul_comm (a (k + 2)) (prodRange1FPS (k + 1) a)))))
    have hfin := FPSEq.trans (fpsNeg_congr hswap) (fpsAltSign_mul_neg k (prodRange1FPS (k + 2) a))
    exact FPSEq.trans hstep (FPSEq.trans hmul_neg hfin)

theorem fpsQPow_mul (d1 d2 : Nat) :
    FPSEq (fpsMul (fpsQPow d1) (fpsQPow d2)) (fpsQPow (d1 + d2)) := by
  intro n
  by_cases h1 : d1 ≤ n
  · change sumRange (n + 1) (fun k => fpsQPow d1 k * fpsQPow d2 (n - k)) = fpsQPow (d1 + d2) n
    rw [sumRange_split_at n d1 h1]
    have hpre : sumRange d1 (fun k => fpsQPow d1 k * fpsQPow d2 (n - k)) = 0 := by
      apply sumRange_zero_of
      intro k hk
      dsimp [fpsQPow]
      rw [bool_cond_false (nat_beq_false_of_ne (Nat.ne_of_lt hk)), Int.zero_mul]
    have hpost : sumRange (n - d1) (fun r => fpsQPow d1 (d1 + 1 + r) * fpsQPow d2 (n - (d1 + 1 + r))) = 0 := by
      apply sumRange_zero_of
      intro r _
      dsimp [fpsQPow]
      have hgt : d1 < d1 + 1 + r := by
        rw [Nat.add_assoc]; exact Nat.lt_add_of_pos_right (Nat.add_comm 1 r ▸ Nat.zero_lt_succ r)
      rw [bool_cond_false (nat_beq_false_of_ne (Nat.ne_of_gt hgt)), Int.zero_mul]
    have hat : fpsQPow d1 d1 = 1 := by dsimp [fpsQPow]; rw [nat_beq_self]; exact Eq.refl _
    rw [hpre, hpost, Int.zero_add, Int.add_zero, hat, Int.one_mul]
    dsimp [fpsQPow]
    by_cases heq : n = d1 + d2
    · have hsub : n - d1 = d2 := by rw [heq, Nat.add_sub_cancel_left]
      rw [hsub, heq, nat_beq_self, nat_beq_self]
    · have hsub_ne : n - d1 ≠ d2 := by
        intro h
        exact heq (by rw [← h, Nat.add_sub_of_le h1])
      rw [nat_beq_false_of_ne hsub_ne, nat_beq_false_of_ne heq]
  · have hlt : n < d1 := Nat.lt_of_not_le h1
    change sumRange (n + 1) (fun k => fpsQPow d1 k * fpsQPow d2 (n - k)) = fpsQPow (d1 + d2) n
    have h0 : sumRange (n + 1) (fun k => fpsQPow d1 k * fpsQPow d2 (n - k)) = 0 := by
      apply sumRange_zero_of
      intro k hk
      dsimp [fpsQPow]
      have hkd : k < d1 := Nat.lt_of_le_of_lt (Nat.le_of_lt_succ hk) hlt
      rw [bool_cond_false (nat_beq_false_of_ne (Nat.ne_of_lt hkd)), Int.zero_mul]
    have hne : n ≠ d1 + d2 := Nat.ne_of_lt (Nat.lt_of_lt_of_le hlt (Nat.le_add_right d1 d2))
    rw [h0]
    dsimp [fpsQPow]
    rw [bool_cond_false (nat_beq_false_of_ne hne)]

theorem rrA_succ : ∀ k : Nat, FPSEq (rrA (k + 1)) (fpsQPow k)
  | 0 => FPSEq.refl fpsOne
  | m + 1 => by
    intro n
    dsimp [rrA, fpsQPow]

theorem prodRange1FPS_rrA : ∀ k : Nat,
    FPSEq (prodRange1FPS (k + 1) rrA) (fpsQPow (k * (k + 1) / 2))
  | 0 => FPSEq.trans (fpsMul_one_left (rrA 1)) (rrA_succ 0)
  | k + 1 => by
    have hih := prodRange1FPS_rrA k
    have hstep := fpsMul_congr hih (rrA_succ (k + 1))
    have hmul := fpsQPow_mul (k * (k + 1) / 2) (k + 1)
    have hidx : k * (k + 1) / 2 + (k + 1) = (k + 1) * (k + 2) / 2 := by
      apply Nat.eq_of_mul_eq_mul_left (by decide : 0 < 2)
      rw [Nat.mul_add, nat_two_dvd_mul_succ k, nat_two_dvd_mul_succ (k + 1),
          Nat.mul_add (k + 1) k 2, Nat.mul_comm (k + 1) k, Nat.mul_comm (k + 1) 2]
    rw [hidx] at hmul
    exact FPSEq.trans hstep hmul

theorem rr_cf_convergent_diff_vanishes_all_k : ∀ (k m : Nat),
    m < k * (k + 1) / 2 →
    (fpsSub (fpsMul (cfPFPS rrA rrB (k + 1)) (cfQFPS rrA rrB k))
            (fpsMul (cfPFPS rrA rrB k) (cfQFPS rrA rrB (k + 1)))) m = 0 := by
  intro k m hm
  rw [euler_wallis_det_fps_all_k rrA rrB k m,
      fpsMul_congr (FPSEq.refl (fpsAltSign k)) (prodRange1FPS_rrA k) m]
  change sumRange (m + 1) (fun j => fpsAltSign k j * fpsQPow (k * (k + 1) / 2) (m - j)) = 0
  apply sumRange_zero_of
  intro j _
  have hlt : m - j < k * (k + 1) / 2 := Nat.lt_of_le_of_lt (Nat.sub_le m j) hm
  dsimp [fpsQPow]
  rw [bool_cond_false (nat_beq_false_of_ne (Nat.ne_of_lt hlt)), Int.mul_zero]

theorem rr_G_exact_16 :
    rrGList 16 = [1, 1, 1, 1, 2, 2, 3, 3, 4, 5, 6, 7, 9, 10, 12, 14] ∧
    rrGList 16 = polyInv (polyMul (qPochList (-1) 5 1 16 16) (qPochList (-1) 5 4 16 16) 16) 16 := by decide

theorem rr_H_exact_16 :
    rrHList 16 = [1, 0, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 6, 6, 8, 9] ∧
    rrHList 16 = polyInv (polyMul (qPochList (-1) 5 2 16 16) (qPochList (-1) 5 3 16 16) 16) 16 := by decide

theorem rr_cf_6_matches_H_over_G_16 :
    let pq := rrCFPoly 6 16
    polyMul pq.1 (polyInv pq.2 16) 16 = polyMul (rrHList 16) (polyInv (rrGList 16) 16) 16 ∧
    polyMul pq.1 (polyInv pq.2 16) 16 = [1, -1, 1, 0, -1, 1, -1, 1, 0, -1, 2, -3, 2, 0, -2, 4] := by decide

theorem neg_ctrl_rr_unshifted_eta_ratio_fails :
    (etaCoeffs { factors := [(1, -1), (2, 1), (3, 1), (4, -1)] } 16).getD 1 0 = 1 ∧
    (polyMul (rrHList 16) (polyInv (rrGList 16) 16) 16).getD 1 0 = -1 ∧
    etaCoeffs { factors := [(1, -1), (2, 1), (3, 1), (4, -1)] } 16 ≠
      polyMul (rrHList 16) (polyInv (rrGList 16) 16) 16 := by decide

theorem neg_ctrl_euler_wallis_missing_sign_fails :
    cfP (fun _ => 1) (fun _ => 1) 2 * cfQ (fun _ => 1) (fun _ => 1) 1 -
      cfP (fun _ => 1) (fun _ => 1) 1 * cfQ (fun _ => 1) (fun _ => 1) 2 = -1 ∧
    (-1 : Int) ≠ prodRange1 2 (fun _ => 1) := by decide

theorem neg_ctrl_rr_G_ne_H :
    (rrGList 16).getD 1 0 = 1 ∧ (rrHList 16).getD 1 0 = 0 ∧ rrGList 16 ≠ rrHList 16 := by decide

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 6: 3rd-Order Mock Theta Functions (Last Letter 1920)
-- ═══════════════════════════════════════════════════════════════════════════════

def mock3FList (N : Nat) : List Int :=
  (List.range N).foldl (fun acc n =>
    if n * n < N then
      let p := qPochList 1 1 1 n N
      polyAdd acc (polyShift (n * n) (polyInv (polyMul p p N) N) N) N
    else acc) (List.replicate N 0)

def mock3PhiList (N : Nat) : List Int :=
  (List.range N).foldl (fun acc n =>
    if n * n < N then
      polyAdd acc (polyShift (n * n) (polyInv (qPochList 1 2 2 n N) N) N) N
    else acc) (List.replicate N 0)

def mock3PsiList (N : Nat) : List Int :=
  (List.range N).foldl (fun acc n =>
    if 1 ≤ n && n * n < N then
      polyAdd acc (polyShift (n * n) (polyInv (qPochList (-1) 2 1 n N) N) N) N
    else acc) (List.replicate N 0)

def seriesNegList (a : List Int) : List Int :=
  (List.range a.length).map (fun i => if i % 2 == 0 then a.getD i 0 else -(a.getD i 0))

def qPochFPS (aCoeff : Int) (step startExp : Nat) : Nat → FPS
  | 0 => fpsOne
  | j + 1 => fpsMul (qPochFPS aCoeff step startExp j)
      (fun n => if n == 0 then 1 else if startExp + j * step > 0 && n == startExp + j * step then aCoeff else 0)

def qShiftSeries (s : Nat) (f : FPS) : FPS :=
  fun n => if n ≥ s then f (n - s) else 0

def mock3FTerm (k : Nat) : FPS :=
  let p := qPochFPS 1 1 1 k
  qShiftSeries (k * k) (fpsInv (fpsMul p p))

def mock3FPartial : Nat → FPS
  | 0 => mock3FTerm 0
  | M + 1 => fpsAdd (mock3FPartial M) (mock3FTerm (M + 1))

def mock3F_FPS (n : Nat) : Int := mock3FPartial n n

def mock3PsiTerm (k : Nat) : FPS :=
  qShiftSeries (k * k) (fpsInv (qPochFPS (-1) 2 1 k))

def mock3PsiPartial : Nat → FPS
  | 0 => fpsZero
  | M + 1 => fpsAdd (mock3PsiPartial M) (mock3PsiTerm (M + 1))

def mock3Psi_FPS (n : Nat) : Int := mock3PsiPartial n n

theorem mock3_f_exact_16 :
    mock3FList 16 = [1, 1, -2, 3, -3, 3, -5, 7, -6, 6, -10, 12, -11, 13, -17, 20] := by decide

theorem mock3_phi_exact_16 :
    mock3PhiList 16 = [1, 1, 0, -1, 1, 1, -1, -1, 0, 2, 0, -2, 1, 1, -1, -2] := by decide

theorem mock3_psi_exact_16 :
    mock3PsiList 16 = [0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 5, 6, 7, 8, 9] := by decide

theorem mock3_f_plus_4psi_neg_eq_eta_16 :
    polyAdd (mock3FList 16) ((seriesNegList (mock3PsiList 16)).map (4 * ·)) 16 =
    etaCoeffs { factors := [(1, 3), (2, -2)] } 16 := by decide

theorem mock3_2phi_neg_minus_f_eq_eta_16 :
    polySub ((seriesNegList (mock3PhiList 16)).map (2 * ·)) (mock3FList 16) 16 =
    etaCoeffs { factors := [(1, 3), (2, -2)] } 16 := by decide

theorem mock3_phi_minus_f_neg_eq_2psi_16 :
    polySub (mock3PhiList 16) (seriesNegList (mock3FList 16)) 16 =
    (mock3PsiList 16).map (2 * ·) := by decide

theorem mock3_psi_const_zero_all_M : ∀ M : Nat, mock3PsiPartial M 0 = 0
  | 0 => Eq.refl _
  | M + 1 => by
    change mock3PsiPartial M 0 + mock3PsiTerm (M + 1) 0 = 0
    rw [mock3_psi_const_zero_all_M M, Int.zero_add]
    dsimp [mock3PsiTerm, qShiftSeries]

theorem mock3_f_stabilizes_add : ∀ n d : Nat, mock3FPartial (n + d) n = mock3F_FPS n
  | _, 0 => Eq.refl _
  | n, d + 1 => by
    have hadd : n + (d + 1) = (n + d) + 1 := (Nat.add_assoc n d 1).symm
    rw [hadd]
    change mock3FPartial (n + d) n + mock3FTerm (n + d + 1) n = mock3F_FPS n
    have hlt : n < (n + d + 1) * (n + d + 1) := by
      have h1 : n + 1 ≤ n + d + 1 := Nat.succ_le_succ (Nat.le_add_right n d)
      have h2 : n < (n + 1) * (n + 1) := by
        rw [Nat.add_mul, Nat.mul_add, Nat.one_mul, Nat.mul_one]
        change n < n * n + n + n + 1
        exact Nat.lt_succ_of_le (Nat.le_add_left n (n * n + n))
      exact Nat.lt_of_lt_of_le h2 (Nat.mul_le_mul h1 h1)
    have ht0 : mock3FTerm (n + d + 1) n = 0 := by
      dsimp [mock3FTerm, qShiftSeries]
      rw [if_neg (Nat.not_le_of_gt hlt)]
    rw [ht0, Int.add_zero]
    exact mock3_f_stabilizes_add n d

theorem mock3_f_stabilizes_all_n : ∀ M n : Nat, n ≤ M → mock3FPartial M n = mock3F_FPS n := by
  intro M n hn
  have hM : M = n + (M - n) := (Nat.add_sub_of_le hn).symm
  rw [hM]
  exact mock3_f_stabilizes_add n (M - n)

theorem mock3_psi_stabilizes_add : ∀ n d : Nat, mock3PsiPartial (n + d) n = mock3Psi_FPS n
  | _, 0 => Eq.refl _
  | n, d + 1 => by
    have hadd : n + (d + 1) = (n + d) + 1 := (Nat.add_assoc n d 1).symm
    rw [hadd]
    change mock3PsiPartial (n + d) n + mock3PsiTerm (n + d + 1) n = mock3Psi_FPS n
    have hlt : n < (n + d + 1) * (n + d + 1) := by
      have h1 : n + 1 ≤ n + d + 1 := Nat.succ_le_succ (Nat.le_add_right n d)
      have h2 : n < (n + 1) * (n + 1) := by
        rw [Nat.add_mul, Nat.mul_add, Nat.one_mul, Nat.mul_one]
        change n < n * n + n + n + 1
        exact Nat.lt_succ_of_le (Nat.le_add_left n (n * n + n))
      exact Nat.lt_of_lt_of_le h2 (Nat.mul_le_mul h1 h1)
    have ht0 : mock3PsiTerm (n + d + 1) n = 0 := by
      dsimp [mock3PsiTerm, qShiftSeries]
      rw [if_neg (Nat.not_le_of_gt hlt)]
    rw [ht0, Int.add_zero]
    exact mock3_psi_stabilizes_add n d

theorem mock3_psi_stabilizes_all_n : ∀ M n : Nat, n ≤ M → mock3PsiPartial M n = mock3Psi_FPS n := by
  intro M n hn
  have hM : M = n + (M - n) := (Nat.add_sub_of_le hn).symm
  rw [hM]
  exact mock3_psi_stabilizes_add n (M - n)

theorem neg_ctrl_mock3_psi_legacy_stub_q0_false :
    mock3Psi_FPS 0 = 0 ∧ (mock3PsiList 16).getD 0 0 ≠ 1 := by decide

theorem neg_ctrl_mock3_f_not_eta_shadow :
    (mock3FList 16).getD 1 0 = 1 ∧
    (etaCoeffs { factors := [(1, 3), (2, -2)] } 16).getD 1 0 = -3 ∧
    mock3FList 16 ≠ etaCoeffs { factors := [(1, 3), (2, -2)] } 16 := by decide

theorem neg_ctrl_mock3_f_plus_2psi_neg_fails :
    polyAdd (mock3FList 16) ((seriesNegList (mock3PsiList 16)).map (2 * ·)) 16 ≠
    etaCoeffs { factors := [(1, 3), (2, -2)] } 16 := by decide

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 7: Highly Composite Numbers (1915) & Minimal Taxicab 1729
-- ═══════════════════════════════════════════════════════════════════════════════

def checkNoQuadBelow13 : Bool :=
  (List.range 13).all fun a =>
    if a == 0 then true
    else (List.range 13).all fun b =>
      if !(a < b) then true
      else (List.range 13).all fun c =>
        if !(a < c && c < b) then true
        else (List.range 13).all fun d =>
          if c ≤ d && d < b then
            (a ^ 3 + b ^ 3 != c ^ 3 + d ^ 3) || (1729 ≤ a ^ 3 + b ^ 3)
          else true

def cubeSumWaysB (n a b acc : Nat) : Nat → Nat
  | 0 => acc
  | fuel + 1 =>
    let s := a ^ 3 + b ^ 3
    if s > n then acc
    else cubeSumWaysB n a (b + 1) (if s == n then acc + 1 else acc) fuel

def cubeSumWaysA (n a acc : Nat) : Nat → Nat
  | 0 => acc
  | fuel + 1 =>
    if 2 * a ^ 3 > n then acc
    else cubeSumWaysA n (a + 1) (cubeSumWaysB n a a acc (n + 2)) fuel

def cubeSumWays (n : Nat) : Nat :=
  if n == 0 then 0 else cubeSumWaysA n 1 0 (n + 2)

def numDivisors (n : Nat) : Nat :=
  if n == 0 then 0
  else (List.range n).foldl (fun acc d0 => if n % (d0 + 1) == 0 then acc + 1 else acc) 0

def isHCN (n : Nat) : Bool :=
  n > 0 && (List.range n).all (fun m => if m == 0 then true else numDivisors m < numDivisors n)

def IsHighlyComposite (n : Nat) : Prop :=
  0 < n ∧ ∀ m : Nat, 0 < m → m < n → numDivisors m < numDivisors n

theorem taxicab_1729_witness :
    1 ^ 3 + 12 ^ 3 = 1729 ∧ 9 ^ 3 + 10 ^ 3 = 1729 ∧ (1 : Nat) ≠ 9 ∧ cubeSumWays 1729 = 2 := by decide

theorem taxicab_quad_check_13 : checkNoQuadBelow13 = true := by decide

theorem taxicab_ordered_below_13 : ∀ a b c d : Nat,
    1 ≤ a → a < c → c ≤ d → d < b → b < 13 → a ^ 3 + b ^ 3 = c ^ 3 + d ^ 3 →
    1729 ≤ a ^ 3 + b ^ 3 := by
  intro a b c d ha hac hcd hdb hb13 heq
  have ha13 : a < 13 := Nat.lt_trans (Nat.lt_trans hac (Nat.lt_of_le_of_lt hcd hdb)) hb13
  have hc13 : c < 13 := Nat.lt_trans (Nat.lt_of_le_of_lt hcd hdb) hb13
  have hd13 : d < 13 := Nat.lt_trans hdb hb13
  have ha0 : (a == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt ha)
  have hab : a < b := Nat.lt_trans hac (Nat.lt_of_le_of_lt hcd hdb)
  have hcb : c < b := Nat.lt_of_le_of_lt hcd hdb
  have h1 := list_mem_of_all _ (List.range 13) taxicab_quad_check_13 a (mem_list_range ha13)
  rw [bool_cond_false ha0] at h1
  have h2 := list_mem_of_all _ (List.range 13) h1 b (mem_list_range hb13)
  have hnab : (!decide (a < b)) = false := by
    rw [decide_eq_true hab]; exact Eq.refl _
  rw [bool_cond_false hnab] at h2
  have h3 := list_mem_of_all _ (List.range 13) h2 c (mem_list_range hc13)
  have hnacb : (!(decide (a < c) && decide (c < b))) = false := by
    rw [decide_eq_true hac, decide_eq_true hcb]; exact Eq.refl _
  rw [bool_cond_false hnacb] at h3
  have h4 := list_mem_of_all _ (List.range 13) h3 d (mem_list_range hd13)
  have hcdb : (c ≤ d && d < b) = true := by
    change (decide (c ≤ d) && decide (d < b)) = true
    rw [decide_eq_true hcd, decide_eq_true hdb]; exact Eq.refl _
  rw [bool_cond_true hcdb] at h4
  have hne : (a ^ 3 + b ^ 3 != c ^ 3 + d ^ 3) = false := by
    rw [heq]
    change (!(c ^ 3 + d ^ 3 == c ^ 3 + d ^ 3)) = false
    rw [nat_beq_self]; exact Eq.refl _
  rw [hne] at h4
  exact of_decide_eq_true h4

theorem taxicab_ordered_all : ∀ a b c d : Nat,
    1 ≤ a → a < c → c ≤ d → a ^ 3 + b ^ 3 = c ^ 3 + d ^ 3 → 1729 ≤ a ^ 3 + b ^ 3 := by
  intro a b c d ha hac hcd heq
  by_cases hb13 : b < 13
  · have hdb : d < b := by
      by_cases hbd : b ≤ d
      · have hac3 : a ^ 3 < c ^ 3 := Nat.pow_lt_pow_left hac (by decide : 3 ≠ 0)
        have hbd3 : b ^ 3 ≤ d ^ 3 := Nat.pow_le_pow_left hbd 3
        have hlt : a ^ 3 + b ^ 3 < c ^ 3 + d ^ 3 :=
          Nat.lt_of_lt_of_le (Nat.add_lt_add_right hac3 (b ^ 3)) (Nat.add_le_add_left hbd3 (c ^ 3))
        rw [heq] at hlt
        exact absurd hlt (Nat.lt_irrefl _)
      · exact Nat.lt_of_not_le hbd
    exact taxicab_ordered_below_13 a b c d ha hac hcd hdb hb13 heq
  · have h13b : 13 ≤ b := Nat.le_of_not_lt hb13
    have hpow : 13 ^ 3 ≤ b ^ 3 := Nat.pow_le_pow_left h13b 3
    exact Nat.le_trans (by decide : 1729 ≤ 13 ^ 3) (Nat.le_trans hpow (Nat.le_add_left (b ^ 3) (a ^ 3)))

theorem taxicab_1729_minimal_all : ∀ a b c d : Nat,
    1 ≤ a → a ≤ b → 1 ≤ c → c ≤ d → a ≠ c → a ^ 3 + b ^ 3 = c ^ 3 + d ^ 3 →
    1729 ≤ a ^ 3 + b ^ 3 := by
  intro a b c d ha _ hc hcd hne heq
  cases Nat.lt_or_gt_of_ne hne with
  | inl hac => exact taxicab_ordered_all a b c d ha hac hcd heq
  | inr hca =>
    rw [heq]
    exact taxicab_ordered_all c d a b hc hca (by assumption) heq.symm

theorem isHCN_sound : ∀ n : Nat, isHCN n = true → IsHighlyComposite n := by
  intro n hn
  dsimp [isHCN] at hn
  cases hpos : decide (n > 0)
  · change (decide (n > 0) && _) = true at hn; rw [hpos] at hn; cases hn
  · change (decide (n > 0) && _) = true at hn; rw [hpos] at hn
    refine ⟨of_decide_eq_true hpos, fun m hm0 hmn => ?_⟩
    have hm := list_mem_of_all _ (List.range n) hn m (mem_list_range hmn)
    have hm0' : (m == 0) = false := nat_beq_false_of_ne (Nat.ne_of_gt hm0)
    rw [bool_cond_false hm0'] at hm
    exact of_decide_eq_true hm

theorem hcn_first_10_verified :
    ([1, 2, 4, 6, 12, 24, 36, 48, 60, 120] : List Nat).all isHCN = true := by decide

theorem hcn_first_10_all_IsHighlyComposite :
    ∀ n : Nat, n ∈ ([1, 2, 4, 6, 12, 24, 36, 48, 60, 120] : List Nat) → IsHighlyComposite n := by
  intro n hn
  exact isHCN_sound n (list_mem_of_all isHCN _ hcn_first_10_verified n hn)

theorem taxicab_1728_below_13_check :
    (List.range 13).all (fun a => (List.range 13).all (fun b =>
      if 1 ≤ a && a ≤ b then a ^ 3 + b ^ 3 != 1728 else true)) = true := by decide

theorem neg_ctrl_taxicab_1728_no_pos_cube_sum :
    cubeSumWays 1728 = 0 ∧ (∀ a b : Nat, 1 ≤ a → a ≤ b → a ^ 3 + b ^ 3 ≠ 1728) := by
  refine ⟨by decide, fun a b ha hab => ?_⟩
  by_cases hb13 : b < 13
  · have ha13 : a < 13 := Nat.lt_of_le_of_lt hab hb13
    have h1 := list_mem_of_all _ (List.range 13) taxicab_1728_below_13_check a (mem_list_range ha13)
    have h2 := list_mem_of_all _ (List.range 13) h1 b (mem_list_range hb13)
    have hcond : (1 ≤ a && a ≤ b) = true := by
      change (decide (1 ≤ a) && decide (a ≤ b)) = true
      rw [decide_eq_true ha, decide_eq_true hab]; exact Eq.refl _
    rw [bool_cond_true hcond] at h2
    exact fun heq => by rw [heq] at h2; cases h2
  · have hpow : 13 ^ 3 ≤ b ^ 3 := Nat.pow_le_pow_left (Nat.le_of_not_lt hb13) 3
    have hge : 1729 ≤ a ^ 3 + b ^ 3 :=
      Nat.le_trans (by decide : 1729 ≤ 13 ^ 3) (Nat.le_trans hpow (Nat.le_add_left (b ^ 3) (a ^ 3)))
    exact Nat.ne_of_gt hge

theorem neg_ctrl_hcn_18_not_hcn :
    isHCN 18 = false ∧ numDivisors 12 = 6 ∧ numDivisors 18 = 6 ∧ ¬ IsHighlyComposite 18 := by
  refine ⟨by decide, by decide, by decide, ?_⟩
  intro ⟨_, h⟩
  exact absurd (h 12 (by decide) (by decide)) (by decide)

theorem neg_ctrl_hcn_100_not_hcn :
    isHCN 100 = false ∧ numDivisors 60 = 12 ∧ numDivisors 100 = 9 ∧ ¬ IsHighlyComposite 100 := by
  refine ⟨by decide, by decide, by decide, ?_⟩
  intro ⟨_, h⟩
  exact absurd (h 60 (by decide) (by decide)) (by decide)

-- ═══════════════════════════════════════════════════════════════════════════════
-- Domain 8: Ramanujan's 1914 Series for 1/π & Universal Convergence Rate
-- ═══════════════════════════════════════════════════════════════════════════════

def natFact : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * natFact n

def ramanujanPiNum (k : Nat) : Nat :=
  natFact (4 * k) * (1103 + 26390 * k)

def ramanujanPiDen (k : Nat) : Nat :=
  (natFact k) ^ 4 * (396 ^ (4 * k))

def ramanujanSumRaw : Nat → Nat → Int × Nat
  | 0, c0 => ratNorm (c0 : Int) 1
  | k + 1, c0 =>
    let prev := ramanujanSumRaw k c0
    let termNum : Int := ((natFact (4 * (k + 1)) * (c0 + 26390 * (k + 1)) : Nat) : Int)
    let termDen : Nat := ramanujanPiDen (k + 1)
    ratAdd prev (ratNorm termNum termDen)

def ramanujanS (K : Nat) : Int × Nat :=
  ratMul (1, 9801) (ramanujanSumRaw K 1103)

def ramanujanS1Pert (c0 : Nat) : Int × Nat :=
  ratMul (1, 9801) (ramanujanSumRaw 1 c0)

def arctanPartialAux (invM : Nat) : Nat → Int × Nat → Int × Nat
  | 0, acc => acc
  | j + 1, acc =>
    let acc' := arctanPartialAux invM j acc
    let den := (2 * j + 1) * (invM ^ (2 * j + 1))
    let sgn : Int := if j % 2 == 0 then 1 else -1
    ratAdd acc' (ratNorm sgn den)

def arctanPartial (invM terms : Nat) : Int × Nat :=
  arctanPartialAux invM terms (0, 1)

def machinPi15Lo : Int × Nat :=
  ratMul (4, 1) (ratSub (ratMul (4, 1) (arctanPartial 5 12)) (arctanPartial 239 3))

def machinPi15Hi : Int × Nat :=
  ratMul (4, 1) (ratSub (ratMul (4, 1) (arctanPartial 5 13)) (arctanPartial 239 4))

def piSqBracket (S lo hi : Int × Nat) : Prop :=
  0 < S.1 ∧ 0 < lo.1 ∧ 0 < hi.1 ∧
  (hi.2 : Int) ^ 2 * (S.2 : Int) ^ 2 < 8 * S.1 ^ 2 * hi.1 ^ 2 ∧
  8 * S.1 ^ 2 * lo.1 ^ 2 < (lo.2 : Int) ^ 2 * (S.2 : Int) ^ 2

theorem ramanujan_S0_exact : ramanujanS 0 = (1103, 9801) := by decide

theorem ramanujan_S1_exact : ramanujanS 1 = (1130173253125, 10042454926944) := by decide

theorem machin_pi_bracket_14 :
    0 < machinPi15Lo.1 ∧ 0 < machinPi15Hi.1 ∧
    314159265358979 * (machinPi15Lo.2 : Int) < machinPi15Lo.1 * (10 ^ 14 : Int) ∧
    machinPi15Hi.1 * (10 ^ 14 : Int) < 314159265358980 * (machinPi15Hi.2 : Int) := by decide

theorem ramanujan_S0_bracket_7_digits :
    piSqBracket (ramanujanS 0) (3141592, 10 ^ 6) (3141593, 10 ^ 6) := by
  dsimp [piSqBracket]; decide

theorem ramanujan_S1_bracket_14_digits :
    piSqBracket (ramanujanS 1) (314159265358979, 10 ^ 14) (314159265358980, 10 ^ 14) := by
  dsimp [piSqBracket]; decide

theorem ramanujan_S2_inside_machin15 :
    piSqBracket (ramanujanS 2) machinPi15Lo machinPi15Hi := by
  dsimp [piSqBracket]; decide

theorem ramanujan_S1_strictly_below_machinHi :
    8 * (ramanujanS 1).1 ^ 2 * machinPi15Hi.1 ^ 2 <
    (machinPi15Hi.2 : Int) ^ 2 * ((ramanujanS 1).2 : Int) ^ 2 := by decide

theorem natFact_pos : ∀ n : Nat, 0 < natFact n
  | 0 => by decide
  | n + 1 => Nat.mul_pos (Nat.zero_lt_succ n) (natFact_pos n)

theorem natFact_4_succ (k : Nat) :
    natFact (4 * (k + 1)) =
    (4 * k + 4) * (4 * k + 3) * (4 * k + 2) * (4 * k + 1) * natFact (4 * k) := by
  have h1 : 4 * (k + 1) = (4 * k + 3) + 1 := Eq.refl _
  have h2 : 4 * k + 3 = (4 * k + 2) + 1 := Eq.refl _
  have h3 : 4 * k + 2 = (4 * k + 1) + 1 := Eq.refl _
  have h4 : 4 * k + 1 = (4 * k) + 1 := Eq.refl _
  rw [h1, natFact, h2, natFact, h3, natFact, h4, natFact,
      ← Nat.mul_assoc, ← Nat.mul_assoc, ← Nat.mul_assoc]

theorem nat_pow4_mul (a b : Nat) : (a * b) ^ 4 = a ^ 4 * b ^ 4 := by
  rw [Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_zero, Nat.one_mul,
      Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_zero, Nat.one_mul,
      Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_zero, Nat.one_mul]
  have s1 : (a * b) * (a * b) = (a * a) * (b * b) := nat_mul4_swap23 a b a b
  have s2 : ((a * a) * (b * b)) * (a * b) = (a * a * a) * (b * b * b) :=
    nat_mul4_swap23 (a * a) (b * b) a b
  rw [s1, s2]
  exact nat_mul4_swap23 (a * a * a) (b * b * b) a b

theorem ramanujan_pi_term_ratio_core (k : Nat) :
    4 * 10 ^ 7 * ((4 * k + 4) * (4 * k + 3) * (4 * k + 2) * (4 * k + 1)) *
      (1103 + 26390 * (k + 1)) <
    (1103 + 26390 * k) * (k + 1) ^ 4 * 396 ^ 4 := by
  cases k with
  | zero => decide
  | succ m =>
    let k := m + 1
    have h41 : 4 * k + 1 ≤ 4 * (k + 1) := by
      rw [Nat.mul_add]; exact Nat.add_le_add_left (by decide : 1 ≤ 4) (4 * k)
    have h42 : 4 * k + 2 ≤ 4 * (k + 1) := by
      rw [Nat.mul_add]; exact Nat.add_le_add_left (by decide : 2 ≤ 4) (4 * k)
    have h43 : 4 * k + 3 ≤ 4 * (k + 1) := by
      rw [Nat.mul_add]; exact Nat.add_le_add_left (by decide : 3 ≤ 4) (4 * k)
    have h44 : 4 * k + 4 ≤ 4 * (k + 1) := Nat.le_refl (4 * (k + 1))
    have hprod_le : (4 * k + 4) * (4 * k + 3) * (4 * k + 2) * (4 * k + 1) ≤ (4 * (k + 1)) ^ 4 := by
      have p12 := Nat.mul_le_mul h44 h43
      have p123 := Nat.mul_le_mul p12 h42
      have p1234 := Nat.mul_le_mul p123 h41
      have hpow : (4 * (k + 1)) * (4 * (k + 1)) * (4 * (k + 1)) * (4 * (k + 1)) = (4 * (k + 1)) ^ 4 := by
        rw [Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_succ, Nat.pow_zero, Nat.one_mul]
      rw [hpow] at p1234
      exact p1234
    have h4pow : (4 * (k + 1)) ^ 4 = 256 * (k + 1) ^ 4 := by
      rw [nat_pow4_mul 4 (k + 1)]
    rw [h4pow] at hprod_le
    have hlin_le : 1103 + 26390 * (k + 1) ≤ 2 * (1103 + 26390 * k) := by
      have hk1 : 1 ≤ k := Nat.succ_le_succ (Nat.zero_le m)
      have h26 : 26390 ≤ 26390 * k := Nat.le_mul_of_pos_right 26390 hk1
      have h26' : 26390 ≤ 1103 + 26390 * k := Nat.le_trans h26 (Nat.le_add_left (26390 * k) 1103)
      rw [Nat.mul_add 26390 k 1, Nat.mul_one, ← Nat.add_assoc, Nat.two_mul (1103 + 26390 * k)]
      exact Nat.add_le_add_left h26' (1103 + 26390 * k)
    have hcomb := Nat.mul_le_mul (Nat.mul_le_mul_left (4 * 10 ^ 7) hprod_le) hlin_le
    have hrearrL : 4 * 10 ^ 7 * (256 * (k + 1) ^ 4) * (2 * (1103 + 26390 * k)) =
        (4 * 10 ^ 7 * 512) * ((1103 + 26390 * k) * (k + 1) ^ 4) := by
      rw [← Nat.mul_assoc (4 * 10 ^ 7) 256 ((k + 1) ^ 4),
          nat_mul4_swap23 (4 * 10 ^ 7 * 256) ((k + 1) ^ 4) 2 (1103 + 26390 * k),
          Nat.mul_comm ((k + 1) ^ 4) (1103 + 26390 * k),
          Nat.mul_assoc (4 * 10 ^ 7) 256 2]
    have hconst : 4 * 10 ^ 7 * 512 < 396 ^ 4 := by decide
    have hpos : 0 < (1103 + 26390 * k) * (k + 1) ^ 4 :=
      Nat.mul_pos (Nat.add_pos_left (by decide : 0 < 1103) _) (Nat.pow_pos (Nat.zero_lt_succ k))
    have hstrict := Nat.mul_lt_mul_of_pos_right hconst hpos
    rw [Nat.mul_comm (396 ^ 4) _] at hstrict
    exact Nat.lt_of_le_of_lt (Nat.le_trans hcomb (Nat.le_of_eq hrearrL)) hstrict

theorem ramanujan_pi_term_ratio_all_k : ∀ k : Nat,
    4 * 10 ^ 7 * (ramanujanPiNum (k + 1) * ramanujanPiDen k) <
    ramanujanPiNum k * ramanujanPiDen (k + 1) := by
  intro k
  dsimp [ramanujanPiNum, ramanujanPiDen]
  rw [natFact_4_succ k]
  have hfact_k1 : (natFact (k + 1)) ^ 4 = (k + 1) ^ 4 * (natFact k) ^ 4 := by
    rw [natFact, nat_pow4_mul]
  have h396 : 396 ^ (4 * (k + 1)) = 396 ^ 4 * 396 ^ (4 * k) := by
    have h4 : 4 * (k + 1) = 4 + 4 * k := by rw [Nat.mul_add, Nat.mul_comm 4 k, Nat.add_comm]
    rw [h4, Nat.pow_add]
  rw [hfact_k1, h396]
  let P := natFact (4 * k) * (natFact k) ^ 4 * 396 ^ (4 * k)
  have hP : 0 < P :=
    Nat.mul_pos (Nat.mul_pos (natFact_pos (4 * k)) (Nat.pow_pos (natFact_pos k)))
      (Nat.pow_pos (by decide : 0 < 396))
  have hcore := Nat.mul_lt_mul_of_pos_left (ramanujan_pi_term_ratio_core k) hP
  let F4 := natFact (4 * k)
  let Fk4 := (natFact k) ^ 4
  let Ck := 396 ^ (4 * k)
  let Q := (4 * k + 4) * (4 * k + 3) * (4 * k + 2) * (4 * k + 1)
  let L := 1103 + 26390 * (k + 1)
  let K := 4 * 10 ^ 7
  let Lin := 1103 + 26390 * k
  let Kp4 := (k + 1) ^ 4
  let C4 := 396 ^ 4
  have hLHS : P * (K * Q * L) = K * ((Q * F4 * L) * (Fk4 * Ck)) := by
    change (F4 * Fk4 * Ck) * (K * Q * L) = _
    calc F4 * Fk4 * Ck * (K * Q * L)
        = (F4 * (Fk4 * Ck)) * (K * (Q * L)) := by rw [Nat.mul_assoc F4 Fk4 Ck, Nat.mul_assoc K Q L]
      _ = (K * (Q * L)) * (F4 * (Fk4 * Ck)) := Nat.mul_comm _ _
      _ = K * ((Q * L) * (F4 * (Fk4 * Ck))) := Nat.mul_assoc K (Q * L) _
      _ = K * (((Q * L) * F4) * (Fk4 * Ck)) := by rw [← Nat.mul_assoc (Q * L) F4 (Fk4 * Ck)]
      _ = K * ((Q * F4 * L) * (Fk4 * Ck)) := by
          rw [Nat.mul_assoc Q L F4, Nat.mul_comm L F4, ← Nat.mul_assoc Q F4 L]
  have hRHS : P * (Lin * Kp4 * C4) = (F4 * Lin) * ((Kp4 * Fk4) * (C4 * Ck)) := by
    change (F4 * Fk4 * Ck) * (Lin * Kp4 * C4) = _
    calc F4 * Fk4 * Ck * (Lin * Kp4 * C4)
        = (F4 * (Fk4 * Ck)) * (Lin * (Kp4 * C4)) := by rw [Nat.mul_assoc F4 Fk4 Ck, Nat.mul_assoc Lin Kp4 C4]
      _ = (F4 * Lin) * ((Fk4 * Ck) * (Kp4 * C4)) := nat_mul4_swap23 F4 (Fk4 * Ck) Lin (Kp4 * C4)
      _ = (F4 * Lin) * ((Kp4 * Fk4) * (C4 * Ck)) := by
          rw [Nat.mul_comm (Fk4 * Ck) (Kp4 * C4), nat_mul4_swap23 Kp4 C4 Fk4 Ck]
  change P * (K * Q * L) < P * (Lin * Kp4 * C4) at hcore
  rw [hLHS, hRHS] at hcore
  exact hcore

theorem ramanujan_pi_term_ratio_1e7_all_k : ∀ k : Nat,
    10 ^ 7 * (ramanujanPiNum (k + 1) * ramanujanPiDen k) <
    ramanujanPiNum k * ramanujanPiDen (k + 1) := by
  intro k
  have h1 : 10 ^ 7 ≤ 4 * 10 ^ 7 := Nat.le_mul_of_pos_left (10 ^ 7) (by decide : 0 < 4)
  have h2 := Nat.mul_le_mul_right (ramanujanPiNum (k + 1) * ramanujanPiDen k) h1
  exact Nat.lt_of_le_of_lt h2 (ramanujan_pi_term_ratio_all_k k)

theorem neg_ctrl_pi_S0_fails_14_digits :
    ¬ piSqBracket (ramanujanS 0) (314159265358979, 10 ^ 14) (314159265358980, 10 ^ 14) := by
  intro ⟨_, _, _, hlt, _⟩
  exact absurd hlt (by decide)

theorem neg_ctrl_pi_perturbed_1103_to_1102_fails :
    8 * (ramanujanS1Pert 1102).1 ^ 2 * (3142 : Int) ^ 2 <
    (1000 : Int) ^ 2 * ((ramanujanS1Pert 1102).2 : Int) ^ 2 ∧
    ¬ piSqBracket (ramanujanS1Pert 1102) (3141, 1000) (3142, 1000) := by
  have hlt : 8 * (ramanujanS1Pert 1102).1 ^ 2 * (3142 : Int) ^ 2 <
      (1000 : Int) ^ 2 * ((ramanujanS1Pert 1102).2 : Int) ^ 2 := by decide
  refine ⟨hlt, ?_⟩
  intro ⟨_, _, _, hge, _⟩
  exact absurd (Int.lt_trans hlt hge) (Int.lt_irrefl _)


-- ═══════════════════════════════════════════════════════════════════════════════
-- Section 9: 1-to-1 Axiom Footprint Verification (253/253 Theorems)
-- ═══════════════════════════════════════════════════════════════════════════════

#print axioms my_foldl_append
#print axioms my_foldl_map
#print axioms foldl_congr
#print axioms list_getD_nil
#print axioms list_getD_cons_zero
#print axioms list_getD_cons_succ
#print axioms list_ext_getD
#print axioms list_getD_map
#print axioms list_getD_replicate
#print axioms list_getD_append_left
#print axioms list_getD_append_right
#print axioms list_getD_take
#print axioms nat_strong_ind
#print axioms nat_beq_iff_eq
#print axioms nat_beq_self
#print axioms nat_beq_false_of_ne
#print axioms int_beq_iff_eq
#print axioms int_beq_false_of_ne
#print axioms bool_cond_true
#print axioms bool_cond_false
#print axioms int_add_comm_left
#print axioms int_add_eq_zero_solve
#print axioms int_sq_sum
#print axioms int_add3_sub3_cancel_mid
#print axioms int_add_sub_cancel_mid
#print axioms int_mul4_swap13
#print axioms int_mul4_swap23
#print axioms int_add4_cancel_mid
#print axioms nat_mul3_swap23
#print axioms nat_mul4_swap13
#print axioms nat_mul4_swap23
#print axioms nat_sq2
#print axioms nat_sq2_add1
#print axioms nat_two_dvd_mul_succ
#print axioms list_range_loop_length
#print axioms list_range_length
#print axioms list_range_loop_eq_append
#print axioms list_range_succ
#print axioms list_range_loop_map_getD_lt
#print axioms getD_map_range
#print axioms list_mem_of_all
#print axioms mem_list_range
#print axioms FPSEq.refl
#print axioms FPSEq.symm
#print axioms FPSEq.trans
#print axioms sumRange_congr
#print axioms sumRange_add
#print axioms sumRange_neg
#print axioms sumRange_sub
#print axioms sumRange_mul_left
#print axioms sumRange_mul_right
#print axioms sumRange_zero_of
#print axioms sumRange_succ_shift
#print axioms sumRange_rev
#print axioms sumRange_triangle
#print axioms sumRange_add_right
#print axioms sumRange_split_at
#print axioms foldl_range_sumRange
#print axioms fpsAdd_congr
#print axioms fpsNeg_congr
#print axioms fpsSub_congr
#print axioms fpsAdd_comm
#print axioms fpsAdd_assoc
#print axioms fpsAdd_zero_left
#print axioms fpsAdd_zero_right
#print axioms fpsAdd_neg_right
#print axioms fpsNeg_neg
#print axioms fpsSub_eq_add_neg
#print axioms fpsMul_congr
#print axioms fpsMul_comm
#print axioms fpsMul_assoc
#print axioms fpsMul_one_left
#print axioms fpsMul_one_right
#print axioms fpsMul_zero_left
#print axioms fpsMul_zero_right
#print axioms fpsMul_add_left
#print axioms fpsMul_add_right
#print axioms fpsMul_neg_left
#print axioms fpsMul_neg_right
#print axioms fpsMul_sub_left
#print axioms fpsMul_sub_right
#print axioms fpsInvPrefix_length
#print axioms fpsInvPrefix_step_getD_lt
#print axioms fpsInvPrefix_getD_le
#print axioms fpsInv_zero
#print axioms fpsInv_succ
#print axioms fpsMul_inv_left
#print axioms fpsMul_inv_right
#print axioms fpsInv_unique
#print axioms fpsInv_inv
#print axioms fpsInv_congr
#print axioms fpsMul_eq_on_le
#print axioms fpsInv_eq_on_le
#print axioms fpsInv_unique_lt
#print axioms fpsPowNat_congr
#print axioms fpsPowNat_add
#print axioms fpsPowNat_mul_two
#print axioms fpsPowInt_congr
#print axioms polyAdd_length
#print axioms polyAdd_getD
#print axioms polySub_length
#print axioms polySub_getD
#print axioms polyShift_length
#print axioms polyShift_getD
#print axioms polyMul_length
#print axioms polyMul_getD
#print axioms listToFPS_eq_on
#print axioms oneList_length
#print axioms oneList_getD
#print axioms polyInvAux_spec
#print axioms polyInv_length
#print axioms polyInv_getD
#print axioms polyPowAux_spec
#print axioms polyPowNat_length
#print axioms polyPowNat_getD
#print axioms polyPowInt_length
#print axioms polyPowInt_getD
#print axioms dilate_baseEta_getD
#print axioms etaCoeffs_spec
#print axioms etaCoeffs_length
#print axioms etaCoeffs_getD
#print axioms replicate_getD_zero
#print axioms evalLinearEtaStep_getD
#print axioms evalLinearEta_getD_eq_FPS
#print axioms oneSubQPow_zero
#print axioms oneAddQPow_zero
#print axioms prodAllMinus_zero
#print axioms prodOddMinus_zero
#print axioms polyBinom_getD
#print axioms prodAllMinusList_getD
#print axioms prodDistinctList_getD
#print axioms prodOddMinusList_getD
#print axioms oneSubQPow_of_pos_ne
#print axioms oneAddQPow_of_pos_ne
#print axioms oneSubQPow_at_self
#print axioms oneAddQPow_at_self
#print axioms oneSub_mul_oneAdd_eq_two
#print axioms prodAllMinus_two_mul
#print axioms prodEvenMinus_eq_mul_distinct
#print axioms fpsMul_tail_one_lt
#print axioms prodAllMinus_step_stabilizes
#print axioms prodAllMinus_stabilizes_all
#print axioms prodDistinct_step_stabilizes
#print axioms prodDistinct_stabilizes_add
#print axioms prodDistinct_stabilizes_all
#print axioms prodOddMinus_step_stabilizes
#print axioms prodOddMinus_stabilizes_add
#print axioms oddParts_stabilizes_all
#print axioms euler_odd_eq_distinct_all_n
#print axioms euler_odd_eq_distinct_all_len
#print axioms pentagonal_product_matches_baseEta_20
#print axioms partition_pentagonal_recurrence_all_n
#print axioms partList_matches_fpsInv_65
#print axioms partList_eq_fpsInv_lt_65
#print axioms euler_combinatorial_odd_eq_distinct_20
#print axioms euler_combinatorial_eq_oddPartsFPS_le_20
#print axioms neg_ctrl_even_parts_ne_distinct
#print axioms neg_ctrl_omit_part1_distinct_fails
#print axioms ramanujan_mod5_prefix_13
#print axioms ramanujan_mod7_prefix_9
#print axioms ramanujan_mod11_prefix_6
#print axioms ramanujan_mod5_gen_identity_12
#print axioms ramanujan_mod5_gen_fps_lt_12
#print axioms ramanujan_mod7_gen_identity_9
#print axioms ramanujan_mod7_gen_fps_lt_9
#print axioms ramanujan_mod5_all_n_conditional
#print axioms ramanujan_mod7_all_n_conditional
#print axioms mod5_other_residues_nz_check
#print axioms neg_ctrl_mod5_other_residues_fail
#print axioms mod13_residues_nz_check
#print axioms neg_ctrl_mod13_no_linear_congruence
#print axioms mod3_residues_nz_check
#print axioms neg_ctrl_mod3_no_linear_congruence
#print axioms tau_exact_1_to_16
#print axioms dilateFPS_one_id
#print axioms tau16_eq_tauFPS_le_16
#print axioms tau_ono_level1_weight12
#print axioms sumRange_pred_split
#print axioms sigmaK_prime_all_p
#print axioms tau_coprime_multiplicative_witnesses
#print axioms tau_hecke_prime_power_witnesses
#print axioms tau_mod_691_witnesses_16
#print axioms tau_deligne_squared_bounds
#print axioms tau_nonzero_and_avoids_forbidden_16
#print axioms neg_ctrl_tau_noncoprime_fails
#print axioms neg_ctrl_tau_mod691_perturbed_fails
#print axioms ramanujanSum_zero_all_n
#print axioms ramanujanSum_one_all_n
#print axioms mobiusGo_prime_aux
#print axioms mobius_prime_eq_neg_one
#print axioms ramanujanSum_prime_all_n
#print axioms ramanujanSum_orthogonality_zero_sum
#print axioms ramanujanSum_orthogonality_zero_sum_prop
#print axioms ramanujanSum_superchar_orthogonality_12
#print axioms neg_ctrl_ramanujanSum_composite_4_fails_prime_rule
#print axioms neg_ctrl_ramanujanSum_q1_nonzero_sum
#print axioms altSign_succ
#print axioms int_cf_alg_step
#print axioms euler_wallis_det_int_all_k
#print axioms fps_cf_alg_step
#print axioms fpsAltSign_mul_neg
#print axioms euler_wallis_det_fps_all_k
#print axioms fpsQPow_mul
#print axioms rrA_succ
#print axioms prodRange1FPS_rrA
#print axioms rr_cf_convergent_diff_vanishes_all_k
#print axioms rr_G_exact_16
#print axioms rr_H_exact_16
#print axioms rr_cf_6_matches_H_over_G_16
#print axioms neg_ctrl_rr_unshifted_eta_ratio_fails
#print axioms neg_ctrl_euler_wallis_missing_sign_fails
#print axioms neg_ctrl_rr_G_ne_H
#print axioms mock3_f_exact_16
#print axioms mock3_phi_exact_16
#print axioms mock3_psi_exact_16
#print axioms mock3_f_plus_4psi_neg_eq_eta_16
#print axioms mock3_2phi_neg_minus_f_eq_eta_16
#print axioms mock3_phi_minus_f_neg_eq_2psi_16
#print axioms mock3_psi_const_zero_all_M
#print axioms mock3_f_stabilizes_add
#print axioms mock3_f_stabilizes_all_n
#print axioms mock3_psi_stabilizes_add
#print axioms mock3_psi_stabilizes_all_n
#print axioms neg_ctrl_mock3_psi_legacy_stub_q0_false
#print axioms neg_ctrl_mock3_f_not_eta_shadow
#print axioms neg_ctrl_mock3_f_plus_2psi_neg_fails
#print axioms taxicab_1729_witness
#print axioms taxicab_quad_check_13
#print axioms taxicab_ordered_below_13
#print axioms taxicab_ordered_all
#print axioms taxicab_1729_minimal_all
#print axioms isHCN_sound
#print axioms hcn_first_10_verified
#print axioms hcn_first_10_all_IsHighlyComposite
#print axioms taxicab_1728_below_13_check
#print axioms neg_ctrl_taxicab_1728_no_pos_cube_sum
#print axioms neg_ctrl_hcn_18_not_hcn
#print axioms neg_ctrl_hcn_100_not_hcn
#print axioms ramanujan_S0_exact
#print axioms ramanujan_S1_exact
#print axioms machin_pi_bracket_14
#print axioms ramanujan_S0_bracket_7_digits
#print axioms ramanujan_S1_bracket_14_digits
#print axioms ramanujan_S2_inside_machin15
#print axioms ramanujan_S1_strictly_below_machinHi
#print axioms natFact_pos
#print axioms natFact_4_succ
#print axioms nat_pow4_mul
#print axioms ramanujan_pi_term_ratio_core
#print axioms ramanujan_pi_term_ratio_all_k
#print axioms ramanujan_pi_term_ratio_1e7_all_k
#print axioms neg_ctrl_pi_S0_fails_14_digits
#print axioms neg_ctrl_pi_perturbed_1103_to_1102_fails

end DualScale.RamanujanElenchusCanon

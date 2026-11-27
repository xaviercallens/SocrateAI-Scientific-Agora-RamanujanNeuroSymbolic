-- MATHESIS-GATE: env=none
-- MATHESIS-GATE: allow=propext
/-!
  Standalone Zero-Custom-Axiom Lean 4.33.1 Kernel Verification
  for Universal `∀ n` / `∀ len` Campaign v2 Identities, Jacobi Triple Product
  Eta-Quotient Lifts, Sturm-Bound Conditional Upgrade with Level-12 Nebentypus
  `χ(d) = (-3/d)` Compatibility, Ono (2004) Mod-24 Algebra, `Sym^2` Recurrence,
  Exact `ℚ⁺` T-Duality, RAMA Deep Burn Invariants, and Certified Refutations /
  Reclassifications (CFM, M2 Alon–Boppana, S12 Recurrence, 14 Campaign v2 OCR Typos).

  Strict kernel hygiene:
  - Standalone `Init`-only (zero `import Mathlib.*`)
  - Zero custom axioms, zero unfinished proof stubs, zero vacuous predicates or reflexive tautologies
  - Every exported theorem footprint strictly `⊆ {propext}` (63/63 audited)
-/

namespace DualScale.AllNPropositions

set_option maxRecDepth 100000
set_option maxHeartbeats 2000000

-- ═══════════════════════════════════════════════════════════════════════════════
-- Section 0: Lean 4.33.1 Init-Only Kernel Hygiene Helpers (No Quot.sound/Choice)
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
  | _ :: xs, ys, 0, hi => absurd hi (Nat.not_le_of_gt (Nat.zero_lt_succ xs.length))
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

theorem int_add3_sub3_cancel_mid (A M B C D : Int) :
    (A + M + B) - (C + M + D) = (A - C) + (B - D) := by
  rw [Int.sub_eq_add_neg, Int.neg_add, Int.neg_add, Int.add_assoc (A + M) B _,
      Int.add_comm (-C) (-M), Int.add_assoc (-M) (-C) (-D),
      int_add_comm_left B (-M) (-C + -D), Int.add_assoc A M _,
      ← Int.add_assoc M (-M) _, Int.add_right_neg, Int.zero_add,
      int_add_comm_left B (-C) (-D), ← Int.add_assoc A (-C) _,
      ← Int.sub_eq_add_neg, ← Int.sub_eq_add_neg]

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

-- List.range helpers without Quot.sound
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
  | 0, acc => Eq.refl _
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

-- ═══════════════════════════════════════════════════════════════════════════════
-- Section 1: Formal Power Series Ring (`FPS := Nat → Int`) & List-FPS Bridge
-- ═══════════════════════════════════════════════════════════════════════════════

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

theorem foldl_range_sumRange (n : Nat) (g : Nat → Int) :
    (List.range n).foldl (fun acc k => acc + g k) 0 = sumRange n g := by
  induction n with
  | zero => exact Eq.refl _
  | succ m ihm =>
    rw [list_range_succ, my_foldl_append]
    change (List.range m).foldl (fun acc k => acc + g k) 0 + g m = sumRange m g + g m
    rw [ihm]

def fpsOne : FPS := fun n => if n == 0 then 1 else 0

def fpsMul (f g : FPS) : FPS :=
  fun n => sumRange (n + 1) (fun k => f k * g (n - k))

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
    FPSEq.trans (fpsMul_congr h.symm (FPSEq.refl (fpsInv f)))
      (FPSEq.trans (fpsMul_comm f (fpsInv f)) (fpsMul_inv_left f hf0))
  exact fpsInv_unique g (fpsInv f) hg0 hmul

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

theorem fpsPowInt_neg1_neg1 (f : FPS) :
    FPSEq (fpsMul (fpsPowInt f (-1)) (fpsPowInt f (-1))) (fpsPowInt f (-2)) := by
  have h1 : fpsPowInt f (-1) = fpsPowNat (fpsInv f) 1 := Eq.refl _
  have h2 : fpsPowInt f (-2) = fpsPowNat (fpsInv f) 2 := Eq.refl _
  rw [h1, h2]
  exact (fpsPowNat_add (fpsInv f) 1 1).symm

theorem fpsPowInt_pos2_pos1 (f : FPS) :
    FPSEq (fpsMul (fpsPowInt f 2) (fpsPowInt f 1)) (fpsPowInt f 3) := by
  have h2 : fpsPowInt f 2 = fpsPowNat f 2 := Eq.refl _
  have h1 : fpsPowInt f 1 = fpsPowNat f 1 := Eq.refl _
  have h3 : fpsPowInt f 3 = fpsPowNat f 3 := Eq.refl _
  rw [h2, h1, h3]
  exact (fpsPowNat_add f 2 1).symm

-- Computable Eta-Quotients (matching CampaignV2Verified.lean)
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

/-- Cusp-0 effective central charge `c_eff(0) = -∑ (r_d / d)`. -/
def cEffCusp0 (eq : EtaQuot) : Int × Nat :=
  eq.factors.foldl (fun acc dr => ratAdd acc (-dr.2, dr.1)) (0, 1)

def modularWeight (eq : EtaQuot) : Int × Nat :=
  let s := eq.factors.foldl (fun acc dr => acc + dr.2) 0
  ratNorm s 2

/-- Ground state shift `E_0 = -(∑ d * r_d) / 24`. -/
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

-- Exact List-FPS bridge theorems
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
  | 0, e, base, acc, f, g, he, _, hlen, hacc => by
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
        have hne0 : (e'' + 2 == 0) = false := nat_beq_false_of_ne (Nat.succ_ne_zero (e'' + 1))
        have hne1 : (e'' + 2 == 1) = false := nat_beq_false_of_ne (by
          intro h; exact absurd (Nat.succ.inj h) (Nat.succ_ne_zero e''))
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
            have ha1 : FPSEq (fpsMul (fpsMul g f) (fpsPowNat (fpsMul f f) ((e'' + 2) / 2)))
                (fpsMul g (fpsMul f (fpsPowNat (fpsMul f f) ((e'' + 2) / 2)))) :=
              fpsMul_assoc g f _
            have ha2 : FPSEq (fpsMul f (fpsPowNat (fpsMul f f) ((e'' + 2) / 2)))
                (fpsMul (fpsPowNat (fpsMul f f) ((e'' + 2) / 2)) f) :=
              fpsMul_comm f _
            have ha3 : FPSEq (fpsMul (fpsPowNat (fpsMul f f) ((e'' + 2) / 2)) f)
                (fpsMul (fpsPowNat f ((e'' + 2) / 2 + (e'' + 2) / 2)) f) :=
              fpsMul_congr (fpsPowNat_mul_two f ((e'' + 2) / 2)).symm (FPSEq.refl f)
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
  · have hd0 : d ≠ 0 := by
      intro h0
      rw [h0] at hd
      cases hd
    have hdiv : i / d < N := by
      cases d with
      | zero => exact absurd (Eq.refl 0) hd0
      | succ d' =>
        exact Nat.lt_of_le_of_lt (Nat.div_le_self i (d' + 1)) hi
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

theorem etaCoeffs_eq_of_etaFPS_eq (a b : EtaQuot) (h : FPSEq (etaFPS a) (etaFPS b)) :
    ∀ len : Nat, etaCoeffs a len = etaCoeffs b len := by
  intro len
  apply list_ext_getD 0
  · rw [etaCoeffs_length, etaCoeffs_length]
  · intro i hi
    rw [etaCoeffs_length] at hi
    rw [etaCoeffs_getD a len i hi, etaCoeffs_getD b len i hi, h i]

-- FPS Dilation Ring Homomorphism & EtaQuot Dilation Bridge
theorem dilateFPS_congr {f g : FPS} (h : FPSEq f g) (d : Nat) :
    FPSEq (dilateFPS f d) (dilateFPS g d) := by
  intro n
  dsimp [dilateFPS]
  by_cases hc : (d != 0 && n % d == 0) = true
  · rw [if_pos hc, if_pos hc, h (n / d)]
  · rw [if_neg hc, if_neg hc]

theorem dilateFPS_at_zero (f : FPS) {d : Nat} (hd : d ≠ 0) :
    dilateFPS f d 0 = f 0 := by
  have hcond : (d != 0 && 0 % d == 0) = true := by
    cases d with
    | zero => exact absurd (Eq.refl 0) hd
    | succ d' => rw [Nat.zero_mod]; exact Eq.refl _
  change (if (d != 0 && 0 % d == 0) = true then f (0 / d) else 0) = f 0
  rw [bool_cond_true hcond, Nat.zero_div]

theorem dilateFPS_of_mod_eq_zero (f : FPS) {d n : Nat} (hd : d ≠ 0) (hm : n % d = 0) :
    dilateFPS f d n = f (n / d) := by
  dsimp [dilateFPS]
  have hd0 : (d != 0) = true := by
    cases d with
    | zero => exact absurd (Eq.refl 0) hd
    | succ _ => exact Eq.refl _
  have hm0 : (n % d == 0) = true := (nat_beq_iff_eq (n % d) 0).mpr hm
  have hcond : (d != 0 && n % d == 0) = true := by rw [hd0, hm0]; exact Eq.refl _
  rw [if_pos hcond]

theorem dilateFPS_of_mod_ne_zero (f : FPS) {d n : Nat} (hm : n % d ≠ 0) :
    dilateFPS f d n = 0 := by
  dsimp [dilateFPS]
  have hmf : (n % d == 0) = false := nat_beq_false_of_ne hm
  have hcond : (d != 0 && n % d == 0) = false := by
    rw [hmf]
    cases (d != 0) <;> exact Eq.refl _
  rw [bool_cond_false hcond]

theorem dilateFPS_one {d : Nat} (hd : d ≠ 0) :
    FPSEq (dilateFPS fpsOne d) fpsOne := by
  intro n
  cases n with
  | zero =>
    rw [dilateFPS_at_zero fpsOne hd]
  | succ m =>
    by_cases hmod : (m + 1) % d = 0
    · rw [dilateFPS_of_mod_eq_zero fpsOne hd hmod]
      have hdiv_pos : (m + 1) / d ≠ 0 := by
        intro h0
        have heq := Nat.div_add_mod (m + 1) d
        rw [h0, Nat.mul_zero, hmod, Nat.zero_add] at heq
        exact Nat.succ_ne_zero m heq.symm
      dsimp [fpsOne]
      rw [bool_cond_false (nat_beq_false_of_ne hdiv_pos)]
    · rw [dilateFPS_of_mod_ne_zero fpsOne hmod]
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

theorem sumRange_dilate_eq (d : Nat) (hd : 0 < d) (F : Nat → Int)
    (hzero : ∀ k, k % d ≠ 0 → F k = 0) :
    ∀ m : Nat, sumRange (d * m + 1) F = sumRange (m + 1) (fun j => F (d * j))
  | 0 => by
    change 0 + F 0 = 0 + F (d * 0)
    rw [Nat.mul_zero]
  | m + 1 => by
    have h1d : 1 ≤ d := hd
    have hstep : d * (m + 1) = (d * m + 1) + (d - 1) := by
      rw [Nat.mul_add, Nat.mul_one, Nat.add_assoc (d * m) 1 (d - 1),
          Nat.add_comm 1 (d - 1), Nat.sub_add_cancel h1d]
    change sumRange (d * (m + 1)) F + F (d * (m + 1)) =
      sumRange (m + 1) (fun j => F (d * j)) + F (d * (m + 1))
    rw [hstep, sumRange_add_right (d * m + 1) (d - 1) F]
    have hmid : sumRange (d - 1) (fun r => F ((d * m + 1) + r)) = 0 := by
      apply sumRange_zero_of
      intro r hr
      apply hzero
      have h1r_lt : 1 + r < d := by
        have h := Nat.add_lt_add_left hr 1
        rw [Nat.add_comm 1 (d - 1), Nat.sub_add_cancel h1d] at h
        exact h
      rw [Nat.add_assoc (d * m) 1 r, Nat.mul_add_mod d m (1 + r), Nat.mod_eq_of_lt h1r_lt,
          Nat.add_comm 1 r]
      exact Nat.succ_ne_zero r
    rw [hmid, Int.add_zero, sumRange_dilate_eq d hd F hzero m, ← hstep]

theorem dilateFPS_mul (f g : FPS) {d : Nat} (hd : d ≠ 0) :
    FPSEq (dilateFPS (fpsMul f g) d) (fpsMul (dilateFPS f d) (dilateFPS g d)) := by
  intro n
  have hd_pos : 0 < d := by
    cases d with
    | zero => exact absurd (Eq.refl 0) hd
    | succ d' => exact Nat.zero_lt_succ d'
  let F : Nat → Int := fun k => dilateFPS f d k * dilateFPS g d (n - k)
  change dilateFPS (fpsMul f g) d n = sumRange (n + 1) F
  by_cases hmod : n % d = 0
  · rw [dilateFPS_of_mod_eq_zero (fpsMul f g) hd hmod]
    let m := n / d
    have hn : n = d * m := by
      have h := Nat.div_add_mod n d
      rw [hmod, Nat.add_zero] at h
      exact h.symm
    have hzero : ∀ k, k % d ≠ 0 → F k = 0 := by
      intro k hk
      dsimp [F]
      rw [dilateFPS_of_mod_ne_zero f hk, Int.zero_mul]
    rw [hn, sumRange_dilate_eq d hd_pos F hzero m]
    dsimp [fpsMul]
    rw [Nat.mul_div_right m hd_pos]
    apply sumRange_congr
    intro j _
    dsimp [F]
    have hmod_dj : (d * j) % d = 0 := Nat.mul_mod_right d j
    have hdiv_dj : (d * j) / d = j := Nat.mul_div_right j hd_pos
    have hsub_n : n - d * j = d * (m - j) := by
      rw [hn, ← Nat.mul_sub_left_distrib]
    have hmod_sub : (d * (m - j)) % d = 0 := Nat.mul_mod_right d (m - j)
    have hdiv_sub : (d * (m - j)) / d = m - j := Nat.mul_div_right (m - j) hd_pos
    rw [dilateFPS_of_mod_eq_zero f hd hmod_dj, hdiv_dj,
        hsub_n, dilateFPS_of_mod_eq_zero g hd hmod_sub, hdiv_sub]
  · rw [dilateFPS_of_mod_ne_zero (fpsMul f g) hmod]
    symm
    apply sumRange_zero_of
    intro k hk
    dsimp [F]
    by_cases hkd : k % d = 0
    · have hsub_ne : (n - k) % d ≠ 0 := by
        intro hsub0
        have hk_le : k ≤ n := Nat.le_of_lt_succ hk
        have h1 : k = d * (k / d) := by
          have h := Nat.div_add_mod k d
          rw [hkd, Nat.add_zero] at h
          exact h.symm
        have h2 : n - k = d * ((n - k) / d) := by
          have h := Nat.div_add_mod (n - k) d
          rw [hsub0, Nat.add_zero] at h
          exact h.symm
        have hn_eq : n = d * (k / d + (n - k) / d) :=
          calc n = k + (n - k) := (Nat.add_sub_of_le hk_le).symm
            _ = d * (k / d) + (n - k) := congrArg (· + (n - k)) h1
            _ = d * (k / d) + d * ((n - k) / d) := congrArg (d * (k / d) + ·) h2
            _ = d * (k / d + (n - k) / d) := (Nat.mul_add d _ _).symm
        have hn0 : n % d = 0 := by rw [hn_eq]; exact Nat.mul_mod_right d _
        exact hmod hn0
      rw [dilateFPS_of_mod_ne_zero g hsub_ne, Int.mul_zero]
    · rw [dilateFPS_of_mod_ne_zero f hkd, Int.zero_mul]

theorem dilateFPS_inv (f : FPS) (hf0 : f 0 = 1) {d : Nat} (hd : d ≠ 0) :
    FPSEq (dilateFPS (fpsInv f) d) (fpsInv (dilateFPS f d)) := by
  have hd0 : dilateFPS f d 0 = 1 := by rw [dilateFPS_at_zero f hd, hf0]
  have hmul1 : FPSEq (fpsMul f (fpsInv f)) fpsOne :=
    FPSEq.trans (fpsMul_comm f (fpsInv f)) (fpsMul_inv_left f hf0)
  have hmul : FPSEq (fpsMul (dilateFPS f d) (dilateFPS (fpsInv f) d)) fpsOne :=
    FPSEq.trans (dilateFPS_mul f (fpsInv f) hd).symm
      (FPSEq.trans (dilateFPS_congr hmul1 d) (dilateFPS_one hd))
  exact fpsInv_unique (dilateFPS f d) (dilateFPS (fpsInv f) d) hd0 hmul

theorem dilateFPS_powNat (f : FPS) {d : Nat} (hd : d ≠ 0) :
    ∀ e : Nat, FPSEq (dilateFPS (fpsPowNat f e) d) (fpsPowNat (dilateFPS f d) e)
  | 0 => dilateFPS_one hd
  | e + 1 =>
    FPSEq.trans (dilateFPS_mul (fpsPowNat f e) f hd)
      (fpsMul_congr (dilateFPS_powNat f hd e) (FPSEq.refl (dilateFPS f d)))

theorem dilateFPS_powInt (f : FPS) (hf0 : f 0 = 1) {d : Nat} (hd : d ≠ 0) (e : Int) :
    FPSEq (dilateFPS (fpsPowInt f e) d) (fpsPowInt (dilateFPS f d) e) := by
  dsimp [fpsPowInt]
  by_cases h : e ≥ 0
  · rw [if_pos h, if_pos h]
    exact dilateFPS_powNat f hd e.toNat
  · rw [if_neg h, if_neg h]
    exact FPSEq.trans (dilateFPS_powNat (fpsInv f) hd (-e).toNat)
      (fpsPowNat_congr (dilateFPS_inv f hf0 hd) (-e).toNat)

theorem dilateFPS_dilateFPS (f : FPS) (d1 d2 : Nat) :
    FPSEq (dilateFPS (dilateFPS f d1) d2) (dilateFPS f (d1 * d2)) := by
  intro n
  by_cases hd1 : d1 = 0
  · rw [hd1, Nat.zero_mul]
    dsimp [dilateFPS]
    cases (d2 != 0 && n % d2 == 0) <;> exact Eq.refl 0
  · by_cases hd2 : d2 = 0
    · rw [hd2, Nat.mul_zero]
      dsimp [dilateFPS]
    · have hd12 : d1 * d2 ≠ 0 := by
        intro h0
        cases d1 with
        | zero => exact hd1 (Eq.refl 0)
        | succ a => cases d2 with
          | zero => exact hd2 (Eq.refl 0)
          | succ b =>
            have hpos : 0 < (a + 1) * (b + 1) := Nat.mul_pos (Nat.zero_lt_succ a) (Nat.zero_lt_succ b)
            rw [h0] at hpos
            exact Nat.not_lt_zero 0 hpos
      have hd2_pos : 0 < d2 := by
        cases d2 with
        | zero => exact absurd (Eq.refl 0) hd2
        | succ b => exact Nat.zero_lt_succ b
      by_cases hm2 : n % d2 = 0
      · rw [dilateFPS_of_mod_eq_zero (dilateFPS f d1) hd2 hm2]
        by_cases hm1 : (n / d2) % d1 = 0
        · rw [dilateFPS_of_mod_eq_zero f hd1 hm1]
          have hn2 : n = d2 * (n / d2) := by
            have h := Nat.div_add_mod n d2
            rw [hm2, Nat.add_zero] at h
            exact h.symm
          have hq1 : n / d2 = d1 * ((n / d2) / d1) := by
            have h := Nat.div_add_mod (n / d2) d1
            rw [hm1, Nat.add_zero] at h
            exact h.symm
          have hn12 : n = (d1 * d2) * ((n / d2) / d1) :=
            calc n = d2 * (n / d2) := hn2
              _ = d2 * (d1 * ((n / d2) / d1)) := congrArg (d2 * ·) hq1
              _ = (d2 * d1) * ((n / d2) / d1) := (Nat.mul_assoc d2 d1 _).symm
              _ = (d1 * d2) * ((n / d2) / d1) := by rw [Nat.mul_comm d2 d1]
          have hm12 : n % (d1 * d2) = 0 := by rw [hn12]; exact Nat.mul_mod_right _ _
          rw [dilateFPS_of_mod_eq_zero f hd12 hm12, Nat.div_div_eq_div_mul, Nat.mul_comm d2 d1]
        · rw [dilateFPS_of_mod_ne_zero f hm1]
          have hm12_ne : n % (d1 * d2) ≠ 0 := by
            intro hm12
            have hn12 : n = (d1 * d2) * (n / (d1 * d2)) := by
              have h := Nat.div_add_mod n (d1 * d2)
              rw [hm12, Nat.add_zero] at h
              exact h.symm
            have hnd2 : n = d2 * (d1 * (n / (d1 * d2))) :=
              calc n = (d1 * d2) * (n / (d1 * d2)) := hn12
                _ = (d2 * d1) * (n / (d1 * d2)) := by rw [Nat.mul_comm d1 d2]
                _ = d2 * (d1 * (n / (d1 * d2))) := Nat.mul_assoc d2 d1 _
            have hdiv2 : n / d2 = d1 * (n / (d1 * d2)) :=
              calc n / d2 = (d2 * (d1 * (n / (d1 * d2)))) / d2 := congrArg (· / d2) hnd2
                _ = d1 * (n / (d1 * d2)) := Nat.mul_div_right _ hd2_pos
            have hdiv1 : (n / d2) % d1 = 0 := by
              rw [hdiv2]; exact Nat.mul_mod_right d1 _
            exact hm1 hdiv1
          exact (dilateFPS_of_mod_ne_zero f hm12_ne).symm
      · rw [dilateFPS_of_mod_ne_zero (dilateFPS f d1) hm2]
        have hm12_ne : n % (d1 * d2) ≠ 0 := by
          intro hm12
          have hn12 : n = (d1 * d2) * (n / (d1 * d2)) := by
            have h := Nat.div_add_mod n (d1 * d2)
            rw [hm12, Nat.add_zero] at h
            exact h.symm
          have hnd2 : n = d2 * (d1 * (n / (d1 * d2))) :=
            calc n = (d1 * d2) * (n / (d1 * d2)) := hn12
              _ = (d2 * d1) * (n / (d1 * d2)) := by rw [Nat.mul_comm d1 d2]
              _ = d2 * (d1 * (n / (d1 * d2))) := Nat.mul_assoc d2 d1 _
          have hn2 : n % d2 = 0 := by rw [hnd2]; exact Nat.mul_mod_right d2 _
          exact hm2 hn2
        exact (dilateFPS_of_mod_ne_zero f hm12_ne).symm

def etaDilate (eq : EtaQuot) (k : Nat) : EtaQuot :=
  { factors := eq.factors.map (fun dr => (k * dr.1, dr.2)) }

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

theorem etaFPS_foldl_dilate (k : Nat) (hk : k ≠ 0) :
    ∀ (xs : List (Nat × Int)) (accL accR : FPS),
    (∀ dr, dr ∈ xs → dr.1 ≠ 0) →
    FPSEq accL (dilateFPS accR k) →
    FPSEq
      ((xs.map (fun dr => (k * dr.1, dr.2))).foldl (fun acc dr =>
        if dr.2 == 0 then acc else fpsMul acc (etaFactorFPS dr)) accL)
      (dilateFPS (xs.foldl (fun acc dr =>
        if dr.2 == 0 then acc else fpsMul acc (etaFactorFPS dr)) accR) k)
  | [], accL, accR, _, hacc => hacc
  | dr :: xs, accL, accR, hxs, hacc => by
    have hdr1 : dr.1 ≠ 0 := hxs dr List.mem_cons_self
    have htail : ∀ y, y ∈ xs → y.1 ≠ 0 := fun y hy => hxs y (List.mem_cons_of_mem dr hy)
    change FPSEq
      ((xs.map (fun dr => (k * dr.1, dr.2))).foldl (fun acc dr =>
        if dr.2 == 0 then acc else fpsMul acc (etaFactorFPS dr))
        (if dr.2 == 0 then accL else fpsMul accL (etaFactorFPS (k * dr.1, dr.2))))
      (dilateFPS (xs.foldl (fun acc dr =>
        if dr.2 == 0 then acc else fpsMul acc (etaFactorFPS dr))
        (if dr.2 == 0 then accR else fpsMul accR (etaFactorFPS dr))) k)
    by_cases h0 : (dr.2 == 0) = true
    · rw [if_pos h0, if_pos h0]
      exact etaFPS_foldl_dilate k hk xs accL accR htail hacc
    · rw [if_neg h0, if_neg h0]
      have hkdr1 : k * dr.1 ≠ 0 := by
        intro hprod
        cases hk_eq : k with
        | zero => exact hk hk_eq
        | succ k' => cases hdr_eq : dr.1 with
          | zero => exact hdr1 hdr_eq
          | succ d' =>
            have hpos : 0 < (k' + 1) * (d' + 1) :=
              Nat.mul_pos (Nat.zero_lt_succ k') (Nat.zero_lt_succ d')
            rw [hk_eq, hdr_eq] at hprod
            rw [hprod] at hpos
            exact Nat.not_lt_zero 0 hpos
      have hbase0 : dilateFPS baseEtaFPS dr.1 0 = 1 := by
        rw [dilateFPS_at_zero baseEtaFPS hdr1]
        exact Eq.refl _
      have hbasek0 : dilateFPS baseEtaFPS (k * dr.1) 0 = 1 := by
        rw [dilateFPS_at_zero baseEtaFPS hkdr1]
        exact Eq.refl _
      have hbase_dil : FPSEq (dilateFPS baseEtaFPS (k * dr.1)) (dilateFPS (dilateFPS baseEtaFPS dr.1) k) := by
        rw [Nat.mul_comm k dr.1]
        exact (dilateFPS_dilateFPS baseEtaFPS dr.1 k).symm
      have hfac1 : FPSEq (etaFactorFPS (k * dr.1, dr.2))
          (fpsPowInt (dilateFPS (dilateFPS baseEtaFPS dr.1) k) dr.2) :=
        fpsPowInt_congr hbasek0 hbase_dil dr.2
      have hfac2 : FPSEq (fpsPowInt (dilateFPS (dilateFPS baseEtaFPS dr.1) k) dr.2)
          (dilateFPS (etaFactorFPS dr) k) :=
        (dilateFPS_powInt (dilateFPS baseEtaFPS dr.1) hbase0 hk dr.2).symm
      have hfac : FPSEq (etaFactorFPS (k * dr.1, dr.2)) (dilateFPS (etaFactorFPS dr) k) :=
        FPSEq.trans hfac1 hfac2
      have hstep : FPSEq (fpsMul accL (etaFactorFPS (k * dr.1, dr.2)))
          (dilateFPS (fpsMul accR (etaFactorFPS dr)) k) :=
        FPSEq.trans (fpsMul_congr hacc hfac) (dilateFPS_mul accR (etaFactorFPS dr) hk).symm
      exact etaFPS_foldl_dilate k hk xs _ _ htail hstep

theorem etaFPS_dilate (eq : EtaQuot) {k : Nat} (hk : k ≠ 0)
    (hd : eq.factors.all (fun dr => dr.1 != 0) = true) :
    FPSEq (etaFPS (etaDilate eq k)) (dilateFPS (etaFPS eq) k) := by
  dsimp [etaFPS, etaDilate]
  have hmem : ∀ dr, dr ∈ eq.factors → dr.1 ≠ 0 := by
    intro dr hdr h0
    have hb := list_mem_of_all (fun dr : Nat × Int => dr.1 != 0) eq.factors hd dr hdr
    rw [h0] at hb
    cases hb
  exact etaFPS_foldl_dilate k hk eq.factors fpsOne fpsOne hmem (dilateFPS_one hk).symm

-- ═══════════════════════════════════════════════════════════════════════════════
-- Section 2: Requirements (a)–(f)
-- ═══════════════════════════════════════════════════════════════════════════════

-- -------------------------------------------------------------------------------
-- Requirement (a): Universal ∀ n / ∀ len Campaign v2 Identities (Theorems 1–4)
-- -------------------------------------------------------------------------------

def countPosSqRoots : Nat → Nat → Nat
  | 0, _ => 0
  | b + 1, n => (if (b + 1) * (b + 1) == n then 1 else 0) + countPosSqRoots b n

def phiCoeff (n : Nat) : Int :=
  if n == 0 then 1 else 2 * (countPosSqRoots n n : Int)

def countTriRoots : Nat → Nat → Nat
  | 0, _ => 0
  | b + 1, t => (if b * (b + 1) / 2 == t then 1 else 0) + countTriRoots b t

def psiCoeff (t : Nat) : Int :=
  (countTriRoots (t + 1) t : Int)

def seriesNeg (f : FPS) : FPS :=
  fun n => if n % 2 == 0 then f n else -f n

def dilateSeries (f : FPS) (d : Nat) : FPS :=
  fun n => if d != 0 && n % d == 0 then f (n / d) else 0

def qShiftSeries (s : Nat) (f : FPS) : FPS :=
  fun n => if n ≥ s then f (n - s) else 0

theorem nat_sq_gt_of_gt {a b : Nat} (h : b < a) : b * b < a * a := by
  have h1 : b * b ≤ b * a := Nat.mul_le_mul_left b (Nat.le_of_lt h)
  have h2 : b * a < a * a := by
    rw [Nat.mul_comm b a, Nat.mul_comm a a]
    exact Nat.mul_lt_mul_of_pos_left h (Nat.zero_lt_of_lt h)
  exact Nat.lt_of_le_of_lt h1 h2

theorem countPosSqRoots_mono_bound (B n : Nat) (hB : ∀ b, B < b → n < b * b) :
    ∀ M : Nat, B ≤ M → countPosSqRoots M n = countPosSqRoots B n
  | 0, hBM => by
    have h0 : B = 0 := Nat.eq_zero_of_le_zero hBM
    rw [h0]
  | M + 1, hBM => by
    cases Nat.lt_or_eq_of_le hBM with
    | inl hlt =>
      have hgt : n < (M + 1) * (M + 1) := hB (M + 1) hlt
      have hne : ((M + 1) * (M + 1) == n) = false :=
        nat_beq_false_of_ne (Nat.ne_of_gt hgt)
      change (if ((M + 1) * (M + 1) == n) = true then 1 else 0) + countPosSqRoots M n =
        countPosSqRoots B n
      rw [bool_cond_false hne, Nat.zero_add]
      exact countPosSqRoots_mono_bound B n hB M (Nat.le_of_lt_succ hlt)
    | inr heq => rw [heq]

theorem countPosSqRoots_eq_of_bound (B M₁ M₂ n : Nat)
    (hB : ∀ b, B < b → n < b * b) (h₁ : B ≤ M₁) (h₂ : B ≤ M₂) :
    countPosSqRoots M₁ n = countPosSqRoots M₂ n := by
  rw [countPosSqRoots_mono_bound B n hB M₁ h₁, countPosSqRoots_mono_bound B n hB M₂ h₂]

theorem nat_mod4_cases (b : Nat) :
    b % 4 = 0 ∨ b % 4 = 1 ∨ b % 4 = 2 ∨ b % 4 = 3 := by
  have hlt : b % 4 < 4 := Nat.mod_lt b (by decide : 0 < 4)
  match h : b % 4 with
  | 0 => exact Or.inl (Eq.refl 0)
  | 1 => exact Or.inr (Or.inl (Eq.refl 1))
  | 2 => exact Or.inr (Or.inr (Or.inl (Eq.refl 2)))
  | 3 => exact Or.inr (Or.inr (Or.inr (Eq.refl 3)))
  | k + 4 =>
    rw [h] at hlt
    have hk : k + 4 < 4 := hlt
    exact absurd (Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ
      (Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ hk)))) (Nat.not_lt_zero k)

theorem sq_mod4_ne_two (b : Nat) : (b * b) % 4 ≠ 2 := by
  rw [Nat.mul_mod]
  cases nat_mod4_cases b with
  | inl h0 => rw [h0]; decide
  | inr h1 => cases h1 with
    | inl h1 => rw [h1]; decide
    | inr h2 => cases h2 with
      | inl h2 => rw [h2]; decide
      | inr h3 => rw [h3]; decide

theorem countPosSqRoots_mod4_eq2 (n : Nat) (hn : n % 4 = 2) :
    ∀ B : Nat, countPosSqRoots B n = 0
  | 0 => Eq.refl _
  | B + 1 => by
    have hne : (B + 1) * (B + 1) ≠ n := by
      intro heq
      have hm : ((B + 1) * (B + 1)) % 4 = n % 4 := by rw [heq]
      rw [hn] at hm
      exact sq_mod4_ne_two (B + 1) hm
    change (if ((B + 1) * (B + 1) == n) = true then 1 else 0) + countPosSqRoots B n = 0
    rw [bool_cond_false (nat_beq_false_of_ne hne), Nat.zero_add]
    exact countPosSqRoots_mod4_eq2 n hn B

theorem nat_mod2_cases (b : Nat) : b % 2 = 0 ∨ b % 2 = 1 := by
  have hlt : b % 2 < 2 := Nat.mod_lt b (by decide : 0 < 2)
  match h : b % 2 with
  | 0 => exact Or.inl (Eq.refl 0)
  | 1 => exact Or.inr (Eq.refl 1)
  | k + 2 =>
    rw [h] at hlt
    exact absurd (Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ hlt)) (Nat.not_lt_zero k)

theorem odd_sq_mod4 (m : Nat) : ((2 * m + 1) * (2 * m + 1)) % 4 = 1 := by
  rw [nat_sq2_add1 m, Nat.mul_add_mod]

theorem double_sq_eq (j k : Nat) : ((2 * j) * (2 * j) == 4 * k) = (j * j == k) := by
  rw [nat_sq2 j]
  cases hjk : (j * j == k)
  · have hne : j * j ≠ k := fun heq => by rw [heq, nat_beq_self k] at hjk; cases hjk
    have hne4 : 4 * (j * j) ≠ 4 * k := fun heq =>
      hne (Nat.eq_of_mul_eq_mul_left (by decide : 0 < 4) heq)
    exact nat_beq_false_of_ne hne4
  · rw [(nat_beq_iff_eq (j * j) k).mp hjk]
    exact nat_beq_self (4 * k)

theorem countPosSqRoots_double_div4 (k : Nat) :
    ∀ B : Nat, countPosSqRoots (2 * B) (4 * k) = countPosSqRoots B k
  | 0 => Eq.refl _
  | B + 1 => by
    have h2 : 2 * (B + 1) = 2 * B + 2 := Eq.refl _
    rw [h2]
    change (if ((2 * B + 2) * (2 * B + 2) == 4 * k) = true then 1 else 0) +
      ((if ((2 * B + 1) * (2 * B + 1) == 4 * k) = true then 1 else 0) +
        countPosSqRoots (2 * B) (4 * k)) =
      (if ((B + 1) * (B + 1) == k) = true then 1 else 0) + countPosSqRoots B k
    have hodd : (2 * B + 1) * (2 * B + 1) ≠ 4 * k := by
      intro heq
      have hm : ((2 * B + 1) * (2 * B + 1)) % 4 = (4 * k) % 4 := by rw [heq]
      rw [odd_sq_mod4 B, Nat.mul_mod_right] at hm
      cases hm
    rw [bool_cond_false (nat_beq_false_of_ne hodd), Nat.zero_add]
    have h2b2 : 2 * B + 2 = 2 * (B + 1) := Eq.refl _
    rw [h2b2, double_sq_eq (B + 1) k, countPosSqRoots_double_div4 k B]

theorem nat_mod8_cases (b : Nat) :
    b % 8 = 0 ∨ b % 8 = 1 ∨ b % 8 = 2 ∨ b % 8 = 3 ∨
    b % 8 = 4 ∨ b % 8 = 5 ∨ b % 8 = 6 ∨ b % 8 = 7 := by
  have hlt : b % 8 < 8 := Nat.mod_lt b (by decide : 0 < 8)
  match h : b % 8 with
  | 0 => exact Or.inl (Eq.refl 0)
  | 1 => exact Or.inr (Or.inl (Eq.refl 1))
  | 2 => exact Or.inr (Or.inr (Or.inl (Eq.refl 2)))
  | 3 => exact Or.inr (Or.inr (Or.inr (Or.inl (Eq.refl 3))))
  | 4 => exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl (Eq.refl 4)))))
  | 5 => exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl (Eq.refl 5))))))
  | 6 => exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl (Eq.refl 6)))))))
  | 7 => exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Eq.refl 7)))))))
  | k + 8 =>
    rw [h] at hlt
    have hk := Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ
      (Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ
      (Nat.lt_of_succ_lt_succ (Nat.lt_of_succ_lt_succ hlt)))))))
    exact absurd hk (Nat.not_lt_zero k)

theorem sq_mod8_cases (b : Nat) :
    (b * b) % 8 = 0 ∨ (b * b) % 8 = 1 ∨ (b * b) % 8 = 4 := by
  rw [Nat.mul_mod]
  cases nat_mod8_cases b with
  | inl h => rw [h]; exact Or.inl (Eq.refl _)
  | inr h => cases h with
    | inl h => rw [h]; exact Or.inr (Or.inl (Eq.refl _))
    | inr h => cases h with
      | inl h => rw [h]; exact Or.inr (Or.inr (Eq.refl _))
      | inr h => cases h with
        | inl h => rw [h]; exact Or.inr (Or.inl (Eq.refl _))
        | inr h => cases h with
          | inl h => rw [h]; exact Or.inl (Eq.refl _)
          | inr h => cases h with
            | inl h => rw [h]; exact Or.inr (Or.inl (Eq.refl _))
            | inr h => cases h with
              | inl h => rw [h]; exact Or.inr (Or.inr (Eq.refl _))
              | inr h => rw [h]; exact Or.inr (Or.inl (Eq.refl _))

theorem countPosSqRoots_mod8_ne (n : Nat) (h0 : n % 8 ≠ 0) (h1 : n % 8 ≠ 1) (h4 : n % 8 ≠ 4) :
    ∀ B : Nat, countPosSqRoots B n = 0
  | 0 => Eq.refl _
  | B + 1 => by
    have hne : (B + 1) * (B + 1) ≠ n := by
      intro heq
      have hm : ((B + 1) * (B + 1)) % 8 = n % 8 := by rw [heq]
      cases sq_mod8_cases (B + 1) with
      | inl c0 => rw [c0] at hm; exact h0 hm.symm
      | inr hc => cases hc with
        | inl c1 => rw [c1] at hm; exact h1 hm.symm
        | inr c4 => rw [c4] at hm; exact h4 hm.symm
    change (if ((B + 1) * (B + 1) == n) = true then 1 else 0) + countPosSqRoots B n = 0
    rw [bool_cond_false (nat_beq_false_of_ne hne), Nat.zero_add]
    exact countPosSqRoots_mod8_ne n h0 h1 h4 B

theorem nat_two_dvd_mul_succ : ∀ m : Nat, 2 * (m * (m + 1) / 2) = m * (m + 1)
  | 0 => Eq.refl _
  | m + 1 => by
    have hmul : (m + 1) * (m + 2) = m * (m + 1) + 2 * (m + 1) := by
      rw [Nat.mul_add (m + 1) m 2, Nat.mul_comm (m + 1) m, Nat.mul_comm (m + 1) 2]
    rw [hmul, Nat.add_mul_div_left (m * (m + 1)) (m + 1) (by decide : 0 < 2),
        Nat.mul_add, nat_two_dvd_mul_succ m]

theorem odd_sq_eq_tri (m : Nat) :
    (2 * m + 1) * (2 * m + 1) = 1 + 8 * (m * (m + 1) / 2) := by
  have h8 : 8 * (m * (m + 1) / 2) = 4 * (m * (m + 1)) := by
    have h42 : 8 = 4 * 2 := Eq.refl _
    rw [h42, Nat.mul_assoc, nat_two_dvd_mul_succ m]
  rw [h8, nat_sq2_add1 m, Nat.add_comm _ 1, Nat.mul_add m m 1, Nat.mul_one]

theorem countPosSqRoots_odd_tri (t : Nat) :
    ∀ B : Nat, countPosSqRoots (2 * B) (8 * t + 1) = countTriRoots B t
  | 0 => Eq.refl _
  | B + 1 => by
    have h2 : 2 * (B + 1) = 2 * B + 2 := Eq.refl _
    rw [h2]
    change (if ((2 * B + 2) * (2 * B + 2) == 8 * t + 1) = true then 1 else 0) +
      ((if ((2 * B + 1) * (2 * B + 1) == 8 * t + 1) = true then 1 else 0) +
        countPosSqRoots (2 * B) (8 * t + 1)) =
      (if (B * (B + 1) / 2 == t) = true then 1 else 0) + countTriRoots B t
    have heven : (2 * B + 2) * (2 * B + 2) ≠ 8 * t + 1 := by
      intro heq
      have hm : ((2 * B + 2) * (2 * B + 2)) % 4 = (8 * t + 1) % 4 := by rw [heq]
      have hL : (2 * B + 2) * (2 * B + 2) = 4 * ((B + 1) * (B + 1)) := by
        have h2b : 2 * B + 2 = 2 * (B + 1) := Eq.refl _
        rw [h2b, nat_sq2 (B + 1)]
      have hR : 8 * t + 1 = 4 * (2 * t) + 1 := by
        have h42 : 8 = 4 * 2 := Eq.refl _
        rw [h42, Nat.mul_assoc]
      rw [hL, hR, Nat.mul_mod_right, Nat.mul_add_mod] at hm
      cases hm
    rw [bool_cond_false (nat_beq_false_of_ne heven), Nat.zero_add]
    have hodd_beq : ((2 * B + 1) * (2 * B + 1) == 8 * t + 1) = (B * (B + 1) / 2 == t) := by
      rw [odd_sq_eq_tri B, Nat.add_comm 1 (8 * (B * (B + 1) / 2))]
      cases ht : (B * (B + 1) / 2 == t)
      · have hne : B * (B + 1) / 2 ≠ t := fun heq => by
          rw [heq, nat_beq_self t] at ht; cases ht
        have hne8 : 8 * (B * (B + 1) / 2) + 1 ≠ 8 * t + 1 := fun heq =>
          hne (Nat.eq_of_mul_eq_mul_left (by decide : 0 < 8) (Nat.succ.inj heq))
        exact nat_beq_false_of_ne hne8
      · rw [(nat_beq_iff_eq (B * (B + 1) / 2) t).mp ht]
        exact nat_beq_self (8 * t + 1)
    rw [hodd_beq, countPosSqRoots_odd_tri t B]

-- Theorem 1
theorem eq_d6899de389_all_n :
    ∀ n : Nat, phiCoeff n + seriesNeg phiCoeff n = 2 * dilateSeries phiCoeff 4 n := by
  intro n
  cases n with
  | zero => exact Eq.refl _
  | succ m =>
    dsimp [seriesNeg, dilateSeries]
    cases hmod2 : ((m + 1) % 2) with
    | zero =>
      change phiCoeff (m + 1) + phiCoeff (m + 1) =
        2 * (if (4 != 0 && (m + 1) % 4 == 0) = true then phiCoeff ((m + 1) / 4) else 0)
      have hmod4 : (m + 1) % 4 = 0 ∨ (m + 1) % 4 = 2 := by
        have hdiv : (m + 1) = 4 * ((m + 1) / 4) + (m + 1) % 4 := (Nat.div_add_mod (m + 1) 4).symm
        cases nat_mod4_cases (m + 1) with
        | inl c0 => exact Or.inl c0
        | inr c => cases c with
          | inl c1 =>
            have h12 : (m + 1) % 2 = (4 * ((m + 1) / 4) + 1) % 2 := by
              conv => lhs; rw [hdiv, c1]
            have h42 : 4 * ((m + 1) / 4) = 2 * (2 * ((m + 1) / 4)) := by
              rw [← Nat.mul_assoc]
            rw [h42, Nat.mul_add_mod, hmod2] at h12
            cases h12
          | inr c2 => cases c2 with
            | inl c2 => exact Or.inr c2
            | inr c3 =>
              have h12 : (m + 1) % 2 = (4 * ((m + 1) / 4) + 3) % 2 := by
                conv => lhs; rw [hdiv, c3]
              have h42 : 4 * ((m + 1) / 4) = 2 * (2 * ((m + 1) / 4)) := by
                rw [← Nat.mul_assoc]
              rw [h42, Nat.mul_add_mod, hmod2] at h12
              cases h12
      cases hmod4 with
      | inl h0 =>
        have hd4t : (4 != 0 && (m + 1) % 4 == 0) = true := by rw [h0]; exact Eq.refl _
        rw [bool_cond_true hd4t]
        let k := (m + 1) / 4
        have hk4 : m + 1 = 4 * k := by
          have hd := Nat.div_add_mod (m + 1) 4
          rw [h0, Nat.add_zero] at hd
          exact hd.symm
        have hk_pos : 1 ≤ k := by
          cases hk : ((m + 1) / 4) with
          | zero =>
            have hk0 : k = 0 := hk
            rw [hk0, Nat.mul_zero] at hk4
            cases hk4
          | succ k' =>
            change 1 ≤ (m + 1) / 4
            rw [hk]
            exact Nat.succ_le_succ (Nat.zero_le k')
        have hk_ne0 : (k == 0) = false :=
          nat_beq_false_of_ne (Nat.ne_of_gt hk_pos)
        dsimp [phiCoeff]
        change (2 * (countPosSqRoots (m + 1) (m + 1) : Int)) +
            (2 * (countPosSqRoots (m + 1) (m + 1) : Int)) =
          2 * (if (k == 0) = true then (1 : Int) else 2 * (countPosSqRoots k k : Int))
        rw [bool_cond_false hk_ne0]
        have hB : ∀ b, 2 * k < b → 4 * k < b * b := by
          intro b hb
          have h1 : (2 * k + 1) * (2 * k + 1) ≤ b * b := Nat.mul_le_mul hb hb
          have h2 : 4 * k < (2 * k + 1) * (2 * k + 1) := by
            rw [nat_sq2_add1 k, Nat.mul_add 4 (k * k) k]
            have hle1 : 4 * k ≤ 4 * (k * k) + 4 * k := Nat.le_add_left (4 * k) (4 * (k * k))
            exact Nat.lt_succ_of_le hle1
          exact Nat.lt_of_lt_of_le h2 h1
        have h2k_le_4k : 2 * k ≤ 4 * k := by
          have h4 : 4 * k = 2 * (2 * k) := by rw [← Nat.mul_assoc]
          rw [h4]
          exact Nat.le_mul_of_pos_left (2 * k) (by decide : 0 < 2)
        have hcnt : countPosSqRoots (m + 1) (m + 1) = countPosSqRoots k k := by
          rw [hk4, countPosSqRoots_mono_bound (2 * k) (4 * k) hB (4 * k) h2k_le_4k,
              countPosSqRoots_double_div4 k k]
        rw [hcnt]
        have hx : (2 * (countPosSqRoots k k : Int)) + (2 * (countPosSqRoots k k : Int)) =
            2 * (2 * (countPosSqRoots k k : Int)) := by
          have h2 : (2 : Int) = 1 + 1 := Eq.refl _
          conv => rhs; lhs; rw [h2]
          rw [Int.add_mul, Int.one_mul]
        exact hx
      | inr h2 =>
        have hd4f : (4 != 0 && (m + 1) % 4 == 0) = false := by rw [h2]; exact Eq.refl _
        rw [bool_cond_false hd4f]
        dsimp [phiCoeff]
        rw [countPosSqRoots_mod4_eq2 (m + 1) h2 (m + 1)]
        exact Eq.refl _
    | succ r =>
      have hr_lt : (m + 1) % 2 < 2 := Nat.mod_lt (m + 1) (by decide : 0 < 2)
      rw [hmod2] at hr_lt
      have hr0 : r = 0 := Nat.eq_zero_of_le_zero (Nat.le_of_lt_succ (Nat.lt_of_succ_lt_succ hr_lt))
      rw [hr0] at hmod2
      rw [hr0]
      have hd4f : (4 != 0 && (m + 1) % 4 == 0) = false := by
        cases hc4 : ((m + 1) % 4 == 0)
        · exact Eq.refl _
        · have hdvd4 : (m + 1) % 4 = 0 := (nat_beq_iff_eq ((m + 1) % 4) 0).mp hc4
          have hdiv := Nat.div_add_mod (m + 1) 4
          rw [hdvd4, Nat.add_zero] at hdiv
          have h42 : 4 * ((m + 1) / 4) = 2 * (2 * ((m + 1) / 4)) := by
            rw [← Nat.mul_assoc]
          have hm0 : (m + 1) % 2 = 0 := by
            rw [← hdiv, h42, Nat.mul_mod_right]
          rw [hm0] at hmod2
          cases hmod2
      change phiCoeff (m + 1) + (-phiCoeff (m + 1)) =
        2 * (if (4 != 0 && (m + 1) % 4 == 0) = true then phiCoeff ((m + 1) / 4) else 0)
      rw [bool_cond_false hd4f, Int.add_right_neg, Int.mul_zero]

-- Theorem 2
theorem eq_c23aa45585_all_n :
    ∀ n : Nat, phiCoeff n - seriesNeg phiCoeff n = 4 * qShiftSeries 1 (dilateSeries psiCoeff 8) n := by
  intro n
  cases n with
  | zero => exact Eq.refl _
  | succ m =>
    dsimp [seriesNeg, qShiftSeries, dilateSeries]
    cases hmod2 : ((m + 1) % 2) with
    | zero =>
      change phiCoeff (m + 1) - phiCoeff (m + 1) =
        4 * (if (8 != 0 && m % 8 == 0) = true then psiCoeff (m / 8) else 0)
      rw [Int.sub_self]
      have hd8f : (8 != 0 && m % 8 == 0) = false := by
        cases hc8 : (m % 8 == 0)
        · exact Eq.refl _
        · have hm8 : m % 8 = 0 := (nat_beq_iff_eq (m % 8) 0).mp hc8
          have hd := Nat.div_add_mod m 8
          rw [hm8, Nat.add_zero] at hd
          have h82 : 8 * (m / 8) = 2 * (4 * (m / 8)) := by
            rw [← Nat.mul_assoc]
          have hm1 : (m + 1) % 2 = 1 := by
            rw [← hd, h82, Nat.mul_add_mod]
          rw [hm1] at hmod2
          cases hmod2
      rw [bool_cond_false hd8f, Int.mul_zero]
    | succ r =>
      have hr_lt : (m + 1) % 2 < 2 := Nat.mod_lt (m + 1) (by decide : 0 < 2)
      rw [hmod2] at hr_lt
      have hr0 : r = 0 := Nat.eq_zero_of_le_zero (Nat.le_of_lt_succ (Nat.lt_of_succ_lt_succ hr_lt))
      rw [hr0] at hmod2
      rw [hr0]
      change phiCoeff (m + 1) - (-phiCoeff (m + 1)) =
        4 * (if (8 != 0 && m % 8 == 0) = true then psiCoeff (m / 8) else 0)
      rw [Int.sub_eq_add_neg, Int.neg_neg]
      cases hmod8 : (m % 8) with
      | zero =>
        change phiCoeff (m + 1) + phiCoeff (m + 1) = 4 * psiCoeff (m / 8)
        let t := m / 8
        have ht8 : m = 8 * t := by
          have hd := Nat.div_add_mod m 8
          rw [hmod8, Nat.add_zero] at hd
          exact hd.symm
        dsimp [phiCoeff, psiCoeff]
        have hB : ∀ b, 2 * t + 1 < b → 8 * t + 1 < b * b := by
          intro b hb
          have h1 : (2 * t + 2) * (2 * t + 2) ≤ b * b := Nat.mul_le_mul hb hb
          have h2 : 8 * t + 1 < (2 * t + 2) * (2 * t + 2) := by
            have h2t : 2 * t + 2 = 2 * (t + 1) := Eq.refl _
            rw [h2t, nat_sq2 (t + 1)]
            have hsqt : (t + 1) * (t + 1) = t * t + 2 * t + 1 := by
              rw [Nat.add_mul, Nat.mul_add, Nat.mul_add, Nat.one_mul, Nat.mul_one]
              rw [Nat.add_assoc (t * t) t (t + 1), ← Nat.add_assoc t t 1, ← Nat.two_mul t,
                  ← Nat.add_assoc (t * t) (2 * t) 1]
            rw [hsqt, Nat.mul_add 4 (t * t + 2 * t) 1, Nat.mul_add 4 (t * t) (2 * t),
                ← Nat.mul_assoc 4 2 t]
            have hle1 : 8 * t + 1 ≤ 4 * (t * t) + 8 * t + 1 :=
              Nat.add_le_add_right (Nat.le_add_left (8 * t) (4 * (t * t))) 1
            have hlt4 : 4 * (t * t) + 8 * t + 1 < 4 * (t * t) + 8 * t + 4 :=
              Nat.add_lt_add_left (by decide : 1 < 4) (4 * (t * t) + 8 * t)
            exact Nat.lt_of_le_of_lt hle1 hlt4
          exact Nat.lt_of_lt_of_le h2 h1
        have h1 : 2 * t + 1 ≤ 8 * t + 1 :=
          Nat.add_le_add_right (Nat.mul_le_mul_right t (by decide : 2 ≤ 8)) 1
        have h2 : 2 * t + 1 ≤ 2 * (t + 1) :=
          Nat.le_succ (2 * t + 1)
        have hcnt : countPosSqRoots (m + 1) (m + 1) = countTriRoots (t + 1) t := by
          rw [ht8, countPosSqRoots_eq_of_bound (2 * t + 1) (8 * t + 1) (2 * (t + 1)) (8 * t + 1) hB h1 h2,
              countPosSqRoots_odd_tri t (t + 1)]
        rw [hcnt]
        have hx : 2 * (countTriRoots (t + 1) t : Int) + 2 * (countTriRoots (t + 1) t : Int) =
            4 * (countTriRoots (t + 1) t : Int) := by
          have h4 : (4 : Int) = 2 + 2 := Eq.refl _
          conv => rhs; lhs; rw [h4]
          rw [Int.add_mul]
        exact hx
      | succ rem =>
        have hrem_ne0 : m % 8 ≠ 0 := by rw [hmod8]; exact Nat.succ_ne_zero rem
        have hrem_beq : (rem + 1 == 0) = false := nat_beq_false_of_ne (Nat.succ_ne_zero rem)
        change phiCoeff (m + 1) + phiCoeff (m + 1) =
          4 * (if (true && (rem + 1 == 0)) = true then psiCoeff (m / 8) else 0)
        rw [hrem_beq]
        change phiCoeff (m + 1) + phiCoeff (m + 1) = 4 * 0
        rw [Int.mul_zero]
        have hm1_odd : (m + 1) % 2 = 1 := hmod2
        have hm1_ne0 : (m + 1) % 8 ≠ 0 := by
          intro h0
          have he2 : (m + 1) % 2 = 0 := by
            have hd := Nat.div_add_mod (m + 1) 8
            rw [h0, Nat.add_zero] at hd
            have h82 : 8 * ((m + 1) / 8) = 2 * (4 * ((m + 1) / 8)) := by rw [← Nat.mul_assoc]
            rw [← hd, h82, Nat.mul_mod_right]
          rw [he2] at hm1_odd
          cases hm1_odd
        have hm1_ne4 : (m + 1) % 8 ≠ 4 := by
          intro h4
          have he2 : (m + 1) % 2 = 0 := by
            have hd := Nat.div_add_mod (m + 1) 8
            rw [h4] at hd
            have h82 : 8 * ((m + 1) / 8) + 4 = 2 * (4 * ((m + 1) / 8) + 2) := by
              rw [Nat.mul_add, ← Nat.mul_assoc]
            rw [← hd, h82, Nat.mul_mod_right]
          rw [he2] at hm1_odd
          cases hm1_odd
        have hm1_ne1 : (m + 1) % 8 ≠ 1 := by
          intro h1
          have hd := Nat.div_add_mod (m + 1) 8
          rw [h1] at hd
          have hm8 : m = 8 * ((m + 1) / 8) := (Nat.succ.inj hd).symm
          have hm0 : m % 8 = 0 := by
            conv => lhs; rw [hm8]
            exact Nat.mul_mod_right 8 ((m + 1) / 8)
          exact hrem_ne0 hm0
        dsimp [phiCoeff]
        rw [countPosSqRoots_mod8_ne (m + 1) hm1_ne0 hm1_ne1 hm1_ne4 (m + 1)]
        exact Eq.refl _

-- Sum-vs-Product Bridge & Conditional JTP Universal ∀ n Lifts for eq_d6899de389 & eq_c23aa45585
def etaQuot_phi : EtaQuot := { factors := [(1, -2), (2, 5), (4, -2)] }
def etaQuot_phi_neg : EtaQuot := { factors := [(1, 2), (2, -1)] }
def etaQuot_psi : EtaQuot := { factors := [(1, -1), (2, 2)] }

def eq_d6899de389_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2)]), (1, 0, [(1, 2), (2, -1)])]

def eq_d6899de389_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(2, 0, [(4, -2), (8, 5), (16, -2)])]

def eq_c23aa45585_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2)]), (-1, 0, [(1, 2), (2, -1)])]

def eq_c23aa45585_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(4, 1, [(8, -1), (16, 2)])]

theorem etaQuot_phi_matches_phiCoeff_16 :
    (List.range 16).map phiCoeff = etaCoeffs etaQuot_phi 16 := by decide

theorem etaQuot_phi_neg_matches_seriesNeg_phiCoeff_16 :
    (List.range 16).map (seriesNeg phiCoeff) = etaCoeffs etaQuot_phi_neg 16 := by decide

theorem etaQuot_psi_matches_psiCoeff_16 :
    (List.range 16).map psiCoeff = etaCoeffs etaQuot_psi 16 := by decide

theorem eq_d6899de389_eta_all_n_of_jtp
    (h_phi : FPSEq (etaFPS etaQuot_phi) phiCoeff)
    (h_phi_neg : FPSEq (etaFPS etaQuot_phi_neg) (seriesNeg phiCoeff)) :
    ∀ n : Nat, evalLinearEtaFPS eq_d6899de389_lhs n = evalLinearEtaFPS eq_d6899de389_rhs n := by
  intro n
  have hphi4 : FPSEq (etaFPS (etaDilate etaQuot_phi 4)) (dilateFPS phiCoeff 4) :=
    FPSEq.trans
      (etaFPS_dilate etaQuot_phi (by decide) (by decide))
      (dilateFPS_congr h_phi 4)
  change (0 + 1 * etaFPS { factors := [(1, -2), (2, 5), (4, -2)] } n) +
      1 * etaFPS { factors := [(1, 2), (2, -1)] } n =
    0 + 2 * etaFPS { factors := [(4, -2), (8, 5), (16, -2)] } n
  rw [Int.zero_add, Int.one_mul, Int.one_mul, Int.zero_add]
  have h1 : etaFPS { factors := [(1, -2), (2, 5), (4, -2)] } n = phiCoeff n := h_phi n
  have h2 : etaFPS { factors := [(1, 2), (2, -1)] } n = seriesNeg phiCoeff n := h_phi_neg n
  have h3 : etaFPS { factors := [(4, -2), (8, 5), (16, -2)] } n = dilateSeries phiCoeff 4 n := hphi4 n
  rw [h1, h2, h3]
  exact eq_d6899de389_all_n n

theorem eq_c23aa45585_eta_all_n_of_jtp
    (h_phi : FPSEq (etaFPS etaQuot_phi) phiCoeff)
    (h_phi_neg : FPSEq (etaFPS etaQuot_phi_neg) (seriesNeg phiCoeff))
    (h_psi : FPSEq (etaFPS etaQuot_psi) psiCoeff) :
    ∀ n : Nat, evalLinearEtaFPS eq_c23aa45585_lhs n = evalLinearEtaFPS eq_c23aa45585_rhs n := by
  intro n
  have hpsi8 : FPSEq (etaFPS (etaDilate etaQuot_psi 8)) (dilateFPS psiCoeff 8) :=
    FPSEq.trans
      (etaFPS_dilate etaQuot_psi (by decide) (by decide))
      (dilateFPS_congr h_psi 8)
  change (0 + 1 * etaFPS { factors := [(1, -2), (2, 5), (4, -2)] } n) +
      (-1) * etaFPS { factors := [(1, 2), (2, -1)] } n =
    0 + 4 * (if n ≥ 1 then etaFPS { factors := [(8, -1), (16, 2)] } (n - 1) else 0)
  have hneg1 : ∀ x : Int, (-1 : Int) * x = -x := fun x => by
    have h : (-1 : Int) = -(1 : Int) := Eq.refl _
    rw [h, Int.neg_mul, Int.one_mul]
  rw [Int.zero_add, Int.one_mul, Int.zero_add,
      hneg1, ← Int.sub_eq_add_neg]
  have h1 : etaFPS { factors := [(1, -2), (2, 5), (4, -2)] } n = phiCoeff n := h_phi n
  have h2 : etaFPS { factors := [(1, 2), (2, -1)] } n = seriesNeg phiCoeff n := h_phi_neg n
  rw [h1, h2]
  by_cases hn : n ≥ 1
  · rw [if_pos hn]
    have h3 : etaFPS { factors := [(8, -1), (16, 2)] } (n - 1) = dilateSeries psiCoeff 8 (n - 1) :=
      hpsi8 (n - 1)
    rw [h3]
    have hr := eq_c23aa45585_all_n n
    dsimp [qShiftSeries] at hr
    rw [if_pos hn] at hr
    exact hr
  · rw [if_neg hn, Int.mul_zero]
    have hr := eq_c23aa45585_all_n n
    dsimp [qShiftSeries] at hr
    rw [if_neg hn, Int.mul_zero] at hr
    exact hr

-- Unmerged eta normalizations for eq_460927b577 and eq_2847c49f95
def ramanujan_f_pos : EtaQuot := { factors := [(1, -1), (2, 3), (4, -1)] }
def ramanujan_f_neg : EtaQuot := { factors := [(1, 1)] }
def ramanujan_psi_pos : EtaQuot := { factors := [(1, -1), (2, 2)] }
def ramanujan_psi_neg : EtaQuot := { factors := [(1, 1), (2, -1), (4, 1)] }
def ramanujan_chi_pos : EtaQuot := { factors := [(1, -1), (2, 2), (4, -1)] }
def ramanujan_chi_neg : EtaQuot := { factors := [(1, 1), (2, -1)] }
def etaQuotDiv24Ref : EtaQuot := { factors := [(1, -2), (2, 3), (4, -1)] }

theorem etaFPS_f_div_eq_ref :
    FPSEq (etaFPS (etaDiv ramanujan_f_pos ramanujan_f_neg)) (etaFPS etaQuotDiv24Ref) := by
  let e1 := etaFactorFPS (1, -1)
  let e23 := etaFactorFPS (2, 3)
  let e4 := etaFactorFPS (4, -1)
  let e12 := etaFactorFPS (1, -2)
  change FPSEq (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e23) e4) e1)
    (fpsMul (fpsMul (fpsMul fpsOne e12) e23) e4)
  have hL1 : FPSEq (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e23) e4) e1)
      (fpsMul (fpsMul (fpsMul e1 e23) e4) e1) :=
    fpsMul_congr (fpsMul_congr (fpsMul_congr (fpsMul_one_left e1) (FPSEq.refl e23)) (FPSEq.refl e4)) (FPSEq.refl e1)
  have hL2 : FPSEq (fpsMul (fpsMul (fpsMul e1 e23) e4) e1)
      (fpsMul (fpsMul e1 e23) (fpsMul e4 e1)) := fpsMul_assoc _ e4 e1
  have hL3 : FPSEq (fpsMul (fpsMul e1 e23) (fpsMul e4 e1))
      (fpsMul (fpsMul e1 e23) (fpsMul e1 e4)) :=
    fpsMul_congr (FPSEq.refl _) (fpsMul_comm e4 e1)
  have hL4 : FPSEq (fpsMul (fpsMul e1 e23) (fpsMul e1 e4))
      (fpsMul (fpsMul (fpsMul e1 e23) e1) e4) := (fpsMul_assoc _ e1 e4).symm
  have hL5 : FPSEq (fpsMul (fpsMul e1 e23) e1) (fpsMul (fpsMul e1 e1) e23) := by
    have a1 := fpsMul_assoc e1 e23 e1
    have a2 := fpsMul_congr (FPSEq.refl e1) (fpsMul_comm e23 e1)
    have a3 := (fpsMul_assoc e1 e1 e23).symm
    exact FPSEq.trans a1 (FPSEq.trans a2 a3)
  have hL6 : FPSEq (fpsMul (fpsMul (fpsMul e1 e23) e1) e4)
      (fpsMul (fpsMul e12 e23) e4) :=
    fpsMul_congr (FPSEq.trans hL5 (fpsMul_congr (fpsPowInt_neg1_neg1 (dilateFPS baseEtaFPS 1)) (FPSEq.refl e23))) (FPSEq.refl e4)
  have hR : FPSEq (fpsMul (fpsMul (fpsMul fpsOne e12) e23) e4) (fpsMul (fpsMul e12 e23) e4) :=
    fpsMul_congr (fpsMul_congr (fpsMul_one_left e12) (FPSEq.refl e23)) (FPSEq.refl e4)
  exact FPSEq.trans hL1 (FPSEq.trans hL2 (FPSEq.trans hL3 (FPSEq.trans hL4 (FPSEq.trans hL6 hR.symm))))

theorem etaFPS_psi_div_eq_ref :
    FPSEq (etaFPS (etaDiv ramanujan_psi_pos ramanujan_psi_neg)) (etaFPS etaQuotDiv24Ref) := by
  let e1 := etaFactorFPS (1, -1)
  let e22 := etaFactorFPS (2, 2)
  let e21 := etaFactorFPS (2, 1)
  let e23 := etaFactorFPS (2, 3)
  let e4 := etaFactorFPS (4, -1)
  let e12 := etaFactorFPS (1, -2)
  change FPSEq (fpsMul (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e22) e1) e21) e4)
    (fpsMul (fpsMul (fpsMul fpsOne e12) e23) e4)
  have h1 : FPSEq (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e22) e1) e21)
      (fpsMul (fpsMul (fpsMul e1 e22) e1) e21) :=
    fpsMul_congr (fpsMul_congr (fpsMul_congr (fpsMul_one_left e1) (FPSEq.refl e22)) (FPSEq.refl e1)) (FPSEq.refl e21)
  have h2 : FPSEq (fpsMul (fpsMul e1 e22) e1) (fpsMul e12 e22) := by
    have a1 := fpsMul_assoc e1 e22 e1
    have a2 := fpsMul_congr (FPSEq.refl e1) (fpsMul_comm e22 e1)
    have a3 := (fpsMul_assoc e1 e1 e22).symm
    have a4 := fpsMul_congr (fpsPowInt_neg1_neg1 (dilateFPS baseEtaFPS 1)) (FPSEq.refl e22)
    exact FPSEq.trans a1 (FPSEq.trans a2 (FPSEq.trans a3 a4))
  have h3 : FPSEq (fpsMul (fpsMul e12 e22) e21) (fpsMul e12 e23) :=
    FPSEq.trans (fpsMul_assoc e12 e22 e21)
      (fpsMul_congr (FPSEq.refl e12) (fpsPowInt_pos2_pos1 (dilateFPS baseEtaFPS 2)))
  have hL : FPSEq (fpsMul (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e22) e1) e21) e4)
      (fpsMul (fpsMul e12 e23) e4) :=
    fpsMul_congr (FPSEq.trans h1 (FPSEq.trans (fpsMul_congr h2 (FPSEq.refl e21)) h3)) (FPSEq.refl e4)
  have hR : FPSEq (fpsMul (fpsMul (fpsMul fpsOne e12) e23) e4) (fpsMul (fpsMul e12 e23) e4) :=
    fpsMul_congr (fpsMul_congr (fpsMul_one_left e12) (FPSEq.refl e23)) (FPSEq.refl e4)
  exact FPSEq.trans hL hR.symm

theorem etaFPS_chi_div_eq_ref :
    FPSEq (etaFPS (etaDiv ramanujan_chi_pos ramanujan_chi_neg)) (etaFPS etaQuotDiv24Ref) := by
  let e1 := etaFactorFPS (1, -1)
  let e22 := etaFactorFPS (2, 2)
  let e21 := etaFactorFPS (2, 1)
  let e23 := etaFactorFPS (2, 3)
  let e4 := etaFactorFPS (4, -1)
  let e12 := etaFactorFPS (1, -2)
  change FPSEq (fpsMul (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e22) e4) e1) e21)
    (fpsMul (fpsMul (fpsMul fpsOne e12) e23) e4)
  have h1 : FPSEq (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e22) e4) e1)
      (fpsMul (fpsMul (fpsMul e1 e22) e4) e1) :=
    fpsMul_congr (fpsMul_congr (fpsMul_congr (fpsMul_one_left e1) (FPSEq.refl e22)) (FPSEq.refl e4)) (FPSEq.refl e1)
  have h2 : FPSEq (fpsMul (fpsMul (fpsMul e1 e22) e4) e1)
      (fpsMul (fpsMul (fpsMul e1 e22) e1) e4) := by
    have a1 := fpsMul_assoc (fpsMul e1 e22) e4 e1
    have a2 := fpsMul_congr (FPSEq.refl (fpsMul e1 e22)) (fpsMul_comm e4 e1)
    have a3 := (fpsMul_assoc (fpsMul e1 e22) e1 e4).symm
    exact FPSEq.trans a1 (FPSEq.trans a2 a3)
  have h3 : FPSEq (fpsMul (fpsMul e1 e22) e1) (fpsMul e12 e22) := by
    have a1 := fpsMul_assoc e1 e22 e1
    have a2 := fpsMul_congr (FPSEq.refl e1) (fpsMul_comm e22 e1)
    have a3 := (fpsMul_assoc e1 e1 e22).symm
    have a4 := fpsMul_congr (fpsPowInt_neg1_neg1 (dilateFPS baseEtaFPS 1)) (FPSEq.refl e22)
    exact FPSEq.trans a1 (FPSEq.trans a2 (FPSEq.trans a3 a4))
  have hL123 : FPSEq (fpsMul (fpsMul (fpsMul (fpsMul (fpsMul fpsOne e1) e22) e4) e1) e21)
      (fpsMul (fpsMul (fpsMul e12 e22) e4) e21) :=
    fpsMul_congr (FPSEq.trans h1 (FPSEq.trans h2 (fpsMul_congr h3 (FPSEq.refl e4)))) (FPSEq.refl e21)
  have hswap : FPSEq (fpsMul (fpsMul (fpsMul e12 e22) e4) e21)
      (fpsMul (fpsMul (fpsMul e12 e22) e21) e4) := by
    have a1 := fpsMul_assoc (fpsMul e12 e22) e4 e21
    have a2 := fpsMul_congr (FPSEq.refl (fpsMul e12 e22)) (fpsMul_comm e4 e21)
    have a3 := (fpsMul_assoc (fpsMul e12 e22) e21 e4).symm
    exact FPSEq.trans a1 (FPSEq.trans a2 a3)
  have hmerge : FPSEq (fpsMul (fpsMul e12 e22) e21) (fpsMul e12 e23) :=
    FPSEq.trans (fpsMul_assoc e12 e22 e21)
      (fpsMul_congr (FPSEq.refl e12) (fpsPowInt_pos2_pos1 (dilateFPS baseEtaFPS 2)))
  have hR : FPSEq (fpsMul (fpsMul (fpsMul fpsOne e12) e23) e4) (fpsMul (fpsMul e12 e23) e4) :=
    fpsMul_congr (fpsMul_congr (fpsMul_one_left e12) (FPSEq.refl e23)) (FPSEq.refl e4)
  exact FPSEq.trans hL123 (FPSEq.trans hswap (FPSEq.trans (fpsMul_congr hmerge (FPSEq.refl e4)) hR.symm))

-- Theorem 3
theorem eq_460927b577_all_len :
    ∀ len : Nat, etaCoeffs (etaDiv ramanujan_f_pos ramanujan_f_neg) len =
      etaCoeffs (etaDiv ramanujan_psi_pos ramanujan_psi_neg) len :=
  etaCoeffs_eq_of_etaFPS_eq _ _
    (FPSEq.trans etaFPS_f_div_eq_ref etaFPS_psi_div_eq_ref.symm)

-- Theorem 4
theorem eq_2847c49f95_all_len :
    ∀ len : Nat, etaCoeffs (etaDiv ramanujan_psi_pos ramanujan_psi_neg) len =
      etaCoeffs (etaDiv ramanujan_chi_pos ramanujan_chi_neg) len :=
  etaCoeffs_eq_of_etaFPS_eq _ _
    (FPSEq.trans etaFPS_psi_div_eq_ref etaFPS_chi_div_eq_ref.symm)

-- -------------------------------------------------------------------------------
-- Requirement (b): Sturm-Bound Conditional All-n Upgrade for eq_0722eebfe8 (5–10)
-- -------------------------------------------------------------------------------

def isSquarefree (n : Nat) : Bool :=
  if n == 0 then false
  else (List.range (n + 1)).all (fun p =>
    if p ≥ 2 && n % (p * p) == 0 then false else true)

def dedekindPsi (N : Nat) : Nat :=
  if N == 0 then 0
  else (List.range (N + 1)).foldl (fun acc d =>
    if d > 0 && N % d == 0 && isSquarefree d then acc + N / d else acc) 0

def sturmBound (N k : Nat) : Nat :=
  (k * dedekindPsi N) / 12

def onoLevelDivisibleBool (eq : EtaQuot) (N : Nat) : Bool :=
  N > 0 && eq.factors.all (fun dr => dr.1 > 0 && N % dr.1 == 0)

def cuspOrderScaledPos (eq : EtaQuot) (N c : Nat) : Bool :=
  let s := eq.factors.foldl (fun acc dr =>
    acc + ((N / dr.1 : Nat) : Int) * ((Nat.gcd dr.1 c * Nat.gcd dr.1 c : Nat) : Int) * dr.2) 0
  decide (s ≥ 0)

def holomorphicAllCusps12 (eq : EtaQuot) : Bool :=
  ([1, 2, 3, 4, 6, 12] : List Nat).all (fun c => cuspOrderScaledPos eq 12 c)

def eq_0722eebfe8_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -3), (2, 6), (3, 1), (6, -2)]),
   (1, 0, [(1, 3), (2, -3), (3, -1), (4, 3), (6, 1), (12, -1)])]

def eq_0722eebfe8_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(2, 0, [(2, -3), (4, 6), (6, 1), (12, -2)])]

def padicValNatAux (p : Nat) : Nat → Nat → Nat
  | 0, _ => 0
  | fuel + 1, n =>
    if p ≤ 1 || n == 0 then 0
    else if n % p == 0 then 1 + padicValNatAux p fuel (n / p)
    else 0

def padicValNat (p n : Nat) : Nat :=
  padicValNatAux p n n

def etaPrimeExpSum (eq : EtaQuot) (p : Nat) : Int :=
  eq.factors.foldl (fun acc dr => acc + (padicValNat p dr.1 : Int) * dr.2) 0

def etaPrimeExpParity12 (eq : EtaQuot) : Nat × Nat :=
  ((etaPrimeExpSum eq 2).natAbs % 2, (etaPrimeExpSum eq 3).natAbs % 2)

def etaSqfreeKernel12 (eq : EtaQuot) : Nat :=
  let par := etaPrimeExpParity12 eq
  (if par.1 == 0 then 1 else 2) * (if par.2 == 0 then 1 else 3)

/-- General level-12 Nebentypus squarefree-part compatibility check:
    verifies every summand in `terms` shares identical prime-exponent parity
    `(v_2 % 2, v_3 % 2) = targetParity` (default `(0, 1)`, i.e., squarefree
    part `3`, yielding common character `χ(d) = (-3 / d)` at weight `k = 1`). -/
def etaNebentypusSqfree12 (terms : List (Int × Nat × List (Nat × Int)))
    (targetParity : Nat × Nat := (0, 1)) : Bool :=
  let targetKernel : Nat :=
    (if targetParity.1 == 0 then 1 else 2) * (if targetParity.2 == 0 then 1 else 3)
  match terms with
  | [] => true
  | t₀ :: _ =>
    let par₀ := etaPrimeExpParity12 { factors := t₀.2.2 }
    par₀ == targetParity &&
      terms.all (fun t =>
        let eq : EtaQuot := { factors := t.2.2 }
        etaPrimeExpParity12 eq == par₀ && etaSqfreeKernel12 eq == targetKernel)

def IsWeight1Level12EtaComb (terms : List (Int × Nat × List (Nat × Int))) : Bool :=
  etaNebentypusSqfree12 terms (0, 1) &&
  terms.all (fun t =>
    let eq : EtaQuot := { factors := t.2.2 }
    t.2.1 == 0 && weight2 eq == 2 && onoLevelDivisibleBool eq 12 &&
      onoSumDR eq == 0 && onoCong1 eq && onoCong2 eq 12 && holomorphicAllCusps12 eq)

def SturmBoundHolomorphicModularEq (N k : Nat) (f g : FPS) : Prop :=
  (∀ n : Nat, n ≤ sturmBound N k → f n = g n) → ∀ n : Nat, f n = g n

def SturmBoundHolomorphicModularEq12 (lhs rhs : List (Int × Nat × List (Nat × Int))) : Prop :=
  IsWeight1Level12EtaComb lhs = true →
  IsWeight1Level12EtaComb rhs = true →
  (∀ n : Nat, n ≤ sturmBound 12 1 → evalLinearEtaFPS lhs n = evalLinearEtaFPS rhs n) →
  ∀ n : Nat, evalLinearEtaFPS lhs n = evalLinearEtaFPS rhs n

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

-- Theorem 5
theorem dedekindPsi_12 : dedekindPsi 12 = 24 := by decide

-- Theorem 6
theorem sturmBound_12_k1 : sturmBound 12 1 = 2 := by decide

-- Theorem 7
theorem sturmBound_12_k1_lt_15 : sturmBound 12 1 < 15 := by decide

-- Theorem 8
theorem eq_0722eebfe8_modular_level12_weight1 :
    IsWeight1Level12EtaComb eq_0722eebfe8_lhs = true ∧
    IsWeight1Level12EtaComb eq_0722eebfe8_rhs = true := by decide

theorem eq_0722eebfe8_common_nebentypus_neg3 :
    etaNebentypusSqfree12 eq_0722eebfe8_lhs (0, 1) = true ∧
    etaNebentypusSqfree12 eq_0722eebfe8_rhs (0, 1) = true ∧
    etaSqfreeKernel12 { factors := [(1, -3), (2, 6), (3, 1), (6, -2)] } = 3 ∧
    etaSqfreeKernel12 { factors := [(1, 3), (2, -3), (3, -1), (4, 3), (6, 1), (12, -1)] } = 3 ∧
    etaSqfreeKernel12 { factors := [(2, -3), (4, 6), (6, 1), (12, -2)] } = 3 := by decide

-- Theorem 9
theorem eq_0722eebfe8_prefix_16 :
    evalLinearEta eq_0722eebfe8_lhs 16 = evalLinearEta eq_0722eebfe8_rhs 16 := by decide

-- Theorem 10
theorem eq_0722eebfe8_all_n_conditional
    (h_sturm : SturmBoundHolomorphicModularEq12 eq_0722eebfe8_lhs eq_0722eebfe8_rhs) :
    ∀ n : Nat, evalLinearEtaFPS eq_0722eebfe8_lhs n = evalLinearEtaFPS eq_0722eebfe8_rhs n := by
  apply h_sturm eq_0722eebfe8_modular_level12_weight1.1 eq_0722eebfe8_modular_level12_weight1.2
  intro n hn
  have h16 : n < 16 :=
    Nat.lt_trans (Nat.lt_of_le_of_lt hn sturmBound_12_k1_lt_15) (by decide : 15 < 16)
  rw [← evalLinearEta_getD_eq_FPS eq_0722eebfe8_lhs 16 n h16,
      ← evalLinearEta_getD_eq_FPS eq_0722eebfe8_rhs 16 n h16,
      eq_0722eebfe8_prefix_16]

-- -------------------------------------------------------------------------------
-- Requirement (c): Universal Algebraic Theorems Over Arbitrary EtaQuot Lists (11–18)
-- -------------------------------------------------------------------------------

theorem foldl_add_init {α : Type} (g : α → Int) :
    ∀ (xs : List α) (init : Int),
    xs.foldl (fun acc x => acc + g x) init = init + xs.foldl (fun acc x => acc + g x) 0
  | [], init => (Int.add_zero init).symm
  | x :: xs, init => by
    change xs.foldl (fun acc y => acc + g y) (init + g x) =
      init + xs.foldl (fun acc y => acc + g y) (0 + g x)
    rw [foldl_add_init g xs (init + g x), foldl_add_init g xs (0 + g x),
        Int.zero_add, Int.add_assoc]

theorem foldl_add_append {α : Type} (g : α → Int) (xs ys : List α) :
    (xs ++ ys).foldl (fun acc x => acc + g x) 0 =
    xs.foldl (fun acc x => acc + g x) 0 + ys.foldl (fun acc x => acc + g x) 0 := by
  rw [my_foldl_append]
  exact foldl_add_init g ys _

theorem foldl_add_map_neg {α : Type} (g h : α → Int)
    (hneg : ∀ x, h x = -g x) :
    ∀ (xs : List α),
    xs.foldl (fun acc x => acc + h x) 0 = -xs.foldl (fun acc x => acc + g x) 0
  | [] => Eq.refl _
  | x :: xs => by
    change xs.foldl (fun acc y => acc + h y) (0 + h x) =
      -xs.foldl (fun acc y => acc + g y) (0 + g x)
    rw [foldl_add_init h xs (0 + h x), foldl_add_init g xs (0 + g x),
        Int.zero_add, Int.zero_add, hneg x, foldl_add_map_neg g h hneg xs, Int.neg_add]

-- Theorem 11
theorem weight2_append (a b : EtaQuot) :
    weight2 (etaMul a b) = weight2 a + weight2 b :=
  foldl_add_append (fun dr : Nat × Int => dr.2) a.factors b.factors

-- Theorem 12
theorem onoSumDR_append (a b : EtaQuot) :
    onoSumDR (etaMul a b) = onoSumDR a + onoSumDR b :=
  foldl_add_append (fun dr : Nat × Int => (dr.1 : Int) * dr.2) a.factors b.factors

-- Theorem 13
theorem onoSumNOverDR_append (a b : EtaQuot) (N : Nat) :
    onoSumNOverDR (etaMul a b) N = onoSumNOverDR a N + onoSumNOverDR b N :=
  foldl_add_append (fun dr : Nat × Int => ((N / dr.1 : Nat) : Int) * dr.2) a.factors b.factors

-- Theorem 14
theorem weight2_invert (a : EtaQuot) :
    weight2 (etaInvert a) = -weight2 a := by
  dsimp [weight2, etaInvert]
  rw [my_foldl_map]
  exact foldl_add_map_neg (fun dr : Nat × Int => dr.2) (fun dr : Nat × Int => -dr.2)
    (fun _ => Eq.refl _) a.factors

-- Theorem 15
theorem onoSumDR_invert (a : EtaQuot) :
    onoSumDR (etaInvert a) = -onoSumDR a := by
  dsimp [onoSumDR, etaInvert]
  rw [my_foldl_map]
  exact foldl_add_map_neg (fun dr : Nat × Int => (dr.1 : Int) * dr.2)
    (fun dr : Nat × Int => (dr.1 : Int) * (-dr.2))
    (fun dr => Int.mul_neg (dr.1 : Int) dr.2) a.factors

-- Theorem 16
theorem onoSumNOverDR_invert (a : EtaQuot) (N : Nat) :
    onoSumNOverDR (etaInvert a) N = -onoSumNOverDR a N := by
  dsimp [onoSumNOverDR, etaInvert]
  rw [my_foldl_map]
  exact foldl_add_map_neg (fun dr : Nat × Int => ((N / dr.1 : Nat) : Int) * dr.2)
    (fun dr : Nat × Int => ((N / dr.1 : Nat) : Int) * (-dr.2))
    (fun dr => Int.mul_neg ((N / dr.1 : Nat) : Int) dr.2) a.factors

theorem int_emod24_add {x y : Int} (hx : x % 24 = 0) (hy : y % 24 = 0) :
    (x + y) % 24 = 0 := by
  rw [Int.add_emod, hx, hy]
  exact Eq.refl _

theorem int_emod24_neg {x : Int} (hx : x % 24 = 0) : (-x) % 24 = 0 := by
  have hdiv : x = (24 : Int) * (x / 24) := by
    have h := Int.mul_ediv_add_emod x 24
    rw [hx, Int.add_zero] at h
    exact h.symm
  rw [hdiv, ← Int.mul_neg]
  have h0 : (24 : Int) * -(x / 24) = 0 + 24 * -(x / 24) := (Int.zero_add _).symm
  rw [h0, Int.add_mul_emod_self_left]
  exact Eq.refl _

-- Theorem 17
theorem onoMod24_closed_append (a b : EtaQuot) (N : Nat)
    (h : onoCong1 a = true ∧ onoCong1 b = true ∧ onoCong2 a N = true ∧ onoCong2 b N = true) :
    onoCong1 (etaMul a b) = true ∧ onoCong2 (etaMul a b) N = true := by
  have h1a : onoSumDR a % 24 = 0 := (int_beq_iff_eq _ 0).mp h.1
  have h1b : onoSumDR b % 24 = 0 := (int_beq_iff_eq _ 0).mp h.2.1
  have h2a : onoSumNOverDR a N % 24 = 0 := (int_beq_iff_eq _ 0).mp h.2.2.1
  have h2b : onoSumNOverDR b N % 24 = 0 := (int_beq_iff_eq _ 0).mp h.2.2.2
  refine ⟨(int_beq_iff_eq _ 0).mpr ?_, (int_beq_iff_eq _ 0).mpr ?_⟩
  · rw [onoSumDR_append]; exact int_emod24_add h1a h1b
  · rw [onoSumNOverDR_append]; exact int_emod24_add h2a h2b

-- Theorem 18
theorem onoMod24_closed_invert (a : EtaQuot) (N : Nat)
    (h : onoCong1 a = true ∧ onoCong2 a N = true) :
    onoCong1 (etaInvert a) = true ∧ onoCong2 (etaInvert a) N = true := by
  have h1a : onoSumDR a % 24 = 0 := (int_beq_iff_eq _ 0).mp h.1
  have h2a : onoSumNOverDR a N % 24 = 0 := (int_beq_iff_eq _ 0).mp h.2
  refine ⟨(int_beq_iff_eq _ 0).mpr ?_, (int_beq_iff_eq _ 0).mpr ?_⟩
  · rw [onoSumDR_invert]; exact int_emod24_neg h1a
  · rw [onoSumNOverDR_invert]; exact int_emod24_neg h2a

-- -------------------------------------------------------------------------------
-- Requirement (d): Universal sym2_recurrence_int Over Int (Theorem 19)
-- -------------------------------------------------------------------------------

theorem sym2_bilinear_cancellation (a b x y z w : Int)
    (hw : w + a * z + b * x = 0) (hby : z + a * x + b * y = 0) :
    w * w + (b - a * a) * z * z + (a * a * b - b * b) * x * x + (-(b * b * b)) * y * y = 0 := by
  have hw' : w = -(a * z + b * x) := by
    rw [Int.add_assoc] at hw
    exact int_add_eq_zero_solve hw
  have hby' : b * y = -(z + a * x) := by
    rw [Int.add_comm (z + a * x) (b * y)] at hby
    exact int_add_eq_zero_solve hby
  have hw2 : w * w = (a * a) * (z * z) + 2 * a * b * z * x + (b * b) * (x * x) := by
    rw [hw', Int.neg_mul_neg, int_sq_sum (a * z) (b * x)]
    have t1 : (a * z) * (a * z) = (a * a) * (z * z) := int_mul4_swap23 a z a z
    have t2 : 2 * (a * z) * (b * x) = 2 * a * b * z * x := by
      rw [← Int.mul_assoc 2 a z, Int.mul_assoc (2 * a) z (b * x), Int.mul_comm z (b * x),
          Int.mul_assoc b x z, ← Int.mul_assoc (2 * a) b (x * z),
          Int.mul_comm x z, ← Int.mul_assoc (2 * a * b) z x]
    have t3 : (b * x) * (b * x) = (b * b) * (x * x) := int_mul4_swap23 b x b x
    rw [t1, t2, t3]
  have hb3y2 : b * ((b * y) * (b * y)) = b * (z * z) + 2 * a * b * z * x + (a * a * b) * (x * x) := by
    rw [hby', Int.neg_mul_neg, int_sq_sum z (a * x), Int.mul_add, Int.mul_add]
    have u2 : b * (2 * z * (a * x)) = 2 * a * b * z * x := by
      rw [Int.mul_assoc 2 z (a * x), Int.mul_comm z (a * x), Int.mul_assoc a x z,
          Int.mul_comm x z, ← Int.mul_assoc 2 a (z * x),
          ← Int.mul_assoc b (2 * a) (z * x), Int.mul_comm b (2 * a),
          ← Int.mul_assoc (2 * a * b) z x]
    have u3 : b * ((a * x) * (a * x)) = (a * a * b) * (x * x) := by
      rw [int_mul4_swap23 a x a x, ← Int.mul_assoc b (a * a) (x * x), Int.mul_comm b (a * a)]
    rw [u2, u3]
  have hby_lhs : b * ((b * y) * (b * y)) = (b * b * b) * (y * y) := by
    rw [int_mul4_swap23 b y b y, ← Int.mul_assoc b (b * b) (y * y), Int.mul_comm b (b * b)]
  have hdiff : w * w - (b * b * b) * (y * y) =
      (a * a - b) * (z * z) + (b * b - a * a * b) * (x * x) := by
    rw [← hby_lhs, hw2, hb3y2,
        int_add3_sub3_cancel_mid ((a * a) * (z * z)) (2 * a * b * z * x) ((b * b) * (x * x))
          (b * (z * z)) ((a * a * b) * (x * x)),
        Int.sub_mul, Int.sub_mul]
  have hneg_z : (b - a * a) * z * z = -((a * a - b) * (z * z)) := by
    rw [Int.mul_assoc (b - a * a) z z, ← Int.neg_mul, Int.neg_sub]
  have hneg_x : (a * a * b - b * b) * x * x = -((b * b - a * a * b) * (x * x)) := by
    rw [Int.mul_assoc (a * a * b - b * b) x x, ← Int.neg_mul, Int.neg_sub]
  have hneg_y : (-(b * b * b)) * y * y = -((b * b * b) * (y * y)) := by
    rw [Int.mul_assoc (-(b * b * b)) y y, Int.neg_mul]
  rw [hneg_z, hneg_x, hneg_y, Int.add_assoc (w * w) (-((a * a - b) * (z * z))) _,
      ← @Int.neg_add ((a * a - b) * (z * z)) ((b * b - a * a * b) * (x * x)), ← hdiff,
      @Int.sub_eq_add_neg (w * w) ((b * b * b) * (y * y)), Int.neg_add, Int.neg_neg,
      ← Int.add_assoc (w * w) (-(w * w)) ((b * b * b) * (y * y)),
      Int.add_right_neg, Int.zero_add, Int.add_right_neg]

-- Theorem 19
theorem sym2_recurrence_int (a b : Int) (u : Nat → Int)
    (hL2 : ∀ n, u (n + 2) + a * u (n + 1) + b * u n = 0) :
    ∃ A B C : Int, ∀ n,
      (u (n + 3)) * (u (n + 3)) + A * (u (n + 2)) * (u (n + 2)) +
      B * (u (n + 1)) * (u (n + 1)) + C * (u n) * (u n) = 0 :=
  ⟨b - a * a, a * a * b - b * b, -(b * b * b), fun n =>
    sym2_bilinear_cancellation a b (u (n + 1)) (u n) (u (n + 2)) (u (n + 3))
      (hL2 (n + 1)) (hL2 n)⟩

-- -------------------------------------------------------------------------------
-- Requirement (e): Exact Positive-Rational (ℚ⁺) T-Duality (Theorems 20–22)
-- -------------------------------------------------------------------------------

structure QPos where
  num : Nat
  den : Nat
  h_num : 0 < num
  h_den : 0 < den

def QPos.eq (x y : QPos) : Prop :=
  x.num * y.den = y.num * x.den

def QPos.add (x y : QPos) : QPos where
  num := x.num * y.den + y.num * x.den
  den := x.den * y.den
  h_num := Nat.lt_of_lt_of_le (Nat.mul_pos x.h_num y.h_den) (Nat.le_add_right _ _)
  h_den := Nat.mul_pos x.h_den y.h_den

def tDual (alpha_prime R : QPos) : QPos where
  num := alpha_prime.num * R.den
  den := alpha_prime.den * R.num
  h_num := Nat.mul_pos alpha_prime.h_num R.h_den
  h_den := Nat.mul_pos alpha_prime.h_den R.h_num

def symRadiusComb (alpha_prime R : QPos) : QPos :=
  QPos.add R (tDual alpha_prime R)

theorem QPos.eq_trans {x y z : QPos} (hxy : QPos.eq x y) (hyz : QPos.eq y z) :
    QPos.eq x z := by
  dsimp [QPos.eq] at *
  have hmul : (x.num * z.den) * y.den = (z.num * x.den) * y.den := by
    rw [nat_mul3_swap23 x.num z.den y.den, hxy, nat_mul3_swap23 y.num x.den z.den,
        hyz, nat_mul3_swap23 z.num y.den x.den]
  exact Nat.eq_of_mul_eq_mul_right y.h_den hmul

theorem QPos.add_comm (x y : QPos) : QPos.eq (QPos.add x y) (QPos.add y x) := by
  dsimp [QPos.eq, QPos.add]
  rw [Nat.add_comm (x.num * y.den) (y.num * x.den), Nat.mul_comm x.den y.den]

theorem QPos.add_congr_right {x y₁ y₂ : QPos} (hy : QPos.eq y₁ y₂) :
    QPos.eq (QPos.add x y₁) (QPos.add x y₂) := by
  dsimp [QPos.eq, QPos.add] at *
  rw [Nat.add_mul, Nat.add_mul]
  have h1 : (x.num * y₁.den) * (x.den * y₂.den) = (x.num * y₂.den) * (x.den * y₁.den) := by
    rw [nat_mul4_swap23 x.num y₁.den x.den y₂.den, Nat.mul_comm y₁.den y₂.den,
        ← nat_mul4_swap23 x.num y₂.den x.den y₁.den]
  have h2 : (y₁.num * x.den) * (x.den * y₂.den) = (y₂.num * x.den) * (x.den * y₁.den) := by
    rw [nat_mul4_swap13 y₁.num x.den x.den y₂.den, hy,
        nat_mul4_swap13 x.den x.den y₂.num y₁.den]
  rw [h1, h2]

-- Theorem 20
theorem tDual_involutive_exact (alpha_prime R : QPos) :
    QPos.eq (tDual alpha_prime (tDual alpha_prime R)) R := by
  dsimp [QPos.eq, tDual]
  rw [Nat.mul_assoc alpha_prime.num (alpha_prime.den * R.num) R.den,
      Nat.mul_assoc alpha_prime.den R.num R.den,
      ← Nat.mul_assoc alpha_prime.num alpha_prime.den (R.num * R.den),
      ← Nat.mul_assoc R.num alpha_prime.den (alpha_prime.num * R.den),
      nat_mul4_swap13 R.num alpha_prime.den alpha_prime.num R.den]

-- Theorem 21
theorem tDual_symmetric_invariant_exact (alpha_prime R : QPos) :
    QPos.eq (symRadiusComb alpha_prime (tDual alpha_prime R)) (symRadiusComb alpha_prime R) := by
  dsimp [symRadiusComb]
  exact QPos.eq_trans
    (QPos.add_congr_right (tDual_involutive_exact alpha_prime R))
    (QPos.add_comm (tDual alpha_prime R) R)

-- Theorem 22
theorem tDual_fixed_point_iff (alpha_prime R : QPos) :
    QPos.eq (tDual alpha_prime R) R ↔
      (R.num * R.num) * alpha_prime.den = alpha_prime.num * (R.den * R.den) := by
  dsimp [QPos.eq, tDual]
  have hL : (alpha_prime.num * R.den) * R.den = alpha_prime.num * (R.den * R.den) :=
    Nat.mul_assoc alpha_prime.num R.den R.den
  have hR : R.num * (alpha_prime.den * R.num) = (R.num * R.num) * alpha_prime.den := by
    rw [Nat.mul_comm alpha_prime.den R.num, ← Nat.mul_assoc]
  rw [hL, hR]
  exact ⟨Eq.symm, Eq.symm⟩

-- -------------------------------------------------------------------------------
-- Requirement (f): Live Kernel Refutation & Reclassification Certificates (23–49)
-- -------------------------------------------------------------------------------

-- Theorems 23–25: CFM Elliptic-Angle Falsification
theorem cfm_constant_ne_elliptic : (4 : Int) * 9 ≠ 16 * 3 := by decide
theorem cfm_elliptic_gap_exact : ratSub (16, 9) (4, 3) = (4, 9) := by decide
theorem cfm_elliptic_gap_nonzero : (ratSub (16, 9) (4, 3)).1 ≠ 0 := by decide

-- Theorems 26–31: M2 Alon–Boppana Falsification
theorem m2_alon_boppana_fail_p2_k3 :
    (1486214340235719 : Nat) ^ 2 > 4 * (3 - 1) * (250000000000000 : Nat) ^ 2 := by decide

theorem m2_alon_boppana_fail_p3_k4 :
    (1576404736640029 : Nat) ^ 2 > 4 * (4 - 1) * (200000000000000 : Nat) ^ 2 := by decide

theorem m2_alon_boppana_fail_p5_k6 :
    (5821844843783463 : Nat) ^ 2 > 4 * (6 - 1) * (500000000000000 : Nat) ^ 2 := by decide

theorem m2_alon_boppana_fail_actual_reg_p2 :
    (1486214340235719 : Nat) ^ 2 > 4 * (6 - 1) * (250000000000000 : Nat) ^ 2 := by decide

theorem m2_alon_boppana_fail_actual_reg_p3 :
    (1576404736640029 : Nat) ^ 2 > 4 * (8 - 1) * (200000000000000 : Nat) ^ 2 := by decide

theorem m2_alon_boppana_fail_actual_reg_p5 :
    (5821844843783463 : Nat) ^ 2 > 4 * (12 - 1) * (500000000000000 : Nat) ^ 2 := by decide

-- Theorems 32–35: S12 Exact Apéry Recurrence, K3 Mock Residual, & Nominal Elliptic/K3 Order
/-- Exact integer recurrence `u_n` of the Apéry `ζ(3)` sequence (`OEIS A005259`)
    recorded in `dualscale/refs/values.json` under `s12_recurrence`:
      `(n + 1)^3 u_{n+1} = (34 n^3 + 51 n^2 + 27 n + 5) u_n - n^3 u_{n-1}`
    with `u_0 = 1, u_1 = 5`.
    WARNING (Epistemic Tier X provenance note): `values.json`'s `s12_recurrence`
    is Apéry's order-3 sequence, and `dualscale/certificates/moduli_map/S12_vs_K3.json`
    and `S12_vs_elliptic.json` are Tier X mock-proxy checks generated by
    `check_C3b_moduli_map.py`, NOT an algebraic-geometric identification of `S12`
    with an order-2 elliptic ODE. -/
def s12RecurrenceSeq : Nat → Int
  | 0 => 1
  | 1 => 5
  | m + 2 =>
    let n : Int := (m + 1 : Nat)
    let uPrev := s12RecurrenceSeq m
    let uCurr := s12RecurrenceSeq (m + 1)
    let num := (34 * n * n * n + 51 * n * n + 27 * n + 5) * uCurr - n * n * n * uPrev
    let den := (n + 1) * (n + 1) * (n + 1)
    num / den

theorem s12_coeff_5_exact : s12RecurrenceSeq 5 = 819005 := by decide
theorem s12_k3_residual_exact : s12RecurrenceSeq 5 - 54000 = 765005 := by decide
theorem s12_k3_residual_nonzero : s12RecurrenceSeq 5 - 54000 ≠ 0 := by decide

/-- Nominal Picard–Fuchs ODE order of a second-order elliptic curve family. -/
def ellipticPfOrder : Nat := 2

/-- Nominal Picard–Fuchs ODE order of a third-order K3 Calabi–Yau 2-fold family. -/
def k3PfOrder : Nat := 3

/-- Nominal ODE-order inequality `2 ≠ 3` between second-order elliptic and
    third-order K3 Picard–Fuchs operators.
    WARNING: This purely compares the nominal integers `ellipticPfOrder` and
    `k3PfOrder`; `values.json`'s `s12_recurrence` is Apéry's order-3 sequence
    and `S12_vs_K3.json` / `S12_vs_elliptic.json` are Tier X mock-proxy checks
    (`check_C3b_moduli_map.py`), so this lemma makes no claim about `S12`. -/
theorem elliptic_pf_order_ne_k3 : ellipticPfOrder ≠ k3PfOrder := by decide

-- Theorems 36–49: 14 Refuted Campaign v2 OCR Typos

-- Typo 01: NoteBook1/chapterVIII/p20 | \phi^2(x) - \phi^2(x^{25}) = 4x f(x^5) f(x^{20}) (q^2: 4 ≠ 0)
def typo01_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -4), (2, 10), (4, -4)]), (-1, 0, [(25, -4), (50, 10), (100, -4)])]
def typo01_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(4, 1, [(5, -1), (10, 3), (20, -1), (20, -1), (40, 3), (80, -1)])]
theorem typo01_refuted_q2 :
    (evalLinearEta typo01_lhs 3).getD 2 0 = 4 ∧
    (evalLinearEta typo01_rhs 3).getD 2 0 = 0 ∧
    evalLinearEta typo01_lhs 3 ≠ evalLinearEta typo01_rhs 3 := by decide

-- Typo 02: NoteBook1/chapterXV/p19 | \phi(x)\phi(-x) = \phi^2(x^4) (q^2: -4 ≠ 0)
def typo02_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2), (1, 2), (2, -1)])]
def typo02_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(4, -4), (8, 10), (16, -4)])]
theorem typo02_refuted_q2 :
    (evalLinearEta typo02_lhs 3).getD 2 0 = -4 ∧
    (evalLinearEta typo02_rhs 3).getD 2 0 = 0 ∧
    evalLinearEta typo02_lhs 3 ≠ evalLinearEta typo02_rhs 3 := by decide

-- Typo 03: NoteBook1/chapterXVI/p32 | \phi^3(x)/\phi(x^3) + 2\phi^3(x^2)/\phi(x^6) = 3\phi(x)\phi(x^3) (q^2: 24 ≠ 0)
def typo03_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -6), (2, 15), (4, -6), (3, 2), (6, -5), (12, 2)]),
   (2, 0, [(2, -6), (4, 15), (8, -6), (6, 2), (12, -5), (24, 2)])]
def typo03_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(3, 0, [(1, -2), (2, 5), (4, -2), (3, -2), (6, 5), (12, -2)])]
theorem typo03_refuted_q2 :
    (evalLinearEta typo03_lhs 3).getD 2 0 = 24 ∧
    (evalLinearEta typo03_rhs 3).getD 2 0 = 0 ∧
    evalLinearEta typo03_lhs 3 ≠ evalLinearEta typo03_rhs 3 := by decide

-- Typo 04: NoteBook1/chapterXVI/p4 | {3\phi(-x^9) - \phi(-x)}^3 = 8 \psi^3(x)/\phi(x^3) \phi(-x^3) (q^3: 8 ≠ 0)
def typo04_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(27, 0, [(9, 6), (18, -3)]),
   (-27, 0, [(9, 4), (18, -2), (1, 2), (2, -1)]),
   (9, 0, [(9, 2), (18, -1), (1, 4), (2, -2)]),
   (-1, 0, [(1, 6), (2, -3)])]
def typo04_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(8, 0, [(1, -3), (2, 6), (3, 2), (6, -5), (12, 2), (3, 2), (6, -1)])]
theorem typo04_refuted_q3 :
    (evalLinearEta typo04_lhs 4).getD 3 0 = 8 ∧
    (evalLinearEta typo04_rhs 4).getD 3 0 = 0 ∧
    evalLinearEta typo04_lhs 4 ≠ evalLinearEta typo04_rhs 4 := by decide

-- Typo 05: NoteBook1/chapterXVI/p49 | \phi(x)\phi(x^{27}) - \phi(-x)\phi(-x^{27}) = 4x f(-x^6)f(-x^{18}) + 4x^7\psi(x^9)\psi(x^{63}) (q^9: 4 ≠ 0)
def typo05_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2), (27, -2), (54, 5), (108, -2)]),
   (-1, 0, [(1, 2), (2, -1), (27, 2), (54, -1)])]
def typo05_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(4, 1, [(6, 1), (18, 1)]),
   (4, 7, [(9, -1), (18, 2), (63, -1), (126, 2)])]
theorem typo05_refuted_q9 :
    (evalLinearEta typo05_lhs 10).getD 9 0 = 4 ∧
    (evalLinearEta typo05_rhs 10).getD 9 0 = 0 ∧
    evalLinearEta typo05_lhs 10 ≠ evalLinearEta typo05_rhs 10 := by decide

-- Typo 06: NoteBook1/chapterXVI/p49 | \phi(x)\phi(x^{35}) - \phi(-x)\phi(-x^{35}) = 4x f(-x^{10})f(-x^{14}) + 4x^9\psi(x^7)\psi(x^{70}) (q^11: 0 ≠ -4)
def typo06_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2), (35, -2), (70, 5), (140, -2)]),
   (-1, 0, [(1, 2), (2, -1), (35, 2), (70, -1)])]
def typo06_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(4, 1, [(10, 1), (14, 1)]),
   (4, 9, [(7, -1), (14, 2), (70, -1), (140, 2)])]
theorem typo06_refuted_q11 :
    (evalLinearEta typo06_lhs 12).getD 11 0 = 0 ∧
    (evalLinearEta typo06_rhs 12).getD 11 0 = -4 ∧
    evalLinearEta typo06_lhs 12 ≠ evalLinearEta typo06_rhs 12 := by decide

-- Typo 07: NoteBook1/chapterXVI/p49 | \phi(x^7)\phi(x^7) - \phi(-x^7)\phi(-x^7) = 4x^3\psi(x^{10})\psi(x^{14}) - 2x^7 f(-x^{70})f(-x^{70}) (q^3: 0 ≠ 4)
def typo07_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(7, -4), (14, 10), (28, -4)]),
   (-1, 0, [(7, 4), (14, -2)])]
def typo07_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(4, 3, [(10, -1), (20, 2), (14, -1), (28, 2)]),
   (-2, 7, [(70, 2)])]
theorem typo07_refuted_q3 :
    (evalLinearEta typo07_lhs 4).getD 3 0 = 0 ∧
    (evalLinearEta typo07_rhs 4).getD 3 0 = 4 ∧
    evalLinearEta typo07_lhs 4 ≠ evalLinearEta typo07_rhs 4 := by decide

-- Typo 08: NoteBook1/chapterXVI/p72 | {\psi^4(x) + 3x\psi^4(x^2)}^2 / (\psi^2(x)\psi^2(x^2)) = {f^4(x) + 27x f^4(x^2)}^2 / (f^2(x)f^2(x^2)) (q^1: 12 ≠ 60)
def typo08_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -6), (2, 14), (4, -4)]),
   (6, 1, [(1, -2), (2, 2), (4, 4)]),
   (9, 2, [(1, 2), (2, -10), (4, 12)])]
def typo08_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -6), (2, 20), (4, -12), (8, 2)]),
   (54, 1, [(1, -2), (2, 4), (4, 4), (8, -2)]),
   (729, 2, [(1, 2), (2, -12), (4, 20), (8, -6)])]
theorem typo08_refuted_q1 :
    (evalLinearEta typo08_lhs 2).getD 1 0 = 12 ∧
    (evalLinearEta typo08_rhs 2).getD 1 0 = 60 ∧
    evalLinearEta typo08_lhs 2 ≠ evalLinearEta typo08_rhs 2 := by decide

-- Typo 09: NoteBook2/chapterXX/p1 | \phi(x)\phi(x^7) - \phi^2(x^3) = 2x\phi(x^2)\psi(x^7)\chi(x^3) (q^3: -4 ≠ 4)
def typo09_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2), (7, -2), (14, 5), (28, -2)]),
   (-1, 0, [(3, -4), (6, 10), (12, -4)])]
def typo09_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(2, 1, [(2, -2), (4, 5), (8, -2), (7, -1), (14, 2), (3, -1), (6, 2), (12, -1)])]
theorem typo09_refuted_q3 :
    (evalLinearEta typo09_lhs 4).getD 3 0 = -4 ∧
    (evalLinearEta typo09_rhs 4).getD 3 0 = 4 ∧
    evalLinearEta typo09_lhs 4 ≠ evalLinearEta typo09_rhs 4 := by decide

-- Typo 10: NoteBook2/chapterXX/p5 | \psi(x^3)\psi(x^5) - \psi(x^2)\psi(-x^5) = 2x^2\psi(x^4)\psi(x^{30}) (q^2: -1 ≠ 2)
def typo10_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(3, -1), (6, 2), (5, -1), (10, 2)]),
   (-1, 0, [(2, -1), (4, 2), (5, 1), (10, -1), (20, 1)])]
def typo10_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(2, 2, [(4, -1), (8, 2), (30, -1), (60, 2)])]
theorem typo10_refuted_q2 :
    (evalLinearEta typo10_lhs 3).getD 2 0 = -1 ∧
    (evalLinearEta typo10_rhs 3).getD 2 0 = 2 ∧
    evalLinearEta typo10_lhs 3 ≠ evalLinearEta typo10_rhs 3 := by decide

-- Typo 11: NoteBook2/chapterXX/p5 | \phi(x^6)\phi(-x^{10}) + 2x\psi(x^2)\psi(x^5) = \phi(x^6)\phi(x^{15}) (q^1: 2 ≠ 0)
def typo11_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(6, -2), (12, 5), (24, -2), (10, 2), (20, -1)]),
   (2, 1, [(2, -1), (4, 2), (5, -1), (10, 2)])]
def typo11_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(6, -2), (12, 5), (24, -2), (15, -2), (30, 5), (60, -2)])]
theorem typo11_refuted_q1 :
    (evalLinearEta typo11_lhs 2).getD 1 0 = 2 ∧
    (evalLinearEta typo11_rhs 2).getD 1 0 = 0 ∧
    evalLinearEta typo11_lhs 2 ≠ evalLinearEta typo11_rhs 2 := by decide

-- Typo 12: NoteBook2/chapterXX/p5 | \phi(-x^2)\phi(-x^{30}) + 2x^2\psi(x)\psi(x^{11}) = \phi(x^2)\phi(x^{15}) (q^2: 0 ≠ 2)
def typo12_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(2, 2), (4, -1), (30, 2), (60, -1)]),
   (2, 2, [(1, -1), (2, 2), (11, -1), (22, 2)])]
def typo12_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(2, -2), (4, 5), (8, -2), (15, -2), (30, 5), (60, -2)])]
theorem typo12_refuted_q2 :
    (evalLinearEta typo12_lhs 3).getD 2 0 = 0 ∧
    (evalLinearEta typo12_rhs 3).getD 2 0 = 2 ∧
    evalLinearEta typo12_lhs 3 ≠ evalLinearEta typo12_rhs 3 := by decide

-- Typo 13: NoteBook2/chapterXX/p9 | \phi(x)\phi(x^{35}) = \phi(x)\phi(x^{31}) + 4xf(x^{10})f(-x^{14}) + 4x^9\psi(x)\psi(x^{70}) (q^1: 2 ≠ 6)
def typo13_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2), (35, -2), (70, 5), (140, -2)])]
def typo13_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -2), (2, 5), (4, -2), (31, -2), (62, 5), (124, -2)]),
   (4, 1, [(10, -1), (20, 3), (40, -1), (14, 1)]),
   (4, 9, [(1, -1), (2, 2), (70, -1), (140, 2)])]
theorem typo13_refuted_q1 :
    (evalLinearEta typo13_lhs 2).getD 1 0 = 2 ∧
    (evalLinearEta typo13_rhs 2).getD 1 0 = 6 ∧
    evalLinearEta typo13_lhs 2 ≠ evalLinearEta typo13_rhs 2 := by decide

-- Typo 14: NoteBook2/chapterXXI/p4 | cleared invertible denominator \phi(x)(\phi(x)+\phi(-x)) vs \phi(-x) (q^0: 2 ≠ 1)
def typo14_lhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, -4), (2, 10), (4, -4)]),
   (1, 0, [(1, -2), (2, 5), (4, -2), (1, 2), (2, -1)])]
def typo14_rhs : List (Int × Nat × List (Nat × Int)) :=
  [(1, 0, [(1, 2), (2, -1)])]
theorem typo14_refuted_q0 :
    (evalLinearEta typo14_lhs 1).getD 0 0 = 2 ∧
    (evalLinearEta typo14_rhs 1).getD 0 0 = 1 ∧
    evalLinearEta typo14_lhs 1 ≠ evalLinearEta typo14_rhs 1 := by decide

-- -------------------------------------------------------------------------------
-- Requirement (g): RAMA Deep Burn Exact Kernel Invariants
-- -------------------------------------------------------------------------------

def deepBurnEta : EtaQuot :=
  { factors := [(1, 24), (2, 23), (3, -14), (4, -24), (5, -24), (6, -24),
                (7, -24), (8, -24), (9, -24), (10, -24), (11, -24), (12, -24)] }

theorem deepBurn_ceff_cusp0 : cEffCusp0 deepBurnEta = (-823, 2310) := by decide
theorem deepBurn_weight : modularWeight deepBurnEta = (-183, 2) := by decide
theorem deepBurn_E0 : groundStateShift deepBurnEta = (425, 6) := by decide
theorem deepBurn_ono_false : onoCong1 deepBurnEta = false := by decide
theorem deepBurn_prefix_10 :
    etaCoeffs deepBurnEta 10 = [1, -24, 229, -906, -1048, 24942, -78956, -114576, 1364463, -2221528] := by decide
theorem deepBurn_has_negative_coeff : (etaCoeffs deepBurnEta 10).getD 1 0 < 0 := by decide

-- ═══════════════════════════════════════════════════════════════════════════════
-- Section 3: Audited Axiom Footprints for All 63 Exported Theorems
-- ═══════════════════════════════════════════════════════════════════════════════

#print axioms dilateFPS_congr
#print axioms etaFPS_dilate
#print axioms eq_d6899de389_all_n
#print axioms etaQuot_phi_matches_phiCoeff_16
#print axioms etaQuot_phi_neg_matches_seriesNeg_phiCoeff_16
#print axioms etaQuot_psi_matches_psiCoeff_16
#print axioms eq_d6899de389_eta_all_n_of_jtp
#print axioms eq_c23aa45585_all_n
#print axioms eq_c23aa45585_eta_all_n_of_jtp
#print axioms eq_460927b577_all_len
#print axioms eq_2847c49f95_all_len
#print axioms dedekindPsi_12
#print axioms sturmBound_12_k1
#print axioms sturmBound_12_k1_lt_15
#print axioms eq_0722eebfe8_modular_level12_weight1
#print axioms eq_0722eebfe8_common_nebentypus_neg3
#print axioms eq_0722eebfe8_prefix_16
#print axioms eq_0722eebfe8_all_n_conditional
#print axioms weight2_append
#print axioms onoSumDR_append
#print axioms onoSumNOverDR_append
#print axioms weight2_invert
#print axioms onoSumDR_invert
#print axioms onoSumNOverDR_invert
#print axioms onoMod24_closed_append
#print axioms onoMod24_closed_invert
#print axioms sym2_recurrence_int
#print axioms tDual_involutive_exact
#print axioms tDual_symmetric_invariant_exact
#print axioms tDual_fixed_point_iff
#print axioms cfm_constant_ne_elliptic
#print axioms cfm_elliptic_gap_exact
#print axioms cfm_elliptic_gap_nonzero
#print axioms m2_alon_boppana_fail_p2_k3
#print axioms m2_alon_boppana_fail_p3_k4
#print axioms m2_alon_boppana_fail_p5_k6
#print axioms m2_alon_boppana_fail_actual_reg_p2
#print axioms m2_alon_boppana_fail_actual_reg_p3
#print axioms m2_alon_boppana_fail_actual_reg_p5
#print axioms s12_coeff_5_exact
#print axioms s12_k3_residual_exact
#print axioms s12_k3_residual_nonzero
#print axioms elliptic_pf_order_ne_k3
#print axioms typo01_refuted_q2
#print axioms typo02_refuted_q2
#print axioms typo03_refuted_q2
#print axioms typo04_refuted_q3
#print axioms typo05_refuted_q9
#print axioms typo06_refuted_q11
#print axioms typo07_refuted_q3
#print axioms typo08_refuted_q1
#print axioms typo09_refuted_q3
#print axioms typo10_refuted_q2
#print axioms typo11_refuted_q1
#print axioms typo12_refuted_q2
#print axioms typo13_refuted_q1
#print axioms typo14_refuted_q0
#print axioms deepBurn_ceff_cusp0
#print axioms deepBurn_weight
#print axioms deepBurn_E0
#print axioms deepBurn_ono_false
#print axioms deepBurn_prefix_10
#print axioms deepBurn_has_negative_coeff

end DualScale.AllNPropositions

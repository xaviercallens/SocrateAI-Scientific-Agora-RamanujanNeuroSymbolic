// Lean compiler output
// Module: DualScale.NS.DyadicShell
// Imports: public import Init public meta import Init public import Mathlib.Analysis.Calculus.FDeriv.Basic public import Mathlib.Analysis.Calculus.Deriv.Basic public import Mathlib.Data.Real.Basic public import Mathlib.Data.Complex.Basic public import Mathlib.Tactic.Ring
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* lp_mathlib_Nat_cast___at___00Nat_cast___at___00Nat_cast___at___00NNReal_instSemiring_spec__2_spec__3_spec__4(lean_object*);
lean_object* lp_mathlib_npowRec___at___00NNReal_instSemiring_spec__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dualscale_Nat_cast___at___00DualScale_NS_DyadicShell_k__n_spec__0(lean_object*);
static lean_once_cell_t lp_dualscale_DualScale_NS_DyadicShell_k__n___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_NS_DyadicShell_k__n___closed__0;
LEAN_EXPORT lean_object* lp_dualscale_DualScale_NS_DyadicShell_k__n(lean_object*);
LEAN_EXPORT lean_object* lp_dualscale_DualScale_NS_DyadicShell_k__n___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dualscale_Nat_cast___at___00DualScale_NS_DyadicShell_k__n_spec__0(lean_object* v_a_1_){
_start:
{
lean_object* v___x_2_; 
v___x_2_ = lp_mathlib_Nat_cast___at___00Nat_cast___at___00Nat_cast___at___00NNReal_instSemiring_spec__2_spec__3_spec__4(v_a_1_);
return v___x_2_;
}
}
static lean_object* _init_lp_dualscale_DualScale_NS_DyadicShell_k__n___closed__0(void){
_start:
{
lean_object* v___x_3_; lean_object* v___x_4_; 
v___x_3_ = lean_unsigned_to_nat(2u);
v___x_4_ = lp_mathlib_Nat_cast___at___00Nat_cast___at___00Nat_cast___at___00NNReal_instSemiring_spec__2_spec__3_spec__4(v___x_3_);
return v___x_4_;
}
}
LEAN_EXPORT lean_object* lp_dualscale_DualScale_NS_DyadicShell_k__n(lean_object* v_n_5_){
_start:
{
lean_object* v___x_6_; lean_object* v___x_7_; 
v___x_6_ = lean_obj_once(&lp_dualscale_DualScale_NS_DyadicShell_k__n___closed__0, &lp_dualscale_DualScale_NS_DyadicShell_k__n___closed__0_once, _init_lp_dualscale_DualScale_NS_DyadicShell_k__n___closed__0);
v___x_7_ = lp_mathlib_npowRec___at___00NNReal_instSemiring_spec__1(v_n_5_, v___x_6_);
return v___x_7_;
}
}
LEAN_EXPORT lean_object* lp_dualscale_DualScale_NS_DyadicShell_k__n___boxed(lean_object* v_n_8_){
_start:
{
lean_object* v_res_9_; 
v_res_9_ = lp_dualscale_DualScale_NS_DyadicShell_k__n(v_n_8_);
lean_dec(v_n_8_);
return v_res_9_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_Calculus_FDeriv_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_Calculus_Deriv_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Real_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Complex_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Tactic_Ring(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dualscale_DualScale_NS_DyadicShell(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_Calculus_FDeriv_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_Calculus_Deriv_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Data_Real_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Data_Complex_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Tactic_Ring(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif

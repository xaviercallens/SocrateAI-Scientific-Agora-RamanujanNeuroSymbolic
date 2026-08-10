// Lean compiler output
// Module: DualScale.NS.HypothesisU
// Imports: public import Init public meta import Init public import Mathlib.Data.Rat.Init public import Mathlib.Analysis.Calculus.FDeriv.Basic public import Mathlib.Analysis.Calculus.ContDiff.Basic public import Mathlib.MeasureTheory.Measure.Lebesgue.Basic public import Mathlib.MeasureTheory.Integral.Bochner.Basic public import Mathlib.Analysis.InnerProductSpace.PiL2 public import Mathlib.Analysis.InnerProductSpace.Basic public import Mathlib.Data.Real.Basic public import Mathlib.Analysis.Real.Sqrt
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
lean_object* lp_mathlib_Nat_cast___at___00Mathlib_Meta_NormNum_evalNNRealRPow_spec__0(lean_object*);
lean_object* l_Rat_div(lean_object*, lean_object*);
static lean_once_cell_t lp_dualscale_DualScale_NS_alphaPrime___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_NS_alphaPrime___closed__0;
static lean_once_cell_t lp_dualscale_DualScale_NS_alphaPrime___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_NS_alphaPrime___closed__1;
static lean_once_cell_t lp_dualscale_DualScale_NS_alphaPrime___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_NS_alphaPrime___closed__2;
LEAN_EXPORT lean_object* lp_dualscale_DualScale_NS_alphaPrime;
static lean_object* _init_lp_dualscale_DualScale_NS_alphaPrime___closed__0(void){
_start:
{
lean_object* v___x_1_; lean_object* v___x_2_; 
v___x_1_ = lean_unsigned_to_nat(1u);
v___x_2_ = lp_mathlib_Nat_cast___at___00Mathlib_Meta_NormNum_evalNNRealRPow_spec__0(v___x_1_);
return v___x_2_;
}
}
static lean_object* _init_lp_dualscale_DualScale_NS_alphaPrime___closed__1(void){
_start:
{
lean_object* v___x_3_; lean_object* v___x_4_; 
v___x_3_ = lean_unsigned_to_nat(100u);
v___x_4_ = lp_mathlib_Nat_cast___at___00Mathlib_Meta_NormNum_evalNNRealRPow_spec__0(v___x_3_);
return v___x_4_;
}
}
static lean_object* _init_lp_dualscale_DualScale_NS_alphaPrime___closed__2(void){
_start:
{
lean_object* v___x_5_; lean_object* v___x_6_; lean_object* v___x_7_; 
v___x_5_ = lean_obj_once(&lp_dualscale_DualScale_NS_alphaPrime___closed__1, &lp_dualscale_DualScale_NS_alphaPrime___closed__1_once, _init_lp_dualscale_DualScale_NS_alphaPrime___closed__1);
v___x_6_ = lean_obj_once(&lp_dualscale_DualScale_NS_alphaPrime___closed__0, &lp_dualscale_DualScale_NS_alphaPrime___closed__0_once, _init_lp_dualscale_DualScale_NS_alphaPrime___closed__0);
v___x_7_ = l_Rat_div(v___x_6_, v___x_5_);
return v___x_7_;
}
}
static lean_object* _init_lp_dualscale_DualScale_NS_alphaPrime(void){
_start:
{
lean_object* v___x_8_; 
v___x_8_ = lean_obj_once(&lp_dualscale_DualScale_NS_alphaPrime___closed__2, &lp_dualscale_DualScale_NS_alphaPrime___closed__2_once, _init_lp_dualscale_DualScale_NS_alphaPrime___closed__2);
return v___x_8_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Rat_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_Calculus_FDeriv_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_Calculus_ContDiff_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_MeasureTheory_Measure_Lebesgue_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_MeasureTheory_Integral_Bochner_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_InnerProductSpace_PiL2(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_InnerProductSpace_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Real_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_Real_Sqrt(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dualscale_DualScale_NS_HypothesisU(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Data_Rat_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_Calculus_FDeriv_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_Calculus_ContDiff_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_MeasureTheory_Measure_Lebesgue_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_MeasureTheory_Integral_Bochner_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_InnerProductSpace_PiL2(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_InnerProductSpace_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Data_Real_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_Real_Sqrt(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_dualscale_DualScale_NS_alphaPrime = _init_lp_dualscale_DualScale_NS_alphaPrime();
lean_mark_persistent(lp_dualscale_DualScale_NS_alphaPrime);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif

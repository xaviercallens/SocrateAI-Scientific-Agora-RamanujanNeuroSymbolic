// Lean compiler output
// Module: DualScale.SusyBreaking.Basic
// Imports: public import Init public meta import Init public import Mathlib.Data.Rat.Init public import Mathlib.Data.Real.Basic public import Mathlib.Tactic.Ring public import Mathlib.Tactic.NormNum public import Mathlib.Tactic.Linarith
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
lean_object* lean_nat_to_int(lean_object*);
lean_object* lean_int_neg(lean_object*);
lean_object* lean_int_add(lean_object*, lean_object*);
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(12) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__0 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__0_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(11) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__0_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__1 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__1_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__1_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__2 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__2_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(9) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__2_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__3 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__3_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(8) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__3_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__4 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__4_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(7) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__4_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__5 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__5_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(6) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__5_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__6 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__6_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(5) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__6_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__7 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__7_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(4) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__7_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__8 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__8_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(3) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__8_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__9 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__9_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__9_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__10 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__10_value;
static const lean_ctor_object lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1)),((lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__10_value)}};
static const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__11 = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__11_value;
LEAN_EXPORT const lean_object* lp_dualscale_DualScale_SusyBreaking_divisorLevels = (const lean_object*)&lp_dualscale_DualScale_SusyBreaking_divisorLevels___closed__11_value;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__1;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__2;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__3;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__5;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__6;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__7;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__8;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__9;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__10;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__11;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__12;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__13;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__14;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__15;
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__16;
LEAN_EXPORT lean_object* lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents;
LEAN_EXPORT lean_object* lp_dualscale_List_foldl___at___00DualScale_SusyBreaking_exponentSum_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dualscale_List_foldl___at___00DualScale_SusyBreaking_exponentSum_spec__0___boxed(lean_object*, lean_object*);
static lean_once_cell_t lp_dualscale_DualScale_SusyBreaking_exponentSum___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dualscale_DualScale_SusyBreaking_exponentSum___closed__0;
LEAN_EXPORT lean_object* lp_dualscale_DualScale_SusyBreaking_exponentSum(lean_object*);
LEAN_EXPORT lean_object* lp_dualscale_DualScale_SusyBreaking_exponentSum___boxed(lean_object*);
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0(void){
_start:
{
lean_object* v___x_38_; lean_object* v___x_39_; 
v___x_38_ = lean_unsigned_to_nat(24u);
v___x_39_ = lean_nat_to_int(v___x_38_);
return v___x_39_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__1(void){
_start:
{
lean_object* v___x_40_; lean_object* v___x_41_; 
v___x_40_ = lean_unsigned_to_nat(23u);
v___x_41_ = lean_nat_to_int(v___x_40_);
return v___x_41_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__2(void){
_start:
{
lean_object* v___x_42_; lean_object* v___x_43_; 
v___x_42_ = lean_unsigned_to_nat(14u);
v___x_43_ = lean_nat_to_int(v___x_42_);
return v___x_43_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__3(void){
_start:
{
lean_object* v___x_44_; lean_object* v___x_45_; 
v___x_44_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__2, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__2_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__2);
v___x_45_ = lean_int_neg(v___x_44_);
return v___x_45_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4(void){
_start:
{
lean_object* v___x_46_; lean_object* v___x_47_; 
v___x_46_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0);
v___x_47_ = lean_int_neg(v___x_46_);
return v___x_47_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__5(void){
_start:
{
lean_object* v___x_48_; lean_object* v___x_49_; lean_object* v___x_50_; 
v___x_48_ = lean_box(0);
v___x_49_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_50_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_50_, 0, v___x_49_);
lean_ctor_set(v___x_50_, 1, v___x_48_);
return v___x_50_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__6(void){
_start:
{
lean_object* v___x_51_; lean_object* v___x_52_; lean_object* v___x_53_; 
v___x_51_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__5, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__5_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__5);
v___x_52_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_53_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_53_, 0, v___x_52_);
lean_ctor_set(v___x_53_, 1, v___x_51_);
return v___x_53_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__7(void){
_start:
{
lean_object* v___x_54_; lean_object* v___x_55_; lean_object* v___x_56_; 
v___x_54_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__6, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__6_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__6);
v___x_55_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_56_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_56_, 0, v___x_55_);
lean_ctor_set(v___x_56_, 1, v___x_54_);
return v___x_56_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__8(void){
_start:
{
lean_object* v___x_57_; lean_object* v___x_58_; lean_object* v___x_59_; 
v___x_57_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__7, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__7_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__7);
v___x_58_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_59_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_59_, 0, v___x_58_);
lean_ctor_set(v___x_59_, 1, v___x_57_);
return v___x_59_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__9(void){
_start:
{
lean_object* v___x_60_; lean_object* v___x_61_; lean_object* v___x_62_; 
v___x_60_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__8, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__8_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__8);
v___x_61_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_62_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_62_, 0, v___x_61_);
lean_ctor_set(v___x_62_, 1, v___x_60_);
return v___x_62_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__10(void){
_start:
{
lean_object* v___x_63_; lean_object* v___x_64_; lean_object* v___x_65_; 
v___x_63_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__9, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__9_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__9);
v___x_64_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_65_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_65_, 0, v___x_64_);
lean_ctor_set(v___x_65_, 1, v___x_63_);
return v___x_65_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__11(void){
_start:
{
lean_object* v___x_66_; lean_object* v___x_67_; lean_object* v___x_68_; 
v___x_66_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__10, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__10_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__10);
v___x_67_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_68_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_68_, 0, v___x_67_);
lean_ctor_set(v___x_68_, 1, v___x_66_);
return v___x_68_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__12(void){
_start:
{
lean_object* v___x_69_; lean_object* v___x_70_; lean_object* v___x_71_; 
v___x_69_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__11, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__11_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__11);
v___x_70_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_71_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_71_, 0, v___x_70_);
lean_ctor_set(v___x_71_, 1, v___x_69_);
return v___x_71_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__13(void){
_start:
{
lean_object* v___x_72_; lean_object* v___x_73_; lean_object* v___x_74_; 
v___x_72_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__12, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__12_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__12);
v___x_73_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__4);
v___x_74_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_74_, 0, v___x_73_);
lean_ctor_set(v___x_74_, 1, v___x_72_);
return v___x_74_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__14(void){
_start:
{
lean_object* v___x_75_; lean_object* v___x_76_; lean_object* v___x_77_; 
v___x_75_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__13, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__13_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__13);
v___x_76_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__3, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__3_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__3);
v___x_77_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_77_, 0, v___x_76_);
lean_ctor_set(v___x_77_, 1, v___x_75_);
return v___x_77_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__15(void){
_start:
{
lean_object* v___x_78_; lean_object* v___x_79_; lean_object* v___x_80_; 
v___x_78_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__14, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__14_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__14);
v___x_79_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__1, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__1_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__1);
v___x_80_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_80_, 0, v___x_79_);
lean_ctor_set(v___x_80_, 1, v___x_78_);
return v___x_80_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__16(void){
_start:
{
lean_object* v___x_81_; lean_object* v___x_82_; lean_object* v___x_83_; 
v___x_81_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__15, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__15_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__15);
v___x_82_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__0);
v___x_83_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_83_, 0, v___x_82_);
lean_ctor_set(v___x_83_, 1, v___x_81_);
return v___x_83_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents(void){
_start:
{
lean_object* v___x_84_; 
v___x_84_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__16, &lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__16_once, _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents___closed__16);
return v___x_84_;
}
}
LEAN_EXPORT lean_object* lp_dualscale_List_foldl___at___00DualScale_SusyBreaking_exponentSum_spec__0(lean_object* v_x_85_, lean_object* v_x_86_){
_start:
{
if (lean_obj_tag(v_x_86_) == 0)
{
return v_x_85_;
}
else
{
lean_object* v_head_87_; lean_object* v_tail_88_; lean_object* v___x_89_; 
v_head_87_ = lean_ctor_get(v_x_86_, 0);
v_tail_88_ = lean_ctor_get(v_x_86_, 1);
v___x_89_ = lean_int_add(v_x_85_, v_head_87_);
lean_dec(v_x_85_);
v_x_85_ = v___x_89_;
v_x_86_ = v_tail_88_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dualscale_List_foldl___at___00DualScale_SusyBreaking_exponentSum_spec__0___boxed(lean_object* v_x_91_, lean_object* v_x_92_){
_start:
{
lean_object* v_res_93_; 
v_res_93_ = lp_dualscale_List_foldl___at___00DualScale_SusyBreaking_exponentSum_spec__0(v_x_91_, v_x_92_);
lean_dec(v_x_92_);
return v_res_93_;
}
}
static lean_object* _init_lp_dualscale_DualScale_SusyBreaking_exponentSum___closed__0(void){
_start:
{
lean_object* v___x_94_; lean_object* v___x_95_; 
v___x_94_ = lean_unsigned_to_nat(0u);
v___x_95_ = lean_nat_to_int(v___x_94_);
return v___x_95_;
}
}
LEAN_EXPORT lean_object* lp_dualscale_DualScale_SusyBreaking_exponentSum(lean_object* v_exps_96_){
_start:
{
lean_object* v___x_97_; lean_object* v___x_98_; 
v___x_97_ = lean_obj_once(&lp_dualscale_DualScale_SusyBreaking_exponentSum___closed__0, &lp_dualscale_DualScale_SusyBreaking_exponentSum___closed__0_once, _init_lp_dualscale_DualScale_SusyBreaking_exponentSum___closed__0);
v___x_98_ = lp_dualscale_List_foldl___at___00DualScale_SusyBreaking_exponentSum_spec__0(v___x_97_, v_exps_96_);
return v___x_98_;
}
}
LEAN_EXPORT lean_object* lp_dualscale_DualScale_SusyBreaking_exponentSum___boxed(lean_object* v_exps_99_){
_start:
{
lean_object* v_res_100_; 
v_res_100_ = lp_dualscale_DualScale_SusyBreaking_exponentSum(v_exps_99_);
lean_dec(v_exps_99_);
return v_res_100_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Rat_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Real_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Tactic_Ring(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Tactic_NormNum(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Tactic_Linarith(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dualscale_DualScale_SusyBreaking_Basic(uint8_t builtin) {
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
res = initialize_mathlib_Mathlib_Data_Real_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Tactic_Ring(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Tactic_NormNum(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Tactic_Linarith(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents = _init_lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents();
lean_mark_persistent(lp_dualscale_DualScale_SusyBreaking_susyBreakingExponents);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif

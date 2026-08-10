// Lean compiler output
// Module: DualScale
// Imports: public import Init public meta import Init public import DualScale.NS.HypothesisU public import DualScale.NS.Basic public import DualScale.SpectralGap.Basic public import DualScale.CFM.Basic public import DualScale.Phase.Basic public import DualScale.K3Lock.Basic
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
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dualscale_DualScale_NS_HypothesisU(uint8_t builtin);
lean_object* initialize_dualscale_DualScale_NS_Basic(uint8_t builtin);
lean_object* initialize_dualscale_DualScale_SpectralGap_Basic(uint8_t builtin);
lean_object* initialize_dualscale_DualScale_CFM_Basic(uint8_t builtin);
lean_object* initialize_dualscale_DualScale_Phase_Basic(uint8_t builtin);
lean_object* initialize_dualscale_DualScale_K3Lock_Basic(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dualscale_DualScale(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dualscale_DualScale_NS_HypothesisU(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dualscale_DualScale_NS_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dualscale_DualScale_SpectralGap_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dualscale_DualScale_CFM_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dualscale_DualScale_Phase_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dualscale_DualScale_K3Lock_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif

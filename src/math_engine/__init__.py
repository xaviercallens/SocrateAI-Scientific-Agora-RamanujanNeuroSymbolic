"""Exact arbitrary-precision q-series, Dedekind eta-quotient, and Ramanujan catalog math engine."""
from .exact_qseries import (
    CLASSICAL_CATALOG,
    compute_eta_invariants,
    eta_base_coeffs,
    eta_quotient_coeffs,
    invert_eta_quotient_exact,
    match_classical_catalog,
)

__all__ = [
    "CLASSICAL_CATALOG",
    "compute_eta_invariants",
    "eta_base_coeffs",
    "eta_quotient_coeffs",
    "invert_eta_quotient_exact",
    "match_classical_catalog",
]

"""
src/math_engine/latex_symbolic_parser.py
========================================
Zero-token deterministic symbolic parser and exact q-series evaluator for
Ramanujan's authentic notebook & Lost Notebook LaTeX notation:

Supported Ramanujan Theta / Eta Dictionary (Berndt, Part III, Ch. 16):
  f(-q^d)  = prod_{n>=1}(1 - q^{dn})          -> {d: 1}
  f(q^d)   = prod_{n>=1}(1 + (-1)^{n-1}q^{dn}) -> {d: -1, 2d: 3, 4d: -1}
  phi(q^d) = sum q^{d n^2}                    -> {d: -2, 2d: 5, 4d: -2}
  phi(-q^d)= sum (-1)^n q^{d n^2}             -> {d: 2, 2d: -1}
  psi(q^d) = sum q^{d n(n+1)/2}               -> {d: -1, 2d: 2}
  psi(-q^d)= sum (-1)^{n(n+1)/2} q^{dn(n+1)/2}-> {d: 1, 2d: -1, 4d: 1}
  chi(q^d) = prod_{n>=0}(1 + q^{d(2n+1)})     -> {d: -1, 2d: 2, 4d: -1}
  chi(-q^d)= prod_{n>=0}(1 - q^{d(2n+1)})     -> {d: 1, 2d: -1}
  eta(d*t) = prod_{n>=1}(1 - q^{dn})          -> {d: 1}  (q-product part)

Capabilities:
  1. Parses algebraic LaTeX expressions built from `+`, `-`, `*`, `\frac{A}{B}`,
     powers `^k`, integer constants, variable shifts `q^m` / `x^m`, and the
     Ramanujan theta/eta atoms above into a clean exact AST (`Expr`).
  2. Extracts exact single Dedekind eta-quotient exponent dicts `{d: r_d}` from
     pure multiplicative sub-expressions (monomials / fractions).
  3. Evaluates BOTH sides of `LHS = RHS` equations to exact arbitrary-precision
     integer power series mod q^N (`N = 30`), proving or refuting the transcribed
     identity with ZERO floating-point error (automatically catching OCR typos!).
  4. Recognizes canonical Ramanujan mock theta & Rogers-Ramanujan infinite sums
     and exact infinite products `(1 - x)(1 - x^2)(1 - x^3)...`.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from src.math_engine.exact_qseries import (
    CLASSICAL_CATALOG,
    eta_quotient_coeffs,
    poly_add_int,
    poly_inv_int,
    poly_mul_int,
    poly_pow_int,
)


# ---------------------------------------------------------------------------
# Ramanujan theta/eta atom -> exact Dedekind eta-quotient exponent mapping
# ---------------------------------------------------------------------------


def ramanujan_atom_to_eta(func: str, sign: int, d: int) -> Dict[int, int]:
    """Map Ramanujan's f, phi, psi, chi, eta at (±q^d) to exact {divisor: exp}."""
    if d <= 0:
        raise ValueError(f"Divisor must be positive, got {d}")
    fn = func.lower()
    if fn == "f":
        if sign < 0:
            return {d: 1}
        return {d: -1, 2 * d: 3, 4 * d: -1}
    if fn == "phi":
        if sign > 0:
            return {d: -2, 2 * d: 5, 4 * d: -2}
        return {d: 2, 2 * d: -1}
    if fn == "psi":
        if sign > 0:
            return {d: -1, 2 * d: 2}
        return {d: 1, 2 * d: -1, 4 * d: 1}
    if fn == "chi":
        if sign > 0:
            return {d: -1, 2 * d: 2, 4 * d: -1}
        return {d: 1, 2 * d: -1}
    if fn == "eta":
        if sign > 0:
            return {d: 1}
        raise ValueError("Negative argument to eta not supported")
    raise ValueError(f"Unknown Ramanujan atom {func!r}")


# ---------------------------------------------------------------------------
# Exact Rational Power Series Evaluation (exact Fraction coeffs mod q^N)
# ---------------------------------------------------------------------------


def _q_add(a: List[Fraction], b: List[Fraction], N: int) -> List[Fraction]:
    return [a[i] + b[i] for i in range(N)]


def _q_sub(a: List[Fraction], b: List[Fraction], N: int) -> List[Fraction]:
    return [a[i] - b[i] for i in range(N)]


def _q_neg(a: List[Fraction], N: int) -> List[Fraction]:
    return [-a[i] for i in range(N)]


def _q_mul(a: List[Fraction], b: List[Fraction], N: int) -> List[Fraction]:
    res = [Fraction(0)] * N
    for i in range(N):
        ai = a[i]
        if ai == 0:
            continue
        for j in range(N - i):
            bj = b[j]
            if bj != 0:
                res[i + j] += ai * bj
    return res


def _q_inv(a: List[Fraction], N: int) -> List[Fraction]:
    if not a or a[0] == 0:
        raise ZeroDivisionError("Cannot invert power series with zero constant term")
    a0 = a[0]
    res = [Fraction(0)] * N
    res[0] = Fraction(1) / a0
    for n in range(1, N):
        s = Fraction(0)
        for k in range(1, n + 1):
            if a[k] != 0 and res[n - k] != 0:
                s += a[k] * res[n - k]
        res[n] = -s / a0
    return res


def _q_pow(a: List[Fraction], exp: int, N: int) -> List[Fraction]:
    if exp == 0:
        out = [Fraction(0)] * N
        if N > 0:
            out[0] = Fraction(1)
        return out
    base = list(a)
    if exp < 0:
        base = _q_inv(base, N)
        exp = -exp
    res = [Fraction(0)] * N
    if N > 0:
        res[0] = Fraction(1)
    while exp > 0:
        if exp & 1:
            res = _q_mul(res, base, N)
        exp >>= 1
        if exp > 0:
            base = _q_mul(base, base, N)
    return res


def _q_shift(a: List[Fraction], k: int, N: int) -> List[Fraction]:
    """Multiply by q^k (supports negative k only if leading k terms are zero)."""
    if k == 0:
        return list(a)
    if k > 0:
        return [Fraction(0)] * min(k, N) + a[: max(0, N - k)]
    shift = -k
    if any(a[i] != 0 for i in range(min(shift, N))):
        raise ZeroDivisionError("Laurent pole encountered during negative q-shift")
    return a[shift:] + [Fraction(0)] * min(shift, N)


# ---------------------------------------------------------------------------
# AST & Recursive-Descent Parser for Ramanujan Theta/Eta LaTeX Expressions
# ---------------------------------------------------------------------------


@dataclass
class ConstNode:
    val: int


@dataclass
class QPowNode:
    exp: int


@dataclass
class EtaAtomNode:
    func: str
    sign: int
    d: int


@dataclass
class BinOpNode:
    op: str  # "+", "-", "*", "/"
    left: Any
    right: Any


@dataclass
class NegNode:
    child: Any


@dataclass
class PowNode:
    base: Any
    exp: int


ExprNode = Union[ConstNode, QPowNode, EtaAtomNode, BinOpNode, NegNode, PowNode]


def _preprocess_latex(s: str) -> str:
    """Normalize LaTeX formatting while preserving mathematical structure."""
    s = s.strip()
    # Reject anything with unsupported calculus/derivatives/elliptic/complex/ellipses/two-arg Ramanujan f(a,b)
    if re.search(r"\\int|\\sum|\\lim|\\sqrt|\\sin|\\cos|\\tan|\\log|\\ln|\\exp|\\pi|\\infty|e\^|\\dots|\\cdots|\.\.\.|\\&c|'|\b\\frac\{d\}|\\partial", s):
        return ""
    if re.search(r"f\s*(?:\^[0-9{}]*)?\s*\([^)]*,[^)]*\)", s):
        return ""  # Two-argument general Ramanujan theta f(a,b) is not an eta-quotient unless specialized
    # Reject OCR-corrupted functional notation like `x(x^3)` where `x` is misread `\chi`
    if re.search(r"(?<![A-Za-z])x\s*\(\s*-?x", s):
        return ""
    # Replace \left, \right, \cdot, \times, \, \; \! \quad spaces
    s = re.sub(r"\\left|\\right|\\big[lr]?|\\Big[lr]?", "", s)
    s = re.sub(r"\\cdot|\\times", "*", s)
    s = re.sub(r"\\[,;:!]|\\quad|\\qquad", " ", s)
    # Normalize \varphi -> \phi
    s = s.replace(r"\varphi", r"\phi")
    # Replace curly brackets used as grouping \{ ... \} -> ( ... )
    s = s.replace(r"\{", "(").replace(r"\}", ")")
    s = s.replace("[", "(").replace("]", ")")
    return s.strip()


def _detect_q_var(s: str) -> Optional[str]:
    """Detect whether the Ramanujan expression uses `q` or `x` as the nome variable."""
    has_q = bool(re.search(r"(?<![A-Za-z])q(?![A-Za-z])", s))
    has_x = bool(re.search(r"(?<![A-Za-z])x(?![A-Za-z])", s))
    if has_q and not has_x:
        return "q"
    if has_x and not has_q:
        return "x"
    return None


class _LatexExprParser:
    """Strict recursive-descent parser for Ramanujan theta/eta algebraic expressions."""

    def __init__(self, text: str, qvar: str):
        self.qvar = qvar
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _tokenize(self, text: str) -> List[Tuple[str, str]]:
        toks: List[Tuple[str, str]] = []
        i, n = 0, len(text)
        while i < n:
            ch = text[i]
            if ch.isspace():
                i += 1
                continue
            if ch == "\\":
                j = i + 1
                while j < n and text[j].isalpha():
                    j += 1
                cmd = text[i + 1 : j]
                if cmd == "frac":
                    toks.append(("FRAC", "frac"))
                elif cmd in ("phi", "psi", "chi", "eta"):
                    toks.append(("FUNC", cmd))
                else:
                    raise ValueError(f"Unsupported LaTeX command \\{cmd}")
                i = j
                continue
            if ch.isdigit():
                j = i
                while j < n and text[j].isdigit():
                    j += 1
                toks.append(("INT", text[i:j]))
                i = j
                continue
            if ch == "f" and (i + 1 < n and text[i + 1] in ("(", "^", " ")):
                toks.append(("FUNC", "f"))
                i += 1
                continue
            if ch == self.qvar:
                toks.append(("QVAR", ch))
                i += 1
                continue
            if ch in "+-*/^(){}":
                toks.append((ch, ch))
                i += 1
                continue
            raise ValueError(f"Unsupported character {ch!r}")
        return toks

    def peek(self) -> Optional[Tuple[str, str]]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected: Optional[str] = None) -> Tuple[str, str]:
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of input")
        tok = self.tokens[self.pos]
        if expected and tok[0] != expected:
            raise ValueError(f"Expected {expected}, got {tok}")
        self.pos += 1
        return tok

    def parse(self) -> ExprNode:
        node = self._parse_add()
        if self.peek() is not None:
            raise ValueError(f"Unexpected trailing token {self.peek()}")
        return node

    def _parse_add(self) -> ExprNode:
        node = self._parse_mul()
        while self.peek() and self.peek()[0] in ("+", "-"):
            op = self.consume()[0]
            rhs = self._parse_mul()
            node = BinOpNode(op, node, rhs)
        return node

    def _parse_mul(self) -> ExprNode:
        node = self._parse_unary()
        while self.peek() is not None:
            t = self.peek()[0]
            if t in ("*", "/"):
                op = self.consume()[0]
                rhs = self._parse_unary()
                node = BinOpNode(op, node, rhs)
            elif t in ("INT", "QVAR", "FUNC", "FRAC", "("):
                # Implicit multiplication: e.g., 4x\psi(x^8) or \phi(x)\phi(-x)
                rhs = self._parse_unary()
                node = BinOpNode("*", node, rhs)
            else:
                break
        return node

    def _parse_unary(self) -> ExprNode:
        if self.peek() and self.peek()[0] == "-":
            self.consume("-")
            return NegNode(self._parse_unary())
        if self.peek() and self.peek()[0] == "+":
            self.consume("+")
            return self._parse_unary()
        return self._parse_pow()

    def _parse_int_exponent(self) -> int:
        if self.peek() and self.peek()[0] == "{":
            self.consume("{")
            sign = 1
            if self.peek() and self.peek()[0] == "-":
                self.consume("-")
                sign = -1
            val = int(self.consume("INT")[1])
            self.consume("}")
            return sign * val
        sign = 1
        if self.peek() and self.peek()[0] == "-":
            self.consume("-")
            sign = -1
        return sign * int(self.consume("INT")[1])

    def _parse_pow(self) -> ExprNode:
        node = self._parse_atom()
        while self.peek() and self.peek()[0] == "^":
            self.consume("^")
            exp = self._parse_int_exponent()
            if abs(exp) > 24:
                raise ValueError(f"Exponent {exp} exceeds bound 24")
            node = PowNode(node, exp)
        return node

    def _parse_func_arg(self) -> Tuple[int, int]:
        """Parse (± q^d) or (± q) or (d * q) inside a Ramanujan function call."""
        self.consume("(")
        sign = 1
        if self.peek() and self.peek()[0] == "-":
            self.consume("-")
            sign = -1
        elif self.peek() and self.peek()[0] == "+":
            self.consume("+")
        # Support q^d or q
        if self.peek() and self.peek()[0] == "QVAR":
            self.consume("QVAR")
            d = 1
            if self.peek() and self.peek()[0] == "^":
                self.consume("^")
                d = self._parse_int_exponent()
        else:
            raise ValueError("Unsupported function argument")
        self.consume(")")
        if d <= 0 or d > 72:
            raise ValueError(f"Divisor {d} out of range 1..72")
        return sign, d

    def _parse_braced_group(self) -> ExprNode:
        self.consume("{")
        node = self._parse_add()
        self.consume("}")
        return node

    def _parse_atom(self) -> ExprNode:
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        kind, val = tok
        if kind == "INT":
            self.consume("INT")
            return ConstNode(int(val))
        if kind == "QVAR":
            self.consume("QVAR")
            return QPowNode(1)
        if kind == "FRAC":
            self.consume("FRAC")
            num = self._parse_braced_group()
            den = self._parse_braced_group()
            return BinOpNode("/", num, den)
        if kind == "FUNC":
            fn = self.consume("FUNC")[1]
            # Handle optional power right after function name: \psi^3(x) or f^2(-x^3)
            pre_exp = 1
            if self.peek() and self.peek()[0] == "^":
                self.consume("^")
                pre_exp = self._parse_int_exponent()
                if abs(pre_exp) > 24:
                    raise ValueError(f"Function exponent {pre_exp} exceeds bound 24")
            sign, d = self._parse_func_arg()
            atom: ExprNode = EtaAtomNode(fn, sign, d)
            return PowNode(atom, pre_exp) if pre_exp != 1 else atom
        if kind == "(":
            self.consume("(")
            node = self._parse_add()
            self.consume(")")
            return node
        if kind == "{":
            return self._parse_braced_group()
        raise ValueError(f"Unexpected token {tok}")


def parse_ramanujan_expr(latex: str, qvar: Optional[str] = None) -> Optional[ExprNode]:
    pre = _preprocess_latex(latex)
    if not pre:
        return None
    v = qvar or _detect_q_var(pre)
    if not v:
        return None
    # Must contain at least one Ramanujan theta/eta atom
    if not re.search(r"(\\phi|\\psi|\\chi|\\eta|(?<![A-Za-z])f\s*(?:\^|\())", pre):
        return None
    try:
        return _LatexExprParser(pre, v).parse()
    except Exception:
        return None


def eval_expr_qseries(node: ExprNode, N: int = 30) -> List[Fraction]:
    """Evaluate parsed Ramanujan AST to exact rational power series mod q^N."""
    if isinstance(node, ConstNode):
        res = [Fraction(0)] * N
        if N > 0:
            res[0] = Fraction(node.val)
        return res
    if isinstance(node, QPowNode):
        res = [Fraction(0)] * N
        if 0 <= node.exp < N:
            res[node.exp] = Fraction(1)
        return res
    if isinstance(node, EtaAtomNode):
        exps = ramanujan_atom_to_eta(node.func, node.sign, node.d)
        ints = eta_quotient_coeffs(exps, N)
        return [Fraction(x) for x in ints]
    if isinstance(node, NegNode):
        return _q_neg(eval_expr_qseries(node.child, N), N)
    if isinstance(node, PowNode):
        if isinstance(node.base, QPowNode):
            res = [Fraction(0)] * N
            p = node.base.exp * node.exp
            if p < 0:
                raise ZeroDivisionError("Negative q power")
            if p < N:
                res[p] = Fraction(1)
            return res
        return _q_pow(eval_expr_qseries(node.base, N), node.exp, N)
    if isinstance(node, BinOpNode):
        l = eval_expr_qseries(node.left, N)
        r = eval_expr_qseries(node.right, N)
        if node.op == "+":
            return _q_add(l, r, N)
        if node.op == "-":
            return _q_sub(l, r, N)
        if node.op == "*":
            return _q_mul(l, r, N)
        if node.op == "/":
            # Handle common q-power cancellation if denominator starts with zeros
            z = 0
            while z < N and r[z] == 0:
                z += 1
            if z == N:
                raise ZeroDivisionError("Division by zero series")
            if z > 0:
                l = _q_shift(l, -z, N)
                r = _q_shift(r, -z, N)
            return _q_mul(l, _q_inv(r, N), N)
    raise ValueError(f"Unsupported AST node {node}")


def extract_pure_eta_monomial(node: ExprNode) -> Optional[Tuple[Fraction, int, Dict[int, int]]]:
    """
    If `node` is a pure multiplicative product/quotient of constants, q-powers,
    and Ramanujan theta/eta atoms (no top-level additions), return
    (rational_scalar, q_shift_int, {d: r_d}). Otherwise return None.
    """
    if isinstance(node, ConstNode):
        if node.val == 0:
            return None
        return Fraction(node.val), 0, {}
    if isinstance(node, QPowNode):
        return Fraction(1), node.exp, {}
    if isinstance(node, EtaAtomNode):
        return Fraction(1), 0, ramanujan_atom_to_eta(node.func, node.sign, node.d)
    if isinstance(node, NegNode):
        sub = extract_pure_eta_monomial(node.child)
        if sub is None:
            return None
        return -sub[0], sub[1], sub[2]
    if isinstance(node, PowNode):
        sub = extract_pure_eta_monomial(node.base)
        if sub is None:
            return None
        c, qs, exps = sub
        if c == 0:
            return None
        c_pow = (c ** node.exp) if node.exp >= 0 else (Fraction(1) / (c ** (-node.exp)))
        return c_pow, qs * node.exp, {d: r * node.exp for d, r in exps.items() if r * node.exp != 0}
    if isinstance(node, BinOpNode) and node.op in ("*", "/"):
        l = extract_pure_eta_monomial(node.left)
        r = extract_pure_eta_monomial(node.right)
        if l is None or r is None:
            return None
        lc, lq, lexp = l
        rc, rq, rexp = r
        merged = dict(lexp)
        if node.op == "*":
            for d, e in rexp.items():
                merged[d] = merged.get(d, 0) + e
            merged = {d: e for d, e in sorted(merged.items()) if e != 0}
            return lc * rc, lq + rq, merged
        else:
            if rc == 0:
                return None
            for d, e in rexp.items():
                merged[d] = merged.get(d, 0) - e
            merged = {d: e for d, e in sorted(merged.items()) if e != 0}
            return lc / rc, lq - rq, merged
    return None


def collect_eta_monomials(node: ExprNode) -> List[Dict[int, int]]:
    """Collect all distinct non-empty pure eta-quotient sub-expressions from an AST."""
    found: List[Dict[int, int]] = []
    seen = set()

    def walk(n: ExprNode) -> None:
        m = extract_pure_eta_monomial(n)
        if m is not None and m[2]:
            key = tuple(sorted(m[2].items()))
            if key not in seen and all(d <= 72 and abs(r) <= 48 for d, r in key):
                seen.add(key)
                found.append(dict(key))
            return
        if isinstance(n, BinOpNode):
            walk(n.left)
            walk(n.right)
        elif isinstance(n, (NegNode, PowNode)):
            walk(n.child if isinstance(n, NegNode) else n.base)

    walk(node)
    return found


def expr_to_linear_eta_terms(node: ExprNode) -> Optional[List[Tuple[int, int, Dict[int, int]]]]:
    """
    Decompose an expression into a sum of integer-scaled shifted eta-quotients:
      sum_i (coeff_i * q^{shift_i} * prod_d eta(d*tau)^{r_d})
    Returns None if any term is non-integer-scaled or negative-shifted or non-linear.
    Used directly to generate standalone Lean 4 kernel proofs of `LHS = RHS` identities!
    """
    if isinstance(node, BinOpNode) and node.op in ("+", "-"):
        l = expr_to_linear_eta_terms(node.left)
        r = expr_to_linear_eta_terms(node.right)
        if l is None or r is None:
            return None
        if node.op == "-":
            r = [(-c, qs, exps) for c, qs, exps in r]
        return l + r

    m = extract_pure_eta_monomial(node)
    if m is not None:
        c, qs, exps = m
        if c.denominator == 1 and qs >= 0:
            return [(int(c.numerator), qs, exps)]
        return None

    # Expand small integer power of a sum, e.g., (3*phi(-x^9) - phi(-x))^3
    if isinstance(node, PowNode) and 1 <= node.exp <= 4:
        base_terms = expr_to_linear_eta_terms(node.base)
        if base_terms is None or len(base_terms) > 4:
            return None
        acc = list(base_terms)
        for _ in range(node.exp - 1):
            nxt: List[Tuple[int, int, Dict[int, int]]] = []
            for c1, q1, e1 in acc:
                for c2, q2, e2 in base_terms:
                    merged = dict(e1)
                    for d, r in e2.items():
                        merged[d] = merged.get(d, 0) + r
                    merged = {d: r for d, r in sorted(merged.items()) if r != 0}
                    nxt.append((c1 * c2, q1 + q2, merged))
            acc = nxt
        return acc

    if isinstance(node, BinOpNode) and node.op == "*":
        l = expr_to_linear_eta_terms(node.left)
        r = expr_to_linear_eta_terms(node.right)
        if l is not None and r is not None and len(l) * len(r) <= 12:
            out: List[Tuple[int, int, Dict[int, int]]] = []
            for c1, q1, e1 in l:
                for c2, q2, e2 in r:
                    merged = dict(e1)
                    for d, rv in e2.items():
                        merged[d] = merged.get(d, 0) + rv
                    merged = {d: rv for d, rv in sorted(merged.items()) if rv != 0}
                    out.append((c1 * c2, q1 + q2, merged))
            return out

    return None


# ---------------------------------------------------------------------------
# Pattern Recognizers for Classic Infinite Products & Mock Theta Sums
# ---------------------------------------------------------------------------


def match_symbolic_mock_or_product(latex: str) -> Optional[Dict[str, Any]]:
    """
    Recognize unambiguous classical Ramanujan mock theta series and Euler
    infinite products directly from faithful LaTeX transcriptions.
    """
    compact = re.sub(r"\s+", "", latex).replace("x", "q")

    # Exact Ramanujan Delta = eta(tau)^24 infinite product
    if re.search(r"\\\{\(1-q\)\(1-q\^2\)\(1-q\^3\)(\.\.\.|\\dots|\\cdots)\\\}\^\{?24\}?", compact):
        return {"kind": "eta_quotient", "exponents": {1: 24}, "catalog_key": "ramanujan_tau_delta"}

    # Exact infinite partition product 1 / prod(1-q^n)
    if re.search(r"\\frac\{1\}\{\(1-q\)\(1-q\^2\)\(1-q\^3\)(\.\.\.|\\dots|\\cdots)", compact) or re.search(
        r"1/\(\(1-q\)\(1-q\^2\)\(1-q\^3\)(\.\.\.|\\dots|\\cdots)", compact
    ):
        return {"kind": "eta_quotient", "exponents": {1: -1}, "catalog_key": "partition_p"}

    # Exact infinite Euler product prod(1-q^n) (must have ellipsis and not be in a quotient with another product)
    if re.search(r"\(1-q\)\(1-q\^2\)\(1-q\^3\)(\.\.\.|\\dots|\\cdots)", compact) and not re.search(
        r"\\frac\{|\b1/", compact
    ):
        return {"kind": "eta_quotient", "exponents": {1: 1}, "catalog_key": "euler_eta"}

    # Canonical mock theta & Rogers-Ramanujan series patterns from Lost Notebook / Last Letter
    patterns = [
        ("mock3_f", r"1\+\\frac\{q\}\{\(1\+q\)\^2\}\+\\frac\{q\^4\}\{\(1\+q\)\^2\(1\+q\^2\)\^2\}"),
        ("mock3_phi", r"1\+\\frac\{q\}\{1\+q\^2\}\+\\frac\{q\^4\}\{\(1\+q\^2\)\(1\+q\^4\)\}"),
        ("mock3_chi", r"1\+\\frac\{q\}\{1-q\+q\^2\}\+\\frac\{q\^4\}\{\(1-q\+q\^2\)\(1-q\^2\+q\^4\)\}"),
        ("mock3_omega", r"\\frac\{1\}\{\(1-q\)\^2\}\+\\frac\{q\^4\}\{\(1-q\)\^2\(1-q\^3\)\^2\}"),
        ("mock3_nu", r"\\frac\{1\}\{1\+q\}\+\\frac\{q\^2\}\{\(1\+q\)\(1\+q\^3\)\}"),
        ("mock5_f0", r"1\+\\frac\{q\}\{1\+q\}\+\\frac\{q\^4\}\{\(1\+q\)\(1\+q\^2\)\}"),
        ("mock5_F0", r"1\+\\frac\{q\^2\}\{1-q\}\+\\frac\{q\^8\}\{\(1-q\)\(1-q\^3\)\}"),
        ("mock5_f1", r"1\+\\frac\{q\^2\}\{1\+q\}\+\\frac\{q\^6\}\{\(1\+q\)\(1\+q\^2\)\}"),
        ("mock6_phi", r"1-\\frac\{q\(1-q\)\}\{\(1\+q\)\(1\+q\^2\)\}\+\\frac\{q\^4\(1-q\)\(1-q\^3\)\}\{\(1\+q\)\(1\+q\^2\)\(1\+q\^3\)\(1\+q\^4\)\}"),
        ("rogers_ramanujan_G", r"1\+\\frac\{q\}\{1-q\}\+\\frac\{q\^4\}\{\(1-q\)\(1-q\^2\)\}"),
        ("rogers_ramanujan_H", r"1\+\\frac\{q\^2\}\{1-q\}\+\\frac\{q\^6\}\{\(1-q\)\(1-q\^2\)\}"),
    ]
    for key, pat in patterns:
        if re.search(pat, compact):
            entry = CLASSICAL_CATALOG[key]
            return {
                "kind": "catalog_symbolic",
                "catalog_key": key,
                "name": entry["name"],
                "oeis": entry["oeis"],
                "category": entry["category"],
                "formula": entry["formula"],
                "reference": entry["reference"],
                "coeffs": entry["coeffs"],
            }
    return None


def analyze_latex_identity(latex: str, check_terms: int = 30) -> Dict[str, Any]:
    """
    Full deterministic symbolic analysis of one transcribed Ramanujan LaTeX identity.
    """
    result: Dict[str, Any] = {
        "verified_equation": None,
        "verified_equations": [],
        "refuted_equation": None,
        "extracted_eta_quotients": [],
        "symbolic_catalog_match": None,
    }

    # 1. Check canonical mock theta / Euler product patterns
    sym_match = match_symbolic_mock_or_product(latex)
    if sym_match:
        result["symbolic_catalog_match"] = sym_match
        if sym_match["kind"] == "eta_quotient":
            result["extracted_eta_quotients"].append(sym_match["exponents"])

    # 2. Split equations on `=` (supporting chained identities A = B = C and assignments v = ...)
    cleaned = re.sub(r"\\text\{[^}]*\}", "", latex).strip()
    parts = [p.strip() for p in cleaned.split("=") if p.strip()]

    qvar = _detect_q_var(re.sub(r"\\text\{[^}]*\}", "", latex))
    parsed_sides: List[Tuple[str, ExprNode]] = []
    for p in parts:
        ast = parse_ramanujan_expr(p, qvar=qvar)
        if ast is not None:
            parsed_sides.append((p, ast))

    # Check all adjacent parsed pairs in chained equations A = B = C
    for idx in range(len(parsed_sides) - 1):
        lhs_str, lhs_ast = parsed_sides[idx]
        rhs_str, rhs_ast = parsed_sides[idx + 1]
        if lhs_str == rhs_str:
            continue
        try:
            lhs_seq = eval_expr_qseries(lhs_ast, check_terms)
            rhs_seq = eval_expr_qseries(rhs_ast, check_terms)
            if lhs_seq == rhs_seq and any(x != 0 for x in lhs_seq):
                lhs_lin = expr_to_linear_eta_terms(lhs_ast)
                rhs_lin = expr_to_linear_eta_terms(rhs_ast)
                all_int = all(x.denominator == 1 for x in lhs_seq)
                eq_obj = {
                    "lhs_latex": lhs_str,
                    "rhs_latex": rhs_str,
                    "terms_verified": check_terms,
                    "series_coeffs": [int(x.numerator) for x in lhs_seq] if all_int else [str(x) for x in lhs_seq],
                    "lhs_linear_terms": lhs_lin,
                    "rhs_linear_terms": rhs_lin,
                    "lean_kernel_ready": bool(lhs_lin is not None and rhs_lin is not None and all_int),
                }
                result["verified_equations"].append(eq_obj)
                if result["verified_equation"] is None:
                    result["verified_equation"] = eq_obj
            elif lhs_seq != rhs_seq and result["refuted_equation"] is None:
                first_diff = next(i for i in range(check_terms) if lhs_seq[i] != rhs_seq[i])
                result["refuted_equation"] = {
                    "lhs_latex": lhs_str,
                    "rhs_latex": rhs_str,
                    "first_mismatch_power": first_diff,
                    "lhs_val": str(lhs_seq[first_diff]),
                    "rhs_val": str(rhs_seq[first_diff]),
                }
        except Exception:
            pass

    # 3. Extract pure eta-quotient monomials ONLY from non-refuted expressions,
    #    avoiding notational homonyms where a bare LHS symbol like `f(x) = ...`
    #    or `\chi(q) = <mock theta sum>` is merely a function name, not Ch.16 theta!
    is_mock_catalog = bool(
        sym_match and sym_match["kind"] == "catalog_symbolic"
    )
    if result["refuted_equation"] is None and not is_mock_catalog:
        seen = {tuple(sorted(e.items())) for e in result["extracted_eta_quotients"]}
        has_verified_eq = bool(result["verified_equations"])
        for side_str, ast in parsed_sides:
            # Reject bare single-atom generic function names (`f(x)`, `\phi(q)`, `\psi(x)`, `\chi(q)`)
            # unless validated as part of a verified multi-side theta equation
            if (
                not has_verified_eq
                and isinstance(ast, EtaAtomNode)
                and ast.sign > 0
                and ast.func in ("f", "phi", "psi", "chi")
            ):
                continue
            mono = extract_pure_eta_monomial(ast)
            candidates = [mono[2]] if (mono is not None and mono[2]) else collect_eta_monomials(ast)
            for exps in candidates:
                key = tuple(sorted(exps.items()))
                if key not in seen and len(exps) >= 1 and all(1 <= d <= 36 and 1 <= abs(r) <= 36 for d, r in key):
                    seen.add(key)
                    result["extracted_eta_quotients"].append(exps)

    return result

#!/usr/bin/env python3
"""
Zero-Token Deterministic Preflight & Verification Gate
======================================================
Runs all deterministic mathematical, formal-verification, test, security, and
hygiene checks locally using Python stdlib + existing repo tooling (0 LLM tokens).

Outputs a compact JSON payload designed to be fed directly into tiered LLM agents
(T0 flash_lite, T1 flash, T2 pro/inherit) so agents never waste tokens scanning
raw logs, PDFs, or thousands of temporary verify_*.lean files.

Usage:
    python3 .agents/skills/rigorous-math-workflow/scripts/preflight_audit.py --json
    python3 .agents/skills/rigorous-math-workflow/scripts/preflight_audit.py --summary
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]

# Regexes for anti-vacuity & soundness checks beyond basic `Prop := True`
RFL_TAUTOLOGY_RE = re.compile(
    r"^\s*(?:theorem|lemma)\s+([\w'!?]+)(?:(?!^\s*(?:theorem|lemma)\b)[\s\S]){0,240}?:\s*([^\n:=]+?)\s*=\s*\2\s*:=\s*by\s+rfl\b",
    re.MULTILINE,
)
ANY_BY_RFL_RE = re.compile(
    r"^\s*(?:theorem|lemma)\s+([\w'!?]+)(?:(?!^\s*(?:theorem|lemma)\b)[\s\S]){0,300}?:=\s*by\s+rfl\b",
    re.MULTILINE,
)
AXIOM_DECL_RE = re.compile(
    r"^[ \t]*(?:@\[[^\]]*\][ \t]*)*(?:private[ \t]+|protected[ \t]+|noncomputable[ \t]+|scoped[ \t]+)*"
    r"axiom[ \t]+([\w'!?]+)",
    re.MULTILINE,
)
SORRY_RE = re.compile(r"\bsorry\b")
GATE_DIRECTIVE_RE = re.compile(r"MATHESIS-GATE:")


def strip_lean_comments(text: str) -> str:
    out: list[str] = []
    i, n, depth, line_comment = 0, len(text), 0, False
    while i < n:
        ch = text[i]
        two = text[i : i + 2]
        if line_comment:
            out.append("\n" if ch == "\n" else " ")
            if ch == "\n":
                line_comment = False
            i += 1
        elif depth > 0:
            if two == "/-":
                depth += 1
                out.append("  ")
                i += 2
            elif two == "-/":
                depth -= 1
                out.append("  ")
                i += 2
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
        elif two == "/-":
            depth = 1
            out.append("  ")
            i += 2
        elif two == "--":
            line_comment = True
            out.append("  ")
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def run_cmd(cmd: list[str], env: dict[str, str] | None = None, timeout: int = 60) -> dict[str, Any]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=merged_env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        combined = (proc.stdout + "\n" + proc.stderr).strip()
        tail = "\n".join(combined.splitlines()[-12:]) if combined else ""
        return {"exit_code": proc.returncode, "passed": proc.returncode == 0, "tail": tail}
    except Exception as exc:
        return {"exit_code": -1, "passed": False, "tail": str(exc)}


def audit_lean_core() -> dict[str, Any]:
    """Scan core Lean files (excluding .lake and generated verify_*.lean)."""
    core_files: list[Path] = []
    verify_files: list[Path] = []
    for p in sorted(ROOT.rglob("*.lean")):
        if ".lake" in p.parts or "lake-packages" in p.parts or "lean_foundations" in p.parts:
            continue
        if p.name.startswith("verify_"):
            verify_files.append(p)
        else:
            core_files.append(p)

    axiom_files: dict[str, list[str]] = {}
    sorry_files: dict[str, int] = {}
    rfl_theorems: list[str] = []
    gated_modules: list[str] = []
    suspicious_ceff_files: list[str] = []

    for p in core_files:
        rel = str(p.relative_to(ROOT))
        raw = p.read_text(encoding="utf-8", errors="replace")
        clean = strip_lean_comments(raw)
        if GATE_DIRECTIVE_RE.search(raw):
            gated_modules.append(rel)
        axioms = [m.group(1) for m in AXIOM_DECL_RE.finditer(clean)]
        if axioms:
            axiom_files[rel] = axioms
        sorries = len(SORRY_RE.findall(clean))
        if sorries:
            sorry_files[rel] = sorries
        for m in ANY_BY_RFL_RE.finditer(clean):
            rfl_theorems.append(f"{rel}:{m.group(1)}")
        # Check for positive-sign cEff formula on eta-quotients
        if "def cEff" in clean and "+ (dr.2 : ℚ) / (dr.1 : ℚ)" in clean:
            suspicious_ceff_files.append(rel)

    # Sample stats on verify_*.lean without dumping their contents
    verify_stats = {"total": len(verify_files), "by_rfl": 0, "type_True": 0, "sorry": 0}
    for p in verify_files:
        txt = p.read_text(encoding="utf-8", errors="replace")
        if ":= by rfl" in txt:
            verify_stats["by_rfl"] += 1
        if ": True" in txt:
            verify_stats["type_True"] += 1
        if "sorry" in txt:
            verify_stats["sorry"] += 1

    lake_dir_present = (ROOT / "dualscale" / "lean" / ".lake").is_dir()

    return {
        "core_file_count": len(core_files),
        "gated_module_count": len(gated_modules),
        "axiom_total": sum(len(v) for v in axiom_files.values()),
        "axiom_files": axiom_files,
        "sorry_total": sum(sorry_files.values()),
        "sorry_files": sorry_files,
        "rfl_theorems": rfl_theorems,
        "suspicious_ceff_sign_files": suspicious_ceff_files,
        "verify_temp_files": verify_stats,
        "dualscale_lake_present": lake_dir_present,
    }


def audit_certificates() -> dict[str, Any]:
    """Cross-check CSV ledgers against JSON certificates for contradictions."""
    cert_dir = ROOT / "dualscale" / "certificates"
    csv_verdicts: dict[str, str] = {}
    ledger_csv = cert_dir / "ledger.csv"
    if ledger_csv.is_file():
        with ledger_csv.open("r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                prime = row.get("prime", "").strip()
                status = (row.get("status") or row.get("Status") or "").strip()
                if prime:
                    csv_verdicts[f"p{prime}"] = status

    json_verdicts: dict[str, dict[str, Any]] = {}
    contradictions: list[str] = []
    placeholders: list[str] = []
    spectral_dir = cert_dir / "spectral"
    if spectral_dir.is_dir():
        for jf in sorted(spectral_dir.glob("*_certificate.json")):
            data = json.loads(jf.read_text(encoding="utf-8"))
            key = jf.name.split("_")[0]
            verdict = data.get("verdict", "")
            note = data.get("details", {}).get("note", "")
            json_verdicts[key] = {"verdict": verdict, "k": data.get("details", {}).get("regularity_k")}
            if "PLACEHOLDER" in note.upper():
                placeholders.append(str(jf.relative_to(ROOT)))
            if key in csv_verdicts and csv_verdicts[key] != verdict:
                contradictions.append(
                    f"{key}: ledger.csv={csv_verdicts[key]} vs {jf.name}={verdict}"
                )

    return {
        "csv_verdicts": csv_verdicts,
        "json_verdicts": json_verdicts,
        "contradictions": contradictions,
        "placeholders": placeholders,
    }


def audit_database() -> dict[str, Any]:
    db_path = ROOT / "namagiri.db"
    if not db_path.is_file():
        return {"present": False}
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        total = cur.execute("SELECT COUNT(*) FROM discoveries").fetchone()[0]
        by_status = dict(
            cur.execute("SELECT lean_status, COUNT(*) FROM discoveries GROUP BY lean_status").fetchall()
        )
        vacuous = cur.execute(
            "SELECT COUNT(*) FROM discoveries WHERE lean_code LIKE '%:= by rfl%' OR lean_code LIKE '%: True%'"
        ).fetchone()[0]
        cols = [r[1] for r in cur.execute("PRAGMA table_info(discoveries)").fetchall()]
    except sqlite3.Error as exc:
        return {"present": True, "error": str(exc)}
    finally:
        conn.close()

    return {
        "present": True,
        "total_rows": total,
        "by_status": by_status,
        "vacuous_lean_rows": vacuous,
        "columns": cols,
    }


def audit_python_and_infra() -> dict[str, Any]:
    """Fast deterministic checks for security, packaging, CI, and code bugs."""
    issues: dict[str, list[str]] = {
        "ci_missing": [],
        "packaging_missing": [],
        "security_hotspots": [],
        "hardcoded_paths": [],
        "code_generator_vacuous": [],
        "schema_conflicts": [],
    }

    if not (ROOT / ".github" / "workflows").is_dir():
        issues["ci_missing"].append("No root .github/workflows/ directory")
    if not (ROOT / "pyproject.toml").is_file() and not (ROOT / "requirements.txt").is_file():
        issues["packaging_missing"].append("Neither pyproject.toml nor requirements.txt present")

    # Targeted checks on known critical files
    checks = [
        ("src/lean/code_generator.py", "candidate.c_eff = candidate.c_eff := by rfl", "code_generator_vacuous"),
        ("src/api/dashboard_api.py", 'allow_origins=["*"]', "security_hotspots"),
        ("dashboard/app.js", ".innerHTML =", "security_hotspots"),
        ("tools/gen_book.py", "os.system(", "security_hotspots"),
        ("live_vision_extractor.py", '"--api-key"', "security_hotspots"),
        ("scripts/init_db.py", "q_series_rep TEXT", "schema_conflicts"),
    ]
    for rel, needle, bucket in checks:
        p = ROOT / rel
        if p.is_file() and needle in p.read_text(encoding="utf-8", errors="replace"):
            issues[bucket].append(f"{rel}: contains `{needle}`")

    # Hardcoded user paths in tracked python scripts
    abs_re = re.compile(r'["\'](?:/home/|/Users/)[^"\']+["\']')
    for rel_dir in ["scripts", "src", "tools"]:
        base = ROOT / rel_dir
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            txt = p.read_text(encoding="utf-8", errors="replace")
            if abs_re.search(txt):
                issues["hardcoded_paths"].append(str(p.relative_to(ROOT)))
    for root_py in sorted(ROOT.glob("*.py")):
        if abs_re.search(root_py.read_text(encoding="utf-8", errors="replace")):
            issues["hardcoded_paths"].append(root_py.name)

    return issues


def audit_git_hygiene() -> dict[str, Any]:
    res = run_cmd(["git", "status", "--porcelain"])
    lines = res["tail"].splitlines() if res["exit_code"] == 0 else []
    # Full count via direct call for accuracy
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    dirty_lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    deleted_lake = sum(1 for ln in dirty_lines if ln.startswith(" D ") and ".lake/" in ln)

    ls_proc = subprocess.run(
        ["git", "ls-files"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = ls_proc.stdout.splitlines()
    tracked_verify = sum(1 for f in tracked if Path(f).name.startswith("verify_") and f.endswith(".lean"))
    tracked_build_aux = sum(
        1 for f in tracked if Path(f).suffix.lower() in {".aux", ".out", ".bbl", ".blg", ".olean", ".lock", ".trace"}
    )
    return {
        "dirty_file_count": len(dirty_lines),
        "deleted_tracked_lake_entries": deleted_lake,
        "tracked_total": len(tracked),
        "tracked_verify_lean": tracked_verify,
        "tracked_build_aux": tracked_build_aux,
        "sample_dirty": dirty_lines[:10],
    }


def run_cli_gates() -> dict[str, Any]:
    gates: dict[str, Any] = {}
    gates["mathesis_gate_self_test"] = run_cmd(
        ["python3", "tools/mathesis-gate/mathesis_gate.py", "--self-test"]
    )
    gates["mathesis_gate_strict"] = run_cmd(
        ["python3", "tools/mathesis-gate/mathesis_gate.py", ".", "--lean-src", "dualscale/lean", "--exclude", "archive", "--exclude", "verify_", "--skip-footprints"]
    )
    gates["mathesis_gate_root"] = run_cmd(
        ["python3", "tools/mathesis-gate/mathesis_gate.py", ".", "--exclude", "dualscale", "--exclude", "lean4", "--exclude", "lean_foundations", "--skip-footprints"]
    )
    gates["audit_lean_dualscale"] = run_cmd(
        ["python3", "dualscale/ci/audit_lean.py", "--root", "dualscale/lean/DualScale"]
    )
    gates["audit_citations_v3"] = run_cmd(
        ["python3", "dualscale/ci/audit_citations.py", "--paper-dir", "docs/v3_paper", "--bib", "dualscale/refs/bib/dualscale.bib"]
    )
    gates["validate_refs"] = run_cmd(["python3", "dualscale/ci/validate_refs.py"])
    gates["run_certificates"] = run_cmd(["python3", "dualscale/ci/run_certificates.py"])
    gates["verify_qseries"] = run_cmd(["python3", "dualscale/ci/verify_qseries.py"])
    gates["pytest_plain"] = run_cmd(
        ["pytest", "-q"], env={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    )
    gates["pytest_pythonpath"] = run_cmd(
        ["pytest", "-q"], env={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONPATH": "."}
    )
    return gates


def build_report() -> dict[str, Any]:
    lean = audit_lean_core()
    certs = audit_certificates()
    db = audit_database()
    py_infra = audit_python_and_infra()
    hygiene = audit_git_hygiene()
    gates = run_cli_gates()

    # Determine which tracks actually have work so the workflow can skip clean tracks (0 tokens)
    active_tracks = {
        "math_t2_and_t1": bool(
            lean["axiom_total"] > 0
            or lean["sorry_total"] > 0
            or lean["rfl_theorems"]
            or lean["suspicious_ceff_sign_files"]
            or certs["contradictions"]
            or certs["placeholders"]
            or db.get("vacuous_lean_rows", 0) > 0
        ),
        "code_and_security_t1": bool(
            py_infra["security_hotspots"]
            or py_infra["code_generator_vacuous"]
            or py_infra["schema_conflicts"]
            or not gates["pytest_plain"]["passed"]
        ),
        "hygiene_and_ci_t0": bool(
            py_infra["ci_missing"]
            or py_infra["packaging_missing"]
            or py_infra["hardcoded_paths"]
            or hygiene["tracked_verify_lean"] > 0
            or hygiene["deleted_tracked_lake_entries"] > 0
        ),
    }

    return {
        "root": str(ROOT),
        "active_tracks": active_tracks,
        "lean_core": lean,
        "certificates": certs,
        "database": db,
        "python_and_infra": py_infra,
        "git_hygiene": hygiene,
        "cli_gates": {k: {"passed": v["passed"], "exit_code": v["exit_code"]} for k, v in gates.items()},
        "failed_gate_tails": {k: v["tail"] for k, v in gates.items() if not v["passed"]},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Zero-token preflight audit for SocrateAI-Scientific-RajMathRecovery.")
    ap.add_argument("--json", action="store_true", help="Emit full compact JSON payload.")
    ap.add_argument("--summary", action="store_true", help="Emit human-readable summary.")
    args = ap.parse_args()

    report = build_report()
    if args.json or not args.summary:
        print(json.dumps(report, indent=2))
    else:
        print("=== PREFLIGHT SUMMARY (0 LLM TOKENS) ===")
        print(f"Active tracks: {report['active_tracks']}")
        lc = report["lean_core"]
        print(
            f"Lean core: {lc['core_file_count']} files | axioms={lc['axiom_total']} | "
            f"sorry={lc['sorry_total']} | rfl={len(lc['rfl_theorems'])} | "
            f"gated={lc['gated_module_count']} | verify_*={lc['verify_temp_files']['total']}"
        )
        print(f"Cert contradictions: {report['certificates']['contradictions']}")
        print(f"DB vacuous rows: {report['database'].get('vacuous_lean_rows')}/{report['database'].get('total_rows')}")
        print(f"CLI gates: { {k: v['passed'] for k, v in report['cli_gates'].items()} }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
RAMA Real-Time Execution Monitor & Observatory
==============================================
Provides real-time terminal monitoring, throughput tracking, ETA calculation,
and live synchronization with the Web Dashboard for RAMA discovery pipelines.

Usage:
  python3 tools/monitor_rama.py              # Single snapshot summary
  python3 tools/monitor_rama.py --watch      # Real-time live updating terminal UI
  python3 tools/monitor_rama.py --log <file> # Monitor specific log file
  python3 tools/monitor_rama.py --sync-web   # Start live web dashboard sync loop
"""

import os
import sys
import time
import re
import json
import argparse
import fractions
from typing import Dict, Any, List, Optional
from collections import deque

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.persistence.database import NamagiriDB

SUB_TRANS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP_TRANS = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")

def to_subscript(num: int) -> str:
    return str(num).translate(SUB_TRANS)

def to_superscript(num: int) -> str:
    return str(num).translate(SUP_TRANS)

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def format_vector_braket(exps: Dict[int, int], q_shift: int = 0, w_val: Optional[float] = None, c_val: Optional[float] = None) -> str:
    if not exps:
        return "|Ω_∅⟩"
    vector_terms = [f"r{to_subscript(d)}={r}" for d, r in sorted(exps.items())]
    inner_str = ", ".join(vector_terms)
    if w_val is None:
        w_val = 0.5 * sum(exps.values())
    if c_val is None:
        c_val = sum(r / d for d, r in exps.items())
    shift_str = f"q^({q_shift}/24) * " if q_shift != 0 else ""
    return f"{shift_str}|Ω_({inner_str})⟩ [Ŵ = {w_val:g}, Ĉ = {c_val:.4f}]"

def format_algebraic_projection(exps: Dict[int, int], q_shift: int = 0) -> str:
    if not exps:
        return "⟨τ|Ω_∅⟩ = 1"
    e0_num = q_shift if q_shift != 0 else sum(d * r for d, r in exps.items())
    frac_e0 = fractions.Fraction(e0_num, 24)
    if frac_e0 == 0:
        q_term = ""
    elif frac_e0.denominator == 1:
        q_term = f"q^{frac_e0.numerator} "
    else:
        q_term = f"q^({frac_e0.numerator}/{frac_e0.denominator}) "

    eta_terms = []
    for d, r in sorted(exps.items()):
        d_label = f"{d}τ" if d > 1 else "τ"
        if r == 1:
            eta_terms.append(f"η({d_label})")
        elif r == -1:
            eta_terms.append(f"η({d_label})⁻¹")
        else:
            eta_terms.append(f"η({d_label}){to_superscript(r)}")
    return f"⟨τ|Ω_r⟩ = {q_term}{' '.join(eta_terms)}".strip()

def clean_conjecture_string(conj_str: str) -> str:
    """Converts legacy dict conjectures into clean algebraic eta products."""
    if not conj_str:
        return "⟨τ|Ω_∅⟩ = 1"
    m_dict = re.search(r'\{([^}]+)\}', conj_str)
    if not m_dict:
        return conj_str
    
    exps = {}
    for pair in m_dict.group(1).split(','):
        if ':' in pair:
            parts = pair.split(':')
            try:
                exps[int(parts[0].strip())] = int(parts[1].strip())
            except Exception:
                pass
    if not exps:
        return conj_str
    
    m_shift = re.search(r'q\^\(([^)]+)\)', conj_str)
    q_shift = 0
    if m_shift:
        try:
            val = m_shift.group(1).strip()
            if '/' in val:
                num, den = val.split('/')
                q_shift = int(num) * (24 // int(den))
            else:
                q_shift = int(val) * 24
        except Exception:
            pass
    return format_algebraic_projection(exps, q_shift)


class RAMAProgressMonitor:
    def __init__(self, log_path: Optional[str] = None, refresh_rate: float = 1.0):
        self.refresh_rate = refresh_rate
        self.log_path = log_path or self._detect_log_file()
        self.db = NamagiriDB()
        self.history_window = deque(maxlen=30)
        self.start_timestamp = None
        self.last_parsed_pos = 0

    def _detect_log_file(self) -> str:
        candidates = ["nightly_run_full.log", "pipeline_full_notebooks.log", "rama_experiment.log"]
        for c in candidates:
            if os.path.exists(c) and os.path.getsize(c) > 0:
                return c
        return "nightly_run_full.log"

    def parse_state(self) -> Dict[str, Any]:
        """Parse log file and SQLite database to construct unified live execution state."""
        log_data = {
            "total_target": 730,
            "current_index": 0,
            "current_image": "N/A",
            "current_gen": 0,
            "max_gen": 15,
            "current_best_energy": 0.0,
            "current_diversity": 0,
            "verified_in_log": 0,
            "failed_in_log": 0,
            "recent_discoveries": [],
            "recent_generations": [],
            "is_active": False,
            "last_log_line": "",
            "log_size_kb": 0.0,
            "elapsed_sec": 0.0
        }

        # Check file size & activity
        if os.path.exists(self.log_path):
            stat = os.stat(self.log_path)
            log_data["log_size_kb"] = stat.st_size / 1024.0
            log_data["is_active"] = (time.time() - stat.st_mtime) < 30.0

            re_page = re.compile(r"--- Processing Page (\d+)/(\d+): (.*) ---")
            re_gen = re.compile(r"\[GeneticRAMA\] Gen (\d+)/(\d+) \| Best E: ([\d\.]+) \| Diversity: (\d+)/\d+")
            re_leap = re.compile(r"-> Evolutionary Leap: (.*)")
            re_energy = re.compile(r"-> Global Best Energy: ([\d\.]+) \(Fit Error: ([\d\.]+)\)")
            re_success = re.compile(r"\[SUCCESS\] Lean 4 verification passed")
            re_provenance = re.compile(r"Theorem stored with Provenance ID: (.*)")

            # Read log
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                if lines:
                    log_data["last_log_line"] = lines[-1].strip()
                    
                cur_img = None
                cur_leap = None
                cur_energy = None
                cur_fit = None
                cur_prov = None

                for line in lines:
                    m_p = re_page.search(line)
                    if m_p:
                        log_data["current_index"] = int(m_p.group(1))
                        log_data["total_target"] = int(m_p.group(2))
                        log_data["current_image"] = m_p.group(3).strip()
                        cur_img = m_p.group(3).strip()
                        continue

                    m_g = re_gen.search(line)
                    if m_g:
                        log_data["current_gen"] = int(m_g.group(1))
                        log_data["max_gen"] = int(m_g.group(2))
                        log_data["current_best_energy"] = float(m_g.group(3))
                        log_data["current_diversity"] = int(m_g.group(4))
                        continue

                    m_l = re_leap.search(line)
                    if m_l:
                        cur_leap = m_l.group(1).strip()
                        continue

                    m_e = re_energy.search(line)
                    if m_e:
                        cur_energy = m_e.group(1).strip()
                        cur_fit = m_e.group(2).strip()
                        continue

                    if re_success.search(line):
                        log_data["verified_in_log"] += 1
                        continue

                    m_pr = re_provenance.search(line)
                    if m_pr:
                        cur_prov = m_pr.group(1).strip()
                        if cur_img:
                            log_data["recent_discoveries"].append({
                                "image": cur_img,
                                "conjecture": clean_conjecture_string(cur_leap or "q-series"),
                                "energy": cur_energy or "0.0",
                                "fit_error": cur_fit or "0.0",
                                "provenance": cur_prov
                            })

        # Database statistics
        db_stats = self.db.get_stats()
        
        # Merge unified metrics
        return {
            "log": log_data,
            "db": db_stats,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def render_cli(self, state: Dict[str, Any]):
        """Render live ASCII/ANSI monitoring dashboard with pure algebraic Dirac notation."""
        clear_screen()
        log = state["log"]
        db = state["db"]
        
        total_target = max(1, log["total_target"])
        curr_idx = log["current_index"]
        progress_pct = (curr_idx / total_target) * 100.0 if curr_idx > 0 else 0.0

        bar_width = 36
        filled_len = int(bar_width * progress_pct // 100)
        bar = "█" * filled_len + "░" * (bar_width - filled_len)

        status_badge = "\033[92m● ACTIVE RUNNING\033[0m" if log["is_active"] else "\033[94m● IDLE / COMPLETED\033[0m"

        print("┌────────────────────────────────────────────────────────────────────────────┐")
        print("│  \033[1;36mRAMA NEURO-SYMBOLIC OBSERVATORY\033[0m — Live Operator Telemetry                 │")
        print("│  " + f"Status: {status_badge}  |  Refreshed: {state['timestamp']}".ljust(82) + "│")
        print("├────────────────────────────────────────────────────────────────────────────┤")
        print(f"│  \033[1mCorpus Progress\033[0m: [{bar}] \033[1;33m{progress_pct:5.1f}%\033[0m ({curr_idx}/{total_target})".ljust(84) + "│")
        print(f"│  Target Manuscript: \033[36m{log['current_image']}\033[0m".ljust(84) + "│")
        
        # Genetic progress
        gen_curr = log["current_gen"]
        gen_max = log["max_gen"]
        gen_bar_len = int(20 * gen_curr // max(1, gen_max))
        gen_bar = "▓" * gen_bar_len + "░" * (20 - gen_bar_len)
        print(f"│  Genetic Evolution: [{gen_bar}] Gen {gen_curr}/{gen_max} (Best E: {log['current_best_energy']:.4f})".ljust(84) + "│")
        print("├────────────────────────────────────────────────────────────────────────────┤")
        print("│  \033[1mDATABASE & PROVENANCE TELEMETRY\033[0m                                           │")
        print(f"│  Total Registered Inventions  : \033[1;37m{db['total']:,}\033[0m".ljust(84) + "│")
        print(f"│  ✅ Zero-Axiom Lean 4 Verified: \033[1;32m{db['verified']:,}\033[0m ({(db['verified']/max(1,db['total'])*100):.1f}%)".ljust(84) + "│")
        print(f"│  ❌ Verification Rejections   : \033[1;31m{db['failed']:,}\033[0m".ljust(84) + "│")
        print(f"│  Log File: \033[35m{self.log_path}\033[0m ({log['log_size_kb']:.1f} KB)".ljust(84) + "│")
        print("├────────────────────────────────────────────────────────────────────────────┤")
        print("│  \033[1mRECENT DISCOVERIES (VECTOR BRA-KET ALGEBRA)\033[0m                               │")
        
        recent = log["recent_discoveries"][-4:] if log["recent_discoveries"] else []
        if recent:
            for item in recent:
                conj_disp = (item["conjecture"][:48] + "...") if len(item["conjecture"]) > 48 else item["conjecture"]
                print(f"│  📄 \033[36m{item['image']}\033[0m → \033[32m{conj_disp}\033[0m".ljust(84) + "│")
                print(f"│     └─ E: \033[33m{item['energy']}\033[0m | ID: \033[90m{item['provenance']}\033[0m".ljust(84) + "│")
        else:
            print("│  No recent discoveries in current log window.                              │")
            
        print("├────────────────────────────────────────────────────────────────────────────┤")
        print(f"│  Last Log: \033[90m{(log['last_log_line'][:62] + '...') if len(log['last_log_line']) > 62 else log['last_log_line']}\033[0m".ljust(84) + "│")
        print("└────────────────────────────────────────────────────────────────────────────┘")
        print("  [Ctrl+C to exit monitor]  •  Web Dashboard: http://localhost:8081")

    def sync_web_json(self, state: Dict[str, Any]):
        """Export live state into dashboard_data.json with pure Dirac vector representation."""
        try:
            verified_rows = self.db.get_discoveries(status="VERIFIED", limit=30)
            failed_rows = self.db.get_discoveries(status="FAILED", limit=10)
            
            verified_theorems = []
            for r in verified_rows:
                w_val = r.get("w_eigenvalue", 0.0)
                c_val = r.get("c_eigenvalue", 0.0)
                is_bps = bool(r.get("is_bps_protected", 0))
                q_shift = r.get("q_shift", 0) or 0

                # Parse exponents
                d_exps = {}
                if r.get("eta_exponents"):
                    try:
                        exps = json.loads(r["eta_exponents"])
                        d_exps = {int(k): int(v) for k, v in exps.items()}
                        w_val = 0.5 * sum(d_exps.values())
                        c_val = sum(v / d for d, v in d_exps.items())
                    except Exception:
                        d_exps = {}

                braket = format_vector_braket(d_exps, q_shift, w_val, c_val)
                proj = format_algebraic_projection(d_exps, q_shift)
                sym_class = "Classe I (BPS)" if is_bps or abs(w_val - 0.5) < 1e-5 else ("Classe II (Invariant)" if abs(w_val) < 1e-5 else "Classe III (SUSY Breaking)")

                verified_theorems.append({
                    "image": os.path.basename(r.get("image_path", "unknown")),
                    "conjecture": proj,
                    "shadow": r.get("shadow", ""),
                    "domain": r.get("domain", "String Theory (K3)"),
                    "energy": str(round(r.get("rama_energy", 0.0), 4)),
                    "scores": f"C: {r.get('rama_C', 0.0):.2f}, I: {r.get('rama_I', 0.0):.4f}",
                    "braket": braket,
                    "projection": proj,
                    "symmetry_class": sym_class,
                    "w_eigenvalue": w_val,
                    "c_eigenvalue": c_val,
                    "is_bps": is_bps,
                    "status": "VERIFIED_ZERO_AXIOM"
                })

            data = {
                "stats": {
                    "total": state["db"]["total"],
                    "verified": state["db"]["verified"],
                    "failed": state["db"]["failed"],
                    "in_progress": state["db"]["unresolved"]
                },
                "verified_theorems": verified_theorems,
                "failed_images": [{"image": os.path.basename(r.get("image_path", "unknown")), "error_msg": r.get("lean_error", "Failed")} for r in failed_rows]
            }
            with open("dashboard_data.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def run_watch_loop(self):
        """Continuously loop and render live execution telemetry."""
        try:
            while True:
                state = self.parse_state()
                self.render_cli(state)
                self.sync_web_json(state)
                time.sleep(self.refresh_rate)
        except KeyboardInterrupt:
            print("\n👋 Exiting RAMA Monitor.")

def main():
    parser = argparse.ArgumentParser(description="RAMA Execution Monitor & Telemetry")
    parser.add_argument("--watch", "-w", action="store_true", help="Run interactive live watching loop")
    parser.add_argument("--log", "-l", type=str, default=None, help="Path to specific log file")
    parser.add_argument("--interval", "-i", type=float, default=1.5, help="Refresh interval in seconds")
    parser.add_argument("--sync-web", action="store_true", help="Sync dashboard_data.json and exit")
    args = parser.parse_args()

    monitor = RAMAProgressMonitor(log_path=args.log, refresh_rate=args.interval)

    if args.watch:
        monitor.run_watch_loop()
    else:
        state = monitor.parse_state()
        monitor.render_cli(state)
        monitor.sync_web_json(state)

if __name__ == "__main__":
    main()

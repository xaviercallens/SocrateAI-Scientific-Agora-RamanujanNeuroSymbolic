"""
Project NAMAGIRI — Full RAMA Experimentation Runner (HoloAlg Formalism)
========================================================================
Conducts end-to-end scientific experimentation:
1. Multi-epoch HoloAlg State Discovery across parameter space
2. Manuscript batch processing (8 prime pages) with Lean 4 verification
3. BPS-protection & unitarity spectrum analysis
4. Category Theory mapping (N -> G -> F) & 3-Act Theorem generation
5. Comprehensive certificate output
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.physics.holoalg import (
    RamanujanState,
    SupersymmetryOperator,
    CentralChargeOperator,
    GroundEnergyOperator,
    ModularInversionOperator,
    HoloAlgMasterEngine
)
from src.persistence.database import NamagiriDB
from autonomous_discovery_engine import AutonomousDiscoveryEngine
from scripts.rama_engine import generate_mock_candidate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_full_experiment(num_discovery_samples: int = 300, run_manuscript_batch: bool = True) -> Dict[str, Any]:
    print("=" * 80)
    print(" 🚀 INITIATING FULL RAMA SCIENTIFIC EXPERIMENTATION")
    print(" Framework: HoloAlg Operator Formalism & Category Theory")
    print("=" * 80)
    
    start_total_time = time.time()
    db = NamagiriDB()
    master_engine = HoloAlgMasterEngine(kappa=1.0, n_level=1.0)
    w_op = SupersymmetryOperator()
    c_op = CentralChargeOperator()
    e0_op = GroundEnergyOperator()
    
    # -------------------------------------------------------------
    # STAGE 1: Heuristic Operator Space Exploration (Discovery)
    # -------------------------------------------------------------
    print(f"\n[STAGE 1] Exploring Hilbert Space H_modular ({num_discovery_samples} samples)...")
    t0_disc = time.time()
    candidates = [generate_mock_candidate() for _ in range(num_discovery_samples)]
    candidates.sort(key=lambda x: x.energy)
    
    bps_count = 0
    unitary_count = 0
    
    for c in candidates:
        st = RamanujanState(c.exponents, c.q_shift_24)
        is_bps = w_op.is_bps_protected(st)
        is_unit = c_op.is_unitary(st)
        if is_bps:
            bps_count += 1
        if is_unit:
            unitary_count += 1
            
    top_states = candidates[:10]
    top_analyses = []
    for i, c in enumerate(top_states, 1):
        analysis = master_engine.analyze_state(c.exponents, c.q_shift_24, f"RAMA-EXP-S1-{i:02d}")
        top_analyses.append({
            "rank": i,
            "braket": analysis["braket"],
            "energy": round(c.energy, 4),
            "w_eigenvalue": round(analysis["operators"]["W_eigenvalue"], 4),
            "c_eigenvalue": round(analysis["operators"]["C_eigenvalue"], 4),
            "is_bps": analysis["operators"]["is_bps_protected"],
            "s_bps": round(analysis["category_G"].bps_entropy, 4),
            "enstrophy_bound": round(analysis["category_F"].enstrophy_bound, 4)
        })
        
        # Persist top discoveries
        db.insert_discovery({
            "image_path": f"synthetic://rama-exp-s1-{i}",
            "notebook": "RAMA-HoloAlg-Exp",
            "chapter": "TopologicalVacua",
            "page": i,
            "archetype": "Topological Vacuum State (HoloAlg)",
            "conjecture": analysis["partition_function"],
            "eta_exponents": json.dumps(c.exponents),
            "q_shift": c.q_shift_24,
            "rama_energy": c.energy,
            "rama_C": c.complexity,
            "rama_I": c.inconsistency,
            "rama_D": c.distance_to_anchor,
            "shadow": "\\eta(q)^3 (Weight 3/2 Mock Modular Shadow)",
            "domain": "String Theory (K3) / Holographic Fluid Boundary",
            "lean_code": "",
            "lean_status": "OPEN",
            "physics_mapping": f"S_BPS = {analysis['category_G'].bps_entropy:.4f}, Enstrophy_bound = {analysis['category_F'].enstrophy_bound:.4f}",
            "braket_notation": analysis["braket"],
            "w_eigenvalue": analysis["operators"]["W_eigenvalue"],
            "c_eigenvalue": analysis["operators"]["C_eigenvalue"],
            "is_bps_protected": analysis["operators"]["is_bps_protected"],
            "demonstration_3act": analysis["demonstration"]
        })
        
    t_elapsed_disc = time.time() - t0_disc
    print(f"  -> Discovered {num_discovery_samples} states in {t_elapsed_disc:.2f}s")
    print(f"  -> BPS-Protected States (Ŵ = 1/2): {bps_count}/{num_discovery_samples} ({bps_count/num_discovery_samples*100:.1f}%)")
    print(f"  -> Unitary States (Ĉ > 0): {unitary_count}/{num_discovery_samples} ({unitary_count/num_discovery_samples*100:.1f}%)")
    
    # -------------------------------------------------------------
    # STAGE 2: Manuscript Batch Execution with Lean 4 Verification
    # -------------------------------------------------------------
    manuscript_results = []
    if run_manuscript_batch:
        print("\n[STAGE 2] Autonomous Manuscript Pipeline & Lean 4 Formalization...")
        auto_engine = AutonomousDiscoveryEngine()
        
        from live_vision_extractor import discover_notebook_images
        discovered_imgs = [str(p) for p in discover_notebook_images()]
        batch_pages = discovered_imgs[:8] if len(discovered_imgs) >= 8 else discovered_imgs
        
        for idx, page in enumerate(batch_pages, 1):
            t_page = time.time()
            try:
                retrieval = auto_engine.step_1_retrieval(page)
                intuition = auto_engine.step_2_antigravity_intuition(retrieval, pop_size=25, max_generations=6)
                bridge = auto_engine.step_3_deep_think_bridge(intuition, retrieval)
                
                disc_id = f"holoalg_exp_p{idx:02d}"
                lean_res = auto_engine.step_4_lean4_auto_formalization(disc_id, intuition, bridge)
                physics_map = auto_engine.step_5_physical_mapping(intuition, bridge)
                
                state = intuition.get("state")
                holo_res = master_engine.analyze_state(state.exponents if state else {}, state.q_shift_24 if state else 0, disc_id) if state else None
                
                is_verified = (lean_res.get("status") == "VERIFIED")
                dt = time.time() - t_page
                
                rec_id = db.insert_discovery({
                    "id": disc_id,
                    "image_path": page,
                    "notebook": "LostNotebook-Letters",
                    "chapter": "MockTheta",
                    "page": idx,
                    "archetype": retrieval.get("archetype_hint", ""),
                    "conjecture": intuition.get("conjecture", ""),
                    "eta_exponents": json.dumps(state.exponents) if state else "{}",
                    "q_shift": state.q_shift_24 if state else 0,
                    "rama_energy": intuition.get("energy", 0.0),
                    "rama_C": intuition.get("metrics", {}).get("c", 0.0),
                    "rama_I": intuition.get("metrics", {}).get("i", 0.0),
                    "rama_D": intuition.get("metrics", {}).get("d", 0.0),
                    "shadow": bridge.get("shadow", ""),
                    "domain": bridge.get("domain_target", ""),
                    "lean_code": lean_res.get("lean_code", ""),
                    "lean_status": lean_res.get("status", "UNRESOLVED"),
                    "lean_error": lean_res.get("error", ""),
                    "physics_mapping": physics_map,
                    "braket_notation": holo_res["braket"] if holo_res else "",
                    "w_eigenvalue": holo_res["operators"]["W_eigenvalue"] if holo_res else 0.0,
                    "c_eigenvalue": holo_res["operators"]["C_eigenvalue"] if holo_res else 0.0,
                    "is_bps_protected": holo_res["operators"]["is_bps_protected"] if holo_res else False,
                    "demonstration_3act": holo_res["demonstration"] if holo_res else ""
                })
                
                manuscript_results.append({
                    "page_index": idx,
                    "filename": os.path.basename(page),
                    "db_id": rec_id,
                    "braket": holo_res["braket"] if holo_res else "None",
                    "is_bps": holo_res["operators"]["is_bps_protected"] if holo_res else False,
                    "lean_status": lean_res.get("status"),
                    "solve_time_sec": round(dt, 2)
                })
                print(f"  [{idx}/{len(batch_pages)}] {os.path.basename(page)}: {holo_res['braket'] if holo_res else 'N/A'} -> {lean_res.get('status')} ({dt:.2f}s)")
            except Exception as e:
                print(f"  [{idx}/{len(batch_pages)}] ❌ Error on {page}: {e}")
                manuscript_results.append({
                    "page_index": idx,
                    "filename": os.path.basename(page),
                    "error": str(e),
                    "solve_time_sec": round(time.time() - t_page, 2)
                })

    # -------------------------------------------------------------
    # STAGE 3: Final Aggregate Report & Certificate Compilation
    # -------------------------------------------------------------
    total_time = time.time() - start_total_time
    stats = db.get_stats()
    
    first_state_exp = top_states[0].exponents if top_states else {}
    first_state_q = top_states[0].q_shift_24 if top_states else 0
    
    report = {
        "title": "Full RAMA HoloAlg Experimentation Report",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_runtime_sec": round(total_time, 2),
        "stage1_discovery": {
            "samples": num_discovery_samples,
            "bps_count": bps_count,
            "bps_rate_percent": round(bps_count / num_discovery_samples * 100, 2),
            "unitary_count": unitary_count,
            "unitary_rate_percent": round(unitary_count / num_discovery_samples * 100, 2),
            "top_discoveries": top_analyses
        },
        "stage2_manuscript_batch": {
            "total_pages": len(manuscript_results),
            "verified_pages": sum(1 for r in manuscript_results if r.get("lean_status") == "VERIFIED"),
            "pages": manuscript_results
        },
        "database_stats": stats,
        "sample_3act_demonstration": master_engine.analyze_state(first_state_exp, first_state_q, "RAMA-DEMO-SAMPLE")["demonstration"]
    }
    
    out_cert_path = "dualscale/certificates/full_rama_experiment_report.json"
    os.makedirs(os.path.dirname(out_cert_path), exist_ok=True)
    with open(out_cert_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print("\n" + "=" * 80)
    print(" 🏁 FULL RAMA EXPERIMENTATION COMPLETE")
    print(f" Total Runtime        : {total_time:.2f}s ({total_time/60:.2f} min)")
    print(f" Database Total State : {stats['total']} discoveries ({stats['verified']} Lean verified)")
    print(f" Certificate Saved    : {out_cert_path}")
    print("=" * 80)
    
    return report


if __name__ == "__main__":
    run_full_experiment(num_discovery_samples=300, run_manuscript_batch=True)

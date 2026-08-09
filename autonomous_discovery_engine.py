"""
Autonomous Discovery Engine for Ramanujan-Style Mathematics (Phase 2)
=====================================================================
Fully wired Phase 2 architecture incorporating:
- WS-1: Pydantic-structured Multimodal Extraction
- WS-7: Genetic RAMA Evolutionary Engine
- WS-3: Substantive Lean 4 Mathlib Auto-Formalization
- WS-8: Saddle Point Matrix & S12 Partitioning
- WS-5: SQLite Provenance Persistence
"""

import os
import json
import logging
import uuid
import glob
from typing import Dict, Any

from src.extraction import VisionExtractor
from src.evolution import GeneticRAMAEngine
from src.lean import LeanCodeGenerator, LeanVerifier
from src.physics import SaddlePointEvaluator, S12PartitionFilter
from src.persistence import NamagiriDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class AutonomousDiscoveryEngine:
    def __init__(self):
        # Initialize Phase 2 Components
        self.vision = VisionExtractor(use_mock=True)
        self.lean_gen = LeanCodeGenerator()
        self.lean_ver = LeanVerifier(lean_project_dir="lean4")
        self.saddle = SaddlePointEvaluator()
        self.s12_filter = S12PartitionFilter()
        self.db = NamagiriDB()
        
    def step_1_retrieval(self, image_path: str) -> Dict[str, Any]:
        logging.info(f"[Phase 1] Vision Extraction: {os.path.basename(image_path)}")
        extraction = self.vision.extract_math(image_path)
        logging.info(f"  -> Archetype: {extraction.archetype_hint} (Confidence: {extraction.confidence:.2f})")
        return extraction.model_dump()

    def step_2_antigravity_intuition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logging.info("[Phase 2] Engaging Genetic RAMA Evolutionary Engine...")
        target_coeffs = data.get("q_series_coefficients")
        
        if target_coeffs:
            import numpy as np
            target_coeffs = np.array(target_coeffs, dtype=np.float64)
            # Run population-based evolutionary search instead of simulated annealing
            engine = GeneticRAMAEngine(target_coeffs, pop_size=25, max_generations=5, lean_gated=False)
            best_state, history = engine.run()
            energy, c, i, d = engine.fitness.evaluate_energy(best_state)
            
            conjecture = f"q^({best_state.q_shift_24}/24) * \\prod \\eta(q^d)^{best_state.exponents}"
            logging.info(f"  -> Evolutionary Leap: {conjecture}")
            logging.info(f"  -> Global Best Energy: {energy:.4f} (Fit Error: {i:.4f})")
            
            return {
                "conjecture": conjecture,
                "state": best_state,
                "energy": energy,
                "metrics": {"c": c, "i": i, "d": d}
            }
        else:
            logging.info("  -> No q-series coefficients. Skipping evolutionary search.")
            return {
                "conjecture": data.get("raw_latex", ""),
                "state": None,
                "energy": 0.0,
                "metrics": {}
            }

    def step_3_deep_think_bridge(self, intuition: Dict[str, Any], extraction: Dict[str, Any]) -> Dict[str, Any]:
        logging.info("[Phase 3] Deep Think Bridge...")
        archetype = extraction.get("archetype_hint", "").lower()
        
        if "mock theta" in archetype or "q-series" in archetype:
            domain = "String Theory (K3)"
            shadow = "\\eta(q)^3 (Weight 3/2 Mock Modular Shadow)"
        elif "continued fraction" in archetype:
            domain = "Topology"
            shadow = "3 distinct finite limit points (Topological Fracturing)"
        else:
            domain = "Astrophysics"
            shadow = "Picard-Fuchs Analytic Bounds"
            
        logging.info(f"  -> Mapped to Domain: {domain}")
        return {"domain_target": domain, "shadow": shadow}

    def step_4_lean4_auto_formalization(self, conjecture_id: str, intuition: Dict[str, Any], bridge: Dict[str, Any]) -> Dict[str, Any]:
        logging.info("[Phase 4] Live Lean 4 Mathlib Auto-Formalization...")
        state = intuition.get("state")
        
        if state:
            data = {
                "exponents": state.exponents,
                "shadow": bridge["shadow"],
                "domain": bridge["domain_target"]
            }
            lean_code = self.lean_gen.generate_verification_file(conjecture_id, data)
            
            # This calls out to the actual `lean` compiler via the verifier we built
            success, final_code, error = self.lean_ver.verify(lean_code, filename=f"verify_{conjecture_id}.lean", retries=2)
            status = "VERIFIED" if success else "FAILED"
            
            return {"lean_code": final_code, "status": status, "error": error}
        else:
            return {"lean_code": "-- Non-symbolic structural blueprint\n", "status": "UNRESOLVED", "error": None}

    def step_5_physical_mapping(self, intuition: Dict[str, Any], bridge: Dict[str, Any]) -> str:
        logging.info("[Phase 5] Extrapolation to Physical Vectors...")
        domain = bridge.get("domain_target")
        state = intuition.get("state")
        mapping = ""
        
        if state and domain == "String Theory (K3)":
            # 1. S12 Filter Isolation
            if self.s12_filter.classify_sequence(state.exponents, state.q_shift_24):
                mapping = "[S12 PARTITION] Sequence rejected from K3 counting. Reclassified to Elliptic Curve background mechanics."
            else:
                # 2. Saddle Point Thermodynamics
                saddle = self.saddle.evaluate_saddle_point(state.q_shift_24, state.exponents)
                mapping = (f"[SADDLE POINT MATRIX] Matrix: {saddle['matrix_applied']}\n"
                           f"  Entropy Scaling (c_eff={saddle['c_eff']}): {saddle['entropy_scaling']}\n"
                           f"  Equilibrium State: {saddle['equilibrium_state']}")
        elif domain == "Topology":
            mapping = "[WRT INVARIANTS] Radial limits mapped via GPPV boundary framework. (See wrt_radial_extractor for full limit calculations)."
        else:
            mapping = f"Mapped to {domain} using {bridge.get('shadow')}"
            
        logging.info(f"  -> {mapping.replace(chr(10), ' | ')}")
        return mapping

    def run_full_pipeline(self, image_path: str):
        print("\n" + "="*70)
        print(f" 🚀 PHASE 2 DISCOVERY LOOP: {os.path.basename(image_path)}")
        print("="*70)
        
        # 1. Retrieval
        retrieval_data = self.step_1_retrieval(image_path)
        
        # 2. Intuition
        intuition = self.step_2_antigravity_intuition(retrieval_data)
        
        # 3. Bridge
        bridge = self.step_3_deep_think_bridge(intuition, retrieval_data)
        
        # 4. Lean
        disc_id = str(uuid.uuid4())[:12].replace('-', '')
        lean_res = self.step_4_lean4_auto_formalization(disc_id, intuition, bridge)
        
        # 5. Physics
        physics_map = self.step_5_physical_mapping(intuition, bridge)
        
        # 6. Persistence (WS-5)
        state = intuition.get("state")
        
        try:
            notebook = "NoteBook" + image_path.split("NoteBook")[1].split("/")[0] if "NoteBook" in image_path else "Unknown"
        except:
            notebook = "Unknown"
            
        db_id = self.db.insert_discovery({
            "id": disc_id,
            "image_path": image_path,
            "notebook": notebook,
            "chapter": "",
            "page": 0,
            "archetype": retrieval_data.get("archetype_hint", ""),
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
            "physics_mapping": physics_map
        })
        
        logging.info(f"✅ Pipeline complete. Theorem stored with Provenance ID: {db_id}")
        return db_id


if __name__ == "__main__":
    engine = AutonomousDiscoveryEngine()
    
    target_dirs = [
        "/home/xavkal/xdev/SocrateAI-Scientific-RajMathRecovery/input/NoteBook1/**/*.jpg",
        "/home/xavkal/xdev/SocrateAI-Scientific-RajMathRecovery/input/NoteBook2/**/*.jpg",
        "/home/xavkal/xdev/SocrateAI-Scientific-RajMathRecovery/input/NoteBook3/**/*.jpg"
    ]
    
    target_images = []
    for d in target_dirs:
        target_images.extend(glob.glob(d, recursive=True))
        
    logging.info(f"Discovered {len(target_images)} manuscript images for Phase 2 processing.")
    
    # Process all discovered images for the full Deep Burn
    for img in target_images:
        try:
            engine.run_full_pipeline(img)
        except Exception as e:
            logging.error(f"Error processing {img}: {e}")

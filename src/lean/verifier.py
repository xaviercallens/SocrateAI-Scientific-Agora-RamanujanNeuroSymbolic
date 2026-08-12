"""
Project NAMAGIRI — Lean 4 Verifier (WS-3)
Wraps the Lean compiler. If verification fails, it reports failure honestly
without masking errors via sorry relaxation.
"""
import subprocess
import os
import logging
from typing import Tuple

class LeanVerifier:
    def __init__(self, lean_project_dir: str = "lean4"):
        self.lean_project_dir = os.path.abspath(lean_project_dir)
        
    def verify(self, lean_code: str, filename: str = "temp_verification.lean", retries: int = 1) -> Tuple[bool, str, str]:
        """
        Write code to a file and run 'lean' on it.
        Returns: (success_bool, lean_code, error_message)
        No sorry relaxation — failures are reported honestly.
        """
        # Place temporary verification files in DualScale/Discovery/ for fast Lake olean lookup
        discovery_dir = os.path.join(self.lean_project_dir, "DualScale", "Discovery")
        os.makedirs(discovery_dir, exist_ok=True)
        target_path = os.path.join(discovery_dir, filename)
        rel_path = os.path.relpath(target_path, self.lean_project_dir)
        
        for attempt in range(retries):
            with open(target_path, "w") as f:
                f.write(lean_code)
                
            try:
                # Run 'lake env lean' on relative path inside DualScale/Discovery
                result = subprocess.run(
                    ["lake", "env", "lean", rel_path],
                    cwd=self.lean_project_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    logging.info(f"  -> [SUCCESS] Lean 4 verification passed on attempt {attempt + 1}.")
                    return True, lean_code, ""
                else:
                    error_msg = result.stderr.strip()
                    logging.warning(f"  -> [FAILED] Lean 4 verification failed on attempt {attempt + 1}:\n{error_msg}")
                    return False, lean_code, error_msg
                    
            except subprocess.TimeoutExpired:
                logging.error(f"  -> [ERROR] Lean verification timed out on attempt {attempt + 1}.")
                return False, lean_code, "Verification timed out"
            except FileNotFoundError:
                logging.error("  -> [ERROR] 'lake' compiler not found in PATH.")
                return False, lean_code, "Compiler not found"
                
        return False, lean_code, "Failed after max retries."

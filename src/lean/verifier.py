"""
Project NAMAGIRI — Lean 4 Verifier (WS-3)
Wraps the Lean compiler. If verification fails, it reports failure honestly
without masking errors via sorry relaxation.
"""
import logging
import os
import subprocess
from typing import Tuple


class LeanVerifier:
    """Runs `lake env lean` on generated verification files."""

    def __init__(self, lean_project_dir: str = "dualscale/lean"):
        self.lean_project_dir = os.path.abspath(lean_project_dir)

    def verify(
        self,
        lean_code: str,
        filename: str = "temp_verification.lean",
        retries: int = 1,
        cleanup: bool = True,
    ) -> Tuple[bool, str, str]:
        """
        Write code to a file and run `lake env lean` on it.
        Returns: (success_bool, lean_code, error_message)
        No sorry relaxation — failures are reported honestly.
        """
        discovery_dir = os.path.join(self.lean_project_dir, "DualScale", "Discovery")
        os.makedirs(discovery_dir, exist_ok=True)
        safe_filename = os.path.basename(filename) or "temp_verification.lean"
        target_path = os.path.join(discovery_dir, safe_filename)
        rel_path = os.path.relpath(target_path, self.lean_project_dir)

        attempts = max(1, int(retries))
        last_error = ""

        try:
            for attempt in range(attempts):
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(lean_code)

                try:
                    result = subprocess.run(
                        ["lake", "env", "lean", rel_path],
                        cwd=self.lean_project_dir,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )

                    if result.returncode == 0:
                        logging.info(
                            "  -> [SUCCESS] Lean 4 verification passed on attempt %d.",
                            attempt + 1,
                        )
                        return True, lean_code, ""

                    combined = "\n".join(
                        part for part in (result.stdout.strip(), result.stderr.strip()) if part
                    ).strip()
                    last_error = combined or f"Lean exited with return code {result.returncode}"
                    logging.warning(
                        "  -> [FAILED] Lean 4 verification failed on attempt %d:\n%s",
                        attempt + 1,
                        last_error,
                    )
                except subprocess.TimeoutExpired:
                    last_error = "Verification timed out"
                    logging.error(
                        "  -> [ERROR] Lean verification timed out on attempt %d.",
                        attempt + 1,
                    )
                except FileNotFoundError:
                    logging.error("  -> [ERROR] 'lake' compiler not found in PATH.")
                    return False, lean_code, "Compiler not found"
        finally:
            if cleanup and os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except OSError as exc:
                    logging.debug("Could not remove temp Lean file %s: %s", target_path, exc)

        return False, lean_code, last_error or "Failed after max retries."

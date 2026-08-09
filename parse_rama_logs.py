import re
import os
from collections import defaultdict

LOG_FILE = "pipeline_full_notebooks.log"

def parse_logs(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    # Tracking dictionaries
    results = defaultdict(dict)
    current_image = None

    # Regex patterns
    re_image = re.compile(r"PROCESSING MANUSCRIPT IMAGE: (.*)")
    re_conjecture = re.compile(r"Proposed Leap \(Identity\): (.*)|Proposed Conjecture: (.*)")
    re_rama = re.compile(r"RAMA Filter \[E = ([\d\.]+)\]: (.*)")
    re_shadow = re.compile(r"Calculated Shadow / Completion: (.*)")
    re_success = re.compile(r"\[SUCCESS\] Lean 4 verification passed!")
    re_error = re.compile(r"\[ERROR\] (.*)")

    with open(file_path, "r") as f:
        for line in f:
            # 1. Identify the current image being processed
            img_match = re_image.search(line)
            if img_match:
                current_image = img_match.group(1).strip()
                results[current_image]['status'] = "PROCESSING"
                continue
            
            if not current_image:
                continue

            # 2. Extract the Conjecture
            conj_match = re_conjecture.search(line)
            if conj_match:
                results[current_image]['conjecture'] = conj_match.group(1) or conj_match.group(2)
            
            # 3. Extract RAMA Energy Scores
            rama_match = re_rama.search(line)
            if rama_match:
                results[current_image]['energy'] = rama_match.group(1).strip()
                results[current_image]['scores'] = rama_match.group(2).strip()

            # 4. Extract Calculated Shadow
            shadow_match = re_shadow.search(line)
            if shadow_match:
                results[current_image]['shadow'] = shadow_match.group(1).strip()

            # 5. Check for Lean 4 Success
            if re_success.search(line):
                results[current_image]['status'] = "VERIFIED_ZERO_AXIOM"
            
            # 6. Check for Errors (e.g. OCR failures or Lean compilation timeouts)
            err_match = re_error.search(line)
            if err_match:
                results[current_image]['status'] = "FAILED"
                results[current_image]['error_msg'] = err_match.group(1).strip()
            
            # Catch Python tracebacks for the missing .get() error
            if "AttributeError" in line and "object has no attribute 'get'" in line:
                results[current_image]['status'] = "FAILED"
                results[current_image]['error_msg'] = line.strip()


    # --- Generate Dashboard ---
    verified = {k: v for k, v in results.items() if v.get('status') == "VERIFIED_ZERO_AXIOM"}
    failed = {k: v for k, v in results.items() if v.get('status') == "FAILED"}
    in_progress = {k: v for k, v in results.items() if v.get('status') == "PROCESSING"}

    print("="*65)
    print(" 🚀 RAMA NEURO-SYMBOLIC PIPELINE DASHBOARD")
    print("="*65)
    print(f"Total Processed/Processing: {len(results)}")
    print(f"✅ ZERO-AXIOM VERIFIED : {len(verified)}")
    print(f"❌ FAILED / UNRESOLVED : {len(failed)}")
    print(f"⏳ IN PROGRESS        : {len(in_progress)}\n")

    print("--- 🏆 TOP 5 RECENT VERIFIED THEOREMS ---")
    for img, data in list(verified.items())[-5:]:
        print(f"📄 {img}")
        print(f"   ├─ Conjecture: {data.get('conjecture', 'N/A')}")
        print(f"   ├─ Shadow:     {data.get('shadow', 'N/A')}")
        print(f"   └─ RAMA Energy: {data.get('energy', 'N/A')} ({data.get('scores', '')})")

    print("\n--- ⚠️ UNRESOLVED STATES (NEEDS DEBUGGING) ---")
    print("="*65)
    
    # --- Generate JSON for Web Dashboard ---
    import json
    dashboard_data = {
        "stats": {
            "total": len(results),
            "verified": len(verified),
            "failed": len(failed),
            "in_progress": len(in_progress)
        },
        "verified_theorems": [{"image": k, **v} for k, v in list(verified.items())[-20:]], # Last 20
        "failed_images": [{"image": k, **v} for k, v in failed.items()]
    }
    with open("dashboard_data.json", "w") as f:
        json.dump(dashboard_data, f, indent=4)
    print("Saved dashboard data to dashboard_data.json.")

if __name__ == "__main__":
    parse_logs(LOG_FILE)

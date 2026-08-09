import argparse
import sys
import os
import glob
import re

def extract_bib_keys(bib_path):
    """Extracts citation keys from a .bib file."""
    keys = set()
    with open(bib_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Match @article{AJO2001, etc.
            match = re.match(r'@\w+\s*{\s*([^,]+),', line)
            if match:
                keys.add(match.group(1).strip())
    return keys

def extract_tex_citations(tex_path):
    """Extracts citation keys from a .tex file."""
    keys = set()
    with open(tex_path, 'r') as f:
        content = f.read()
        # Match \cite{key1,key2}
        citations = re.findall(r'\\cite{([^}]+)}', content)
        for citation in citations:
            # Handle multiple keys separated by comma
            for k in citation.split(','):
                keys.add(k.strip())
    return keys

def main():
    parser = argparse.ArgumentParser(description="Audit citations in LaTeX paper against bib file.")
    parser.add_argument("--paper-dir", required=True)
    parser.add_argument("--bib", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.bib):
        print(f"Error: Bib file {args.bib} not found.")
        sys.exit(1)

    bib_keys = extract_bib_keys(args.bib)
    print(f"Found {len(bib_keys)} entries in bibliography.")

    tex_files = glob.glob(os.path.join(args.paper_dir, "**", "*.tex"), recursive=True)
    if not tex_files:
        print(f"No .tex files found in {args.paper_dir}.")
        sys.exit(0)

    missing_citations = []
    used_keys = set()
    
    for tex_file in tex_files:
        print(f"Scanning {tex_file}...")
        tex_keys = extract_tex_citations(tex_file)
        
        for key in tex_keys:
            used_keys.add(key)
            if key not in bib_keys:
                missing_citations.append((tex_file, key))
                
    if missing_citations:
        print("\n=== RULE R4 VIOLATION: MISSING CITATIONS ===")
        for tex_file, key in missing_citations:
            print(f"File {tex_file} cites '{key}', which is missing from {args.bib}")
        sys.exit(1)
        
    unused_keys = bib_keys - used_keys
    if unused_keys:
        print(f"\nWARNING: Found {len(unused_keys)} unused bibliography entries in {args.bib}:")
        for key in sorted(unused_keys):
            print(f"  - {key}")
        
    print("\nRule R4 Verification Complete: All Tier-B claims have valid citations.")
    sys.exit(0)

if __name__ == "__main__":
    main()

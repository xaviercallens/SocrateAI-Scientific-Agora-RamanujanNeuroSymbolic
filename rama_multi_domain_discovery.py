#!/usr/bin/env python3
"""
RAMA Multi-Source & Multi-Domain Discovery CLI Engine
=====================================================
Executes RAMA heuristic discovery across 5 input sources and 10 physical domains.

Usage examples:
  python3 rama_multi_domain_discovery.py --oeis A000041
  python3 rama_multi_domain_discovery.py --oeis A000521
  python3 rama_multi_domain_discovery.py --latex "f(q) = 1 + q + 2q^2 + 3q^3 + 5q^4 + 7q^5"
  python3 rama_multi_domain_discovery.py --coeffs "1,1,-1,1,-2,2,-3,3,-4,5"
  python3 rama_multi_domain_discovery.py --arxiv "Mock theta function and black hole entropy"
  python3 rama_multi_domain_discovery.py --image data/manuscripts/page76.jpg
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from autonomous_discovery_engine import AutonomousDiscoveryEngine

def main():
    parser = argparse.ArgumentParser(description="RAMA Multi-Source & Multi-Domain Discovery Engine")
    parser.add_argument("--oeis", type=str, default=None, help="OEIS Sequence ID (e.g. A000041, A000521, A002107, A000594)")
    parser.add_argument("--latex", type=str, default=None, help="Raw LaTeX formula string")
    parser.add_argument("--coeffs", type=str, default=None, help="Comma-separated numerical coefficients (e.g. '1,1,2,3,5,7')")
    parser.add_argument("--arxiv", type=str, default=None, help="ArXiv manuscript text or abstract")
    parser.add_argument("--image", type=str, default=None, help="Path to manuscript image file")
    parser.add_argument("--pop-size", type=int, default=40, help="Genetic evolutionary population size")
    parser.add_argument("--generations", type=int, default=10, help="Evolutionary search generations")
    args = parser.parse_args()

    engine = AutonomousDiscoveryEngine(use_mock_vision=False)

    if args.oeis:
        print(f"🔬 Ingesting OEIS Sequence: {args.oeis}")
        engine.run_full_pipeline(args.oeis, source_type="oeis_id", pop_size=args.pop_size, max_generations=args.generations)
    elif args.latex:
        print(f"🔬 Ingesting LaTeX Formula: {args.latex}")
        engine.run_full_pipeline(args.latex, source_type="raw_latex", pop_size=args.pop_size, max_generations=args.generations)
    elif args.coeffs:
        print(f"🔬 Ingesting Coefficients Vector: {args.coeffs}")
        engine.run_full_pipeline(args.coeffs, source_type="coefficients_vector", pop_size=args.pop_size, max_generations=args.generations)
    elif args.arxiv:
        print(f"🔬 Ingesting ArXiv Text: {args.arxiv}")
        engine.run_full_pipeline(args.arxiv, source_type="arxiv_paper", pop_size=args.pop_size, max_generations=args.generations)
    elif args.image:
        print(f"🔬 Ingesting Manuscript Image: {args.image}")
        engine.run_full_pipeline(args.image, source_type="image_scan", pop_size=args.pop_size, max_generations=args.generations)
    else:
        # Run a multi-source demo across 3 distinct sources
        print("🚀 Executing RAMA Multi-Source & Multi-Domain Demonstration Run...\n")
        
        print("--- [Source 1/3: OEIS Partition Sequence A000041] ---")
        engine.run_full_pipeline("A000041", source_type="oeis_id", pop_size=30, max_generations=5)
        
        print("\n--- [Source 2/3: Mock Theta LaTeX Ingestion] ---")
        engine.run_full_pipeline("f(q) = 1 + q - q^2 + q^3 - 2q^4 + 2q^5 - 3q^6", source_type="raw_latex", pop_size=30, max_generations=5)
        
        print("\n--- [Source 3/3: ArXiv Fluid Hydrodynamics Paper] ---")
        engine.run_full_pipeline("Navier-Stokes enstrophy dissipation in 3D turbulent flows with mock modular shadows", source_type="arxiv_paper", pop_size=30, max_generations=5)

if __name__ == "__main__":
    main()

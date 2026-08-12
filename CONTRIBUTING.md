# Contributing to SocrateAI Ramanujan Neuro-Symbolic Discovery

Thank you for your interest in contributing to this research project!

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Run Lean checks: `cd dualscale/lean && lake build`
6. Submit a pull request

## Contributor License Agreement

**All contributors must agree to the [CLA](CLA.md).** Include the following
statement in your first pull request:

> I have read and agree to the Contributor License Agreement (CLA.md).

## Code Standards

- **Python:** PEP 8, type hints preferred, docstrings on all public functions
- **Lean 4:** Zero `sorry`, zero unauthorized `axiom`, `lake build` must pass
- **Papers:** All claims must be classified as Tier A (verified), B (computational), or C (conjectural)
- **Data:** All OEIS references must be verified against the live database

## What We Need Help With

- [ ] LMFDB cross-referencing for novel discoveries
- [ ] Extended coefficient computation (1000+ terms)
- [ ] Sage/Magma verification of modularity conditions
- [ ] Peer review of physical interpretation sections
- [ ] DNS simulation data for enstrophy bound testing

## License

Code contributions are licensed under MIT; research contributions under CC BY-SA 4.0.
See [LICENSE.md](LICENSE.md) for details.

"""
Unit tests for the hardened NAMAGIRI pipeline, API, persistence, and verification gates.
"""

import csv
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api import dashboard_api
from src.lean.code_generator import LeanCodeGenerator, _fmt_rat
from src.lean.verifier import LeanVerifier
from src.persistence.database import NamagiriDB


def _load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mathesis_gate = _load_module("mathesis_gate", "tools/mathesis-gate/mathesis_gate.py")
run_certificates = _load_module("run_certificates", "dualscale/ci/run_certificates.py")


class TestLeanCodeGenerator:
    def test_fmt_rat_exact(self):
        assert _fmt_rat(Fraction(1, 1)) == "(1 : ℚ)"
        assert _fmt_rat(Fraction(-2, 1)) == "(-2 : ℚ)"
        assert _fmt_rat(Fraction(-1, 24)) == "((-1 : ℚ) / 24)"
        assert _fmt_rat(Fraction(25, 72)) == "((25 : ℚ) / 72)"

    def test_tier_a_exact_rationals_and_no_vacuity(self):
        gen = LeanCodeGenerator()
        exponents = {1: -1}  # 1/eta(tau): c_eff = +1, weight = -1/2, P = -1/24, E0 = +1/24
        code = gen.generate_verification_file(
            "inv-eta-1",
            {
                "exponents": exponents,
                "q_shift": -1,
                "shadow": "eta(q)^3",
                "domain": "String Theory (K3)",
            },
        )

        assert "by rfl" not in code
        assert "native_decide" not in code
        assert ": True" not in code
        assert ": Prop := True" not in code
        assert "sorry" not in code
        assert "\naxiom " not in code

        assert "theorem verify_c_eff : candidate.c_eff = (1 : ℚ) := by" in code
        assert "theorem verify_weight : candidate.weight = ((-1 : ℚ) / 2) := by" in code
        assert "theorem verify_leading_power : candidate.leading_power = ((-1 : ℚ) / 24) := by" in code
        assert "theorem verify_ground_state_shift : candidate.ground_state_shift = ((1 : ℚ) / 24) := by" in code
        assert "norm_num" in code
        assert "-- q_shift_24 = -1" in code
        assert "Tier C" in code
        assert "Ono Thm 1.64" in code

    def test_multifactor_negative_c_eff(self):
        gen = LeanCodeGenerator()
        exponents = {3: 1, 8: 1, 9: -1}
        code = gen.generate_tier_a_eta_quotient_verification("nb1_ch1", exponents, 2)
        # c_eff = -(1/3 + 1/8 - 1/9) = -25/72
        assert "candidate.c_eff = ((-25 : ℚ) / 72)" in code
        assert "candidate.weight = ((1 : ℚ) / 2)" in code
        assert "candidate.leading_power = ((1 : ℚ) / 12)" in code
        assert "candidate.ground_state_shift = ((-1 : ℚ) / 12)" in code

    def test_empty_exponents_and_validation(self):
        gen = LeanCodeGenerator()
        code = gen.generate_tier_a_eta_quotient_verification("empty", {}, 0)
        assert "{ factors := [(1, 0)] }" in code
        assert "candidate.c_eff = (0 : ℚ)" in code

        with pytest.raises(ValueError):
            gen.generate_tier_a_eta_quotient_verification("bad_d0", {0: 1}, 0)
        with pytest.raises(ValueError):
            gen.generate_tier_a_eta_quotient_verification("bad_neg", {-2: 1}, 0)
        with pytest.raises(ValueError):
            gen.generate_tier_a_eta_quotient_verification("bad_bool", {True: 1}, 0)


class TestLeanVerifier:
    def test_retries_and_cleanup(self, tmp_path):
        ver = LeanVerifier(lean_project_dir=str(tmp_path))
        assert ver.lean_project_dir == str(tmp_path)
        assert LeanVerifier().lean_project_dir.endswith("dualscale/lean")

        fail_proc = subprocess.CompletedProcess(
            args=["lake"], returncode=1, stdout="stdout detail\n", stderr="stderr detail\n"
        )
        ok_proc = subprocess.CompletedProcess(
            args=["lake"], returncode=0, stdout="", stderr=""
        )

        with patch("src.lean.verifier.subprocess.run", side_effect=[fail_proc, ok_proc]) as mock_run:
            ok, _, err = ver.verify("-- lean", filename="probe.lean", retries=2, cleanup=True)
        assert ok is True
        assert err == ""
        assert mock_run.call_count == 2
        assert not (tmp_path / "DualScale" / "Discovery" / "probe.lean").exists()

        with patch("src.lean.verifier.subprocess.run", return_value=fail_proc):
            ok, _, err = ver.verify("-- lean", filename="probe_fail.lean", retries=2, cleanup=True)
        assert ok is False
        assert "stdout detail" in err and "stderr detail" in err
        assert not (tmp_path / "DualScale" / "Discovery" / "probe_fail.lean").exists()


class TestNamagiriDB:
    def test_id_preservation_canonical_dedup_and_export(self, tmp_path):
        db_file = tmp_path / "test.db"
        db = NamagiriDB(str(db_file))

        id1 = db.insert_discovery({
            "id": "custom_id_1",
            "image_path": "/manuscripts/nb1/p1.jpg",
            "eta_exponents": {2: 1, 1: -1},
            "q_shift": 3,
            "lean_code": (
                "import Mathlib.Data.Rat.Init\n"
                "import Mathlib.Tactic.NormNum\n"
                "theorem t1 : (1 : ℚ) = 1 := by norm_num\n"
            ),
            "lean_status": "VERIFIED",
            "domain": "String Theory (K3)",
            "conjecture": "c1",
        })
        assert id1 == "custom_id_1"

        # Different key order / string JSON should deduplicate to custom_id_1
        dup_id = db.insert_discovery({
            "id": "should_not_insert",
            "image_path": "/manuscripts/nb1/p2.jpg",
            "eta_exponents": json.dumps({"1": -1, "2": 1}),
            "q_shift": 3,
        })
        assert dup_id == "custom_id_1"

        id2 = db.insert_discovery({
            "id": "custom_id_2",
            "image_path": "/manuscripts/nb1/p3.jpg",
            "eta_exponents": {1: -2},
            "q_shift": 0,
            "lean_code": (
                "import Mathlib.Data.Rat.Init\n"
                "import Mathlib.Tactic.NormNum\n"
                "theorem t2 : (2 : ℚ) = 2 := by norm_num\n"
            ),
            "lean_status": "VERIFIED",
            "domain": "Topology",
            "conjecture": "c2",
        })
        assert id2 == "custom_id_2"

        out_lean = tmp_path / "combined.lean"
        exported_count = db.export_lean_library(str(out_lean))
        assert exported_count == 2
        exported = out_lean.read_text(encoding="utf-8")
        assert exported.count("import Mathlib.Data.Rat.Init") == 1
        assert exported.count("import Mathlib.Tactic.NormNum") == 1
        assert exported.index("import Mathlib.Tactic.NormNum") < exported.index("namespace Namagiri.Generated")

    def test_init_db_schema_parity(self, tmp_path):
        init_src = (ROOT / "scripts" / "init_db.py").read_text(encoding="utf-8")
        assert "q_series_rep" not in init_src

        init_db_mod = _load_module("init_db_script", "scripts/init_db.py")
        init_path = tmp_path / "via_script.db"
        ref_path = tmp_path / "via_class.db"

        init_db_mod.init_db(str(init_path))
        NamagiriDB(str(ref_path))

        with sqlite3.connect(init_path) as c1, sqlite3.connect(ref_path) as c2:
            cols1 = [(r[1], r[2]) for r in c1.execute("PRAGMA table_info(discoveries)").fetchall()]
            cols2 = [(r[1], r[2]) for r in c2.execute("PRAGMA table_info(discoveries)").fetchall()]
        assert cols1 == cols2
        assert ("eta_exponents", "TEXT") in cols1
        assert all(name != "q_series_rep" for name, _ in cols1)


class TestDashboardAPI:
    def test_endpoints_bounds_404_and_cors(self, tmp_path, monkeypatch):
        test_db = NamagiriDB(str(tmp_path / "api_test.db"))
        test_db.insert_discovery({
            "id": "api_rec_1",
            "image_path": "/tmp/page1.jpg",
            "eta_exponents": {1: -1},
            "q_shift": 0,
            "lean_status": "FAILED",
            "domain": "Topology",
        })
        monkeypatch.setattr(dashboard_api, "db", test_db)
        client = TestClient(dashboard_api.app)

        stats_res = client.get("/api/stats")
        assert stats_res.status_code == 200
        assert stats_res.json() == {"total": 1, "verified": 0, "failed": 1, "unresolved": 0}

        list_res = client.get("/api/discoveries?limit=10&offset=0")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1

        assert client.get("/api/discoveries?limit=201").status_code == 422
        assert client.get("/api/discoveries?limit=0").status_code == 422
        assert client.get("/api/discoveries?offset=-1").status_code == 422

        found_res = client.get("/api/discoveries/api_rec_1")
        assert found_res.status_code == 200
        assert found_res.json()["id"] == "api_rec_1"

        missing_res = client.get("/api/discoveries/nonexistent_id")
        assert missing_res.status_code == 404

        cors_ok = client.get("/api/stats", headers={"Origin": "http://localhost:8080"})
        assert cors_ok.headers.get("access-control-allow-origin") == "http://localhost:8080"
        assert cors_ok.headers.get("access-control-allow-credentials") is None

        cors_bad = client.get("/api/stats", headers={"Origin": "https://evil.example"})
        assert "access-control-allow-origin" not in cors_bad.headers

    def test_dashboard_app_js_no_innerhtml(self):
        app_js = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
        assert "innerHTML" not in app_js
        assert "document.createElement" in app_js
        assert "textContent" in app_js
        assert "replaceChildren" in app_js


class TestGatesAndCertificates:
    def test_mathesis_gate_self_test_and_rfl_probe(self, tmp_path):
        assert mathesis_gate.self_test() == []

        bad_file = tmp_path / "vacuous.lean"
        bad_file.write_text(
            "theorem verify_c_eff : candidate.c_eff = candidate.c_eff := by rfl\n",
            encoding="utf-8",
        )
        findings = mathesis_gate.check_vacuity([bad_file], tmp_path)
        assert len(findings) == 1
        assert "reflexive tautology" in findings[0]

        gen_file = tmp_path / "valid_gen.lean"
        gen_file.write_text(
            LeanCodeGenerator().generate_verification_file(
                "gate_ok", {"exponents": {1: -1}, "q_shift": 0}
            ),
            encoding="utf-8",
        )
        assert mathesis_gate.check_vacuity([gen_file], tmp_path) == []
        assert mathesis_gate.check_hygiene([gen_file], tmp_path, allow_sorry=False) == []

    def test_run_certificates_validation(self, tmp_path):
        cert_dir = tmp_path / "certs"
        spectral_dir = cert_dir / "spectral"
        spectral_dir.mkdir(parents=True)

        with (cert_dir / "ledger.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["prime", "k", "lambda_2", "bound", "status"])
            writer.writerow(["2", "3", "2.5", "2.8284", "PASS"])

        valid_cert = {
            "milestone": "M2",
            "target": "spectral/p2_alon_boppana",
            "verdict": "PASS",
            "timestamp": "2026-08-09T20:13:20+00:00",
            "git_commit": "abc1234",
            "details": {"prime": 2, "note": "LPS exact check"},
        }
        cert_file = spectral_dir / "p2_certificate.json"
        cert_file.write_text(json.dumps(valid_cert), encoding="utf-8")
        assert run_certificates.validate_certificates(cert_dir) == []

        # Placeholder with PASS must fail
        placeholder_cert = dict(valid_cert, details={"prime": 2, "note": "PLACEHOLDER stub"})
        cert_file.write_text(json.dumps(placeholder_cert), encoding="utf-8")
        errs = run_certificates.validate_certificates(cert_dir)
        assert any("PLACEHOLDER" in e for e in errs)

        # Contradiction with ledger.csv must fail
        contradiction_cert = dict(valid_cert, verdict="FAIL", details={"prime": 2, "note": "honest fail"})
        cert_file.write_text(json.dumps(contradiction_cert), encoding="utf-8")
        errs = run_certificates.validate_certificates(cert_dir)
        assert any("contradiction" in e for e in errs)

        # Missing required fields must fail
        cert_file.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
        errs = run_certificates.validate_certificates(cert_dir)
        assert any("missing or empty required field" in e for e in errs)

        # Repo's reconciled certificates should pass validation cleanly
        assert run_certificates.validate_certificates(ROOT / "dualscale" / "certificates") == []

    def test_mathesis_gate_single_file_invocation(self, tmp_path):
        gate_script = ROOT / "tools" / "mathesis-gate" / "mathesis_gate.py"

        bad_file = tmp_path / "single_bad.lean"
        bad_file.write_text(
            "theorem t_bad : candidate.c_eff = candidate.c_eff := by rfl\n",
            encoding="utf-8",
        )
        assert mathesis_gate.lean_files(bad_file, []) == [bad_file]
        bad_proc = subprocess.run(
            [sys.executable, str(gate_script), str(bad_file), "--skip-footprints"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert bad_proc.returncode == 1
        assert "1 Lean file(s) scanned" in bad_proc.stdout
        assert "reflexive tautology" in bad_proc.stdout

        ok_file = tmp_path / "single_ok.lean"
        ok_file.write_text(
            LeanCodeGenerator().generate_verification_file(
                "single_ok", {"exponents": {1: -1}, "q_shift": 0}
            ),
            encoding="utf-8",
        )
        ok_proc = subprocess.run(
            [sys.executable, str(gate_script), str(ok_file), "--skip-footprints"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert ok_proc.returncode == 0
        assert "1 Lean file(s) scanned" in ok_proc.stdout
        assert "ALL CHECKS PASS" in ok_proc.stdout

    def test_run_certificates_hardened_guards(self, tmp_path):
        cert_dir = tmp_path / "certs"
        moduli_dir = cert_dir / "moduli_map"
        moduli_dir.mkdir(parents=True)

        def write_s12_ledger(status: str, classification: str):
            with (cert_dir / "s12_ledger.csv").open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Sequence", "J_Invariant", "Classification", "Rule_R5_Status"])
                writer.writerow(["S_12", "N/A_MOCK_PROXY_QUARANTINED", classification, status])

        write_s12_ledger("FAIL", "Quarantined Tier X Mock Proxy (Apery zeta(3))")

        moduli_cert = {
            "milestone": "M4",
            "target": "S12_vs_elliptic",
            "verdict": "FAIL",
            "is_mock_proxy": True,
            "timestamp": "2026-11-27T19:50:00+00:00",
            "git_commit": "abc1234",
            "details": {"match": False, "details": "Quarantined Tier X mock-proxy check"},
        }
        moduli_path = moduli_dir / "S12_vs_elliptic.json"
        moduli_path.write_text(json.dumps(moduli_cert), encoding="utf-8")

        seq_41 = [i - 10 for i in range(41)]
        deep_path = cert_dir / "deep_verification_triple_check.json"
        f3_path = cert_dir / "f3_oeis_lmfdb_crosscheck.json"
        deep_path.write_text(
            json.dumps({"c_eff_exact": "-823/2310", "verified_sequence": seq_41}),
            encoding="utf-8",
        )
        f3_path.write_text(
            json.dumps({
                "c_eff_exact": "-823/2310",
                "coefficient_sequence_first_20": seq_41[:20],
                "coefficient_sequence_full_40": seq_41,
            }),
            encoding="utf-8",
        )

        campaign_path = cert_dir / "campaign_v2_report.json"
        campaign_path.write_text(
            json.dumps({
                "extraction_errors": 0,
                "lean_kernel_verification": {"mathesis_gate_ok": True},
            }),
            encoding="utf-8",
        )

        llm_path = cert_dir / "llm_lean_validation_report.json"
        llm_path.write_text(
            json.dumps({"approved": True, "overall_verdict": "APPROVED"}),
            encoding="utf-8",
        )

        valid_entropy = {
            "description": "Entropy comparison: RAMA Deep Burn vs Sen Kerr corrections",
            "epistemic_tier": "X",
            "status": "QUARANTINED_LEGACY_SIGN_INVERTED",
            "warning": "QUARANTINED: negative cusp-0 c_eff = -823/2310",
            "parameters": {
                "c_eff_DeepBurn": -823 / 2310,
                "c_eff_DeepBurn_cusp0_exact": "-823/2310",
                "c_eff_DeepBurn_legacy_sign_inverted": 0.3563,
            },
        }
        entropy_path = cert_dir / "entropy_sen_kerr_comparison.json"
        entropy_path.write_text(json.dumps(valid_entropy), encoding="utf-8")

        assert run_certificates.validate_certificates(cert_dir) == []

        # (a) Mock proxy with PASS must be rejected
        moduli_path.write_text(json.dumps(dict(moduli_cert, verdict="PASS")), encoding="utf-8")
        assert any("mock-proxy" in e for e in run_certificates.validate_certificates(cert_dir))
        moduli_path.write_text(json.dumps(moduli_cert), encoding="utf-8")

        # (b) s12_ledger.csv with quarantined/mock/tier X + PASS must be rejected
        write_s12_ledger("PASS", "Quarantined Tier X Mock Proxy")
        assert any("quarantined/mock" in e for e in run_certificates.validate_certificates(cert_dir))
        write_s12_ledger("FAIL", "Quarantined Tier X Mock Proxy (Apery zeta(3))")

        # (c) Deep Burn c_eff_exact or sequence drift must be rejected
        drifted_seq = list(seq_41[:20])
        drifted_seq[6] += 999
        f3_path.write_text(
            json.dumps({"c_eff_exact": "+823/2310", "coefficient_sequence_first_20": drifted_seq}),
            encoding="utf-8",
        )
        errs = run_certificates.validate_certificates(cert_dir)
        assert any("c_eff_exact" in e for e in errs)
        assert any("drifts" in e for e in errs)
        f3_path.write_text(
            json.dumps({
                "c_eff_exact": "-823/2310",
                "coefficient_sequence_first_20": seq_41[:20],
                "coefficient_sequence_full_40": seq_41,
            }),
            encoding="utf-8",
        )

        # (d) campaign_v2_report errors must be rejected
        campaign_path.write_text(
            json.dumps({
                "extraction_errors": 1,
                "lean_kernel_verification": {"mathesis_gate_ok": False},
            }),
            encoding="utf-8",
        )
        errs = run_certificates.validate_certificates(cert_dir)
        assert any("extraction_errors" in e for e in errs)
        assert any("mathesis_gate_ok" in e for e in errs)
        campaign_path.write_text(
            json.dumps({
                "extraction_errors": 0,
                "lean_kernel_verification": {"mathesis_gate_ok": True},
            }),
            encoding="utf-8",
        )

        # (e) llm_lean_validation_report rejection
        llm_path.write_text(
            json.dumps({"approved": False, "overall_verdict": "REJECTED"}),
            encoding="utf-8",
        )
        errs = run_certificates.validate_certificates(cert_dir)
        assert any("approved is True" in e for e in errs)
        assert any("overall_verdict" in e for e in errs)
        llm_path.write_text(
            json.dumps({"approved": True, "overall_verdict": "APPROVED"}),
            encoding="utf-8",
        )

        # (f) Unquarantined entropy_sen_kerr_comparison.json must be rejected
        entropy_path.write_text(
            json.dumps({
                "description": "Legacy unquarantined schema",
                "parameters": {
                    "c_eff_BPS": 6.0,
                    "c_eff_DeepBurn": 0.3563,
                    "c_eff_Kerr_Sen2012": 3.0,
                },
            }),
            encoding="utf-8",
        )
        errs = run_certificates.validate_certificates(cert_dir)
        assert any("epistemic_tier" in e for e in errs)
        assert any("QUARANTINED_LEGACY_SIGN_INVERTED" in e for e in errs)
        assert any("c_eff_DeepBurn_cusp0_exact" in e for e in errs)
        assert any("c_eff_DeepBurn < 0" in e for e in errs)

        entropy_path.write_text(json.dumps(valid_entropy), encoding="utf-8")
        assert run_certificates.validate_certificates(cert_dir) == []

    def test_generator_scripts_emit_hardened_r5_schemas(self, tmp_path):
        f3_mod = _load_module("f3_crosscheck", "dualscale/experiments/f3_oeis_lmfdb_crosscheck.py")
        ent_mod = _load_module("entropy_sen", "dualscale/experiments/entropy_sen_comparison.py")

        # Verify negative-exponent forward loop in expand_eta_power matches partition numbers A000041
        assert f3_mod.expand_eta_power(1, -1, 10) == [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42]

        deep_ref = json.loads(
            (ROOT / "dualscale" / "certificates" / "deep_verification_triple_check.json").read_text(
                encoding="utf-8"
            )
        )
        f3_cert = f3_mod.build_certificate(order=40)
        assert f3_cert["epistemic_tier"] == "B_EXACT_NUMERICS_NON_UNITARY"
        assert f3_cert["c_eff_exact"] == "-823/2310"
        assert f3_cert["c_eff"] == pytest.approx(-823 / 2310)
        assert f3_cert["max_cusp_c_eff_exact"] == "81859/6930"
        assert f3_cert["ground_state_E0_exact"] == "425/6"
        assert f3_cert["ground_state_E0"] == pytest.approx(425 / 6)
        assert f3_cert["is_unitary_bps_state_count"] is False
        assert f3_cert["coefficient_sequence_full_40"] == deep_ref["verified_sequence"]
        assert f3_cert["coefficient_sequence_first_20"] == deep_ref["verified_sequence"][:20]

        ent_cert = ent_mod.build_quarantined_certificate()
        assert ent_cert["epistemic_tier"] == "X"
        assert ent_cert["status"] == "QUARANTINED_LEGACY_SIGN_INVERTED"
        assert ent_cert["parameters"]["c_eff_DeepBurn_cusp0_exact"] == "-823/2310"
        assert ent_cert["parameters"]["c_eff_DeepBurn"] < 0
        assert ent_cert["parameters"]["c_eff_DeepBurn_legacy_sign_inverted"] == 0.3563
        with pytest.raises(ValueError, match="QUARANTINED"):
            ent_mod.S_deep_burn(100)

        cert_dir = tmp_path / "generated_certs"
        cert_dir.mkdir()
        with (cert_dir / "ledger.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["prime", "status"])
            writer.writerow(["2", "PASS"])
        (cert_dir / "deep_verification_triple_check.json").write_text(
            json.dumps(deep_ref), encoding="utf-8"
        )
        (cert_dir / "f3_oeis_lmfdb_crosscheck.json").write_text(
            json.dumps(f3_cert), encoding="utf-8"
        )
        (cert_dir / "entropy_sen_kerr_comparison.json").write_text(
            json.dumps(ent_cert), encoding="utf-8"
        )
        assert run_certificates.validate_certificates(cert_dir) == []

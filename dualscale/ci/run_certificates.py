import argparse
import csv
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional


REQUIRED_CERT_FIELDS = ("milestone", "target", "verdict", "timestamp", "git_commit")
VALID_VERDICTS = {"PASS", "FAIL"}
QUARANTINE_TOKENS = ("MOCK", "QUARANTINED", "TIER X")


def _load_json_object(path: Path, errors: List[str]) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON ({exc})")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path}: JSON root must be an object")
        return None
    return data


def _validate_certificate_record(
    cert_path: Path,
    errors: List[str],
    csv_verdicts: Optional[Dict[str, str]] = None,
    check_spectral_csv: bool = False,
) -> None:
    data = _load_json_object(cert_path, errors)
    if data is None:
        return

    for field in REQUIRED_CERT_FIELDS:
        val = data.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"{cert_path}: missing or empty required field '{field}'")

    verdict = str(data.get("verdict", "")).strip()
    if verdict not in VALID_VERDICTS:
        errors.append(f"{cert_path}: invalid verdict '{verdict}' (expected PASS or FAIL)")

    details = data.get("details")
    if details is not None and not isinstance(details, dict):
        errors.append(f"{cert_path}: 'details' must be an object if present")
        details = {}
    details = details or {}

    note_upper = str(details.get("note", "")).upper()
    details_text_upper = str(details.get("details", "")).upper()
    combined_upper = f"{note_upper}\n{details_text_upper}"
    is_mock_proxy = bool(data.get("is_mock_proxy")) or bool(details.get("is_mock_proxy"))

    if verdict == "PASS":
        if "PLACEHOLDER" in combined_upper:
            errors.append(
                f"{cert_path}: Rule R5 violation — PLACEHOLDER certificate cannot emit verdict=PASS"
            )
        if is_mock_proxy or "MOCK" in combined_upper:
            errors.append(
                f"{cert_path}: Rule R5 violation — mock-proxy certificate cannot emit verdict=PASS"
            )

    if check_spectral_csv and csv_verdicts is not None:
        prime_val = details.get("prime")
        key = f"p{prime_val}" if prime_val is not None else cert_path.name.split("_")[0]
        if key in csv_verdicts and verdict in VALID_VERDICTS and csv_verdicts[key] != verdict:
            errors.append(
                f"{cert_path}: CSV-vs-JSON contradiction for {key} "
                f"(ledger.csv={csv_verdicts[key]} vs {cert_path.name}={verdict})"
            )


def _validate_deep_burn_crosscheck(base: Path, errors: List[str]) -> None:
    deep_path = base / "deep_verification_triple_check.json"
    f3_path = base / "f3_oeis_lmfdb_crosscheck.json"

    deep_data = _load_json_object(deep_path, errors) if deep_path.is_file() else None
    f3_data = _load_json_object(f3_path, errors) if f3_path.is_file() else None

    if deep_data is not None and deep_data.get("c_eff_exact") != "-823/2310":
        errors.append(
            f"{deep_path}: expected c_eff_exact == '-823/2310', got {deep_data.get('c_eff_exact')!r}"
        )
    if f3_data is not None and f3_data.get("c_eff_exact") != "-823/2310":
        errors.append(
            f"{f3_path}: expected c_eff_exact == '-823/2310', got {f3_data.get('c_eff_exact')!r}"
        )

    if deep_data is not None and f3_data is not None:
        verified_seq = deep_data.get("verified_sequence")
        first_20 = f3_data.get("coefficient_sequence_first_20")
        if not isinstance(verified_seq, list) or len(verified_seq) < 20:
            errors.append(f"{deep_path}: 'verified_sequence' must be a list of at least 20 integers")
        elif verified_seq[:20] != first_20:
            errors.append(
                f"{f3_path}: coefficient_sequence_first_20 drifts from {deep_path.name} verified_sequence[:20]"
            )
        full_40 = f3_data.get("coefficient_sequence_full_40")
        if full_40 is not None and isinstance(verified_seq, list) and full_40 != verified_seq:
            errors.append(
                f"{f3_path}: coefficient_sequence_full_40 drifts from {deep_path.name} verified_sequence"
            )


def _validate_entropy_quarantine(base: Path, errors: List[str]) -> None:
    entropy_path = base / "entropy_sen_kerr_comparison.json"
    if not entropy_path.is_file():
        return
    data = _load_json_object(entropy_path, errors)
    if data is None:
        return

    if data.get("epistemic_tier") != "X":
        errors.append(
            f"{entropy_path}: expected epistemic_tier == 'X', got {data.get('epistemic_tier')!r}"
        )
    if data.get("status") != "QUARANTINED_LEGACY_SIGN_INVERTED":
        errors.append(
            f"{entropy_path}: expected status == 'QUARANTINED_LEGACY_SIGN_INVERTED', "
            f"got {data.get('status')!r}"
        )

    params = data.get("parameters")
    if not isinstance(params, dict):
        errors.append(f"{entropy_path}: 'parameters' must be an object")
        return

    if params.get("c_eff_DeepBurn_cusp0_exact") != "-823/2310":
        errors.append(
            f"{entropy_path}: expected parameters.c_eff_DeepBurn_cusp0_exact == '-823/2310', "
            f"got {params.get('c_eff_DeepBurn_cusp0_exact')!r}"
        )

    c_eff_db = params.get("c_eff_DeepBurn")
    if (
        not isinstance(c_eff_db, (int, float))
        or isinstance(c_eff_db, bool)
        or not math.isfinite(c_eff_db)
        or c_eff_db >= 0
    ):
        errors.append(
            f"{entropy_path}: expected finite negative parameters.c_eff_DeepBurn < 0, "
            f"got {c_eff_db!r}"
        )


def _validate_reports(base: Path, errors: List[str]) -> None:
    campaign_path = base / "campaign_v2_report.json"
    if campaign_path.is_file():
        data = _load_json_object(campaign_path, errors)
        if data is not None:
            if data.get("extraction_errors") != 0:
                errors.append(
                    f"{campaign_path}: expected extraction_errors == 0, got {data.get('extraction_errors')!r}"
                )
            lean_ver = data.get("lean_kernel_verification")
            if not isinstance(lean_ver, dict) or lean_ver.get("mathesis_gate_ok") is not True:
                errors.append(
                    f"{campaign_path}: lean_kernel_verification.mathesis_gate_ok must be True"
                )

    llm_report_path = base / "llm_lean_validation_report.json"
    if llm_report_path.is_file():
        data = _load_json_object(llm_report_path, errors)
        if data is not None:
            if data.get("approved") is not True:
                errors.append(
                    f"{llm_report_path}: expected approved is True, got {data.get('approved')!r}"
                )
            if data.get("overall_verdict") != "APPROVED":
                errors.append(
                    f"{llm_report_path}: expected overall_verdict == 'APPROVED', "
                    f"got {data.get('overall_verdict')!r}"
                )

    elenchus_ledger_path = base / "ramanujan_elenchus_audit_ledger.json"
    if elenchus_ledger_path.is_file():
        data = _load_json_object(elenchus_ledger_path, errors)
        if data is not None:
            if data.get("approved") is not True:
                errors.append(
                    f"{elenchus_ledger_path}: expected approved is True, got {data.get('approved')!r}"
                )
            if data.get("overall_verdict") != "APPROVED":
                errors.append(
                    f"{elenchus_ledger_path}: expected overall_verdict == 'APPROVED', "
                    f"got {data.get('overall_verdict')!r}"
                )
            scores = data.get("elenchus_audit_scores")
            if not isinstance(scores, dict) or not scores or not all(v is True for v in scores.values()):
                errors.append(
                    f"{elenchus_ledger_path}: all elenchus_audit_scores must be True, got {scores!r}"
                )


def validate_certificates(cert_dir: Path | str = "dualscale/certificates") -> List[str]:
    """
    Validate CSV ledgers, JSON certificates, and cross-check artifacts under Rule R5.
    Returns a list of error strings (empty means all checks passed).
    """
    base = Path(cert_dir)
    errors: List[str] = []

    ledger_paths = sorted(base.glob("*ledger*.csv"))
    if not ledger_paths:
        return [f"No ledger files found in {base}"]

    csv_verdicts: Dict[str, str] = {}
    for ledger_path in ledger_paths:
        with ledger_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            status_col = "status"
            if "Rule_R5_Status" in fieldnames:
                status_col = "Rule_R5_Status"
            elif "Status" in fieldnames:
                status_col = "Status"

            if status_col not in fieldnames:
                errors.append(f"Missing status column in {ledger_path}")
                continue

            for row in reader:
                status = (row.get(status_col) or "").strip()
                if status not in VALID_VERDICTS:
                    errors.append(f"Certificate schema error (invalid status) in {ledger_path}: {row}")
                row_text_upper = " ".join(str(v or "") for v in row.values()).upper()
                if status == "PASS" and any(tok in row_text_upper for tok in QUARANTINE_TOKENS):
                    errors.append(
                        f"{ledger_path}: Rule R5 violation — quarantined/mock row cannot emit PASS: {row}"
                    )
                if ledger_path.name == "ledger.csv":
                    prime = (row.get("prime") or "").strip()
                    if prime:
                        csv_verdicts[f"p{prime}"] = status

    spectral_dir = base / "spectral"
    if spectral_dir.is_dir():
        cert_files = sorted(spectral_dir.glob("*_certificate.json"))
        if not cert_files:
            errors.append(f"No *_certificate.json files found in {spectral_dir}")

        for cert_path in cert_files:
            _validate_certificate_record(
                cert_path,
                errors,
                csv_verdicts=csv_verdicts,
                check_spectral_csv=True,
            )

    moduli_dir = base / "moduli_map"
    if moduli_dir.is_dir():
        moduli_files = sorted(moduli_dir.glob("*.json"))
        if not moduli_files:
            errors.append(f"No *.json files found in {moduli_dir}")
        for cert_path in moduli_files:
            _validate_certificate_record(cert_path, errors, check_spectral_csv=False)

    _validate_deep_burn_crosscheck(base, errors)
    _validate_entropy_quarantine(base, errors)
    _validate_reports(base, errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Rule R5 certificates and ledgers.")
    parser.add_argument(
        "--cert-dir",
        default="dualscale/certificates",
        help="Path to certificates directory (default: dualscale/certificates)",
    )
    args = parser.parse_args()

    errors = validate_certificates(args.cert_dir)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        print(f"Certificate validation failed with {len(errors)} error(s).")
        return 1

    print("All certificates passed Rule R5 schema and consistency validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

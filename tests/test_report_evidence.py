import copy
import json
from pathlib import Path

import pytest

from ink_fidelity.experiment import MODEL_HASHES
from ink_fidelity.provenance import file_hash, write_json
from ink_fidelity.report import report
from ink_fidelity.upstream import VILLA_SHA
from ink_fidelity.validation import validate_report_rows


@pytest.fixture
def evidence():
    return (
        json.loads(Path("reports/benchmark-records.json").read_text(encoding="utf-8")),
        json.loads(Path("experiments/frozen-test.json").read_text(encoding="utf-8")),
    )


def validate(rows, manifest):
    validate_report_rows(
        rows,
        manifest,
        manifest_sha256=file_hash("experiments/frozen-test.json"),
        model_hashes=MODEL_HASHES,
        upstream_sha=VILLA_SHA,
    )


def test_all_published_real_data_records_pass_without_mutation(evidence):
    rows, manifest = evidence
    saved = copy.deepcopy(rows)
    validate(rows, manifest)
    assert rows == saved


def test_same_row_count_and_unique_run_ids_do_not_hide_missing_experiment(evidence):
    rows, manifest = evidence
    missing = next(i for i, row in enumerate(rows) if row["arm"] == "zstd")
    duplicate = copy.deepcopy(next(row for row in rows if row["arm"] == "q8"))
    duplicate["run_id"] = "f" * 64
    rows[missing] = duplicate
    assert len(rows) == 128 and len({r["run_id"] for r in rows}) == 128
    with pytest.raises(ValueError, match="Duplicate experiment cell"):
        validate(rows, manifest)


def test_missing_cell_is_rejected(evidence):
    rows, manifest = evidence
    with pytest.raises(ValueError, match="Incomplete experiment matrix"):
        validate(rows[:-1], manifest)


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("seed", 99, "Unexpected experiment cell"),
        ("placement", "before-depth-pool", "identity mismatch"),
        ("sample", "different-scroll", "identity mismatch"),
        ("manifest_sha256", "f" * 64, "manifest hash"),
        ("delta_ap", 0.1, "delta_ap arithmetic"),
        ("delta_f1", 0.1, "delta_f1 arithmetic"),
        ("size_ratio_vs_native_zstd", 1000, "Storage ratio arithmetic"),
    ],
)
def test_changed_source_or_derived_fields_are_rejected(evidence, field, replacement, message):
    rows, manifest = evidence
    row = next(r for r in rows if r["arm"] == "q8")
    row[field] = replacement
    with pytest.raises(ValueError, match=message):
        validate(rows, manifest)


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("average_precision", float("nan"), "invalid average_precision"),
        ("f1", 0.001, "F1/confusion arithmetic"),
        ("threshold", 0.7, "threshold mismatch"),
        ("pixels", 1, "denominator/confusion"),
        ("tp", -1, "Invalid confusion count"),
        ("defined", False, "Undefined scored evidence"),
    ],
)
def test_nonfinite_or_inconsistent_metric_evidence_is_rejected(
    evidence, field, replacement, message
):
    rows, manifest = evidence
    next(r for r in rows if r["arm"] == "q8")["metrics"][field] = replacement
    with pytest.raises(ValueError, match=message):
        validate(rows, manifest)


def test_model_runtime_and_lossless_control_receipts_are_enforced(evidence):
    rows, manifest = evidence
    q8 = next(r for r in rows if r["arm"] == "q8")
    q8["inference"]["checkpoint_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="Model/inference"):
        validate(rows, manifest)
    q8["inference"]["checkpoint_sha256"] = MODEL_HASHES[q8["seed"]]
    q8["inference"]["device"] = "different-GPU"
    with pytest.raises(ValueError, match="runtime mismatch"):
        validate(rows, manifest)
    q8["inference"]["device"] = rows[0]["inference"]["device"]
    next(r for r in rows if r["arm"] == "zstd")["probability_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="lossless control"):
        validate(rows, manifest)


def test_invalid_real_data_table_produces_no_report_artifacts(evidence, tmp_path):
    rows, _ = evidence
    for row in rows:
        if row["arm"] == "q8":
            row["delta_ap"] = abs(row["delta_ap"])
    damaged = tmp_path / "damaged.json"
    write_json(damaged, rows, compact_rows=True)
    destination = tmp_path / "reports"
    with pytest.raises(ValueError, match="delta_ap arithmetic"):
        report(damaged, Path("experiments/frozen-test.json"), destination)
    assert not destination.exists()

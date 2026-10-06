from __future__ import annotations

import copy
import json
from pathlib import Path

from .benchmark import benchmark
from .provenance import write_json


def reproduce(results_path: Path, manifest_path: Path, out: Path, cache: Path, receipts_path: Path):
    rows = json.loads(results_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipts = json.loads(receipts_path.read_text(encoding="utf-8"))
    by_sample = {}
    for row in sorted((r for r in rows if r["arm"] == "q8"), key=lambda r: r["delta_ap"]):
        by_sample.setdefault(row["sample"], row)
    selected = sorted(by_sample.values(), key=lambda r: r["delta_ap"])[:2]
    keys = {r["window"] for r in selected}
    subset = copy.deepcopy(manifest)
    subset["records"] = []
    for record in manifest["records"]:
        record = copy.deepcopy(record)
        record["windows"] = [w for w in record["windows"] if w["id"] in keys]
        if record["windows"]:
            subset["records"].append(record)
    subset["selection"] = (
        "Post-test cold-cache reproduction of worst q8 window in each of two distinct scrolls; not new held-out evidence"
    )
    out.mkdir(parents=True, exist_ok=True)
    subset_path = out / "manifest.json"
    write_json(subset_path, subset)
    rerun = benchmark(subset_path, out, cache=cache, receipts=receipts)
    original = {(r["window"], r["seed"], r["arm"]): r for r in rows}
    comparisons = []
    for row in rerun:
        old = original[row["window"], row["seed"], row["arm"]]
        comparisons.append(
            {
                "window": row["window"],
                "seed": row["seed"],
                "arm": row["arm"],
                "metric_max_abs": max(
                    abs(row["metrics"][key] - old["metrics"][key])
                    for key in ("average_precision", "roc_auc", "f1")
                ),
                "probability_file_hash_equal": row["probability_sha256"]
                == old["probability_sha256"],
                "decoded_hash_equal": row["decoded_sha256"] == old["decoded_sha256"],
            }
        )
    result = {
        "post_test_reproduction_not_new_validation": True,
        "distinct_scrolls": sorted(r["sample"] for r in selected),
        "arms_reproduced": len(comparisons),
        "comparisons": comparisons,
        "pass": all(
            c["metric_max_abs"] <= 1e-6
            and c["probability_file_hash_equal"]
            and c["decoded_hash_equal"]
            for c in comparisons
        ),
    }
    write_json(out / "reproduction.json", result)
    if not result["pass"]:
        raise ValueError("Cold-cache reproduction disagrees with original evidence")
    return result

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import numpy as np

from .experiment import MODEL_HASHES
from .metrics import grouped_delta_interval
from .provenance import file_hash, write_json
from .upstream import VILLA_SHA
from .validation import validate_report_rows


def report(results_path: Path, manifest_path: Path, out: Path):
    rows = json.loads(results_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_report_rows(
        rows,
        manifest,
        manifest_sha256=file_hash(manifest_path),
        model_hashes=MODEL_HASHES,
        upstream_sha=VILLA_SHA,
    )
    os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache/matplotlib").resolve()))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for arm in sorted({r["arm"] for r in rows}):
        subset = [r for r in rows if r["arm"] == arm]
        stats = grouped_delta_interval(subset)
        stats["f1"] = grouped_delta_interval(subset, metric="delta_f1")
        stats["windows"] = len({r["window"] for r in subset})
        stats["min_window_seed_delta_ap"] = min(r["delta_ap"] for r in subset)
        stats["min_window_seed_delta_f1"] = min(r["delta_f1"] for r in subset)
        stats["min_store_ratio"] = min(r["size_ratio_vs_native_zstd"] for r in subset)
        stats["median_store_ratio"] = float(
            np.median([r["size_ratio_vs_native_zstd"] for r in subset])
        )
        stats["min_segment_mean_delta_ap"] = min(
            np.mean([r["delta_ap"] for r in subset if r["physical_segment"] == segment])
            for segment in {r["physical_segment"] for r in subset}
        )
        summaries[arm] = stats
    candidate = summaries["q2"]
    candidate["operating_gate_pass"] = (
        candidate["lower95_one_sided"] is not None
        and candidate["lower95_one_sided"] >= -0.005
        and candidate["min_store_ratio"] >= 2
        and candidate["min_segment_mean_delta_ap"] >= -0.02
        and candidate["min_window_seed_delta_f1"] >= -0.01
    )
    losses = [r for r in rows if r["arm"] == "q8" and r["delta_ap"] <= -0.03]
    failure_segments = sorted({r["physical_segment"] for r in losses})
    summary = {
        "record_count": len(rows),
        "window_count": len({r["window"] for r in rows}),
        "physical_segments": len({r["physical_segment"] for r in rows}),
        "samples": sorted({r["sample"] for r in rows}),
        "arms": summaries,
        "q8_material_failure_segments": failure_segments,
        "material_failure_gate_pass": len(failure_segments) >= 2,
        "lossless_max_abs": max(r["max_abs_vs_raw"] for r in rows if r["arm"] == "zstd"),
        "max_vram_bytes": max(r["inference"]["peak_vram_bytes"] for r in rows),
        "max_observed_end_arm_rss": max(r["rss_bytes_after_arm"] for r in rows),
        "largest_loss": min(rows, key=lambda r: r["delta_ap"])["run_id"],
        "manifest_sha256": file_hash(manifest_path),
    }
    write_json(out / "summary.json", summary)
    write_json(out / "benchmark-records.json", rows, compact_rows=True)
    fields = [
        "window",
        "physical_segment",
        "sample",
        "seed",
        "arm",
        "placement",
        "raw_ap",
        "ap",
        "delta_ap",
        "f1",
        "delta_f1",
        "store_bytes",
        "native_zstd_bytes",
        "size_ratio",
        "psnr",
        "mae",
        "prediction_dice",
    ]
    raw_scores = {
        (r["window"], r["seed"]): r["metrics"]["average_precision"]
        for r in rows
        if r["arm"] == "raw"
    }
    with (out / "scores.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    **{k: r[k] for k in fields[:6]},
                    "raw_ap": raw_scores[r["window"], r["seed"]],
                    "ap": r["metrics"]["average_precision"],
                    "delta_ap": r["delta_ap"],
                    "f1": r["metrics"]["f1"],
                    "delta_f1": r["delta_f1"],
                    "store_bytes": r["storage"]["store_bytes"],
                    "native_zstd_bytes": r["native_zstd_bytes"],
                    "size_ratio": r["size_ratio_vs_native_zstd"],
                    "psnr": r["compression"]["psnr"],
                    "mae": r["compression"]["mae"],
                    "prediction_dice": r["drift"]["prediction_dice"],
                }
            )
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    for arm, color in [("q2", "#167c80"), ("q8", "#b54735")]:
        subset = [r for r in rows if r["arm"] == arm]
        axes[0].scatter(
            [r["size_ratio_vs_native_zstd"] for r in subset],
            [r["delta_ap"] for r in subset],
            color=color,
            alpha=0.7,
            label=arm,
            s=32,
        )
    axes[0].axhline(0, color="#555555", linewidth=0.8)
    axes[0].axhline(-0.005, color="#777777", linestyle="--", linewidth=0.8)
    axes[0].set(
        xlabel="Zstd store bytes / lossy store bytes",
        ylabel="Change in masked ink AP",
        title="Storage savings do not establish ink fidelity",
    )
    axes[0].legend()
    segments = sorted({r["physical_segment"] for r in rows})
    for offset, arm, color in [(-0.12, "q2", "#167c80"), (0.12, "q8", "#b54735")]:
        means = [
            np.mean([r["delta_ap"] for r in rows if r["arm"] == arm and r["physical_segment"] == s])
            for s in segments
        ]
        axes[1].scatter(np.arange(len(segments)) + offset, means, color=color, s=50, label=arm)
    axes[1].axhline(0, color="#555555", linewidth=0.8)
    labels = []
    for segment in segments:
        sample, name = segment.split("/", 1)
        if "-w" in name:
            short = "w" + name.split("-w", 1)[1].split("_", 1)[0]
        elif "auto_grown" in name:
            short = "auto-grown"
        else:
            short = name[:8]
        labels.append(sample.replace("PHerc", "") + " / " + short)
    axes[1].set_xticks(range(len(segments)), labels, rotation=25, ha="right", fontsize=9)
    axes[1].set(
        ylabel="Mean paired AP change per physical segment",
        title="Two windows and two seeds per segment",
    )
    fig.savefig(out / "ink-fidelity.png", dpi=180)
    plt.close(fig)
    print(
        json.dumps(
            {
                "operating_gate": candidate["operating_gate_pass"],
                "material_failure_gate": summary["material_failure_gate_pass"],
                "q2": candidate,
                "q8": summaries["q8"],
            },
            indent=2,
        )
    )
    return summary

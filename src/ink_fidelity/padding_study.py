from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import zarr

from .acquisition import Fetcher, mirror_label_array, open_array
from .compression import Codec
from .experiment import MODEL_HASHES, save_input
from .inference import InkModel
from .metrics import ink_metrics
from .provenance import array_hash, file_hash, write_json

LOGGER = logging.getLogger(__name__)


def development_cases(reference):
    return [
        min(
            (r for r in reference if r["arm"] == "q8" and r["sample"] == sample),
            key=lambda r: r["delta_ap"],
        )
        for sample in ("PHercParis4", "PHerc0841")
    ]


def development_region(case, manifest, artifact_root, fetcher):
    segment = next(
        s for s in manifest["records"] if s["physical_segment"] == case["physical_segment"]
    )
    window = next(w for w in segment["windows"] if w["id"] == case["window"])
    raw = np.asarray(open_array(artifact_root / case["window"] / "raw/input.zarr")[:])
    if array_hash(raw) != case["raw_input_sha256"]:
        raise ValueError("Development input differs from the published experiment")
    labels = np.asarray(
        mirror_label_array(
            segment["label_url"] + f"/inklabels.zarr/{segment['label_level']}", fetcher
        )[:]
    )
    supervision = np.asarray(
        mirror_label_array(
            segment["label_url"] + f"/supervision.zarr/{segment['label_level']}", fetcher
        )[:]
    )
    y, x, size, halo = window["y"], window["x"], window["size"], segment["halo"]
    return (
        raw,
        labels[y : y + size, x : x + size] >= 128,
        supervision[y : y + size, x : x + size] >= 128,
        np.s_[halo : halo + size, halo : halo + size],
        segment,
    )


def encoded_padding_store(path: Path, raw: np.ndarray, codec: Codec, policy: str, q=8):
    array = zarr.create_array(
        str(path),
        shape=raw.shape,
        chunks=(128, 128, 128),
        dtype="uint8",
        zarr_format=3,
        compressors=None,
        serializer=codec.module.VolcompCodec(q=q),
        overwrite=True,
        attributes={
            "experimental_encoder_padding": policy,
            "continuation_extent": "next16-voxel-transform-block",
            "zarr_fill_recommendation_deviation": policy != "zero",
        },
    )
    restored, _ = codec.array_roundtrip(raw, kind="volcomp", q=q, padding=policy)
    for y in range(0, raw.shape[1], 128):
        for x in range(0, raw.shape[2], 128):
            for z in range(0, raw.shape[0], 128):
                block = raw[z : z + 128, y : y + 128, x : x + 128]
                padded = codec.pad_chunk(block, policy)
                encoded = codec.module.encode(padded.tobytes(), q)
                target = path / "c" / str(z // 128) / str(y // 128) / str(x // 128)
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_suffix(".partial")
                temporary.write_bytes(encoded)
                temporary.replace(target)
    standard_read = np.asarray(array[:])
    if not np.array_equal(standard_read, restored):
        raise ValueError("Experimental store does not match the standard volcomp reader")
    return {
        "store_bytes": sum(p.stat().st_size for p in path.rglob("*") if p.is_file()),
        "reader_match": True,
        "decoded_sha256": array_hash(standard_read),
    }


def padding_study(results_path: Path, manifest_path: Path, artifact_root: Path, out: Path):
    reference = json.loads(results_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selected = development_cases(reference)
    out.mkdir(parents=True, exist_ok=True)
    write_json(
        out / "selection.json",
        {
            "role": "post-test-exploratory-development",
            "windows": [r["window"] for r in selected],
            "selection": "Worst published q8 region per named scroll, not held out",
        },
    )
    codec = Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))
    models = {
        seed: InkModel(
            Path("external/villa"),
            Path(f"data/models/ink9-seed{seed}.pth"),
            expected_hash=MODEL_HASHES[seed],
        )
        for seed in (42, 43)
    }
    fetcher = Fetcher(Path(".cache/http"), receipts=manifest["acquisition"])
    records = []
    for case in selected:
        raw, lab, sup, area, segment = development_region(case, manifest, artifact_root, fetcher)
        decoded = {}
        codec_records = {}
        for policy in ("zero", "edge", "reflect"):
            decoded[policy], codec_records[policy] = codec.array_roundtrip(
                raw, kind="volcomp", q=8, padding=policy
            )
        boundary = raw.shape[0] // 16 * 16
        if not 0 < boundary < raw.shape[0]:
            raise ValueError("Study requires a partial depth transform block")
        for policy in ("edge", "reflect"):
            if not np.array_equal(decoded[policy][:boundary], decoded["zero"][:boundary]):
                raise ValueError("Full transform blocks changed unexpectedly")
        tail_restored = decoded["zero"].copy()
        tail_restored[boundary:] = raw[boundary:]
        tail_only = raw.copy()
        tail_only[boundary:] = decoded["zero"][boundary:]
        arms = {
            "raw": raw,
            "zero": decoded["zero"],
            "edge": decoded["edge"],
            "reflect": decoded["reflect"],
            "tail-restored": tail_restored,
            "tail-only": tail_only,
        }
        for arm, data in arms.items():
            destination = out / case["window"] / arm
            destination.mkdir(parents=True, exist_ok=True)
            store = (
                encoded_padding_store(destination / "encoded.zarr", raw, codec, arm)
                if arm in decoded
                else None
            )
            save_input(destination / "input.zarr", data)
            plane_mae = (
                np.abs(data.astype(np.float32) - raw.astype(np.float32)).mean(axis=(1, 2)).tolist()
            )
            for seed in (42, 43):
                p, inference = models[seed].predict(
                    destination / "input.zarr",
                    destination / f"seed{seed}.tif",
                    direction=segment["direction"],
                )
                np.save(destination / f"seed{seed}.npy", p)
                metrics = ink_metrics(lab, p[area], sup, threshold=0.5)
                original_raw = next(
                    r
                    for r in reference
                    if r["window"] == case["window"] and r["seed"] == seed and r["arm"] == "raw"
                )
                original_zero = next(
                    r
                    for r in reference
                    if r["window"] == case["window"] and r["seed"] == seed and r["arm"] == "q8"
                )
                probability_hash = file_hash(destination / f"seed{seed}.npy")
                control = original_raw if arm == "raw" else original_zero if arm == "zero" else None
                if control and probability_hash != control["probability_sha256"]:
                    raise ValueError("Padding-study control differs from published prediction")
                raw_prediction = np.load(out / case["window"] / "raw" / f"seed{seed}.npy")
                drift = np.abs(p[area][sup] - raw_prediction[area][sup])
                record = {
                    "role": "post-test-exploratory-development",
                    "window": case["window"],
                    "physical_segment": case["physical_segment"],
                    "seed": seed,
                    "arm": arm,
                    "metrics": metrics,
                    "delta_ap_vs_raw": metrics["average_precision"]
                    - original_raw["metrics"]["average_precision"],
                    "delta_ap_vs_zero": metrics["average_precision"]
                    - original_zero["metrics"]["average_precision"],
                    "plane_mae": plane_mae,
                    "boundary_start": boundary,
                    "codec": codec_records.get(arm),
                    "storage": store,
                    "inference": inference,
                    "decoded_sha256": array_hash(data),
                    "probability_sha256": probability_hash,
                    "supervised_probability_mae_vs_raw": float(drift.mean()),
                    "supervised_probability_max_abs_vs_raw": float(drift.max()),
                }
                records.append(record)
                write_json(out / "results.json", records)
                LOGGER.warning(
                    "Padding %s %s seed%s AP=%.4f improvement=%.4f",
                    case["window"],
                    arm,
                    seed,
                    metrics["average_precision"],
                    record["delta_ap_vs_zero"],
                )
    return records

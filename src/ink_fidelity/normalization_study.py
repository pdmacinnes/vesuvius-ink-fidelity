from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from .acquisition import Fetcher
from .compression import Codec
from .experiment import MODEL_HASHES, save_input
from .inference import InkModel
from .metrics import ink_metrics
from .padding_study import development_cases, development_region
from .provenance import array_hash, file_hash, write_json

LOGGER = logging.getLogger(__name__)


def reference_calibrated(raw, decoded, normalized_raw):
    if raw.shape != decoded.shape or raw.shape != normalized_raw.shape:
        raise ValueError("Reference calibration requires matched patch shapes")
    low, high = (float(v) for v in np.percentile(raw, [1, 99]))
    source = np.clip(raw.astype(np.float32), low, high)
    target = np.clip(decoded.astype(np.float32), low, high)
    if high <= low:
        return normalized_raw.copy(), {"low": low, "high": high, "scale": None, "constant": True}
    flat = source.ravel()
    norm = normalized_raw.ravel()
    imin, imax = int(flat.argmin()), int(flat.argmax())
    denominator = float(norm[imax] - norm[imin])
    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError("Official raw normalization has no recoverable affine scale")
    scale = float(flat[imax] - flat[imin]) / denominator
    calibrated = normalized_raw + (target - source) / np.float32(scale)
    if not np.isfinite(calibrated).all():
        raise ValueError("Non-finite calibrated tensor")
    return np.ascontiguousarray(calibrated, dtype=np.float32), {
        "low": low,
        "high": high,
        "scale": scale,
        "constant": False,
        "raw_vs_decoded_mean_abs": float(np.abs(target - source).mean()),
    }


@contextmanager
def source_normalization(model, raw_path, parameter_records):
    infer = model.infer
    original_dataset = infer.FlatBlockDataset

    class ReferenceDataset(original_dataset):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            if self.preprocessing != "tifxyz_robust":
                raise ValueError("Counterfactual supports the pinned robust normalization only")
            reader = self.reader
            self.raw_reader = infer.FlatPatchReader(
                input_path=str(raw_path),
                resolution=reader.resolution,
                depth_axis_first=reader.depth_axis_first,
                height=reader.height,
                width=reader.width,
                layer_indices=reader.layer_indices,
                output_depth=reader.output_depth,
                preprocessing=reader.preprocessing,
            )

        def __getitem__(self, index):
            _, metadata = super().__getitem__(index)
            block = self.blocks[index]
            raw = np.moveaxis(
                self.raw_reader.read(block.y0, block.x0, self.patch_size, self.patch_size), -1, 0
            )
            decoded = np.moveaxis(
                self.reader.read(block.y0, block.x0, self.patch_size, self.patch_size), -1, 0
            )
            normalized_raw = infer.normalize_flat_patch(raw, self.preprocessing)
            image, parameters = reference_calibrated(raw, decoded, normalized_raw)
            metadata[4] = int(raw.any())
            parameter_records.append({"y": block.y0, "x": block.x0, **parameters})
            return model.torch.from_numpy(image).unsqueeze(0), metadata

    try:
        infer.FlatBlockDataset = ReferenceDataset
        yield
    finally:
        infer.FlatBlockDataset = original_dataset


def normalization_study(results_path: Path, manifest_path: Path, artifact_root: Path, out: Path):
    reference = json.loads(results_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fetcher = Fetcher(Path(".cache/http"), receipts=manifest["acquisition"])
    codec = Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))
    models = {
        seed: InkModel(
            Path("external/villa"),
            Path(f"data/models/ink9-seed{seed}.pth"),
            expected_hash=MODEL_HASHES[seed],
        )
        for seed in (42, 43)
    }
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for case in development_cases(reference):
        raw, lab, sup, area, segment = development_region(case, manifest, artifact_root, fetcher)
        decoded, _ = codec.array_roundtrip(raw, kind="volcomp", q=8)
        root = out / case["window"]
        root.mkdir(exist_ok=True)
        save_input(root / "raw.zarr", raw)
        save_input(root / "q8.zarr", decoded)
        for arm, data_path, fixed in [
            ("raw", root / "raw.zarr", False),
            ("zero-q8", root / "q8.zarr", False),
            ("frozen-raw", root / "raw.zarr", True),
            ("reference-normalized-q8", root / "q8.zarr", True),
        ]:
            for seed, model in models.items():
                parameters = []
                if fixed:
                    with source_normalization(model, root / "raw.zarr", parameters):
                        p, inference = model.predict(
                            data_path,
                            root / f"{arm}-seed{seed}.tif",
                            direction=segment["direction"],
                        )
                else:
                    p, inference = model.predict(
                        data_path, root / f"{arm}-seed{seed}.tif", direction=segment["direction"]
                    )
                path = root / f"{arm}-seed{seed}.npy"
                np.save(path, p)
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
                control = (
                    original_raw
                    if arm in ("raw", "frozen-raw")
                    else original_zero
                    if arm == "zero-q8"
                    else None
                )
                if control and file_hash(path) != control["probability_sha256"]:
                    raise ValueError("Normalization-control prediction hash mismatch")
                raw_prediction = np.load(root / f"raw-seed{seed}.npy")
                drift = np.abs(p[area][sup] - raw_prediction[area][sup])
                record = {
                    "role": "post-test-exploratory-counterfactual",
                    "window": case["window"],
                    "physical_segment": case["physical_segment"],
                    "seed": seed,
                    "arm": arm,
                    "metrics": metrics,
                    "inference": inference,
                    "delta_ap_vs_raw": metrics["average_precision"]
                    - original_raw["metrics"]["average_precision"],
                    "delta_ap_vs_zero": metrics["average_precision"]
                    - original_zero["metrics"]["average_precision"],
                    "source_reference_required": fixed,
                    "parameters": parameters,
                    "probability_sha256": file_hash(path),
                    "decoded_sha256": array_hash(raw if arm in ("raw", "frozen-raw") else decoded),
                    "supervised_probability_mae_vs_raw": float(drift.mean()),
                    "supervised_probability_max_abs_vs_raw": float(drift.max()),
                }
                records.append(record)
                write_json(out / "results.json", records)
                LOGGER.warning(
                    "Normalization %s %s seed%s AP=%.4f delta=%.4f",
                    case["window"],
                    arm,
                    seed,
                    metrics["average_precision"],
                    record["delta_ap_vs_zero"],
                )
    return records

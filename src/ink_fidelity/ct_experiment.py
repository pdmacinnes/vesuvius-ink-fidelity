from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

from .acquisition import Fetcher, RemoteV2Array, acquire_mesh, mirror_label_array
from .compression import Codec
from .experiment import MODEL_HASHES, save_input
from .inference import InkModel
from .metrics import ink_metrics
from .provenance import array_hash, write_json
from .rendering import render_surface

LOGGER = logging.getLogger(__name__)


def ct_experiment(manifest_path: Path, out: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fetcher = Fetcher(Path(".cache/http"))
    acquire_mesh(manifest["mesh_url"], Path(manifest["mesh"]), fetcher)
    reader = RemoteV2Array(manifest["ct_url"], fetcher)
    surface = RemoteV2Array(manifest["surface_url"], fetcher)
    codec = Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))
    models = {
        seed: InkModel(
            Path("external/villa"),
            Path(f"data/models/ink9-seed{seed}.pth"),
            expected_hash=MODEL_HASHES[seed],
        )
        for seed in (42, 43)
    }
    labels = np.asarray(mirror_label_array(manifest["label_url"] + "/inklabels.zarr/0", fetcher)[:])
    supervision = np.asarray(
        mirror_label_array(manifest["label_url"] + "/supervision.zarr/0", fetcher)[:]
    )
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for window in manifest["windows"]:
        halo, size = 128, 128
        candidates = []
        for y0 in range(window["y"], window["y"] + window["size"] - size + 1, 128):
            for x0 in range(window["x"], window["x"] + window["size"] - size + 1, 128):
                mask = supervision[y0 : y0 + size, x0 : x0 + size] > 0
                ink = labels[y0 : y0 + size, x0 : x0 + size] > 0
                if (ink & mask).sum() >= 100 and (~ink & mask).sum() >= 100:
                    candidates.append((-int(mask.sum()), y0, x0))
        if not candidates:
            raise ValueError("No two-class supervised CT control within the pilot window")
        _, y, x = min(candidates)
        bounds = (y - halo, y + size + halo, x - halo, x + size + halo)
        raw_predictions = {}
        reference = surface.read((0, bounds[0], bounds[2]), (28, size + 2 * halo, size + 2 * halo))
        for name, kind, q in [
            ("raw", "raw", 0),
            ("zstd", "zstd", 0),
            ("q2", "volcomp", 2),
            ("q8", "volcomp", 8),
        ]:
            rendered, info = render_surface(
                reader,
                Path(manifest["mesh"]),
                villa=Path("external/villa"),
                canvas_shape=tuple(manifest["canvas_shape"]),
                bounds=bounds,
                offsets=list(np.arange(28, dtype=float) - 13.5),
                kind=kind,
                q=q,
                codec=codec,
            )
            # VC3D stores uint8 CT samples by truncation; compare like with like.
            data = np.clip(rendered, 0, 255).astype(np.uint8)
            if name == "raw":
                mae = float(np.abs(data.astype(float) - reference).mean())
                corr = float(np.corrcoef(data.ravel(), reference.ravel())[0, 1])
                if mae >= 2 or corr <= 0.98:
                    raise ValueError(f"Raw rendering parity failed: MAE={mae}, correlation={corr}")
                info["parity_mae"] = mae
                info["parity_correlation"] = corr
                raw_hash = array_hash(data)
            if name == "zstd" and array_hash(data) != raw_hash:
                raise ValueError("Lossless raw CT rendering parity failed")
            destination = out / f"{window['id']}-{name}"
            destination.mkdir(exist_ok=True)
            save_input(destination / "input.zarr", data)
            for seed in (42, 43):
                prediction, inference = models[seed].predict(
                    destination / "input.zarr", destination / f"seed{seed}.tif", direction="forward"
                )
                area = np.s_[halo : halo + size, halo : halo + size]
                score = ink_metrics(
                    labels[y : y + size, x : x + size],
                    prediction[area],
                    supervision[y : y + size, x : x + size],
                    threshold=0.5,
                )
                if name == "raw":
                    raw_predictions[seed] = score
                row = {
                    "window": window["id"],
                    "seed": seed,
                    "arm": name,
                    "role": "development",
                    "placement": "raw-CT-before-render",
                    "metrics": score,
                    "delta_ap": score["average_precision"]
                    - raw_predictions[seed]["average_precision"]
                    if score["defined"]
                    else None,
                    "scored_bounds": [y, y + size, x, x + size],
                    "render": info,
                    "inference": inference,
                    "input_sha256": array_hash(data),
                }
                records.append(row)
                write_json(out / "results.json", records)
                LOGGER.warning(
                    "CT %s %s seed%s AP=%.4f delta=%.4f",
                    window["id"],
                    name,
                    seed,
                    score["average_precision"],
                    row["delta_ap"],
                )
        write_json(out / "acquisition.json", list(fetcher.records.values()))
    return records

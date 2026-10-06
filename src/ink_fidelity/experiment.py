from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import zarr
from numcodecs import Blosc

from .acquisition import Fetcher, RemoteV2Array, acquire_mesh, mirror_label_array
from .compression import Codec
from .inference import InkModel
from .metrics import ink_metrics, prediction_drift
from .provenance import array_hash, canonical_hash, file_hash, write_json
from .rendering import render_surface

MODEL_HASHES = {
    42: "e635558ae6a1a807a7e5ec1e83adfd45bc3c0ac53883ea43f1d4e085d62a9cab",
    43: "2aeaa85a35ef28d7bc7bf3e848c4a6a91385e9132710927fdba41133c4ecb28f",
}
LOGGER = logging.getLogger(__name__)


def save_input(path: Path, data: np.ndarray):
    result = zarr.create_array(
        str(path),
        shape=data.shape,
        chunks=(data.shape[0], 128, 128),
        dtype=data.dtype,
        zarr_format=2,
        compressors=Blosc(cname="zstd", clevel=3, shuffle=2),
        overwrite=True,
    )
    result[:] = data
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def pilot(manifest_path: Path, out: Path, *, render_only=False, seed=42):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(Path(".cache/http"))
    surface = RemoteV2Array(manifest["surface_url"], fetcher)
    codec = Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))
    if render_only:
        acquire_mesh(manifest["mesh_url"], Path(manifest["mesh"]), fetcher)
        window = manifest["windows"][0]
        y, x = window["y"], window["x"]
        shape = 128
        reference = surface.read((0, y, x), (surface.shape[0], shape, shape))
        reader = RemoteV2Array(manifest["ct_url"], fetcher)
        rendered, record = render_surface(
            reader,
            Path(manifest["mesh"]),
            villa=Path("external/villa"),
            canvas_shape=tuple(manifest["canvas_shape"]),
            bounds=(y, y + shape, x, x + shape),
            offsets=list(np.arange(surface.shape[0], dtype=float) - (surface.shape[0] - 1) / 2),
        )
        delta = rendered - reference.astype(np.float32)
        correlation = float(np.corrcoef(rendered.ravel(), reference.ravel())[0, 1])
        result = {
            "mae": float(np.abs(delta).mean()),
            "correlation": correlation,
            "layer_mae": np.abs(delta).mean(axis=(1, 2)).tolist(),
            "mean_delta": float(delta.mean()),
            "render": record,
            "pass": correlation > 0.98 and float(np.abs(delta).mean()) < 2,
            "acquisition": list(fetcher.records.values()),
        }
        np.savez_compressed(out / "parity-arrays.npz", reference=reference, rendered=rendered)
        write_json(out / "parity.json", result)
        print(json.dumps({k: result[k] for k in ("mae", "correlation", "mean_delta", "pass")}))
        return result
    labels = np.asarray(mirror_label_array(manifest["label_url"] + "/inklabels.zarr/0", fetcher)[:])
    supervision = np.asarray(
        mirror_label_array(manifest["label_url"] + "/supervision.zarr/0", fetcher)[:]
    )
    if labels.shape != tuple(surface.shape[1:]) or labels.shape != supervision.shape:
        raise ValueError("Label/surface canvas mismatch")
    model = InkModel(
        Path("external/villa"),
        Path(f"data/models/ink9-seed{seed}.pth"),
        expected_hash=MODEL_HASHES[seed],
    )
    all_records = []
    arms = [
        ("raw", "raw", 0, False),
        ("zstd", "zstd", 0, False),
        ("q2", "volcomp", 2, False),
        ("q4", "volcomp", 4, False),
        ("q8", "volcomp", 8, False),
        ("q8-smooth", "volcomp", 8, True),
    ]
    for window in manifest["windows"]:
        y, x, size, halo = window["y"], window["x"], window["size"], manifest["halo"]
        data = surface.read(
            (0, y - halo, x - halo), (surface.shape[0], size + 2 * halo, size + 2 * halo)
        )
        score_slice = np.s_[halo : halo + size, halo : halo + size]
        lab, sup = labels[y : y + size, x : x + size], supervision[y : y + size, x : x + size]
        predictions = {}
        for name, kind, quality, smooth in arms:
            destination = out / f"{window['id']}-seed{seed}-{name}"
            destination.mkdir(exist_ok=True)
            restored, compression = codec.array_roundtrip(data, kind=kind, q=quality, smooth=smooth)
            stored = save_input(destination / "input.zarr", restored)
            p, inference = model.predict(
                destination / "input.zarr",
                destination / "prediction.tif",
                direction=manifest["direction"],
            )
            predictions[name] = p
            np.save(destination / "probability.npy", p)
            scored = ink_metrics(lab, p[score_slice], sup, threshold=manifest["threshold"])
            record = {
                "window": window["id"],
                "seed": seed,
                "arm": name,
                "physical_segment": manifest["physical_segment"],
                "role": "development",
                "manifest_sha256": file_hash(manifest_path),
                "input_sha256": array_hash(data),
                "decoded_sha256": array_hash(restored),
                "compression": compression,
                "materialized_lossless_input_bytes": stored,
                "inference": inference,
                "ink_metrics": scored,
                "drift": prediction_drift(
                    predictions["raw"][score_slice],
                    p[score_slice],
                    sup,
                    threshold=manifest["threshold"],
                ),
            }
            if name == "raw":
                repeat, _ = model.predict(
                    destination / "input.zarr",
                    destination / "repeat.tif",
                    direction=manifest["direction"],
                )
                record["repeat_max_abs"] = float(np.abs(repeat - p).max())
                if record["repeat_max_abs"] > 1e-6:
                    raise ValueError("Raw inference repeatability failed")
            if name == "zstd" and float(np.abs(p - predictions["raw"]).max()) > 1e-6:
                raise ValueError("Lossless prediction control failed")
            record["run_id"] = canonical_hash(
                {
                    "window": window,
                    "seed": seed,
                    "arm": name,
                    "input": record["input_sha256"],
                    "model": model.checkpoint_hash,
                }
            )
            write_json(destination / "result.json", record)
            all_records.append(record)
            LOGGER.warning(
                "%s seed=%s arm=%s AP=%.4f AUC=%.4f",
                window["id"],
                seed,
                name,
                scored["average_precision"],
                scored["roc_auc"],
            )
        write_json(out / f"results-seed{seed}.json", all_records)
    write_json(out / f"acquisition-seed{seed}.json", list(fetcher.records.values()))
    return all_records

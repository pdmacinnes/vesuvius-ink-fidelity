from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import numpy as np
import psutil
import zarr
from numcodecs import Blosc

from .acquisition import Fetcher, RemoteV2Array, mirror_label_array
from .compression import Codec
from .experiment import MODEL_HASHES, save_input
from .inference import InkModel
from .metrics import ink_metrics, prediction_drift
from .provenance import array_hash, canonical_hash, file_hash, write_json
from .upstream import VILLA_SHA, add_source
from .validation import validate_test_manifest, verified_resume

LOGGER = logging.getLogger(__name__)


def depth_pool(source: np.ndarray, factor: int) -> np.ndarray:
    if factor == 1:
        return source
    if factor != 4:
        raise ValueError("Only the official four-plane depth pooling is supported")
    from vesuvius.ink_detection.preprocessing.prepare_9um_isotropic_input import centered_slice

    z0, z1 = centered_slice(source.shape[0], 84)
    return np.rint(
        source[z0:z1].astype(np.float32).reshape(21, 4, *source.shape[1:]).mean(axis=1)
    ).astype(np.uint8)


def save_encoded(path: Path, raw: np.ndarray, codec: Codec, *, kind: str, q=2):
    start = time.perf_counter()
    if kind == "volcomp":
        array = zarr.create_array(
            str(path),
            shape=raw.shape,
            chunks=(128, 128, 128),
            dtype="uint8",
            zarr_format=3,
            compressors=None,
            serializer=codec.module.VolcompCodec(q=q),
            overwrite=True,
        )
    else:
        array = zarr.create_array(
            str(path),
            shape=raw.shape,
            chunks=(128, 128, 128),
            dtype="uint8",
            zarr_format=2,
            compressors=Blosc(cname="zstd", clevel=3, shuffle=2),
            overwrite=True,
        )
    array[:] = raw
    size = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    decoded = np.asarray(array[:])
    return {
        "store_bytes": size,
        "write_verify_seconds": time.perf_counter() - start,
        "decoded_sha256": array_hash(decoded),
        "padding_and_metadata_included": True,
    }


def benchmark(
    manifest_path: Path, out: Path, *, seeds=(42, 43), cache=Path(".cache/http"), receipts=None
):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_test_manifest(manifest)
    manifest_hash = file_hash(manifest_path)
    fetcher = Fetcher(cache, receipts=receipts or manifest.get("acquisition"))
    codec = Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))
    add_source(Path("external/villa"), "vesuvius/src", VILLA_SHA)
    out.mkdir(parents=True, exist_ok=True)
    models = {
        seed: InkModel(
            Path("external/villa"),
            Path(f"data/models/ink9-seed{seed}.pth"),
            expected_hash=MODEL_HASHES[seed],
        )
        for seed in seeds
    }
    rows = []
    for segment in manifest["records"]:
        reader = RemoteV2Array(segment["surface_url"], fetcher)
        if tuple(segment["surface_shape"]) != reader.shape:
            raise ValueError("Source array shape changed from the frozen manifest")
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
        if labels.shape != supervision.shape or labels.shape != reader.shape[1:]:
            raise ValueError("Label/surface canvas mismatch")
        for window in segment["windows"]:
            y, x, size, halo = window["y"], window["x"], window["size"], segment["halo"]
            source = reader.read(
                (0, y - halo, x - halo), (reader.shape[0], size + 2 * halo, size + 2 * halo)
            )
            raw = depth_pool(source, segment["depth_pool"])
            lab = labels[y : y + size, x : x + size] >= 128
            sup = supervision[y : y + size, x : x + size] >= 128
            area = np.s_[halo : halo + size, halo : halo + size]
            root = out / window["id"]
            root.mkdir(exist_ok=True)
            raw_hash = array_hash(raw)
            native_lossless = save_input(root / "lossless-native.zarr", raw)
            arms = [
                ("raw", "raw", 0, "model-input"),
                ("zstd", "zstd", 0, "model-input"),
                ("q2", "volcomp", 2, "model-input"),
                ("q8", "volcomp", 8, "model-input"),
            ]
            if segment["depth_pool"] == 4:
                arms += [
                    ("q2-before-pool", "volcomp", 2, "before-depth-pool"),
                    ("q8-before-pool", "volcomp", 8, "before-depth-pool"),
                ]
            references = {}
            for name, kind, q, placement in arms:
                input_data = source if placement == "before-depth-pool" else raw
                decoded, compression = codec.array_roundtrip(input_data, kind=kind, q=q)
                restored = depth_pool(decoded, 4) if placement == "before-depth-pool" else decoded
                destination = root / name
                destination.mkdir(exist_ok=True)
                if kind != "raw":
                    storage = save_encoded(
                        destination / "encoded.zarr", input_data, codec, kind=kind, q=q
                    )
                    if storage["decoded_sha256"] != array_hash(decoded):
                        raise ValueError("Actual codec store disagrees with bytes-level round trip")
                else:
                    storage = {
                        "store_bytes": input_data.nbytes,
                        "padding_and_metadata_included": False,
                    }
                save_input(destination / "input.zarr", restored)
                for seed in seeds:
                    identity = {
                        "manifest": manifest_hash,
                        "window": window,
                        "seed": seed,
                        "arm": name,
                        "input": array_hash(restored),
                        "model": models[seed].checkpoint_hash,
                        "upstream": VILLA_SHA,
                        "threshold": manifest["threshold"],
                        "direction": segment["direction"],
                        "runtime": {
                            "torch": models[seed].torch.__version__,
                            "numpy": np.__version__,
                            "zarr": zarr.__version__,
                            "cuda": models[seed].torch.version.cuda,
                        },
                        "inference_contract": "fp32-tf32off-center17-stride64-hann-v1",
                    }
                    run_id = canonical_hash(identity)
                    record_path = destination / f"seed{seed}.json"
                    probability_path = destination / f"seed{seed}.npy"
                    if record_path.exists() and probability_path.exists():
                        cached = json.loads(record_path.read_text(encoding="utf-8"))
                        if verified_resume(
                            cached,
                            run_id=run_id,
                            probability_path=probability_path,
                            hash_file=file_hash,
                        ):
                            p = np.load(probability_path)
                            rows.append(cached)
                            if name == "raw":
                                references[seed] = p
                            LOGGER.warning("Resume verified %s %s seed%s", window["id"], name, seed)
                            continue
                    p, inference = models[seed].predict(
                        destination / "input.zarr",
                        destination / f"seed{seed}.tif",
                        direction=segment["direction"],
                    )
                    np.save(probability_path, p)
                    metrics = ink_metrics(lab, p[area], sup, threshold=manifest["threshold"])
                    if name == "raw":
                        references[seed] = p
                    raw_metrics = ink_metrics(
                        lab, references[seed][area], sup, threshold=manifest["threshold"]
                    )
                    difference = float(np.abs(p - references[seed]).max())
                    if name == "zstd" and difference > 1e-6:
                        raise ValueError("Lossless baseline prediction mismatch")
                    row = {
                        "run_id": run_id,
                        "manifest_sha256": manifest_hash,
                        "window": window["id"],
                        "physical_segment": segment["physical_segment"],
                        "sample": segment["sample_id"],
                        "training_exposure": segment["training_exposure"],
                        "seed": seed,
                        "arm": name,
                        "placement": placement,
                        "role": "frozen-test",
                        "raw_input_sha256": raw_hash,
                        "decoded_sha256": array_hash(restored),
                        "metrics": metrics,
                        "inference": inference,
                        "compression": compression,
                        "storage": storage,
                        "native_zstd_bytes": native_lossless,
                        "size_ratio_vs_native_zstd": native_lossless / storage["store_bytes"],
                        "delta_ap": metrics["average_precision"] - raw_metrics["average_precision"]
                        if metrics["defined"]
                        else None,
                        "delta_f1": metrics["f1"] - raw_metrics["f1"]
                        if metrics["defined"]
                        else None,
                        "max_abs_vs_raw": difference,
                        "drift": prediction_drift(
                            references[seed][area], p[area], sup, threshold=manifest["threshold"]
                        ),
                        "probability_sha256": file_hash(probability_path),
                        "rss_bytes_after_arm": psutil.Process().memory_info().rss,
                        "os_peak_rss_bytes": getattr(
                            psutil.Process().memory_info(), "peak_wset", None
                        ),
                    }
                    write_json(record_path, row)
                    rows.append(row)
                    LOGGER.warning(
                        "%s seed%s %s AP=%.4f delta=%.4f",
                        window["id"],
                        seed,
                        name,
                        metrics["average_precision"],
                        row["delta_ap"],
                    )
                write_json(out / "results.json", rows)
            write_json(out / "acquisition.json", list(fetcher.records.values()))
    return rows

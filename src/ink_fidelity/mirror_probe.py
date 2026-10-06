from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from .acquisition import Fetcher, RemoteV2Array, acquire_mesh, open_array
from .compression import Codec
from .provenance import array_hash, file_hash, write_json
from .rendering import render_surface


class HttpBudget:
    def __init__(self, max_bytes=64 << 20):
        self.max_bytes = max_bytes
        self.announced_bytes = 0
        self.requests = []

    def observe(self, *, status, headers, requested_range=None, method="GET"):
        if method == "HEAD":
            return
        length = headers.get("Content-Length")
        if length is None or not str(length).isdigit():
            raise ValueError("HTTP probe requires an explicit response length")
        length = int(length)
        if requested_range:
            if status != 206:
                raise ValueError("Server ignored or rejected a bounded Range request")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", headers.get("Content-Range", ""))
            requested = re.fullmatch(r"bytes=(\d*)-(\d*)", requested_range)
            if match is None or requested is None:
                raise ValueError("Invalid HTTP range contract")
            start, end, total = map(int, match.groups())
            first, last = requested.groups()
            if not first and not last:
                raise ValueError("Empty HTTP range")
            wanted_start = int(first) if first else max(0, total - int(last))
            wanted_end = min(int(last), total - 1) if first and last else total - 1
            if (
                not 0 <= start <= end < total
                or (start, end) != (wanted_start, wanted_end)
                or length != end - start + 1
                or headers.get("Content-Encoding", "identity") != "identity"
            ):
                raise ValueError("Response does not match the requested byte range")
        if self.announced_bytes + length > self.max_bytes:
            raise ValueError("HTTP probe transfer budget exceeded before body read")
        self.announced_bytes += length
        self.requests.append({"status": status, "range": requested_range, "body_bytes": length})

    def trace(self):
        import aiohttp

        config = aiohttp.TraceConfig()

        async def ended(_session, _context, params):
            response = params.response
            self.observe(
                status=response.status,
                headers=response.headers,
                requested_range=response.request_info.headers.get("Range"),
                method=response.method,
            )

        config.on_request_end.append(ended)
        return config


def mirror_metadata_contract(metadata, original):
    if (
        metadata.get("zarr_format") != 3
        or metadata.get("node_type") != "array"
        or tuple(metadata.get("shape", [])) != original.shape
        or metadata.get("data_type") != "uint8"
        or tuple(metadata.get("dimension_names") or ()) != ("z", "y", "x")
        or original.dtype != np.uint8
        or original.chunks != (128, 128, 128)
    ):
        raise ValueError("Mirror source shape/dtype/frame contract mismatch")
    codecs = metadata.get("codecs", [])
    if len(codecs) != 1 or codecs[0].get("name") != "sharding_indexed":
        raise ValueError("Mirror requires the standard sharding codec")
    shard = codecs[0]["configuration"]
    if tuple(shard.get("chunk_shape") or ()) != (128, 128, 128) or tuple(
        shard.get("codecs") or ()
    ) != ({"name": "volcomp", "configuration": {"q": 8.0}},):
        raise ValueError("Mirror codec/chunk contract mismatch")


def mirror_probe(
    manifest_path: Path,
    reference_path: Path,
    out: Path,
    *,
    receipts_path: Path = Path("reports/mirror-source-receipts.json"),
    cache: Path = Path(".cache/http"),
    expand=False,
):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    keys = sorted(
        {
            tuple(c["key"])
            for r in reference
            if r["arm"] == "raw"
            for c in r["render"]["chunk_records"]
        }
    )
    if len(keys) < 3:
        raise ValueError("Three source-identified CT chunks are required")
    selected = [keys[0], keys[len(keys) // 2], keys[-1]]
    original_url = manifest["ct_url"]
    prefix = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/"
    if not original_url.startswith(prefix):
        raise ValueError("Probe requires the documented original catalog host")
    mirror_url = original_url.replace(
        prefix, "https://dl.ash2txt.org/community-uploads/forrest/volcomp/", 1
    )
    out.mkdir(parents=True, exist_ok=True)
    write_json(
        out / "selection.json",
        {
            "role": "bounded-format-parity-development",
            "original_url": original_url,
            "mirror_url": mirror_url,
            "reference_sha256": file_hash(reference_path),
            "preflight_keys": selected,
            "expanded_keys": keys if expand else [],
            "selection": "First/middle/last sorted keys of previous CT crops, before mirror values",
        },
    )
    receipts = json.loads(receipts_path.read_text(encoding="utf-8"))
    fetcher = Fetcher(cache, max_bytes=(256 if expand else 20) << 20, receipts=receipts)
    original = RemoteV2Array(original_url, fetcher)
    metadata = fetcher.json(mirror_url + "/zarr.json")
    codec = Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))
    previous_smoothing = codec.module.set_read_smoothing(0)
    budget = HttpBudget()
    records, rendered_records = [], []
    report = {
        "role": "bounded-format-parity-development",
        "gpu_inference_launched": False,
        "manifest_sha256": file_hash(manifest_path),
        "reference_sha256": file_hash(reference_path),
        "receipts_sha256": file_hash(receipts_path),
        "original_url": original_url,
        "mirror_url": mirror_url,
        "index_location": None,
        "records": records,
        "renders": rendered_records,
        "pass": False,
    }
    try:
        mirror_metadata_contract(metadata, original)
        report["index_location"] = metadata["codecs"][0]["configuration"].get("index_location")
        mirror = open_array(
            mirror_url,
            zarr_format=3,
            storage_options={"client_kwargs": {"trace_configs": [budget.trace()]}, "block_size": 0},
        )
        mirror_metadata_contract(mirror.metadata.to_dict(), original)
        cached = {}

        def chunk(key):
            if key not in cached:
                cached[key] = np.asarray(mirror[tuple(slice(k * 128, (k + 1) * 128) for k in key)])
            return cached[key]

        for key in selected + ([k for k in keys if k not in selected] if expand else []):
            raw = original.chunk(key)
            local, _ = codec.roundtrip(raw, kind="volcomp", q=8)
            deployed = chunk(key)
            if deployed.shape != raw.shape:
                raise ValueError("Mirror chunk shape mismatch")
            delta = deployed.astype(np.float32) - raw.astype(np.float32)
            match = np.array_equal(deployed, local)
            records.append(
                {
                    "key": key,
                    "raw_sha256": array_hash(raw),
                    "local_q8_sha256": array_hash(local),
                    "mirror_sha256": array_hash(deployed),
                    "local_q8_equal": match,
                    "raw_mae": float(np.abs(delta).mean()),
                    "raw_max_abs": float(np.abs(delta).max()),
                    "local_q8_max_abs": int(np.abs(deployed.astype(int) - local.astype(int)).max()),
                }
            )
            write_json(out / "results.json", report)
            if not match:
                raise ValueError(f"Mirror/local-q8 disagreement at {key}; expansion stopped")
        if expand:
            acquire_mesh(manifest["mesh_url"], Path(manifest["mesh"]), fetcher)

            class MirrorReader:
                shape, chunks, dtype = original.shape, original.chunks, original.dtype

                def chunk(self, key):
                    if key not in cached:
                        raise ValueError("Render attempted an unregistered source chunk")
                    return cached[key]

            for row in reference:
                if row["arm"] != "q8" or row["seed"] != 42:
                    continue
                image, _ = render_surface(
                    MirrorReader(),
                    Path(manifest["mesh"]),
                    villa=Path("external/villa"),
                    canvas_shape=tuple(manifest["canvas_shape"]),
                    bounds=tuple(row["render"]["bounds"]),
                    offsets=row["render"]["offsets"],
                )
                decoded = np.clip(image, 0, 255).astype(np.uint8)
                match = array_hash(decoded) == row["input_sha256"]
                rendered_records.append(
                    {
                        "window": row["window"],
                        "input_sha256": array_hash(decoded),
                        "published_q8_input_equal": match,
                    }
                )
                if not match:
                    raise ValueError("Public mirror render differs from historical q8 model input")
        report["pass"] = True
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        codec.module.set_read_smoothing(previous_smoothing)
        report["announced_http_body_bytes"] = budget.announced_bytes
        report["http_requests"] = budget.requests
        report["source_receipts"] = list(fetcher.records.values())
        report["original_source_bytes_received"] = fetcher.bytes_received
        write_json(out / "results.json", report)
    return report

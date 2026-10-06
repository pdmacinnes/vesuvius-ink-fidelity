from __future__ import annotations

import itertools
import os
import time
from pathlib import Path

import numpy as np
from numcodecs import Blosc

from .upstream import VOLCOMP_SHA, add_source


class Codec:
    def __init__(self, repository: Path, library: Path):
        add_source(repository, "python", VOLCOMP_SHA)
        os.environ["VOLCOMP_LIB"] = str(Path(library).resolve())
        import volcomp_zarr

        self.module = volcomp_zarr
        self.lossless = Blosc(cname="zstd", clevel=3, shuffle=Blosc.BITSHUFFLE)

    def roundtrip(self, chunk: np.ndarray, *, kind: str, q=8, smooth=False):
        if chunk.dtype != np.uint8 or chunk.ndim != 3 or any(s > 128 for s in chunk.shape):
            raise ValueError("Codec chunk requires uint8, 3 dimensions, each at most 128")
        padded = np.zeros((128, 128, 128), dtype=np.uint8)
        slices = tuple(slice(0, s) for s in chunk.shape)
        padded[slices] = chunk
        raw = padded.tobytes()
        start = time.perf_counter()
        if kind == "zstd":
            encoded = bytes(self.lossless.encode(raw))
        elif kind == "volcomp":
            encoded = self.module.encode(raw, q)
        elif kind == "raw":
            encoded = raw
        else:
            raise ValueError(f"Unknown codec {kind}")
        encode_seconds = time.perf_counter() - start
        start = time.perf_counter()
        if kind == "zstd":
            decoded = self.lossless.decode(encoded)
        elif kind == "volcomp":
            decoded = (
                self.module.decode_smooth(encoded, 2.0, zero_guard=True, gated=True)
                if smooth
                else self.module.decode(encoded)
            )
        else:
            decoded = encoded
        decode_seconds = time.perf_counter() - start
        restored = np.frombuffer(decoded, dtype=np.uint8).reshape(padded.shape)[slices].copy()
        if (kind in ("raw", "zstd") or q == 0) and not np.array_equal(chunk, restored):
            raise ValueError("Lossless control failed")
        delta = chunk.astype(np.float32) - restored.astype(np.float32)
        mse = float(np.mean(delta * delta))
        return restored, {
            "encoded_bytes": len(encoded),
            "valid_bytes": chunk.nbytes,
            "padded_bytes": padded.nbytes,
            "encode_seconds": encode_seconds,
            "decode_seconds": decode_seconds,
            "mae": float(np.abs(delta).mean()),
            "psnr": float(10 * np.log10(255**2 / mse)) if mse else None,
        }

    def array_roundtrip(self, array: np.ndarray, *, kind: str, q=8, smooth=False):
        if array.ndim != 3 or array.dtype != np.uint8:
            raise ValueError("Compression input must be a 3D uint8 array")
        output = np.empty_like(array)
        records = []
        for origin in itertools.product(*[range(0, s, 128) for s in array.shape]):
            slices = tuple(slice(o, min(o + 128, s)) for o, s in zip(origin, array.shape))
            output[slices], record = self.roundtrip(array[slices], kind=kind, q=q, smooth=smooth)
            records.append({"origin": list(origin), **record})
        delta = array.astype(np.float32) - output.astype(np.float32)
        mse = float(np.mean(delta * delta))
        return output, {
            "chunks": len(records),
            "codec_stream_bytes": sum(r["encoded_bytes"] for r in records),
            "valid_bytes": array.nbytes,
            "padded_bytes": sum(r["padded_bytes"] for r in records),
            "encode_seconds": sum(r["encode_seconds"] for r in records),
            "decode_seconds": sum(r["decode_seconds"] for r in records),
            "mae": float(np.abs(delta).mean()),
            "psnr": float(10 * np.log10(255**2 / mse)) if mse else None,
            "chunk_records": records,
        }

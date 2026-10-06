from __future__ import annotations

import hashlib
import itertools
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import requests
import zarr
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .provenance import file_hash


class Fetcher:
    def __init__(self, cache: Path, *, max_bytes: int = 20 << 30, receipts=None):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self.bytes_received = 0
        self.records = {}
        self.expected = {r["url"]: r["sha256"] for r in (receipts or [])}
        self.session = requests.Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=3,
                    backoff_factor=0.5,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["GET"],
                )
            ),
        )

    def get(self, url: str, *, expected_sha256: str | None = None) -> Path:
        if urlparse(url).scheme != "https":
            raise ValueError("Remote acquisition requires an HTTPS URL")
        key = hashlib.sha256(url.encode()).hexdigest()
        path = self.cache / key
        if not path.exists():
            temporary = self.cache / (key + ".partial")
            try:
                with self.session.get(url, stream=True, timeout=(15, 90)) as response:
                    response.raise_for_status()
                    with temporary.open("wb") as stream:
                        for chunk in response.iter_content(1 << 20):
                            self.bytes_received += len(chunk)
                            if self.bytes_received > self.max_bytes:
                                raise RuntimeError("Acquisition byte budget exceeded")
                            stream.write(chunk)
                    expected_size = response.headers.get("Content-Length")
                    if expected_size and int(expected_size) != temporary.stat().st_size:
                        raise OSError(f"Truncated HTTP response for {url}")
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
        digest = file_hash(path)
        expected_sha256 = expected_sha256 or self.expected.get(url)
        if expected_sha256 and digest != expected_sha256:
            raise ValueError(f"SHA-256 mismatch for {url}")
        self.records[url] = {"url": url, "bytes": path.stat().st_size, "sha256": digest}
        return path

    def json(self, url: str) -> dict:
        return json.loads(self.get(url).read_text(encoding="utf-8"))


class RemoteV2Array:
    """A bounded reader of original v2 chunks, retaining their global coordinates."""

    def __init__(self, url: str, fetcher: Fetcher):
        self.url = url.rstrip("/")
        self.fetcher = fetcher
        self.metadata = fetcher.json(self.url + "/.zarray")
        self.shape = tuple(self.metadata["shape"])
        self.chunks = tuple(self.metadata["chunks"])
        self.dtype = np.dtype(self.metadata["dtype"])
        if self.dtype.hasobject or self.dtype.kind not in "uif":
            raise ValueError("Expected a numeric CT dtype without Python objects")
        if any(c <= 0 for c in self.chunks) or np.prod(self.chunks) * self.dtype.itemsize > 1 << 30:
            raise ValueError("Invalid or unbounded chunk shape")
        if len(self.shape) != 3 or self.metadata.get("filters"):
            raise ValueError("Raw-volume reader requires a 3D v2 array without filters")
        if self.metadata.get("order", "C") != "C":
            raise ValueError("Raw-volume reader requires C-order chunks")
        self.separator = self.metadata.get("dimension_separator", ".")
        if self.separator not in (".", "/"):
            raise ValueError("Invalid chunk dimension separator")

    def chunk(self, key: tuple[int, int, int]) -> np.ndarray:
        import numcodecs

        if any(k < 0 or k * c >= s for k, c, s in zip(key, self.chunks, self.shape)):
            raise ValueError(f"Chunk outside volume: {key}")
        url = self.url + "/" + self.separator.join(map(str, key))
        encoded = self.fetcher.get(url).read_bytes()
        config = self.metadata.get("compressor")
        decoded = numcodecs.get_codec(config).decode(encoded) if config else encoded
        expected = int(np.prod(self.chunks)) * self.dtype.itemsize
        if len(decoded) != expected:
            raise ValueError(f"Chunk {key} has {len(decoded)} bytes, expected {expected}")
        return np.frombuffer(decoded, self.dtype).reshape(self.chunks).copy()

    def read(self, start: tuple[int, int, int], shape: tuple[int, int, int]) -> np.ndarray:
        if len(start) != 3 or len(shape) != 3 or any(s <= 0 for s in shape):
            raise ValueError("ROI must have three positive dimensions")
        end = tuple(a + b for a, b in zip(start, shape))
        if any(a < 0 or b > s for a, b, s in zip(start, end, self.shape)):
            raise ValueError("ROI outside volume")
        output = np.empty(shape, self.dtype)
        ranges = [range(a // c, (b - 1) // c + 1) for a, b, c in zip(start, end, self.chunks)]
        for key in itertools.product(*ranges):
            chunk = self.chunk(key)
            origin = tuple(k * c for k, c in zip(key, self.chunks))
            lo = tuple(max(a, o) for a, o in zip(start, origin))
            hi = tuple(min(b, o + c) for b, o, c in zip(end, origin, self.chunks))
            output[tuple(slice(a - s, b - s) for a, b, s in zip(lo, hi, start))] = chunk[
                tuple(slice(a - o, b - o) for a, b, o in zip(lo, hi, origin))
            ]
        return output


def open_array(
    path: str | Path,
    *,
    level: str | None = None,
    storage_options: dict | None = None,
    zarr_format: int | None = None,
) -> zarr.Array:
    if str(path).startswith("https://"):
        store = zarr.storage.FsspecStore.from_url(
            str(path), read_only=True, storage_options=storage_options or {}
        )
        node = zarr.open(store, mode="r", zarr_format=zarr_format)
    else:
        if storage_options is not None:
            raise ValueError("Storage options apply only to remote HTTPS arrays")
        node = zarr.open(str(path), mode="r", zarr_format=zarr_format)
    if isinstance(node, zarr.Group):
        if level is None:
            raise ValueError("A Zarr group requires an explicit pyramid level")
        node = node[level]
    if not isinstance(node, zarr.Array):
        raise TypeError("Input does not resolve to a Zarr array")
    return node


def mirror_label_array(url: str, fetcher: Fetcher) -> zarr.Array:
    # Released labels use one small compressed v3 shard. Downloading that shard
    # avoids relying on a remote reader's treatment of missing objects as zeros.
    metadata = fetcher.json(url.rstrip("/") + "/zarr.json")
    if metadata.get("node_type") != "array":
        raise ValueError("Expected the explicit label-array level")
    shape = metadata["shape"]
    grid = metadata["chunk_grid"]["configuration"]["chunk_shape"]
    local = fetcher.cache / (hashlib.sha256(url.encode()).hexdigest() + ".zarr")
    local.mkdir(exist_ok=True)
    (local / "zarr.json").write_text(json.dumps(metadata), encoding="utf-8")
    encoding = metadata.get("chunk_key_encoding", {})
    if encoding.get("name") != "default":
        raise ValueError("Label mirror requires the default v3 chunk key encoding")
    separator = encoding.get("configuration", {}).get("separator", "/")
    if separator not in (".", "/"):
        raise ValueError("Invalid label chunk separator")
    for key in itertools.product(*[range((s + c - 1) // c) for s, c in zip(shape, grid)]):
        suffix = "c" + separator + separator.join(map(str, key))
        source = fetcher.get(url.rstrip("/") + "/" + suffix)
        target = local / suffix
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(source.read_bytes())
    return zarr.open(str(local), mode="r")


def acquire_mesh(url: str, destination: Path, fetcher: Fetcher) -> Path:
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("x.tif", "y.tif", "z.tif", "meta.json", "mask.tif"):
        try:
            source = fetcher.get(url.rstrip("/") + "/" + name)
        except requests.HTTPError as exc:
            if name == "mask.tif" and exc.response.status_code == 404:
                continue
            raise
        target = destination / name
        if target.exists() and file_hash(target) != file_hash(source):
            raise ValueError("Local mesh differs from the recorded public source")
        if not target.exists():
            temporary = destination / (name + ".partial")
            temporary.write_bytes(source.read_bytes())
            os.replace(temporary, target)
    return destination

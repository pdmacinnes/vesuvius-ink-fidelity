from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np


def file_hash(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def array_hash(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256(str((contiguous.shape, contiguous.dtype.str)).encode())
    digest.update(memoryview(contiguous).cast("B"))
    return digest.hexdigest()


def canonical_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path: str | Path, value: dict | list, *, compact_rows=False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as stream:
        if compact_rows and isinstance(value, list):
            stream.write(
                "[\n"
                + ",\n".join(
                    json.dumps(row, sort_keys=True, allow_nan=False, separators=(",", ":"))
                    for row in value
                )
                + "\n]"
            )
        else:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

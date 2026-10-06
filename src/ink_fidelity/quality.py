from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from skimage.metrics import structural_similarity

from .acquisition import open_array
from .provenance import write_json


def model_input_quality(results_path: Path, artifact_root: Path, out: Path):
    rows = json.loads(results_path.read_text(encoding="utf-8"))
    records = []
    raw_by_window = {}
    seen = set()
    for row in rows:
        key = row["window"], row["arm"]
        if key in seen:
            continue
        seen.add(key)
        window, arm = key
        if window not in raw_by_window:
            raw_by_window[window] = np.asarray(
                open_array(artifact_root / window / "raw/input.zarr")[:]
            )
        raw = raw_by_window[window]
        candidate = np.asarray(open_array(artifact_root / window / arm / "input.zarr")[:])
        start = raw.shape[0] // 2 - 17 // 2
        a, b = raw[start : start + 17], candidate[start : start + 17]
        mse = float(np.mean((a.astype(np.float32) - b.astype(np.float32)) ** 2))
        records.append(
            {
                "window": window,
                "arm": arm,
                "comparison": "Same final 17-plane model input, including inference halo",
                "ssim_mean": float(
                    np.mean([structural_similarity(x, y, data_range=255) for x, y in zip(a, b)])
                ),
                "psnr": float(10 * np.log10(255**2 / mse)) if mse else None,
                "mae": float(np.abs(a.astype(np.float32) - b.astype(np.float32)).mean()),
            }
        )
    write_json(out, records)
    return records

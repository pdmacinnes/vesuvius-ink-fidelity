from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .acquisition import Fetcher, RemoteV2Array, mirror_label_array
from .provenance import write_json

ROOT = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/"
TARGETS = [
    ("PHerc0139", "20250831000000-w040_2025083102", "9.362um", 0, "forward"),
    ("PHerc0139", "20260115000000-w044_2026011522", "9.362um", 0, "forward"),
    ("PHercParis4", "20231016151002", "2.4um", 2, "forward"),
    ("PHercParis4", "20230702185753", "2.4um", 2, "forward"),
    ("PHerc0841", "20260220213127-w00", "2.403um", 2, "reverse"),
    ("PHerc0841", "20260220214732-auto_grown_20260220144552896", "2.403um", 2, "reverse"),
]


def select_windows(labels, supervision, *, size=256, halo=128, count=2):
    candidates = []
    for y in range(halo, labels.shape[0] - size - halo + 1, 128):
        for x in range(halo, labels.shape[1] - size - halo + 1, 128):
            sup = supervision[y : y + size, x : x + size] >= 128
            ink = labels[y : y + size, x : x + size] >= 128
            positives, negatives = int((ink & sup).sum()), int((~ink & sup).sum())
            if positives >= 100 and negatives >= 100 and sup.sum() >= 2000:
                candidates.append((-int(sup.sum()), y, x, positives, negatives))
    chosen = []
    for neg_coverage, y, x, positives, negatives in sorted(candidates):
        if all(
            abs(y - c["y"]) >= size + 2 * halo or abs(x - c["x"]) >= size + 2 * halo for c in chosen
        ):
            chosen.append(
                {
                    "y": y,
                    "x": x,
                    "size": size,
                    "supervised": -neg_coverage,
                    "positives": positives,
                    "negatives": negatives,
                }
            )
        if len(chosen) == count:
            return chosen
    raise ValueError(f"Only {len(chosen)} separated supervised windows available")


def freeze_manifest(catalog_path: Path, destination: Path):
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    fetcher = Fetcher(Path(".cache/http"))
    records = []
    for sample, segment_id, pitch, level, direction in TARGETS:
        segments = list(catalog["samples"][sample]["segments"].values())
        segment = next(s for s in segments if s["long_id"] == segment_id)
        surface = next(
            d
            for d in segment["data"]
            if d["type"] == "layers-zarr" and f"/{pitch}-" in d["origins"][0]["path"]
        )
        label = next(
            d
            for d in segment["data"]
            if d["type"] == "ink-labels" and f"/{pitch}-" in d["origins"][0]["path"]
        )
        surface_url = ROOT + surface["origins"][0]["path"].rstrip("/") + f"/{level}"
        label_url = ROOT + label["origins"][0]["path"].rstrip("/")
        reader = RemoteV2Array(surface_url, fetcher)
        labels = np.asarray(mirror_label_array(label_url + f"/inklabels.zarr/{level}", fetcher)[:])
        supervision = np.asarray(
            mirror_label_array(label_url + f"/supervision.zarr/{level}", fetcher)[:]
        )
        if labels.shape != supervision.shape or labels.shape != reader.shape[1:]:
            raise ValueError(
                f"Canvas mismatch on {sample}/{segment_id}: {labels.shape}, {reader.shape}"
            )
        if level and reader.shape[0] < 84:
            raise ValueError("Cannot apply the official 84-plane pooling convention")
        windows = select_windows(labels, supervision)
        for i, window in enumerate(windows):
            window["id"] = f"{sample}-{segment_id}-{i}"
        physical_segment = sample + "/" + segment_id
        record = {
            "physical_segment": physical_segment,
            "sample_id": sample,
            "segment_id": segment_id,
            "surface_url": surface_url,
            "label_url": label_url,
            "label_level": level,
            "surface_shape": reader.shape,
            "direction": direction,
            "depth_pool": 4 if level else 1,
            "halo": 128,
            "windows": windows,
            "training_exposure": "unseen scroll"
            if sample == "PHerc0841"
            else "training scroll; physical segment may have been exposed",
            "label_interpretation": "Released binary/pyramid label and supervision >=128; not independent IR truth",
        }
        records.append(record)
        print(sample, segment_id, reader.shape, windows, flush=True)
    manifest = {
        "role": "frozen-test",
        "records": records,
        "threshold": 0.5,
        "seeds": [42, 43],
        "candidate_quality": 2,
        "diagnostic_quality": 8,
        "selection": "Two separated windows per fixed segment, ranked by supervision only; no model scores inspected",
        "acquisition": list(fetcher.records.values()),
    }
    write_json(destination, manifest)
    return manifest

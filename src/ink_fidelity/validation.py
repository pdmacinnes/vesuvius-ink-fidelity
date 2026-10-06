from __future__ import annotations

import re


def validate_test_manifest(manifest: dict):
    if manifest.get("role") != "frozen-test":
        raise ValueError("Benchmark requires a frozen test manifest")
    if not 0 <= manifest.get("threshold", -1) <= 1:
        raise ValueError("Threshold must be in [0,1]")
    seen = set()
    physical_ids = set()
    for segment in manifest["records"]:
        physical = f"{segment['sample_id']}/{segment['segment_id']}"
        if segment["physical_segment"] != physical or physical in physical_ids:
            raise ValueError("Physical segment identity is inconsistent or duplicated")
        physical_ids.add(physical)
        prefix = f"/{segment['sample_id']}/segments/{segment['segment_id']}/"
        if prefix not in segment["surface_url"] or prefix not in segment["label_url"]:
            raise ValueError("Declared sample/segment does not match input URLs")
        source_frame = re.search(r"volume-(\d+)", segment["surface_url"])
        label_frame = re.search(r"volume-(\d+)", segment["label_url"])
        if not source_frame or not label_frame or source_frame.group(1) != label_frame.group(1):
            raise ValueError("Label and surface volume frames disagree or are undeclared")
        if segment["depth_pool"] not in (1, 4):
            raise ValueError("Unsupported depth pooling convention")
        halo = segment["halo"]
        if halo < 128 or halo % 128:
            raise ValueError("Halo must preserve 128-pixel codec and 64-pixel inference grids")
        height, width = segment["surface_shape"][1:]
        previous = []
        for window in segment["windows"]:
            if window["id"] in (".", "..") or not re.fullmatch(
                r"[A-Za-z0-9_.-]{1,240}", window["id"]
            ):
                raise ValueError("Window identity must be a safe filename component")
            if window["id"] in seen:
                raise ValueError("Duplicate window identity")
            seen.add(window["id"])
            y, x, size = window["y"], window["x"], window["size"]
            if size <= 0 or (y - halo) % 128 or (x - halo) % 128:
                raise ValueError("ROI is not aligned to the original codec chunk grid")
            if y - halo < 0 or x - halo < 0 or y + size + halo > height or x + size + halo > width:
                raise ValueError("ROI or halo outside the declared surface")
            for old_y, old_x, old_size in previous:
                if (
                    y < old_y + old_size
                    and old_y < y + size
                    and x < old_x + old_size
                    and old_x < x + size
                ):
                    raise ValueError("Scored windows overlap within a physical segment")
            previous.append((y, x, size))


def verified_resume(record, *, run_id, probability_path, hash_file):
    return (
        record.get("run_id") == run_id
        and probability_path.exists()
        and record.get("probability_sha256") == hash_file(probability_path)
    )

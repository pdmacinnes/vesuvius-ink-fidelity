from __future__ import annotations

import itertools
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import map_coordinates

from .acquisition import RemoteV2Array
from .upstream import VILLA_SHA, add_source


def render_surface(
    reader: RemoteV2Array,
    mesh: Path,
    *,
    villa: Path,
    canvas_shape: tuple[int, int],
    bounds: tuple[int, int, int, int],
    offsets: list[float],
    kind="raw",
    q=8,
    codec=None,
    sample_step=1,
    flip_normals=True,
):
    add_source(villa, "vesuvius/src", VILLA_SHA)
    from vesuvius.tifxyz_label_transfer.io import load_surface
    from vesuvius.tifxyz_label_transfer.self_render_tifxyz import (
        surface_geometry_at_uv,
        surface_tile_geometry,
    )

    surface = load_surface(mesh)
    xyz, normals, valid = surface_tile_geometry(surface, canvas_shape, bounds)
    # VC3D's linear renderer interpolates positions but uses the nearest stored
    # vertex normal. Continuous normals change deep layers on curved surfaces.
    ys = (np.arange(bounds[0], bounds[1]) + 0.5) * surface.shape[0] / canvas_shape[0]
    xs = (np.arange(bounds[2], bounds[3]) + 0.5) * surface.shape[1] / canvas_shape[1]
    gy, gx = np.meshgrid(np.floor(ys + 0.5), np.floor(xs + 0.5), indexing="ij")
    _, normals, normal_valid = surface_geometry_at_uv(surface, gy, gx, np.ones(gy.shape, bool))
    valid &= normal_valid
    if not valid.all():
        raise ValueError("Render ROI contains invalid geometry; choose a valid pilot/control")
    if flip_normals:
        normals = -normals
    xyz, normals = xyz[::sample_step, ::sample_step], normals[::sample_step, ::sample_step]
    points = xyz[None] + np.asarray(offsets)[:, None, None, None] * normals[None]
    points = points[..., ::-1]
    low = np.floor(points.reshape(-1, 3).min(axis=0)).astype(int)
    high = np.ceil(points.reshape(-1, 3).max(axis=0)).astype(int) + 1
    if (low < 0).any() or (high > reader.shape).any():
        raise ValueError("Sampling band extends outside CT")
    block_shape = tuple(high - low + 1)
    if reader.dtype != np.uint8:
        raise ValueError("This ink_9um benchmark requires the declared uint8 input")
    block = np.zeros(block_shape, np.uint8)
    records = []
    start = time.perf_counter()
    ranges = [range(a // c, b // c + 1) for a, b, c in zip(low, high, reader.chunks)]
    for key in itertools.product(*ranges):
        chunk = reader.chunk(key)
        if kind != "raw":
            if codec is None:
                raise ValueError("Compressed render requires a codec")
            chunk, record = codec.roundtrip(chunk, kind=kind, q=q)
        else:
            record = {
                "encoded_bytes": chunk.nbytes,
                "valid_bytes": chunk.nbytes,
                "encode_seconds": 0.0,
                "decode_seconds": 0.0,
            }
        origin = np.asarray(key) * reader.chunks
        lo, hi = np.maximum(low, origin), np.minimum(high + 1, origin + reader.chunks)
        block[tuple(slice(a - lower, b - lower) for a, b, lower in zip(lo, hi, low))] = chunk[
            tuple(slice(a - o, b - o) for a, b, o in zip(lo, hi, origin))
        ]
        records.append({"key": list(key), **record})
    sampled = map_coordinates(
        block.astype(np.float32),
        np.moveaxis(points - low, -1, 0).reshape(3, -1),
        order=1,
        mode="nearest",
        prefilter=False,
    ).reshape(points.shape[:-1])
    return sampled, {
        "render_seconds": time.perf_counter() - start,
        "chunk_records": records,
        "bounds": list(bounds),
        "canvas_shape": list(canvas_shape),
        "offsets": offsets,
        "flip_normals": flip_normals,
        "voxel_bounds_zyx": [low.tolist(), high.tolist()],
        "stream_bytes": sum(r["encoded_bytes"] for r in records),
    }

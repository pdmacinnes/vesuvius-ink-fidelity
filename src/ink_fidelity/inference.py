from __future__ import annotations

import os
import time
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np

from .provenance import file_hash
from .upstream import VILLA_SHA, add_source


class InkModel:
    def __init__(self, villa: Path, checkpoint: Path, *, expected_hash: str | None = None):
        add_source(villa, "vesuvius/src", VILLA_SHA)
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        import torch
        from vesuvius.ink_detection.inference import infer

        self.checkpoint_hash = file_hash(checkpoint)
        if expected_hash and self.checkpoint_hash != expected_hash:
            raise ValueError("Checkpoint checksum mismatch")
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable; real benchmark requires the declared GPU")
        args = infer.parse_args(
            [
                "input.zarr",
                str(checkpoint),
                "output.tif",
                "--num-workers",
                "0",
                "--no-compile",
                "--amp-dtype",
                "default",
                "--stride",
                "64",
            ]
        )
        old_loader, old_state = infer.load_checkpoint, infer.load_flat_inference_state

        def strict_state(model, state):
            result = old_state(model, state)
            if result.missing_keys or result.unexpected_keys:
                raise ValueError(f"Checkpoint/model mismatch: {result}")
            return result

        try:
            infer.load_checkpoint = lambda p: torch.load(p, map_location="cpu", weights_only=True)
            infer.load_flat_inference_state = strict_state
            configured = infer.configure_model(args)
        finally:
            infer.load_checkpoint, infer.load_flat_inference_state = old_loader, old_state
        self.torch, self.infer, self.args = torch, infer, args
        self.device = torch.device("cuda:0")
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True)
        # In this pin, dtype=None still enters CUDA autocast. Explicit float32
        # makes PyTorch disable autocast without changing the upstream model.
        self.configured = replace(
            configured, model=configured.model.to(self.device), amp_dtype=torch.float32
        )

    def predict(
        self, input_zarr: Path, output: Path, *, direction: str, layer_start=None, layer_end=None
    ) -> tuple[np.ndarray, dict]:
        torch, infer = self.torch, self.infer
        captured = {}
        observed_dtypes = set()
        first_conv = next(
            m for m in self.configured.model.modules() if isinstance(m, torch.nn.Conv3d)
        )
        hook = first_conv.register_forward_hook(
            lambda _m, _args, result: observed_dtypes.add(result.dtype)
        )
        original_writer = infer.write_output_tiff

        def capture(probability, weights, path, tile_shape):
            sums, w = np.asarray(probability[:]), np.asarray(weights[:])
            result = np.zeros_like(sums)
            np.divide(sums, w, out=result, where=w > 1e-6)
            if not np.isfinite(result).all():
                raise ValueError("Non-finite upstream output")
            captured["probability"] = np.clip(result, 0, 1)
            original_writer(probability, weights, path, tile_shape)

        args = replace_args(self.args, layer_start=layer_start, layer_end=layer_end)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        start = time.perf_counter()
        try:
            infer.write_output_tiff = capture
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="In CUDA autocast, but the target dtype")
                infer.infer_single_zarr(
                    args=args,
                    input_zarr=str(input_zarr),
                    configured_model=self.configured,
                    device=self.device,
                    output_tiff=output,
                    layer_direction=direction,
                )
        finally:
            infer.write_output_tiff = original_writer
            hook.remove()
        torch.cuda.synchronize()
        if observed_dtypes != {torch.float32}:
            raise ValueError(f"Precision control failed: convolution dtypes {observed_dtypes}")
        return captured["probability"], {
            "inference_seconds": time.perf_counter() - start,
            "peak_vram_bytes": torch.cuda.max_memory_allocated(),
            "checkpoint_sha256": self.checkpoint_hash,
            "torch": torch.__version__,
            "device": torch.cuda.get_device_name(0),
            "precision": "float32, TF32 disabled",
            "convolution_dtype_verified": "float32",
            "upstream_sha": VILLA_SHA,
            "stride": 64,
            "blend": "hann",
            "direction": direction,
            "layers": [layer_start, layer_end],
        }


def replace_args(args, **kwargs):
    from argparse import Namespace

    return Namespace(**{**vars(args), **kwargs})

from types import SimpleNamespace

import numpy as np
import pytest

from ink_fidelity.normalization_study import reference_calibrated, source_normalization


def test_identical_raw_control_retains_exact_official_tensor():
    raw = np.arange(128, dtype=np.float32).reshape(2, 8, 8)
    low, high = np.percentile(raw, [1, 99])
    normalized = (np.clip(raw, low, high).astype(np.float32) - 64) / 10
    result, _ = reference_calibrated(raw, raw, normalized)
    assert np.array_equal(result, normalized)


def test_decoded_delta_uses_reference_transform_and_clipping():
    raw = np.arange(128, dtype=np.float32).reshape(2, 8, 8)
    low, high = np.percentile(raw, [1, 99])
    normalized = (np.clip(raw, low, high).astype(np.float32) - 64) / 10
    decoded = raw + 3
    result, _ = reference_calibrated(raw, decoded, normalized)
    expected = (np.clip(decoded, low, high).astype(np.float32) - 64) / 10
    assert np.allclose(result, expected, atol=1e-6)


def test_constant_raw_reference_has_explicit_clipping_rule():
    raw = np.full((2, 8, 8), 42, np.float32)
    result, params = reference_calibrated(raw, raw + 100, np.zeros_like(raw))
    assert params["constant"]
    assert not result.any()


def test_mismatched_or_unrecoverable_reference_fails():
    with pytest.raises(ValueError, match="matched patch"):
        reference_calibrated(np.ones(3), np.ones(2), np.ones(3))
    with pytest.raises(ValueError, match="affine scale"):
        reference_calibrated(np.arange(10), np.arange(10), np.zeros(10))


def test_dataset_wrapper_restored_after_inference_failure():
    original = type("OriginalDataset", (), {})
    model = SimpleNamespace(infer=SimpleNamespace(FlatBlockDataset=original))
    with pytest.raises(RuntimeError, match="inference failed"):
        with source_normalization(model, "unused.zarr", []):
            assert model.infer.FlatBlockDataset is not original
            raise RuntimeError("inference failed")
    assert model.infer.FlatBlockDataset is original

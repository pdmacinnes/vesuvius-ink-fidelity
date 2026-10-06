from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def codec():
    from ink_fidelity.compression import Codec

    if not Path(".tools/volcomp.dll").exists():
        pytest.skip("Build the pinned native codec")
    return Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))


def test_continuation_preserves_real_voxels_and_only_fills_boundary_block(codec):
    chunk = np.random.default_rng(2).integers(0, 256, (21, 128, 128), dtype=np.uint8)
    for policy in ("zero", "edge", "reflect"):
        padded = codec.pad_chunk(chunk, policy)
        assert np.array_equal(padded[:21], chunk)
        assert not np.any(padded[32:])
    with pytest.raises(ValueError, match="padding policy"):
        codec.pad_chunk(chunk, "unknown")


@pytest.mark.parametrize("policy", ["zero", "edge", "reflect"])
def test_exact_controls_for_each_padding_policy(codec, policy):
    chunk = np.random.default_rng(42).integers(0, 256, (21, 128, 128), dtype=np.uint8)
    for kind in ("zstd", "volcomp"):
        restored, _ = codec.roundtrip(chunk, kind=kind, q=0, padding=policy)
        assert np.array_equal(restored, chunk)


def test_padding_does_not_change_complete_dct_blocks(codec):
    chunk = np.random.default_rng(9).integers(0, 256, (21, 128, 128), dtype=np.uint8)
    zero, _ = codec.roundtrip(chunk, kind="volcomp", q=8)
    for policy in ("edge", "reflect"):
        result, _ = codec.roundtrip(chunk, kind="volcomp", q=8, padding=policy)
        assert np.array_equal(result[:16], zero[:16])
    full_block = chunk[:16]
    assert np.array_equal(codec.pad_chunk(full_block, "zero"), codec.pad_chunk(full_block, "edge"))

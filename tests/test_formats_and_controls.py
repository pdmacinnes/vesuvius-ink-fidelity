import json
from pathlib import Path

import numpy as np
import pytest
import zarr

from ink_fidelity.acquisition import RemoteV2Array, open_array
from ink_fidelity.provenance import array_hash, write_json


@pytest.mark.parametrize("version", [2, 3])
def test_array_and_multiscale_group_require_level(tmp_path, version):
    root = zarr.open_group(str(tmp_path / "data.zarr"), mode="w", zarr_format=version)
    data = np.arange(60, dtype=np.uint8).reshape(3, 4, 5)
    array = root.create_array("0", shape=data.shape, dtype=data.dtype)
    array[:] = data
    with pytest.raises(ValueError, match="explicit pyramid"):
        open_array(tmp_path / "data.zarr")
    assert np.array_equal(open_array(tmp_path / "data.zarr", level="0")[:], data)
    assert np.array_equal(open_array(tmp_path / "data.zarr" / "0")[:], data)


class FakeFetcher:
    def __init__(self, tmp_path):
        self.path = tmp_path / "chunk"
        self.path.write_bytes(bytes(range(64)))

    def json(self, _):
        return {
            "shape": [4, 4, 4],
            "chunks": [4, 4, 4],
            "dtype": "|u1",
            "compressor": None,
            "filters": None,
            "dimension_separator": "/",
        }

    def get(self, _):
        return self.path


def test_original_chunk_bounds_and_truncated_bytes(tmp_path):
    fetcher = FakeFetcher(tmp_path)
    reader = RemoteV2Array("https://example.test/0", fetcher)
    assert reader.read((1, 1, 1), (2, 2, 2)).shape == (2, 2, 2)
    with pytest.raises(ValueError, match="outside"):
        reader.read((3, 3, 3), (2, 2, 2))
    fetcher.path.write_bytes(b"wrong-size")
    with pytest.raises(ValueError, match="expected"):
        reader.chunk((0, 0, 0))


def test_array_hash_includes_shape_and_dtype():
    a = np.arange(8, dtype=np.uint8)
    assert array_hash(a) != array_hash(a.reshape(2, 4))
    assert array_hash(a) != array_hash(a.astype(np.int8))


def test_atomic_result_rejects_nonfinite_and_never_overwrites_good_output(tmp_path):
    path = tmp_path / "result.json"
    write_json(path, {"complete": True})
    with pytest.raises(ValueError):
        write_json(path, {"score": float("nan")})
    assert json.loads(path.read_text())["complete"]


def test_native_lossless_codec_and_partial_depth_padding():
    from ink_fidelity.compression import Codec

    if not Path(".tools/volcomp.dll").exists():
        pytest.skip("Build the pinned codec to run native codec controls")
    codec = Codec(Path("external/volume-compressor"), Path(".tools/volcomp.dll"))
    chunk = np.random.default_rng(42).integers(0, 256, (17, 128, 128), dtype=np.uint8)
    for kind in ("zstd", "volcomp"):
        restored, record = codec.roundtrip(chunk, kind=kind, q=0)
        assert np.array_equal(restored, chunk)
        assert record["padded_bytes"] == 128**3
        assert record["valid_bytes"] == chunk.nbytes
    with pytest.raises(ValueError, match="uint8"):
        codec.roundtrip(chunk.astype(np.uint16), kind="volcomp", q=8)

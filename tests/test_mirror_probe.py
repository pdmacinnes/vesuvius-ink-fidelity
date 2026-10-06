import asyncio
from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest
import zarr

from ink_fidelity.acquisition import open_array
from ink_fidelity.cli import parse_args
from ink_fidelity.mirror_probe import HttpBudget, mirror_metadata_contract


@pytest.mark.parametrize(
    ("requested", "returned", "length"),
    [("bytes=10-19", "bytes 10-19/100", "10"), ("bytes=-20", "bytes 80-99/100", "20")],
)
def test_partial_response_contract_accepts_exact_ranges(requested, returned, length):
    budget = HttpBudget()
    budget.observe(
        status=206,
        headers={"Content-Length": length, "Content-Range": returned},
        requested_range=requested,
    )
    assert budget.announced_bytes == int(length)


def test_server_ignoring_range_is_rejected_before_reserving_body():
    budget = HttpBudget()
    with pytest.raises(ValueError, match="ignored"):
        budget.observe(status=200, headers={"Content-Length": "100"}, requested_range="bytes=0-9")
    assert budget.announced_bytes == 0


@pytest.mark.parametrize(
    "headers",
    [
        {"Content-Length": "10", "Content-Range": "bytes 20-29/100"},
        {"Content-Length": "9", "Content-Range": "bytes 10-19/100"},
        {"Content-Length": "10", "Content-Range": "bytes 10-19/100", "Content-Encoding": "gzip"},
        {"Content-Length": "10", "Content-Range": "bytes 10-19/*"},
    ],
)
def test_misdirected_truncated_encoded_or_unbounded_range_is_rejected(headers):
    with pytest.raises(ValueError, match="range"):
        HttpBudget().observe(status=206, headers=headers, requested_range="bytes=10-19")


def test_unknown_length_and_excess_budget_fail_without_reserving():
    budget = HttpBudget(max_bytes=15)
    with pytest.raises(ValueError, match="length"):
        budget.observe(status=200, headers={})
    budget.observe(status=200, headers={"Content-Length": "10"})
    with pytest.raises(ValueError, match="budget"):
        budget.observe(status=200, headers={"Content-Length": "10"})
    assert budget.announced_bytes == 10
    budget.observe(status=200, headers={"Content-Length": "1000000000"}, method="HEAD")
    assert budget.announced_bytes == 10


def test_standard_http_trace_propagates_guard_failure():
    pytest.importorskip("aiohttp")
    budget = HttpBudget()
    trace = budget.trace()
    trace.freeze()
    params = SimpleNamespace(
        response=SimpleNamespace(
            status=200,
            headers={"Content-Length": "100"},
            request_info=SimpleNamespace(headers={"Range": "bytes=0-9"}),
            method="GET",
        )
    )
    with pytest.raises(ValueError, match="ignored"):
        asyncio.run(trace.on_request_end.send(None, None, params))


def test_known_source_metadata_contract_rejects_frame_or_codec_changes():
    original = SimpleNamespace(shape=(256, 256, 256), dtype=np.dtype("uint8"), chunks=(128,) * 3)
    metadata = {
        "zarr_format": 3,
        "node_type": "array",
        "shape": [256] * 3,
        "data_type": "uint8",
        "dimension_names": ["z", "y", "x"],
        "codecs": [
            {
                "name": "sharding_indexed",
                "configuration": {
                    "chunk_shape": [128] * 3,
                    "codecs": [{"name": "volcomp", "configuration": {"q": 8.0}}],
                },
            }
        ],
    }
    mirror_metadata_contract(metadata, original)
    normalized = deepcopy(metadata)
    normalized["dimension_names"] = tuple(normalized["dimension_names"])
    normalized["codecs"] = tuple(normalized["codecs"])
    normalized["codecs"][0]["configuration"]["chunk_shape"] = (128,) * 3
    normalized["codecs"][0]["configuration"]["codecs"] = tuple(
        normalized["codecs"][0]["configuration"]["codecs"]
    )
    mirror_metadata_contract(normalized, original)
    bad = deepcopy(metadata)
    bad["dimension_names"] = ["x", "y", "z"]
    with pytest.raises(ValueError, match="frame"):
        mirror_metadata_contract(bad, original)
    bad = deepcopy(metadata)
    bad["codecs"][0]["configuration"]["codecs"][0]["configuration"]["q"] = 2
    with pytest.raises(ValueError, match="codec/chunk"):
        mirror_metadata_contract(bad, original)


def test_explicit_remote_format_and_transport_options_reach_standard_reader(tmp_path, monkeypatch):
    local = zarr.create_array(str(tmp_path / "array"), shape=(2, 2), dtype="uint8", zarr_format=3)
    captured = {}

    def store(url, *, read_only, storage_options):
        captured.update(url=url, read_only=read_only, options=storage_options)
        return local.store

    monkeypatch.setattr(zarr.storage.FsspecStore, "from_url", store)
    array = open_array(
        "https://example.test/array", zarr_format=3, storage_options={"block_size": 0}
    )
    assert array.shape == (2, 2)
    assert captured == {
        "url": "https://example.test/array",
        "read_only": True,
        "options": {"block_size": 0},
    }
    with pytest.raises(ValueError, match="only to remote"):
        open_array(tmp_path / "array", storage_options={})


def test_public_mirror_defaults_require_only_shipped_references():
    args = parse_args(["mirror-probe"])
    assert args.manifest.exists() and args.reference.exists() and args.receipts.exists()
    assert args.receipts.parts[0] == "reports"

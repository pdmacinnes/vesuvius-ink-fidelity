import hashlib
import shutil

import numpy as np
import pytest
import zarr

from ink_fidelity.acquisition import Fetcher, mirror_label_array
from ink_fidelity.provenance import file_hash


@pytest.fixture
def label_cache(tmp_path):
    source = tmp_path / "source"
    values = np.arange(64, dtype=np.uint8).reshape(8, 8)
    array = zarr.create_array(
        str(source),
        shape=values.shape,
        chunks=values.shape,
        dtype="uint8",
        zarr_format=3,
        compressors=None,
    )
    array[:] = values
    cache = tmp_path / "cache"
    cache.mkdir()
    url = "https://example.test/labels/0"
    receipts = []
    for path in source.rglob("*"):
        if path.is_file():
            location = url + "/" + path.relative_to(source).as_posix()
            shutil.copyfile(path, cache / hashlib.sha256(location.encode()).hexdigest())
            receipts.append({"url": location, "sha256": file_hash(path)})
    local = cache / (hashlib.sha256(url.encode()).hexdigest() + ".zarr")
    fetcher = Fetcher(cache, receipts=receipts)
    mirror_label_array(url, fetcher)
    return url, fetcher, local, values


def test_valid_but_modified_shard_is_repaired_from_checked_source(label_cache):
    url, fetcher, local, values = label_cache
    zarr.open(str(local), mode="r+")[1, 1] = 255
    assert not np.array_equal(zarr.open(str(local), mode="r")[:], values)
    assert np.array_equal(mirror_label_array(url, fetcher)[:], values)


def test_truncated_shard_and_metadata_are_repaired(label_cache):
    url, fetcher, local, values = label_cache
    (local / "c/0/0").write_bytes(b"truncated")
    (local / "zarr.json").write_text("{partial", encoding="utf-8")
    assert np.array_equal(mirror_label_array(url, fetcher)[:], values)


def test_interrupted_copy_preserves_old_target_and_retry_repairs(label_cache, monkeypatch):
    url, fetcher, local, values = label_cache
    target = local / "c/0/0"
    damaged = b"previous-target"
    target.write_bytes(damaged)
    original_copy = shutil.copyfileobj

    def interrupted(_reader, writer, **_kwargs):
        writer.write(b"partial")
        raise OSError("injected write interruption")

    monkeypatch.setattr(shutil, "copyfileobj", interrupted)
    with pytest.raises(OSError, match="interruption"):
        mirror_label_array(url, fetcher)
    assert target.read_bytes() == damaged
    assert not list(local.rglob("*.partial"))
    monkeypatch.setattr(shutil, "copyfileobj", original_copy)
    assert np.array_equal(mirror_label_array(url, fetcher)[:], values)


def test_matching_cache_is_reused_without_rewriting(label_cache):
    url, fetcher, local, _ = label_cache
    before = {p: p.stat().st_mtime_ns for p in local.rglob("*") if p.is_file()}
    mirror_label_array(url, fetcher)
    assert before == {p: p.stat().st_mtime_ns for p in local.rglob("*") if p.is_file()}


def test_corrupted_source_receipt_fails_without_touching_good_target(label_cache):
    url, fetcher, local, values = label_cache
    encoded_source = fetcher.cache / hashlib.sha256((url + "/c/0/0").encode()).hexdigest()
    encoded_source.write_bytes(b"corrupt-source")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        mirror_label_array(url, fetcher)
    assert np.array_equal(zarr.open(str(local), mode="r")[:], values)

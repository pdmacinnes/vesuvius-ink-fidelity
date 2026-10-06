import copy
import json
from pathlib import Path

import pytest

from ink_fidelity.provenance import file_hash
from ink_fidelity.validation import validate_test_manifest, verified_resume


def test_frozen_real_manifest_and_cross_frame_refusal():
    manifest = json.loads(Path("experiments/frozen-test.json").read_text())
    validate_test_manifest(manifest)
    changed = copy.deepcopy(manifest)
    changed["records"][0]["label_url"] = changed["records"][0]["label_url"].replace(
        "20250728140407", "20260102150214"
    )
    with pytest.raises(ValueError, match="frames disagree"):
        validate_test_manifest(changed)


def test_unaligned_codec_origin_and_duplicated_id_refused():
    manifest = json.loads(Path("experiments/frozen-test.json").read_text())
    manifest["records"][0]["windows"][0]["y"] += 1
    with pytest.raises(ValueError, match="aligned"):
        validate_test_manifest(manifest)
    manifest["records"][0]["windows"][0]["y"] -= 1
    manifest["records"][0]["windows"][1]["id"] = manifest["records"][0]["windows"][0]["id"]
    with pytest.raises(ValueError, match="Duplicate"):
        validate_test_manifest(manifest)


def test_partial_corrupt_or_changed_run_never_resumes(tmp_path):
    path = tmp_path / "prediction.npy"
    record = {"run_id": "a", "probability_sha256": "missing"}
    assert not verified_resume(record, run_id="a", probability_path=path, hash_file=file_hash)
    path.write_bytes(b"complete result")
    record["probability_sha256"] = file_hash(path)
    assert verified_resume(record, run_id="a", probability_path=path, hash_file=file_hash)
    assert not verified_resume(record, run_id="b", probability_path=path, hash_file=file_hash)
    path.write_bytes(b"truncated")
    assert not verified_resume(record, run_id="a", probability_path=path, hash_file=file_hash)


def test_receipt_hash_rejects_corrupt_cached_source(tmp_path):
    import hashlib

    from ink_fidelity.acquisition import Fetcher

    url = "https://example.test/asset"
    path = tmp_path / hashlib.sha256(url.encode()).hexdigest()
    path.write_bytes(b"wrong source bytes")
    fetcher = Fetcher(tmp_path, receipts=[{"url": url, "sha256": "expected"}])
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        fetcher.get(url)


def test_interrupted_http_does_not_publish_partial_asset(tmp_path):
    from ink_fidelity.acquisition import Fetcher

    class Response:
        @property
        def headers(self):
            return {}

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def raise_for_status(self):
            pass

        def iter_content(self, _):
            yield b"partial"
            raise OSError("connection lost")

    fetcher = Fetcher(tmp_path)
    fetcher.session.get = lambda *a, **k: Response()
    with pytest.raises(OSError, match="connection lost"):
        fetcher.get("https://example.test/asset")
    assert not list(tmp_path.iterdir())


def test_official_centered_depth_pool_and_rounding():
    import numpy as np

    from ink_fidelity.benchmark import depth_pool
    from ink_fidelity.upstream import VILLA_SHA, add_source

    if not Path("external/villa").exists():
        pytest.skip("Acquire pinned upstream for its preprocessing contract")
    add_source(Path("external/villa"), "vesuvius/src", VILLA_SHA)
    source = np.arange(109, dtype=np.uint8)[:, None, None]
    output = depth_pool(source, 4)
    assert output.shape == (21, 1, 1)
    assert output[0, 0, 0] == 14  # np.rint(13,14,15,16 mean) uses ties-to-even
    assert output[-1, 0, 0] == 94

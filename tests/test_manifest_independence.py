import copy
import json
from pathlib import Path

import pytest

from ink_fidelity.validation import validate_test_manifest


def test_distinct_names_cannot_hide_overlapping_scored_area():
    manifest = json.loads(Path("experiments/frozen-test.json").read_text())
    first = manifest["records"][0]["windows"][0]
    duplicate = copy.deepcopy(first)
    duplicate["id"] = "different-name-same-area"
    manifest["records"][0]["windows"].append(duplicate)
    with pytest.raises(ValueError, match="Scored windows overlap"):
        validate_test_manifest(manifest)


def test_a_segment_cannot_be_renamed_as_an_independent_group():
    manifest = json.loads(Path("experiments/frozen-test.json").read_text())
    manifest["records"][0]["physical_segment"] = "another-independent-group"
    with pytest.raises(ValueError, match="Physical segment identity"):
        validate_test_manifest(manifest)

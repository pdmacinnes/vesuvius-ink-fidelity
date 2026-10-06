from ink_fidelity.cli import parse_args


def test_reproduction_uses_files_shipped_in_public_repository():
    args = parse_args(["reproduce"])
    assert args.results.exists()
    assert args.receipts.exists()
    assert args.manifest.exists()
    assert args.results.parts[0] == "reports"
    assert args.receipts.parts[0] == "reports"


def test_explicit_local_reference_paths_remain_available(tmp_path):
    local = tmp_path / "results.json"
    args = parse_args(["reproduce", "--results", str(local)])
    assert args.results == local

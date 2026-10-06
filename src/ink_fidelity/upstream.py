from __future__ import annotations

import subprocess
import sys
from pathlib import Path

VILLA_SHA = "0e14cf48c8cee74b11e5e40a9d1d520b74e35423"
VOLCOMP_SHA = "20b03983ee741baa160d3e630da77a3b3a24ee44"


def add_source(repository: Path, relative: str, expected_sha: str) -> None:
    repository = Path(repository).resolve()
    head = subprocess.check_output(["git", "-C", str(repository), "rev-parse", "HEAD"], text=True)
    if head.strip() != expected_sha:
        raise ValueError(f"Expected upstream {expected_sha}, found {head.strip()}")
    changes = subprocess.check_output(
        ["git", "-C", str(repository), "diff", "--name-only"], text=True
    )
    if changes.strip():
        raise ValueError("Upstream source has local changes; baseline must be unmodified")
    source = str(repository / relative)
    if source not in sys.path:
        sys.path.insert(0, source)

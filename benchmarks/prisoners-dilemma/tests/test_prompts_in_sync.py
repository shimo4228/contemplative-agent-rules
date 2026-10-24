"""The packaged prompt copies must equal the repository's root ``prompts/``.

``prompts/{custom,paper-faithful}.md`` at the repository root are the published
files; ``src/ipd/prompts/`` carries the copies the installed package loads. The
two were identical by hand only. The consumer (contemplative-agent ADR-0090)
calibrates against the packaged copies, so a drift would silently change what
its null pair measured.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[1]
ROOT_PROMPTS = BENCH.parents[1] / "prompts"
PACKAGED = BENCH / "src" / "ipd" / "prompts"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("name", ["custom.md", "paper-faithful.md"])
def test_packaged_prompt_matches_root_prompt(name: str) -> None:
    assert _sha(PACKAGED / name) == _sha(ROOT_PROMPTS / name)


def test_every_packaged_prompt_has_a_root_twin() -> None:
    for packaged in PACKAGED.glob("*.md"):
        assert (ROOT_PROMPTS / packaged.name).is_file(), packaged.name

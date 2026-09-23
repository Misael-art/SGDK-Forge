from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("analyze_hdbg_probe", ROOT / "tests/analyze_hdbg_probe.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_hdbg_decoder_self_check() -> None:
    assert MODULE.self_check() == 0

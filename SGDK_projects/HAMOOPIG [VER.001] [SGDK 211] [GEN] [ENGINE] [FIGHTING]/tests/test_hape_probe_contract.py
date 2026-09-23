#!/usr/bin/env python3
"""Contract checks for the same-boundary HAPE runtime event record."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("analyze_hape_probe", ROOT / "analyze_hape_probe.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
    assert MODULE.self_check() == 0
    print("hape_probe_contract: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

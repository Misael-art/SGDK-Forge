#!/usr/bin/env python3
"""Canonical v3 entrypoint for artifact-bound animation strip validation.

The legacy filename ``validate_strip.py`` remains importable for old contracts
and local materializations. New production calls this central entrypoint so a
project-local frozen copy cannot silently weaken the gate.
"""

from __future__ import annotations

import sys

from validate_strip import main, self_check as _validate_strip_self_check


TOOL_VERSION = "1.0.0"


def self_check() -> int:
    return _validate_strip_self_check()


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        sys.exit(self_check())
    sys.exit(main())

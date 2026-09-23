#!/usr/bin/env python3
"""Run the audited native-authoring builder against the second A-route source."""
from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
builder_path = PROJECT / "tools/art/build_taina_native_authoring_face_guard_v02.py"
spec = importlib.util.spec_from_file_location("native_authoring_v02", builder_path)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

builder.OUT = PROJECT / "rascunho/taina_native_authoring_face_guard_v03"
builder.SOURCE = builder.OUT / "source/face_and_guard_topology_native_authoring_source_v03.png"
builder.ASSET_ID = "taina_48x64_native_authoring_face_guard_v03"

if __name__ == "__main__":
    raise SystemExit(builder.main())

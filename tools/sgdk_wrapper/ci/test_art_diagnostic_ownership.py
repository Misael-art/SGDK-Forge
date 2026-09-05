#!/usr/bin/env python3
"""Synthetic regression for source-art versus active-resource ownership."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


TOOL = Path(__file__).resolve().parents[1] / "art_diagnostic.py"


def indexed_png(path: Path, size: tuple[int, int] = (24, 32)) -> None:
    image = Image.new("P", size, 0)
    image.putpalette([255, 0, 255, 0, 0, 0] + [0, 0, 0] * 254)
    for y in range(4, size[1] - 2):
        for x in range(8, min(16, size[0] - 1)):
            image.putpixel((x, y), 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, transparency=0)


def rgb_source(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (127, 95), (37, 83, 149)).save(path)


def run(project: Path) -> tuple[int, dict]:
    output = project / "doc/art_diagnostic_report.json"
    process = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--project",
            str(project),
            "--output",
            str(output),
            "--json-only",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return process.returncode, json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="art_ownership_") as temp:
        root = Path(temp)

        valid = root / "valid_active_graph"
        rgb_source(valid / "data/source_art/concept.png")
        indexed_png(valid / "res/sprite/player_strip.png", (48, 32))
        (valid / "res/sprite.res").write_text(
            'SPRITE player "sprite/player_strip.png" 3 4 FAST 5\n',
            encoding="utf-8",
        )
        exit_code, report = run(valid)
        assert exit_code == 0, report
        assert report["source_asset_status"]["critical_issues"] > 0
        assert report["active_res_asset_status"]["critical_issues"] == 0
        assert not report["build_blocking_issues"]
        assert "1 asset(s) ativos referenciados em /res" in report["summary"]

        invalid = root / "invalid_active_graph"
        rgb_source(invalid / "data/source_art/concept.png")
        bad = invalid / "res/sprite/player.png"
        bad.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (25, 31), (255, 255, 255)).save(bad)
        (invalid / "res/sprite.res").write_text(
            'SPRITE player "sprite/player.png" 4 4 FAST 5\n',
            encoding="utf-8",
        )
        exit_code, report = run(invalid)
        assert exit_code == 1, report
        assert report["build_blocking_issues"]
        assert report["active_res_asset_status"]["critical_issues"] > 0

    print("[PASS] source art routes conversion without poisoning a valid active .res graph")
    print("[PASS] critical defects in referenced /res assets remain build-blocking")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

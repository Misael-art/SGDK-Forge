#!/usr/bin/env python3
"""Fix common indexed PNG transparency issues for SGDK resources.

This utility rebuilds the palette of a PNG by converting it to RGBA and then
requantizing to a fresh 16-color palette. It creates a `.original` backup on
first run so the previous file can still be recovered manually.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image


def iter_pngs(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix.lower() == ".png" else []
    if target.is_dir():
        return sorted(path for path in target.rglob("*.png") if path.is_file())
    return []


def backup_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".original")


def fix_png(path: Path) -> bool:
    backup = backup_path(path)
    if not backup.exists():
        shutil.copy2(path, backup)

    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        # SGDK resources are safest when the palette is rebuilt from opaque RGB.
        rgb = Image.new("RGB", rgba.size, (0, 0, 0))
        rgb.paste(rgba, mask=rgba.getchannel("A"))
        quantized = rgb.quantize(colors=16, method=Image.MEDIANCUT)
        quantized.info.pop("transparency", None)
        quantized.save(path, format="PNG")

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fix palette/transparency corruption in SGDK PNG assets."
    )
    parser.add_argument("target", help="PNG file or directory to process")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.target).expanduser()
    files = iter_pngs(target)

    if not files:
        print(f"[WARN] No PNG files found at: {target}")
        return 1

    fixed = 0
    for path in files:
        try:
            if fix_png(path):
                fixed += 1
                print(f"[OK] Fixed {path}")
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Failed to process {path}: {exc}")

    print(f"[INFO] Finished. Fixed {fixed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

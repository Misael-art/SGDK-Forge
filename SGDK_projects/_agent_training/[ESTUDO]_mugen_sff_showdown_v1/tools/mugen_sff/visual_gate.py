from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image


TARGET_W = 320
TARGET_H = 224
DEFAULT_MATTE_COLORS = ((255, 0, 255), (242, 0, 242))
DEFAULT_THRESHOLD = 0.05


def _norm_rgb(color: Iterable[int]) -> tuple[int, int, int]:
    r, g, b = list(color)[:3]
    return int(r), int(g), int(b)


def analyze_frame_integrity(
    path: Path,
    *,
    matte_colors: Iterable[Iterable[int]] = DEFAULT_MATTE_COLORS,
    threshold: float = DEFAULT_THRESHOLD,
    expected_width: int = TARGET_W,
    expected_height: int = TARGET_H,
) -> dict:
    with Image.open(path) as src:
        rgba = src.convert("RGBA")

    total = rgba.width * rgba.height
    matte_set = {_norm_rgb(c) for c in matte_colors}
    transparent_pixels = 0
    exact_matte_pixels = 0
    near_magenta_pixels = 0
    bad_pixels = 0

    for r, g, b, a in rgba.getdata():
        is_transparent = int(a) == 0
        rgb = (int(r), int(g), int(b))
        is_exact_matte = rgb in matte_set
        is_near_magenta = int(r) >= 200 and int(g) <= 40 and int(b) >= 200
        if is_transparent:
            transparent_pixels += 1
        if is_exact_matte:
            exact_matte_pixels += 1
        if is_near_magenta:
            near_magenta_pixels += 1
        if is_transparent or is_exact_matte or is_near_magenta:
            bad_pixels += 1

    ratio = (bad_pixels / total) if total else 1.0
    size_ok = rgba.size == (int(expected_width), int(expected_height))
    status = "pass" if size_ok and ratio <= threshold else "fail"
    return {
        "path": Path(path).as_posix(),
        "status": status,
        "width": rgba.width,
        "height": rgba.height,
        "expected_width": int(expected_width),
        "expected_height": int(expected_height),
        "total_pixels": total,
        "transparent_pixels": transparent_pixels,
        "exact_matte_pixels": exact_matte_pixels,
        "near_magenta_pixels": near_magenta_pixels,
        "bad_pixels": bad_pixels,
        "bad_ratio": round(ratio, 6),
        "threshold": threshold,
    }


def assert_frame_integrity(
    path: Path,
    *,
    matte_colors: Iterable[Iterable[int]] = DEFAULT_MATTE_COLORS,
    threshold: float = DEFAULT_THRESHOLD,
    expected_width: int = TARGET_W,
    expected_height: int = TARGET_H,
) -> dict:
    report = analyze_frame_integrity(
        path,
        matte_colors=matte_colors,
        threshold=threshold,
        expected_width=expected_width,
        expected_height=expected_height,
    )
    if report["status"] != "pass":
        raise RuntimeError(
            "visual integrity gate failed for "
            f"{path}: bad_ratio={report['bad_ratio']} threshold={threshold} "
            f"transparent={report['transparent_pixels']} matte={report['exact_matte_pixels']} "
            f"near_magenta={report['near_magenta_pixels']}"
        )
    return report

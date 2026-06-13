from pathlib import Path
import sys

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from mugen_sff.visual_gate import analyze_frame_integrity, assert_frame_integrity


def test_visual_gate_rejects_large_magenta_matte(tmp_path: Path) -> None:
    path = tmp_path / "bad.png"
    img = Image.new("RGB", (320, 224), (0, 0, 0))
    for y in range(224):
        for x in range(20):
            img.putpixel((x, y), (242, 0, 242))
    img.save(path)

    report = analyze_frame_integrity(path)

    assert report["status"] == "fail"
    assert report["bad_ratio"] > 0.05
    with pytest.raises(RuntimeError):
        assert_frame_integrity(path)


def test_visual_gate_accepts_clean_frame(tmp_path: Path) -> None:
    path = tmp_path / "clean.png"
    Image.new("RGB", (320, 224), (34, 68, 102)).save(path)

    report = assert_frame_integrity(path)

    assert report["status"] == "pass"
    assert report["bad_pixels"] == 0


def test_visual_gate_accepts_declared_world_size(tmp_path: Path) -> None:
    path = tmp_path / "world.png"
    Image.new("RGB", (768, 480), (68, 116, 224)).save(path)

    report = assert_frame_integrity(path, expected_width=768, expected_height=480)

    assert report["status"] == "pass"
    assert report["width"] == 768
    assert report["height"] == 480

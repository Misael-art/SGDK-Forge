"""The stage gate must keep HUD ownership and reject unmeasured capacity."""
from collections import Counter
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge.stage_candidate import _palette, _rgb, _tiles, _view_width, generate  # noqa: E402


def test_palette_keeps_hud_words_and_selects_eight_other_cram_words():
    src = [(0, 0, 0)] * 256
    for i in range(1, 32):
        src[i] = (i * 7, i * 3, 255 - i * 4)
    fixed = [0xEEE, 0x444, 0x02E, 0x0EE, 0x00A, 0xE62, 0xA20]
    a = _palette(src, Counter({i: 32 + i for i in range(1, 32)}), fixed)
    b = _palette(src, Counter({i: 32 + i for i in range(1, 32)}), fixed)
    assert a == b
    assert a[0] == 0
    assert a[9:] == fixed
    assert len(set(a[1:9])) == 8
    assert set(a[1:9]).isdisjoint(fixed)


def test_flip_equivalent_tile_is_counted_once():
    left = bytes((1, 2, 3, 4, 5, 6, 7, 8))
    data = b"".join(left + left[::-1] for _ in range(8))
    assert len(_tiles(data, 16, 8)) == 1


def test_view_covers_full_camera_span_instead_of_truncating_right_edge():
    assert _view_width(448, 0.43) == 520
    assert _view_width(448, 0.67) == 624


def test_stage_cram_decode_uses_hardware_rgb_order_and_converter_grid():
    assert _rgb(0x000) == (0, 0, 0)
    assert _rgb(0x00E) == (252, 0, 0)
    assert _rgb(0x0E0) == (0, 252, 0)
    assert _rgb(0xE00) == (0, 0, 252)
    assert _rgb(0xEEE) == (252, 252, 252)

    for red in range(8):
        for green in range(8):
            for blue in range(8):
                word = (red << 1) | (green << 5) | (blue << 9)
                assert _rgb(word) == (red * 36, green * 36, blue * 36)


def test_stage_requires_measured_budget(tmp_path):
    with pytest.raises(ValueError, match="budget"):
        generate(tmp_path / "missing.zip", tmp_path / "out", [0] * 7, 0)

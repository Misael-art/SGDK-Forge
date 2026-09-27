"""Stage feasibility must classify colors using the shipping converter grid."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge.parsers.sff import Sprite
from mugen2sgdk_forge.stage_measure import _md, _frame_stats, layer_stats, plane_stats


@pytest.mark.parametrize("red,level", [(17,0),(18,1),(53,1),(54,2),(125,3),
                                      (126,4),(197,5),(198,6),(233,6),(234,7),(255,7)])
def test_measurement_uses_converter_thresholds(red, level):
    assert _md((red,0,0)) == (level,0,0)


@pytest.mark.parametrize("colors,expected", [([(17,0,0),(18,0,0)],2),
                                           ([(18,0,0),(19,0,0)],1)])
def test_stage_color_counts_do_not_merge_or_split_wrong_boundary(colors,expected):
    palette = [(255,0,255)] + colors + [(0,0,0)]*253
    pixels = bytes([1,2]*32)  # Both indices opaque, including hardware black.
    sprite = Sprite(0,0,0,0,8,8,pixels,palette,False,None,0)
    layer = layer_stats(sprite,palette)
    assert layer["md_colours"] == expected
    assert layer["max_md_colours_per_tile"] == expected
    assert _frame_stats(sprite)["max_md_colours_per_tile"] == expected
    # plane_stats expects a complete 224-row plane.
    plane = [list(pixels[:8]) for _ in range(224)]
    assert plane_stats(plane,palette)["md_colours"] == expected

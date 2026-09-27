"""Static source-stage compositor keeps mask semantics and exposes H-scroll conflicts."""
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import stage_source_view  # noqa: E402
from mugen2sgdk_forge.parsers import stage  # noqa: E402
from mugen2sgdk_forge.parsers.sff import Sprite  # noqa: E402

PROJECT = Path(__file__).resolve().parents[3] / "SGDK_projects" / \
    "Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
SUZAKU = PROJECT / "rascunho" / "entrada_bruta" / "ssf2_01_ryu.zip"


def test_masked_upper_layer_reveals_opaque_underlay_and_reports_two_speeds():
    st = stage.parse("""[StageInfo]
localcoord = 8,8
[Camera]
boundleft = -1
boundright = 1
[BG base]
spriteno = 1,0
delta = 0,1
[BG overlay]
spriteno = 2,0
delta = 1,1
mask = 1
""")
    palette = [(0, 0, 0), (32, 64, 96), (224, 32, 32)] + [(0, 0, 0)] * 253
    base = Sprite(1, 0, 4, 0, 8, 8, bytes([1] * 64), palette, False, None, 0)
    overlay_row = bytes([2, 0] * 4)
    overlay = Sprite(2, 0, 5, 0, 8, 8, overlay_row * 8, palette, False, None, 1)
    view = stage_source_view.render(st, [base, overlay], 0, crop_top=0, width=8, height=8)
    assert view["pixels"][:8] == bytes([2, 1] * 4)
    assert view["visible_pixels_by_layer"] == {"BG base": 32, "BG overlay": 32}
    assert view["scanlines"][0]["horizontal_deltas"] == [0.0, 1.0]
    assert view["scanlines"][0]["horizontal_delta_by_layer"] == {"BG base": 0.0, "BG overlay": 1.0}
    assert view["scanlines"][0]["one_scroll_group_needed_per_visible_delta"] == 2


def test_scroll_assignment_can_render_an_analysis_only_speed_remap():
    st = stage.parse("""[StageInfo]
localcoord = 8,8
[Camera]
boundleft = -1
boundright = 1
[BG base]
spriteno = 1,0
delta = 0,1
[BG overlay]
spriteno = 2,0
delta = 1,1
mask = 1
""")
    palette = [(0, 0, 0), (32, 64, 96), (224, 32, 32)] + [(0, 0, 0)] * 253
    base = Sprite(1, 0, 4, 0, 8, 8, bytes([1] * 64), palette, False, None, 0)
    overlay = Sprite(2, 0, 5, 0, 8, 8, bytes([2] * 64), palette, False, None, 1)
    unchanged = stage_source_view.render(st, [base, overlay], 0, crop_top=0, width=8, height=8)
    remapped = stage_source_view.render(
        st, [base, overlay], 0, crop_top=0, width=8, height=8,
        speed_remap_by_scanline={y: {"1.0": 0.0} for y in range(8)})
    assert unchanged["pixels"] != remapped["pixels"]


def test_camera_sweep_aggregates_visible_groups_and_anchor_distance():
    def view(speed, count):
        return {"scanlines": [{"screen_y": 0,
                               "visible_pixels_by_layer": {"roof": count},
                               "horizontal_delta_by_layer": {"roof": speed}}]}

    profile = stage_source_view.aggregate_camera_sweep(
        [(0, view(0.5, 3)), (4, view(0.5, 2)), (8, view(0.75, 5))], anchor=4)
    assert profile["sample_count"] == 3
    assert profile["total_visible_pixel_samples"] == 10
    by_speed = {row["speed"]: row for row in profile["scanlines"][0]["source_speed_groups"]}
    assert by_speed[0.5]["visible_pixels"] == 5
    assert by_speed[0.5]["distance_weighted_pixels"] == 12
    assert by_speed[0.5]["max_camera_distance"] == 4
    assert by_speed[0.75]["max_camera_from_left"] == 8


def test_camera_sweep_rejects_duplicate_positions_or_bad_anchor():
    sample = (0, {"scanlines": []})
    with pytest.raises(ValueError, match="unique"):
        stage_source_view.aggregate_camera_sweep([sample, sample], anchor=0)
    with pytest.raises(ValueError, match="inside sampled bounds"):
        stage_source_view.aggregate_camera_sweep([sample], anchor=1)


def test_suzaku_source_view_confirms_opaque_sky_fallback_is_fully_covered(tmp_path):
    if not SUZAKU.exists():
        pytest.skip("stage de terceiros fora do Git")
    from mugen2sgdk_forge.stage_bands import load_source
    st, sprites = load_source(SUZAKU, "ssf2-01-ryu.def", "ssf2-01-ryu.sff")
    report = stage_source_view.analyze(st, sprites, hashlib.sha256(SUZAKU.read_bytes()).hexdigest(),
                                       tmp_path, crop_top=16)
    assert report["camera_samples_from_left_bound"] == [0, 224, 448]
    assert all(view["visible_pixels_by_layer"]["BG 0a"] == 0 for view in report["views"])
    assert all(view["multi_delta_scanline_count"] > 0 for view in report["views"])
    assert report["views"][1]["max_distinct_scroll_groups_in_scanline"] == 4
    assert report["views"][1]["scanlines_over_two_plane_capacity_count"] == 32
    assert report["views"][1]["visible_pixels_by_layer"]["BG 0b"] > 0
    assert report["views"][1]["visible_pixels_by_layer"]["BG 1"] > 0
    assert report["views"][1]["visible_pixels_by_layer"]["BG 2"] > 0
    assert report["views"][1]["visible_pixels_by_layer"]["BG 3"] > 0
    assert report["views"][1]["scanlines_over_two_plane_capacity"]
    assert len(report["previews"]) == 3
    assert all((tmp_path / item["path"]).is_file() for item in report["previews"])


def test_source_view_rejects_unsupported_blend_and_window_features():
    st = stage.parse("""[StageInfo]
localcoord = 8,8
[BG x]
spriteno = 1,0
trans = add
""")
    palette = [(0, 0, 0), (255, 255, 255)] + [(0, 0, 0)] * 254
    sprite = Sprite(1, 0, 0, 0, 8, 8, bytes([1] * 64), palette, False, None, 0)
    with pytest.raises(ValueError, match="does not support"):
        stage_source_view.render(st, [sprite], 0, crop_top=0, width=8, height=8)

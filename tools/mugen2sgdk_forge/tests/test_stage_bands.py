"""H-scroll band compositor estimate: synthetic geometry plus the real Suzaku source."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import stage_bands  # noqa: E402
from mugen2sgdk_forge.parsers import stage  # noqa: E402
from mugen2sgdk_forge.parsers.sff import Sprite  # noqa: E402

PROJECT = Path(__file__).resolve().parents[3] / "SGDK_projects" / \
    "Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
SUZAKU = PROJECT / "rascunho" / "entrada_bruta" / "ssf2_01_ryu.zip"
CONTRACT = PROJECT / "doc" / "mugen" / "suzaku_front_bands_contract_2026_09_25.json"


def _tiny_fixture():
    st = stage.parse("""[StageInfo]
localcoord = 8, 8
[Camera]
boundleft = -2
boundright = 2
[BG p]
type = parallax
spriteno = 1,0
start = 0,0
delta = .5,1
xscale = 1,2
""")
    palette = [(0, 0, 0), (255, 0, 0)] + [(0, 0, 0)] * 254
    pixels = bytes([1, 0, 1, 0, 1, 0, 1, 0] * 8)
    spr = Sprite(1, 0, 0, 0, 8, 8, pixels, palette, False, None, 0)
    contract = {"viewport_width": 8, "viewport_height": 8, "crop_top": 0,
                "camera_sampling": {"step": 1},
                "bands": [{"name": "test", "layer": "BG p", "y0": 0, "y1": 8}]}
    return st, [spr], contract


def test_parallax_xscale_becomes_a_per_scanline_scroll_profile(tmp_path):
    st, sprites, contract = _tiny_fixture()
    words = ["0x000", "0xE00"] + ["0x000"] * 14
    report = stage_bands.analyze(st, sprites, contract, "a" * 64, tmp_path,
                                 {"palette_words": words, "_report_sha256": "c" * 64})
    profile = report["line_scroll_profile"]
    assert profile[0]["camera_delta_per_pixel"] == pytest.approx(0.5)
    assert profile[7]["camera_delta_per_pixel"] == pytest.approx(1.0)
    assert profile[0]["offsets_at_first_middle_last_camera_sample"] == [0, 1, 2]
    assert report["camera_sampling"]["positions"] == 5
    assert report["map"]["width_pixels_for_full_camera_span"] == 16
    assert len(report["previews"]) == 3
    assert all((tmp_path / item["path"]).is_file() for item in report["previews"])
    assert report["status"] == "analysis_only_opaque_index0_remap_required"
    assert report["source_zero_semantics"]["opaque_zero_remap_required"] is True
    assert report["candidate_palette_pattern_cost"]["status"] == "unapproved_candidate_with_opaque_zero_remap"
    assert report["candidate_palette_pattern_cost"]["opaque_source_zero_target_index"] > 0
    assert report["candidate_palette_pattern_cost"]["palette_approved"] is False


def test_contract_must_cover_the_viewport_exactly():
    st, sprites, contract = _tiny_fixture()
    contract["bands"][0]["y1"] = 7
    with pytest.raises(ValueError, match="bands end at 7"):
        stage_bands.analyze(st, sprites, contract, "b" * 64)


def test_suzaku_front_contract_measures_scroll_and_vdp_color_zero_semantics(tmp_path):
    if not SUZAKU.exists():
        pytest.skip("stage de terceiros fora do Git")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    st, sprites = stage_bands.load_source(SUZAKU, "ssf2-01-ryu.def", "ssf2-01-ryu.sff")
    import hashlib
    palette_candidate_path = PROJECT / "rascunho" / "processado" / "stage_takeover" / \
        "v2_color_corrected" / "candidate_report.json"
    palette_candidate = json.loads(palette_candidate_path.read_text(encoding="utf-8"))
    report = stage_bands.analyze(st, sprites, contract,
                                 hashlib.sha256(SUZAKU.read_bytes()).hexdigest(), tmp_path,
                                 palette_candidate)
    profile = {row["screen_y"]: row for row in report["line_scroll_profile"]}
    assert profile[0]["layer"] == "BG 3"
    assert profile[0]["camera_delta_per_pixel"] == pytest.approx(0.671875)
    assert profile[176]["layer"] == "BG 4a"
    assert profile[176]["camera_delta_per_pixel"] == pytest.approx(0.792410)
    assert profile[211]["camera_delta_per_pixel"] == pytest.approx(0.792410 * 1.377466)
    assert profile[212]["layer"] == "BG 4b"
    assert profile[212]["camera_delta_per_pixel"] == pytest.approx(1.102678)
    assert report["map"]["width_pixels_for_full_camera_span"] > 512
    assert report["map"]["fits_128_column_plane"] is True
    assert report["semantic_gates"]["mugen_mask_layers"] == ["BG 3"]
    assert report["semantic_gates"]["genesis_scroll_plane_color0_is_transparent"] is True
    assert report["semantic_gates"]["layer_assignment_across_bg_a_bg_b"] == "not_modeled"
    assert report["claim_ceiling"] == "source_derived_analysis_only"
    assert report["camera_sampling"]["camera_frame_step"] == 4
    assert report["viewport_pattern_cost"]["maximum_unique_source_tiles_with_flip"] == 460
    assert report["candidate_palette_pattern_cost"]["maximum_unique_tiles_with_flip"] == 431
    assert report["source_zero_semantics"]["opaque_zero_remap_required"] is False
    assert all(row["total_visible_opaque_index0_pixels"] == 0
               for row in report["source_zero_semantics"]["visible_opaque_index0_pixels_by_camera"])

"""Two-plane scroll speed tradeoff lower-bound tests."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import stage_plane_tradeoffs  # noqa: E402


def test_weighted_pair_preserves_the_two_large_speed_groups():
    row = {"screen_y": 7,
           "visible_pixels_by_layer": {"far": 10, "middle": 1, "near": 10},
           "horizontal_delta_by_layer": {"far": 0.0, "middle": 0.5, "near": 1.0}}
    result = stage_plane_tradeoffs._line_tradeoff(row, camera_frame_step=4)
    assert result["preserved_scroll_speeds"] == [0.0, 1.0]
    assert result["remapped_visible_pixels"] == 1
    assert result["pixel_displacement_error_lower_bound"] == pytest.approx(2.0)
    assert result["source_to_plane_speed_assignment"]["0.5"] == 0.0


def test_two_or_fewer_groups_have_zero_speed_remap_cost():
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "source_sha256": "a" * 64,
              "views": [{"camera_from_left": 3, "scanlines": [
                  {"screen_y": 0, "visible_pixels_by_layer": {"base": 8, "front": 8},
                   "horizontal_delta_by_layer": {"base": 0.0, "front": 1.0}}
              ]}]}
    result = stage_plane_tradeoffs.analyze(report, 4)
    view = result["views"][0]
    assert view["source_scanlines_over_two_speed_capacity"] == 0
    assert view["pixels_assigned_to_a_different_speed_group"] == 0
    assert view["mean_displacement_error_per_visible_pixel_per_frame"] == 0
    assert result["cross_camera_scanline_profile"]["source_scanlines_over_two_speed_capacity"] == 0


def test_tradeoff_rejects_missing_layer_speed_mapping_and_invalid_step():
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1", "views": []}
    with pytest.raises(ValueError, match="positive integer"):
        stage_plane_tradeoffs.analyze(report, 0)
    with pytest.raises(ValueError, match="positive integer"):
        stage_plane_tradeoffs.analyze(report, True)
    line = {"screen_y": 0, "visible_pixels_by_layer": {"base": 8},
            "horizontal_delta_by_layer": {}}
    with pytest.raises(ValueError, match="every visible layer"):
        stage_plane_tradeoffs._line_tradeoff(line, 4)


def test_cross_camera_profile_chooses_one_speed_pair_for_each_scanline():
    def row(counts):
        return {"screen_y": 0, "visible_pixels_by_layer": counts,
                "horizontal_delta_by_layer": {"far": 0.0, "mid": 0.5, "near": 1.0}}
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "views": [{"camera_from_left": 0, "scanlines": [row({"far": 10, "mid": 1, "near": 10})]},
                        {"camera_from_left": 8, "scanlines": [row({"far": 10, "mid": 10, "near": 8})]}]}
    result = stage_plane_tradeoffs.analyze(report, 4)
    combined = result["cross_camera_scanline_profile"]
    assignment = combined["scanline_assignments"][0]
    assert combined["camera_samples_from_left_bound"] == [0, 8]
    assert assignment["preserved_scroll_speeds"] == [0.0, 1.0]
    assert assignment["remapped_visible_pixels"] == 11
    assert combined["maximum_displacement_per_pixel_per_frame"] == pytest.approx(2.0)
    assert combined["maximum_displacement_screen_y"] == 0
    assert result["anchor_alignment_tradeoff"]["reference_camera_from_left"] == 4
    assert result["anchor_alignment_tradeoff"]["maximum_alignment_drift_px"] == pytest.approx(2.0)


def test_cross_camera_profile_rejects_inconsistent_same_layer_speed():
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "views": [{"camera_from_left": 0, "scanlines": [
                  {"screen_y": 0, "visible_pixels_by_layer": {"bg": 8},
                   "horizontal_delta_by_layer": {"bg": 0.0}}]},
                        {"camera_from_left": 8, "scanlines": [
                  {"screen_y": 0, "visible_pixels_by_layer": {"bg": 8},
                   "horizontal_delta_by_layer": {"bg": 0.5}}]}]}
    with pytest.raises(ValueError, match="inconsistent scroll delta"):
        stage_plane_tradeoffs.analyze(report, 4)


def test_anchor_must_be_integral_and_inside_camera_span():
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "views": [{"camera_from_left": 0, "scanlines": []},
                        {"camera_from_left": 8, "scanlines": []}]}
    with pytest.raises(ValueError, match="within sampled camera bounds"):
        stage_plane_tradeoffs.analyze(report, 4, 9)
    with pytest.raises(ValueError, match="within sampled camera bounds"):
        stage_plane_tradeoffs.analyze(report, 4, 4.5)


def test_endpoint_minimax_can_choose_continuous_targets_to_reduce_worst_drift():
    def row():
        return {"screen_y": 0,
                "visible_pixels_by_layer": {"far": 8, "middle": 8, "near": 8},
                "horizontal_delta_by_layer": {"far": 0.0, "middle": 0.47, "near": 0.672}}

    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "source_sha256": "a" * 64,
              "views": [{"camera_from_left": 0, "scanlines": [row()]},
                        {"camera_from_left": 8, "scanlines": [row()]}]}
    result = stage_plane_tradeoffs.analyze(report, 4, 4,
                                            objective="endpoint_minimax_continuous")
    profile = result["cross_camera_scanline_profile"]
    assignment = profile["scanline_assignments"][0]
    assert result["objective"] == "endpoint_minimax_continuous"
    assert assignment["target_scroll_speeds"] == pytest.approx([0.0, 0.571])
    assert assignment["preserved_scroll_speeds"] == [0.0]
    assert assignment["source_to_plane_speed_assignment"]["0.47"] == pytest.approx(0.571)
    assert assignment["source_to_plane_speed_assignment"]["0.672"] == pytest.approx(0.571)
    assert result["anchor_alignment_tradeoff"]["maximum_alignment_drift_px"] == pytest.approx(0.404)
    assert result["anchor_alignment_tradeoff"]["maximum_alignment_drift_px"] < 0.47 * 4


def test_endpoint_minimax_keeps_two_source_speeds_exact():
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "source_sha256": "b" * 64,
              "views": [{"camera_from_left": 0, "scanlines": [
                  {"screen_y": 0, "visible_pixels_by_layer": {"far": 8, "near": 8},
                   "horizontal_delta_by_layer": {"far": 0.0, "near": 1.0}}]},
                        {"camera_from_left": 8, "scanlines": [
                  {"screen_y": 0, "visible_pixels_by_layer": {"far": 8, "near": 8},
                   "horizontal_delta_by_layer": {"far": 0.0, "near": 1.0}}]}]}
    result = stage_plane_tradeoffs.analyze(report, 4, 4,
                                            objective="endpoint_minimax_continuous")
    assignment = result["cross_camera_scanline_profile"]["scanline_assignments"][0]
    assert assignment["status"] == "two_or_fewer_source_groups"
    assert assignment["source_to_plane_speed_assignment"] == {"0.0": 0.0, "1.0": 1.0}
    assert result["anchor_alignment_tradeoff"]["maximum_alignment_drift_px"] == 0


def test_endpoint_minimax_prefers_camera_sweep_weights_when_available():
    def row(camera):
        return {"screen_y": 0,
                "visible_pixels_by_layer": {"far": 8, "middle": 8, "near": 8},
                "horizontal_delta_by_layer": {"far": 0.0, "middle": 0.47, "near": 0.672}}

    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "source_sha256": "c" * 64,
              "views": [{"camera_from_left": camera, "scanlines": [row(camera)]}
                        for camera in (0, 4, 8)],
              "camera_sweep_profile": {
                  "schema": "mugen2sgdk_forge.stage_camera_sweep_profile/v1",
                  "camera_positions_from_left": [0, 2, 4, 6, 8],
                  "sample_count": 5,
                  "reference_camera_from_left": 4,
                  "total_visible_pixel_samples": 120,
                  "scanlines": [{"screen_y": 0, "total_visible_pixel_samples": 120,
                                 "source_speed_groups": [
                                     {"speed": 0.0, "visible_pixels": 40,
                                      "distance_weighted_pixels": 120,
                                      "max_camera_distance": 4,
                                      "max_camera_from_left": 0, "layers": ["far"]},
                                     {"speed": 0.47, "visible_pixels": 40,
                                      "distance_weighted_pixels": 120,
                                      "max_camera_distance": 4,
                                      "max_camera_from_left": 0, "layers": ["middle"]},
                                     {"speed": 0.672, "visible_pixels": 40,
                                      "distance_weighted_pixels": 120,
                                      "max_camera_distance": 4,
                                      "max_camera_from_left": 8, "layers": ["near"]}]}]}}
    result = stage_plane_tradeoffs.analyze(report, 4, 4,
                                            objective="endpoint_minimax_continuous")
    assert result["camera_sweep_sample_count"] == 5
    assert result["cross_camera_scanline_profile"]["camera_samples_from_left_bound"] == [0, 2, 4, 6, 8]
    assert result["anchor_alignment_tradeoff"]["total_visible_pixel_samples"] == 120
    assert result["anchor_alignment_tradeoff"]["maximum_alignment_drift_px"] == pytest.approx(0.404)
    discrete = stage_plane_tradeoffs.analyze(report, 4, 4)
    assert discrete["camera_sweep_sample_count"] == 5
    assert discrete["cross_camera_scanline_profile"]["total_visible_pixel_samples"] == 120
    assert discrete["anchor_alignment_tradeoff"]["total_visible_pixel_samples"] == 120

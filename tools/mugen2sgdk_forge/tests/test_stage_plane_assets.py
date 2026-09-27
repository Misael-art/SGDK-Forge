from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from mugen2sgdk_forge import stage_plane_assets


def _palette_png(path: Path, pixels: list[int]) -> None:
    image = Image.new("P", (8, 8))
    image.putpalette([0, 0, 0, 0, 0, 34, 34, 0, 34] + [0, 0, 0] * 13)
    image.putdata(pixels)
    image.save(path, "PNG", bits=4)


def _valid_case(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    far_path = tmp_path / "far.png"
    near_path = tmp_path / "near.png"
    composite_path = tmp_path / "composite.png"
    palette_path = tmp_path / "palette.png"
    output = tmp_path / "out"

    far = Image.new("RGB", (8, 8), (0, 0, 34))
    far.save(far_path)
    near = Image.new("RGBA", (8, 8), (34, 0, 34, 0))
    for y in range(8):
        for x in range(4):
            near.putpixel((x, y), (34, 0, 34, 200 if x < 2 else 127))
    near.save(near_path)

    hard_near = near.copy()
    alpha = hard_near.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
    hard_near.putalpha(alpha)
    far_rgba = far.convert("RGBA")
    composite = far_rgba.copy()
    composite.alpha_composite(hard_near)
    composite.convert("RGB").save(composite_path)

    indices = [2 if x < 2 else 1 for y in range(8) for x in range(8)]
    _palette_png(palette_path, indices)
    return far_path, near_path, composite_path, palette_path, output


def test_split_pair_shares_palette_and_reconstructs_flat_candidate(tmp_path: Path) -> None:
    far, near, composite, palette, output = _valid_case(tmp_path)
    report = stage_plane_assets.split_plane_images(
        far, near, composite, palette, output, target=(8, 8), alpha_threshold=128
    )
    assert report["status"] == "technical_candidate"
    assert report["blocking"] is False
    assert report["reconstruction"]["mismatch_pixels_vs_palette_candidate"] == 0
    assert report["far_plane"]["pixel_contract"]["blocking"] is False
    assert report["near_plane"]["pixel_contract"]["blocking"] is False
    assert report["near_plane"]["alpha_source_counts"]["partial"] > 0


def test_tile_pool_probe_finds_exact_cross_plane_reuse(tmp_path: Path) -> None:
    far, near, composite, palette, output = _valid_case(tmp_path)
    # Make the near tile opaque and identical to the far tile. A shared hardware
    # tileset can represent both planes with one pattern; separate TILESET
    # resources would otherwise carry it twice.
    near_image = Image.new("RGBA", (8, 8), (0, 0, 34, 255))
    near_image.save(near)
    with Image.open(far) as opened:
        opened.convert("RGB").save(composite)
    _palette_png(palette, [1] * 64)
    report = stage_plane_assets.split_plane_images(
        far, near, composite, palette, output, target=(8, 8), alpha_threshold=128
    )
    probe = report["tile_pool_reuse_probe"]
    assert probe["far_unique_tiles"] == 1
    assert probe["near_unique_tiles"] == 1
    assert probe["cross_plane_shared_tiles"] == 1
    assert probe["common_tileset_unique_union"] == 1
    assert probe["separate_plane_unique_sum"] == 2


def test_split_rejects_composite_that_does_not_match_plates(tmp_path: Path) -> None:
    far, near, composite, palette, output = _valid_case(tmp_path)
    with Image.open(composite) as opened:
        altered = opened.convert("RGB")
    altered.putpixel((7, 7), (238, 0, 0))
    altered.save(composite)
    with pytest.raises(stage_plane_assets.StagePlaneAssetsError, match="composite_source_does_not_match"):
        stage_plane_assets.split_plane_images(
            far, near, composite, palette, output, target=(8, 8), alpha_threshold=128
        )


def test_split_rejects_transparency_in_far_plane(tmp_path: Path) -> None:
    far, near, composite, palette, output = _valid_case(tmp_path)
    image = Image.new("RGBA", (8, 8), (0, 0, 34, 255))
    image.putpixel((0, 0), (0, 0, 34, 0))
    image.save(far)
    with pytest.raises(stage_plane_assets.StagePlaneAssetsError, match="far_plane_must_be_fully_opaque"):
        stage_plane_assets.split_plane_images(
            far, near, composite, palette, output, target=(8, 8), alpha_threshold=128
        )


def test_split_rejects_nonempty_output_directory(tmp_path: Path) -> None:
    far, near, composite, palette, output = _valid_case(tmp_path)
    output.mkdir()
    (output / "keep.txt").write_text("preserve", encoding="utf-8")
    with pytest.raises(stage_plane_assets.StagePlaneAssetsError, match="output_dir_must_be_empty"):
        stage_plane_assets.split_plane_images(
            far, near, composite, palette, output, target=(8, 8), alpha_threshold=128
        )
    assert (output / "keep.txt").read_text(encoding="utf-8") == "preserve"


def test_split_rejects_bad_target_and_threshold(tmp_path: Path) -> None:
    far, near, composite, palette, output = _valid_case(tmp_path)
    with pytest.raises(stage_plane_assets.StagePlaneAssetsError, match="multiples_of_8"):
        stage_plane_assets.split_plane_images(
            far, near, composite, palette, output, target=(10, 8), alpha_threshold=128
        )
    with pytest.raises(stage_plane_assets.StagePlaneAssetsError, match="alpha_threshold_out_of_range"):
        stage_plane_assets.split_plane_images(
            far, near, composite, palette, output, target=(8, 8), alpha_threshold=300
        )

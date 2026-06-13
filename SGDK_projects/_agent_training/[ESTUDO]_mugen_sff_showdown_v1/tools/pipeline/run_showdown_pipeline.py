from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from mugen_sff.sff_v1 import extract_sff_v1_pcx, iter_sff_v1_entries
from mugen_sff.def_stage import parse_stage_def
from mugen_sff.visual_gate import assert_frame_integrity


VIEWPORT_W = 320
VIEWPORT_H = 224
MUGEN_VIEW_H = 240
SKY_TOP_RGB = (85, 117, 255)
SKY_HORIZON_RGB = (117, 170, 255)


@dataclass(frozen=True)
class SpriteAsset:
    group: int
    index: int
    path: Path
    axis_x: int
    axis_y: int
    palette_index0_rgb: tuple[int, int, int]
    width: int
    height: int


@dataclass(frozen=True)
class WorldGeometry:
    width: int
    height: int
    tiles_w: int
    tiles_h: int
    camera_min_x: int
    camera_max_x: int
    camera_min_y: int
    camera_max_y: int
    camera_start_scroll_x: int
    camera_start_scroll_y: int
    viewer_default_x: int
    viewer_default_y: int


def _palette_index0_rgb(img: Image.Image) -> tuple[int, int, int]:
    palette = img.getpalette() or []
    if len(palette) < 3:
        return (0, 0, 0)
    return (int(palette[0]), int(palette[1]), int(palette[2]))


def _is_chroma_key_matte(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return int(r) >= 200 and int(g) <= 40 and int(b) >= 200


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _ceil8(value: int) -> int:
    return ((int(value) + 7) // 8) * 8


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def compute_world_geometry(stage) -> WorldGeometry:
    camera_span_x = int(stage.camera_boundright - stage.camera_boundleft)
    camera_span_y = int(stage.camera_boundlow - stage.camera_boundhigh)
    width = _ceil8(VIEWPORT_W + max(0, camera_span_x))
    height = _ceil8(MUGEN_VIEW_H + max(0, camera_span_y))
    camera_max_x = max(0, width - VIEWPORT_W)
    camera_max_y = max(0, height - VIEWPORT_H)
    start_x = _clamp(stage.camera_startx - stage.camera_boundleft, 0, camera_max_x)
    start_y = _clamp((stage.camera_starty - stage.camera_boundhigh) + (MUGEN_VIEW_H - VIEWPORT_H), 0, camera_max_y)

    return WorldGeometry(
        width=width,
        height=height,
        tiles_w=width // 8,
        tiles_h=height // 8,
        camera_min_x=0,
        camera_max_x=camera_max_x,
        camera_min_y=0,
        camera_max_y=camera_max_y,
        camera_start_scroll_x=start_x,
        camera_start_scroll_y=start_y,
        viewer_default_x=_clamp(start_x, 0, camera_max_x),
        viewer_default_y=_clamp(start_y, 0, camera_max_y),
    )


def load_sprite_catalog(sff_path: Path, sprite_dir: Path) -> dict[tuple[int, int], SpriteAsset]:
    catalog: dict[tuple[int, int], SpriteAsset] = {}
    previous_palette: list[int] | None = None

    for entry in iter_sff_v1_entries(sff_path):
        path = sprite_dir / f"{entry.group}_{entry.index}.pcx"
        with Image.open(path) as src:
            pimg = src.convert("P")
            if entry.same_palette_as_previous and previous_palette is not None:
                pimg.putpalette(previous_palette)
                pimg.save(path)
            palette = pimg.getpalette()
            if palette:
                previous_palette = list(palette)
            key_rgb = _palette_index0_rgb(pimg)
            width, height = pimg.size

        catalog[(entry.group, entry.index)] = SpriteAsset(
            group=int(entry.group),
            index=int(entry.index),
            path=path,
            axis_x=int(entry.axis_x),
            axis_y=int(entry.axis_y),
            palette_index0_rgb=key_rgb,
            width=int(width),
            height=int(height),
        )

    return catalog


def load_pcx(
    catalog: dict[tuple[int, int], SpriteAsset],
    group: int,
    index: int,
    *,
    mask: int,
) -> tuple[Image.Image, SpriteAsset, int, str]:
    asset = catalog[(group, index)]
    effective_mask = 1 if mask or _is_chroma_key_matte(asset.palette_index0_rgb) else 0
    mask_source = "def_mask" if mask else ("inferred_chroma_key_index0" if effective_mask else "opaque")
    with Image.open(asset.path) as img:
        pimg = img.convert("P")
        rgba = pimg.convert("RGBA")
        if effective_mask:
            alpha = pimg.point(lambda px: 0 if int(px) == 0 else 255, "L")
            rgba.putalpha(alpha)
        return rgba, asset, effective_mask, mask_source


def _sky_background(width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height), SKY_TOP_RGB + (255,))
    px = img.load()
    for y in range(height):
        # Match the source sky near the BG0 top edge, then drift slightly toward
        # the original horizon ramp. This fills camera-bounds space without a
        # black void or an obvious resized source rectangle.
        hold = max(1, (height * 36) // 100)
        t_num = max(0, y - hold)
        t_den = max(1, height - hold)
        r = (SKY_TOP_RGB[0] * (t_den - t_num) + SKY_HORIZON_RGB[0] * t_num) // t_den
        g = (SKY_TOP_RGB[1] * (t_den - t_num) + SKY_HORIZON_RGB[1] * t_num) // t_den
        b = (SKY_TOP_RGB[2] * (t_den - t_num) + SKY_HORIZON_RGB[2] * t_num) // t_den
        for x in range(width):
            px[x, y] = (int(r), int(g), int(b), 255)
    return img


def _tile_positions(origin: int, extent: int, target_extent: int, enabled: int) -> list[int]:
    if not enabled:
        return [origin]
    if extent <= 0:
        return [origin]
    start = origin
    while start > 0:
        start -= extent
    positions: list[int] = []
    cursor = start
    while cursor < target_extent:
        positions.append(cursor)
        cursor += extent
    return positions


def _paste_layer(
    base: Image.Image,
    layer: Image.Image,
    origin_x: int,
    origin_y: int,
    tile_x: int,
    tile_y: int,
) -> list[dict[str, int]]:
    placements: list[dict[str, int]] = []
    xs = _tile_positions(origin_x, layer.width, base.width, tile_x)
    ys = _tile_positions(origin_y, layer.height, base.height, tile_y)
    for y in ys:
        for x in xs:
            base.paste(layer, (int(x), int(y)), layer)
            placements.append({"x": int(x), "y": int(y)})
    return placements


def composite_world_frame(stage, geometry: WorldGeometry, catalog: dict[tuple[int, int], SpriteAsset], bg2_frame):
    base = _sky_background(geometry.width, geometry.height)
    placement_report: list[dict] = []

    for bg in stage.bgs:
        if bg.kind == "anim":
            if bg2_frame is None:
                continue
            group, index = bg2_frame.group, bg2_frame.index
            offset_x, offset_y = bg2_frame.offset_x, bg2_frame.offset_y
        else:
            if bg.sprite_group is None or bg.sprite_index is None:
                continue
            group, index = bg.sprite_group, bg.sprite_index
            offset_x, offset_y = 0, 0

        layer, asset, effective_mask, mask_source = load_pcx(catalog, group, index, mask=bg.mask)
        origin_x = int((geometry.width // 2) + bg.start_x + offset_x - asset.axis_x)
        origin_y = int(geometry.height - (MUGEN_VIEW_H - bg.start_y) + offset_y - asset.axis_y)
        placements = _paste_layer(base, layer, origin_x, origin_y, bg.tile_x, bg.tile_y)
        placement_report.append(
            {
                "bg_id": int(bg.id),
                "kind": bg.kind,
                "sprite": {"group": int(group), "index": int(index)},
                "mask": int(bg.mask),
                "effective_mask": int(effective_mask),
                "mask_source": mask_source,
                "start": {"x": int(bg.start_x), "y": int(bg.start_y)},
                "delta": {"x": bg.delta_x, "y": bg.delta_y},
                "tile": {"x": int(bg.tile_x), "y": int(bg.tile_y)},
                "action_offset": {"x": int(offset_x), "y": int(offset_y)},
                "axis": {"x": int(asset.axis_x), "y": int(asset.axis_y)},
                "sprite_size": {"w": int(asset.width), "h": int(asset.height)},
                "origin": {"x": int(origin_x), "y": int(origin_y)},
                "palette_index0_rgb": list(asset.palette_index0_rgb),
                "placements": placements,
            }
        )

    if not placement_report:
        raise RuntimeError("nenhuma camada encontrada para compor")

    return base, placement_report


def _write_viewport_previews(root: Path, frames: list[Path], geometry: WorldGeometry) -> list[dict]:
    preview_dir = root / "work" / "reconstructed_viewports"
    preview_dir.mkdir(parents=True, exist_ok=True)
    keyframes = [
        ("viewer_default", geometry.viewer_default_x, geometry.viewer_default_y),
        ("top_left", geometry.camera_min_x, geometry.camera_min_y),
        ("top_right", geometry.camera_max_x, geometry.camera_min_y),
        ("bottom_right", geometry.camera_max_x, geometry.camera_max_y),
        ("bottom_left", geometry.camera_min_x, geometry.camera_max_y),
        ("mugen_start", geometry.camera_start_scroll_x, geometry.camera_start_scroll_y),
    ]

    previews: list[dict] = []
    with Image.open(frames[0]) as src:
        rgb = src.convert("RGB")
        for name, x, y in keyframes:
            out = preview_dir / f"frame_0000_{name}.png"
            rgb.crop((x, y, x + VIEWPORT_W, y + VIEWPORT_H)).save(out)
            gate = assert_frame_integrity(out, expected_width=VIEWPORT_W, expected_height=VIEWPORT_H)
            gate["path"] = _rel(out)
            previews.append({"name": name, "camera_x": int(x), "camera_y": int(y), "path": _rel(out), "visual_integrity": gate})
    return previews


def main() -> int:
    root = ROOT
    sff_path = ROOT / "rascunho" / "inputs" / "showdown.sff"
    def_path = ROOT / "rascunho" / "inputs" / "showdown.def"

    extracted_dir = root / "work" / "extracted_pcx"
    extract_sff_v1_pcx(sff_path, extracted_dir)
    catalog = load_sprite_catalog(sff_path, extracted_dir)

    stage = parse_stage_def(def_path)
    geometry = compute_world_geometry(stage)
    frames_dir = root / "work" / "reconstructed_layers"
    frames_dir.mkdir(parents=True, exist_ok=True)

    action = stage.actions.get(2, [])
    bg2_frames = list(action) if action else [None]

    written: list[str] = []
    written_paths: list[Path] = []
    frame_reports: list[dict] = []
    for idx, bg2 in enumerate(bg2_frames):
        frame, placements = composite_world_frame(stage, geometry, catalog, bg2)
        out = frames_dir / f"frame_{idx:04d}.png"
        frame.convert("RGB").save(out)
        integrity = assert_frame_integrity(
            out,
            matte_colors=[asset.palette_index0_rgb for asset in catalog.values()],
            expected_width=geometry.width,
            expected_height=geometry.height,
        )
        integrity["path"] = _rel(out)
        written.append(_rel(out))
        written_paths.append(out)
        frame_reports.append(
            {
                "frame": _rel(out),
                "bg2_frame": None
                if bg2 is None
                else {"group": bg2.group, "index": bg2.index, "offset_x": bg2.offset_x, "offset_y": bg2.offset_y},
                "placements": placements,
                "visual_integrity": integrity,
            }
        )

    viewport_previews = _write_viewport_previews(root, written_paths, geometry)

    report = {
        "schema_version": "1.1.0",
        "source": {
            "sff": _rel(sff_path),
            "def": _rel(def_path),
        },
        "frames": written,
        "frame_count": len(written),
        "viewport": {"w": VIEWPORT_W, "h": VIEWPORT_H},
        "world": {
            "w": geometry.width,
            "h": geometry.height,
            "tiles_w": geometry.tiles_w,
            "tiles_h": geometry.tiles_h,
        },
        "mugen_logical_view": {"w": VIEWPORT_W, "h": MUGEN_VIEW_H},
        "zoffset": stage.zoffset,
        "camera": {
            "mugen_start": {"x": stage.camera_startx, "y": stage.camera_starty},
            "mugen_bounds": {
                "left": stage.camera_boundleft,
                "right": stage.camera_boundright,
                "high": stage.camera_boundhigh,
                "low": stage.camera_boundlow,
            },
            "scroll_bounds_px": {
                "min_x": geometry.camera_min_x,
                "max_x": geometry.camera_max_x,
                "min_y": geometry.camera_min_y,
                "max_y": geometry.camera_max_y,
            },
            "mugen_start_scroll_px": {
                "x": geometry.camera_start_scroll_x,
                "y": geometry.camera_start_scroll_y,
            },
            "viewer_default_scroll_px": {
                "x": geometry.viewer_default_x,
                "y": geometry.viewer_default_y,
            },
            "verticalfollow": stage.verticalfollow,
        },
        "composition_contract": {
            "alpha_rule": "mask=1 converts PCX palette index 0 to RGBA alpha 0 before paste; unmistakable magenta index0 matte is also inferred as transparent and reported",
            "world_extent_rule": "world size is viewport plus MUGEN camera bounds, rounded to 8px tiles; no downscale is applied",
            "x_rule": "world_center + bg.start.x + action.offset.x - sff.axis_x",
            "y_rule": "world_h - (mugen_view_h - bg.start.y) + action.offset.y - sff.axis_y",
            "z_order": "BG sections are composited in DEF order from low id/background to high id/foreground",
            "tiling": "tile x/y repeats the source sprite until the world canvas is covered",
            "sky_fill": "empty camera-bounds space is filled with an MD-friendly sky ramp before layer paste, avoiding black or transparent voids",
            "known_limit": "This training pass exports a flat world tilemap. Exact MUGEN multi-delta parallax remains a future curation/runtime route.",
            "visual_gate": "world and viewport previews abort if transparent or matte/magenta pixels exceed 5 percent",
        },
        "layers": [
            {
                "id": bg.id,
                "kind": bg.kind,
                "sprite": None
                if bg.sprite_group is None or bg.sprite_index is None
                else {"group": bg.sprite_group, "index": bg.sprite_index},
                "actionno": bg.actionno,
                "mask": bg.mask,
                "start": {"x": bg.start_x, "y": bg.start_y},
                "delta": {"x": bg.delta_x, "y": bg.delta_y},
                "tile": {"x": bg.tile_x, "y": bg.tile_y},
            }
            for bg in stage.bgs
        ],
        "actions": {
            str(action_id): [
                {
                    "group": frame.group,
                    "index": frame.index,
                    "offset_x": frame.offset_x,
                    "offset_y": frame.offset_y,
                    "time": frame.time,
                }
                for frame in frames
            ]
            for action_id, frames in stage.actions.items()
        },
        "viewport_previews": viewport_previews,
        "frames_detail": frame_reports,
    }
    (root / "analysis").mkdir(parents=True, exist_ok=True)
    (root / "analysis" / "reconstruction.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

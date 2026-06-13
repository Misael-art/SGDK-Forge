from __future__ import annotations

import argparse
import json
import math
import struct
import zlib
from pathlib import Path

from PIL import Image


CELL_W = 48
CELL_H = 64
PIVOT = (24, 58)
VISUAL_STATUS = "rejected_visual_placeholder"
VISUAL_REJECTION_REASON = (
    "v002 is retained only as a technical lab artifact. Human review rejected it "
    "for semantic visual failures: source/model-sheet anatomy gate failed, facial "
    "acting is static, and runtime 48x64 fidelity loses the eyes, lava arm, shorts "
    "and warm material contrast."
)

PAL2 = [
    (238, 0, 238),   # 0 transparent
    (34, 34, 68),    # 1 outline
    (34, 34, 102),   # 2 deep shadow
    (68, 68, 102),   # 3 stone shadow
    (102, 102, 136), # 4 stone base
    (136, 136, 170), # 5 stone light
    (170, 170, 238), # 6 stone highlight
    (102, 68, 34),   # 7 skin shadow
    (136, 102, 68),  # 8 skin base
    (170, 136, 102), # 9 skin light
    (68, 68, 68),    # 10 wrap shadow
    (102, 102, 102), # 11 wrap base
    (136, 136, 136), # 12 wrap light
    (170, 34, 34),   # 13 shorts/accent
    (204, 204, 204), # 14 cloth highlight
    (238, 238, 238), # 15 eye/spec
]

PAL3 = [
    (238, 0, 238),   # 0 transparent
    (34, 34, 34),    # 1 outline
    (170, 34, 0),    # 2 flame deep
    (238, 102, 0),   # 3 flame mid
    (238, 238, 0),   # 4 flame hot
    (238, 238, 238), # 5 flame white
    (0, 204, 238),   # 6 cool crack
    (0, 238, 238),   # 7 cool white
    (238, 0, 170),   # 8 scar magenta
    (68, 68, 68),    # 9 smoke dark
    (102, 102, 102), # 10 smoke mid
    (136, 136, 136), # 11 smoke light
    (0, 0, 0),
    (34, 34, 68),
    (68, 68, 102),
    (170, 170, 238),
]


def indexed_canvas(w: int, h: int, palette: list[tuple[int, int, int]]) -> Image.Image:
    img = Image.new("P", (w, h), 0)
    raw: list[int] = []
    for r, g, b in palette:
        raw.extend([r, g, b])
    while len(raw) < 256 * 3:
        raw.extend([0, 0, 0])
    img.putpalette(raw)
    return img


def put(img: Image.Image, x: int, y: int, c: int) -> None:
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)


def rect(img: Image.Image, x0: int, y0: int, x1: int, y1: int, c: int) -> None:
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(img, x, y, c)


def ellipse(img: Image.Image, cx: int, cy: int, rx: int, ry: int, c: int) -> None:
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            dx = (x - cx) / max(1, rx)
            dy = (y - cy) / max(1, ry)
            if dx * dx + dy * dy <= 1.0:
                put(img, x, y, c)


def poly(img: Image.Image, pts: list[tuple[int, int]], c: int) -> None:
    min_y = min(y for _, y in pts)
    max_y = max(y for _, y in pts)
    for y in range(min_y, max_y + 1):
        xs: list[float] = []
        for i, (x0, y0) in enumerate(pts):
            x1, y1 = pts[(i + 1) % len(pts)]
            if y0 == y1:
                continue
            if (y >= min(y0, y1)) and (y < max(y0, y1)):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs), 2):
            if i + 1 >= len(xs):
                break
            for x in range(math.ceil(xs[i]), math.floor(xs[i + 1]) + 1):
                put(img, x, y, c)


def line(img: Image.Image, a: tuple[int, int], b: tuple[int, int], c: int, thickness: int = 1) -> None:
    x0, y0 = a
    x1, y1 = b
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        x = round(x0 + (x1 - x0) * i / steps)
        y = round(y0 + (y1 - y0) * i / steps)
        for oy in range(-thickness, thickness + 1):
            for ox in range(-thickness, thickness + 1):
                if ox * ox + oy * oy <= thickness * thickness:
                    put(img, x + ox, y + oy, c)


def limb(img: Image.Image, a: tuple[int, int], b: tuple[int, int], c: int, thickness: int) -> None:
    line(img, a, b, c, thickness)
    ellipse(img, a[0], a[1], thickness, thickness, c)
    ellipse(img, b[0], b[1], thickness, thickness, c)


def outline(img: Image.Image, c: int = 1) -> None:
    src = img.copy()
    px = src.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y] != 0:
                continue
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + ox, y + oy
                if 0 <= nx < img.width and 0 <= ny < img.height and px[nx, ny] != 0:
                    img.putpixel((x, y), c)
                    break


def draw_body(pose: dict) -> Image.Image:
    img = indexed_canvas(CELL_W, CELL_H, PAL2)
    dx = int(pose.get("dx", 0))
    bob = int(pose.get("bob", 0))
    lean = int(pose.get("lean", 0))
    torso = [(18 + dx + lean, 18 + bob), (32 + dx + lean, 20 + bob), (35 + dx, 41 + bob), (29 + dx, 51 + bob), (18 + dx, 49 + bob), (13 + dx, 35 + bob)]
    poly(img, torso, 4)
    poly(img, [(16 + dx + lean, 20 + bob), (24 + dx + lean, 19 + bob), (23 + dx, 48 + bob), (16 + dx, 46 + bob)], 3)
    poly(img, [(25 + dx + lean, 20 + bob), (32 + dx + lean, 22 + bob), (32 + dx, 39 + bob), (24 + dx, 48 + bob)], 5)
    ellipse(img, 25 + dx + lean, 12 + bob, 6, 7, 8)
    rect(img, 22 + dx + lean, 17 + bob, 27 + dx + lean, 21 + bob, 7)
    put(img, 28 + dx + lean, 11 + bob, 15)
    rect(img, 16 + dx, 39 + bob, 33 + dx, 50 + bob, 13)
    rect(img, 17 + dx, 42 + bob, 32 + dx, 45 + bob, 10)
    rect(img, 20 + dx, 43 + bob, 29 + dx, 45 + bob, 12)

    arms = pose["arms"]
    for shoulder, elbow, hand, stone_color in arms:
        limb(img, (shoulder[0] + dx + lean, shoulder[1] + bob), (elbow[0] + dx, elbow[1] + bob), stone_color, 3)
        limb(img, (elbow[0] + dx, elbow[1] + bob), (hand[0] + dx, hand[1] + bob), max(3, stone_color - 1), 3)
        rect(img, hand[0] + dx - 3, hand[1] + bob - 2, hand[0] + dx + 4, hand[1] + bob + 3, 11)
        line(img, (hand[0] + dx - 3, hand[1] + bob), (hand[0] + dx + 4, hand[1] + bob + 2), 12, 1)

    for hip, knee, foot, shade in pose["legs"]:
        limb(img, (hip[0] + dx, hip[1] + bob), (knee[0] + dx, knee[1] + bob), shade, 4)
        limb(img, (knee[0] + dx, knee[1] + bob), (foot[0] + dx, foot[1] + bob), max(3, shade - 1), 4)
        rect(img, foot[0] + dx - 5, foot[1] + bob - 1, foot[0] + dx + 5, foot[1] + bob + 2, 10)

    # Hard pixel material details: cracks, scars and wraps, not random noise.
    line(img, (19 + dx, 26 + bob), (24 + dx, 30 + bob), 2)
    line(img, (24 + dx, 30 + bob), (21 + dx, 35 + bob), 6)
    line(img, (30 + dx, 25 + bob), (27 + dx, 34 + bob), 6)
    line(img, (18 + dx, 33 + bob), (15 + dx, 38 + bob), 2)
    put(img, 23 + dx, 25 + bob, 14)
    put(img, 24 + dx, 26 + bob, 14)
    outline(img)
    return img


def draw_fx(pose: dict) -> Image.Image:
    img = indexed_canvas(CELL_W, CELL_H, PAL3)
    dx = int(pose.get("dx", 0))
    bob = int(pose.get("bob", 0))
    for x, y in pose.get("cracks", []):
        put(img, x + dx, y + bob, 8)
        put(img, x + dx + 1, y + bob + 1, 3)
    for hx, hy, power in pose.get("flames", []):
        poly(img, [(hx + dx - 4, hy + bob + 2), (hx + dx, hy + bob - 9 - power), (hx + dx + 4, hy + bob + 2), (hx + dx, hy + bob)], 3)
        poly(img, [(hx + dx - 2, hy + bob), (hx + dx, hy + bob - 5 - power), (hx + dx + 2, hy + bob), (hx + dx, hy + bob + 1)], 4)
        put(img, hx + dx, hy + bob - 3 - power, 5)
    if pose.get("impact"):
        cx, cy = pose["impact"]
        for a, b in [((-6, 0), (6, 0)), ((0, -5), (0, 5)), ((-4, -3), (4, 3)), ((-4, 3), (4, -3))]:
            line(img, (cx + dx + a[0], cy + bob + a[1]), (cx + dx + b[0], cy + bob + b[1]), 4, 1)
    outline(img)
    return img


def pose_idle(i: int) -> dict:
    bob = 1 if i in (2, 3, 6, 7) else 0
    guard_shift = 1 if i in (1, 2, 5, 6) else 0
    return {
        "bob": bob,
        "lean": 0,
        "arms": [
            ((17, 23), (13, 33 + guard_shift), (16, 42), 4),
            ((31, 23), (36, 32 - guard_shift), (34, 42), 5),
        ],
        "legs": [
            ((20, 47), (16, 51), (14, 51), 4),
            ((29, 48), (34, 51), (37, 51), 5),
        ],
        "cracks": [(23, 28), (29, 29)],
        "flames": [(16, 42, 0)] if i in (2, 6) else [],
    }


def pose_walk(i: int) -> dict:
    phase = i % 6
    front = phase in (1, 2, 3)
    return {
        "dx": -1 if phase in (1, 2) else 1 if phase in (4, 5) else 0,
        "bob": 1 if phase in (1, 4) else 0,
        "lean": 1 if front else 0,
        "arms": [
            ((17, 23), (14 if front else 18, 32), (18 if front else 13, 42), 4),
            ((31, 23), (34 if front else 37, 31), (32 if front else 37, 41), 5),
        ],
        "legs": [
            ((20, 47), (14 if front else 22, 51), (11 if front else 22, 51), 4),
            ((29, 48), (33 if front else 27, 51), (38 if front else 29, 51), 5),
        ],
        "cracks": [(23, 28), (29, 29)],
        "flames": [],
    }


def pose_teep(i: int) -> dict:
    table = [
        (0, 0, 0, False),
        (-1, 1, -1, False),
        (-1, 2, -2, False),
        (0, 0, -2, True),
        (1, -1, -1, True),
        (0, 1, 0, False),
    ]
    dx, lean, bob, active = table[i]
    foot_x = 39 if active else 36 if i == 2 else 32
    knee_x = 33 if active else 31 if i == 2 else 29
    return {
        "dx": dx,
        "bob": bob,
        "lean": lean,
        "arms": [
            ((17, 23), (13, 31), (15, 39), 4),
            ((31, 23), (34, 30), (32, 38), 5),
        ],
        "legs": [
            ((20, 47), (15, 51), (13, 51), 4),
            ((29, 48), (knee_x, 48 if active else 51), (foot_x, 47 if active else 51), 5),
        ],
        "cracks": [(23, 28), (29, 29)],
        "flames": [(foot_x, 47 if active else 58, 1)] if active else [],
        "impact": (35, 47) if active and i == 4 else None,
    }


def strip(action: str, poses: list[dict], fx: bool = False) -> Image.Image:
    pal = PAL3 if fx else PAL2
    out = indexed_canvas(CELL_W * len(poses), CELL_H, pal)
    for i, p in enumerate(poses):
        frame = draw_fx(p) if fx else draw_body(p)
        out.paste(frame, (i * CELL_W, 0))
    return out


def trim_plte(path: Path, max_entries: int = 16) -> None:
    data = path.read_bytes()
    out = bytearray(data[:8])
    i = 8
    while i + 8 <= len(data):
        length = struct.unpack(">I", data[i:i + 4])[0]
        ctype = data[i + 4:i + 8]
        chunk = data[i + 8:i + 8 + length]
        crc = data[i + 8 + length:i + 12 + length]
        i += 12 + length
        if ctype == b"PLTE":
            chunk = chunk[:max_entries * 3]
            out += struct.pack(">I", len(chunk)) + ctype + chunk
            out += struct.pack(">I", zlib.crc32(chunk, zlib.crc32(ctype)) & 0xFFFFFFFF)
        else:
            out += struct.pack(">I", len(chunk)) + ctype + chunk + crc
        if ctype == b"IEND":
            break
    path.write_bytes(bytes(out))


def save(path: Path, img: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=False)
    trim_plte(path)


def bbox_for_frame(img: Image.Image, frame_index: int) -> dict:
    crop = img.crop((frame_index * CELL_W, 0, (frame_index + 1) * CELL_W, CELL_H))
    xs: list[int] = []
    ys: list[int] = []
    for y in range(CELL_H):
        for x in range(CELL_W):
            if crop.getpixel((x, y)) != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return {"empty": True}
    return {"x": min(xs), "y": min(ys), "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1}


def palette_report(path: Path) -> dict:
    data = path.read_bytes()
    plte_entries = 0
    i = 8
    while i + 8 <= len(data):
        length = struct.unpack(">I", data[i:i + 4])[0]
        ctype = data[i + 4:i + 8]
        if ctype == b"PLTE":
            plte_entries = length // 3
            break
        i += 12 + length
    img = Image.open(path)
    colors = sorted(set(img.getdata()))
    return {
        "path": str(path),
        "mode": img.mode,
        "size": list(img.size),
        "plte_entries": plte_entries,
        "visible_indices": [c for c in colors if c != 0],
        "index0_transparent_contract": True,
        "grid_9bit": True,
        "dim_multiple_8": img.width % 8 == 0 and img.height % 8 == 0,
    }


def contact_sheet(project: Path, actions: dict[str, list[dict]]) -> None:
    sheet = indexed_canvas(CELL_W * 8, CELL_H * len(actions), PAL2)
    for row, poses in enumerate(actions.values()):
        for i, p in enumerate(poses):
            sheet.paste(draw_body(p), (i * CELL_W, row * CELL_H))
    save(project / "data/processed/model_sheets/hibrido_fighter_model_sheet_48x64_v002.png", sheet)


def pivot_overlay(project: Path, action: str, poses: list[dict]) -> None:
    img = indexed_canvas(CELL_W * len(poses), CELL_H, PAL2)
    for i, p in enumerate(poses):
        frame = draw_body(p)
        x0 = i * CELL_W
        img.paste(frame, (x0, 0))
        line(img, (x0 + PIVOT[0] - 4, PIVOT[1]), (x0 + PIVOT[0] + 4, PIVOT[1]), 15, 1)
        line(img, (x0 + PIVOT[0], PIVOT[1] - 4), (x0 + PIVOT[0], PIVOT[1] + 4), 15, 1)
        line(img, (x0, PIVOT[1]), (x0 + CELL_W - 1, PIVOT[1]), 10, 1)
    save(project / f"data/processed/reports/hibrido_{action}_pivot_overlay_v002.png", img)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate rejected v002 technical lab sprites. Not final art."
    )
    parser.add_argument(
        "--allow-rejected-lab-output",
        action="store_true",
        help="Explicitly acknowledge that generated assets are debug placeholders, not final art.",
    )
    args = parser.parse_args()
    if not args.allow_rejected_lab_output:
        raise SystemExit(
            "Blocked: hibrido v002 is visually rejected. Use --allow-rejected-lab-output "
            "only to reproduce the failed technical lab artifact."
        )

    project = Path(__file__).resolve().parents[2]
    actions = {
        "idle": [pose_idle(i) for i in range(8)],
        "walk_step": [pose_walk(i) for i in range(6)],
        "teep": [pose_teep(i) for i in range(6)],
    }
    out_dir = project / "res/sprites/hibrido"
    reports: dict[str, object] = {
        "schema_version": "1.0.0",
        "asset_id": "hibrido_fighter_runtime_v002",
        "visual_status": VISUAL_STATUS,
        "not_final_art": True,
        "technical_lab_asset": True,
        "rejection_reason": VISUAL_REJECTION_REASON,
        "cell_px": [CELL_W, CELL_H],
        "pivot_px": list(PIVOT),
        "actions": {},
    }
    for action, poses in actions.items():
        body = strip(action, poses, fx=False)
        fx = strip(action, poses, fx=True)
        body_path = out_dir / f"hibrido_{action}_body_48x64_strip_v002.png"
        fx_path = out_dir / f"hibrido_{action}_fx_48x64_strip_v002.png"
        save(body_path, body)
        save(fx_path, fx)
        frames = []
        for idx in range(len(poses)):
            frames.append({
                "frame_index": idx,
                "pivot_px": list(PIVOT),
                "bbox_body": bbox_for_frame(body, idx),
                "bbox_fx": bbox_for_frame(fx, idx),
                "foot_contact_y": PIVOT[1],
            })
        reports["actions"][action] = {
            "frames": len(poses),
            "body_strip": str(body_path.relative_to(project)).replace("\\", "/"),
            "fx_strip": str(fx_path.relative_to(project)).replace("\\", "/"),
            "frame_delta_report": frames,
            "motion_phase_map": ["startup" if action == "teep" and i < 3 else "active" if action == "teep" and i in (3, 4) else "recovery" if action == "teep" else "loop" for i in range(len(poses))],
        }
        pivot_overlay(project, action, poses)

    contact_sheet(project, actions)
    report_dir = project / "out/logs"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "hibrido_v002_animation_report.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    compliance = [palette_report(path) for path in sorted(out_dir.glob("*_v002.png"))]
    (report_dir / "hibrido_v002_pixel_compliance_report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "asset_id": "hibrido_fighter_runtime_v002",
                "visual_status": VISUAL_STATUS,
                "not_final_art": True,
                "technical_lab_asset": True,
                "assets": compliance,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (project / "data/processed/reports/hibrido_v002_motion_phase_map.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

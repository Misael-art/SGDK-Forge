#!/usr/bin/env python3
"""Build the native 64x64 active key pose for TAÍNA's combo jab.

This is a deterministic native-grid redraw.  It deliberately reuses the
approved idle v02 head, palette and grounded lower-body topology; only the
upper-body clusters required by the jab are redrawn.
"""

from pathlib import Path

from PIL import Image, ImageDraw


PROJECT = Path(__file__).resolve().parents[2]
IDLE = (
    PROJECT
    / "rascunho/taina_idle_guard_v02/"
    "taina_idle_guard_key_pose_clean_48x64_v02.png"
)
OUT_DIR = PROJECT / "rascunho/taina_combo_hit_1_jab_v01"
REVIEW_DIR = PROJECT / "doc/art/characters/taina/review"

NATIVE = OUT_DIR / "taina_combo_hit_1_jab_active_key_pose_64x64_v01.png"
ZOOM = OUT_DIR / "taina_combo_hit_1_jab_active_key_pose_64x64_v01_12x.png"
SILHOUETTE = OUT_DIR / "taina_combo_hit_1_jab_active_silhouette_64x64_v01.png"
BOARD = REVIEW_DIR / "taina_idle_v02_jab_native_active_compare_v01.png"
GAMEPLAY = REVIEW_DIR / "taina_combo_hit_1_jab_native_gameplay_context_v01.png"


def polygon(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: int) -> None:
    draw.polygon(points, fill=fill)


def rectangle(
    draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: int
) -> None:
    draw.rectangle(box, fill=fill)


def build_native() -> Image.Image:
    idle = Image.open(IDLE)
    if idle.mode != "P" or idle.size != (48, 64):
        raise RuntimeError("Approved idle source must remain indexed 48x64.")

    palette = idle.getpalette()
    frame = Image.new("P", (64, 64), 0)
    frame.putpalette(palette)
    frame.info["transparency"] = 0

    # Preserve the approved source at its exact coordinates.  The active pose
    # is a controlled cluster edit: remove only the original lead arm and
    # rebuild shoulder-to-fist topology without rescaling the body.
    frame.paste(idle, (0, 0))
    d = ImageDraw.Draw(frame)

    # Remove the old lead forearm/fist while retaining the approved chest,
    # neck, head, sash and both grounded legs.
    rectangle(d, (34, 12, 47, 25), 0)

    # Re-establish the front edge of the orange torso after the surgical erase.
    polygon(d, [(30, 14), (34, 15), (36, 19), (35, 24), (32, 27),
                (29, 26), (30, 20)], 1)
    polygon(d, [(31, 15), (33, 16), (35, 19), (34, 23), (32, 25),
                (30, 24), (31, 19)], 7)
    polygon(d, [(32, 16), (34, 18), (34, 21), (32, 22)], 9)

    # Lead shoulder and direct jab.  The arm tapers from a protected chin to
    # a compact wrapped fist and remains connected in every row.
    polygon(d, [(28, 13), (33, 13), (37, 15), (42, 16), (51, 16),
                (53, 15), (57, 16), (59, 18), (59, 21), (57, 23),
                (53, 23), (50, 21), (41, 21), (36, 20), (31, 18),
                (28, 17)], 1)
    polygon(d, [(30, 14), (33, 14), (37, 16), (42, 17), (50, 17),
                (51, 20), (42, 20), (37, 19), (32, 17), (29, 16)], 7)
    polygon(d, [(34, 15), (38, 17), (49, 18), (49, 20), (41, 19),
                (36, 18)], 8)
    rectangle(d, (40, 17, 48, 17), 9)

    # Compact wrapped fist, seven pixels of core mass rather than an oversized
    # glove.  Warm knuckle highlight keeps the contact endpoint readable.
    polygon(d, [(53, 15), (57, 16), (59, 18), (59, 21), (57, 23),
                (53, 23), (50, 20), (51, 17)], 1)
    polygon(d, [(53, 16), (56, 17), (58, 18), (58, 20), (56, 22),
                (53, 22), (51, 20), (52, 17)], 5)
    rectangle(d, (53, 16, 56, 17), 9)
    rectangle(d, (52, 18, 53, 20), 4)
    rectangle(d, (57, 19, 58, 20), 2)

    # Shoulder cap overlaps the jaw and makes the defensive intent explicit.
    polygon(d, [(27, 13), (31, 13), (33, 15), (32, 18), (29, 18),
                (27, 16)], 1)
    polygon(d, [(28, 14), (30, 14), (32, 15), (31, 17), (29, 17),
                (28, 16)], 8)
    polygon(d, [(32, 16), (36, 16), (39, 18), (37, 20), (33, 19)], 7)
    rectangle(d, (33, 16, 35, 17), 9)

    return frame


def save_indexed(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=False, bits=4, transparency=0)


def make_silhouette(native: Image.Image) -> Image.Image:
    out = Image.new("P", native.size, 0)
    out.putpalette(native.getpalette())
    out.info["transparency"] = 0
    src = native.load()
    dst = out.load()
    for y in range(native.height):
        for x in range(native.width):
            if src[x, y] != 0:
                dst[x, y] = 1
    return out


def make_review_board(native: Image.Image, idle: Image.Image) -> None:
    scale = 8
    bg = (10, 18, 34)
    panel = Image.new("RGB", (640, 224), bg)
    idle_rgba = idle.convert("RGBA")
    native_rgba = native.convert("RGBA")
    idle_mask = Image.new("L", idle.size)
    idle_mask.putdata([0 if value == 0 else 255 for value in idle.getdata()])
    native_mask = Image.new("L", native.size)
    native_mask.putdata([0 if value == 0 else 255 for value in native.getdata()])
    idle_rgba.putalpha(idle_mask)
    native_rgba.putalpha(native_mask)
    idle_zoom = idle_rgba.resize((48 * scale, 64 * scale), Image.Resampling.NEAREST)
    jab_zoom = native_rgba.resize((64 * scale, 64 * scale), Image.Resampling.NEAREST)
    # Crop around the figures to keep the board at 224px high.
    idle_crop = idle_zoom.crop((96, 0, 320, 512)).resize(
        (98, 224), Image.Resampling.NEAREST
    )
    jab_crop = jab_zoom.crop((104, 0, 504, 512)).resize(
        (175, 224), Image.Resampling.NEAREST
    )
    panel.paste(idle_crop, (55, 0), idle_crop)
    panel.paste(jab_crop, (280, 0), jab_crop)
    panel.save(BOARD)


def make_gameplay_context(native: Image.Image) -> None:
    scene = Image.new("RGB", (320, 224), (12, 34, 48))
    d = ImageDraw.Draw(scene)
    d.rectangle((0, 160, 319, 223), fill=(32, 48, 58))
    d.rectangle((0, 177, 319, 180), fill=(68, 102, 102))
    d.rectangle((0, 181, 319, 182), fill=(12, 18, 34))
    sprite = native.convert("RGBA")
    mask = Image.new("L", native.size)
    mask.putdata([0 if value == 0 else 255 for value in native.getdata()])
    sprite.putalpha(mask)
    scene.paste(sprite, (112, 101), sprite)
    scene.save(GAMEPLAY)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    idle = Image.open(IDLE)
    native = build_native()
    save_indexed(native, NATIVE)
    native.resize((768, 768), Image.Resampling.NEAREST).save(ZOOM)
    save_indexed(make_silhouette(native), SILHOUETTE)
    make_review_board(native, idle)
    make_gameplay_context(native)
    print(NATIVE)
    print(ZOOM)
    print(SILHOUETTE)
    print(BOARD)
    print(GAMEPLAY)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build P1 assets A2-E3 from the approved R1/R2 visual direction.

This is native-grid raster authoring: every primitive lands directly on the
final pixel grid, every palette entry is on the project RGB333 lattice, and no
resampling/anti-aliasing is used.  A1 is intentionally owned by
``build_p1_kirby.py`` because it has the stricter animation artifact gate.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
P1 = ROOT / "data" / "source_art" / "p1"
KEY = (255, 0, 255)
LEGAL = {0, 36, 73, 109, 146, 182, 219, 255}


PAL2 = {
    0: KEY, 1: (255, 219, 255), 2: (255, 182, 219), 3: (255, 146, 182),
    4: (219, 73, 146), 5: (146, 36, 109), 6: (109, 36, 73),
    7: (219, 73, 73), 8: (146, 36, 36), 9: (36, 36, 73),
    10: (255, 255, 255), 11: (182, 146, 219), 12: (109, 73, 182),
    13: (73, 73, 146), 14: (36, 36, 73), 15: (219, 182, 73),
}


def make_image(size: tuple[int, int], colours: dict[int, tuple[int, int, int]]) -> Image.Image:
    for colour in colours.values():
        assert all(channel in LEGAL for channel in colour), colour
    image = Image.new("P", size, 0)
    palette: list[int] = []
    for index in range(256):
        palette.extend(colours.get(index, (0, 0, 0)))
    image.putpalette(palette)
    return image


def save(asset_id: str, filename: str, image: Image.Image) -> None:
    folder = P1 / asset_id
    folder.mkdir(parents=True, exist_ok=True)
    image.save(folder / filename, optimize=False)


def repeat_x(tile: Image.Image, count: int) -> Image.Image:
    out = make_image((tile.width * count, tile.height), palette_dict(tile))
    for index in range(count):
        out.paste(tile, (index * tile.width, 0))
    return out


def palette_dict(image: Image.Image) -> dict[int, tuple[int, int, int]]:
    raw = image.getpalette()
    return {index: tuple(raw[index * 3:index * 3 + 3]) for index in range(16)}


def lock_horizontal_seam(tile: Image.Image) -> None:
    for y in range(tile.height):
        tile.putpixel((tile.width - 1, y), tile.getpixel((0, y)))


def outline_mask(image: Image.Image, mask: Image.Image, fill: int, outline: int) -> None:
    src = mask.load()
    dilation = Image.new("1", mask.size, 0)
    dst = dilation.load()
    for y in range(mask.height):
        for x in range(mask.width):
            if not src[x, y]:
                continue
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < mask.width and 0 <= ny < mask.height:
                        dst[nx, ny] = 1
    image.paste(outline, mask=dilation)
    image.paste(fill, mask=mask)


def draw_a2() -> Image.Image:
    image = make_image((32, 16), PAL2)
    for frame in range(2):
        ox = frame * 16
        mask = Image.new("1", (16, 16), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse((3, 2, 12, 12), fill=1)
        md.ellipse((1 if frame == 0 else 3, 10, 7 if frame == 0 else 9, 14), fill=1)
        md.ellipse((9 if frame == 0 else 7, 10, 14 if frame == 0 else 13, 14), fill=1)
        cell = make_image((16, 16), PAL2)
        outline_mask(cell, mask, 11, 14)
        d = ImageDraw.Draw(cell)
        d.rectangle((5, 8, 11, 11), fill=12)
        d.rectangle((5, 5, 6, 7), fill=9)
        d.rectangle((9, 5, 10, 7), fill=9)
        d.point((5, 5), fill=10)
        d.point((9, 5), fill=10)
        d.point((8, 9), fill=15)
        # Restore feet after the body shadow so both steps remain readable.
        d.rectangle((2 if frame == 0 else 4, 12, 6 if frame == 0 else 8, 13), fill=13)
        d.rectangle((10 if frame == 0 else 8, 12, 13 if frame == 0 else 12, 13), fill=13)
        image.paste(cell, (ox, 0))
    return image


def draw_a3() -> Image.Image:
    image = make_image((24, 8), PAL2)
    d = ImageDraw.Draw(image)
    shapes = [
        [(4, 0), (5, 3), (7, 4), (5, 5), (4, 7), (3, 5), (1, 4), (3, 3)],
        [(12, 1), (13, 3), (15, 4), (13, 5), (12, 7), (11, 5), (9, 4), (11, 3)],
        [(20, 2), (21, 4), (20, 6), (19, 4)],
    ]
    for index, points in enumerate(shapes):
        d.polygon(points, fill=1)
        if index < 2:
            cx = 4 + index * 8
            d.point((cx, 4), fill=10)
            d.point((cx - 1, 4), fill=15)
    return image


PAL0_CLOUD = {
    0: KEY, 1: (255, 255, 255), 2: (255, 255, 219),
    3: (255, 219, 255), 4: (219, 219, 219), 5: (182, 219, 219),
}


def cloud(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int) -> None:
    draw.ellipse((x, y + scale, x + scale * 4, y + scale * 3), fill=4)
    draw.ellipse((x + scale, y, x + scale * 3, y + scale * 3), fill=2)
    draw.ellipse((x + scale * 2, y + scale // 2, x + scale * 5, y + scale * 3), fill=1)
    draw.rectangle((x + scale, y + scale * 2, x + scale * 5, y + scale * 3), fill=3)
    draw.rectangle((x + scale * 2, y + scale * 2, x + scale * 4, y + scale * 2), fill=1)


def draw_b1() -> Image.Image:
    image = make_image((512, 80), PAL0_CLOUD)
    d = ImageDraw.Draw(image)
    for args in ((17, 13, 7), (96, 45, 4), (151, 8, 5), (238, 36, 6), (337, 15, 8), (447, 48, 4)):
        cloud(d, *args)
    # Small detached wisps create depth without a mechanically repeated tile.
    d.ellipse((73, 25, 88, 32), fill=4)
    d.rectangle((77, 25, 91, 29), fill=3)
    d.ellipse((407, 8, 429, 17), fill=2)
    d.rectangle((411, 12, 433, 17), fill=3)
    for y in range(image.height):
        image.putpixel((511, y), image.getpixel((0, y)))
    return image


PAL0_MOUNT = {
    0: KEY, 1: (73, 109, 109), 2: (109, 146, 146),
    3: (146, 146, 182), 4: (182, 182, 219),
}


def draw_b2() -> Image.Image:
    image = make_image((512, 56), PAL0_MOUNT)
    d = ImageDraw.Draw(image)
    back = [(0, 39), (28, 31), (52, 17), (76, 34), (111, 23), (139, 37), (176, 12), (208, 35), (241, 27), (274, 39), (314, 20), (346, 32), (379, 15), (410, 34), (451, 24), (481, 35), (511, 39), (511, 55), (0, 55)]
    middle = [(0, 44), (45, 32), (83, 46), (126, 29), (167, 47), (215, 25), (257, 45), (304, 31), (350, 47), (399, 28), (446, 44), (480, 33), (511, 44), (511, 55), (0, 55)]
    front = [(0, 50), (57, 42), (99, 52), (151, 38), (197, 52), (251, 39), (301, 52), (354, 40), (407, 52), (464, 41), (511, 50), (511, 55), (0, 55)]
    d.polygon(back, fill=3)
    d.polygon(middle, fill=2)
    d.polygon(front, fill=1)
    d.line(back[:-2], fill=4, width=1)
    # Sparse snow/light facets follow only the tallest peaks.
    d.polygon([(164, 18), (176, 12), (188, 25), (178, 22), (173, 26)], fill=4)
    d.polygon([(369, 22), (379, 15), (391, 28), (380, 25), (375, 29)], fill=4)
    for y in range(image.height):
        image.putpixel((511, y), image.getpixel((0, y)))
    return image


PAL0_HILLS = {
    0: KEY, 1: (73, 109, 73), 2: (73, 146, 73), 3: (109, 146, 73),
    4: (146, 182, 109), 5: (73, 109, 109), 6: (109, 73, 36),
}


def tree(draw: ImageDraw.ImageDraw, x: int, y: int, r: int) -> None:
    draw.rectangle((x - 1, y + r - 1, x + 1, 87), fill=6)
    draw.ellipse((x - r, y - r, x + r, y + r), fill=1)
    draw.ellipse((x - r + 2, y - r + 1, x + r - 1, y + r - 2), fill=2)
    draw.ellipse((x - r + 3, y - r + 2, x + 1, y + 1), fill=4)
    draw.point((x - 2, y - 2), fill=3)


def draw_b3() -> Image.Image:
    image = make_image((512, 88), PAL0_HILLS)
    d = ImageDraw.Draw(image)
    d.polygon([(0, 65), (51, 39), (101, 64), (151, 34), (207, 65), (259, 42), (309, 67), (363, 31), (418, 64), (466, 42), (511, 65), (511, 87), (0, 87)], fill=2)
    d.polygon([(0, 75), (69, 54), (121, 76), (184, 49), (241, 75), (298, 55), (351, 77), (413, 48), (472, 73), (511, 59), (511, 87), (0, 87)], fill=3)
    d.polygon([(0, 83), (82, 66), (147, 82), (218, 63), (284, 83), (348, 65), (419, 82), (474, 66), (511, 78), (511, 87), (0, 87)], fill=1)
    for args in ((26, 50, 10), (72, 63, 6), (116, 45, 12), (168, 60, 7), (220, 48, 10), (269, 65, 6), (316, 45, 11), (371, 60, 7), (421, 42, 13), (476, 57, 8)):
        tree(d, *args)
    # Readable light clusters on the playable-facing sides of the hills.
    for x, y in ((44, 61), (139, 55), (249, 62), (347, 55), (455, 58)):
        d.line((x, y, x + 12, y - 4), fill=4, width=2)
    for y in range(image.height):
        image.putpixel((511, y), image.getpixel((0, y)))
    return image


PAL1_TERRAIN = {
    0: KEY, 1: (36, 36, 36), 2: (73, 36, 36), 3: (109, 73, 36),
    4: (146, 109, 73), 5: (73, 109, 36), 6: (109, 146, 36),
    7: (146, 182, 73), 8: (36, 73, 36), 9: (73, 73, 36),
    10: (182, 146, 73),
}


def terrain_segment(image: Image.Image, x0: int, x1: int, top: int) -> None:
    d = ImageDraw.Draw(image)
    d.rectangle((x0, top, x1 - 1, 63), fill=3)
    d.rectangle((x0, top, x1 - 1, top + 1), fill=7)
    d.rectangle((x0, top + 2, x1 - 1, top + 4), fill=6)
    d.rectangle((x0, top + 5, x1 - 1, top + 7), fill=5)
    d.rectangle((x0, top + 8, x1 - 1, top + 9), fill=1)
    for x in range(x0 + 5, x1 - 3, 13):
        y = top + 14 + ((x * 7) % max(8, 48 - top))
        d.rectangle((x, y, min(x + 3, x1 - 1), min(y + 2, 62)), fill=2)
        d.point((min(x + 1, x1 - 1), min(y + 1, 62)), fill=4)
    for x in range(x0 + 8, x1, 24):
        d.line((x, top + 10, x + 4, top + 13), fill=9)


def draw_b4() -> Image.Image:
    image = make_image((512, 64), PAL1_TERRAIN)
    for segment in ((0, 64, 16), (64, 160, 8), (208, 256, 16), (256, 320, 0), (352, 448, 16), (448, 512, 8)):
        terrain_segment(image, *segment)
    for y in range(image.height):
        image.putpixel((511, y), image.getpixel((0, y)))
    return image


PAL1_FG = {0: KEY, 1: (36, 36, 36), 2: (36, 73, 36), 3: (36, 109, 36), 4: (73, 109, 36)}


def draw_b5() -> Image.Image:
    image = make_image((32, 16), PAL1_FG)
    d = ImageDraw.Draw(image)
    d.polygon([(1, 15), (4, 7), (7, 14), (10, 3), (12, 14), (16, 5), (18, 14), (23, 2), (24, 14), (29, 6), (31, 15)], fill=2)
    d.polygon([(1, 15), (7, 11), (11, 15), (17, 10), (22, 15), (27, 11), (31, 15)], fill=1)
    d.line((10, 4, 11, 13), fill=4)
    d.line((23, 3, 23, 13), fill=3)
    return image


PAL3_WOOD = {
    0: KEY, 1: (36, 36, 36), 2: (73, 36, 0), 3: (109, 73, 36),
    4: (146, 109, 36), 5: (182, 146, 73), 6: (219, 182, 109),
    7: (255, 255, 219), 8: (36, 36, 73), 9: (146, 36, 36),
    10: (219, 73, 73), 11: (36, 109, 36), 12: (73, 146, 36),
    13: (109, 182, 73),
}


def draw_c1() -> Image.Image:
    image = make_image((64, 96), PAL3_WOOD)
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, 63, 95), fill=3)
    wave = (0, -2, 1, 3, 0, -1, 2, -2, 1, 0, 3, -1, 0)
    for lane, base in enumerate((5, 17, 31, 45, 58)):
        points = [(base + wave[(y // 8 + lane * 2) % len(wave)], y) for y in range(0, 96, 4)]
        d.line(points, fill=2 if lane % 2 == 0 else 4, width=5)
        d.line([(x + 2, y) for x, y in points], fill=5 if lane % 2 == 0 else 1, width=1)
    for x, y, r in ((12, 25, 6), (39, 67, 8), (55, 18, 4)):
        d.ellipse((x - r, y - r, x + r, y + r), fill=1)
        d.ellipse((x - r + 2, y - r + 2, x + r - 2, y + r - 2), fill=4)
        d.arc((x - r + 2, y - r + 2, x + r - 2, y + r - 2), 210, 30, fill=6, width=1)
    for x in range(64):
        image.putpixel((x, 95), image.getpixel((x, 0)))
    return image


def face_frame(angry: bool) -> Image.Image:
    image = make_image((48, 32), PAL3_WOOD)
    d = ImageDraw.Draw(image)
    # Eyes are large and asymmetrical enough to carry expression at 1x.
    for ex in (13, 33):
        d.ellipse((ex - 6, 5, ex + 5, 19), fill=1)
        d.ellipse((ex - 4, 6, ex + 3, 17), fill=7)
        d.ellipse((ex - 1, 9, ex + 2, 16), fill=8)
        d.point((ex, 10), fill=7)
    if angry:
        d.polygon([(5, 4), (20, 8), (19, 11), (7, 8)], fill=1)
        d.polygon([(28, 8), (43, 4), (41, 8), (29, 11)], fill=1)
    else:
        d.line((7, 4, 19, 3), fill=2, width=3)
        d.line((29, 3, 41, 4), fill=2, width=3)
    d.ellipse((18, 12, 30, 25), fill=1)
    d.ellipse((20, 11, 28, 23), fill=5)
    d.rectangle((22, 19, 26, 22), fill=4)
    if angry:
        d.arc((13, 19, 36, 33), 195, 345, fill=1, width=3)
    else:
        d.arc((13, 17, 36, 29), 15, 165, fill=1, width=3)
    return image


def draw_c2() -> Image.Image:
    image = make_image((96, 32), PAL3_WOOD)
    image.paste(face_frame(False), (0, 0))
    image.paste(face_frame(True), (48, 0))
    return image


def draw_c3() -> Image.Image:
    image = make_image((16, 16), PAL3_WOOD)
    d = ImageDraw.Draw(image)
    d.polygon([(1, 6), (4, 4), (12, 4), (15, 6), (15, 9), (12, 11), (4, 11), (1, 9)], fill=1)
    d.polygon([(2, 7), (5, 5), (12, 5), (14, 7), (14, 8), (12, 10), (5, 10), (2, 8)], fill=3)
    d.line((5, 6, 11, 6), fill=5)
    d.line((5, 9, 11, 9), fill=2)
    d.line((7, 5, 7, 10), fill=4)
    return image


def apple_frame(wobble: int) -> Image.Image:
    image = make_image((16, 16), PAL3_WOOD)
    d = ImageDraw.Draw(image)
    ox = wobble
    d.line((8 + ox, 1, 7 + ox, 4), fill=1, width=2)
    d.ellipse((8 + ox, 1, 13 + ox, 5), fill=11)
    d.ellipse((2 + ox, 4, 13 + ox, 14), fill=1)
    d.ellipse((3 + ox, 4, 12 + ox, 13), fill=9)
    d.rectangle((4 + ox, 6, 10 + ox, 11), fill=10)
    d.rectangle((4 + ox, 5, 6 + ox, 7), fill=6)
    d.rectangle((9 + ox, 10, 11 + ox, 12), fill=9)
    return image


def draw_c4() -> Image.Image:
    image = make_image((32, 16), PAL3_WOOD)
    image.paste(apple_frame(0), (0, 0))
    image.paste(apple_frame(1), (16, 0))
    return image


PAL3_FX = {
    0: KEY, 1: (36, 36, 73), 2: (146, 36, 36), 3: (219, 73, 36),
    4: (255, 146, 36), 5: (255, 219, 73), 6: (255, 255, 219),
    7: (36, 109, 182), 8: (73, 182, 255), 9: (182, 219, 255),
    10: (73, 73, 73), 11: (146, 146, 146), 12: (219, 219, 219),
    13: (109, 182, 73),
}


def draw_d1() -> Image.Image:
    image = make_image((240, 16), PAL3_FX)
    for index in range(15):
        cell = make_image((16, 16), PAL3_FX)
        d = ImageDraw.Draw(cell)
        group, phase = divmod(index, 3)
        if group == 0:  # FIRE: round plume opening
            r = 3 + phase * 2
            d.ellipse((8 - r, 8 - r, 8 + r, 8 + r), fill=2)
            d.polygon([(2, 8), (7, 5 - phase), (7, 11 + phase)], fill=3)
            d.ellipse((7 - phase, 6 - phase, 10 + phase, 10 + phase), fill=4)
            d.ellipse((8, 7, 11, 10), fill=5)
        elif group == 1:  # BEAM: angular and thin
            points = [(1, 8), (4, 5 - phase), (7, 9), (10, 4 + phase), (14, 7)]
            d.line(points, fill=7, width=3)
            d.line(points, fill=9, width=1)
        elif group == 2:  # CUTTER: hollow crescent
            d.arc((1 + phase, 1, 14, 14 - phase), 245, 115, fill=6, width=3)
            d.arc((3 + phase, 3, 12, 12 - phase), 245, 115, fill=8, width=1)
        elif group == 3:  # STONE: no curves
            inset = 3 - phase
            d.rectangle((inset, inset + 1, 15 - inset, 14 - inset), fill=10)
            d.rectangle((inset + 1, inset + 2, 13 - inset, 12 - inset), fill=11)
            d.line((inset + 2, inset + 3, 12 - inset, inset + 3), fill=12)
            d.line((inset + 2, 12 - inset, 12 - inset, 12 - inset), fill=1)
        else:  # SWORD: thin swept arc
            d.arc((1, 1 + phase, 14, 14), 205, 345, fill=6, width=2)
            d.arc((2, 2 + phase, 13, 13), 205, 345, fill=9, width=1)
            d.rectangle((2 + phase, 10, 5 + phase, 12), fill=5)
            d.point((3 + phase, 13), fill=3)
        image.paste(cell, (index * 16, 0))
    return image


PAL0_TITLE = {0: KEY, 1: (73, 73, 182), 2: (146, 109, 219), 3: (219, 182, 255), 4: (255, 255, 255)}


def draw_e1() -> Image.Image:
    image = make_image((512, 96), PAL0_TITLE)
    d = ImageDraw.Draw(image)
    stars = [(13, 15, 1), (39, 58, 2), (77, 29, 1), (112, 78, 1), (151, 18, 3), (189, 62, 1), (226, 36, 2), (271, 84, 1), (305, 22, 1), (348, 53, 3), (389, 11, 1), (427, 74, 2), (471, 31, 1), (498, 60, 1)]
    for x, y, size in stars:
        if size == 1:
            d.point((x, y), fill=4)
        elif size == 2:
            d.line((x - 2, y, x + 2, y), fill=3)
            d.line((x, y - 2, x, y + 2), fill=3)
            d.point((x, y), fill=4)
        else:
            d.line((x - 3, y, x + 3, y), fill=2)
            d.line((x, y - 3, x, y + 3), fill=2)
            d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=4)
    for y in range(image.height):
        image.putpixel((511, y), image.getpixel((0, y)))
    return image


PAL0_HILL = {0: KEY, 1: (0, 0, 36), 2: (36, 36, 73), 3: (36, 36, 109), 4: (73, 73, 146), 5: (109, 73, 146)}


def draw_e2() -> Image.Image:
    image = make_image((512, 64), PAL0_HILL)
    d = ImageDraw.Draw(image)
    d.polygon([(0, 47), (62, 36), (111, 41), (174, 25), (229, 38), (285, 31), (342, 43), (402, 24), (459, 39), (511, 47), (511, 63), (0, 63)], fill=2)
    d.polygon([(0, 55), (92, 44), (159, 52), (236, 39), (306, 53), (376, 40), (448, 51), (511, 44), (511, 63), (0, 63)], fill=1)
    # One unmistakable tree silhouette; no internal texture.
    d.rectangle((111, 16, 119, 49), fill=1)
    d.ellipse((83, 2, 148, 31), fill=1)
    d.ellipse((96, 0, 135, 23), fill=1)
    for y in range(image.height):
        image.putpixel((511, y), image.getpixel((0, y)))
    return image


FONT = {
    "C": ["1111", "1000", "1000", "1000", "1000", "1000", "1111"],
    "L": ["1000", "1000", "1000", "1000", "1000", "1000", "1111"],
    "O": ["1111", "1001", "1001", "1001", "1001", "1001", "1111"],
    "U": ["1001", "1001", "1001", "1001", "1001", "1001", "1111"],
    "D": ["1110", "1001", "1001", "1001", "1001", "1001", "1110"],
    "E": ["1111", "1000", "1000", "1110", "1000", "1000", "1111"],
}


def draw_e3() -> Image.Image:
    image = make_image((224, 48), PAL2)
    mask = Image.new("1", image.size, 0)
    md = ImageDraw.Draw(mask)
    widths = {"C": 28, "L": 24, "O": 28, "U": 28, "D": 28, "E": 24}
    word = "CLOUDE"
    spacing = 4
    total = sum(widths[letter] for letter in word) + spacing * (len(word) - 1)
    x = (224 - total) // 2
    y0, h = 8, 32
    for letter in word:
        w = widths[letter]
        if letter == "C":
            md.rounded_rectangle((x, y0, x + w - 1, y0 + h - 1), radius=8, fill=1)
            md.rounded_rectangle((x + 7, y0 + 6, x + w - 6, y0 + h - 7), radius=4, fill=0)
            md.rectangle((x + w - 10, y0 + 8, x + w, y0 + h - 9), fill=0)
        elif letter == "L":
            md.rounded_rectangle((x, y0, x + 8, y0 + h - 1), radius=4, fill=1)
            md.rounded_rectangle((x, y0 + h - 9, x + w - 1, y0 + h - 1), radius=4, fill=1)
        elif letter == "O":
            md.rounded_rectangle((x, y0, x + w - 1, y0 + h - 1), radius=9, fill=1)
            md.rounded_rectangle((x + 7, y0 + 7, x + w - 8, y0 + h - 8), radius=4, fill=0)
        elif letter == "U":
            md.rounded_rectangle((x, y0, x + 8, y0 + h - 7), radius=4, fill=1)
            md.rounded_rectangle((x + w - 9, y0, x + w - 1, y0 + h - 7), radius=4, fill=1)
            md.rounded_rectangle((x, y0 + h - 13, x + w - 1, y0 + h - 1), radius=7, fill=1)
            md.rectangle((x + 8, y0 + h - 13, x + w - 9, y0 + h - 8), fill=0)
        elif letter == "D":
            md.rounded_rectangle((x, y0, x + w - 1, y0 + h - 1), radius=9, fill=1)
            md.rounded_rectangle((x + 8, y0 + 7, x + w - 8, y0 + h - 8), radius=4, fill=0)
        elif letter == "E":
            md.rounded_rectangle((x, y0, x + 8, y0 + h - 1), radius=4, fill=1)
            for bar_y in (y0, y0 + 12, y0 + h - 8):
                md.rounded_rectangle((x, bar_y, x + w - 1, bar_y + 7), radius=3, fill=1)
        x += w + spacing
    outline = Image.new("1", image.size, 0)
    src, dst = mask.load(), outline.load()
    for y in range(image.height):
        for x in range(image.width):
            if src[x, y]:
                for dy in (-2, -1, 0, 1, 2):
                    for dx in (-2, -1, 0, 1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < image.width and 0 <= ny < image.height:
                            dst[nx, ny] = 1
    image.paste(6, mask=outline)
    image.paste(4, mask=mask)
    d = ImageDraw.Draw(image)
    # Top-light pixels and two small authorial star accents.
    for y in range(y0, y0 + 5):
        for x in range(image.width):
            if mask.getpixel((x, y)):
                image.putpixel((x, y), 1)
    d.polygon([(7, 23), (10, 24), (11, 28), (12, 24), (16, 23), (12, 22), (11, 18), (10, 22)], fill=3)
    d.polygon([(207, 14), (210, 15), (211, 18), (212, 15), (215, 14), (212, 13), (211, 10), (210, 13)], fill=1)
    return image


def luminance(colour: tuple[int, int, int]) -> float:
    r, g, b = colour
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def report(asset_id: str, filename: str, image: Image.Image) -> None:
    rgb = image.convert("RGB")
    colours = set(rgb.get_flattened_data())
    visible = [pixel for pixel in rgb.get_flattened_data() if pixel != KEY]
    mean = sum(luminance(pixel) for pixel in visible[::37]) / max(1, len(visible[::37]))
    illegal = [colour for colour in colours if any(channel not in LEGAL for channel in colour)]
    print(f"{asset_id:2} {filename:20} {image.width:3}x{image.height:<3} visible_colours={len(colours - {KEY}):2} lum={mean:.3f} illegal={len(illegal)}")


def make_review_board(name: str, entries: list[tuple[str, Image.Image, int]]) -> None:
    margin = 12
    label_h = 18
    prepared: list[tuple[str, Image.Image]] = []
    width = 0
    height = margin
    for label, source, scale in entries:
        preview = source.convert("RGB").resize(
            (source.width * scale, source.height * scale), Image.Resampling.NEAREST
        )
        prepared.append((label, preview))
        width = max(width, preview.width + margin * 2)
        height += label_h + preview.height + margin
    board = Image.new("RGB", (width, height), (18, 22, 30))
    draw = ImageDraw.Draw(board)
    y = margin
    for label, preview in prepared:
        draw.text((margin, y), label, fill=(235, 239, 244))
        y += label_h
        board.paste(preview, (margin, y))
        y += preview.height + margin
    evidence = P1 / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    board.save(evidence / f"{name}_contact_sheet.png")


def main() -> int:
    assets = [
        ("A2", "ph_enemy.png", draw_a2()),
        ("A3", "ph_particle.png", draw_a3()),
        ("B1", "ph_sky.png", draw_b1()),
        ("B2", "ph_mount.png", draw_b2()),
        ("B3", "ph_hills.png", draw_b3()),
        ("B4", "ph_terrain.png", draw_b4()),
        ("B5", "ph_fg.png", draw_b5()),
        ("C1", "ph_trunk.png", draw_c1()),
        ("C2", "ph_boss_face.png", draw_c2()),
        ("C3", "ph_branch.png", draw_c3()),
        ("C4", "ph_apple.png", draw_c4()),
        ("D1", "ph_ability_fx.png", draw_d1()),
        ("E1", "ph_title_stars.png", draw_e1()),
        ("E2", "ph_title_hill.png", draw_e2()),
        ("E3", "ph_title_logo.png", draw_e3()),
    ]
    for asset_id, filename, image in assets:
        save(asset_id, filename, image)
        report(asset_id, filename, image)
    by_id = {asset_id: (filename, image) for asset_id, filename, image in assets}
    a1 = Image.open(P1 / "A1" / "ph_kirby.png")
    make_review_board("group_a", [
        ("A1 ph_kirby.png | 8 poses", a1, 4),
        ("A2 ph_enemy.png | walk A/B", by_id["A2"][1], 8),
        ("A3 ph_particle.png | shrink 3 frames", by_id["A3"][1], 12),
    ])
    make_review_board("group_b", [
        (f"{asset_id} {by_id[asset_id][0]}", by_id[asset_id][1], 1 if asset_id != "B5" else 8)
        for asset_id in ("B1", "B2", "B3", "B4", "B5")
    ])
    make_review_board("group_c_d", [
        ("C1 ph_trunk.png | vertical tile", by_id["C1"][1], 2),
        ("C2 ph_boss_face.png | calm/angry", by_id["C2"][1], 4),
        ("C3 ph_branch.png | modular segment", by_id["C3"][1], 8),
        ("C4 ph_apple.png | wobble A/B", by_id["C4"][1], 8),
        ("D1 ph_ability_fx.png | FIRE/BEAM/CUTTER/STONE/SWORD", by_id["D1"][1], 3),
    ])
    make_review_board("group_e", [
        ("E1 ph_title_stars.png", by_id["E1"][1], 1),
        ("E2 ph_title_hill.png", by_id["E2"][1], 1),
        ("E3 ph_title_logo.png", by_id["E3"][1], 2),
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

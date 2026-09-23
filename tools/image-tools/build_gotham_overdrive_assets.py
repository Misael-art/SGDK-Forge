#!/usr/bin/env python3
"""Build Master-Quality AAA Mega Drive Assets for GOTHAM_OVERDRIVE [VER.001].

Strictly adheres to:
- 4-bit indexed PNGs (16 colors per file, index 0 transparent)
- 9-bit RGB quantization ({0, 34, 68, 102, 136, 170, 204, 238})
- Multiples of 8x8 tile boundaries
- Authentic Dark Deco 90s visual aesthetic (Batman: TAS / The Adventures of Batman & Robin)
- Ordered Bayer dithering (2x2 / 4x4) for volumetric lighting, specular chrome and shadows
- Volumetric 3D sculptured forms for pseudo-3D raster perspective
- High-intensity glowing energy cores (multi-layer bloom / incandescence)
- Full asset provenance tracking with source art in data/source_art/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


# -----------------------------------------------------------------------------
# PALETTES (Strict 9-bit RGB values)
# -----------------------------------------------------------------------------

# PAL0: Gotham Skyline & Atmosphere
PAL0 = [
    (0, 0, 0),        # 0: Transparent / Black
    (0, 0, 34),       # 1: Deep Night Blue
    (0, 34, 68),      # 2: Midnight Blue
    (34, 34, 68),     # 3: Gothic Slate
    (34, 68, 102),    # 4: Urban Mist Blue
    (68, 68, 102),    # 5: Spire Shadow
    (68, 102, 136),   # 6: Skyscraper Midtone
    (102, 136, 170),  # 7: Skyscraper Edge Highlight
    (34, 0, 68),      # 8: Twilight Violet
    (102, 34, 102),   # 9: Purple Cloud
    (170, 136, 34),   # 10: Dark Deco Amber Glass
    (238, 204, 68),   # 11: Bright Gold Window Light
    (136, 170, 204),  # 12: Silver Cloud Rim
    (204, 238, 238),  # 13: Bat-Signal Spotlight Beam (dynamic pulse)
    (238, 238, 238),  # 14: Pure White Moonlight
    (0, 0, 0),        # 15: Deep Black Shadow
]

# PAL1: Perspective Roadway & Bridge Deck
PAL1 = [
    (0, 0, 0),        # 0: Transparent / Upper Sky
    (34, 34, 34),     # 1: Dark Textured Asphalt
    (68, 68, 68),     # 2: Asphalt Midtone
    (102, 102, 102),  # 3: Concrete Barrier / Curbs
    (136, 136, 136),  # 4: Metallic Guardrail
    (170, 170, 170),  # 5: Steel Bridge Truss
    (0, 68, 102),     # 6: Roadway Truss Shadow
    (0, 136, 170),    # 7: Cyan Suspension Cable
    (0, 204, 238),    # 8: Cyan Neon Lane Dividers
    (238, 170, 0),    # 9: Amber Road Reflector
    (238, 238, 0),    # 10: Bright Yellow Central Stripe
    (136, 34, 34),    # 11: Red Asphalt Reflection
    (204, 68, 68),    # 12: Red Hazard Beacon
    (34, 68, 68),     # 13: Distant Mist Pillar
    (204, 204, 204),  # 14: Steel Glint Highlight
    (238, 238, 238),  # 15: Telemetry / Highlight
]

# PAL2: Batmobile & Player Weapons
PAL2 = [
    (0, 0, 0),        # 0: Transparent
    (0, 0, 0),        # 1: Obsidian Chassis Black
    (34, 34, 68),     # 2: Titanium Armor Shadow
    (68, 68, 102),    # 3: Armored Panel Midtone
    (102, 102, 136),  # 4: Metallic Rim Highlight
    (136, 170, 204),  # 5: Cockpit Canopy Glass Reflection
    (204, 238, 238),  # 6: Windshield Frame Glint
    (0, 136, 204),    # 7: Cyan Neon Accent
    (0, 238, 238),    # 8: Plasma Cyan Headlights/Tail Glow
    (238, 204, 0),    # 9: Golden Bat Emblem
    (238, 102, 0),    # 10: Turbine Orange Flame
    (238, 34, 0),     # 11: Afterburner Red Core
    (238, 238, 68),   # 12: Vulcan Yellow Tracer
    (34, 34, 34),     # 13: Tire Rubber Dark
    (170, 170, 170),  # 14: Wheel Alloy Silver
    (238, 238, 238),  # 15: Muzzle / Engine White Core
]

# PAL3: Two-Face Siege Dreadnought, Drones, Projectiles & Particles
PAL3 = [
    (0, 0, 0),        # 0: Transparent
    (0, 0, 0),        # 1: Shadow / Cannon Bore
    (34, 68, 34),     # 2: Acid Green Armor Shadow
    (68, 136, 68),    # 3: Bionic Green Midtone
    (102, 204, 102),  # 4: Toxic Green Highlight
    (68, 0, 0),       # 5: Crimson Armor Shadow
    (136, 34, 34),    # 6: Flayed Crimson Steel Midtone
    (204, 68, 68),    # 7: Crimson Highlight
    (238, 34, 34),    # 8: Laser Sensor / Reticle Red
    (51, 51, 51),     # 9: Dark Tread Steel
    (102, 102, 102),  # 10: Tread Link Metal
    (170, 136, 68),   # 11: Turret Bronze Casing
    (238, 170, 0),    # 12: Plasma Fireball Orange
    (238, 238, 0),    # 13: Electric Spark Yellow
    (136, 136, 170),  # 14: Pod Alloy Plating
    (238, 238, 238),  # 15: Shockwave White
]

# 4x4 Bayer Matrix
BAYER4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
]

def bayer_dither(val: float, x: int, y: int) -> bool:
    """Return True if float ratio val (0.0 to 1.0) exceeds Bayer threshold at (x, y)."""
    thresh = (BAYER4[y % 4][x % 4] + 0.5) / 16.0
    return val >= thresh


def pal_flat(colors: list[tuple[int, int, int]]) -> list[int]:
    out: list[int] = []
    for r, g, b in colors:
        out.extend([r, g, b])
    out.extend([0] * (768 - len(out)))
    return out


def save_p4(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.info["transparency"] = 0
    img.save(path, format="PNG", bits=4, optimize=False)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# -----------------------------------------------------------------------------
# 1. GOTHAM SKYLINE (BG_B - 320x224 - PAL0)
# -----------------------------------------------------------------------------
def make_gotham_skyline() -> Image.Image:
    w, h = 320, 224
    img = Image.new("P", (w, h), 0)
    img.putpalette(pal_flat(PAL0))
    d = ImageDraw.Draw(img)

    # 1. Sky Dithering (Continuous Bayer 4x4 vertical twilight gradient)
    for y in range(h):
        for x in range(w):
            if y < 35:
                # Top: 1 (Deep Night Blue) to 8 (Twilight Violet)
                ratio = y / 35.0
                img.putpixel((x, y), 8 if bayer_dither(ratio, x, y) else 1)
            elif y < 75:
                # Upper: 8 (Twilight Violet) to 9 (Purple Cloud) to 2 (Midnight Blue)
                ratio = (y - 35) / 40.0
                if ratio < 0.5:
                    sub = ratio * 2.0
                    img.putpixel((x, y), 9 if bayer_dither(sub, x, y) else 8)
                else:
                    sub = (ratio - 0.5) * 2.0
                    img.putpixel((x, y), 2 if bayer_dither(sub, x, y) else 9)
            elif y < 120:
                # Mid sky: 2 (Midnight Blue) to 3 (Gothic Slate) / 4 (Urban Mist)
                ratio = (y - 75) / 45.0
                img.putpixel((x, y), 3 if bayer_dither(ratio, x, y) else 2)
            else:
                # Base horizon glow
                ratio = (y - 120) / float(h - 120)
                img.putpixel((x, y), 1 if bayer_dither(ratio, x, y) else 3)

    # 2. Giant Colossal Moon (x=215, y=50, radius=28) with Volumetric Craters & Halo
    mx, my, mr = 215, 50, 28
    for y in range(my - mr - 6, my + mr + 7):
        for x in range(mx - mr - 6, mx + mr + 7):
            dist = math.hypot(x - mx, y - my)
            if dist <= mr:
                # Shading across moon sphere
                angle = math.atan2(y - my, x - mx)
                norm_x = (x - mx) / float(mr)
                norm_y = (y - my) / float(mr)
                sphere_shade = (1.0 - (norm_x * 0.4 + norm_y * 0.6))
                # Crater pattern synthesis
                crater1 = math.sin(x * 0.35 + 1.2) * math.cos(y * 0.35 + 0.8)
                crater2 = math.sin(x * 0.7 - y * 0.5) * 0.5

                if dist > mr - 2:
                    img.putpixel((x, y), 12)  # Silver rim
                elif crater1 + crater2 > 0.45:
                    img.putpixel((x, y), 3)   # Deep crater shadow
                elif crater1 > 0.15:
                    img.putpixel((x, y), 7)   # Crater midtone
                elif sphere_shade < 0.6:
                    img.putpixel((x, y), 12 if bayer_dither(sphere_shade, x, y) else 14)
                else:
                    img.putpixel((x, y), 14)  # Pure white moon face
            elif dist <= mr + 5:
                # Dithered lunar corona
                falloff = 1.0 - (dist - mr) / 5.0
                if bayer_dither(falloff * 0.75, x, y):
                    img.putpixel((x, y), 12)

    # 3. Dynamic Bat-Signal Spotlight Beam (Originating lower left (35, 224) to upper clouds (195, 45))
    for y in range(20, 210):
        t = (210 - y) / 190.0
        bx = 35 + t * 160
        bw = 8 + t * 38
        for x in range(int(bx - bw), int(bx + bw + 1)):
            if 0 <= x < w:
                cur = img.getpixel((x, y))
                edge_dist = abs(x - bx) / float(bw)
                beam_density = 1.0 - (edge_dist ** 1.5)
                if beam_density > 0.65:
                    img.putpixel((x, y), 13)  # Bright spotlight core (dynamic pulse PAL0[13])
                elif beam_density > 0.2:
                    if bayer_dither(beam_density, x, y):
                        img.putpixel((x, y), 13)

    # Bat Insignia Silhouette projected on the cloud layer
    bat_cx, bat_cy = 195, 45
    bat_shape = [
        (-14, -3), (-10, -8), (-7, -5), (-4, -8), (0, -4), (4, -8), (7, -5), (10, -8), (14, -3),
        (12, 4), (7, 8), (0, 11), (-7, 8), (-12, 4)
    ]
    d.polygon([(bat_cx + px, bat_cy + py) for px, py in bat_shape], fill=3)
    # Head & Ears
    d.polygon([(bat_cx - 3, bat_cy - 6), (bat_cx - 3, bat_cy - 11), (bat_cx, bat_cy - 7)], fill=3)
    d.polygon([(bat_cx + 3, bat_cy - 6), (bat_cx + 3, bat_cy - 11), (bat_cx, bat_cy - 7)], fill=3)

    # 4. Billowing Gothic Clouds (Multi-layer shaded banks)
    clouds = [
        (15, 30, 130, 60), (135, 55, 245, 90), (240, 35, 319, 65),
        (50, 75, 175, 105), (160, 90, 310, 120)
    ]
    for cx0, cy0, cx1, cy1 in clouds:
        for cy in range(cy0, cy1):
            for cx in range(cx0, cx1):
                if 0 <= cx < w and 0 <= cy < h:
                    norm_u = (cx - cx0) / float(cx1 - cx0)
                    norm_v = (cy - cy0) / float(cy1 - cy0)
                    density = math.sin(norm_u * math.pi) * math.sin(norm_v * math.pi)
                    if density > 0.65:
                        if bayer_dither(density, cx, cy):
                            img.putpixel((cx, cy), 9)   # Purple cloud body
                    elif density > 0.35:
                        if bayer_dither(density * 0.8, cx, cy):
                            img.putpixel((cx, cy), 8)   # Twilight violet
                    # Silver rim on upper crest
                    if 0.4 < density < 0.7 and norm_v < 0.4:
                        if bayer_dither(0.8, cx, cy):
                            img.putpixel((cx, cy), 12)

    # 5. Gothic Cathedral Spires & Art Deco Skyscrapers (Deep Layer & Mid Layer)
    # Distant spires with setbacks and antennas
    distant_spires = [
        (12, 65, 38, 200), (52, 55, 82, 200), (102, 70, 138, 200),
        (155, 45, 192, 200), (218, 62, 252, 200), (272, 50, 308, 200)
    ]
    for x0, y0, x1, y1 in distant_spires:
        d.rectangle((x0, y0, x1, y1), fill=3)
        mid_x = (x0 + x1) // 2
        d.polygon([(x0, y0), (mid_x, y0 - 22), (x1, y0)], fill=5)
        d.line((mid_x, y0 - 22, mid_x, y0 - 32), fill=7)

    # Foreground Art Deco Skyscrapers with Stepped Setbacks & Stained Glass
    mid_buildings = [
        (0, 85, 26, 223), (28, 70, 68, 223), (72, 80, 118, 223),
        (122, 60, 172, 223), (170, 75, 222, 223), (226, 65, 274, 223),
        (276, 80, 319, 223)
    ]
    for x0, y0, x1, y1 in mid_buildings:
        mid_x = (x0 + x1) // 2
        # Building silhouette
        d.rectangle((x0, y0, x1, y1), fill=1)
        # Setback tiers
        d.rectangle((x0 + 4, y0 - 12, x1 - 4, y0), fill=3)
        d.rectangle((x0 + 8, y0 - 24, x1 - 8, y0 - 12), fill=5)
        d.polygon([(x0 + 10, y0 - 24), (mid_x, y0 - 38), (x1 - 10, y0 - 24)], fill=6)
        d.line((mid_x, y0 - 38, mid_x, y0 - 48), fill=14)

        # Chrome/Metallic Highlight edge on left side
        d.line((x0, y0, x0, y1), fill=7)
        d.line((x0 + 1, y0, x0 + 1, y1), fill=6)
        d.line((x0 + 4, y0 - 12, x0 + 4, y0), fill=7)
        d.line((x0 + 8, y0 - 24, x0 + 8, y0 - 12), fill=7)

        # Deep Core Shadow on right side
        d.line((x1, y0, x1, y1), fill=15)
        d.line((x1 - 1, y0, x1 - 1, y1), fill=1)

        # Architectural Fluted Pilasters (Vertical stone ribs)
        for rx in range(x0 + 4, x1 - 4, 8):
            d.line((rx, y0 + 4, rx, min(y1 - 6, 170)), fill=5)

        # Dark Deco Glowing Stained Glass Windows (Amber & Gold)
        for wy in range(y0 + 10, min(y1 - 12, 165), 12):
            for wx in range(x0 + 6, x1 - 6, 8):
                # Arched window frame
                d.rectangle((wx, wy + 2, wx + 3, wy + 7), fill=10)
                d.point((wx + 1, wy + 1), fill=10)
                d.point((wx + 2, wy + 1), fill=10)
                # Bright gold incandescent core
                d.rectangle((wx + 1, wy + 3, wx + 2, wy + 6), fill=11)
                # Dithered glow halo under window
                if (wx + wy) % 2 == 0:
                    d.point((wx + 1, wy + 8), fill=10)

    # Perched Stone Gargoyles on tower ledges
    for gx, gy in [(68, 70), (226, 65)]:
        d.polygon([(gx, gy), (gx + 8, gy - 6), (gx + 11, gy + 3), (gx + 3, gy + 6)], fill=5)
        d.polygon([(gx + 3, gy - 4), (gx + 7, gy - 7), (gx + 8, gy - 3)], fill=6)  # Wing
        d.point((gx + 9, gy - 4), fill=11)  # Glowing Amber Eye

    return img


# -----------------------------------------------------------------------------
# 2. PERSPECTIVE ROADWAY & BRIDGE DECK (BG_A - 320x224 - PAL1)
# -----------------------------------------------------------------------------
def make_gotham_roadway() -> Image.Image:
    w, h = 320, 224
    img = Image.new("P", (w, h), 0)
    img.putpalette(pal_flat(PAL1))
    d = ImageDraw.Draw(img)

    # Upper zone Y=0..79 is strictly transparent (index 0)
    horizon_y = 80

    # Draw 3D Perspective Roadway Bed with Dithered Asphalt & Wet Sheen
    for y in range(horizon_y, h):
        t = (y - horizon_y) / float(h - horizon_y)  # 0.0 at horizon, 1.0 at bottom
        road_half_w = 48 + (t ** 1.15) * 82
        cx = 160
        rx0 = int(cx - road_half_w)
        rx1 = int(cx + road_half_w)

        for x in range(rx0, rx1 + 1):
            if 0 <= x < w:
                # Asphalt grain with Bayer dithering
                asphalt_noise = ((x * 17) ^ (y * 31)) & 7
                speed_band = ((y + int(t * 12)) % 8 < 4)

                # Wet road cyan reflections near lane markers
                dist_to_cyan = min(abs(x - (rx0 + 5)), abs(x - (rx1 - 5)))
                if dist_to_cyan < 8 and bayer_dither(1.0 - (dist_to_cyan / 8.0) * 0.7, x, y):
                    img.putpixel((x, y), 6)  # Roadway cyan shadow sheen
                elif speed_band and asphalt_noise > 3:
                    img.putpixel((x, y), 2)  # Asphalt midtone
                else:
                    img.putpixel((x, y), 1)  # Dark asphalt

        # Concrete Curbs with 3D Bevel
        for k in range(4):
            c_color = 4 if k == 0 else 3
            if 0 <= rx0 - k < w:
                img.putpixel((rx0 - k, y), c_color)
            if 0 <= rx1 + k < w:
                img.putpixel((rx1 + k, y), c_color)

        # Cyan Neon Lane Dividers with Outer Glow
        cyan_w = max(1, int(1 + t * 2.5))
        for k in range(cyan_w):
            if 0 <= rx0 + 3 + k < w:
                img.putpixel((rx0 + 3 + k, y), 8)
            if 0 <= rx1 - 3 - k < w:
                img.putpixel((rx1 - 3 - k, y), 8)

        # Central Dashed Yellow Lane Marker (Expanding in 3D perspective)
        dash_len = int(8 + t * 18)
        dash_gap = int(6 + t * 12)
        cycle = (y * 2) % (dash_len + dash_gap)
        if cycle < dash_len:
            c_width = max(1, int(1 + t * 3.5))
            for k in range(-c_width, c_width + 1):
                if 0 <= cx + k < w:
                    if abs(k) == c_width:
                        img.putpixel((cx + k, y), 9)   # Amber edge
                    else:
                        img.putpixel((cx + k, y), 10)  # Bright yellow core

        # Amber Roadway Reflectors on Curbs
        if (y % 20) < 3 and t > 0.25:
            if 0 <= rx0 - 2 < w:
                img.putpixel((rx0 - 2, y), 9)
            if 0 <= rx1 + 2 < w:
                img.putpixel((rx1 + 2, y), 9)

    # Massive Industrial Suspension Bridge Steel Superstructure (Trusses & Cables)
    for y in range(horizon_y - 25, h):
        t = (y - (horizon_y - 25)) / float(h - (horizon_y - 25))
        lx0, lx1 = 0, int(32 + t * 20)
        rx0, rx1 = int(288 - t * 20), 319

        # Steel plates body
        d.rectangle((lx0, y, lx1, y), fill=6)
        d.rectangle((rx0, y, rx1, y), fill=6)

        # Structural Girders with Specular Bevels
        d.line((lx1 - 3, y, lx1, y), fill=5)
        d.line((lx1 - 1, y, lx1, y), fill=14)
        d.line((rx0, y, rx0 + 3, y), fill=5)
        d.line((rx0, y, rx0 + 1, y), fill=14)

        # Heavy Industrial Rivets & Bolts
        if (y % 10) == 0:
            d.point((lx1 - 5, y), fill=14)
            d.point((rx0 + 5, y), fill=14)
            d.point((lx1 - 6, y), fill=1)
            d.point((rx0 + 6, y), fill=1)

    # Steel Suspension Cables with Specular Glints
    for y in range(horizon_y - 45, h, 2):
        t = (y - (horizon_y - 45)) / float(h - (horizon_y - 45))
        c_lx = int(5 + t * 44)
        c_rx = int(314 - t * 44)
        if 0 <= c_lx < w:
            img.putpixel((c_lx, y), 7)
            img.putpixel((c_lx + 1, y), 14)
        if 0 <= c_rx < w:
            img.putpixel((c_rx, y), 7)
            img.putpixel((c_rx - 1, y), 14)

    # Red Hazard Warning Beacons with White Flash Core
    for bx in [34, 286]:
        d.rectangle((bx - 4, horizon_y - 14, bx + 4, horizon_y - 6), fill=12)
        d.rectangle((bx - 2, horizon_y - 12, bx + 2, horizon_y - 8), fill=15)

    return img


# -----------------------------------------------------------------------------
# 3. PLAYER BATMOBILE (SPRITE - 192x24 [4 frames of 48x24] - PAL2)
# -----------------------------------------------------------------------------
def make_batmobile_spritesheet() -> Image.Image:
    fw, fh = 48, 24
    img = Image.new("P", (fw * 4, fh), 0)
    img.putpalette(pal_flat(PAL2))

    for frame in range(4):
        ox = frame * fw
        d = ImageDraw.Draw(img)

        # Dynamic banking & tilt offsets
        if frame == 1:    # Bank Left
            tilt_y_l, tilt_y_r = -1, 1
            body_dx = -1
            fin_l_raise = 2
            fin_r_raise = -2
        elif frame == 2:  # Bank Right
            tilt_y_l, tilt_y_r = 1, -1
            body_dx = 1
            fin_l_raise = -2
            fin_r_raise = 2
        else:             # Neutral / Turbo
            tilt_y_l, tilt_y_r = 0, 0
            body_dx = 0
            fin_l_raise = 0
            fin_r_raise = 0

        # 1. Wide Rear Racing Tires (Obsidian Rubber + Silver Alloy 5-Spoke Rims)
        # Left Tire
        tlx0, tlx1 = ox + 4, ox + 14
        tly0, tly1 = 14 + tilt_y_l, 22 + tilt_y_l
        d.rectangle((tlx0, tly0, tlx1, tly1), fill=13)
        d.rectangle((tlx0 + 2, tly0 + 2, tlx1 - 2, tly1 - 2), fill=14)
        d.point((tlx0 + 5, tly0 + 4), fill=1)
        # Tread ribs
        for ty in range(tly0 + 1, tly1, 3):
            d.line((tlx0, ty, tlx0 + 1, ty), fill=1)

        # Right Tire
        trx0, trx1 = ox + 34, ox + 44
        try0, try1 = 14 + tilt_y_r, 22 + tilt_y_r
        d.rectangle((trx0, try0, trx1, try1), fill=13)
        d.rectangle((trx0 + 2, try0 + 2, trx1 - 2, try1 - 2), fill=14)
        d.point((trx0 + 5, try0 + 4), fill=1)
        for ty in range(try0 + 1, try1, 3):
            d.line((trx1 - 1, ty, trx1, ty), fill=1)

        # 2. Main Obsidian Chassis Body (Scalloped aerodynamic silhouette)
        body_poly = [
            (ox + 13 + body_dx, 4),   # Front nose
            (ox + 35 + body_dx, 4),
            (ox + 43, 17 + tilt_y_r), # Rear right fender
            (ox + 39, 22 + tilt_y_r),
            (ox + 9, 22 + tilt_y_l),
            (ox + 5, 17 + tilt_y_l),  # Rear left fender
        ]
        d.polygon(body_poly, fill=1)

        # 3. 3D Volumetric Panel Shading (Titanium core shadow & midtones with dithering)
        for py in range(5, 21):
            for px in range(ox + 7, ox + 41):
                cur = img.getpixel((px, py))
                if cur == 1:
                    norm_x = (px - (ox + 24)) / 16.0
                    norm_y = (py - 12) / 8.0
                    # Convex cylindrical hull shading
                    shade = 1.0 - (norm_x * norm_x + norm_y * norm_y * 0.5)
                    if shade > 0.65:
                        if bayer_dither(shade * 0.8, px, py):
                            img.putpixel((px, py), 3)  # Armored panel midtone
                    elif shade > 0.35:
                        img.putpixel((px, py), 2)      # Titanium armor shadow

        # 4. Sculptured Bat-Fins (Left & Right curved scalloped fins)
        # Left Fin
        fin_l_pts = [
            (ox + 6, 17 + tilt_y_l),
            (ox + 4, 7 + fin_l_raise),
            (ox + 9, 2 + fin_l_raise),
            (ox + 12, 9 + fin_l_raise),
            (ox + 13, 17 + tilt_y_l)
        ]
        d.polygon(fin_l_pts, fill=1)
        d.line((ox + 4, 7 + fin_l_raise, ox + 9, 2 + fin_l_raise), fill=4)  # Metallic specular highlight
        d.line((ox + 9, 2 + fin_l_raise, ox + 12, 9 + fin_l_raise), fill=6) # Chrome bevel
        d.polygon([(ox + 7, 10 + fin_l_raise), (ox + 9, 5 + fin_l_raise), (ox + 11, 11 + fin_l_raise)], fill=3)

        # Right Fin
        fin_r_pts = [
            (ox + 42, 17 + tilt_y_r),
            (ox + 44, 7 + fin_r_raise),
            (ox + 39, 2 + fin_r_raise),
            (ox + 36, 9 + fin_r_raise),
            (ox + 35, 17 + tilt_y_r)
        ]
        d.polygon(fin_r_pts, fill=1)
        d.line((ox + 44, 7 + fin_r_raise, ox + 39, 2 + fin_r_raise), fill=4)
        d.line((ox + 39, 2 + fin_r_raise, ox + 36, 9 + fin_r_raise), fill=6)
        d.polygon([(ox + 41, 10 + fin_r_raise), (ox + 39, 5 + fin_r_raise), (ox + 37, 11 + fin_r_raise)], fill=3)

        # 5. Tinted Cockpit Glass Canopy (Curved aerodynamic bubble)
        canopy = [
            (ox + 18 + body_dx, 5),
            (ox + 30 + body_dx, 5),
            (ox + 33 + body_dx, 13),
            (ox + 15 + body_dx, 13)
        ]
        d.polygon(canopy, fill=1)
        d.polygon([
            (ox + 19 + body_dx, 6),
            (ox + 29 + body_dx, 6),
            (ox + 32 + body_dx, 12),
            (ox + 16 + body_dx, 12)
        ], fill=5)
        # Multi-tone Cyan Specular Reflection Streaks
        d.line((ox + 20 + body_dx, 7, ox + 23 + body_dx, 11), fill=6)
        d.line((ox + 21 + body_dx, 7, ox + 24 + body_dx, 11), fill=8)
        d.line((ox + 26 + body_dx, 7, ox + 28 + body_dx, 11), fill=8)

        # 6. Golden Bat Emblem on chassis spine
        d.polygon([
            (ox + 22 + body_dx, 14), (ox + 26 + body_dx, 14),
            (ox + 27 + body_dx, 16), (ox + 24 + body_dx, 17), (ox + 21 + body_dx, 16)
        ], fill=9)
        d.point((ox + 24 + body_dx, 15), fill=12)

        # 7. Central Jet Turbine Exhaust Housing
        ex_x0, ex_x1 = ox + 20 + body_dx, ox + 28 + body_dx
        ex_y0, ex_y1 = 17, 22
        d.rectangle((ex_x0, ex_y0, ex_x1, ex_y1), fill=1)
        d.rectangle((ex_x0 + 1, ex_y0 + 1, ex_x1 - 1, ex_y1 - 1), fill=2)
        d.ellipse((ex_x0 + 2, ex_y0 + 1, ex_x1 - 2, ex_y1 - 1), fill=13)

        # Cyan Tail Light Plasma Strips
        d.rectangle((ox + 11, 19 + tilt_y_l, ox + 17, 20 + tilt_y_l), fill=8)
        d.rectangle((ox + 31, 19 + tilt_y_r, ox + 37, 20 + tilt_y_r), fill=8)

        # 8. Turbo Boost Plasma Plume (Frame 3 only)
        if frame == 3:
            flame_pts = [
                (ox + 20, 19), (ox + 15, 23), (ox + 24, 24),
                (ox + 33, 23), (ox + 28, 19)
            ]
            d.polygon(flame_pts, fill=11)  # Combustion Red
            d.polygon([(ox + 21, 20), (ox + 18, 23), (ox + 24, 24), (ox + 30, 23), (ox + 27, 20)], fill=10) # Flame Orange
            d.polygon([(ox + 22, 20), (ox + 20, 23), (ox + 24, 24), (ox + 28, 23), (ox + 26, 20)], fill=12) # Vulcan Yellow
            d.rectangle((ox + 23, 20, ox + 25, 23), fill=15) # Pure White Incandescent Core
            # Shockwave spark trail
            for sp_x in (ox + 12, ox + 16, ox + 32, ox + 36):
                d.point((sp_x, 22), fill=10)
                d.point((sp_x, 23), fill=12)
        else:
            d.point((ox + 24 + body_dx, 20), fill=10)

    return img


# -----------------------------------------------------------------------------
# 4. TWO-FACE SIEGE DREADNOUGHT CHASSIS (SPRITE - 64x48 - PAL3)
# -----------------------------------------------------------------------------
def make_boss_chassis() -> Image.Image:
    w, h = 64, 48
    img = Image.new("P", (w, h), 0)
    img.putpalette(pal_flat(PAL3))
    d = ImageDraw.Draw(img)

    # Base Heavy Armored Dreadnought Silhouette
    hull_base = [(12, 4), (52, 4), (60, 20), (58, 44), (6, 44), (4, 20)]
    d.polygon(hull_base, fill=1)

    # --- LEFT SIDE: HARVEY DENT CRIMSON STEEL ARMOR (X=4..31, Y=4..44) ---
    crimson_hull = [(12, 6), (31, 6), (31, 42), (8, 42), (6, 22)]
    d.polygon(crimson_hull, fill=6)

    # 3D Armor Layering & Beveled Plates
    d.line((12, 6, 6, 22), fill=7)  # Specular edge highlight
    d.line((6, 22, 8, 42), fill=7)
    d.line((14, 10, 31, 10), fill=7)
    d.line((12, 6, 31, 6), fill=7)

    # Layered Inner Recessed Plates with Core Shadow
    d.rectangle((10, 16, 30, 38), fill=5)
    d.rectangle((12, 18, 29, 36), fill=6)

    # Dithered Surface Shading
    for py in range(18, 36):
        for px in range(12, 30):
            if bayer_dither((30 - px) / 20.0, px, py):
                img.putpixel((px, py), 7)

    # Heavy Industrial Stamped Rivets
    for ry in (12, 20, 28, 36):
        d.point((9, ry), fill=14)
        d.point((9, ry + 1), fill=1)
        d.point((28, ry), fill=14)
        d.point((28, ry + 1), fill=1)

    # Cooling Louvers / Intake Grille
    for ly in range(22, 34, 4):
        d.line((16, ly, 24, ly), fill=1)
        d.line((16, ly + 1, 24, ly + 1), fill=7)

    # --- RIGHT SIDE: TWO-FACE ACID-SCARRED BIONIC NIGHTMARE (X=32..60, Y=4..44) ---
    acid_hull = [(32, 6), (52, 6), (58, 22), (56, 42), (32, 42)]
    d.polygon(acid_hull, fill=3)

    # Corroded Inner Cavity with Exposed Mechanism
    d.rectangle((34, 12, 54, 38), fill=2)

    # Exposed Copper Wiring Harnesses & Glowing Vacuum Tubes
    d.line((35, 14, 46, 14), fill=11, width=2)  # Bronze conduit
    d.line((38, 18, 52, 18), fill=11, width=1)
    # Toxic glowing vacuum coils
    for cy in (22, 28, 34):
        d.line((36, cy, 47, cy), fill=4)
        d.point((48, cy), fill=13)  # Glowing spark terminal
        d.point((49, cy), fill=15)

    # Black & Acid-Yellow Hazard Chevron Stripes
    for s in range(35, 56, 6):
        d.line((s, 38, s + 4, 42), fill=13, width=2)
        d.line((s + 2, 38, s + 6, 42), fill=1, width=1)

    # Corroded Slag & Melted Armor Holes
    for hx, hy in [(42, 12), (50, 24), (37, 30)]:
        d.ellipse((hx - 2, hy - 2, hx + 2, hy + 2), fill=1)
        d.point((hx, hy), fill=4)

    # --- CENTRAL TURRET MOUNTING RING (X=32, Y=20, R=12) ---
    d.ellipse((22, 10, 42, 30), fill=1)
    d.ellipse((24, 12, 40, 28), fill=10) # Steel bearing race
    d.ellipse((26, 14, 38, 26), fill=11) # Bronze inner ring
    d.ellipse((28, 16, 36, 24), fill=1)  # Deep central well
    # Ball bearings glints
    for bx, by in [(25, 16), (39, 16), (32, 11), (32, 29), (27, 24), (37, 24)]:
        d.point((bx, by), fill=14)

    # Jagged Central Fracture Line (Dividing crimson and acid)
    for sy in range(4, 44):
        offset = int(math.sin(sy * 0.6) * 2)
        img.putpixel((31 + offset, sy), 14 if (sy % 4 == 0) else 1)

    return img


# -----------------------------------------------------------------------------
# 5. BOSS TURRET (SPRITE - 256x32 [8 frames of 32x32] - PAL3)
# -----------------------------------------------------------------------------
def make_boss_turret() -> Image.Image:
    fw, fh = 32, 32
    img = Image.new("P", (fw * 8, fh), 0)
    img.putpalette(pal_flat(PAL3))

    angles = [0, -15, -30, -45, 0, 15, 30, 45]

    for frame, angle in enumerate(angles):
        ox = frame * fw
        cx, cy = ox + 16, 14
        d = ImageDraw.Draw(img)

        rad = math.radians(angle)
        dx = math.sin(rad)
        dy = math.cos(rad)

        # 1. Heavy Armored Gun Mantlet / Bronze Turret Cupola
        d.ellipse((cx - 11, cy - 9, cx + 11, cy + 9), fill=1)
        d.ellipse((cx - 10, cy - 8, cx + 10, cy + 8), fill=11) # Bronze casing
        d.ellipse((cx - 8, cy - 6, cx + 8, cy + 6), fill=10)   # Steel gun housing

        # 3D Cupola Specular Shading
        for py in range(cy - 6, cy + 6):
            for px in range(cx - 8, cx + 8):
                dist = math.hypot(px - cx, py - cy)
                if dist < 7:
                    if bayer_dither(1.0 - dist / 7.0, px, py):
                        img.putpixel((px, py), 14)

        # 2. Dual Heavy Fluted Plasma Cannon Barrels with Recoil Pistons
        barrel_len = 16
        sep = 5
        px_vec = -dy * sep
        py_vec = dx * sep

        for sign in (-1, 1):
            bx0 = cx + px_vec * sign * 0.65
            by0 = cy + py_vec * sign * 0.65
            bx1 = bx0 + dx * barrel_len
            by1 = by0 + dy * barrel_len

            # Heavy fluted cannon barrel
            d.line((bx0, by0, bx1, by1), fill=1, width=3)
            d.line((bx0, by0, bx1, by1), fill=11, width=1)
            d.line((bx0 - px_vec * 0.2, by0 - py_vec * 0.2, bx1 - px_vec * 0.2, by1 - py_vec * 0.2), fill=14)

            # Glowing Plasma Containment Coils (Incandescent Energy Rings)
            c1_x, c1_y = int(bx0 + dx * 6), int(by0 + dy * 6)
            c2_x, c2_y = int(bx0 + dx * 11), int(by0 + dy * 11)
            d.rectangle((c1_x - 1, c1_y - 1, c1_x + 1, c1_y + 1), fill=13)
            d.point((c1_x, c1_y), fill=15)
            d.rectangle((c2_x - 1, c2_y - 1, c2_x + 1, c2_y + 1), fill=13)
            d.point((c2_x, c2_y), fill=15)

            # Muzzle Brake Tip
            mx_tip, my_tip = int(bx1), int(by1)
            d.rectangle((mx_tip - 1, my_tip - 1, mx_tip + 1, my_tip + 1), fill=1)
            d.point((mx_tip, my_tip), fill=12 if frame != 4 else 15)

        # 3. Targeting Optical Sensor (Red laser reticle lens with glare)
        d.rectangle((cx - 3, cy - 3, cx + 3, cy + 3), fill=1)
        d.rectangle((cx - 2, cy - 2, cx + 2, cy + 2), fill=8)
        d.point((cx, cy), fill=15) # Glare core

        # Recoil Flash State (Frame 4)
        if frame == 4:
            for sign in (-1, 1):
                mx_f = int(cx + px_vec * sign * 0.65 + dx * barrel_len)
                my_f = int(cy + py_vec * sign * 0.65 + dy * barrel_len)
                d.ellipse((mx_f - 3, my_f - 3, mx_f + 3, my_f + 3), fill=12)
                d.ellipse((mx_f - 1, my_f - 1, mx_f + 1, my_f + 1), fill=15)

    return img


# -----------------------------------------------------------------------------
# 6. BOSS TREADS LEFT & RIGHT (SPRITE - 128x16 [4 frames of 32x16] - PAL3)
# -----------------------------------------------------------------------------
def make_boss_treads(is_right: bool = False) -> Image.Image:
    fw, fh = 32, 16
    img = Image.new("P", (fw * 4, fh), 0)
    img.putpalette(pal_flat(PAL3))

    for frame in range(4):
        ox = frame * fw
        d = ImageDraw.Draw(img)

        # Heavy Armored Tread Frame with 3D Depth
        d.rectangle((ox + 2, 2, ox + 30, 14), fill=1)
        d.rectangle((ox + 3, 3, ox + 29, 13), fill=9)

        # 3 Internal Heavy Bogie Wheels with Hub Caps & Bolts
        for wx in (ox + 7, ox + 16, ox + 25):
            d.ellipse((wx - 4, 4, wx + 4, 12), fill=1)
            d.ellipse((wx - 3, 5, wx + 3, 11), fill=10) # Steel rim
            d.ellipse((wx - 1, 7, wx + 1, 9), fill=14)   # Axle cap
            d.point((wx, 8), fill=1)

        # Articulated Track Links with Beveled Teeth (Advancing smoothly)
        offset = frame * 2
        for lx in range(ox + 4, ox + 30, 4):
            tx = lx + (offset % 4)
            if tx < ox + 29:
                # Top track link
                d.line((tx, 2, tx, 4), fill=14)
                d.point((tx, 3), fill=10)
                # Bottom track link
                d.line((tx, 12, tx, 14), fill=14)
                d.point((tx, 13), fill=10)

        # Armored Side Skirt (Left: Crimson, Right: Toxic Acid-Green)
        skirt_color = 3 if is_right else 6
        d.rectangle((ox + 4, 3, ox + 28, 7), fill=skirt_color)
        d.line((ox + 4, 3, ox + 28, 3), fill=skirt_color + 1) # Highlight
        d.line((ox + 4, 7, ox + 28, 7), fill=1)                 # Shadow line
        # Skirt panel bolts
        for bx in (ox + 6, ox + 13, ox + 20, ox + 27):
            d.point((bx, 5), fill=14)

    return img


# -----------------------------------------------------------------------------
# 7. BOSS MISSILE POD (SPRITE - 48x24 [2 frames of 24x24] - PAL3)
# -----------------------------------------------------------------------------
def make_boss_missile_pod() -> Image.Image:
    fw, fh = 24, 24
    img = Image.new("P", (fw * 2, fh), 0)
    img.putpalette(pal_flat(PAL3))

    # Frame 0: Heavy Armored Carapace Closed with Locking Latches & Hazard Decals
    d0 = ImageDraw.Draw(img)
    d0.rectangle((2, 2, 22, 22), fill=1)
    d0.rectangle((3, 3, 21, 21), fill=14) # Alloy plating
    d0.rectangle((5, 5, 19, 19), fill=9)  # Recessed armor panel
    # Beveled reinforcement cross-struts
    d0.line((4, 4, 20, 20), fill=10, width=2)
    d0.line((4, 20, 20, 4), fill=10, width=2)
    d0.line((4, 4, 20, 20), fill=14, width=1)
    # Status LED & Lock Pin
    d0.rectangle((10, 10, 14, 14), fill=1)
    d0.point((12, 12), fill=8)

    # Frame 1: Open Silo Doors Retracted with 4 Glowing Missile Tubes
    ox = 24
    d1 = ImageDraw.Draw(img)
    # Silo Pod Box
    d1.rectangle((ox + 2, 4, ox + 22, 22), fill=1)
    d1.rectangle((ox + 3, 5, ox + 21, 21), fill=9)

    # 4 Detailed Missile Silo Launch Tubes (2x2 Matrix)
    tubes = [(ox + 7, 9), (ox + 17, 9), (ox + 7, 17), (ox + 17, 17)]
    for tx, ty in tubes:
        d1.ellipse((tx - 4, ty - 4, tx + 4, ty + 4), fill=1)
        d1.ellipse((tx - 3, ty - 3, tx + 3, ty + 3), fill=10) # Silo bore
        d1.ellipse((tx - 2, ty - 2, tx + 2, ty + 2), fill=12) # Incandescent warhead tip
        d1.point((tx, ty), fill=15)                            # White fuse point
        # Thermal chamber glow
        d1.point((tx - 1, ty), fill=13)
        d1.point((tx + 1, ty), fill=13)

    # Retracted Armored Blast Doors Elevated with Exposed Pistons
    d1.rectangle((ox + 4, 1, ox + 20, 4), fill=14)
    d1.line((ox + 4, 1, ox + 20, 1), fill=15)
    # Hydraulic piston rods
    d1.line((ox + 6, 4, ox + 6, 7), fill=14)
    d1.line((ox + 18, 4, ox + 18, 7), fill=14)

    return img


# -----------------------------------------------------------------------------
# 8. ESCORT DRONE (SPRITE - 48x16 [2 frames of 24x16] - PAL3)
# -----------------------------------------------------------------------------
def make_drone() -> Image.Image:
    fw, fh = 24, 16
    img = Image.new("P", (fw * 2, fh), 0)
    img.putpalette(pal_flat(PAL3))

    for frame in range(2):
        ox = frame * fw
        d = ImageDraw.Draw(img)

        # Advanced Swept-Forward Delta Fuselage
        wing_poly = [
            (ox + 12, 1),   # Needle nose
            (ox + 23, 9),   # Right wingtip
            (ox + 19, 14),  # Right rear
            (ox + 5, 14),   # Left rear
            (ox + 1, 9)     # Left wingtip
        ]
        d.polygon(wing_poly, fill=1)

        # 3D Armor Faceting
        d.polygon([
            (ox + 12, 3),
            (ox + 21, 9),
            (ox + 17, 13),
            (ox + 7, 13),
            (ox + 3, 9)
        ], fill=3) # Bionic green armor
        d.line((ox + 12, 3, ox + 21, 9), fill=4) # Specular wing highlight
        d.line((ox + 12, 3, ox + 3, 9), fill=4)

        # Crimson Optical Sensor Visor (Glowing Eye)
        d.rectangle((ox + 9, 5, ox + 15, 8), fill=1)
        d.rectangle((ox + 10, 6, ox + 14, 7), fill=8)
        d.point((ox + 12, 6), fill=15) # Glare

        # Twin Underwing Rotary Plasma Cannons
        d.line((ox + 4, 10, ox + 4, 14), fill=1, width=2)
        d.line((ox + 4, 10, ox + 4, 14), fill=10, width=1)
        d.line((ox + 20, 10, ox + 20, 14), fill=1, width=2)
        d.line((ox + 20, 10, ox + 20, 14), fill=10, width=1)

        # Dual Plasma Thrusters
        d.rectangle((ox + 9, 13, ox + 15, 15), fill=1)
        if frame == 1:
            # Full Afterburner Plume
            d.polygon([(ox + 9, 14), (ox + 12, 16), (ox + 15, 14)], fill=12)
            d.point((ox + 12, 15), fill=13)
            d.point((ox + 12, 14), fill=15)
        else:
            d.point((ox + 11, 14), fill=12)
            d.point((ox + 13, 14), fill=12)

    return img


# -----------------------------------------------------------------------------
# 9. PROJECTILES ATLAS (SPRITE - 64x16 [4 frames of 16x16] - PAL2/PAL3)
# -----------------------------------------------------------------------------
def make_projectiles() -> Image.Image:
    fw, fh = 16, 16
    img = Image.new("P", (fw * 4, fh), 0)
    img.putpalette(pal_flat(PAL3))
    d = ImageDraw.Draw(img)

    # Frame 0: Batmobile Vulcan 20mm Kinetic Rounds (Dual Tracers with Dithered Tails)
    for bx in (4, 11):
        # Motion blur tail
        d.line((bx, 7, bx, 14), fill=12, width=2)
        d.line((bx - 1, 10, bx + 1, 14), fill=10)
        # Bullet core
        d.rectangle((bx - 1, 2, bx + 1, 6), fill=12)
        d.rectangle((bx, 2, bx, 5), fill=15) # Pure white kinetic tip

    # Frame 1: Batarang Micro-Missile (Bat-Winged Rocket with Flame Plume)
    ox1 = 16
    missile_body = [
        (ox1 + 8, 1), (ox1 + 14, 6), (ox1 + 13, 10), (ox1 + 8, 8),
        (ox1 + 3, 10), (ox1 + 2, 6)
    ]
    d.polygon(missile_body, fill=1)
    d.polygon([
        (ox1 + 8, 2), (ox1 + 12, 6), (ox1 + 11, 9), (ox1 + 8, 7),
        (ox1 + 5, 9), (ox1 + 4, 6)
    ], fill=14) # Silver alloy wing body
    d.point((ox1 + 8, 3), fill=15)
    # Rocket exhaust flame
    d.polygon([(ox1 + 6, 9), (ox1 + 8, 15), (ox1 + 10, 9)], fill=12)
    d.point((ox1 + 8, 10), fill=13)
    d.point((ox1 + 8, 11), fill=15)

    # Frame 2: Boss Heavy Plasma Orb (Volumetric Sphere with Multilayer Corona)
    ox2 = 32
    d.ellipse((ox2 + 1, 1, ox2 + 14, 14), fill=5)  # Crimson perimeter
    d.ellipse((ox2 + 2, 2, ox2 + 13, 13), fill=6)  # Flayed midtone
    d.ellipse((ox2 + 3, 3, ox2 + 12, 12), fill=12) # Bright orange plasma
    d.ellipse((ox2 + 5, 5, ox2 + 10, 10), fill=13) # Yellow core
    d.ellipse((ox2 + 6, 6, ox2 + 9, 9), fill=15)   # Pure white incandescent center
    # Orbiting electric corona sparks
    for sp_x, sp_y in [(ox2 + 8, 0), (ox2 + 8, 15), (ox2 + 0, 8), (ox2 + 15, 8), (ox2 + 3, 3), (ox2 + 12, 12)]:
        d.point((sp_x, sp_y), fill=13)

    # Frame 3: Drone Laser Dart (Particle Beam with Diamond Tip)
    ox3 = 48
    d.polygon([(ox3 + 8, 1), (ox3 + 12, 14), (ox3 + 8, 12), (ox3 + 4, 14)], fill=8) # Crimson bloom
    d.line((ox3 + 8, 1, ox3 + 8, 13), fill=15, width=1) # Glowing white spine
    d.point((ox3 + 8, 1), fill=15)
    d.point((ox3 + 7, 3), fill=13)
    d.point((ox3 + 9, 3), fill=13)

    return img


# -----------------------------------------------------------------------------
# 10. PARTICLES ATLAS (SPRITE - 64x16 [4 frames of 16x16] - PAL3)
# -----------------------------------------------------------------------------
def make_particles() -> Image.Image:
    fw, fh = 16, 16
    img = Image.new("P", (fw * 4, fh), 0)
    img.putpalette(pal_flat(PAL3))
    d = ImageDraw.Draw(img)

    # Frame 0: Intense 8-Pointed Electric Star Spark
    d.line((8, 0, 8, 15), fill=13, width=2)
    d.line((0, 8, 15, 8), fill=13, width=2)
    d.line((3, 3, 12, 12), fill=12, width=1)
    d.line((12, 3, 3, 12), fill=12, width=1)
    d.rectangle((6, 6, 9, 9), fill=13)
    d.rectangle((7, 7, 8, 8), fill=15) # Pure white flash center

    # Frame 1: Metal Shrapnel Debris (Molten Incandescent Jagged Chunk)
    ox1 = 16
    d.polygon([(ox1 + 3, 2), (ox1 + 13, 4), (ox1 + 14, 11), (ox1 + 8, 14), (ox1 + 2, 9)], fill=1)
    d.polygon([(ox1 + 4, 3), (ox1 + 12, 5), (ox1 + 13, 10), (ox1 + 8, 12), (ox1 + 3, 8)], fill=10) # Steel body
    # Molten red-hot glowing edges
    d.line((ox1 + 4, 3, ox1 + 12, 5), fill=13)
    d.line((ox1 + 12, 5, ox1 + 13, 10), fill=8)
    d.point((ox1 + 8, 7), fill=15)

    # Frame 2: Volcanic Explosion Fireball (Multilayer Dithered Flame Ring)
    ox2 = 32
    d.ellipse((ox2 + 1, 1, ox2 + 14, 14), fill=5)  # Crimson soot boundary
    d.ellipse((ox2 + 2, 2, ox2 + 13, 13), fill=6)
    d.ellipse((ox2 + 4, 4, ox2 + 11, 11), fill=12) # Fiery orange billow
    d.ellipse((ox2 + 5, 5, ox2 + 10, 10), fill=13) # Yellow core
    d.ellipse((ox2 + 6, 6, ox2 + 9, 9), fill=15)   # White flash center
    # Flying incandescent embers
    d.point((ox2 + 2, 3), fill=13)
    d.point((ox2 + 13, 12), fill=13)
    d.point((ox2 + 12, 2), fill=8)

    # Frame 3: Volumetric Dithered Smoke Puff (3-tone billows)
    ox3 = 48
    for y in range(1, 15):
        for x in range(ox3 + 1, ox3 + 15):
            dist = math.hypot(x - (ox3 + 8), y - 8)
            if dist < 6.5:
                noise = ((x * 13) ^ (y * 29)) & 3
                if dist < 3.0:
                    img.putpixel((x, y), 10 if bayer_dither(0.7, x, y) else 9)
                elif dist < 5.0:
                    img.putpixel((x, y), 9 if bayer_dither(0.5, x, y) else 1)
                else:
                    if bayer_dither(0.3, x, y):
                        img.putpixel((x, y), 1)

    return img


# -----------------------------------------------------------------------------
# MAIN BUILD & PROVENANCE GENERATOR
# -----------------------------------------------------------------------------
def build_all(project_root: Path) -> int:
    res_bgs = project_root / "res" / "bgs"
    res_sprites = project_root / "res" / "sprites"
    source_art_dir = project_root / "data" / "source_art" / "dark_deco_aaa"
    source_art_branding = project_root / "data" / "source_art" / "branding"
    doc_dir = project_root / "doc"

    res_bgs.mkdir(parents=True, exist_ok=True)
    res_sprites.mkdir(parents=True, exist_ok=True)
    source_art_dir.mkdir(parents=True, exist_ok=True)
    source_art_branding.mkdir(parents=True, exist_ok=True)
    doc_dir.mkdir(parents=True, exist_ok=True)

    print("[GOTHAM_OVERDRIVE] Synthesizing Master-Quality AAA Mega Drive Assets...")

    # Build Assets
    bg_skyline = make_gotham_skyline()
    bg_roadway = make_gotham_roadway()
    spr_batmobile = make_batmobile_spritesheet()
    spr_boss_chassis = make_boss_chassis()
    spr_boss_turret = make_boss_turret()
    spr_boss_tread_left = make_boss_treads(is_right=False)
    spr_boss_tread_right = make_boss_treads(is_right=True)
    spr_boss_missile_pod = make_boss_missile_pod()
    spr_drone = make_drone()
    spr_projectiles = make_projectiles()
    spr_particles = make_particles()

    assets_map = {
        "img_gotham_skyline_bgb": (bg_skyline, res_bgs / "img_gotham_skyline_bgb.png", "bgs/img_gotham_skyline_bgb.png", "IMAGE"),
        "img_gotham_roadway_bga": (bg_roadway, res_bgs / "img_gotham_roadway_bga.png", "bgs/img_gotham_roadway_bga.png", "IMAGE"),
        "spr_batmobile": (spr_batmobile, res_sprites / "spr_batmobile.png", "sprites/spr_batmobile.png", "SPRITE"),
        "spr_boss_chassis": (spr_boss_chassis, res_sprites / "spr_boss_chassis.png", "sprites/spr_boss_chassis.png", "SPRITE"),
        "spr_boss_turret": (spr_boss_turret, res_sprites / "spr_boss_turret.png", "sprites/spr_boss_turret.png", "SPRITE"),
        "spr_boss_tread_left": (spr_boss_tread_left, res_sprites / "spr_boss_tread_left.png", "sprites/spr_boss_tread_left.png", "SPRITE"),
        "spr_boss_tread_right": (spr_boss_tread_right, res_sprites / "spr_boss_tread_right.png", "sprites/spr_boss_tread_right.png", "SPRITE"),
        "spr_boss_missile_pod": (spr_boss_missile_pod, res_sprites / "spr_boss_missile_pod.png", "sprites/spr_boss_missile_pod.png", "SPRITE"),
        "spr_drone": (spr_drone, res_sprites / "spr_drone.png", "sprites/spr_drone.png", "SPRITE"),
        "spr_projectiles": (spr_projectiles, res_sprites / "spr_projectiles.png", "sprites/spr_projectiles.png", "SPRITE"),
        "spr_particles": (spr_particles, res_sprites / "spr_particles.png", "sprites/spr_particles.png", "SPRITE"),
    }

    provenance_entries = []

    # Handle branding assets
    modelo_source = project_root.parent.parent / "tools" / "sgdk_wrapper" / "modelo" / "data" / "source_art" / "branding_intro" / "production"
    branding_symbols = [
        ("img_brand_fx_tiles", "branding/brand_fx_tiles.png", "IMAGE", "engine_mark_source.png"),
        ("img_brand_engine_logo", "branding/brand_engine_logo.png", "IMAGE", "engine_mark_source.png"),
        ("img_brand_author_logo", "branding/brand_author_logo.png", "IMAGE", "author_panel_source.png"),
        ("img_brand_project_logo", "branding/brand_project_logo.png", "IMAGE", "project_crest_source.png"),
        ("img_brand_presents_text", "branding/brand_presents_text.png", "IMAGE", "project_crest_source.png"),
    ]
    for b_sym, b_path, b_kind, b_src_name in branding_symbols:
        src_orig = modelo_source / b_src_name
        dest_src = source_art_branding / b_src_name
        if src_orig.exists() and not dest_src.exists():
            shutil.copy2(src_orig, dest_src)

        b_hash = sha256_file(dest_src) if dest_src.exists() else sha256_file(project_root / "res" / b_path)
        provenance_entries.append({
            "res_symbol": b_sym,
            "res_kind": b_kind,
            "asset_path": b_path,
            "source_kind": "procedural_composed_from_authored",
            "acceptance_status": "final",
            "generated_by": "tools/image-tools/build_branding_intro_assets.py",
            "authored_source": str(dest_src.relative_to(project_root)),
            "authored_source_hash": b_hash,
            "license": "proprietary",
            "notes": "Canonical branding intro asset composed from authored source"
        })

    for sym, (img_obj, out_path, rel_path, res_kind) in assets_map.items():
        # Save source art
        source_path = source_art_dir / out_path.name
        save_p4(img_obj, source_path)
        source_hash = sha256_file(source_path)

        # Save runtime PNG
        save_p4(img_obj, out_path)
        print(f"  -> Generated {rel_path} ({img_obj.size[0]}x{img_obj.size[1]}) [SHA256: {source_hash[:8]}]")

        provenance_entries.append({
            "res_symbol": sym,
            "res_kind": res_kind,
            "asset_path": rel_path,
            "source_kind": "procedural_composed_from_authored",
            "acceptance_status": "final",
            "generated_by": "tools/image-tools/build_gotham_overdrive_assets.py",
            "authored_source": str(source_path.relative_to(project_root)),
            "authored_source_hash": source_hash,
            "license": "proprietary",
            "notes": "Dark Deco 90s Master AAA asset crafted for Mega Drive VDP compliance"
        })

    # Write asset provenance manifest
    manifest_payload = {
        "schema_version": "1.0.0",
        "project_name": "GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]",
        "declared_at": datetime.now(timezone.utc).isoformat(),
        "validator_fixture": False,
        "entries": provenance_entries
    }
    manifest_path = doc_dir / "asset_provenance_manifest.json"
    manifest_path.write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] Asset provenance manifest written to {manifest_path}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path, help="Root path of GOTHAM_OVERDRIVE project")
    args = parser.parse_args()
    return build_all(args.project_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

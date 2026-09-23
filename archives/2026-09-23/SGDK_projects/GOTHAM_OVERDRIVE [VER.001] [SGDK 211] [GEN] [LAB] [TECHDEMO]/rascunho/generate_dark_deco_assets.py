#!/usr/bin/env python3
import os
import sys
from PIL import Image

def create_palette_bytes(colors):
    flat = []
    for c in colors:
        flat.extend(c[:3])
    while len(flat) < 768:
        flat.extend((0, 0, 0))
    return bytes(flat)

# 9-bit RGB quantized palettes (16 colors each)
PAL0_SKYLINE = [
    (0, 0, 0),        # 0: transparent / black
    (0, 0, 34),       # 1: deepest navy
    (0, 34, 68),      # 2: midnight blue
    (34, 34, 68),     # 3: gothic slate
    (34, 68, 102),    # 4: fog blue
    (68, 68, 102),    # 5: spire shadow
    (68, 102, 136),   # 6: skyscraper mid
    (102, 136, 170),  # 7: skyscraper highlight
    (34, 0, 68),      # 8: gothic violet
    (102, 34, 102),   # 9: purple cloud
    (170, 136, 34),   # 10: amber window
    (238, 204, 68),   # 11: brilliant gold window
    (136, 170, 204),  # 12: cloud silver rim
    (204, 238, 238),  # 13: Bat-Signal spotlight beam
    (238, 238, 238),  # 14: pure white moon
    (0, 0, 0)         # 15: black
]

PAL1_ROADWAY = [
    (0, 0, 0),        # 0: transparent
    (34, 34, 34),     # 1: dark asphalt
    (68, 68, 68),     # 2: asphalt mid
    (102, 102, 102),  # 3: concrete curb
    (136, 136, 136),  # 4: guardrail
    (170, 170, 170),  # 5: steel truss
    (0, 68, 102),     # 6: expressway shadow
    (0, 136, 170),    # 7: cable cyan
    (0, 204, 238),    # 8: neon cyan divider
    (238, 170, 0),    # 9: amber reflector
    (238, 238, 0),    # 10: yellow center stripe
    (136, 34, 34),    # 11: red asphalt brake reflection
    (204, 68, 68),    # 12: warning beacon
    (34, 68, 68),     # 13: distant bridge pillar
    (204, 204, 204),  # 14: steel girder light
    (238, 238, 238)   # 15: pure white text / lamp burst
]

PAL2_HERO = [
    (0, 0, 0),        # 0: transparent
    (0, 0, 0),        # 1: obsidian black
    (34, 34, 68),     # 2: dark armor shadow
    (68, 68, 102),    # 3: armor highlight
    (102, 102, 136),  # 4: titanium body panel
    (136, 170, 204),  # 5: glass reflection
    (204, 238, 238),  # 6: cockpit frame
    (0, 136, 204),    # 7: cyan dash glow
    (0, 238, 238),    # 8: cyan plasma headlamp
    (238, 204, 0),    # 9: gold bat insignia
    (238, 102, 0),    # 10: turbine orange flame
    (238, 34, 0),     # 11: exhaust core red
    (238, 238, 68),   # 12: vulcan tracer yellow
    (34, 34, 34),     # 13: tire rubber
    (170, 170, 170),  # 14: wheel alloy
    (238, 238, 238)   # 15: muzzle flash white
]

PAL3_BOSS = [
    (0, 0, 0),        # 0: transparent
    (0, 0, 0),        # 1: black shadow
    (34, 68, 34),     # 2: toxic green shadow
    (68, 136, 68),    # 3: green armor mid
    (102, 204, 102),  # 4: green highlight
    (68, 0, 0),       # 5: crimson shadow
    (136, 34, 34),    # 6: scarred crimson mid
    (204, 68, 68),    # 7: crimson highlight
    (238, 34, 34),    # 8: red sensor / laser
    (51, 51, 51),     # 9: tread steel dark
    (102, 102, 102),  # 10: tread link
    (170, 136, 68),   # 11: bronze turret plating
    (238, 170, 0),    # 12: plasma fireball orange
    (238, 238, 0),    # 13: electrical spark yellow
    (136, 136, 170),  # 14: radar alloy
    (238, 238, 238)   # 15: shockwave white
]

def save_indexed_image(img, palette_colors, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.putpalette(create_palette_bytes(palette_colors))
    img.save(out_path)
    print(f"[OK] Saved: {out_path} ({img.width}x{img.height})")

def generate_skyline_bg(out_path):
    w, h = 320, 224
    img = Image.new('P', (w, h), 0)

    # 0..79: Dark Deco Night Sky with Gothic Skyline
    for y in range(80):
        for x in range(w):
            if y < 18:
                col = 1 if ((x + y) % 4 != 0) else 2
            elif y < 42:
                col = 2 if ((x + y) % 3 != 0) else 3
            else:
                col = 3 if ((x + y) % 2 == 0) else 4
            img.putpixel((x, y), col)

    # Giant Moon & Bat-Signal in sky (x=240, y=30)
    cx, cy, radius = 240, 30, 24
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if 0 <= x < w and 0 <= y < 80:
                dist_sq = (x - cx)**2 + (y - cy)**2
                if dist_sq <= radius**2:
                    if dist_sq > (radius - 2)**2:
                        img.putpixel((x, y), 12)
                    elif dist_sq > (radius - 4)**2:
                        img.putpixel((x, y), 13)
                    else:
                        img.putpixel((x, y), 14)
                        # Bat silhouette inside moon
                        dx, dy = abs(x - cx), y - cy
                        if dx < 15 and abs(dy) < 9:
                            if dy > 0 or (dx > 5 and dy > -5):
                                img.putpixel((x, y), 1)

    # Bat-Signal Searchlight Beam sweeping diagonally across skyline
    for y in range(8, 80):
        beam_x_start = int(240 - (80 - y) * 2.4)
        beam_x_end = int(240 - (80 - y) * 0.9)
        for x in range(beam_x_start, beam_x_end):
            if 0 <= x < w:
                if (x + y) % 2 == 0:
                    curr = img.getpixel((x, y))
                    if curr in (1, 2, 3, 4):
                        img.putpixel((x, y), 13 if (x + y) % 4 == 0 else 6)

    # Dark Deco Gothic Skyscrapers (Silhouettes)
    buildings = [
        (0, 44, 24, 79), (20, 36, 26, 79), (44, 48, 22, 79), (62, 24, 30, 79),
        (88, 40, 26, 79), (110, 16, 36, 79), (142, 32, 28, 79), (166, 44, 24, 79),
        (186, 26, 32, 79), (214, 48, 24, 79), (234, 34, 32, 79), (262, 20, 34, 79),
        (292, 42, 28, 79)
    ]
    for bx, by, bw, bh in buildings:
        for y in range(by, bh + 1):
            for x in range(bx, bx + bw):
                if 0 <= x < w:
                    # Gothic spire tip
                    if y < by + 8:
                        if abs(x - (bx + bw//2)) > (y - by):
                            continue
                    edge = (x == bx or x == bx + bw - 1 or y == by)
                    img.putpixel((x, y), 7 if edge else (5 if (x % 4 == 0) else 1))
                    # Lit Art Deco amber windows
                    if y > by + 10 and y < bh - 4:
                        if (x % 6 in (2, 3)) and (y % 7 in (2, 3, 4)):
                            img.putpixel((x, y), 11 if (x + y) % 3 == 0 else 10)

    # 80..223: Lower abyss & background bridge piers
    for y in range(80, h):
        for x in range(w):
            img.putpixel((x, y), 1 if (y % 4 == 0) else 0)

    # Bridge vertical steel pillars
    for px in range(16, w, 40):
        for y in range(80, h):
            img.putpixel((px, y), 6)
            img.putpixel((px + 1, y), 5)
            img.putpixel((px + 2, y), 1)

    save_indexed_image(img, PAL0_SKYLINE, out_path)

def generate_roadway_bga(out_path):
    w, h = 320, 224
    img = Image.new('P', (w, h), 0)

    # 0..79: Transparent (shows Layer B skyline)
    for y in range(80):
        for x in range(w):
            img.putpixel((x, y), 0)

    # Horizon glowing neon line at Y=80
    for x in range(w):
        img.putpixel((x, 79), 8 if (x % 8 < 4) else 0)
        img.putpixel((x, 80), 5)

    # 81..223: 3D Perspective Roadway & Suspension Bridge Deck
    for y in range(81, h):
        progress = (y - 80) / (h - 80)
        half_road_w = int(24 + progress * 132)
        cx = 160
        left_edge = cx - half_road_w
        right_edge = cx + half_road_w

        for x in range(w):
            if x < left_edge or x > right_edge:
                # Outside road: Bridge suspension rail & abyss
                if x < left_edge - 10 or x > right_edge + 10:
                    img.putpixel((x, y), 0)
                else:
                    img.putpixel((x, y), 5 if (y % 2 == 0) else 4)
            else:
                lane_offset = abs(x - cx)
                is_center = lane_offset < int(2 + progress * 3)
                is_sublane = abs(lane_offset - int(half_road_w * 0.5)) < int(1 + progress * 2)

                if is_center:
                    img.putpixel((x, y), 10 if (y % 16 < 8) else 2) # Yellow center dashes
                elif is_sublane:
                    img.putpixel((x, y), 8 if (y % 12 < 6) else 2)  # Cyan sublane dashes
                elif abs(x - left_edge) < 4 or abs(x - right_edge) < 4:
                    img.putpixel((x, y), 9 if (y % 8 < 4) else 12)  # Amber curb
                else:
                    img.putpixel((x, y), 2 if ((x + y * 2) % 6 == 0) else 1)

    save_indexed_image(img, PAL1_ROADWAY, out_path)

def generate_batmobile_sprite(out_path):
    # 4 frames of 48x24: 192x24 (Frame 0: Straight, Frame 1: Tilt Left, Frame 2: Tilt Right, Frame 3: Turbo Boost)
    fw, fh = 48, 24
    w, h = fw * 4, fh
    img = Image.new('P', (w, h), 0)

    for f in range(4):
        ox = f * fw
        # Aerodynamic Batmobile Body
        for y in range(4, 20):
            # Left Bat-Fin
            img.putpixel((ox + 8, y), 1)
            img.putpixel((ox + 9, y), 3)
            # Right Bat-Fin
            img.putpixel((ox + 39, y), 1)
            img.putpixel((ox + 38, y), 3)

        # Main chassis hull
        for y in range(7, 21):
            for x in range(12, 36):
                img.putpixel((ox + x, y), 1)

        # Titanium armor paneling & highlights
        for x in range(14, 34):
            img.putpixel((ox + x, 8), 2)
            img.putpixel((ox + x, 9), 3)
            img.putpixel((ox + x, 19), 2)

        # Cockpit canopy (Cyan neon glass)
        for y in range(10, 15):
            for x in range(20, 28):
                img.putpixel((ox + x, y), 8 if (x in (20, 27) or y == 10) else 7)

        # Gold Bat Emblem
        img.putpixel((ox + 23, 16), 9)
        img.putpixel((ox + 24, 16), 9)
        img.putpixel((ox + 22, 17), 9)
        img.putpixel((ox + 25, 17), 9)

        # Twin Plasma Headlamps
        img.putpixel((ox + 14, 20), 8)
        img.putpixel((ox + 15, 20), 15)
        img.putpixel((ox + 32, 20), 15)
        img.putpixel((ox + 33, 20), 8)

        # Wheels (Left & Right)
        for y in range(6, 11):
            img.putpixel((ox + 6, y), 13)
            img.putpixel((ox + 7, y), 14)
            img.putpixel((ox + 40, y), 14)
            img.putpixel((ox + 41, y), 13)
        for y in range(15, 20):
            img.putpixel((ox + 6, y), 13)
            img.putpixel((ox + 7, y), 14)
            img.putpixel((ox + 40, y), 14)
            img.putpixel((ox + 41, y), 13)

        # Turbine Jet Exhaust Flame
        flame_len = 10 if f == 3 else (6 if f % 2 == 1 else 4)
        for fx in range(flame_len):
            fy = 5 - fx // 2
            if fy < 0: fy = 0
            for dy in range(12 - fy, 14 + fy):
                col = 15 if fx < 2 else (10 if fx < 5 else 11)
                img.putpixel((ox + 23 - fx, dy), col)

    save_indexed_image(img, PAL2_HERO, out_path)

def generate_boss_sprites(sprites_dir):
    # 1. Boss Chassis (64x48)
    img_chassis = Image.new('P', (64, 48), 0)
    for y in range(6, 44):
        for x in range(4, 60):
            if (x < 10 and (y < 12 or y > 38)) or (x > 54 and (y < 12 or y > 38)):
                continue
            is_left = x < 32
            base_col = 6 if is_left else 3
            edge_col = 7 if is_left else 4
            dark_col = 5 if is_left else 2

            if x == 4 or x == 59 or y == 6 or y == 43:
                img_chassis.putpixel((x, y), edge_col)
            elif (x + y) % 4 == 0:
                img_chassis.putpixel((x, y), dark_col)
            else:
                img_chassis.putpixel((x, y), base_col)

    # Hazard stripes and reactor core
    for y in range(18, 32):
        for x in range(24, 40):
            img_chassis.putpixel((x, y), 10 if (x + y) % 6 < 3 else 1)

    for y in range(22, 28):
        for x in range(29, 35):
            img_chassis.putpixel((x, y), 8 if (x in (29, 34) or y in (22, 27)) else 15)

    save_indexed_image(img_chassis, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_chassis.png"))

    # 2. Boss Turret (8 frames of 32x32: 256x32)
    img_turret = Image.new('P', (256, 32), 0)
    for f in range(8):
        ox = f * 32
        cx, cy = ox + 16, 16
        for y in range(8, 24):
            for x in range(ox + 8, ox + 24):
                if (x - cx)**2 + (y - cy)**2 <= 49:
                    img_turret.putpixel((x, y), 11 if (x + y) % 2 == 0 else 1)
        angle_offsets = [
            (0, 10), (-3, 9), (-6, 7), (-8, 4),
            (0, 10), (3, 9), (6, 7), (8, 4)
        ]
        dx, dy = angle_offsets[f]
        for step in range(12):
            bx1 = cx - 3 + int(dx * step / 10)
            by1 = cy + int(dy * step / 10)
            bx2 = cx + 3 + int(dx * step / 10)
            by2 = cy + int(dy * step / 10)
            if 0 <= bx1 < ox + 32 and 0 <= by1 < 32: img_turret.putpixel((bx1, by1), 10)
            if 0 <= bx2 < ox + 32 and 0 <= by2 < 32: img_turret.putpixel((bx2, by2), 10)
        img_turret.putpixel((cx - 3 + dx, cy + dy), 15)
        img_turret.putpixel((cx + 3 + dx, cy + dy), 15)

    save_indexed_image(img_turret, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_turret.png"))

    # 3. Boss Treads (4 frames of 32x16: 128x16)
    img_treads = Image.new('P', (128, 16), 0)
    for f in range(4):
        ox = f * 32
        for y in range(2, 14):
            for x in range(2, 30):
                img_treads.putpixel((ox + x, y), 9)
        for x in range(2, 30):
            if (x + f * 2) % 6 < 3:
                img_treads.putpixel((ox + x, 2), 10)
                img_treads.putpixel((ox + x, 13), 10)
        for wx in (6, 13, 20, 27):
            for wy in (5, 6, 7, 8, 9, 10):
                img_treads.putpixel((ox + wx, wy), 14)
    save_indexed_image(img_treads, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_tread.png"))

    # 4. Boss Missile Pod (2 frames of 24x24: 48x24)
    img_pod = Image.new('P', (48, 24), 0)
    for f in range(2):
        ox = f * 24
        for y in range(4, 20):
            for x in range(4, 20):
                img_pod.putpixel((ox + x, y), 6 if f == 0 else 7)
        tubes = [(7, 7), (14, 7), (7, 14), (14, 14)]
        for tx, ty in tubes:
            for dy in range(4):
                for dx in range(4):
                    col = 1 if f == 0 else (12 if (dx in (1, 2) and dy in (1, 2)) else 8)
                    img_pod.putpixel((ox + tx + dx, ty + dy), col)
    save_indexed_image(img_pod, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_missile_pod.png"))

    # 5. Escort Drone (2 frames of 24x16: 48x16)
    img_drone = Image.new('P', (48, 16), 0)
    for f in range(2):
        ox = f * 24
        for y in range(4, 12):
            for x in range(6, 18):
                img_drone.putpixel((ox + x, y), 3)
        for x in range(9, 15):
            img_drone.putpixel((ox + x, 7), 8)
        img_drone.putpixel((ox + 4, 8), 12 if f == 0 else 13)
        img_drone.putpixel((ox + 19, 8), 12 if f == 0 else 13)
    save_indexed_image(img_drone, PAL3_BOSS, os.path.join(sprites_dir, "spr_drone.png"))

    # 6. Projectiles (4 frames of 16x16: 64x16)
    img_proj = Image.new('P', (64, 16), 0)
    for y in range(4, 12):
        for x in range(6, 10):
            img_proj.putpixel((x, y), 12 if (x in (7, 8) and y in (6, 7, 8, 9)) else 15)
    ox = 16
    for y in range(5, 11):
        for x in range(2, 14):
            img_proj.putpixel((ox + x, y), 9 if x < 6 else 14)
    img_proj.putpixel((ox + 1, 7), 12)
    img_proj.putpixel((ox + 1, 8), 12)
    ox = 32
    for y in range(16):
        for x in range(16):
            d2 = (x - 8)**2 + (y - 8)**2
            if d2 <= 36:
                img_proj.putpixel((ox + x, y), 15 if d2 <= 9 else (13 if d2 <= 20 else 12))
    ox = 48
    for y in range(6, 10):
        for x in range(2, 14):
            img_proj.putpixel((ox + x, y), 15 if y in (7, 8) else 8)
    save_indexed_image(img_proj, PAL3_BOSS, os.path.join(sprites_dir, "spr_projectiles.png"))

    # 7. Particles & Sparks (4 frames of 16x16: 64x16)
    img_part = Image.new('P', (64, 16), 0)
    for i in range(2, 14):
        img_part.putpixel((8, i), 15 if abs(i - 8) < 3 else 13)
        img_part.putpixel((i, 8), 15 if abs(i - 8) < 3 else 13)
    ox = 16
    img_part.putpixel((ox + 4, 5), 10)
    img_part.putpixel((ox + 5, 5), 14)
    img_part.putpixel((ox + 11, 4), 10)
    img_part.putpixel((ox + 10, 11), 14)
    img_part.putpixel((ox + 6, 12), 10)
    ox = 32
    for y in range(2, 14):
        for x in range(2, 14):
            if (x - 8)**2 + (y - 8)**2 <= 25:
                img_part.putpixel((ox + x, y), 15 if (x + y) % 2 == 0 else 12)
    ox = 48
    for y in range(16):
        for x in range(16):
            if (x - 8)**2 + (y - 8)**2 <= 36 and (x + y) % 2 == 0:
                img_part.putpixel((ox + x, y), 10)
    save_indexed_image(img_part, PAL3_BOSS, os.path.join(sprites_dir, "spr_particles.png"))

if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    res_dir = os.path.join(project_dir, "res")
    bgs_dir = os.path.join(res_dir, "bgs")
    sprites_dir = os.path.join(res_dir, "sprites")

    generate_skyline_bg(os.path.join(bgs_dir, "img_gotham_skyline_bgb.png"))
    generate_roadway_bga(os.path.join(bgs_dir, "img_gotham_roadway_bga.png"))
    generate_batmobile_sprite(os.path.join(sprites_dir, "spr_batmobile.png"))
    generate_boss_sprites(sprites_dir)
    print("\n[SUCCESS] Assets re-rendered.")

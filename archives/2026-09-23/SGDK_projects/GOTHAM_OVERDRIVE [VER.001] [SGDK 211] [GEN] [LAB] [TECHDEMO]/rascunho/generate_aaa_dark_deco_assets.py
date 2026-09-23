#!/usr/bin/env python3
import os
import sys
import math
from PIL import Image

def create_palette_bytes(colors):
    flat = []
    for c in colors:
        flat.extend(c[:3])
    while len(flat) < 768:
        flat.extend((0, 0, 0))
    return bytes(flat)

# Exact 9-bit RGB quantized palettes for Mega Drive
# Values per channel: 0, 34, 68, 102, 136, 170, 204, 238
PAL0_SKYLINE = [
    (0, 0, 0),        # 0: transparent / black
    (0, 0, 34),       # 1: deepest midnight navy
    (0, 34, 68),      # 2: dark gothic blue
    (34, 34, 68),     # 3: gothic slate
    (34, 68, 102),    # 4: fog haze blue
    (68, 68, 102),    # 5: spire shadow
    (68, 102, 136),   # 6: skyscraper midtone
    (102, 136, 170),  # 7: art deco highlight
    (34, 0, 68),      # 8: gothic violet shadow
    (102, 34, 102),   # 9: purple storm cloud
    (170, 136, 34),   # 10: amber window warm
    (238, 204, 68),   # 11: brilliant gold arch light
    (136, 170, 204),  # 12: silver cloud rim
    (204, 238, 238),  # 13: Bat-Signal spotlight beam
    (238, 238, 238),  # 14: pure white moon glow
    (0, 0, 0)         # 15: deep black
]

PAL1_ROADWAY = [
    (0, 0, 0),        # 0: transparent
    (34, 34, 34),     # 1: dark asphalt texture
    (68, 68, 68),     # 2: asphalt midtone
    (102, 102, 102),  # 3: concrete barrier edge
    (136, 136, 136),  # 4: steel guardrail
    (170, 170, 170),  # 5: bridge truss light
    (0, 68, 102),     # 6: deep shadow under bridge
    (0, 136, 170),    # 7: suspension cable cyan
    (0, 204, 238),    # 8: neon cyan lane marker
    (238, 170, 0),    # 9: amber road reflector
    (238, 238, 0),    # 10: vibrant yellow center line
    (136, 34, 34),    # 11: red brake light on asphalt
    (204, 68, 68),    # 12: hazard beacon red
    (34, 68, 68),     # 13: distant bridge pier
    (204, 204, 204),  # 14: polished steel reflection
    (238, 238, 238)   # 15: pure white neon beam / text
]

PAL2_HERO = [
    (0, 0, 0),        # 0: transparent
    (0, 0, 0),        # 1: obsidian black Batmobile body
    (34, 34, 68),     # 2: deep blue-black armor shade
    (68, 68, 102),    # 3: armor plate midtone
    (102, 102, 136),  # 4: titanium edge highlight
    (136, 170, 204),  # 5: windshield reflection blue
    (204, 238, 238),  # 6: cockpit canopy rim
    (0, 136, 204),    # 7: dashboard cyan glow
    (0, 238, 238),    # 8: twin headlamp plasma
    (238, 204, 0),    # 9: gold Bat insignia
    (238, 102, 0),    # 10: turbine afterburner orange
    (238, 34, 0),     # 11: jet exhaust core red
    (238, 238, 68),   # 12: Vulcan tracer yellow
    (34, 34, 34),     # 13: heavy rubber tire
    (170, 170, 170),  # 14: chrome wheel rim
    (238, 238, 238)   # 15: muzzle flash white
]

PAL3_BOSS = [
    (0, 0, 0),        # 0: transparent
    (0, 0, 0),        # 1: deep shadow / interior barrel
    (34, 68, 34),     # 2: toxic acid green shadow
    (68, 136, 68),    # 3: bionic green plate midtone
    (102, 204, 102),  # 4: toxic green edge highlight
    (68, 0, 0),       # 5: scarred deep crimson shadow
    (136, 34, 34),    # 6: scarred steel crimson midtone
    (204, 68, 68),    # 7: crimson plate highlight
    (238, 34, 34),    # 8: sensor eye / laser red
    (51, 51, 51),     # 9: crawler tread dark steel
    (102, 102, 102),  # 10: tread link plate
    (170, 136, 68),   # 11: bronze cannon turret armor
    (238, 170, 0),    # 12: heavy plasma fireball orange
    (238, 238, 0),    # 13: electrical discharge spark
    (136, 136, 170),  # 14: missile pod steel alloy
    (238, 238, 238)   # 15: shockwave white
]

def save_img(img, pal, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.putpalette(create_palette_bytes(pal))
    img.save(path)
    print(f"[OK] Generated: {path} ({img.width}x{img.height})")

def render_skyline_bgb(path):
    w, h = 320, 224
    img = Image.new('P', (w, h), 0)

    # 1. Gradient Sky with 50% checkerboard dithering
    for y in range(80):
        for x in range(w):
            if y < 16:
                c = 1 if ((x ^ y) & 1) else 2
            elif y < 36:
                c = 2 if ((x ^ y) & 1) else 3
            elif y < 58:
                c = 3 if ((x ^ y) & 1) else 4
            else:
                c = 4 if ((x ^ y) & 1) else 5
            img.putpixel((x, y), c)

    # 2. Giant Moon with Craters (x=240, y=30, r=26)
    cx, cy, r = 240, 30, 26
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if 0 <= x < w and 0 <= y < 80:
                d2 = (x - cx)**2 + (y - cy)**2
                if d2 <= r**2:
                    if d2 > (r - 2)**2:
                        img.putpixel((x, y), 12)
                    elif d2 > (r - 4)**2:
                        img.putpixel((x, y), 13 if ((x ^ y) & 1) else 12)
                    else:
                        img.putpixel((x, y), 14)
                        # Stylized Bat-Signal Crest Inside Moon
                        dx, dy = abs(x - cx), y - cy
                        if dx <= 16 and abs(dy) <= 10:
                            # Wing curvature
                            wing_top = 4 - (dx // 4)
                            wing_bot = (dx * dx) // 30 - 3
                            if dy >= wing_bot and dy <= wing_top:
                                # Head & ears
                                if dx < 3 and dy < 2:
                                    img.putpixel((x, y), 1)
                                elif dx >= 3:
                                    img.putpixel((x, y), 1)

    # 3. Dynamic Searchlight Cone (Bat-Signal Beam) Sweeping Across Sky
    for y in range(6, 80):
        bx1 = int(240 - (80 - y) * 2.6)
        bx2 = int(240 - (80 - y) * 1.0)
        for x in range(bx1, bx2):
            if 0 <= x < w:
                if ((x + y) % 3 == 0) or (((x ^ y) & 1) and y > 40):
                    cur = img.getpixel((x, y))
                    if cur in (1, 2, 3, 4, 5):
                        img.putpixel((x, y), 13 if ((x + y) % 4 == 0) else 6)

    # 4. Gotham Gothic Architecture Skyline (Detailed Art Deco Towers)
    # List of (x, top_y, width, style)
    # style 0: Cathedral Spire, style 1: Art Deco Stepped Skyscraper, style 2: Clocktower
    towers = [
        (0, 36, 26, 1), (22, 28, 24, 0), (42, 44, 20, 1), (58, 18, 30, 2),
        (84, 38, 24, 1), (104, 12, 36, 0), (136, 30, 28, 1), (160, 42, 22, 1),
        (178, 22, 32, 2), (206, 44, 24, 1), (226, 32, 30, 0), (252, 16, 34, 1),
        (282, 38, 26, 0), (304, 26, 20, 1)
    ]
    for tx, ty, tw, tstyle in towers:
        for y in range(ty, 80):
            for x in range(tx, tx + tw):
                if 0 <= x < w:
                    rel_y = y - ty
                    # Steep Gothic Spire top
                    if tstyle == 0 and rel_y < 12:
                        center_x = tx + tw // 2
                        if abs(x - center_x) > (rel_y * tw // 24):
                            continue
                    # Stepped Art Deco setbacks
                    elif tstyle == 1:
                        if rel_y < 6 and (x < tx + 4 or x > tx + tw - 5):
                            continue
                        elif rel_y < 14 and (x < tx + 2 or x > tx + tw - 3):
                            continue

                    # Outline & Shadowing
                    is_edge = (x == tx or x == tx + tw - 1 or y == ty)
                    is_right_shadow = (x > tx + tw * 0.6)

                    if is_edge:
                        img.putpixel((x, y), 7)
                    elif is_right_shadow:
                        img.putpixel((x, y), 3 if ((x ^ y) & 1) else 1)
                    else:
                        img.putpixel((x, y), 6 if ((x ^ y) & 1) else 5)

                    # Lit Gothic & Art Deco Windows
                    if rel_y > 10 and y < 76:
                        # Grid of glowing amber/gold windows
                        wx = (x - tx) % 5
                        wy = rel_y % 6
                        if wx in (1, 2) and wy in (1, 2, 3):
                            # Stained glass / amber glow
                            col = 11 if ((x * y) % 5 == 0) else 10
                            img.putpixel((x, y), col)

    # 5. Lower Level: City in Mist & Suspension Bridge Under-Pillars (Y=80..223)
    for y in range(80, h):
        for x in range(w):
            img.putpixel((x, y), 1 if (y % 4 == 0) else 0)

    # Massive Gothic Bridge Iron Pylons in Background
    for px in range(12, w, 44):
        for y in range(80, h):
            img.putpixel((px, y), 7)
            img.putpixel((px + 1, y), 6)
            img.putpixel((px + 2, y), 5)
            img.putpixel((px + 3, y), 3)
            img.putpixel((px + 4, y), 1)

    save_img(img, PAL0_SKYLINE, path)

def render_roadway_bga(path):
    w, h = 320, 224
    img = Image.new('P', (w, h), 0)

    # 0..79: 100% Transparent (Layer B shows completely)
    for y in range(80):
        for x in range(w):
            img.putpixel((x, y), 0)

    # Horizon Line at Y=80 (Neon Horizon Glow)
    for x in range(w):
        img.putpixel((x, 79), 8 if ((x % 8) < 4) else 0)
        img.putpixel((x, 80), 5)

    # 81..223: Pseudo-3D Perspective Expressway Deck
    for y in range(81, h):
        progress = (y - 80) / (h - 80) # 0.0 to 1.0
        # Road width expands with perspective
        half_w = int(22 + (progress ** 1.3) * 136)
        cx = 160
        left_edge = cx - half_w
        right_edge = cx + half_w

        # Asphalt speed texture with dither
        for x in range(w):
            if x < left_edge or x > right_edge:
                # Outside roadway: Steel suspension bridge trusses & dark abyss
                if x < left_edge - 14 or x > right_edge + 14:
                    img.putpixel((x, y), 0)
                else:
                    # Guardrails with vertical struts
                    is_strut = (x % 16 < 3) and (y % 3 == 0)
                    img.putpixel((x, y), 14 if is_strut else (5 if (y & 1) else 4))
            else:
                # Road Surface
                dist_center = abs(x - cx)
                is_center_lane = dist_center < int(2 + progress * 3.5)
                is_sublane_l = abs(dist_center - int(half_w * 0.5)) < int(1.5 + progress * 2.5)
                is_curb = (abs(x - left_edge) < 4) or (abs(x - right_edge) < 4)

                if is_center_lane:
                    # Dashed Yellow Center Line
                    img.putpixel((x, y), 10 if (y % 16 < 8) else 2)
                elif is_sublane_l:
                    # Dashed Cyan Lane Dividers
                    img.putpixel((x, y), 8 if (y % 12 < 6) else 2)
                elif is_curb:
                    # Red/Amber Rumble Strip on Curbs
                    img.putpixel((x, y), 9 if (y % 8 < 4) else 12)
                else:
                    # Asphalt surface with speed streaks
                    dither = 2 if ((x + y * 2) % 5 == 0) else 1
                    img.putpixel((x, y), dither)

    save_img(img, PAL1_ROADWAY, path)

def render_batmobile(path):
    # 4 frames of 48x24: 192x24 (0: Straight, 1: Left Tilt, 2: Right Tilt, 3: Turbo Boost)
    fw, fh = 48, 24
    w, h = fw * 4, fh
    img = Image.new('P', (w, h), 0)

    for f in range(4):
        ox = f * fw
        # Long, sleek Batmobile 90s Dark Deco design
        # 1. Rear Sweeping Bat-Fins
        fin_l = 8 if f != 1 else 9
        fin_r = 39 if f != 2 else 38
        for y in range(3, 21):
            img.putpixel((ox + fin_l, y), 1)
            img.putpixel((ox + fin_l + 1, y), 3 if ((y ^ ox) & 1) else 2)
            img.putpixel((ox + fin_r, y), 1)
            img.putpixel((ox + fin_r - 1, y), 3 if ((y ^ ox) & 1) else 2)

        # 2. Main Long Hull (Aerodynamic fuselage)
        for y in range(6, 22):
            for x in range(11, 37):
                # Curved nose at front (y=19..21)
                if y > 19 and (x < 14 or x > 33): continue
                # Scalloped sides
                if y < 9 and (x < 14 or x > 33): continue
                img.putpixel((ox + x, y), 1)

        # 3. Titanium Body Shading & Panel Lines
        for x in range(14, 34):
            img.putpixel((ox + x, 7), 2)
            img.putpixel((ox + x, 8), 4 if (x in (14, 33)) else 3)
            img.putpixel((ox + x, 18), 3)
            img.putpixel((ox + x, 19), 2)

        # 4. Long Tinted Cockpit Canopy with Cyan Reflection
        for y in range(9, 16):
            for x in range(19, 29):
                is_rim = (x in (19, 28) or y in (9, 15))
                if is_rim:
                    img.putpixel((ox + x, y), 6)
                else:
                    # Glass reflection
                    img.putpixel((ox + x, y), 8 if (x - y == 11 or x - y == 12) else 5)

        # 5. Golden Bat Crest on Front Hood
        img.putpixel((ox + 23, 17), 9)
        img.putpixel((ox + 24, 17), 9)
        img.putpixel((ox + 21, 18), 9)
        img.putpixel((ox + 22, 18), 9)
        img.putpixel((ox + 25, 18), 9)
        img.putpixel((ox + 26, 18), 9)

        # 6. Twin Front Plasma Cannons (Vulcan Muzzle Ports)
        img.putpixel((ox + 13, 21), 8)
        img.putpixel((ox + 14, 21), 15)
        img.putpixel((ox + 33, 21), 15)
        img.putpixel((ox + 34, 21), 8)

        # 7. Heavy Combat Wheels with Alloy Hubs
        for wy in range(5, 10):
            for wx in range(5, 8):
                img.putpixel((ox + wx, wy), 14 if (wx == 6 and wy in (6, 7, 8)) else 13)
            for wx in range(40, 43):
                img.putpixel((ox + wx, wy), 14 if (wx == 41 and wy in (6, 7, 8)) else 13)

        for wy in range(15, 20):
            for wx in range(5, 8):
                img.putpixel((ox + wx, wy), 14 if (wx == 6 and wy in (16, 17, 18)) else 13)
            for wx in range(40, 43):
                img.putpixel((ox + wx, wy), 14 if (wx == 41 and wy in (16, 17, 18)) else 13)

        # 8. Jet Exhaust Afterburner Turbine Flame
        flame_len = 12 if f == 3 else (7 if (f & 1) else 5)
        for fx in range(flame_len):
            spread = 4 - (fx // 3)
            if spread < 1: spread = 1
            for dy in range(12 - spread, 14 + spread):
                col = 15 if fx < 2 else (10 if fx < 6 else 11)
                img.putpixel((ox + 23 - fx, dy), col)

    save_img(img, PAL2_HERO, path)

def render_boss_assets(sprites_dir):
    # 1. Boss Chassis (64x48) — Two-Face Siege Dreadnought
    img_chassis = Image.new('P', (64, 48), 0)
    for y in range(4, 46):
        for x in range(4, 60):
            # Angular heavy tank hull
            if (x < 10 and (y < 12 or y > 38)) or (x > 53 and (y < 12 or y > 38)):
                continue
            is_left = (x < 32)
            # Left = Scarred Crimson, Right = Toxic Acid Green
            base_col = 6 if is_left else 3
            edge_col = 7 if is_left else 4
            dark_col = 5 if is_left else 2

            is_border = (x in (4, 59) or y in (4, 45) or x == 31 or x == 32)
            if is_border:
                img_chassis.putpixel((x, y), edge_col if (x < 32) else 1)
            elif ((x ^ y) & 1):
                img_chassis.putpixel((x, y), dark_col)
            else:
                img_chassis.putpixel((x, y), base_col)

    # Armored Heavy Hazard Stripes on right hull
    for y in range(16, 34):
        for x in range(34, 52):
            img_chassis.putpixel((x, y), 10 if ((x + y) % 6 < 3) else 1)

    # Scarred Metal Rivets & Scratches on left hull
    for y in range(12, 38, 4):
        for x in range(8, 28, 6):
            img_chassis.putpixel((x, y), 7)
            img_chassis.putpixel((x + 1, y), 1)

    # Glowing Heavy Reactor Core (Center)
    for y in range(20, 30):
        for x in range(28, 36):
            is_core_rim = (x in (28, 35) or y in (20, 29))
            img_chassis.putpixel((x, y), 8 if is_core_rim else 15)

    save_img(img_chassis, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_chassis.png"))

    # 2. Boss Turret (8 frames of 32x32: 256x32)
    img_turret = Image.new('P', (256, 32), 0)
    for f in range(8):
        ox = f * 32
        cx, cy = ox + 16, 16
        # Bronze Dome Base
        for y in range(6, 26):
            for x in range(ox + 6, ox + 26):
                if (x - cx)**2 + (y - cy)**2 <= 64:
                    img_turret.putpixel((x, y), 11 if ((x ^ y) & 1) else 1)

        # Turret Armored Ring
        for y in range(10, 22):
            for x in range(ox + 10, ox + 22):
                if (x - cx)**2 + (y - cy)**2 <= 25:
                    img_turret.putpixel((x, y), 10)

        # Dual Heavy Plasma Cannons angled by frame
        angles = [(0, 12), (-4, 11), (-8, 9), (-11, 5), (0, 12), (4, 11), (8, 9), (11, 5)]
        dx, dy = angles[f]
        for step in range(14):
            bx1 = cx - 4 + int(dx * step / 12)
            by1 = cy + int(dy * step / 12)
            bx2 = cx + 4 + int(dx * step / 12)
            by2 = cy + int(dy * step / 12)
            if 0 <= bx1 < ox + 32 and 0 <= by1 < 32: img_turret.putpixel((bx1, by1), 10)
            if 0 <= bx2 < ox + 32 and 0 <= by2 < 32: img_turret.putpixel((bx2, by2), 10)

        # White-hot plasma muzzle tips
        mx1, my1 = cx - 4 + dx, cy + dy
        mx2, my2 = cx + 4 + dx, cy + dy
        if 0 <= mx1 < ox + 32 and 0 <= my1 < 32: img_turret.putpixel((mx1, my1), 15)
        if 0 <= mx2 < ox + 32 and 0 <= my2 < 32: img_turret.putpixel((mx2, my2), 15)

    save_img(img_turret, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_turret.png"))

    # 3. Boss Left Tread (4 frames of 32x16: 128x16)
    img_tl = Image.new('P', (128, 16), 0)
    for f in range(4):
        ox = f * 32
        for y in range(2, 14):
            for x in range(2, 30):
                img_tl.putpixel((ox + x, y), 9)
        # Animated tread teeth loop
        for x in range(2, 30):
            if (x + f * 2) % 6 < 3:
                img_tl.putpixel((ox + x, 2), 10)
                img_tl.putpixel((ox + x, 13), 10)
        # Bogie wheels
        for wx in (6, 13, 20, 27):
            for wy in range(5, 11):
                img_tl.putpixel((ox + wx, wy), 14 if wy in (7, 8) else 10)
    save_img(img_tl, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_tread_left.png"))

    # 4. Boss Right Tread (4 frames of 32x16: 128x16)
    img_tr = Image.new('P', (128, 16), 0)
    for f in range(4):
        ox = f * 32
        for y in range(2, 14):
            for x in range(2, 30):
                img_tr.putpixel((ox + x, y), 9)
        for x in range(2, 30):
            if (x + f * 2) % 6 < 3:
                img_tr.putpixel((ox + x, 2), 10)
                img_tr.putpixel((ox + x, 13), 10)
        for wx in (6, 13, 20, 27):
            for wy in range(5, 11):
                img_tr.putpixel((ox + wx, wy), 14 if wy in (7, 8) else 10)
    save_img(img_tr, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_tread_right.png"))

    # 5. Boss Missile Pod (2 frames of 24x24: 48x24)
    img_pod = Image.new('P', (48, 24), 0)
    for f in range(2):
        ox = f * 24
        # Armored pod box
        for y in range(3, 21):
            for x in range(3, 21):
                img_pod.putpixel((ox + x, y), 6 if f == 0 else 7)
        # 4 Missile launch tubes
        tubes = [(6, 6), (13, 6), (6, 13), (13, 13)]
        for tx, ty in tubes:
            for dy in range(5):
                for dx in range(5):
                    if f == 0:
                        img_pod.putpixel((ox + tx + dx, ty + dy), 1)
                    else:
                        is_core = (dx in (1, 2, 3) and dy in (1, 2, 3))
                        img_pod.putpixel((ox + tx + dx, ty + dy), 15 if is_core else 12)
    save_img(img_pod, PAL3_BOSS, os.path.join(sprites_dir, "spr_boss_missile_pod.png"))

def render_drone_projectiles_particles(sprites_dir):
    # 1. Escort Drone (2 frames of 24x16: 48x16)
    img_drone = Image.new('P', (48, 16), 0)
    for f in range(2):
        ox = f * 24
        for y in range(3, 13):
            for x in range(4, 20):
                img_drone.putpixel((ox + x, y), 3 if ((x ^ y) & 1) else 2)
        # Red Sensor Visor
        for x in range(8, 16):
            img_drone.putpixel((ox + x, 7), 8)
            img_drone.putpixel((ox + x, 8), 15 if x in (11, 12) else 8)
        # Twin Jet Thrusters
        img_drone.putpixel((ox + 3, 9), 12 if f == 0 else 15)
        img_drone.putpixel((ox + 20, 9), 12 if f == 0 else 15)
    save_img(img_drone, PAL3_BOSS, os.path.join(sprites_dir, "spr_drone.png"))

    # 2. Projectiles (4 frames of 16x16: 64x16)
    img_proj = Image.new('P', (64, 16), 0)
    # Q0: Batmobile Vulcan Tracer
    for y in range(2, 14):
        for x in range(6, 10):
            img_proj.putpixel((x, y), 15 if (x in (7, 8) and y in (5, 6, 7, 8)) else 12)
    # Q1: Batarang Micro-Missile
    ox = 16
    for y in range(4, 12):
        for x in range(1, 15):
            img_proj.putpixel((ox + x, y), 9 if x < 6 else 14)
    img_proj.putpixel((ox + 1, 7), 12)
    img_proj.putpixel((ox + 1, 8), 12)
    # Q2: Boss Heavy Plasma Sphere
    ox = 32
    for y in range(16):
        for x in range(16):
            d2 = (x - 8)**2 + (y - 8)**2
            if d2 <= 49:
                img_proj.putpixel((ox + x, y), 15 if d2 <= 9 else (13 if d2 <= 25 else 12))
    # Q3: Drone Red Laser Bolt
    ox = 48
    for y in range(5, 11):
        for x in range(1, 15):
            img_proj.putpixel((ox + x, y), 15 if y in (7, 8) else 8)
    save_img(img_proj, PAL3_BOSS, os.path.join(sprites_dir, "spr_projectiles.png"))

    # 3. Particles (4 frames of 16x16: 64x16)
    img_part = Image.new('P', (64, 16), 0)
    # Q0: Electric Star Spark
    for i in range(1, 15):
        img_part.putpixel((8, i), 15 if abs(i - 8) < 3 else 13)
        img_part.putpixel((i, 8), 15 if abs(i - 8) < 3 else 13)
    # Q1: Shrapnel Debris
    ox = 16
    img_part.putpixel((ox + 4, 5), 10)
    img_part.putpixel((ox + 5, 5), 14)
    img_part.putpixel((ox + 11, 4), 10)
    img_part.putpixel((ox + 10, 11), 14)
    img_part.putpixel((ox + 6, 12), 10)
    # Q2: Explosion Shockwave
    ox = 32
    for y in range(1, 15):
        for x in range(1, 15):
            d2 = (x - 8)**2 + (y - 8)**2
            if d2 <= 36:
                img_part.putpixel((ox + x, y), 15 if ((x ^ y) & 1) else 12)
    # Q3: Dithered Volumetric Smoke
    ox = 48
    for y in range(16):
        for x in range(16):
            d2 = (x - 8)**2 + (y - 8)**2
            if d2 <= 49 and ((x ^ y) & 1):
                img_part.putpixel((ox + x, y), 10 if d2 < 20 else 9)
    save_img(img_part, PAL3_BOSS, os.path.join(sprites_dir, "spr_particles.png"))

if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    res_dir = os.path.join(project_dir, "res")
    bgs_dir = os.path.join(res_dir, "bgs")
    sprites_dir = os.path.join(res_dir, "sprites")

    render_skyline_bgb(os.path.join(bgs_dir, "img_gotham_skyline_bgb.png"))
    render_roadway_bga(os.path.join(bgs_dir, "img_gotham_roadway_bga.png"))
    render_batmobile(os.path.join(sprites_dir, "spr_batmobile.png"))
    render_boss_assets(sprites_dir)
    render_drone_projectiles_particles(sprites_dir)
    print("\n[SUCCESS] All AAA Dark Deco pixel art assets generated.")

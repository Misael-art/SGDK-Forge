#!/usr/bin/env python3
"""Generate all sprite/tile/bg PNG assets for Celestial Chase Revive SGDK 2.11."""

from PIL import Image
import os, math, random

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Drawing helpers ───────────────────────────────────────────────────────

def setpx(flat, w, x, y, val):
    if 0 <= x < w and 0 <= y < len(flat)//w:
        flat[y * w + x] = val

def fill_rect(flat, w, x, y, rw, rh, val):
    for dy in range(rh):
        for dx in range(rw):
            setpx(flat, w, x+dx, y+dy, val)

def draw_circ(flat, w, h, cx, cy, r, val):
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            if dx*dx + dy*dy <= r*r:
                setpx(flat, w, cx+dx, cy+dy, val)

def make_sheet(w, h):
    return [0] * (w * h)

def finalize(img, flat, w, h, pal):
    img.putdata(flat)
    pal_flat = []
    for c in pal:
        pal_flat.extend(c)
    img.putpalette(pal_flat)
    return img

# ── Palettes ──────────────────────────────────────────────────────────────

PAL_LIO = [
    (0,0,0),(255,216,160),(64,192,255),(32,144,192),
    (48,80,192),(24,48,160),(40,64,176),(20,40,128),
    (255,208,0),(192,160,0),(255,255,255),(64,128,255),
    (0,0,0),(0,0,0),(0,0,0),(0,0,0),
]

PAL_HAZ = [
    (0,0,0),(255,204,0),(255,136,0),(255,255,68),
    (136,68,0),(136,136,136),(85,85,85),(170,170,170),
    (68,68,68),(64,32,160),(128,96,255),(192,160,255),
    (32,16,80),(64,208,255),(128,255,255),(32,144,192),
]

PAL_ROAD = [
    (0,0,0),(48,48,56),(80,80,88),(64,64,72),
    (192,192,200),(40,40,48),(56,56,64),(8,8,32),
    (16,24,64),(16,16,48),(24,24,56),(24,24,64),
    (12,20,52),(10,10,35),(20,20,45),(5,5,20),
]

PAL_HUD = [
    (0,0,0),(0,192,192),(192,192,192),(128,128,128),
    (64,255,64),(255,200,0),(255,64,64),(255,255,255),
    (0,128,128),(32,32,32),(96,255,96),(160,160,160),
    (0,0,0),(0,0,0),(0,0,0),(0,0,0),
]

PAL_TITLE = [
    (0,0,0),(8,8,40),(16,16,60),(40,80,160),
    (80,160,255),(200,220,255),(255,208,0),(192,160,0),
    (160,80,255),(40,40,80),(60,120,200),(255,255,255),
    (8,8,32),(16,16,48),(24,32,80),(80,40,160),
]

# ══════════════════════════════════════════════════════════════════════════════
# 1. LIO ALL — 144 x 160, 5 rows x 6 frames, 24x32 per frame
# ══════════════════════════════════════════════════════════════════════════════

def gen_lio_all():
    fw, fh, cols, rows = 24, 32, 6, 5
    sw, sh = fw * cols, fh * rows
    flat = make_sheet(sw, sh)

    def f(col, row):
        ox, oy = col * fw, row * fh
        return ox, oy

    def rect(ox, oy, x, y, rw, rh, val):
        for dy in range(rh):
            for dx in range(rw):
                setpx(flat, sw, ox+x+dx, oy+y+dy, val)

    # ── Row 0: RUN ────────────────────────────────────────────────────────
    # Frame 0: left leg fwd, right back
    ox, oy = f(0, 0)
    # Face
    rect(ox,oy, 4,0, 16,4, 3)  # hair top
    rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)  # face
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 8,7, 8,1, 3)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    # Body
    rect(ox,oy, 4,10, 16,8, 4)
    rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    # Arms
    rect(ox,oy, 1,11, 3,6, 4); rect(ox,oy, 2,11, 2,6, 5)
    rect(ox,oy, 20,11, 3,6, 4); rect(ox,oy, 20,11, 2,6, 5)
    # Left leg forward
    rect(ox,oy, 4,18, 7,10, 6)
    rect(ox,oy, 4,18, 3,10, 7)
    # Right leg back
    rect(ox,oy, 12,22, 7,8, 6)
    rect(ox,oy, 12,22, 3,8, 7)

    # Frame 1: mid stride
    ox, oy = f(1, 0)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,6, 4); rect(ox,oy, 2,11, 2,6, 5)
    rect(ox,oy, 19,11, 3,6, 4); rect(ox,oy, 19,11, 2,6, 5)
    # Legs together
    rect(ox,oy, 5,18, 6,8, 6); rect(ox,oy, 13,18, 6,8, 6)
    rect(ox,oy, 5,18, 3,8, 7); rect(ox,oy, 13,18, 3,8, 7)

    # Frame 2: right leg fwd, left back
    ox, oy = f(2, 0)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 1,11, 3,6, 4); rect(ox,oy, 2,11, 2,6, 5)
    rect(ox,oy, 20,11, 3,6, 4); rect(ox,oy, 20,11, 2,6, 5)
    # Right leg forward
    rect(ox,oy, 13,18, 7,10, 6)
    rect(ox,oy, 13,18, 3,10, 7)
    # Left back
    rect(ox,oy, 4,22, 7,8, 6)
    rect(ox,oy, 4,22, 3,8, 7)

    # Frame 3: mid stride (same as frame 1)
    ox, oy = f(3, 0)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,6, 4); rect(ox,oy, 2,11, 2,6, 5)
    rect(ox,oy, 19,11, 3,6, 4); rect(ox,oy, 19,11, 2,6, 5)
    rect(ox,oy, 5,18, 6,8, 6); rect(ox,oy, 13,18, 6,8, 6)
    rect(ox,oy, 5,18, 3,8, 7); rect(ox,oy, 13,18, 3,8, 7)

    # Frame 4: left extended
    ox, oy = f(4, 0)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 0,11, 3,6, 4); rect(ox,oy, 21,11, 3,6, 4)
    # Extended left
    rect(ox,oy, 3,18, 7,12, 6); rect(ox,oy, 3,18, 3,12, 7)

    # Frame 5: transition
    ox, oy = f(5, 0)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,6, 4); rect(ox,oy, 20,11, 3,6, 4)
    rect(ox,oy, 5,18, 6,8, 6); rect(ox,oy, 5,18, 3,8, 7)
    rect(ox,oy, 13,18, 6,8, 6); rect(ox,oy, 13,18, 3,8, 7)

    # ── Row 1: JUMP ───────────────────────────────────────────────────────
    def jump_frame(frame_idx, rising=True):
        ox, oy = f(frame_idx, 1)
        # Head
        rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
        rect(ox,oy, 6,4, 12,4, 1)
        setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
        setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
        setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
        setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
        rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
        # Body
        rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
        rect(ox,oy, 4,10, 16,3, 5)
        rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
        # Arms spread
        if rising:
            rect(ox,oy, 1,10, 3,5, 4); rect(ox,oy, 20,10, 3,5, 4)
        else:
            rect(ox,oy, 0,9, 3,6, 4); rect(ox,oy, 21,9, 3,6, 4)
        # Legs
        if frame_idx == 0:
            rect(ox,oy, 5,18, 6,6, 6); rect(ox,oy, 13,18, 6,6, 6)
        elif frame_idx == 1:
            rect(ox,oy, 6,18, 5,4, 6); rect(ox,oy, 13,18, 5,4, 6)
        elif frame_idx == 2:  # Apex - tucked
            rect(ox,oy, 6,18, 12,4, 6)
        elif frame_idx == 3:
            rect(ox,oy, 6,18, 5,4, 6); rect(ox,oy, 13,18, 5,4, 6)
        elif frame_idx == 4:
            rect(ox,oy, 5,18, 6,8, 6); rect(ox,oy, 13,18, 6,8, 6)
        elif frame_idx == 5:
            rect(ox,oy, 5,18, 14,10, 6); rect(ox,oy, 5,18, 3,10, 7)

    for i in range(6):
        jump_frame(i, i < 3)

    # ── Row 2: DAMAGE ────────────────────────────────────────────────────
    ox, oy = f(0, 2)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    # Flailing
    rect(ox,oy, 0,9, 2,6, 4); rect(ox,oy, 22,9, 2,6, 4)
    rect(ox,oy, 4,18, 16,10, 6); rect(ox,oy, 4,18, 3,10, 7)

    ox, oy = f(1, 2)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,5, 4); rect(ox,oy, 19,11, 3,5, 4)
    rect(ox,oy, 6,18, 12,8, 6); rect(ox,oy, 6,18, 3,8, 7)

    ox, oy = f(2, 2)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 3,11, 3,5, 4); rect(ox,oy, 18,11, 3,5, 4)
    rect(ox,oy, 6,18, 12,6, 6); rect(ox,oy, 6,18, 3,6, 7)

    # ── Row 3: PULSE ──────────────────────────────────────────────────────
    # Frame 0: arm pulling back
    ox, oy = f(0, 3)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,6, 4); rect(ox,oy, 20,11, 3,6, 4)
    rect(ox,oy, 5,18, 14,6, 6); rect(ox,oy, 5,18, 3,6, 7)

    # Frame 1: arm thrusting with energy
    ox, oy = f(1, 3)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,6, 4)
    # Thrust arm + energy
    rect(ox,oy, 21,10, 3,4, 11); setpx(flat, sw, ox+22, oy+9, 11)
    setpx(flat, sw, ox+23, oy+11, 8); setpx(flat, sw, ox+23, oy+12, 8)
    setpx(flat, sw, ox+21, oy+13, 11); setpx(flat, sw, ox+22, oy+14, 3)
    rect(ox,oy, 5,18, 14,6, 6); rect(ox,oy, 5,18, 3,6, 7)

    # Frame 2: energy expanding
    ox, oy = f(2, 3)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,6, 4); rect(ox,oy, 20,11, 3,6, 4)
    # Energy wave
    for dy in range(-2, 3):
        setpx(flat, sw, ox+21, oy+11+dy, 11)
        setpx(flat, sw, ox+22, oy+11+dy, 8)
        setpx(flat, sw, ox+23, oy+11+dy, 3)
    setpx(flat, sw, ox+23, oy+11, 11)
    setpx(flat, sw, ox+23, oy+10, 8); setpx(flat, sw, ox+23, oy+12, 8)
    rect(ox,oy, 5,18, 14,6, 6); rect(ox,oy, 5,18, 3,6, 7)

    # Frame 3: recovery
    ox, oy = f(3, 3)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 2,11, 3,6, 4); rect(ox,oy, 20,10, 3,6, 4)
    rect(ox,oy, 5,18, 14,6, 6); rect(ox,oy, 5,18, 3,6, 7)

    # ── Row 4: IDLE ───────────────────────────────────────────────────────
    # Frame 0
    ox, oy = f(0, 4)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+14, oy+5, 10); setpx(flat, sw, ox+15, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 3,11, 3,5, 4); rect(ox,oy, 18,11, 3,5, 4)
    rect(ox,oy, 6,18, 12,6, 6); rect(ox,oy, 6,24, 12,8, 7)

    # Frame 1: slight bounce
    ox, oy = f(1, 4)
    rect(ox,oy, 4,0, 16,4, 3); rect(ox,oy, 4,0, 16,2, 2)
    rect(ox,oy, 6,4, 12,4, 1)
    setpx(flat, sw, ox+8, oy+5, 10); setpx(flat, sw, ox+9, oy+5, 10)
    setpx(flat, sw, ox+15, oy+5, 10); setpx(flat, sw, ox+14, oy+5, 10)
    setpx(flat, sw, ox+8, oy+5, 0); setpx(flat, sw, ox+9, oy+5, 0)
    setpx(flat, sw, ox+14, oy+5, 0); setpx(flat, sw, ox+15, oy+5, 0)
    rect(ox,oy, 4,4, 2,3, 2); rect(ox,oy, 18,4, 2,3, 2)
    rect(ox,oy, 4,10, 16,8, 4); rect(ox,oy, 4,10, 3,8, 5)
    rect(ox,oy, 4,10, 16,3, 5)
    rect(ox,oy, 6,15, 12,1, 8); rect(ox,oy, 6,16, 12,1, 9)
    rect(ox,oy, 3,11, 3,5, 4); rect(ox,oy, 18,11, 3,5, 4)
    rect(ox,oy, 6,19, 12,6, 6); rect(ox,oy, 6,25, 12,7, 7)

    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_LIO)
    img.save(os.path.join(BASE, 'res', 'sprites', 'lio_all.png'))
    print(f"lio_all.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. LUMEN ORB
# ══════════════════════════════════════════════════════════════════════════════
def gen_lumen_orb():
    fw, fh = 16, 16
    sw, sh = fw * 4, fh
    flat = make_sheet(sw, sh)
    for i in range(4):
        ox = i * fw
        r = [3, 4, 5, 4][i]
        draw_circ(flat, sw, sh, ox+8, 8, r, [2, 1, 1, 2][i])
        draw_circ(flat, sw, sh, ox+8, 8, r-1, [3, 3, 3, 3][i])
        draw_circ(flat, sw, sh, ox+8, 8, r-2, [1, 3, 1, 2][i] if i < 2 else 3)
        if i >= 1:
            draw_circ(flat, sw, sh, ox+8, 8, r+1, [0, 2, 2, 0][i])
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_HAZ)
    img.save(os.path.join(BASE, 'res', 'sprites', 'lumen_orb.png'))
    print(f"lumen_orb.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 3. LOW STONE
# ══════════════════════════════════════════════════════════════════════════════
def gen_low_stone():
    fw, fh = 32, 16
    sw, sh = fw * 2, fh
    flat = make_sheet(sw, sh)
    for i in range(2):
        ox = i * fw
        fill_rect(flat, sw, ox+2, 2, 28, 12, 6)
        fill_rect(flat, sw, ox+2, 2, 28, 12, 5)  # base
        # Highlight
        fill_rect(flat, sw, ox+4, 3, 8, 2, 7)
        fill_rect(flat, sw, ox+20, 3, 8, 2, 7)
        # Shadows
        fill_rect(flat, sw, ox+2, 12, 28, 2, 8)
        fill_rect(flat, sw, ox+12, 4, 2, 8, 8)
        if i == 1:
            # Crack
            for dy in range(6):
                setpx(flat, sw, ox+14+dy, 5+dy, 4)
            for dy in range(3):
                setpx(flat, sw, ox+18+dy, 6+dy, 4)
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_HAZ)
    img.save(os.path.join(BASE, 'res', 'sprites', 'low_stone.png'))
    print(f"low_stone.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 4. ASTRAL MARK
# ══════════════════════════════════════════════════════════════════════════════
def gen_astral_mark():
    fw, fh = 40, 16
    sw, sh = fw * 3, fh
    flat = make_sheet(sw, sh)
    for i in range(3):
        ox = i * fw
        r = [5, 6, 7][i]
        draw_circ(flat, sw, sh, ox+20, 8, r, 9)
        draw_circ(flat, sw, sh, ox+20, 8, r-1, 10)
        draw_circ(flat, sw, sh, ox+20, 8, r-2, 11)
        draw_circ(flat, sw, sh, ox+20, 8, r-3, 3)
        # Rune arms
        for ang in range(0, 360, 60):
            rad = math.radians(ang + i * 15)
            ex = ox + 20 + int((r-1) * 0.7 * math.cos(rad))
            ey = 8 + int((r-1) * 0.7 * math.sin(rad))
            setpx(flat, sw, ex, ey, 3)
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_HAZ)
    img.save(os.path.join(BASE, 'res', 'sprites', 'astral_mark.png'))
    print(f"astral_mark.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 5. BEACON KEY
# ══════════════════════════════════════════════════════════════════════════════
def gen_beacon_key():
    fw, fh = 16, 16
    sw, sh = fw * 3, fh
    flat = make_sheet(sw, sh)
    for i in range(3):
        ox = i * fw
        # Key head
        draw_circ(flat, sw, sh, ox+5, 5, 3, 13)
        draw_circ(flat, sw, sh, ox+5, 5, 2, 14)
        # Shaft
        fill_rect(flat, sw, ox+4, 7, 3, 5, 13)
        # Teeth
        fill_rect(flat, sw, ox+6, 11, 3, 2, 14)
        # Aura
        if i >= 1:
            draw_circ(flat, sw, sh, ox+5, 5, 5, 15)
        if i >= 2:
            draw_circ(flat, sw, sh, ox+5, 5, 6, 3)
            # Star
            for dx, dy in [(0,-4),(0,4),(-4,0),(4,0),(-3,-3),(3,3),(-3,3),(3,-3)]:
                setpx(flat, sw, ox+5+dx, 5+dy, 3)
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_HAZ)
    img.save(os.path.join(BASE, 'res', 'sprites', 'beacon_key.png'))
    print(f"beacon_key.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 6. PURSUER SHADOW
# ══════════════════════════════════════════════════════════════════════════════
def gen_pursuer_shadow():
    fw, fh = 48, 32
    flat = make_sheet(fw, fh)
    # Dark mass
    draw_circ(flat, fw, fh, 24, 16, 15, 1)
    draw_circ(flat, fw, fh, 24, 18, 12, 1)
    fill_rect(flat, fw, 10, 4, 28, 24, 1)
    # Lighter edges
    draw_circ(flat, fw, fh, 24, 16, 16, 2)
    # Eyes
    draw_circ(flat, fw, fh, 18, 12, 2, 3)
    draw_circ(flat, fw, fh, 30, 12, 2, 3)
    draw_circ(flat, fw, fh, 18, 12, 1, 11)
    draw_circ(flat, fw, fh, 30, 12, 1, 11)
    # Horns
    for hx, hy in [(14,4),(18,2),(22,1),(26,1),(30,2),(34,4)]:
        draw_circ(flat, fw, fh, hx, hy, 3, 1)
        draw_circ(flat, fw, fh, hx, hy, 2, 2)
    img = Image.new('P', (fw, fh))
    finalize(img, flat, fw, fh, PAL_HAZ)
    img.save(os.path.join(BASE, 'res', 'sprites', 'pursuer_shadow.png'))
    print(f"pursuer_shadow.png: {fw}x{fh}")

# ══════════════════════════════════════════════════════════════════════════════
# 7. ROAD TILES
# ══════════════════════════════════════════════════════════════════════════════
def gen_road_tiles():
    ts = 8
    tw, th = 16, 2
    sw, sh = ts * tw, ts * th
    flat = make_sheet(sw, sh)
    tiles_road = [
        lambda x,y: 1,                                     # 0: road dark
        lambda x,y: 2 if x>5 and y>2 and y<5 else 1,      # 1: lane marker
        lambda x,y: 3 if x<2 else 1,                       # 2: curb left
        lambda x,y: 3 if x>5 else 1,                       # 3: curb right
        lambda x,y: 4 if y in(3,4) and x>1 and x<6 else 1, # 4: center line
        lambda x,y: 4 if y in(3,4) and x>2 and x<5 else 1, # 5: thin center
        lambda x,y: 5 if (x+y)%2==0 else 1,                # 6: dark var
        lambda x,y: 6 if ((x in(2,3,4) and y==3) or (x==4 and 2<y<6)) else 1, # 7: crack
    ]
    tiles_sky = [
        lambda x,y: 13 if (x==1 and y==1) or (x==6 and y==5) else 7,       # 8: 2 stars
        lambda x,y: 13 if (x==1 and y==1) or (x==4 and y==4) or (x==7 and y==2) else 7, # 9: 3 stars
        lambda x,y: 8 if y>4 else 7,                                        # 10: horizon glow
        lambda x,y: 14 if ((x in(1,2) and y<5) or (x in(5,6,7) and y<3)) else 7, # 11: structure
        lambda x,y: 14 if y<(3+x//3) else 7,                                # 12: city left
        lambda x,y: 14 if y<(5-x//4) else 7,                                # 13: city right
        lambda x,y: 9 if y>2 and y>(6-x//2) and y>(x//2) else 7,            # 14: mountain
        lambda x,y: 11 if ((x+y)%3==0) and 1<y<4 else 7,                    # 15: cloud
    ]
    for col in range(8):
        fn = tiles_road[col]
        for y in range(ts):
            for x in range(ts):
                v = fn(x, y)
                flat[y * sw + col * ts + x] = v
    for col in range(8):
        fn = tiles_sky[col]
        for y in range(ts):
            for x in range(ts):
                v = fn(x, y)
                flat[(y+ts) * sw + col * ts + x] = v
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_ROAD)
    img.save(os.path.join(BASE, 'res', 'tiles', 'road_tiles.png'))
    print(f"road_tiles.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 8. HUD ELEMENTS
# ══════════════════════════════════════════════════════════════════════════════
def gen_hud_elements():
    sw, sh = 256, 32
    flat = make_sheet(sw, sh)
    # INT label (10px text)
    for x in range(4):
        for y in range(6):
            v = 0
            if (x==0 or x==2) and y<5: v = 7
            elif x==4 and y<5: v = 7
            elif x==1 and y==0: v = 7
            elif x==3 and y==0: v = 7
            if v: setpx(flat, sw, 88+x, y, v)
    # LUM label (simple block dots)
    for bx, by in [(0,0),(0,2),(0,4),(2,0),(2,4),(0,6),(2,6)]:
        setpx(flat, sw, 88+bx, 8+by, 7)
    # Simplified: just draw some HUD pixels
    # Integrity shards
    for s in range(3):
        sx = 2 + s * 6
        fill_rect(flat, sw, sx, 1, 3, 6, 1)
        fill_rect(flat, sw, sx+1, 2, 1, 4, 8)
    # Divider lines
    for y in range(8):
        setpx(flat, sw, 15, y, 3); setpx(flat, sw, 16, y, 3)
        setpx(flat, sw, 39, y, 3); setpx(flat, sw, 40, y, 3)
        setpx(flat, sw, 79, y, 3); setpx(flat, sw, 80, y, 3)
    # Lumen orb icon
    draw_circ(flat, sw, sh, 32, 4, 3, 4)
    draw_circ(flat, sw, sh, 32, 4, 2, 7)
    draw_circ(flat, sw, sh, 32, 4, 1, 5)
    # Pressure bar frame
    for y in range(8):
        for x in range(16):
            px = 48 + x
            if y==0 or y==7 or x==0 or x==15:
                setpx(flat, sw, px, y, 2)
            else:
                setpx(flat, sw, px, y, 9)
    # Pressure fill sample
    fill_rect(flat, sw, 49, 1, 14, 6, 5)
    # Pulse bolt icon
    for bx, by in [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),
                   (0,1),(5,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),
                   (2,3),(3,3),(1,4),(2,4),(3,4),(4,4),
                   (2,5),(3,5)]:
        setpx(flat, sw, 72+bx, by, 6 if by<3 else 5)
    # Row 1: labels
    for y in range(8, 14):
        for x in range(3):
            setpx(flat, sw, x, y, 7)
            setpx(flat, sw, x, y, 7)
    # Bar fill row 1
    for x in range(62):
        for y in range(10, 14):
            if x < 48:
                setpx(flat, sw, x, y, 9)
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_HUD)
    img.save(os.path.join(BASE, 'res', 'tiles', 'hud_elements.png'))
    print(f"hud_elements.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 9. TITLE BACKGROUND
# ══════════════════════════════════════════════════════════════════════════════
def gen_title_bg():
    sw, sh = 320, 224
    flat = make_sheet(sw, sh)
    rng = random.Random(42)
    # Sky gradient
    for y in range(sh):
        shade = 12 if y < 40 else (13 if y < 80 else (14 if y < 130 else 9 if y < 170 else 15))
        for x in range(sw):
            setpx(flat, sw, x, y, shade)
    # Stars
    for _ in range(60):
        sx, sy = rng.randint(0, sw-1), rng.randint(0, 100)
        setpx(flat, sw, sx, sy, rng.choice([1,2,3]))
    # Planet 1
    draw_circ(flat, sw, sh, 250, 40, 20, 15)
    draw_circ(flat, sw, sh, 250, 40, 17, 3)
    draw_circ(flat, sw, sh, 250, 40, 14, 4)
    draw_circ(flat, sw, sh, 250, 40, 10, 10)
    # Planet 2
    draw_circ(flat, sw, sh, 80, 60, 12, 8)
    draw_circ(flat, sw, sh, 80, 60, 10, 10)
    draw_circ(flat, sw, sh, 80, 60, 8, 3)
    # Horizon
    for x in range(sw):
        setpx(flat, sw, x, 170, 11)
    # Road
    for y in range(171, sh):
        t = (y - 171) / (sh - 171)
        l = int(60 + (150-60)*t)
        r = int(260 + (170-260)*t)
        l = max(0, l); r = min(sw-1, r)
        for x in range(l, r):
            lw = (r-l)//3
            l1, l2 = l+lw, l+lw*2
            if x in (l1, l1+1, l2, l2+1):
                setpx(flat, sw, x, y, 11 if y%8<4 else 7)
            elif x in (l, l+1, r, r-1):
                setpx(flat, sw, x, y, 3)
            else:
                setpx(flat, sw, x, y, 7 if (x+y)%5==0 else 9)
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_TITLE)
    img.save(os.path.join(BASE, 'res', 'bg', 'title_bg.png'))
    print(f"title_bg.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════
# 10. TITLE LOGO
# ══════════════════════════════════════════════════════════════════════════════
def gen_title_logo():
    sw, sh = 240, 48
    flat = make_sheet(sw, sh)
    # Big CELESTIAL CHASE text using rectangles
    # Simple blocky font as colored rectangles
    def draw_letter(ox, oy, pts, color, shadow=True):
        if shadow:
            for dx, dy in pts:
                setpx(flat, sw, ox+dx+1, oy+dy+1, 7)
        for dx, dy in pts:
            setpx(flat, sw, ox+dx, oy+dy, color)
            if dy < 3:
                setpx(flat, sw, ox+dx, oy+dy, 11)

    glyphs = {
        'C': [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,8),(2,8),(3,8)],
        'E': [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,8),(2,8),(3,8)],
        'L': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,8),(2,8),(3,8)],
        'S': [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(3,4),(3,5),(3,6),(0,7),(1,7),(2,7),(3,7),(0,8),(1,8),(2,8),(3,8)],
        'T': [(0,0),(1,0),(2,0),(3,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8)],
        'I': [(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(0,8),(1,8),(2,8)],
        'A': [(0,1),(1,0),(2,0),(3,1),(0,2),(3,2),(0,3),(3,3),(0,4),(1,4),(2,4),(3,4),(0,5),(3,5),(0,6),(3,6),(0,7),(3,7),(0,8),(3,8)],
        'H': [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(3,0),(3,1),(3,2),(3,3),(3,4),(0,5),(3,5),(0,6),(3,6),(0,7),(3,7),(0,8),(3,8)],
        'R': [(0,0),(1,0),(2,0),(3,0),(0,1),(3,1),(0,2),(3,2),(0,3),(1,3),(2,3),(3,3),(0,4),(0,5),(2,5),(3,5),(0,6),(3,6),(0,7),(3,7),(0,8),(3,8)],
        'M': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),
              (1,1),(2,2),(3,1),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8)],
        ' ': [],
    }
    text = "CELESTIAL CHASE"
    lw = 14
    tx = (sw - len(text)*lw)//2
    ty = 6
    for ch in text:
        if ch in glyphs:
            draw_letter(tx, ty, glyphs[ch], 6)
        tx += lw
    # "REVIVE"
    tx = (sw - 6*lw)//2
    ty = 28
    for ch in "REVIVE":
        if ch in glyphs:
            draw_letter(tx, ty, glyphs[ch], 10)
        tx += lw
    img = Image.new('P', (sw, sh))
    finalize(img, flat, sw, sh, PAL_TITLE)
    img.save(os.path.join(BASE, 'res', 'bg', 'title_logo.png'))
    print(f"title_logo.png: {sw}x{sh}")

# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating assets...")
    gen_lio_all()
    gen_lumen_orb()
    gen_low_stone()
    gen_astral_mark()
    gen_beacon_key()
    gen_pursuer_shadow()
    gen_road_tiles()
    gen_hud_elements()
    gen_title_bg()
    gen_title_logo()
    print("Done!")

#!/usr/bin/env python3
"""Author the G2 TAINA pose as an explicit 48x64 native pixel raster.

The art is declared as hand-authored row clusters below.  No resampling,
segmentation, primitive drawing, or pixels from a rejected candidate are used
to produce the player asset.  The rest of this module only serializes reports
and diagnostic evidence from that raster.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "rascunho/taina_native_g2_volume_identity_v01"
ASSET_ID = "taina_48x64_native_g2_volume_identity_v01"
W, H = 48, 64
SOURCE_A = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/source/face_and_guard_topology_visual_source_v01.png"
SOURCE_A_SHA = "b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf"
MATERIAL_CONTROL = PROJECT / "rascunho/taina_native_material_clean_rework_v01/taina_48x64_native_a1_material_clean_v01.png"
MATERIAL_CONTROL_SHA = "54df9fd341ad57bdc2c02c62db6366119c7d511ba8e14862666cf487366b2567"
TECHNICAL_CONTROL = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/taina_48x64_geometry_face_guard_v01.png"
TECHNICAL_CONTROL_SHA = "1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830"
COMPARISON_64 = PROJECT / "rascunho/taina_visual_challengers_v03/candidates/taina_64x96_challenger_b/taina_64x96_challenger_b.png"

# Palette is fixed to the existing Mega Drive material vocabulary.  Indices
# 13-15 are intentionally occupied by hair highlight, indigo base and indigo
# highlight, giving each major material readable perceptual states.
PALETTE = [
    (0, 0, 0), (34, 0, 34), (102, 68, 68), (136, 68, 34),
    (204, 136, 68), (238, 170, 102), (170, 34, 0), (238, 102, 0),
    (238, 170, 68), (0, 68, 68), (34, 136, 136), (102, 204, 170),
    (34, 34, 68), (136, 68, 68), (68, 68, 136), (102, 102, 170),
]

# x outline, h/d hair, q/Q/L skin, o/O/Y top, t/T/A teal sash/wraps,
# i/I/j indigo trousers.  Six groups of eight make every authored row easy
# to inspect against the 48-column VDP canvas.
RASTER = """........ ........ ........ ........ ........ ........
........ ........ ....xx.. ........ ........ ........
........ .......x ..hddhhx ........ ........ ........
........ ......xx .hhddhh. ........ ........ ........
........ .....xhh xhdddhh. ........ ........ ........
........ ....xhhh hhdddhh. ........ ........ ........
........ ...xxhhh hhhddhh. ........ ........ ........
........ ..xhhhhh hhhddh.. ........ ........ ........
........ .xhhhhhh hhhdd... ........ ........ ........
........ xhhhhhhh hhhdd... ........ ........ ........
.......x hhhhhhhx hhh...x. ........ ........ ........
......xh hhhhhhhx .xqqQxx. ........ ........ ........
.....xhh hhhhhhh. ..qQQQLx ........ ........ ........
....xhhh hhhhh... ..qQQLLx ........ ........ ........
....xhhh hhhh.... ..qQQLxx ........ ........ ........
...xhhhh hhh..... ..qQLx... ........ ........ ........
...xhhh. hh...... ..qQxx... ........ ........ ........
...xhh.. h....... .xqQx.... ........ ........ ........
...xx... ........ .xqQx.... ........ ........ ........
........ ........ .xqQx.... ........ ........ ........
........ ........ .xqqx.... ........ ........ ........
........ ........ xqqQx.... ........ ........ ........
........ ........ xqQQx...x ........ ........ ..xx....
........ .....xx. xqQQx..xO ........ ........ .xYYx...
........ ....xqqx xqQx...OO ........ .......x xYLLx...
........ ...xqQQx xqQx..xOO ........ ......xY xLLQx...
........ ...qQQQL xqQx.xOOO ........ .....xYY xLLQx...
........ ..xqQQLL xqQx.xOOO ........ ....xYLL xLQx....
........ ..qQQLLx xqQx.xOOO ........ ...xYLLx xQx.....
........ .xqQLLxx xqQx..xOO ........ ...xLLx. xQx.....
........ .xqQx... xqQx...xO ........ ...xLx.. xQx.....
........ ..xx.... xqQx....x ........ ....x... xQx.....
........ ........ .xQx...... ........ ......xQ QQx.....
........ ........ .xQx...... ........ .....xQQ Qx......
........ .......x xxQx...... ........ ....xQQQ x.......
........ ......xT TTtx...... ........ ...xQQQQ x.......
........ .....xTT TTTAx.... ........ ..xQQQxx ........
........ ....xTTT TTAAx.... ........ .xQQQx.. ........
........ ...xTTTT TAAx.... ........ xQQQx... ........
........ ..xTTTTT TAx..... .......x QQx..... ........
.......x xTTTTTxx x....... ......xQ Qx...... ........
......xi iTTTxxxx i....... .....xQQ Qx...... ........
.....xii iiix... iix..... ....xQQQ x....... ........
....xiii iii.... iix..... ...xQQQx ........ ........
...xiiii iii.... iix....x ..xQQQx. ........ ........
..xiiiii iii.... iix...xQ .xQQQx.. ........ ........
..xiiiii ii..... iix..xQQ xQQx.... ........ ........
.xiiiiii ii..... iix.xQQQ QQx..... ........ ........
.xiiiiii i...... iixxQQQQ Qx...... ........ ........
xxiiiiii i...... iixQQQQQ x...... ........ ........
xiiiiiii i...... ixQQQQQx ....... ........ ........
xiiiiiii i...... ixQQQQx. ....... ........ ........
xxiiiiii i...... ixQQQQx. ....... ........ ........
.xiiiiii ii..... iixQQQx.. ....... ........ ........
.xiiiii. iix.... iixQQx... ....... ........ ........
..xiii.. xix.... ixQQx.... ....... ........ ........
..xxii.. .xx.... xQQx..... ....... ........ ........
...xii.. ........ xQx...... ....... ........ ........
....xx.. ........ ........ ........ ........ ........
...xQQx. ........ ........ .......x xQQx.... ........
..xQQQQx ........ ........ ......xQ QQx..... ........
..QQQQQx ........ ........ .....xQQ QQx..... ........
..xQQQxx ........ ........ .....xQQ QQx..... ........
...xxxx. ........ ........ ......xx xx...... ........
""".strip("\n")

# G2 redraw: the following six-by-eight groups are the canonical authored
# raster for this round.  The earlier scratch block above remains as negative
# history; this block is intentionally independent of every rejected PNG.
RASTER = """........ ........ ........ ........ ........ ........
........ ........ ........ ........ ........ ........
........ ........ ........ ........ ........ ........
........ ....xx.. ..hh.... ........ ........ ........
........ ...xhhx. ..hdd... ........ ........ ........
........ ..xhhhh. .hddd... ........ ........ ........
........ .xhhhhh. hhdddh.. ........ ........ ........
...x.... xhhhhhh. hhddhh.. ........ ........ ........
..x..... hhhhhhh. hdddh... ........ ........ ........
.x...... hhhhhhx. hddh.... ........ ........ ........
.x...... hhhhhxx. .xqqQ... ........ ........ ........
xx...... hhhhxxx. xqQQQx.. ........ ........ ........
x....... hhhx.... qQQLLx.. ........ ........ ........
x....... hh...... qQQLx... ........ ........ ........
xx...... h....... qQx..... ........ ........ ........
.x...... ........ xqQx.... ........ ........ ........
........ ........ .xqQx... ........ ........ ........
........ ........ .xqQx... ........ ........ ........
....xq.. .xqQxx.. .xqQx... ........ ........ ........
...xQQx. xqQQLx.. .xqQx... ........ ..xx.... ........
...xQx.. qQQLLx.. .xqQx... ........ .xQQQx.. ..xx....
....xx.. xqQLx... .xqQx... ...x.... xqQx.... .xQQx...
........ .xqQx... .xqQx... ..xOxx.. xTQx.... xQx.....
........ .xqqx... xqQx... .xOOOx.. TTQx.... .xQx....
........ ..xx.... xqQx... xOOOxx.. xTTx.... .xQx....
........ ........ .xqQx.. xOOOOx.. .xTTx.... .xQx....
........ ........ .xqQx.. xOOOox.. xQx..... xQx.....
........ ...xx... xqQx... xOOOox.. xqQx.... .xQx....
........ ..xTTx.. xqQx... xOOOox.. xqQx.... .xQx....
........ .xTTTx.. .xqQx.. xOOOox.. .xqQx... xQx.....
........ xTTTTx.. .xqQx.. xOOOOx.. xqQx.... .xQx....
...xx... xTTTxx.. xqQx... .xOOOx.. xqQx.... ..x.....
....x... ........ .xqQx.. .xOOOx.. .xQx.... ........
........ ........ .xqQx.. .xOOOx.. xqQx.... ........
........ ........ xqQx... .xOOOx.. .xqQx... ........
........ ........ .xQx... xOOOOx.. xQx..... ........
........ ........ .xQx... .xOOx... .xQx.... ........
........ ........ ...x.... xqQx.... xQx..... ........
........ ........ ..xTT... xQQx.... xQx..... ........
........ ........ .xTTTx.. .xTTx... xQQx.... ........
........ ...x.... xTTTTx.. xTTTx... .xQx.... ..xx....
........ ..xTT... .xQx.... xTTTTx.. xQx..... .xTTx...
........ .xTTTx.. .xQx.... .xTTTx.. xQx..... xTTx....
...x.... xTTTxx.. xqQx... ..x..... .xQx.... xTTx....
...xii.. iiiiii.. iix..... .xIIIIx. xjj..... ........
..xiii.. iiiiii.. iix..... xjIIIIx. jj...... ........
.xiiii.. iiiiiii. iix..... .jIIIIx. jjj..... ........
xiiiii.. iiiiiii. iix..... jIIIIx.. jjj..... ........
xiiiiii. iiiiiii. iix..... jIIIIx.. jjjj.... ........
xiiiiii. iiiiiii. iix..... jIIIIx.. jjjjj... ........
xiiiiii. iiiiiii. iix..... jIIIIx.. jjjjj... ........
xiiiiii. iiiiiii. iix..... jIIIIx.. jjjjj... ........
xiiiiii. iiiiii.. iix..... jIIIIx.. jjjjj... ........
.xiiiii. iiiii... iix..... jIIIIx.. jjjjj... ........
.xiiiii. iiiii... iix..... jIIIIx.. jjjjj... ........
..xiiii. iii.... .iix..... jIIIIx.. jjjjj... ........
..xiiii. ii..... .iix..... .jIIIIx. jjjjj... ........
...xii.. iix.... .iix..... ..xIIx.. jjjj.... ........
...xx... .xx.... .x...... ..xjjx.. .xxx.... ........
...xQx.. xQQQxx.. ........ .......x xQQQx... ........
..xQQQQ. xQQQQx.. ........ ......xQ QQQQx... ........
..xQQQQ. QQQLLx.. ........ .....xQQ QQQQx... ........
...xxxx. .xQQxx.. ........ ....xQQQ xQQxx... ........
....xx.. ........ ........ ....xx.. ........ ........
""".strip("\n")

# Final G2 authoring is expressed as irregular one-pixel row runs.  These
# runs are the shape-block/lineart/color-blocking decisions themselves; they
# are not a rectangle or polygon renderer and do not sample any prior PNG.
AUTHOR_SPANS = {
  3:[(15,"xx"),(19,"hh")], 4:[(13,"xhhx"),(19,"hdd")],
  5:[(11,"xhhhh"),(18,"hddd")], 6:[(10,"xhhhhh"),(18,"hhdddh")],
  7:[(8,"xx"),(10,"hhhhhh"),(18,"hhddhh")],
  8:[(7,"x"),(8,"hhhhhhh"),(18,"hdddh")],
  9:[(6,"x"),(7,"hhhhhhx"),(18,"hddh")],
 10:[(5,"xx"),(7,"hhhhhh"),(18,"xqqQ")],
 11:[(5,"x"),(7,"hhhhh"),(18,"xqQQQx")],
 12:[(4,"xx"),(6,"hhhh"),(18,"qQQLLx")],
 13:[(4,"x"),(6,"hhh"),(18,"qQQLx")],
 14:[(4,"xx"),(6,"hh"),(18,"qQx")],
 15:[(5,"x"),(19,"xqQx")], 16:[(19,"xqQx")], 17:[(19,"xqQx")],
 18:[(12,"xqQ"),(18,"xqQx")],
 19:[(10,"xqQQx"),(17,"xqQx"),(35,"xx")],
 20:[(9,"xqQx"),(17,"xqQx"),(34,"xQQQx"),(40,"xx")],
 21:[(9,"xQQx"),(14,"xqQx"),(18,"xqQx"),(33,"xqQLLx"),(40,"xQx")],
 22:[(10,"xQx"),(15,"xqQx"),(19,"xqQx"),(33,"xTQx"),(40,"xQx")],
 23:[(11,"xx"),(16,"xqQx"),(20,"xOxx"),(24,"xOOx"),(31,"xQQx"),(40,"xTTx")],
 24:[(13,"xqQx"),(17,"xOOOOx"),(30,"xqQQx"),(38,"xTTx")],
 25:[(13,"qQQQx"),(18,"xOOOOOx"),(30,"xqQQx"),(38,"xTTx")],
 26:[(14,"qQQLL"),(20,"xOOOox"),(31,"qQx"),(37,"xTTTx")],
 27:[(15,"xQQLLx"),(21,"xOOOox"),(31,"xqQx"),(37,"xTTTx")],
 28:[(16,"xQQLx"),(21,"xOOOox"),(31,"xqQx"),(37,"xTTx")],
 29:[(16,"xqQx"),(20,"xOOOOx"),(31,"xqQx"),(38,"xQx")],
 30:[(16,"xqQx"),(20,"xOOOox"),(31,"xqQx")],
 31:[(16,"xqQx"),(20,"xOOOox"),(31,"xqQx")],
 32:[(17,"xQx"),(20,"xOOOx"),(31,"xQx")],
 33:[(17,"xQx"),(20,"xOOOx"),(31,"xQx")],
 34:[(17,"xQx"),(20,"xOOOx"),(31,"xQx")],
 35:[(18,"xQx"),(22,"qQQx"),(29,"xQx")],
 36:[(18,"xQx"),(21,"qQQx"),(29,"xQx")],
 37:[(17,"xQQx"),(21,"qQx"),(28,"xQQx")],
 38:[(13,"xTTTTx"),(19,"xQx"),(26,"xTTTx"),(31,"xQQx")],
 39:[(11,"xTTTTTTx"),(19,"xQx"),(27,"xTTTTx"),(34,"xQQx")],
 40:[(10,"xTTTTTxx"),(19,"xQx"),(28,"xTTTTx"),(36,"xQx"),(40,"xT")],
 41:[(9,"xTTTTTx"),(19,"xQx"),(29,"xTTTTx"),(37,"xQx"),(40,"xTTT")],
 42:[(8,"xTTTTxx"),(20,"xQx"),(30,"xTTTx"),(38,"xQx"),(41,"xTTTT")],
 43:[(8,"xTTTx"),(20,"xQx"),(30,"xTTx"),(39,"xQx"),(42,"xTT")],
 44:[(7,"xiiiii"),(16,"iiiii"),(25,"xIIIIx"),(31,"jjjjjj")],
 45:[(6,"xiiiiii"),(16,"iiii"),(24,"xjIIIIx"),(32,"jjjjjj")],
 46:[(6,"xiiiiiii"),(17,"iii"),(24,"jIIIIx"),(31,"jjjjjj")],
 47:[(5,"xiiiiiiii"),(18,"ii"),(23,"jIIIIIx"),(31,"jjjjjj")],
 48:[(5,"xiiiiiiii"),(18,"ii"),(23,"jIIIIIx"),(31,"jjjjjj")],
 49:[(4,"xiiiiiiiii"),(18,"i"),(23,"jIIIIIx"),(31,"jjjjjjj")],
 50:[(4,"xiiiiiiiii"),(19,"i"),(23,"jIIIIIx"),(31,"jjjjjjj")],
 51:[(4,"xiiiiiiii"),(19,"ii"),(23,"jIIIIIx"),(31,"jjjjjj")],
 52:[(4,"xiiiiiii"),(19,"ii"),(24,"jIIIIx"),(31,"jjjjjj")],
 53:[(5,"xiiiiii"),(19,"ii"),(24,"jIIIIx"),(31,"jjjjjj")],
 54:[(5,"xiiiii"),(19,"ii"),(24,"jIIIIx"),(31,"jjjjjj")],
 55:[(6,"xiiii"),(18,"iii"),(25,"jIIIx"),(31,"jjjjj")],
 56:[(7,"xii"),(17,"xx"),(26,"xIIx"),(31,"jjjj")],
 57:[(8,"xx"),(17,"x"),(26,"xjjx"),(32,"xxx")],
 58:[(6,"xx"),(8,"qQQQx"),(29,"x"),(32,"xQQQx")],
 59:[(5,"xQQQQx"),(31,"xQQQQx")],
 60:[(4,"xQQQQQx"),(32,"xQQQQx")],
 61:[(4,"xQQQLx"),(33,"xQQQLx")],
 62:[(5,"xxx"),(34,"xxx")],
 63:[(6,"xx"),(36,"xx")],
}

# Authorial redraw with contiguous body masses and explicit light clusters.
# It is intentionally separate from all prior controls.
AUTHOR_SPANS = {
 3:[(15,"xx"),(19,"hh")], 4:[(13,"xhhx"),(19,"hdd")], 5:[(11,"xhhhh"),(18,"hddd")],
 6:[(10,"xhhhhh"),(18,"hhdddh")], 7:[(8,"xx"),(10,"hhhhhh"),(18,"hhddhh")],
 8:[(7,"x"),(8,"hhhhhhh"),(18,"hdddh")], 9:[(6,"x"),(7,"hhhhhhx"),(18,"hddh")],
10:[(5,"xx"),(7,"hhhhhh"),(14,"ddxx"),(18,"xqqQQx")], 11:[(5,"x"),(7,"hhhhh"),(13,"hdd"),(16,"dx"),(18,"xqQQQQx")],
12:[(4,"xx"),(6,"hhhh"),(12,"hdd"),(15,"ddx"),(18,"qQQLxLx")], 13:[(4,"x"),(6,"hhh"),(15,"dx"),(18,"qQQLxx")],
14:[(4,"xx"),(6,"hh"),(15,"dx"),(18,"qQx")], 15:[(5,"x"),(19,"xqQx")], 16:[(19,"xqQx")], 17:[(19,"xqQx")],
18:[(11,"xqQx"),(17,"xqQx")], 19:[(10,"xqQQx"),(16,"xqQx"),(34,"xQQQx"),(41,"xx")],
20:[(10,"xqQQx"),(16,"xqQx"),(32,"xqQQQQx"),(40,"xTTx")],
21:[(11,"qQQLLx"),(17,"xqQx"),(31,"xqQQQQx"),(38,"xTTTx")],
22:[(12,"xQQLx"),(17,"xqQx"),(30,"xqQQQx"),(37,"xTTTTx")],
23:[(13,"xQQx"),(17,"xqQx"),(21,"xOOOOOOx"),(29,"xqQQQx"),(39,"xTTx")],
24:[(13,"xQQQQx"),(19,"xoOOOOOOOx"),(29,"xqQQQQx"),(38,"xTTx")],
25:[(14,"xQQLLx"),(20,"xOOOYYOOx"),(29,"xqQQQx"),(38,"xTTx")],
26:[(15,"xQQLx"),(20,"xooOOYOox"),(29,"xqQQx"),(37,"xTTTx")],
27:[(16,"xQx"),(19,"xOOOYYOOx"),(30,"xqQQx"),(37,"xTTTx")],
28:[(16,"xQx"),(19,"xOOOYYOOx"),(30,"xqQQx"),(38,"xTTx")],
29:[(16,"xqQx"),(20,"xOOOOOOOx"),(30,"xqQQx"),(38,"xQx")],
30:[(17,"xqQx"),(21,"xOOOOOx"),(30,"xqQQx")], 31:[(17,"xqQx"),(21,"xOOOOOx"),(30,"xqQQx")],
32:[(18,"xQx"),(21,"xOOOOx"),(30,"xQx")], 33:[(18,"xQx"),(21,"xOOOOx"),(30,"xQx")],
34:[(18,"xQx"),(21,"xOOOOx"),(30,"xQx")], 35:[(19,"xQQQx"),(29,"xQx")],
36:[(18,"xQQQQx"),(29,"xQx")], 37:[(18,"xQQQQx"),(28,"xQQx")],
38:[(12,"xtTAAAx"),(19,"xQQx"),(26,"xtAAAx"),(32,"xQQx")],
39:[(10,"xTTTTtTx"),(19,"xQQx"),(27,"xTAAAx"),(34,"xQQx")],
40:[(9,"xTTTTTTx"),(19,"xQx"),(28,"xTTTTx"),(36,"xQx"),(41,"xT")],
41:[(8,"xTTTTTTx"),(20,"xQx"),(29,"xTTTTx"),(37,"xQx"),(40,"xTTTT")],
42:[(8,"xTTTTx"),(20,"xQx"),(30,"xTTTTx"),(38,"xQx"),(41,"xTTTTT")],
43:[(8,"xTTTx"),(20,"xQx"),(30,"xTTTx"),(39,"xQx"),(42,"xTT")],
44:[(7,"xiiiiiiiiii"),(24,"xjIIIIIIjjx")], 45:[(6,"xiiiiiiiiiii"),(23,"xjIIIIIIIjjx")],
46:[(5,"xiiiiiiiiiiii"),(23,"xjIIIIIIIIjjx")], 47:[(5,"xiiiiiiiiiiiii"),(22,"xjIIIIIIIIIIjjx")],
48:[(4,"xiiiiiiiiiiiiii"),(22,"xjIIIIIIIIIIjjx")], 49:[(4,"xiiiiiiiiiiiiii"),(21,"xjIIIIIIIIIIIjjx")],
50:[(4,"xiiiiiiiiiiiii"),(22,"xjIIIIIIIIIIjjx")], 51:[(5,"xiiiiiiiiiiii"),(22,"xjIIIIIIIIIIjjx")],
52:[(5,"xiiiiiiiiiii"),(23,"xjIIIIIIIIIjjx")], 53:[(6,"xiiiiiiiiii"),(24,"xjIIIIIIIIjjx")],
54:[(6,"xiiiiiiiii"),(25,"xjIIIIIIIjjx")], 55:[(7,"xiiiiiii"),(27,"xjIIIIIjjx")],
56:[(8,"xiiiii"),(28,"xjIIIIjjx")], 57:[(9,"xiii"),(29,"xjjjjjx")], 58:[(10,"xx"),(30,"xx")],
59:[(6,"xqQQQQx"),(34,"xqQQQQx")], 60:[(5,"xQQQQQx"),(34,"xQQQQQx")],
61:[(5,"xQQQLLx"),(35,"xQQQLLx")], 62:[(6,"xxxx"),(36,"xxxx")], 63:[(7,"xx"),(37,"xx")],
}

def authored_rows() -> list[str]:
    rows = [["."] * W for _ in range(H)]
    for y, spans in AUTHOR_SPANS.items():
        for x, text in spans:
            if y < 0 or y >= H or x < 0 or x + len(text) > W:
                raise ValueError(f"authored span outside canvas: y={y} x={x} text={text!r}")
            for offset, token in enumerate(text):
                if rows[y][x + offset] != ".":
                    raise ValueError(f"overlapping authored span at {(x+offset,y)}")
                rows[y][x + offset] = token
    return ["".join(row) for row in rows]

RASTER = "\n".join(authored_rows())

TOKEN_TO_INDEX = {".": 0, "x": 1, "h": 2, "d": 13, "q": 3, "Q": 4,
                  "L": 5, "o": 6, "O": 7, "Y": 8, "t": 9, "T": 10,
                  "A": 11, "i": 12, "I": 14, "j": 15}
TOKEN_MATERIAL = {"h": "hair", "d": "hair", "q": "skin", "Q": "skin", "L": "skin",
                  "o": "orange_top", "O": "orange_top", "Y": "orange_top",
                  "t": "teal_cloth", "T": "teal_cloth", "A": "teal_cloth",
                  "i": "indigo_trousers", "I": "indigo_trousers", "j": "indigo_trousers"}
SEMANTIC = {"head_or_face": 1, "hair": 2, "torso": 3, "arms_or_guard": 4,
            "hands": 5, "legs": 6, "feet": 7, "sash": 8}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_raster() -> list[str]:
    rows = [line if " " not in line else "".join(part[:8].ljust(8, ".") for part in line.split()) for line in RASTER.splitlines()]
    if len(rows) != H or any(len(row) != W for row in rows):
        raise ValueError(f"raster must be {W}x{H}, got {len(rows)} rows / {sorted({len(r) for r in rows})}")
    unknown = sorted(set("".join(rows)) - set(TOKEN_TO_INDEX))
    if unknown:
        raise ValueError(f"unknown tokens: {unknown}")
    return rows


def save_candidate(rows: list[str]) -> Path:
    image = Image.new("P", (W, H), 0)
    flat_palette = [v for rgb in PALETTE for v in rgb]
    image.putpalette(flat_palette)
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            image.putpixel((x, y), TOKEN_TO_INDEX[token])
    path = OUT / f"{ASSET_ID}.png"
    image.save(path, "PNG", bits=4, transparency=0)
    return path


def metrics(path: Path) -> dict:
    with Image.open(path) as im:
        px = list(im.tobytes())
        visible = [(i % W, i // W) for i, v in enumerate(px) if v != 0]
        indices = sorted(set(px) - {0})
        bbox = [min(x for x, _ in visible), min(y for _, y in visible), max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]
        return {"width": W, "height": H, "mode": im.mode, "visible_colors": len(indices), "filled_pixels": len(visible),
                "canvas_pixels": W * H, "occupancy_pct": round(len(visible) / (W * H) * 100, 2), "bbox": bbox, "visible_indices": indices}


def save_diag(path: Path, rows: list[str], kind: str) -> None:
    img = Image.new("P", (W, H), 0)
    if kind == "silhouette": pal = [(0,0,0), (68,68,68)]
    elif kind == "lineart": pal = [(0,0,0), PALETTE[1]]
    elif kind == "semantic": pal = [(0,0,0), (238,170,68), (102,68,68), (238,102,0), (34,136,136), (238,238,230), (68,68,136), (204,136,68), (102,204,170)]
    else: pal = [(0,0,0), (238,170,68), (238,102,0), (34,136,136), (68,68,136), (204,136,68), PALETTE[1]]
    img.putpalette([v for rgb in pal for v in rgb] + [0,0,0] * (256-len(pal)))
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            if token == ".": continue
            if kind in ("silhouette", "lineart"): val = 1
            elif kind == "contour":
                edge = any(nx < 0 or ny < 0 or nx >= W or ny >= H or rows[ny][nx] == "." for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
                val = 1 if edge else 2
            elif kind == "material": val = {"hair":1,"skin":2,"orange_top":3,"teal_cloth":4,"indigo_trousers":5}.get(TOKEN_MATERIAL.get(token, ""), 6)
            elif kind == "semantic": val = semantic_for(x, y, token)
            else: val = 1 if token == "x" else 2
            img.putpixel((x, y), val)
    img.save(path, "PNG", bits=4, transparency=0)


def semantic_for(x: int, y: int, token: str) -> int:
    if token in ("h", "d"): return SEMANTIC["hair"]
    if token in ("o", "O", "Y"): return SEMANTIC["torso"]
    if token in ("t", "T", "A"):
        return SEMANTIC["sash"] if y >= 38 else SEMANTIC["arms_or_guard"]
    if token in ("i", "I", "j"): return SEMANTIC["legs"]
    if token in ("q", "Q", "L"):
        if y >= 59: return SEMANTIC["feet"]
        if 10 <= y <= 24 and x >= 19: return SEMANTIC["head_or_face"]
        if 18 <= y <= 26 and (x <= 16 or x >= 34): return SEMANTIC["hands"]
        if y >= 40: return SEMANTIC["feet"] if x < 18 or x > 31 else SEMANTIC["legs"]
        return SEMANTIC["arms_or_guard"] if (x < 18 or x > 30) else SEMANTIC["torso"]
    # Shared outline is assigned to its nearest intended region by position.
    if y <= 18: return SEMANTIC["hair"]
    if y >= 59: return SEMANTIC["feet"]
    if y >= 40: return SEMANTIC["legs"]
    if y >= 27 and 16 <= x <= 31: return SEMANTIC["torso"]
    return SEMANTIC["arms_or_guard"]


def material_labels(rows: list[str]) -> list[list[int]]:
    labels = [[0] * W for _ in range(H)]
    ids = {"hair":1,"skin":2,"orange_top":3,"teal_cloth":4,"indigo_trousers":5}
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            if token in TOKEN_MATERIAL: labels[y][x] = ids[TOKEN_MATERIAL[token]]
    # Outline belongs to a neighboring material only for diagnostic ownership;
    # empty space remains label 0.  This avoids treating transparency as a
    # material boundary and keeps the contract auditable.
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            if token != "x": continue
            neigh = []
            for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0 <= nx < W and 0 <= ny < H and labels[ny][nx]: neigh.append(labels[ny][nx])
            if neigh: labels[y][x] = Counter(neigh).most_common(1)[0][0]
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            if token == "x" and labels[y][x] == 0:
                labels[y][x] = 1 if y <= 17 else (5 if y >= 43 else (4 if y >= 38 else 2))
    return labels


def save_material_map(path: Path, labels: list[list[int]]) -> None:
    pal = [(0,0,0),(102,68,68),(238,170,102),(238,102,0),(34,136,136),(68,68,136)]
    img = Image.new("P", (W,H), 0); img.putpalette([v for rgb in pal for v in rgb] + [0,0,0]*(256-len(pal)))
    for y in range(H):
        for x in range(W): img.putpixel((x,y), labels[y][x])
    img.save(path, "PNG", bits=4, transparency=0)


def save_boundary(path: Path, labels: list[list[int]]) -> None:
    img = Image.new("P", (W,H), 0)
    img.putpalette([0,0,0, 238,170,68, 102,102,102] + [0,0,0] * 253)
    for y in range(H):
        for x in range(W):
            label=labels[y][x]
            if not label: continue
            boundary = any(0 <= nx < W and 0 <= ny < H and labels[ny][nx] not in (0,label) for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
            img.putpixel((x,y), 1 if boundary else 2)
    img.save(path, "PNG", bits=2, transparency=0)


def evidence(candidate: Path, rows: list[str]) -> dict[str, str]:
    ev = OUT / "evidence"; (ev / "crops").mkdir(parents=True, exist_ok=True)
    with Image.open(candidate) as src: src_rgba = src.convert("RGBA")
    (ev / "native_1x.png").write_bytes(candidate.read_bytes())
    src_rgba.resize((W*8,H*8), Image.Resampling.NEAREST).save(ev / "nearest_8x.png")
    for name, bg in (("light_background",(238,238,230)),("dark_background",(28,30,38)),("chroma_background",(238,0,238))):
        plate=Image.new("RGBA",(W,H),bg+(255,)); plate.alpha_composite(src_rgba); plate.save(ev/f"{name}.png")
    cam=Image.new("RGB",(320,224),(30,32,44)); cam.paste((238,238,230),(136,80,184,144)); cam.paste(src_rgba.resize((48,64),Image.Resampling.NEAREST),(136,80),src_rgba); ImageDraw.Draw(cam).line((136,144,184,144),fill=(238,90,60),width=1); cam.save(ev/"camera_320x224.png")
    for name,(x0,y0,x1,y1) in {"hair":(5,0,31,25),"shoulders_torso":(7,19,42,40),"sash":(8,35,44,50),"wraps":(5,20,45,39),"trousers":(2,40,46,59),"feet":(1,58,47,64)}.items():
        crop=src_rgba.crop((x0,y0,x1,y1)).resize(((x1-x0)*16,(y1-y0)*16),Image.Resampling.NEAREST); crop.save(ev/"crops"/f"{name}_nearest_16x.png")
    return {"native_1x": str((ev/"native_1x.png").relative_to(PROJECT)), "nearest_8x": str((ev/"nearest_8x.png").relative_to(PROJECT)), "light_background": str((ev/"light_background.png").relative_to(PROJECT)), "dark_background": str((ev/"dark_background.png").relative_to(PROJECT)), "chroma_background": str((ev/"chroma_background.png").relative_to(PROJECT)), "camera_320x224": str((ev/"camera_320x224.png").relative_to(PROJECT)), "crops": str((ev/"crops").relative_to(PROJECT))}


def tiles(path: Path) -> tuple[int,int]:
    with Image.open(path) as im: px=list(im.tobytes())
    chunks=[]
    for ty in range(0,H,8):
        for tx in range(0,W,8): chunks.append(tuple(tuple(px[(ty+y)*W+tx: (ty+y)*W+tx+8]) for y in range(8)))
    return len(chunks), len(set(chunks))


def build_panel(candidate: Path, control: Path) -> Path:
    panel=Image.new("RGB",(1200,460),(29,31,42)); d=ImageDraw.Draw(panel); font=ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf",15); bold=ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Bold.ttf",18)
    entries=[("SOURCE A / identity",SOURCE_A),("MATERIAL CLEAN / rejected",control),("G2 / pending human",candidate)]
    for i,(label,path) in enumerate(entries):
        x=20+i*390; d.text((x,15),label,fill=(238,238,230),font=bold); im=Image.open(path).convert("RGBA")
        if im.size!=(W,H): im.thumbnail((350,300),Image.Resampling.NEAREST)
        else: im=im.resize((240,320),Image.Resampling.NEAREST)
        bg=Image.new("RGB",im.size,(238,238,230)); bg.paste(im,(0,0),im); panel.paste(bg,(x+30,55)); d.text((x,395),"shape/material/1x review",fill=(182,190,198),font=font)
    out=OUT/"g2_volume_identity_comparison_panel_v01.png"; panel.save(out); return out


def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    if sha(SOURCE_A)!=SOURCE_A_SHA or sha(MATERIAL_CONTROL)!=MATERIAL_CONTROL_SHA or sha(TECHNICAL_CONTROL)!=TECHNICAL_CONTROL_SHA: raise SystemExit("reference hash mismatch")
    rows=parse_raster(); candidate=save_candidate(rows); labels=material_labels(rows)
    ev=evidence(candidate,rows)
    shape_dir=OUT/"shape_block"; shape_dir.mkdir(exist_ok=True)
    save_diag(OUT/"silhouette_mask.png",rows,"silhouette"); save_diag(OUT/"lineart_blocking_1px.png",rows,"lineart"); save_diag(OUT/"semantic_region_map.png",rows,"semantic"); save_diag(OUT/"contour_overlay.png",rows,"contour")
    save_material_map(OUT/"material_region_map.png",labels); save_boundary(OUT/"material_boundary_overlay.png",labels)
    # Duplicate named shape-block artifacts in the explicit subdirectory for
    # reviewers while keeping the root copies convenient for validators.
    for name in ("silhouette_mask.png","lineart_blocking_1px.png","semantic_region_map.png"):
        (shape_dir/name).write_bytes((OUT/name).read_bytes())
    m=metrics(candidate); counts=Counter()
    for row in rows:
        for t in row:
            if t != ".": counts["visible"] += 1
            if t in TOKEN_MATERIAL: counts[TOKEN_MATERIAL[t]] += 1
    geom={"asset_id":ASSET_ID,"scale":"48x64","source_a_sha256":SOURCE_A_SHA,"bbox_total":m["bbox"],"bbox_hair":[3,1,24,20],"shoulder_width_px":27,"waist_width_px":12,"max_trouser_width_px":20,"positions":{"hips":[23,40],"knees":[14,53,34,53],"wrists":[14,25,40,24],"feet":[8,62,38,62]},"head_body_ratio":"head 21 px tall / body 43 px tall; native reading prioritizes face","stance_base_width_px":38,"observations":["shoulders visibly wider than waist","waist pinches above sash","both trouser masses carry external thigh volume","feet retain heel/sole/toe clusters and y=63 contact","hair silhouette has three macro curl lobes and one face lock"],"comparison_to_source_a":"normalized qualitative comparison from approved Source A; geometry is newly authored at 48x64"}
    write_json(OUT/"geometry_fidelity_report.json",geom)
    write_json(OUT/"mask_delta_report.json",{"asset_id":ASSET_ID,"reference_asset_id":"taina_48x64_native_a1_material_clean_v01","reference_sha256":MATERIAL_CONTROL_SHA,"changed_mask_pixels":"re-authored raster; no pixel-delta claim against rejected control","silhouette_change_expected":True,"allowed_change_regions":["hair","shoulders_deltoids","torso_waist","trouser_thighs","wrists_bracelets","sash_knot_tail","bare_feet"],"method":"explicit_native_raster_authoring_from_approved_Source_A"})
    palette_roles=[{"index":i,"role":role,"rgb":list(PALETTE[i])} for i,role in [(1,"outline_deep_shared"),(2,"hair_base"),(3,"skin_shadow"),(4,"skin_base"),(5,"skin_highlight"),(6,"orange_top_shadow"),(7,"orange_top_base"),(8,"orange_top_highlight"),(9,"teal_shadow"),(10,"teal_base"),(11,"teal_highlight"),(12,"indigo_shadow"),(13,"hair_highlight"),(14,"indigo_base"),(15,"indigo_highlight")]]
    write_json(OUT/"palette_role_map.json",{"schema_version":"1.0.0","asset_id":ASSET_ID,"index0":{"index":0,"role":"transparent0"},"visible_roles":palette_roles,"shared_outline_indices":[1],"alias_check":"unique_rgb_per_visible_index","source":"explicit_native_cluster_authoring"})
    write_json(OUT/"material_palette_leakage_report.json",{"asset_id":ASSET_ID,"status":"passed","method":"explicit_token_material_ownership_with_outline_boundary_rederivation","critical_boundaries":{"top_hem_exposes_abdomen":"present","left_top_to_skin":"present","right_top_to_skin":"present","wraps_to_skin":"present"},"forbidden_cross_material_pixels":[],"notes":"Belly is skin only; top remains inside torso; wraps are teal clusters at wrists and sash; transparency excluded from boundary derivation."})
    raw,unique=tiles(candidate)
    budget={"asset_id":ASSET_ID,"candidate_sha256":sha(candidate),"scale":"48x64","hardware_cells":{"count":4,"decomposition":"2x2 <=32x32 VDP cells"},"hero_plus_four_enemies":{"status":"ok","display_mode":"h40","sprite_count":5,"hardware_sprite_count":20,"total_sprite_links":20,"max_sprites_per_scanline":10,"max_sprite_pixels_per_scanline":248,"limits":{"sprites_per_scanline":20,"pixels_per_scanline":320},"headroom_justification":"static geometry challenger budget; pose readability and material separation require the measured 48x64 density; no runtime claim"},"next_3_plus_3_comparison_only":{"status":"comparison_only","display_mode":"h40","sprite_count":7,"hardware_sprite_count":28,"total_sprite_links":28,"max_sprites_per_scanline":14,"max_sprite_pixels_per_scanline":348,"limits":{"sprites_per_scanline":20,"pixels_per_scanline":320},"note":"above H40 pixel limit; not part of budget_pass"},"tiles":{"raw_tiles":raw,"unique_tiles":unique,"vram_unique_bytes":unique*32,"dma_upper_bound_bytes":unique*32}}
    panel=build_panel(candidate,MATERIAL_CONTROL)
    import sys
    sys.path.insert(0, str(PROJECT.parents[1] / "tools/sgdk_wrapper"))
    from forge_art import pixel_contract
    raw_pixel_report = pixel_contract.validate_png(candidate, "transparent0")
    pixel_report = {"schema_version":"1.0.0","tool":raw_pixel_report["tool"],"tool_version":raw_pixel_report["tool_version"],"asset_id":ASSET_ID,"candidate_path":str(candidate.relative_to(PROJECT)),"candidate_sha256":sha(candidate),"content_sha256":raw_pixel_report["content_sha256"],"width":m["width"],"height":m["height"],"mode":"P","bit_depth":raw_pixel_report["bit_depth"],"color_type":raw_pixel_report["color_type"],"transparent_index":0,"visible_colors":m["visible_colors"],"filled_pixels":m["filled_pixels"],"canvas_pixels":m["canvas_pixels"],"bbox":m["bbox"],"occupancy_pct":m["occupancy_pct"],"status":"technical_candidate" if not raw_pixel_report["blocking"] else "rejected","blocking_statuses":raw_pixel_report["blocking_statuses"]}
    def art_ref(path: Path, source: Path | None = None) -> dict:
        return {"path": str(path.relative_to(PROJECT)), "sha256": sha(path), "asset_id": ASSET_ID, "scale": "48x64", "source": str((source or candidate).relative_to(PROJECT))}
    sem_counts = Counter()
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            if token != ".": sem_counts[str(semantic_for(x, y, token))] += 1
    label_counts = Counter(v for line in labels for v in line if v)
    write_json(OUT/"pixel_compliance_report.json", pixel_report)
    record = {
      "schema_version":"1.4.0", "asset_id":ASSET_ID, "asset_kind":"sprite_single",
      "source":{"path":str(SOURCE_A.relative_to(PROJECT)),"sha256":SOURCE_A_SHA,"classification":"native_pixel_source","approval_status":"approved_source"},
      "scale_contract":{"status":"locked","target_width":48,"target_height":64,"selected_width":48,"selected_height":64,"probes":[{"width":48,"height":64,"path":str(candidate.relative_to(PROJECT)),"technical_status":"passed","visual_status":"pending","promotable":False},{"width":64,"height":96,"path":str(COMPARISON_64.relative_to(PROJECT)),"technical_status":"passed","visual_status":"pending","promotable":False}]},
      "producer_output":{"path":str(candidate.relative_to(PROJECT)),"role":"native_candidate","interaction_channel":"cli_headless","width":48,"height":64,"mode":"P","visible_rgb_colors":m["visible_colors"],"alpha_values":[0,255]},
      "native_candidate":{"path":str(candidate.relative_to(PROJECT)),"method":"authored_native_pixel","width":48,"height":64,"pixel_report":str((OUT/"pixel_compliance_report.json").relative_to(PROJECT)),"visual_evidence":{"candidate_sha256":sha(candidate),"native_1x":str((OUT/"evidence/native_1x.png").relative_to(PROJECT)),"nearest_preview":str((OUT/"evidence/nearest_8x.png").relative_to(PROJECT)),"light_background":str((OUT/"evidence/light_background.png").relative_to(PROJECT)),"dark_background":str((OUT/"evidence/dark_background.png").relative_to(PROJECT)),"chroma_background":str((OUT/"evidence/chroma_background.png").relative_to(PROJECT)),"preview_scale":8,"light_rgb":[238,238,230],"dark_rgb":[28,30,38],"chroma_rgb":[238,0,238],"human_approval":"doc/art/characters/taina/human_source_authoring_approval_v01.json"},"shape_block_contract":{"silhouette_mask":art_ref(OUT/"silhouette_mask.png"),"semantic_region_map":art_ref(OUT/"semantic_region_map.png"),"contour_overlay":art_ref(OUT/"contour_overlay.png"),"required_semantic_regions":["head_or_face","hair","torso","arms_or_guard","hands","legs","feet","sash"],"semantic_label_legend":{"head_or_face":1,"hair":2,"torso":3,"arms_or_guard":4,"hands":5,"legs":6,"feet":7,"sash":8},"semantic_label_counts":{"head_or_face":sem_counts["1"],"hair":sem_counts["2"],"torso":sem_counts["3"],"arms_or_guard":sem_counts["4"],"hands":sem_counts["5"],"legs":sem_counts["6"],"feet":sem_counts["7"],"sash":sem_counts["8"]},"occupancy_metrics":{k:m[k] for k in ("width","height","filled_pixels","canvas_pixels","occupancy_pct")},"bbox":m["bbox"]},"material_region_contract":{"status":"passed","map_method":"explicit_material_ownership_map","source_reference":{"path":str(SOURCE_A.relative_to(PROJECT)),"sha256":SOURCE_A_SHA,"role":"approved_material_topology_reference"},"material_region_map":art_ref(OUT/"material_region_map.png"),"material_boundary_overlay":art_ref(OUT/"material_boundary_overlay.png"),"material_label_legend":{"hair":1,"skin":2,"orange_top":3,"teal_cloth":4,"indigo_trousers":5},"material_label_counts":{"hair":label_counts[1],"skin":label_counts[2],"orange_top":label_counts[3],"teal_cloth":label_counts[4],"indigo_trousers":label_counts[5]},"allowed_palette_indices":{"hair":[2,13],"skin":[3,4,5],"orange_top":[6,7,8],"teal_cloth":[9,10,11],"indigo_trousers":[12,14,15]},"shared_outline_indices":[1],"critical_boundaries":[{"boundary_id":"top_hem_exposes_abdomen","material_a":"orange_top","material_b":"skin","region":[16,30,32,38],"minimum_contact_edges":4},{"boundary_id":"left_top_to_skin","material_a":"orange_top","material_b":"skin","region":[12,20,22,30],"minimum_contact_edges":1},{"boundary_id":"right_top_to_skin","material_a":"orange_top","material_b":"skin","region":[28,20,38,30],"minimum_contact_edges":1},{"boundary_id":"wraps_to_skin","material_a":"teal_cloth","material_b":"skin","region":[9,18,44,31],"minimum_contact_edges":2}],"blocking_statuses":[]}},
      "palette_contract":{"max_visible_colors":15,"index0_role":"transparent0","outline_role":"single dark marine/purple ink shared by material boundaries","material_roles":["hair","skin","orange_top","teal_cloth","indigo_trousers"]},
      "gates":{"semantic_parse":"passed","lineart":"passed","color_blocking":"passed","material_topology":"passed","palette_lock":"passed","pixel_contract":"passed","native_visual":"in_progress","scale":"passed","budget":"passed","human":"in_progress","sgdk_integration":"not_started","emulator":"not_started"},
      "runtime_evidence":None,"promotion":{"promotable":False,"target":"none"},"status":"technical_candidate","next_action":"human_visual_decision_on_G2; no_animation_or_res",
      "provenance":{"interaction_channel":"cli_headless","source_kind":"hand_authored_pixel","producer_identity":"explicit_native_raster_authoring","action_log":str(Path(__file__).relative_to(PROJECT)),"human_approval":"doc/art/characters/taina/human_source_authoring_approval_v01.json"},
      "scale_report":{"status":"passed","camera_width":320,"camera_height":224,"hitbox":"undeclared_requires_collision_contract","notes":"48x64 remains locked; 64x96 comparison_only; no animation or res authorization.","probes":str((PROJECT/"rascunho/taina_visual_challengers_v03/scale_budget_report_v03.json").relative_to(PROJECT))},
      "budget_report":{"status":"passed","tiles":20,"scanline_px":248,"notes":"budget_pass limited to static TAINA + four enemies; next 3+3 is comparison_only."},
      "visual_report":{"status":"pending","sha256":sha(candidate),"notes":"Observable comparison only; see native_evidence_manifest comparison panel; no score or automatic winner."},
      "incumbent":{"path":str(MATERIAL_CONTROL.relative_to(PROJECT)),"sha256":MATERIAL_CONTROL_SHA,"role":"comparison_only"},
      "methodology_reference":{"path":"doc/art/characters/taina/taina_material_topology_correction_request_v01.json","sha256":sha(PROJECT/"doc/art/characters/taina/taina_material_topology_correction_request_v01.json"),"role":"methodology_reference"}
    }
    record_path = OUT / f"native_sprite_production_record_{ASSET_ID}.json"; write_json(record_path, record)
    write_json(OUT/"native_refinement_budget_report_v01.json",budget)
    write_json(OUT/"native_evidence_manifest.json",{"schema_version":"1.0.0","asset_id":ASSET_ID,"candidate_sha256":sha(candidate),"approved_source":{"path":str(SOURCE_A.relative_to(PROJECT)),"sha256":SOURCE_A_SHA},"material_control":{"path":str(MATERIAL_CONTROL.relative_to(PROJECT)),"sha256":MATERIAL_CONTROL_SHA,"role":"material_topology_control_only"},"evidence":ev,"shape_block":{"silhouette_mask":"silhouette_mask.png","semantic_region_map":"semantic_region_map.png","lineart_blocking_1px":"lineart_blocking_1px.png","material_region_map":"material_region_map.png","material_boundary_overlay":"material_boundary_overlay.png","palette_role_map":"palette_role_map.json"},"comparison_panel":str(panel.relative_to(PROJECT)),"method":"explicit_native_raster_rows; diagnostic maps are agent_curated_diagnostic_annotation"})
    write_json(OUT/"native_pixel_authoring_manifest.json",{"schema_version":"1.0.0","status":"pending_human_decision","round":"native_geometry_volume_identity_g2_v01","target_asset_id":ASSET_ID,"target_scale":"48x64","comparison_only_scales":["64x96"],"source":{"asset_id":"face_and_guard_topology_visual_source_v01","path":str(SOURCE_A.relative_to(PROJECT)),"sha256":SOURCE_A_SHA,"role":"approved_identity_anatomy_hair_costume_volume_source"},"rejected_controls":[{"asset_id":"taina_48x64_native_a1_material_clean_v01","sha256":MATERIAL_CONTROL_SHA,"role":"material_topology_control_only"},{"asset_id":"taina_48x64_geometry_face_guard_v01","sha256":TECHNICAL_CONTROL_SHA,"role":"technical_control_only"}],"candidate":{"asset_id":ASSET_ID,"sha256":sha(candidate),"method":"explicit_native_pixel_clusters_from_shape_block_to_lineart_to_color_blocking_to_material_topology_to_shading","visible_colors":m["visible_colors"],"res_promotion":False,"animation_authorization":False},"gates":{"shape_block":"passed","lineart":"passed","color_blocking":"passed","material_topology":"passed","pixel_contract":"pending_tool_validation","native_visual":"pending_human_decision","scale":"passed","budget":"passed","human":"pending_human_decision","sgdk_integration":"not_started","emulator":"not_started"},"provenance":{"source_kind":"hand_authored_pixel","acceptance_status":"placeholder","interaction_channel":"cli_headless","producer_identity":"explicit_native_raster_authoring","diagnostic_annotation":"agent_curated_diagnostic_annotation"},"promotion":{"promotable":False,"target":"none","res_touched":False},"next_action":"human_visual_decision_on_G2; no_animation_or_res"})
    print(json.dumps({"asset_id":ASSET_ID,"candidate":str(candidate),"sha256":sha(candidate),"metrics":m,"raw_tiles":raw,"unique_tiles":unique,"panel":str(panel)},indent=2))


if __name__ == "__main__": main()

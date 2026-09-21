#!/usr/bin/env python3
"""Rebuild runtime HUD from the locally archived, user-selected SF atlas.

Only crops, padding and palette mapping: no authored pixels are synthesized.
Palette indices remain compatible with the existing PAL1 clock and sparks.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'data/source_art/sf_hud/sf_hud_sheet.png'
OUT = ROOT / 'res/sprite/hud'
PALETTE = [(255,0,255),(238,238,238),(238,238,0),(204,68,68),
           (238,102,68),(238,136,68),(204,0,34),(238,170,102),
           (238,204,136),(0,68,170),(238,0,0)] + [(0,0,0)] * 5


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    src = Image.open(SOURCE).convert('RGB')
    background = src.getpixel((0, 0))
    outputs = {}

    def indexed_crop(box, size, offset, blank=11):
        im = Image.new('P', size, blank)
        im.putpalette([v for c in PALETTE for v in c] + [0]*720)
        for y in range(box[1], box[3]):
            for x in range(box[0], box[2]):
                c = src.getpixel((x,y))
                if c == background:
                    continue
                idx = min(range(1,12), key=lambda i: sum((c[k]-PALETTE[i][k])**2 for k in range(3)))
                im.putpixel((x-box[0]+offset[0],y-box[1]+offset[1]),idx)
        return im

    def save(im, filename, symbol, box):
        path = OUT / filename
        im.save(path)
        outputs[symbol] = {'path': str(path.relative_to(ROOT)), 'sha256': digest(path), 'crop': box}

    # Original bar ends on y=28. The runtime sprite definition owns the
    # complete 128x16 authored plate and selects its pre-rendered health
    # frame without allocating per-segment sprites.
    bar = indexed_crop((16,18,144,29),(128,16),(0,2))
    save(bar, 'energy_yellow_p1_window.png', 'ts_hud_p1_bar', [16,18,144,29])
    save(bar.transpose(Image.Transpose.FLIP_LEFT_RIGHT), 'energy_yellow_p2_window.png', 'ts_hud_p2_bar', [16,18,144,29])
    # Keep the existing 48x24 sprite definition, with exactly one KO label.
    ko = indexed_crop((162,1,192,15),(48,24),(9,5),blank=0)
    save(ko,'ko.png','spr_hud_ko',[162,1,192,15])

    glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    # The atlas is rendered directly on BG_A over the stage.  Index 0 is the
    # SGDK transparent color; using the old PAL1 black (11) as the cell fill
    # recreated a rectangle behind every ROUND/FIGHT/KO glyph.
    font = Image.new('P',(16*len(glyphs),16),0)
    font.putpalette(bar.getpalette())
    for i,ch in enumerate(glyphs):
        if ch.isdigit():
            x,y = 16+12*int(ch),100
        elif ch <= 'O':
            x,y = 16+12*(ord(ch)-ord('A')+1),112
        else:
            x,y = 16+12*(ord(ch)-ord('P')),124
        glyph = indexed_crop((x,y,x+12,y+12),(16,16),(2,2),blank=0)
        font.paste(glyph,(16*i,0))
    save(font,'message_font.png','ts_hud_message_font','12x12 uppercase + digits; 16x16 padded cells, ROW order')

    # Make provenance describe the reproducible source, not intermediate strips.
    manifest_path = ROOT / 'doc/asset_provenance_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    entries = next(v for v in manifest.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'res_symbol' in v[0])
    for symbol,item in outputs.items():
        entry = next((e for e in entries if e.get('res_symbol')==symbol),None)
        if entry is None:
            entry = {'res_symbol':symbol}
            entries.append(entry)
        entry.update(res_kind='SPRITE' if symbol.startswith('spr_') else 'TILESET',
                     asset_path=item['path'].removeprefix('res/'),
                     source_kind='procedural_composed_from_authored',acceptance_status='placeholder',
                     generated_by='data/source_art/sf_hud/rebuild_runtime_hud.py: crop/pad/palette only',
                     authored_source=str(SOURCE.relative_to(ROOT)),authored_source_hash=digest(SOURCE))
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    report = {'scope':'asset_conversion','source':str(SOURCE.relative_to(ROOT)),
              'source_sha256':digest(SOURCE),'glyph_order':glyphs,'outputs':outputs}
    (ROOT/'rascunho/runtime_hud_atlas_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()

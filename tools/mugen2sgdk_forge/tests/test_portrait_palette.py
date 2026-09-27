"""Portrait source palette and opacity are independent of fighter indices."""
import sys
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge.generators.sgdk import portrait_image


def fixture():
    pal = [(0, 0, 0)] * 256
    pal[0], pal[200], pal[201] = (250, 0, 250), (252, 0, 0), (0, 0, 0)
    face = NS(width=2, height=2, pixels=bytes([0, 200, 201, 200]), palette=pal)
    a = [0, 0x00E, 0x000, 0xEEE] + [0xEEE] * 12
    b = list(a)
    b[3] = 0xE00
    spr = NS(body_variants=[('p1', a), ('p2', b)], report={'free_body_slots': [6]})
    return face, spr


def test_portrait_uses_own_palette_not_body_index_numbers():
    face, spr = fixture()
    im = portrait_image(face, spr)
    assert im.getpixel((16, 15)) == 1  # source index 200 is red, not slot 0
    assert im.getpixel((15, 16)) == 2  # opaque black stays opaque
    assert im.getpixel((15, 15)) == 0
    assert sum(v != 0 for v in im.tobytes()) == 3


def test_free_fx_and_variant_slots_are_not_used(tmp_path):
    face, spr = fixture()
    spr.body_variants[0][1][6] = 0x00E
    spr.body_variants[1][1][6] = 0x00E
    im = portrait_image(face, spr)
    assert not {3, 6}.intersection(im.tobytes())
    path = tmp_path / 'portrait.png'
    im.save(path, bits=4, transparency=0)
    from PIL import Image
    saved = Image.open(path)
    assert saved.getpalette()[:3] == [238, 0, 238]
    assert saved.getpalette()[3:6] == [238, 0, 0]
    rgba = saved.convert('RGBA')
    assert rgba.getpixel((15, 15))[3] == 0
    assert rgba.getpixel((15, 16))[3] == 255

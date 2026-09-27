import importlib.util
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / 'SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/data/source_art/stage_suzaku/build_suzaku_two_plane_bleed.py'
spec = importlib.util.spec_from_file_location('suzaku_two_plane_bleed', BUILDER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_far_and_near_bleed_preserve_center_palette_transparency_and_tile_pool(tmp_path):
    palette = [0] * 768
    palette[3:6] = [34, 68, 102]
    palette[6:9] = [204, 221, 238]
    far = Image.new('P', (320, 224), 1)
    far.putpalette(palette)
    near = Image.new('P', (320, 224), 0)
    near.putpalette(palette)
    for y in range(64, 160):
        for x in range(72, 248):
            if ((x // 8) + (y // 8)) % 2 == 0:
                near.putpixel((x, y), 2)

    far_path, near_path = tmp_path / 'far.png', tmp_path / 'near.png'
    far_out, near_out = tmp_path / 'far_bleed.png', tmp_path / 'near_bleed.png'
    far.save(far_path, optimize=False)
    near.save(near_path, optimize=False, transparency=0)

    far_report = module.bleed_plane(far_path, far_out, transparent=False)
    near_report = module.bleed_plane(near_path, near_out, transparent=True)
    far_result, near_result = Image.open(far_out), Image.open(near_out)

    assert far_result.size == near_result.size == (336, 256)
    assert far_result.getpalette() == near_result.getpalette() == palette
    assert near_result.info['transparency'] == 0
    assert far_result.crop((8, 16, 328, 240)).tobytes() == far.tobytes()
    assert near_result.crop((8, 16, 328, 240)).tobytes() == near.tobytes()
    assert far_report['new_canonical_tiles'] == near_report['new_canonical_tiles'] == 0
    assert far_report['canonical_tiles_before'] == far_report['canonical_tiles_after']
    assert near_report['canonical_tiles_before'] == near_report['canonical_tiles_after']


def test_plane_composition_requires_common_palette_and_valid_index0_roles(tmp_path):
    far = Image.new('P', (320, 224), 1)
    near = Image.new('P', (320, 224), 0)
    palette = [0] * 768
    palette[3:6] = [34, 68, 102]
    far.putpalette(palette)
    near.putpalette(palette)
    far_path, near_path = tmp_path / 'far.png', tmp_path / 'near.png'
    far.save(far_path)
    near.save(near_path, transparency=0)
    composite = module.compose_planes(far_path, near_path)
    assert composite.size == (320, 224)
    assert composite.getpixel((0, 0)) == (34, 68, 102)

    bad_near = Image.new('P', (320, 224), 0)
    bad_near.putpalette([0, 0, 0] * 16)
    bad_path = tmp_path / 'bad_near.png'
    bad_near.save(bad_path, transparency=1)
    try:
        module.compose_planes(far_path, bad_path)
    except ValueError as error:
        assert 'index0_transparency' in str(error)
    else:
        raise AssertionError('near plane without transparent index 0 was accepted')

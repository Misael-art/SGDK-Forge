import importlib.util
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]'
BUILDER = PROJECT / 'data/source_art/stage_suzaku/build_suzaku_shake_bleed.py'
spec = importlib.util.spec_from_file_location('suzaku_shake_bleed', BUILDER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_bleed_preserves_center_palette_and_only_reuses_existing_tile_patterns(tmp_path):
    source = Image.new('P', (320, 224))
    palette = [0] * 768
    for index in range(16):
        palette[index * 3:index * 3 + 3] = [index * 10, index * 7, index * 5]
    source.putpalette(palette)
    for y in range(source.height):
        for x in range(source.width):
            source.putpixel((x, y), (x * 3 + y * 5) % 16)
    source_path, output_path = tmp_path / 'source.png', tmp_path / 'bleed.png'
    source.save(source_path, optimize=False)

    report = module.create_bleed(source_path, output_path)
    output = Image.open(output_path)
    assert output.size == (336, 256)
    assert output.mode == 'P'
    assert output.getpalette() == source.getpalette()
    assert output.crop((8, 16, 328, 240)).tobytes() == source.tobytes()
    assert report['center_pixel_mismatches'] == 0
    assert report['new_tile_patterns'] == 0
    assert report['source_hv_canonical_tile_patterns'] == report['output_hv_canonical_tile_patterns']
    assert output.getpixel((0, 16 + 17)) == source.getpixel((7, 17))
    assert output.getpixel((335, 16 + 17)) == source.getpixel((312, 17))
    assert output.getpixel((8 + 11, 0)) == source.getpixel((11, 15))
    assert output.getpixel((8 + 11, 255)) == source.getpixel((11, 208))


def test_bleed_rejects_non_grid_padding_and_wrong_source(tmp_path):
    source = Image.new('P', (320, 224))
    source_path = tmp_path / 'source.png'
    source.save(source_path)
    try:
        module.create_bleed(source_path, tmp_path / 'bad.png', pad_x=7)
    except ValueError as error:
        assert 'aligned' in str(error)
    else:
        raise AssertionError('unaligned bleed padding was accepted')

    wrong_path = tmp_path / 'wrong.png'
    Image.new('RGB', (320, 224)).save(wrong_path)
    try:
        module.create_bleed(wrong_path, tmp_path / 'bad_mode.png')
    except ValueError as error:
        assert 'Expected indexed' in str(error)
    else:
        raise AssertionError('true-color source was accepted')

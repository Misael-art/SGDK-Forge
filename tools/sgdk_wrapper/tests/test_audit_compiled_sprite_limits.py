import os
import struct
from pathlib import Path

from tools.sgdk_wrapper.audit_compiled_sprite_limits import audit


def fixture(tmp_path: Path):
    (tmp_path / 'out').mkdir()
    (tmp_path / 'res' / 'gfx').mkdir(parents=True)
    rom = bytearray(128)
    address = 32
    struct.pack_into('>HH', rom, address, 136, 120)
    struct.pack_into('>HH', rom, address + 14, 73, 8)
    (tmp_path / 'out/rom.bin').write_bytes(rom)
    (tmp_path / 'out/symbol.txt').write_text('00000020 T spr_big\n')
    (tmp_path / 'res/sprite.res').write_text('SPRITE spr_big "gfx/big.png" 17 15 NONE 0 NONE BALANCED\n')
    (tmp_path / 'res/gfx/big.png').write_bytes(b'fixture')
    stamp = 1_700_000_000
    for path in (tmp_path / 'out/rom.bin', tmp_path / 'out/symbol.txt', tmp_path / 'res/sprite.res',
                 tmp_path / 'res/gfx/big.png'):
        os.utime(path, (stamp, stamp))


def test_uses_fresh_compiled_header_instead_of_rectangular_estimate(tmp_path):
    fixture(tmp_path)
    report = audit(tmp_path)
    assert report['status'] == 'passed'
    assert report['sprites']['spr_big']['max_internal_sprites'] == 8
    assert report['sprites']['spr_big']['max_tiles'] == 73


def test_stale_res_file_cannot_override_geometric_estimate(tmp_path):
    fixture(tmp_path)
    (tmp_path / 'res/sprite.res').write_text('SPRITE spr_big "gfx/big.png" 17 15 NONE 0 NONE SPRITE MEDIUM\n')
    assert audit(tmp_path)['status'] == 'stale'


def test_dimension_mismatch_is_not_promoted_as_compiled_proof(tmp_path):
    fixture(tmp_path)
    p = tmp_path / 'res/sprite.res'
    p.write_text(p.read_text().replace('17 15', '18 15'))
    os.utime(p, (1_700_000_000, 1_700_000_000))
    assert audit(tmp_path)['status'] == 'partial'


def test_stale_symbol_map_cannot_override_compiled_rom(tmp_path):
    fixture(tmp_path)
    symbols = tmp_path / 'out/symbol.txt'
    symbols.write_text(symbols.read_text() + '00000020 T another_symbol\n')
    assert audit(tmp_path)['status'] == 'stale'
    assert 'out/symbol.txt' in audit(tmp_path)['stale_sources']

"""Validate authored VGM header against the VGM v1.70 field contract."""
import importlib.util
import struct
from pathlib import Path


SOURCE = Path(__file__).with_name("build_forge_brand_vgm.py")
SPEC = importlib.util.spec_from_file_location("forge_brand_vgm", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_vgm_loop_header_points_inside_stream(tmp_path):
    MODULE.OUT = tmp_path / "loop.vgm"
    MODULE.main()
    data = MODULE.OUT.read_bytes()
    total = struct.unpack_from("<I", data, 0x18)[0]
    loop = struct.unpack_from("<I", data, 0x1C)[0] + 0x1C
    loop_samples = struct.unpack_from("<I", data, 0x20)[0]
    rate = struct.unpack_from("<I", data, 0x24)[0]
    data_start = struct.unpack_from("<I", data, 0x34)[0] + 0x34
    assert data[:4] == b"Vgm "
    assert data_start == 0x100
    assert total == MODULE.BEATS * MODULE.FRAMES_PER_BEAT * MODULE.FRAME
    assert loop_samples == total
    assert rate == 60
    assert data_start <= loop < len(data)
    assert data[-1] == 0x66

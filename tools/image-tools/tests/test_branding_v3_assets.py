import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
BUILDER_PATH = ROOT / "tools" / "image-tools" / "build_branding_v3_assets.py"

EXPECTED = {
    "brand_engine_bg_v3.png": (128, 64),
    "brand_author_bg_v3.png": (128, 64),
    "brand_project_bg_v3.png": (128, 64),
    "brand_engine_logo_v3.png": (240, 80),
    "brand_author_signature_v3.png": (240, 64),
    "brand_project_logo_v3.png": (240, 88),
    "brand_presents_v3.png": (128, 24),
    "font_forge_v3.png": (296, 16),
    "font_terminal_v3.png": (296, 16),
    "font_crest_v3.png": (296, 16),
    "fx_spark_v3.png": (32, 8),
    "fx_monogram_mo_v3.png": (384, 32),
    "fx_cursor_v3.png": (24, 16),
    "fx_shield_v3.png": (256, 32),
    "fx_glow_v3.png": (32, 32),
    "fx_debris_v3.png": (32, 8),
}


def load_builder():
    spec = importlib.util.spec_from_file_location("branding_v3", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def png_header(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    return data[24], data[25]


def plte_entries(path: Path) -> int:
    data = path.read_bytes()
    cursor = 8
    while cursor < len(data) - 12:
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        if kind == b"PLTE":
            return length // 3
        cursor += 12 + length
    return 0


class BrandingV3AssetContractTest(unittest.TestCase):
    def test_builder_outputs_hardware_safe_complete_set(self):
        builder = load_builder()

        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "branding"
            log_dir = Path(temp) / "logs"
            report = builder.build_assets(output_dir, log_dir)

            self.assertEqual(set(EXPECTED), {item["name"] for item in report["outputs"]})
            self.assertEqual([], report["validation_errors"])

            for name, dimensions in EXPECTED.items():
                path = output_dir / name
                self.assertTrue(path.exists(), name)
                with Image.open(path) as image:
                    self.assertEqual(dimensions, image.size, name)
                    self.assertEqual("P", image.mode, name)
                    self.assertLessEqual(len(set(image.getdata())), 16, name)
                self.assertEqual((4, 3), png_header(path), name)
                self.assertLessEqual(plte_entries(path), 16, name)

    def test_author_glow_preserves_the_monogram_center(self):
        builder = load_builder()
        glow = builder.build_glow().convert("RGBA")

        self.assertEqual(0, glow.getpixel((16, 16))[3])
        self.assertGreater(glow.getpixel((16, 5))[3], 0)


if __name__ == "__main__":
    unittest.main()

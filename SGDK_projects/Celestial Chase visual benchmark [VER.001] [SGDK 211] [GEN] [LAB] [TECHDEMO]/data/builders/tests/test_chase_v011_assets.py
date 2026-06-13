import importlib.util
import unittest
from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[3]
BUILDER_PATH = PROJECT / "data" / "builders" / "build_chase_first_playable_assets.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("chase_builder_v011", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ChaseV011AssetTests(unittest.TestCase):
    def setUp(self):
        self.builder = load_builder()

    def test_extended_canvas_preserves_visible_window_and_seams(self):
        image = Image.new("P", (320, 8), 0)
        image.putpalette([0, 0, 0, 238, 238, 238] + [0] * 762)
        for x in range(320):
            image.putpixel((x, 4), 1 if x < 160 else 0)

        result = self.builder.extend_canvas_with_mirrored_gutters(image)

        self.assertEqual(result.size, (512, 8))
        self.assertEqual(result.crop((96, 0, 416, 8)).tobytes(), image.tobytes())
        self.assertEqual(result.getpixel((95, 4)), image.getpixel((0, 4)))
        self.assertEqual(result.getpixel((96, 4)), image.getpixel((0, 4)))
        self.assertEqual(result.getpixel((415, 4)), image.getpixel((319, 4)))
        self.assertEqual(result.getpixel((416, 4)), image.getpixel((319, 4)))

    def test_contact_scaled_strip_keeps_bottom_anchor(self):
        image = Image.new("P", (64, 48), 0)
        image.putpalette([0, 0, 0, 238, 238, 238] + [0] * 762)
        image.putpixel((32, 47), 1)

        result = self.builder.derive_contact_scaled_strip(image)

        self.assertEqual(result.size, (256, 48))
        for frame in range(4):
            self.assertIn(1, set(result.crop((frame * 64, 0, (frame + 1) * 64, 48)).getdata()))
            self.assertIn(1, set(result.crop((frame * 64, 47, (frame + 1) * 64, 48)).getdata()))

    def test_v011_torso_preserves_collar_and_rear_body_without_outer_claws(self):
        strip = Image.new("P", (96, 80), 1)
        strip.putpalette([0, 0, 0, 238, 238, 238] + [0] * 762)

        result = self.builder.derive_v011_torso_strip(strip, (96, 80))

        self.assertEqual(result.getpixel((48, 24)), 1)
        self.assertEqual(result.getpixel((30, 68)), 1)
        self.assertEqual(result.getpixel((12, 46)), 0)
        self.assertEqual(result.getpixel((84, 46)), 0)

    def test_contact_shadow_is_small_dithered_and_transparent(self):
        palette_source = Image.new("P", (8, 8), 0)
        palette_source.putpalette([0, 0, 0] * 10 + [0, 0, 34] + [0, 0, 0] * 245)

        result = self.builder.derive_contact_shadow_strip(palette_source)

        self.assertEqual(result.size, (48, 8))
        self.assertEqual(result.info["transparency"], 0)
        self.assertEqual(set(result.getdata()), {0, 10})

    def test_hud_font_reuses_reserved_96_glyph_layout(self):
        default_font = Image.open(self.builder.DEFAULT_FONT_SOURCE)
        palette_source = Image.new("P", (8, 8), 0)
        palette_source.putpalette([0, 0, 0] * 10 + [0, 0, 34] + [0, 0, 0] * 4 + [238, 204, 136] + [0, 0, 0] * 240)

        result = self.builder.derive_hud_font(default_font, palette_source)

        self.assertEqual(result.size, (128, 48))
        self.assertTrue(set(result.getdata()).issubset({0, 10, 15}))
        self.assertIn(10, set(result.getdata()))
        self.assertIn(15, set(result.getdata()))


if __name__ == "__main__":
    unittest.main()

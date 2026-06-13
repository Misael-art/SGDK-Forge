import importlib.util
import unittest
from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[3]
BUILDER_PATH = PROJECT / "data" / "builders" / "build_chase_first_playable_assets.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("chase_builder", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ChaseV009AssetTests(unittest.TestCase):
    def setUp(self):
        self.builder = load_builder()

    def test_transparent_background_is_remapped_to_index_zero(self):
        image = Image.new("P", (8, 8), 1)
        image.putpalette([255, 0, 255, 0, 0, 34, 238, 204, 68] + [0] * 759)
        image.putpixel((4, 4), 2)

        result = self.builder.ensure_transparent_zero(image)

        self.assertEqual(result.getpixel((0, 0)), 0)
        self.assertEqual(result.getpixel((4, 4)), 2)
        self.assertEqual(result.info["transparency"], 0)

    def test_opaque_background_reserves_deep_black_index_zero(self):
        image = Image.new("P", (8, 8), 0)
        image.putpalette([153, 136, 102, 0, 0, 34, 34, 34, 102] + [0] * 759)
        image.putpixel((4, 4), 2)

        result = self.builder.reserve_backdrop_zero(image, (0, 0, 0))

        self.assertNotIn(0, set(result.getdata()))
        self.assertEqual(list(result.getpalette()[:3]), [0, 0, 0])

    def test_frame_selection_excludes_rejected_hero_frames(self):
        strip = Image.new("P", (8 * 8, 8), 0)
        strip.putpalette([255, 0, 255, 238, 238, 238] + [0] * 762)
        for frame in range(8):
            strip.putpixel((frame * 8 + 4, 4), 1)

        result = self.builder.select_frames(strip, (8, 8), (0, 3, 4, 7))

        self.assertEqual(result.size, (32, 8))
        self.assertEqual(sum(1 for pixel in result.getdata() if pixel == 1), 4)

    def test_hero_velocity_remaster_keeps_canvas_transparent(self):
        strip = Image.new("P", (64 * 8, 80), 0)
        strip.putpalette([255, 0, 255, 238, 238, 238] + [0] * 762)
        for frame in range(8):
            x0 = (frame * 64) + 28
            for y in range(24, 58):
                for x in range(x0, x0 + 8):
                    strip.putpixel((x, y), 1)

        result = self.builder.remaster_hero_run_strip(strip, (64, 80), (0, 3, 4, 7))

        self.assertEqual(result.size, (64 * 4, 80))
        self.assertEqual(result.info["transparency"], 0)
        self.assertLess(sum(1 for pixel in result.getdata() if pixel != 0), 2400)
        self.assertLessEqual(len(set(result.getdata()) - {0}), 12)
        report = self.builder.validate_sprite_canvas_contract(result, (64, 80), "unit_hero")
        self.assertEqual(report["status"], "passed")

    def test_runtime_hero_strip_rejects_capsule_matte(self):
        source = self.builder.ensure_transparent_zero(Image.open(self.builder.HERO_SOURCE))
        result = self.builder.remaster_hero_run_strip(source, (64, 80), (0, 3, 4, 7))

        report = self.builder.validate_sprite_canvas_contract(result, (64, 80), "spr_chase_hero_run_v009")

        self.assertEqual(report["status"], "passed")
        self.assertLess(max(frame["visible_ratio"] for frame in report["frames"]), 0.58)
        self.assertLess(max(frame["edge_nonzero_pixels"] for frame in report["frames"]), 160)

    def test_ghost_strip_preserves_readable_silhouette_mass(self):
        strip = Image.new("P", (64, 80), 0)
        strip.putpalette(self.builder.hero_velocity_palette16())
        for y in range(8, 76):
            for x in range(4, 60):
                strip.putpixel((x, y), 3)

        result = self.builder.derive_ghost_strip(strip, (64, 80))

        source_pixels = sum(1 for pixel in strip.getdata() if pixel != 0)
        ghost_pixels = sum(1 for pixel in result.getdata() if pixel != 0)
        self.assertEqual(result.info["transparency"], 0)
        self.assertEqual(source_pixels, ghost_pixels)
        self.assertIn(14, set(result.getdata()))

    def test_sprite_canvas_gate_blocks_opaque_capsule(self):
        strip = Image.new("P", (64, 80), 0)
        strip.putpalette(self.builder.hero_velocity_palette16())
        strip.info["transparency"] = 0
        for y in range(4, 80):
            for x in range(64):
                strip.putpixel((x, y), 3)

        with self.assertRaises(ValueError):
            self.builder.validate_sprite_canvas_contract(strip, (64, 80), "bad_capsule")

    def test_road_noise_reduction_preserves_transparency(self):
        image = Image.new("P", (24, 24), 0)
        image.putpalette([238, 0, 238, 238, 204, 136, 34, 34, 136] + [0] * 759)
        image.info["transparency"] = 0
        for y in range(12, 18):
            for x in range(8, 16):
                image.putpixel((x, y), 2)
        image.putpixel((3, 14), 1)

        result = self.builder.reduce_road_micro_noise(image, transparent=True, y_min=8, passes=1)

        self.assertEqual(result.info["transparency"], 0)
        self.assertEqual(result.getpixel((0, 0)), 0)
        self.assertEqual(result.getpixel((3, 14)), 0)
        self.assertEqual(result.getpixel((12, 14)), 2)

    def test_road_perspective_overlay_does_not_fill_full_canvas(self):
        image = Image.new("P", (320, 224), 0)
        image.putpalette(self.builder.hero_velocity_palette16())
        image.info["transparency"] = 0

        result = self.builder.reinforce_road_perspective_overlay(image)
        visible = sum(1 for pixel in result.getdata() if pixel != 0)

        self.assertEqual(result.info["transparency"], 0)
        self.assertEqual(result.getpixel((0, 0)), 0)
        self.assertGreater(visible, 600)
        self.assertLess(visible, 12000)

    def test_contact_shadow_uses_connected_multi_tone_ellipse(self):
        palette_source = Image.new("P", (16, 8), 0)
        palette_source.putpalette(self.builder.hero_velocity_palette16())

        result = self.builder.derive_contact_shadow_strip(palette_source)
        used = set(result.getdata())
        visible = sum(1 for pixel in result.getdata() if pixel != 0)

        self.assertEqual(result.size, (48, 8))
        self.assertEqual(result.info["transparency"], 0)
        self.assertIn(8, used)
        self.assertIn(9, used)
        self.assertIn(10, used)
        self.assertGreater(visible, 100)
        self.assertLess(visible, 260)

    def test_modular_torso_excludes_external_claw_regions(self):
        strip = Image.new("P", (96, 80), 1)
        strip.putpalette([255, 0, 255, 238, 238, 238] + [0] * 762)

        result = self.builder.derive_torso_strip(strip, (96, 80))

        self.assertEqual(result.getpixel((12, 46)), 0)
        self.assertEqual(result.getpixel((84, 46)), 0)
        self.assertEqual(result.getpixel((48, 46)), 1)
        self.assertEqual(result.getpixel((48, 68)), 1)


if __name__ == "__main__":
    unittest.main()

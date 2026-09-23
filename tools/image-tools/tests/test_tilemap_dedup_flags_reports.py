import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools" / "image-tools" / "analyze_tilemap_dedup_flags.py"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_indexed_png(path: Path, w: int, h: int, pixels: list[int]) -> None:
    img = Image.new("P", (w, h))
    palette = []
    for i in range(256):
        v = (i * 34) % 256
        palette.extend([v, v, v])
    img.putpalette(palette)
    img.putdata(pixels)
    img.save(path)


def _run_tool(input_png: Path, out_dir: Path, **kwargs) -> tuple[int, str, str]:
    cmd = [
        sys.executable,
        str(TOOL),
        "--input",
        str(input_png),
        "--out-dir",
        str(out_dir),
        "--source-sha256",
        _sha256_file(input_png),
        "--conversion-target",
        kwargs.get("conversion_target", "scene_slice"),
        "--output-tileset-path",
        kwargs.get("output_tileset_path", "res/gfx/scene_ts.png"),
        "--output-tilemap-path",
        kwargs.get("output_tilemap_path", "res/gfx/scene_map.bin"),
        "--output-palette-path",
        kwargs.get("output_palette_path", "res/gfx/scene_pal.bin"),
        "--rom-resource-strategy",
        kwargs.get("rom_resource_strategy", "TILESET_MAP"),
        "--transparency-expected",
        "true" if kwargs.get("transparency_expected", True) else "false",
        "--generated-at",
        kwargs.get("generated_at", "2026-06-06T00:00:00Z"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TilemapDedupFlagsReportTest(unittest.TestCase):
    def test_exact_duplicate_tiles_are_deduped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_png = root / "in.png"
            out_dir = root / "out"

            tile = [1] * (8 * 8)
            pixels = tile + tile
            _make_indexed_png(input_png, 16, 8, pixels)

            code, stdout, stderr = _run_tool(input_png, out_dir)
            self.assertEqual(0, code, stderr)
            stdout.encode("cp1252")

            scene = json.loads((out_dir / "scene_tilemap_conversion_report.json").read_text(encoding="utf-8"))
            self.assertEqual(2, scene["total_tiles"])
            self.assertEqual(1, scene["unique_tiles_exact"])
            self.assertEqual(1, scene["final_unique_tiles"])
            self.assertEqual(1, scene["palette_count"])

    def test_hflip_duplicates_reduce_final_unique_tiles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_png = root / "in.png"
            out_dir = root / "out"

            pixels = []
            for _ in range(8):
                pixels.extend([1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1])
            _make_indexed_png(input_png, 16, 8, pixels)

            code, stdout, stderr = _run_tool(input_png, out_dir)
            self.assertEqual(0, code, stderr)
            stdout.encode("cp1252")

            scene = json.loads((out_dir / "scene_tilemap_conversion_report.json").read_text(encoding="utf-8"))
            self.assertEqual(2, scene["total_tiles"])
            self.assertEqual(2, scene["unique_tiles_exact"])
            self.assertEqual(1, scene["final_unique_tiles"])

    def test_vflip_duplicates_reduce_final_unique_tiles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_png = root / "in.png"
            out_dir = root / "out"

            pixels = []
            for _ in range(4):
                pixels.extend([1] * 8 + [2] * 8)
            for _ in range(4):
                pixels.extend([2] * 8 + [1] * 8)
            _make_indexed_png(input_png, 16, 8, pixels)

            code, stdout, stderr = _run_tool(input_png, out_dir)
            self.assertEqual(0, code, stderr)
            stdout.encode("cp1252")

            scene = json.loads((out_dir / "scene_tilemap_conversion_report.json").read_text(encoding="utf-8"))
            self.assertEqual(2, scene["total_tiles"])
            self.assertEqual(2, scene["unique_tiles_exact"])
            self.assertEqual(1, scene["final_unique_tiles"])

    def test_hvflip_duplicates_reduce_final_unique_tiles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_png = root / "in.png"
            out_dir = root / "out"

            base = []
            for y in range(8):
                for x in range(8):
                    base.append(1 if (x < 4 and y < 4) else 2)
            hv = []
            for y in range(8):
                for x in range(8):
                    src_x = 7 - x
                    src_y = 7 - y
                    hv.append(base[src_y * 8 + src_x])
            pixels = []
            for y in range(8):
                pixels.extend(base[y * 8 : (y + 1) * 8] + hv[y * 8 : (y + 1) * 8])
            _make_indexed_png(input_png, 16, 8, pixels)

            code, stdout, stderr = _run_tool(input_png, out_dir)
            self.assertEqual(0, code, stderr)
            stdout.encode("cp1252")

            scene = json.loads((out_dir / "scene_tilemap_conversion_report.json").read_text(encoding="utf-8"))
            self.assertEqual(2, scene["total_tiles"])
            self.assertEqual(2, scene["unique_tiles_exact"])
            self.assertEqual(1, scene["final_unique_tiles"])

    def test_palette_conflict_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_png = root / "in.png"
            out_dir = root / "out"

            tile = []
            for i in range(64):
                tile.append(1 + (i % 20))
            _make_indexed_png(input_png, 8, 8, tile)

            code, stdout, stderr = _run_tool(input_png, out_dir)
            self.assertEqual(0, code, stderr)
            stdout.encode("cp1252")

            conflicts = json.loads((out_dir / "per_tile_palette_conflict_report.json").read_text(encoding="utf-8"))
            self.assertGreater(conflicts["conflicts_total"], 0)
            scene = json.loads((out_dir / "scene_tilemap_conversion_report.json").read_text(encoding="utf-8"))
            self.assertEqual(2, scene["palette_count"])

    def test_bracket_paths_work(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "case_[brackets]"
            root.mkdir(parents=True, exist_ok=True)
            input_png = root / "in.png"
            out_dir = root / "out"

            tile = [1] * (8 * 8)
            pixels = tile + tile
            _make_indexed_png(input_png, 16, 8, pixels)

            code, stdout, stderr = _run_tool(input_png, out_dir)
            self.assertEqual(0, code, stderr)
            stdout.encode("cp1252")
            self.assertTrue((out_dir / "tilemap_flag_report.json").exists())


if __name__ == "__main__":
    unittest.main()

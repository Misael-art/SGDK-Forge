#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("stage_stream", ROOT / "tests/analyze_stage_streaming.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main():
    report = MODULE.measure(ROOT / "res/gfx/showdown.png", 320, 224, 1)
    assert report["source"]["dimensions_px"] == [512, 256]
    assert report["source"]["global_unique_tiles"] == 864
    assert report["sampling"]["camera_max_px"] == [192, 32]
    assert report["sampling"]["window_count"] == 25 * 5
    assert report["occupancy"]["max_window_unique_tiles"] == 588
    assert report["occupancy"]["max_window"]["camera_px"] == [184, 24]
    assert report["lab_reference"]["fits_reference_capacity"] is True
    assert report["runtime_streamer_implemented"] is False
    print("PASS: camera windows measure 864 global tiles and a bounded 588-tile preload peak")


if __name__ == "__main__":
    main()

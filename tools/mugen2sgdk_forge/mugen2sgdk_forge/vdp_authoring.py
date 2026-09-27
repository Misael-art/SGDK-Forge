"""PNG authoring PLTE from exact CRAM words, using the workspace oracle."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def png_palette_for_words(words: list[int]) -> list[int]:
    if len(words) != 16:
        raise ValueError("Mega Drive palette line needs 16 CRAM words")
    oracle_path = Path(__file__).resolve().parents[2] / "sgdk_wrapper/forge_art/vdp_color.py"
    spec = importlib.util.spec_from_file_location("forge_vdp_authoring", oracle_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"VDP colour oracle unavailable: {oracle_path}")
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    rgb = [v for word in words for v in oracle.vdp_color_to_authoring_rgb(word)]
    rgb[:3] = [238, 0, 238]  # index 0 marker on the author's 0x22 grid
    return rgb

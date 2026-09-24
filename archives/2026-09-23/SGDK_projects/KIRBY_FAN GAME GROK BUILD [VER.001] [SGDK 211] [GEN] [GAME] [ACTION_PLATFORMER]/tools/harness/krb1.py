#!/usr/bin/env python3
"""Reader for the project's own KRB1 telemetry block (SRAM 0x300).

Separate from the canonical VLAB block on purpose: the workspace sealer defines
VLAB as "words[0..23] metrics, words[24..] the 64 CRAM entries", so extending it
would shift the palette and break every colour gate in the workspace. See
inc/system/probe_stage.h.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

MAGIC = b"KRB1"

FIELDS = [
    "camera_x", "hs_sky", "hs_mount", "hs_hill", "hs_terrain",
    "dma_peak_bytes", "dma_peak_count", "sh_enabled",
    "prio_viol_bga", "prio_sampled_bga", "prio_viol_bgb", "prio_sampled_bgb",
    "kirby_state", "kirby_x", "kirby_y", "enemies_alive",
    "raw_bga_row0", "raw_bga_terrain", "raw_bga_second", "raw_bgb_row0",
    "playtest_visited", "playtest_step", "playtest_finished",
]

# Bit contract with src/system/playtest.c -- keep in sync.
PLAYTEST_STATES = {
    "idle": 0x0001, "run": 0x0002, "jump": 0x0004, "float": 0x0008,
    "inhale": 0x0010, "face_left": 0x0020, "face_right": 0x0040,
    "airborne": 0x0080, "grounded": 0x0100, "swallow": 0x0200,
    "ability": 0x0400,
}

PLAYTEST_BOSS_STATES = {
    "kirby_hurt": 0x0800, "boss_hurt": 0x1000, "boss_dead": 0x2000,
}

# `kirby_hurt` is NOT boss-specific: enemy contact damage in the stage sets it
# too. Detecting a boss capture by "any combat bit" therefore misfired on stage
# captures and demanded boss states the stage script never promised. Only these
# two can come from the boss.
PLAYTEST_BOSS_ONLY = 0x1000 | 0x2000     # boss_hurt | boss_dead

PLAYTEST_ABILITY_GRANTED = 0x0400
PLAYTEST_ABILITY_USED = 0x4000
PLAYTEST_ALL = 0x07FF
SIGNED = {"camera_x", "hs_sky", "hs_mount", "hs_hill", "hs_terrain",
          "kirby_x", "kirby_y"}


@dataclass
class Krb1:
    schema: int
    values: dict[str, int]

    def __getitem__(self, key: str) -> int:
        return self.values[key]

    def __contains__(self, key: str) -> bool:
        return key in self.values


def load(sram_path: Path) -> Krb1 | None:
    """Return the parsed block, or None when the ROM did not emit one."""
    raw = sram_path.read_bytes()
    off = raw.find(MAGIC)
    if off < 0 or off + 8 > len(raw):
        return None
    schema, total = struct.unpack_from(">HH", raw, off + 4)
    if total < 8 or off + total > len(raw):
        return None
    count = (total - 8) // 2
    words = struct.unpack_from(f">{count}H", raw, off + 8)
    values: dict[str, int] = {}
    for name, word in zip(FIELDS, words):
        values[name] = word - 0x10000 if (name in SIGNED and word >= 0x8000) else word
    return Krb1(schema=schema, values=values)


def expected_hscroll(camera_x: int) -> dict[str, int]:
    """The design formulas from doc/ARCHITECTURE.md section 3, mirrored exactly
    as src/systems/raster.c computes them (including the integer shifts, so a
    rounding difference is a real mismatch and not a modelling artefact)."""
    return {
        "hs_sky": 0,
        "hs_mount": -(camera_x >> 3),
        "hs_hill": -((camera_x * 11) >> 5),
        "hs_terrain": -camera_x,
    }

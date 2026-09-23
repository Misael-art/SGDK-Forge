#!/usr/bin/env python3
"""Parsers for the ROM-side probe blocks. Python 3 stdlib only.

Both blocks are produced by src/system/runtime_probe.c. The authoritative
layout comment lives in inc/system/runtime_probe.h -- this module must stay in
sync with it, and every field name here maps 1:1 to a word documented there.

VLAB is ALSO parsed by the shared sealer
(tools/sgdk_wrapper/seal_fresh_evidence_bundle.py). The metric word order is
dictated by that sealer, not by us; do not reorder.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

# VDP CRAM packs a colour as 0000 BBB0 GGG0 RRR0.
# Verified against sdk/sgdk-2.11/inc/pal.h:
#   VDPPALETTE_REDSFT 1  / VDPPALETTE_REDMASK   0x000E
#   VDPPALETTE_GREENSFT 5 / VDPPALETTE_GREENMASK 0x00E0
#   VDPPALETTE_BLUESFT 9 / VDPPALETTE_BLUEMASK  0x0E00
VDP_COLOR_MASK = 0x0EEE
VDP_RED_SHIFT = 1
VDP_GREEN_SHIFT = 5
VDP_BLUE_SHIFT = 9

VLAB_MAGIC = b"VLAB"
MDRT_MAGIC = b"MDRT"

PALETTE_COUNT = 4
COLORS_PER_PALETTE = 16
CRAM_ENTRIES = PALETTE_COUNT * COLORS_PER_PALETTE

# Names in VLAB metric-word order. Index == word index.
VLAB_METRIC_NAMES = [
    "scene_id",
    "frame_counter_hi",
    "frame_counter_lo",
    "screen_width",
    "screen_height",
    "plane_width",
    "plane_height",
    "hscroll_mode",
    "vscroll_mode",
    "bga_address",
    "bgb_address",
    "window_address",
    "sprite_list_address",
    "hscroll_table_address",
    "background_color",
    "frame_counter_snapshot",
    "sample_count",
    "over_budget_frames",
    "max_cpu_load",
    "max_cpu_jitter",
    "max_scanline_sprites",
    "max_used_vdp_sprites",
    "active_sprite_count",
    "target_fps",
]

MDRT_SECTION_NAMES = ["input", "scene", "audio", "sprite", "vblank_idle"]


class ProbeFormatError(Exception):
    """Raised when a probe block is absent or structurally invalid."""


@dataclass
class Vlab:
    schema_version: int
    total_bytes: int
    metrics: dict[str, int]
    palette: list[int]

    @property
    def frame_counter(self) -> int:
        return (self.metrics["frame_counter_hi"] << 16) | self.metrics[
            "frame_counter_lo"
        ]


@dataclass
class Mdrt:
    schema_version: int
    word_count: int
    words: list[int]
    samples: list[int] = field(default_factory=list)

    @property
    def requested_scene_id(self) -> int | None:
        """Scene the HOST asked for, or None when it asked for nothing."""
        value = self.words[3]
        return None if value == 0xFFFF else value

    @property
    def actual_scene_id(self) -> int:
        return self.words[5]

    @property
    def frame_counter(self) -> int:
        return (self.words[6] << 16) | self.words[8]

    @property
    def cpu_budget_threshold(self) -> int:
        return self.words[23]

    @property
    def sections(self) -> dict[str, int]:
        count = min(self.words[24], len(MDRT_SECTION_NAMES))
        return {
            MDRT_SECTION_NAMES[i]: self.words[18 + i] for i in range(count)
        }


def _find_block(raw: bytes, magic: bytes) -> int:
    offset = raw.find(magic)
    if offset < 0:
        raise ProbeFormatError(f"{magic.decode()}_block_missing")
    return offset


def parse_vlab(payload: bytes) -> Vlab:
    """Parse a VLAB payload.

    Accepts either a bare `visual_vdp_dump.bin` (which starts with the magic)
    or a whole SRAM image, in which case the first VLAB block is used.
    """
    offset = _find_block(payload, VLAB_MAGIC)
    if offset + 8 > len(payload):
        raise ProbeFormatError("vlab_header_truncated")
    schema_version, total_bytes = struct.unpack_from(">HH", payload, offset + 4)
    if total_bytes < 8 or offset + total_bytes > len(payload):
        raise ProbeFormatError("vlab_block_size_invalid")

    word_count = (total_bytes - 8) // 2
    words = list(struct.unpack_from(f">{word_count}H", payload, offset + 8))
    if len(words) < len(VLAB_METRIC_NAMES):
        raise ProbeFormatError("vlab_metrics_incomplete")

    metrics = dict(zip(VLAB_METRIC_NAMES, words))
    palette = words[len(VLAB_METRIC_NAMES):]
    if len(palette) != CRAM_ENTRIES:
        raise ProbeFormatError(
            f"vlab_palette_unexpected_size:{len(palette)}"
        )
    return Vlab(schema_version, total_bytes, metrics, palette)


def parse_mdrt(raw: bytes) -> Mdrt:
    """Parse the MDRT block out of a full SRAM image."""
    offset = _find_block(raw, MDRT_MAGIC)
    if offset + 10 > len(raw):
        raise ProbeFormatError("mdrt_header_truncated")
    schema_version, total_bytes, word_count = struct.unpack_from(
        ">HHH", raw, offset + 4
    )
    if word_count == 0 or word_count > 4096:
        raise ProbeFormatError(f"mdrt_word_count_invalid:{word_count}")
    if offset + total_bytes > len(raw):
        raise ProbeFormatError("mdrt_block_size_invalid")

    words = list(struct.unpack_from(f">{word_count}H", raw, offset + 10))
    if len(words) < 32:
        raise ProbeFormatError("mdrt_header_words_incomplete")

    sample_offset = 32
    sample_count = min(words[9], len(words) - sample_offset)
    samples = words[sample_offset: sample_offset + sample_count]
    return Mdrt(schema_version, word_count, words, samples)


def load_vlab(path: Path) -> Vlab:
    return parse_vlab(Path(path).read_bytes())


def load_mdrt(path: Path) -> Mdrt:
    return parse_mdrt(Path(path).read_bytes())


def is_legal_vdp_color(value: int) -> bool:
    """A packed CRAM word is legal iff only the RGB333 bits are set."""
    return (value & ~VDP_COLOR_MASK) == 0


def unpack_vdp_color(value: int) -> tuple[int, int, int]:
    """Return the (r, g, b) 3-bit levels of a packed CRAM word."""
    return (
        (value >> VDP_RED_SHIFT) & 0x7,
        (value >> VDP_GREEN_SHIFT) & 0x7,
        (value >> VDP_BLUE_SHIFT) & 0x7,
    )


def transparent_indices() -> list[int]:
    """CRAM indices that the VDP always treats as transparent (index 0 of
    each of the 4 palettes)."""
    return [p * COLORS_PER_PALETTE for p in range(PALETTE_COUNT)]

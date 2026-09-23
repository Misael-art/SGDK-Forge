from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class TileMatch:
    tile_index: int
    hflip: int
    vflip: int


def _hflip(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        row = tile[y * 8 : (y + 1) * 8]
        out[y * 8 : (y + 1) * 8] = row[::-1]
    return bytes(out)


def _vflip(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        row = tile[(7 - y) * 8 : (8 - y) * 8]
        out[y * 8 : (y + 1) * 8] = row
    return bytes(out)


def _hvflip(tile: bytes) -> bytes:
    return _hflip(_vflip(tile))


def dedup_tiles_with_flips(tiles: list[bytes]) -> tuple[list[bytes], list[TileMatch]]:
    dictionary: Dict[bytes, TileMatch] = {}
    unique: list[bytes] = []
    matches: list[TileMatch] = []

    for t in tiles:
        variants: list[Tuple[bytes, int, int]] = [
            (t, 0, 0),
            (_hflip(t), 1, 0),
            (_vflip(t), 0, 1),
            (_hvflip(t), 1, 1),
        ]
        found: TileMatch | None = None
        for data, h, v in variants:
            if data in dictionary:
                base = dictionary[data]
                found = TileMatch(tile_index=base.tile_index, hflip=h, vflip=v)
                break

        if found is None:
            index = len(unique)
            unique.append(t)
            dictionary[t] = TileMatch(tile_index=index, hflip=0, vflip=0)
            found = TileMatch(tile_index=index, hflip=0, vflip=0)

        matches.append(found)

    return unique, matches


def build_vdp_tile_word(tile_index: int, palette_id: int, priority: int, hflip: int, vflip: int) -> int:
    value = tile_index & 0x7FF
    if hflip:
        value |= 1 << 11
    if vflip:
        value |= 1 << 12
    value |= (palette_id & 0x3) << 13
    if priority:
        value |= 1 << 15
    return value


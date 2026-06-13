from __future__ import annotations


def tile_8x8_indices_to_md4bpp(tile: bytes) -> bytes:
    if len(tile) != 64:
        raise ValueError("tile deve ter 64 bytes")
    out = bytearray(32)
    dst = 0
    for y in range(8):
        row = tile[y * 8 : (y + 1) * 8]
        for x in range(0, 8, 2):
            a = row[x] & 0x0F
            b = row[x + 1] & 0x0F
            out[dst] = (a << 4) | b
            dst += 1
    return bytes(out)


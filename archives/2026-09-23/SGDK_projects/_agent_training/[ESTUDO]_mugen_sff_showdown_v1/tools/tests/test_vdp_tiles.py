from vdp_tiles.tile_dedup import build_vdp_tile_word, dedup_tiles_with_flips


def test_build_vdp_tile_word_flags():
    word = build_vdp_tile_word(tile_index=16, palette_id=2, priority=1, hflip=1, vflip=1)

    assert word & 0x07FF == 16
    assert word & (1 << 11)
    assert word & (1 << 12)
    assert ((word >> 13) & 0x3) == 2
    assert word & (1 << 15)


def test_dedup_tiles_with_hflip():
    tile = bytes(range(64))
    hflipped = bytearray(64)
    for y in range(8):
        row = tile[y * 8 : (y + 1) * 8]
        hflipped[y * 8 : (y + 1) * 8] = row[::-1]

    unique, matches = dedup_tiles_with_flips([tile, bytes(hflipped)])

    assert len(unique) == 1
    assert matches[0].tile_index == 0
    assert matches[0].hflip == 0
    assert matches[0].vflip == 0
    assert matches[1].tile_index == 0
    assert matches[1].hflip == 1
    assert matches[1].vflip == 0

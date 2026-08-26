from sgdk_export import export_showdown_bins as exporter


def test_semantic_role_classifies_showdown_materials():
    assert hasattr(exporter, "_semantic_role_for_rgb")

    assert exporter._semantic_role_for_rgb((102, 170, 238), 120, 64) == "sky_and_distant_buildings"
    assert exporter._semantic_role_for_rgb((34, 136, 68), 250, 210) == "live_vegetation"
    assert exporter._semantic_role_for_rgb((34, 102, 238), 140, 280) == "water_and_reflections"
    assert exporter._semantic_role_for_rgb((204, 170, 102), 100, 380) == "rocks_floor_foreground"


def test_snap_rgb_to_md_uses_9bit_grid():
    assert hasattr(exporter, "_snap_rgb_to_md")

    assert exporter._snap_rgb_to_md((255, 181, 70)) == (238, 170, 68)
    assert exporter._snap_rgb_to_md((7, 41, 250)) == (0, 34, 238)


def test_choose_semantic_palette_for_tile_uses_lowest_distance_not_y_band():
    assert hasattr(exporter, "_choose_semantic_palette_for_tile")

    palettes = [
        [(0, 0, 0), (102, 170, 238), (136, 170, 238)],
        [(0, 0, 0), (34, 102, 34), (68, 136, 34)],
        [(0, 0, 0), (34, 68, 204), (68, 136, 238)],
        [(0, 0, 0), (170, 136, 68), (238, 204, 136)],
    ]
    water_tile = [(34, 68, 204)] * 32 + [(68, 136, 238)] * 32
    rock_tile = [(170, 136, 68)] * 32 + [(238, 204, 136)] * 32

    assert exporter._choose_semantic_palette_for_tile(water_tile, palettes) == 2
    assert exporter._choose_semantic_palette_for_tile(rock_tile, palettes) == 3


def test_choose_semantic_palette_can_anchor_by_tile_role():
    palettes = [
        [(0, 0, 0), (102, 170, 238), (136, 170, 238)],
        [(0, 0, 0), (34, 102, 34), (68, 136, 34)],
        [(0, 0, 0), (34, 68, 204), (68, 136, 238)],
        [(0, 0, 0), (170, 136, 68), (238, 204, 136)],
    ]
    mixed_leaf_tile = [(170, 136, 68)] * 35 + [(68, 136, 34)] * 29
    role_counts = exporter.Counter(
        {
            "live_vegetation": 44,
            "rocks_floor_foreground": 20,
        }
    )

    assert exporter._choose_semantic_palette_for_tile(mixed_leaf_tile, palettes, role_counts) == 1


def test_semantic_palette_anchor_falls_back_when_distance_is_too_large():
    palettes = [
        [(0, 0, 0), (102, 170, 238), (136, 170, 238)],
        [(0, 0, 0), (34, 102, 34), (68, 136, 34)],
        [(0, 0, 0), (34, 68, 204), (68, 136, 238)],
        [(0, 0, 0), (170, 136, 68), (238, 204, 136)],
    ]
    water_tile = [(34, 68, 204)] * 64
    wrong_role_counts = exporter.Counter({"live_vegetation": 64})

    assert exporter._choose_semantic_palette_for_tile(water_tile, palettes, wrong_role_counts) == 2


def test_custom_map_word_decodes_to_sgdk_tile_attr_bits():
    word = exporter._pack_custom_map_word(tile_index=2261, palette_id=2, hflip=1, vflip=1)

    assert exporter._custom_map_tile_id(word) == 2261
    assert exporter._custom_map_palette_id(word) == 2
    assert exporter._custom_map_hflip(word) == 1
    assert exporter._custom_map_vflip(word) == 1

    sgdk_attr = exporter._custom_map_word_to_sgdk_attr(word, local_slot=37)
    assert sgdk_attr & 0x07FF == exporter.TILE_USER_INDEX + 37
    assert sgdk_attr & (1 << 11)
    assert sgdk_attr & (1 << 12)
    assert ((sgdk_attr >> 13) & 0x3) == 2


def test_live_vegetation_palette_keeps_vivid_green_anchor_ahead_of_mud():
    muddy_counts = exporter.Counter(
        {
            (68, 68, 34): 900,
            (102, 102, 68): 850,
            (34, 68, 34): 700,
            (68, 136, 34): 100,
        }
    )

    palette = exporter._palette_from_role_counts("live_vegetation", muddy_counts)

    assert palette[0] == exporter.BACKDROP_MD_RGB
    assert (136, 204, 68) in palette[1:5]
    assert (170, 238, 102) in palette[1:8]
    assert palette.index((136, 204, 68)) < palette.index((68, 68, 34))


def test_water_palette_keeps_bright_reflection_anchor_ahead_of_dark_blues():
    dark_counts = exporter.Counter(
        {
            (0, 34, 68): 1000,
            (0, 68, 136): 940,
            (34, 68, 204): 120,
            (102, 204, 238): 80,
        }
    )

    palette = exporter._palette_from_role_counts("water_and_reflections", dark_counts)

    assert (34, 102, 238) in palette[1:6]
    assert (102, 204, 238) in palette[1:8]
    assert palette.index((102, 204, 238)) < palette.index((0, 34, 68))

from camera.showdown_fight_camera import Fighter, compute_camera, layer_camera_x, water_line_extra


def test_default_dual_focus_matches_mugen_start_scroll():
    camera = compute_camera(
        Fighter(x=314, y=471),
        Fighter(x=454, y=471),
        current_x=224,
        current_y=256,
        smoothing_px=999,
    )

    assert camera.x == 224
    assert camera.y == 256
    assert camera.focus_x == 384
    assert camera.floor_anchor_world_y == 471


def test_horizontal_midpoint_clamps_to_stage_bounds():
    left_edge = compute_camera(
        Fighter(x=30, y=471),
        Fighter(x=170, y=471),
        current_x=224,
        current_y=256,
        smoothing_px=999,
    )
    right_edge = compute_camera(
        Fighter(x=620, y=471),
        Fighter(x=760, y=471),
        current_x=224,
        current_y=256,
        smoothing_px=999,
    )

    assert left_edge.x == 0
    assert right_edge.x == 448


def test_normal_jump_stays_inside_vertical_dead_zone():
    camera = compute_camera(
        Fighter(x=314, y=430),
        Fighter(x=454, y=471),
        current_x=224,
        current_y=256,
        smoothing_px=999,
    )

    assert camera.y == 256
    assert camera.vertical_state == "floor_locked"


def test_super_jump_activates_verticalfollow_without_losing_floor_contract_bounds():
    camera = compute_camera(
        Fighter(x=314, y=190),
        Fighter(x=454, y=471),
        current_x=224,
        current_y=256,
        smoothing_px=999,
    )

    assert camera.y == 165
    assert camera.vertical_state == "super_jump_follow"


def test_parallax_bands_align_at_default_camera_and_split_when_scrolling():
    assert layer_camera_x(224, 24) == 224
    assert layer_camera_x(224, 112) == 224
    assert layer_camera_x(224, 200) == 224

    assert layer_camera_x(448, 24) == 320
    assert layer_camera_x(448, 112) == 383
    assert layer_camera_x(448, 200) == 448


def test_water_line_scroll_distortion_gets_stronger_lower_in_reflection():
    upper = water_line_extra(448, 92)
    lower = water_line_extra(448, 168)

    assert upper > 0
    assert lower > upper

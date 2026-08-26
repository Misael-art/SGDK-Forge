from __future__ import annotations

from dataclasses import dataclass


VIEWPORT_W = 320
VIEWPORT_H = 224
CAMERA_DEFAULT_X = 224
CAMERA_DEFAULT_Y = 256
CAMERA_MAX_X = 448
CAMERA_MAX_Y = 256
MUGEN_ZOFFSET = 215
FLOOR_ANCHOR_WORLD_Y = CAMERA_DEFAULT_Y + MUGEN_ZOFFSET
VERTICAL_DEADZONE_PX = 100
VERTICALFOLLOW_NUM = 1
VERTICALFOLLOW_DEN = 2
PARALLAX_FAR_SCREEN_MAX_Y = 72
PARALLAX_MID_SCREEN_MAX_Y = 176
WATER_LINE_TOP = 88
WATER_LINE_BOTTOM = 176


@dataclass(frozen=True)
class Fighter:
    x: int
    y: int


@dataclass(frozen=True)
class CameraResult:
    x: int
    y: int
    focus_x: int
    focus_y: int
    floor_anchor_world_y: int
    vertical_state: str


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _approach(current: int, target: int, step: int) -> int:
    if step <= 0 or abs(target - current) <= step:
        return target
    if target > current:
        return current + step
    return current - step


def _scaled_from_default(camera_value: int, default_value: int, num: int, den: int, max_value: int) -> int:
    delta = camera_value - default_value
    return _clamp(default_value + ((delta * num) // den), 0, max_value)


def layer_camera_x(camera_x: int, screen_y: int) -> int:
    if screen_y < PARALLAX_FAR_SCREEN_MAX_Y:
        return _scaled_from_default(camera_x, CAMERA_DEFAULT_X, 43, 100, CAMERA_MAX_X)
    if screen_y < PARALLAX_MID_SCREEN_MAX_Y:
        return _scaled_from_default(camera_x, CAMERA_DEFAULT_X, 71, 100, CAMERA_MAX_X)
    return _clamp(camera_x, 0, CAMERA_MAX_X)


def water_line_extra(camera_x: int, screen_y: int) -> int:
    if screen_y < WATER_LINE_TOP or screen_y >= WATER_LINE_BOTTOM:
        return 0
    camera_delta = abs(camera_x - CAMERA_DEFAULT_X)
    depth = (screen_y - WATER_LINE_TOP) + 1
    return (camera_delta * depth) // ((WATER_LINE_BOTTOM - WATER_LINE_TOP) * 10)


def compute_camera(
    p1: Fighter,
    p2: Fighter,
    *,
    current_x: int = CAMERA_DEFAULT_X,
    current_y: int = CAMERA_DEFAULT_Y,
    smoothing_px: int = 6,
) -> CameraResult:
    focus_x = (p1.x + p2.x) // 2
    focus_y = min(p1.y, p2.y)

    target_x = _clamp(focus_x - (VIEWPORT_W // 2), 0, CAMERA_MAX_X)

    airborne_delta = max(0, FLOOR_ANCHOR_WORLD_Y - focus_y)
    if airborne_delta <= VERTICAL_DEADZONE_PX:
        target_y = CAMERA_DEFAULT_Y
        vertical_state = "floor_locked"
    else:
        followed_delta = ((airborne_delta - VERTICAL_DEADZONE_PX) * VERTICALFOLLOW_NUM + (VERTICALFOLLOW_DEN - 1)) // VERTICALFOLLOW_DEN
        target_y = CAMERA_DEFAULT_Y - followed_delta
        vertical_state = "super_jump_follow"

    target_y = _clamp(target_y, 0, CAMERA_MAX_Y)

    return CameraResult(
        x=_approach(current_x, target_x, smoothing_px),
        y=_approach(current_y, target_y, smoothing_px),
        focus_x=focus_x,
        focus_y=focus_y,
        floor_anchor_world_y=FLOOR_ANCHOR_WORLD_Y,
        vertical_state=vertical_state,
    )

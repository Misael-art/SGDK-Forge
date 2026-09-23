from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict
from collections import defaultdict


@dataclass(frozen=True)
class BgDef:
    id: int
    kind: str
    sprite_group: int | None
    sprite_index: int | None
    actionno: int | None
    mask: int
    start_x: int
    start_y: int
    delta_x: float
    delta_y: float
    tile_x: int
    tile_y: int


@dataclass(frozen=True)
class ActionFrame:
    group: int
    index: int
    offset_x: int
    offset_y: int
    time: int


@dataclass(frozen=True)
class StageDef:
    bgs: list[BgDef]
    actions: dict[int, list[ActionFrame]]
    zoffset: int
    camera_startx: int
    camera_starty: int
    camera_boundleft: int
    camera_boundright: int
    camera_boundhigh: int
    camera_boundlow: int
    verticalfollow: float


def _strip_comment(line: str) -> str:
    return line.split(";", 1)[0].strip()


def _parse_key_value(line: str) -> tuple[str, str] | None:
    if "=" not in line:
        return None
    key, value = line.split("=", 1)
    return key.strip().lower(), value.strip()


def _parse_int_pair(value: str, default: tuple[int, int]) -> tuple[int, int]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) < 2:
        return default
    return int(float(parts[0])), int(float(parts[1]))


def _parse_float_pair(value: str, default: tuple[float, float]) -> tuple[float, float]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) < 2:
        return default
    return float(parts[0]), float(parts[1])


def _flush_bg(bgs: list[BgDef], bg_id: int | None, acc: dict[str, str]) -> None:
    if bg_id is None:
        return

    kind = acc.get("type", "normal").strip().lower()
    spr = acc.get("spriteno")
    actionno = acc.get("actionno")
    mask = int(acc.get("mask", "0"))
    start_x, start_y = _parse_int_pair(acc.get("start", "0,0"), (0, 0))
    delta_x, delta_y = _parse_float_pair(acc.get("delta", "1,1"), (1.0, 1.0))
    tile_x, tile_y = _parse_int_pair(acc.get("tile", "0,0"), (0, 0))

    sprite_group: int | None = None
    sprite_index: int | None = None
    if spr:
        parts = [p.strip() for p in spr.split(",")]
        if len(parts) == 2:
            sprite_group = int(parts[0])
            sprite_index = int(parts[1])

    bgs.append(
        BgDef(
            id=int(bg_id),
            kind=kind,
            sprite_group=sprite_group,
            sprite_index=sprite_index,
            actionno=int(actionno) if actionno is not None else None,
            mask=mask,
            start_x=start_x,
            start_y=start_y,
            delta_x=delta_x,
            delta_y=delta_y,
            tile_x=tile_x,
            tile_y=tile_y,
        )
    )


def parse_stage_def(path: Path) -> StageDef:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()

    section: str | None = None
    current_bg_id: int | None = None
    bg_accum: dict[str, str] = {}
    stage_info: dict[str, str] = {}
    camera_info: dict[str, str] = {}

    bgs: list[BgDef] = []
    actions: DefaultDict[int, list[ActionFrame]] = defaultdict(list)

    for raw in lines:
        line = _strip_comment(raw)
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            if section and section.startswith("bg "):
                _flush_bg(bgs, current_bg_id, bg_accum)
            bg_accum = {}

            section = line[1:-1].strip().lower()
            if section.startswith("bg "):
                current_bg_id = int(section.split(" ", 1)[1])
            else:
                current_bg_id = None
            continue

        if section and section.startswith("begin action "):
            action_id = int(section.split(" ", 2)[2])
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                actions[action_id].append(
                    ActionFrame(
                        group=int(parts[0]),
                        index=int(parts[1]),
                        offset_x=int(parts[2]),
                        offset_y=int(parts[3]),
                        time=int(parts[4]),
                    )
                )
            continue

        parsed = _parse_key_value(line)
        if parsed and section and section.startswith("bg "):
            key, value = parsed
            bg_accum[key] = value
        elif parsed and section == "stageinfo":
            key, value = parsed
            stage_info[key] = value
        elif parsed and section == "camera":
            key, value = parsed
            camera_info[key] = value

    if section and section.startswith("bg "):
        _flush_bg(bgs, current_bg_id, bg_accum)

    return StageDef(
        bgs=bgs,
        actions=dict(actions),
        zoffset=int(stage_info.get("zoffset", "0")),
        camera_startx=int(float(camera_info.get("startx", "0"))),
        camera_starty=int(float(camera_info.get("starty", "0"))),
        camera_boundleft=int(float(camera_info.get("boundleft", "0"))),
        camera_boundright=int(float(camera_info.get("boundright", "0"))),
        camera_boundhigh=int(float(camera_info.get("boundhigh", "0"))),
        camera_boundlow=int(float(camera_info.get("boundlow", "0"))),
        verticalfollow=float(camera_info.get("verticalfollow", "0")),
    )

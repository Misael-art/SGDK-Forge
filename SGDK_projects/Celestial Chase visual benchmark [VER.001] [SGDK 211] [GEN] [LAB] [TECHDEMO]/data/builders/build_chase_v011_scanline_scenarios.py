#!/usr/bin/env python3
"""Build v011 scanline fixtures from the final ROM's FrameVDPSprite geometry."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parents[1]
ROM_PATH = PROJECT_ROOT / "out" / "rom.bin"
SYMBOL_PATH = PROJECT_ROOT / "out" / "symbol.txt"
LOG_DIR = PROJECT_ROOT / "out" / "logs"
SIMULATOR_PATH = (
    WORKSPACE_ROOT
    / "tools"
    / "sgdk_wrapper"
    / ".agent"
    / "scripts"
    / "vdp_scanline_simulator.py"
)

RIG_SINE = (
    0, 2, 4, 6, 7, 8, 9, 10,
    10, 10, 9, 8, 7, 6, 4, 2,
    0, -2, -4, -6, -7, -8, -9, -10,
    -10, -10, -9, -8, -7, -6, -4, -2,
)

# Runtime requests six logical frames. ResComp aliases the duplicated frames.
RIG_STATES = (
    (0, 0, 0),
    (0, 0, 1),
    (2, 2, 1),
    (2, 2, 3),
    (2, 2, 3),
    (2, 2, 1),
)


def load_simulator() -> Any:
    spec = importlib.util.spec_from_file_location("vdp_scanline_simulator", SIMULATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load canonical simulator: {SIMULATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_symbols() -> dict[str, int]:
    symbols: dict[str, int] = {}
    pattern = re.compile(r"([0-9a-fA-F]{8})\s+\w\s+(\S+)$")
    for line in SYMBOL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.match(line)
        if match:
            symbols[match.group(2)] = int(match.group(1), 16)
    return symbols


def add_frame_parts(
    output: list[dict[str, Any]],
    rom: bytes,
    symbols: dict[str, int],
    symbol: str,
    actor_x: int,
    actor_y: int,
    actor_name: str,
) -> None:
    address = symbols.get(symbol)
    if address is None:
        raise RuntimeError(f"frame symbol missing from final ROM: {symbol}")

    sprite_count = rom[address] & 0x7F
    for index in range(sprite_count):
        offset = address + 10 + (index * 6)
        offset_y = rom[offset]
        size = rom[offset + 2]
        offset_x = rom[offset + 3]
        width = (((size >> 2) & 3) + 1) * 8
        height = ((size & 3) + 1) * 8
        output.append(
            {
                "name": f"{actor_name}.{index}",
                "x": actor_x + offset_x,
                "y": actor_y + offset_y,
                "w": width,
                "h": height,
                "sprite_links": 1,
                "source_frame": symbol,
            }
        )


def add_clouds(parts: list[dict[str, Any]], rom: bytes, symbols: dict[str, int]) -> None:
    symbol = "spr_chase_cloud_v009_animation0_frame0"
    add_frame_parts(parts, rom, symbols, symbol, 272, 38, "cloud_near")
    add_frame_parts(parts, rom, symbols, symbol, -52, 18, "cloud_far")


def add_player(
    parts: list[dict[str, Any]],
    rom: bytes,
    symbols: dict[str, int],
    hero_frame: int,
    ghosts_visible: bool,
) -> None:
    add_frame_parts(
        parts,
        rom,
        symbols,
        f"spr_chase_hero_run_v009_animation0_frame{hero_frame}",
        128,
        136,
        "hero",
    )
    add_frame_parts(
        parts,
        rom,
        symbols,
        "spr_chase_contact_shadow_v011_animation0_frame2",
        152,
        208,
        "hero_shadow",
    )
    if ghosts_visible:
        ghost_symbol = "spr_chase_hero_ghost_v009_animation0_frame0"
        add_frame_parts(parts, rom, symbols, ghost_symbol, 126, 138, "ghost_near")
        add_frame_parts(parts, rom, symbols, ghost_symbol, 123, 140, "ghost_far")


def add_pursuer(
    parts: list[dict[str, Any]],
    rom: bytes,
    symbols: dict[str, int],
    phase: int,
    pressure: int,
    rig_state: int,
    far_claw_visible: bool,
) -> None:
    torso_frame, head_frame, claw_frame = RIG_STATES[rig_state]
    bob = RIG_SINE[phase] >> 2
    head_swing = RIG_SINE[(phase + 6) & 31] >> 2
    reach = RIG_SINE[(phase + 10) & 31]
    root_x = 112
    root_y = 44 + (pressure // 24) + bob

    add_frame_parts(
        parts,
        rom,
        symbols,
        f"spr_chase_pursuer_torso_v011_animation0_frame{torso_frame}",
        root_x,
        root_y,
        "pursuer_torso",
    )
    add_frame_parts(
        parts,
        rom,
        symbols,
        f"spr_chase_pursuer_head_v009_animation0_frame{head_frame}",
        root_x + 8 + head_swing,
        root_y - 18 - (bob >> 1),
        "pursuer_head",
    )
    add_frame_parts(
        parts,
        rom,
        symbols,
        f"spr_chase_pursuer_claw_v009_animation0_frame{claw_frame}",
        root_x + 54 + reach,
        root_y + 34 - bob,
        "pursuer_claw_near",
    )
    add_frame_parts(
        parts,
        rom,
        symbols,
        "spr_chase_contact_shadow_v011_animation0_frame2",
        root_x + 78 + reach,
        root_y + 92,
        "pursuer_shadow_near",
    )
    if far_claw_visible:
        add_frame_parts(
            parts,
            rom,
            symbols,
            f"spr_chase_pursuer_claw_v009_animation0_frame{claw_frame}",
            root_x - 34 - (reach >> 1),
            root_y + 24 + (bob >> 1),
            "pursuer_claw_far",
        )
        add_frame_parts(
            parts,
            rom,
            symbols,
            "spr_chase_contact_shadow_v011_animation0_frame2",
            root_x - 10 - (reach >> 1),
            root_y + 82,
            "pursuer_shadow_far",
        )


def add_traffic_fixture(parts: list[dict[str, Any]], rom: bytes, symbols: dict[str, int]) -> None:
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_obstacle_boulder_v011_animation0_frame3",
        80, 155, "boulder_near",
    )
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_contact_shadow_v011_animation0_frame2",
        104, 197, "boulder_shadow",
    )
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_obstacle_brand_v011_animation0_frame2",
        176, 105, "brand_mid",
    )
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_contact_shadow_v011_animation0_frame2",
        200, 147, "brand_shadow",
    )
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_energy_star_v009_animation0_frame1",
        144, 132, "energy_pickup",
    )


def add_impact_fixture(
    parts: list[dict[str, Any]],
    rom: bytes,
    symbols: dict[str, int],
    fx_frame: int,
) -> None:
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_obstacle_brand_v011_animation0_frame3",
        176, 155, "brand_other_lane",
    )
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_contact_shadow_v011_animation0_frame2",
        200, 197, "brand_shadow",
    )
    add_frame_parts(
        parts, rom, symbols,
        "spr_chase_energy_star_v009_animation0_frame1",
        144, 132, "energy_pickup",
    )
    add_frame_parts(
        parts, rom, symbols,
        f"spr_chase_pursuer_dust_impact_animation0_frame{fx_frame}",
        128, 162, "impact_dust",
    )


def add_pulse_fixture(
    parts: list[dict[str, Any]],
    rom: bytes,
    symbols: dict[str, int],
    fx_frame: int,
) -> None:
    add_frame_parts(
        parts, rom, symbols,
        f"spr_chase_pulse_impact_v009_animation0_frame{fx_frame}",
        128, 156, "pulse_impact",
    )


def scenario_candidates(mode: str, rom: bytes, symbols: dict[str, int]) -> Iterable[tuple[dict[str, int], list[dict[str, Any]]]]:
    far_claw_visible = mode != "pulse"
    pressures = (0, 24, 48, 72, 88) if far_claw_visible else (0, 24, 48, 72, 96)
    fx_frames: Iterable[int | None]
    if mode == "impact":
        fx_frames = range(5)
    elif mode == "pulse":
        fx_frames = range(6)
    else:
        fx_frames = (None,)

    for phase in range(32):
        for pressure in pressures:
            for rig_state in range(6):
                for hero_frame in range(4):
                    for fx_frame in fx_frames:
                        parts: list[dict[str, Any]] = []
                        add_clouds(parts, rom, symbols)
                        add_pursuer(
                            parts,
                            rom,
                            symbols,
                            phase,
                            pressure,
                            rig_state,
                            far_claw_visible,
                        )
                        add_player(parts, rom, symbols, hero_frame, ghosts_visible=True)
                        if mode == "traffic":
                            add_traffic_fixture(parts, rom, symbols)
                        elif mode == "impact" and fx_frame is not None:
                            add_impact_fixture(parts, rom, symbols, fx_frame)
                        elif mode == "pulse" and fx_frame is not None:
                            add_pulse_fixture(parts, rom, symbols, fx_frame)
                        yield (
                            {
                                "phase": phase,
                                "pressure": pressure,
                                "rig_state": rig_state,
                                "hero_frame": hero_frame,
                                "fx_frame": -1 if fx_frame is None else fx_frame,
                            },
                            parts,
                        )


def build_scenario(mode: str, simulator: Any, rom: bytes, symbols: dict[str, int]) -> dict[str, Any]:
    best_key: tuple[int, int] | None = None
    best_fixture: dict[str, int] | None = None
    best_parts: list[dict[str, Any]] | None = None
    best_result: dict[str, Any] | None = None

    for fixture, parts in scenario_candidates(mode, rom, symbols):
        result = simulator.simulate({"sprites": parts})
        key = (int(result["max_sprites_per_scanline"]), int(result["total_sprite_links"]))
        if best_key is None or key > best_key:
            best_key = key
            best_fixture = fixture
            best_parts = parts
            best_result = result

    if best_fixture is None or best_parts is None or best_result is None:
        raise RuntimeError(f"no candidates generated for scenario: {mode}")

    input_path = LOG_DIR / f"sprite_scanline_{mode}_v011_input.json"
    report_path = LOG_DIR / f"sprite_scanline_{mode}.json"
    input_payload = {
        "schema_version": "1.0.0",
        "scenario": mode,
        "fixture": best_fixture,
        "sprites": best_parts,
    }
    best_result["scenario"] = mode
    best_result["fixture"] = best_fixture
    best_result["input_path"] = str(input_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    input_path.write_text(json.dumps(input_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(best_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return best_result


def main() -> int:
    if not ROM_PATH.is_file() or not SYMBOL_PATH.is_file():
        raise RuntimeError("build out/rom.bin and out/symbol.txt before scanline analysis")
    simulator = load_simulator()
    rom = ROM_PATH.read_bytes()
    symbols = load_symbols()
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    scenario_reports = [
        build_scenario(mode, simulator, rom, symbols)
        for mode in ("traffic", "impact", "pulse")
    ]
    max_scanline = max(int(report["max_sprites_per_scanline"]) for report in scenario_reports)
    blockers = [
        f"{report['scenario']}:{blocker}"
        for report in scenario_reports
        for blocker in report["blockers"]
    ]
    combined = {
        "schema_version": "1.0.0",
        "status": "ok" if not blockers else "error",
        "rom_sha256": hashlib.sha256(rom).hexdigest(),
        "method": "final_rom_frame_vdp_sprite_geometry_plus_canonical_scanline_simulator",
        "canonical_simulator": str(SIMULATOR_PATH.relative_to(WORKSPACE_ROOT)).replace("\\", "/"),
        "hardware_limit": 20,
        "preferred_operating_target": 18,
        "max_sprites_per_scanline": max_scanline,
        "headroom_to_hardware_limit": 20 - max_scanline,
        "scenarios": scenario_reports,
        "blockers": blockers,
        "notes": [
            "Each logical sprite is flattened from the final ROM's FrameVDPSprite geometry.",
            "The enumerator covers reachable rig frame states, 32 FK phases, pressure bands, hero frames and every impact/Pulse frame.",
            "Fixtures include contact shadows and conservative simultaneous traffic; fresh BlastEm runtime telemetry remains the final gate.",
        ],
    }
    output_path = LOG_DIR / "sprite_scanline_pressure_report.json"
    output_path.write_text(json.dumps(combined, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"v011 scanline report: max={max_scanline}/20 "
        f"headroom={combined['headroom_to_hardware_limit']} "
        f"status={combined['status']}"
    )
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())

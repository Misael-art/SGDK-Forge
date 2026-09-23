from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

RUNTIME_TOKENS = [
    "StagePlayer",
    "StageActor",
    "STAGE_WORLD_W",
    "stageUpdatePlayer",
    "stageUpdateCamera",
    "stageUpdateLineSentry",
    "stageUpdateBreakerCore",
    "stageUpdatePulse",
    "spr_bc_player_idle",
    "spr_bc_player_run",
    "spr_bc_player_jump",
    "spr_bc_player_shoot",
    "spr_bc_line_sentry_idle",
    "spr_bc_breaker_core_idle",
    "spr_bc_projectile_pulse",
    "img_bc_stage_bg",
    "img_bc_stage_fg",
]

APP_BOOTSTRAP_TOKENS = [
    "APP_SCENE_BOOTSTRAP_OFFSET",
    "APP_SCENE_BOOTSTRAP_SCHEMA",
    "APP_readSceneBootstrap",
    "SRAM_enableRO",
    "SBIS",
]

FORBIDDEN_TEMPLATE_TEXT = [
    "PLAYABLE TEMPLATE",
    "Edite src/scenes",
    "A/Y jump  B/Z run  X strike",
]


def main() -> int:
    app = (ROOT / "src/core/app.c").read_text(encoding="utf-8")
    scene_demo = (ROOT / "src/scenes/scene_demo.c").read_text(encoding="utf-8")
    scene_menu = (ROOT / "src/scenes/scene_menu.c").read_text(encoding="utf-8")
    failures: list[str] = []

    for token in RUNTIME_TOKENS:
        if token not in scene_demo:
            failures.append(f"scene_demo.c missing {token}")

    for token in APP_BOOTSTRAP_TOKENS:
        if token not in app:
            failures.append(f"app.c missing scene bootstrap support: {token}")

    for token in FORBIDDEN_TEMPLATE_TEXT:
        if token in scene_demo or token in scene_menu:
            failures.append(f"template text still present: {token}")

    if "BLUE_CIRCUIT" not in scene_menu:
        failures.append("scene_menu.c must present BLUE_CIRCUIT title flow")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: BLUE_CIRCUIT runtime contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

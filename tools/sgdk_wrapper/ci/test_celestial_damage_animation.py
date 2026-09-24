#!/usr/bin/env python3
"""Static regression guard for Celestial's promised damage animation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "SGDK_projects/Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]"
SOURCE = PROJECT / "src/scenes/race_scene.c"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    invulnerable = text.index("if (Player_isInvulnerable())")
    jumping = text.index("else if (Player_isJumping())", invulnerable)
    pulse = text.index("else if (Player_isPulseActive())", jumping)
    damage_anim = text.index("SPR_setAnim(player_sprite, ANIM_DAMAGE);", invulnerable, jumping)
    damage_frame = text.index("DAMAGE_FRAME_COUNT", damage_anim, jumping)
    assert invulnerable < damage_anim < damage_frame < jumping < pulse
    assert "SPR_setAnim(player_sprite, ANIM_RUN);" not in text[invulnerable:jumping]
    print("[PASS] Celestial damage overrides jump/pulse and uses ANIM_DAMAGE frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

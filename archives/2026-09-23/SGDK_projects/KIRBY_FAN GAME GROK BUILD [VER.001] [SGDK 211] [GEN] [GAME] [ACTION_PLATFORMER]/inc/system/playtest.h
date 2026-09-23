#ifndef SYSTEM_PLAYTEST_H
#define SYSTEM_PLAYTEST_H

#include <genesis.h>

/*
 * ROM-side scripted input playback.
 *
 * WHY IN THE ROM instead of driving the emulator with xdotool: the point of a
 * playtest gate is determinism. Emulator-side key injection depends on window
 * focus, X11 timing and the emulator's own polling, so the same script would
 * produce different frames on different runs and the gate would be flaky. A
 * table compiled into the ROM is frame-exact and version-controlled.
 *
 * The brief asks for "inputs gravados cobrindo 100% dos estados do jogador".
 * This module supplies the inputs; PLAYTEST_visited() records which states were
 * actually reached, so the gate checks COVERAGE achieved, not coverage intended.
 * Those are different claims and only the second one is worth anything.
 *
 * Activated by booting APP_SCENE_STAGE_PLAYTEST (scene id 5). The normal stage
 * (scene 4) is untouched and still reads the pad, so this cannot leak into
 * ordinary play. Scene 5 exists because the canonical bootstrap block carries
 * only a scene id and no flags field, and that block is written by shared
 * tooling this project may not modify.
 */

/* Player states the script must provoke. Bit positions are the contract with
 * tools/harness/gates.py -- do not renumber without updating the gate. */
#define PLAYTEST_STATE_IDLE     0x0001u
#define PLAYTEST_STATE_RUN      0x0002u
#define PLAYTEST_STATE_JUMP     0x0004u
#define PLAYTEST_STATE_FLOAT    0x0008u
#define PLAYTEST_STATE_INHALE   0x0010u
#define PLAYTEST_STATE_FACE_L   0x0020u
#define PLAYTEST_STATE_FACE_R   0x0040u
#define PLAYTEST_STATE_AIRBORNE 0x0080u
#define PLAYTEST_STATE_GROUNDED 0x0100u
#define PLAYTEST_STATE_SWALLOW  0x0200u   /* an enemy was actually swallowed */
#define PLAYTEST_STATE_ABILITY  0x0400u   /* a copy ability was actually granted */

#define PLAYTEST_STATE_KIRBY_HURT 0x0800u  /* Kirby actually took damage */
#define PLAYTEST_STATE_BOSS_HURT  0x1000u  /* the boss actually lost HP */
#define PLAYTEST_STATE_BOSS_DEAD  0x2000u  /* the boss reached DEFEATED */
#define PLAYTEST_STATE_ABILITY_USED 0x4000u /* an ability moveset actually FIRED,
                                             * not merely granted */

#define PLAYTEST_STATE_ALL       0x07FFu   /* stage script: player states only */
#define PLAYTEST_STATE_BOSS_ALL  0x3800u   /* boss script: the combat loop */

void PLAYTEST_begin(void);
void PLAYTEST_beginBoss(void);
void PLAYTEST_mark(u16 stateBits);
bool PLAYTEST_active(void);

/* Returns the buttons held this frame and fills *pressed with edges. */
u16 PLAYTEST_poll(u16* pressed);

/* Called by the scene each frame with what actually happened. */
void PLAYTEST_observe(u16 kirbyState, bool onGround, bool facingLeft,
                      bool swallowed, bool abilityGranted);

u16 PLAYTEST_visited(void);
u16 PLAYTEST_step(void);
bool PLAYTEST_finished(void);

#endif

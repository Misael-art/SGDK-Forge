#ifndef ENTITIES_BOSS_WHISPY_H
#define ENTITIES_BOSS_WHISPY_H

#include <genesis.h>

/*
 * Whispy Woods -- the stress test the contract was written around.
 *
 * doc/ARCHITECTURE.md section 5.1 budgets it at 58 of the 80 sprites/frame:
 *   trunk      BG_A tiles          0 sprites
 *   face       composed sprite     6
 *   4 branches x 7 segments       28
 *   apples     pool                8
 *   particles  pool               16
 *
 * The branches use forward kinematics with a fix16 sine table (F16_sin, degrees).
 * ZERO float: AGENTS.md forbids it and the 68000 has no FPU.
 *
 * Smoothness comes from INTERPOLATING the target angle, not from adding
 * segments. That distinction is the documented degradation lever: if the chain
 * costs too much, interpolate every 2 frames, then drop to 5 segments, then to
 * 3 branches -- and never cut the face animation.
 */

#define BOSS_BRANCH_COUNT 4
/*
 * LEVER 2 of the degradation ladder in doc/ARCHITECTURE.md section 5.1, spent
 * on 2026-08-06.
 *
 * The ladder, written in FASE 0 before the boss existed, reads: interpolate
 * every 2 frames -> 5 segments per branch -> 3 branches. Never cut the face
 * animation. Lever 1 was spent when the boss alone hit 87% CPU. Lever 2 is
 * spent here: adding R5's spotlight to the arena took cpu p99 to 106% with 289
 * frames over budget, and 7 segments per branch is the next cheapest thing to
 * give up.
 *
 * 7 -> 5 removes 8 sprites and about a quarter of the chain solve. The ladder
 * only works because it was written BEFORE the problem; a ladder invented at
 * this moment would just be rationalising whatever is easiest to cut.
 */
#define BOSS_SEGMENTS_PER_BRANCH 5
#define BOSS_SEGMENT_SPRITES (BOSS_BRANCH_COUNT * BOSS_SEGMENTS_PER_BRANCH)
#define BOSS_APPLE_POOL 8

#define BOSS_MAX_HP 6

typedef enum BossPhase {
    BOSS_IDLE = 0,
    BOSS_WINDUP = 1,     /* branches curl back */
    BOSS_WHIP = 2,       /* branches lash forward */
    BOSS_DROP_APPLES = 3,
    BOSS_HURT = 4,
    BOSS_DEFEATED = 5
} BossPhase;

typedef struct BossSegment {
    s16 x;
    s16 y;
} BossSegment;

typedef struct BossBranch {
    fix16 baseAngle;     /* degrees */
    fix16 targetAngle;
    fix16 curl;          /* per-segment angle delta, degrees */
    fix16 targetCurl;
    s16 originX;
    s16 originY;
    BossSegment seg[BOSS_SEGMENTS_PER_BRANCH];
} BossBranch;

typedef struct BossApple {
    fix16 x, y, vy;
    bool active;
} BossApple;

typedef struct Boss {
    BossPhase phase;
    u16 phaseTimer;
    u16 hp;
    u8 hitStop;
    u8 faceFrame;
    u8 solveToggle;   /* degradation lever 1: solve chains every other frame */
    s16 x, y;
    BossBranch branch[BOSS_BRANCH_COUNT];
    BossApple apple[BOSS_APPLE_POOL];
} Boss;

void BOSS_init(Boss* b, s16 x, s16 y);
void BOSS_update(Boss* b, fix16 kirbyX);
void BOSS_damage(Boss* b, u16 amount);
u16 BOSS_activeAppleCount(const Boss* b);

#endif

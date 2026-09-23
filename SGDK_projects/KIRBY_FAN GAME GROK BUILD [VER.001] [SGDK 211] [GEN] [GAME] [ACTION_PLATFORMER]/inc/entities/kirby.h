#ifndef ENTITIES_KIRBY_H
#define ENTITIES_KIRBY_H

#include <genesis.h>

/*
 * The player. All physics in fix16 — AGENTS.md forbids float/double.
 * Tunables come from doc/ARCHITECTURE.md section 7 and exist to be MEASURED
 * and argued with, not because they are right.
 */

typedef enum KirbyState {
    KIRBY_IDLE = 0,
    KIRBY_RUN = 1,
    KIRBY_JUMP = 2,
    KIRBY_FLOAT = 3,
    KIRBY_INHALE = 4
} KirbyState;

typedef struct Kirby {
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    KirbyState state;
    bool onGround;
    bool wasOnGround; /* previous frame — G6 land dust edge */
    bool facingLeft;
    bool justLanded;  /* TRUE for one frame after FALL/AIR -> ground */
    bool justDash;    /* TRUE when run speed crosses a punch threshold */
    u8 coyote;        /* frames of grace after leaving a ledge   (target 4) */
    u8 jumpBuffer;    /* frames a jump press stays queued        (target 5) */
    u8 animFrame;
    u8 animTimer;
    u8 hitStop;       /* frames frozen on impact                 (target 4) */
    bool inhaling;    /* B held: the vortex is active */
    u8 health;        /* hits remaining before defeat */
    u8 invuln;        /* i-frames after taking a hit */
    bool defeated;
    u8 ability;       /* CopyAbility currently held */
} Kirby;

/* Sprite quota from doc/ARCHITECTURE.md section 5: Kirby owns 8 of 80. */
#define KIRBY_SPRITE_QUOTA 8

void KIRBY_init(Kirby* k, fix16 x, fix16 y);
void KIRBY_update(Kirby* k, u16 held, u16 pressed);
void KIRBY_applyHitStop(Kirby* k, u8 frames);

/* Damage with knockback. Ignored while invulnerable or already defeated.
 * Returns TRUE if the hit actually landed. */
bool KIRBY_damage(Kirby* k, bool fromLeft);

#define KIRBY_MAX_HEALTH 6
#define KIRBY_INVULN_FRAMES 60
s16 KIRBY_screenX(const Kirby* k, s16 cameraX);
u16 KIRBY_animIndex(const Kirby* k);

#endif

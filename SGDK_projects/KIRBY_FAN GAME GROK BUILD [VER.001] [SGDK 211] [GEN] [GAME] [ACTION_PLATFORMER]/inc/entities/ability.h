#ifndef ENTITIES_ABILITY_H
#define ENTITIES_ABILITY_H

#include <genesis.h>
#include "entities/enemy.h"

/*
 * Copy ability movesets.
 *
 * Until now swallowing an enemy granted a hat that did nothing: the loop closed
 * mechanically but did not REWARD. This module is what makes inhaling worth
 * doing.
 *
 * Each ability is deliberately different in reach, duration and commitment, not
 * just in colour -- doc/art/AI_IMAGE_PROMPT_PACK.md R1-04 and
 * doc/17-audio-design.md 3.1 both require they be distinguishable by shape and
 * by sound. Here they must also be distinguishable by FEEL:
 *
 *   FIRE    short reach, continuous, hurts while held      -> pressure
 *   BEAM    medium reach, instant, no travel               -> precision
 *   CUTTER  long reach, travels and RETURNS                -> commitment
 *   STONE   no reach, Kirby becomes invulnerable and drops -> defence
 *   SWORD   short reach, one strong arc                    -> decisiveness
 *
 * The projectile pool is FIXED (AGENTS.md: no malloc) and comes out of the
 * 12-projectile quota in doc/ARCHITECTURE.md section 5.
 */

#define ABILITY_SHOT_POOL 12

typedef struct AbilityShot {
    fix16 x, y, vx;
    u16 life;          /* frames remaining */
    u8 frame;
    u8 kind;           /* CopyAbility that spawned it */
    bool returning;    /* CUTTER only */
    bool active;
} AbilityShot;

void ABILITY_init(void);

/* Fire the given ability. Returns TRUE if something was actually spawned
 * (i.e. the button did something the player can see). */
bool ABILITY_fire(u8 ability, fix16 kirbyX, fix16 kirbyY, bool facingLeft);

void ABILITY_update(fix16 kirbyX, fix16 kirbyY);

const AbilityShot* ABILITY_get(u16 index);
u16 ABILITY_activeCount(void);

/* Cooldown so holding the button does not spray. */
u16 ABILITY_cooldown(void);

#endif

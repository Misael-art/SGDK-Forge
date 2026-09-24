#ifndef ENTITIES_PARTICLE_H
#define ENTITIES_PARTICLE_H

#include <genesis.h>

/*
 * Fixed pool of dust / impact puffs. Work RAM only — no malloc (AGENTS.md).
 * Quota: up to PARTICLE_POOL_SIZE hardware sprites; degrade before enemies.
 * G6 (blind critic): land and dash feedback.
 */

/*
 * 2 slots: land spawns exactly two puffs. Ground scanline budget is the
 * binding constraint (20/line): Kirby+6 enemies+shots+FG already ~18.
 */
#define PARTICLE_POOL_SIZE 2u
/* Longer life so land dust survives into the proof screenshot frame. */
#define PARTICLE_LIFE 18u
#define PARTICLE_FRAMES 3u

typedef struct Particle {
    bool alive;
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    u8 life;
    u8 frame;
    u8 timer;
} Particle;

void PARTICLE_initPool(void);
void PARTICLE_updateAll(void);
void PARTICLE_spawnDust(fix16 x, fix16 y, bool faceLeft);
void PARTICLE_spawnLand(fix16 x, fix16 y);

/* Access for the scene renderer. */
const Particle* PARTICLE_get(u16 i);
u16 PARTICLE_aliveCount(void);

#endif

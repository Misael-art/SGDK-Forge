#ifndef GAMEPLAY_GOTHAM_PARTICLES_H
#define GAMEPLAY_GOTHAM_PARTICLES_H

#include <genesis.h>

#define MAX_PROJECTILES 24
#define MAX_PARTICLES   24

typedef enum ProjectileType {
    PROJ_NONE = 0,
    PROJ_PLAYER_VULCAN,
    PROJ_PLAYER_MISSILE,
    PROJ_BOSS_PLASMA,
    PROJ_ENEMY_LASER
} ProjectileType;

typedef enum ParticleType {
    PART_NONE = 0,
    PART_SPARK,
    PART_SHRAPNEL,
    PART_EXPLOSION,
    PART_SMOKE
} ParticleType;

typedef struct Projectile {
    ProjectileType type;
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    s16   targetX;
    s16   targetY;
    u8    lifetime;
    u8    damage;
    Sprite* sprite;
} Projectile;

typedef struct Particle {
    ParticleType type;
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    u8    animFrame;
    u8    lifetime;
    u8    maxLifetime;
    Sprite* sprite;
} Particle;

void GOTHAM_PARTICLES_init(void);
void GOTHAM_PARTICLES_update(void);
void GOTHAM_PARTICLES_clear(void);

bool GOTHAM_PARTICLES_spawnProjectile(ProjectileType type, fix16 x, fix16 y, fix16 vx, fix16 vy, s16 targetX, s16 targetY);
bool GOTHAM_PARTICLES_spawnParticle(ParticleType type, fix16 x, fix16 y, fix16 vx, fix16 vy, u8 lifetime);
void GOTHAM_PARTICLES_spawnExplosion(s16 x, s16 y, u8 count);

u16 GOTHAM_PARTICLES_getActiveCount(void);
Projectile* GOTHAM_PARTICLES_getProjectiles(void);

#endif

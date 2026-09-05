#include "gameplay/gotham_particles.h"
#include "resources.h"

static Projectile sProjectiles[MAX_PROJECTILES];
static Particle   sParticles[MAX_PARTICLES];
static u16        sActiveCount = 0;

void GOTHAM_PARTICLES_init(void)
{
    u16 i;
    for (i = 0; i < MAX_PROJECTILES; i++) {
        sProjectiles[i].type = PROJ_NONE;
        sProjectiles[i].sprite = SPR_addSprite(&spr_projectiles, -32, -32, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
        if (sProjectiles[i].sprite != NULL) {
            SPR_setVisibility(sProjectiles[i].sprite, HIDDEN);
            SPR_setAutoAnimation(sProjectiles[i].sprite, FALSE);
        }
    }
    for (i = 0; i < MAX_PARTICLES; i++) {
        sParticles[i].type = PART_NONE;
        sParticles[i].sprite = SPR_addSprite(&spr_particles, -32, -32, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
        if (sParticles[i].sprite != NULL) {
            SPR_setVisibility(sParticles[i].sprite, HIDDEN);
            SPR_setAutoAnimation(sParticles[i].sprite, FALSE);
        }
    }
    sActiveCount = 0;
}

void GOTHAM_PARTICLES_clear(void)
{
    u16 i;
    for (i = 0; i < MAX_PROJECTILES; i++) {
        sProjectiles[i].type = PROJ_NONE;
        if (sProjectiles[i].sprite != NULL) {
            SPR_setVisibility(sProjectiles[i].sprite, HIDDEN);
            SPR_setPosition(sProjectiles[i].sprite, -32, -32);
        }
    }
    for (i = 0; i < MAX_PARTICLES; i++) {
        sParticles[i].type = PART_NONE;
        if (sParticles[i].sprite != NULL) {
            SPR_setVisibility(sParticles[i].sprite, HIDDEN);
            SPR_setPosition(sParticles[i].sprite, -32, -32);
        }
    }
    sActiveCount = 0;
}

bool GOTHAM_PARTICLES_spawnProjectile(ProjectileType type, fix16 x, fix16 y, fix16 vx, fix16 vy, s16 targetX, s16 targetY)
{
    u16 i;
    for (i = 0; i < MAX_PROJECTILES; i++) {
        if (sProjectiles[i].type == PROJ_NONE) {
            sProjectiles[i].type = type;
            sProjectiles[i].x = x;
            sProjectiles[i].y = y;
            sProjectiles[i].vx = vx;
            sProjectiles[i].vy = vy;
            sProjectiles[i].targetX = targetX;
            sProjectiles[i].targetY = targetY;

            switch (type) {
                case PROJ_PLAYER_VULCAN:
                    sProjectiles[i].lifetime = 35;
                    sProjectiles[i].damage = 2;
                    if (sProjectiles[i].sprite) {
                        SPR_setPalette(sProjectiles[i].sprite, PAL2);
                        SPR_setFrame(sProjectiles[i].sprite, 0);
                    }
                    break;
                case PROJ_PLAYER_MISSILE:
                    sProjectiles[i].lifetime = 50;
                    sProjectiles[i].damage = 8;
                    if (sProjectiles[i].sprite) {
                        SPR_setPalette(sProjectiles[i].sprite, PAL2);
                        SPR_setFrame(sProjectiles[i].sprite, 1);
                    }
                    break;
                case PROJ_BOSS_PLASMA:
                    sProjectiles[i].lifetime = 70;
                    sProjectiles[i].damage = 15;
                    if (sProjectiles[i].sprite) {
                        SPR_setPalette(sProjectiles[i].sprite, PAL3);
                        SPR_setFrame(sProjectiles[i].sprite, 2);
                    }
                    break;
                case PROJ_ENEMY_LASER:
                default:
                    sProjectiles[i].lifetime = 55;
                    sProjectiles[i].damage = 5;
                    if (sProjectiles[i].sprite) {
                        SPR_setPalette(sProjectiles[i].sprite, PAL3);
                        SPR_setFrame(sProjectiles[i].sprite, 3);
                    }
                    break;
            }

            if (sProjectiles[i].sprite) {
                SPR_setPosition(sProjectiles[i].sprite, F16_toInt(x), F16_toInt(y));
                SPR_setVisibility(sProjectiles[i].sprite, VISIBLE);
            }
            return TRUE;
        }
    }
    return FALSE;
}

bool GOTHAM_PARTICLES_spawnParticle(ParticleType type, fix16 x, fix16 y, fix16 vx, fix16 vy, u8 lifetime)
{
    u16 i;
    for (i = 0; i < MAX_PARTICLES; i++) {
        if (sParticles[i].type == PART_NONE) {
            sParticles[i].type = type;
            sParticles[i].x = x;
            sParticles[i].y = y;
            sParticles[i].vx = vx;
            sParticles[i].vy = vy;
            sParticles[i].lifetime = lifetime;
            sParticles[i].maxLifetime = lifetime;
            sParticles[i].animFrame = 0;

            if (sParticles[i].sprite) {
                u8 frame = 0;
                switch (type) {
                    case PART_SPARK: frame = 0; break;
                    case PART_SHRAPNEL: frame = 1; break;
                    case PART_EXPLOSION: frame = 2; break;
                    case PART_SMOKE: frame = 3; break;
                    default: break;
                }
                SPR_setFrame(sParticles[i].sprite, frame);
                SPR_setPosition(sParticles[i].sprite, F16_toInt(x), F16_toInt(y));
                SPR_setVisibility(sParticles[i].sprite, VISIBLE);
            }
            return TRUE;
        }
    }
    return FALSE;
}

/* Cada particula nasce JA deslocada na direcao da propria velocidade, como se a
 * explosao ja tivesse EXPLOSION_BIRTH_SPREAD quadros de idade no primeiro quadro.
 *
 * PORQUE: nascendo todas no mesmo pixel, uma chamada de count 6 punha 18 sprites
 * de 16x16 na mesma scanline. Somado a geometria do boss, o pior quadro da
 * derrota media 23/20 sprites e 448/320 px — estouro dos DOIS limites do VDP em
 * 16 scanlines seguidas, ou seja dropout no climax da fatia jogavel.
 *
 * Espalhar o spawn no TEMPO nao resolve: foi medido em 24/20 e 464/320, pior que
 * o original, porque o pool de 24 satura igual e so muda de arranjo. O que
 * resolve e espalhar no ESPACO, e isso nao tira nada da tela — as 24 particulas,
 * o count 6 e o periodo de 8 quadros continuam iguais.
 *
 * Medido com r=6: 13/20 sprites e 288/320 px, 32 px de folga. */
#define EXPLOSION_BIRTH_SPREAD 6

void GOTHAM_PARTICLES_spawnExplosion(s16 x, s16 y, u8 count)
{
    u8 i;
    for (i = 0; i < count; i++) {
        s16 vx = (s16)((i * 13) % 7) - 3;
        s16 vy = (s16)((i * 17) % 7) - 3;
        s16 sy = vy + 1;
        GOTHAM_PARTICLES_spawnParticle(
            PART_EXPLOSION,
            FIX16(x + vx * EXPLOSION_BIRTH_SPREAD),
            FIX16(y + vy * EXPLOSION_BIRTH_SPREAD),
            FIX16(vx), FIX16(vy), 14);
        GOTHAM_PARTICLES_spawnParticle(
            PART_SPARK,
            FIX16(x + vx * 2 * EXPLOSION_BIRTH_SPREAD),
            FIX16(y + vy * 2 * EXPLOSION_BIRTH_SPREAD),
            FIX16(vx * 2), FIX16(vy * 2), 18);
        GOTHAM_PARTICLES_spawnParticle(
            PART_SHRAPNEL,
            FIX16(x + vx * EXPLOSION_BIRTH_SPREAD),
            FIX16(y + sy * EXPLOSION_BIRTH_SPREAD),
            FIX16(vx), FIX16(sy), 22);
    }
}

void GOTHAM_PARTICLES_update(void)
{
    u16 i;
    sActiveCount = 0;

    // Update projectiles
    for (i = 0; i < MAX_PROJECTILES; i++) {
        if (sProjectiles[i].type != PROJ_NONE) {
            sActiveCount++;
            sProjectiles[i].x += sProjectiles[i].vx;
            sProjectiles[i].y += sProjectiles[i].vy;

            // Micro-missile homing guidance towards target
            if (sProjectiles[i].type == PROJ_PLAYER_MISSILE && sProjectiles[i].lifetime > 10) {
                s16 curX = F16_toInt(sProjectiles[i].x);
                if (curX < sProjectiles[i].targetX) sProjectiles[i].vx += FIX16(0.2);
                else if (curX > sProjectiles[i].targetX) sProjectiles[i].vx -= FIX16(0.2);
            }

            sProjectiles[i].lifetime--;

            // Bounds check (Screen: 0..320, 0..224)
            {
                s16 sx = F16_toInt(sProjectiles[i].x);
                s16 sy = F16_toInt(sProjectiles[i].y);
                if (sProjectiles[i].lifetime == 0 || sx < -16 || sx > 328 || sy < -16 || sy > 230) {
                    sProjectiles[i].type = PROJ_NONE;
                    if (sProjectiles[i].sprite) {
                        SPR_setVisibility(sProjectiles[i].sprite, HIDDEN);
                        SPR_setPosition(sProjectiles[i].sprite, -32, -32);
                    }
                } else if (sProjectiles[i].sprite) {
                    SPR_setPosition(sProjectiles[i].sprite, sx, sy);
                }
            }
        }
    }

    // Update particles
    for (i = 0; i < MAX_PARTICLES; i++) {
        if (sParticles[i].type != PART_NONE) {
            sActiveCount++;
            sParticles[i].x += sParticles[i].vx;
            sParticles[i].y += sParticles[i].vy;
            sParticles[i].lifetime--;

            if (sParticles[i].lifetime == 0) {
                sParticles[i].type = PART_NONE;
                if (sParticles[i].sprite) {
                    SPR_setVisibility(sParticles[i].sprite, HIDDEN);
                    SPR_setPosition(sParticles[i].sprite, -32, -32);
                }
            } else if (sParticles[i].sprite) {
                s16 sx = F16_toInt(sParticles[i].x);
                s16 sy = F16_toInt(sParticles[i].y);
                SPR_setPosition(sParticles[i].sprite, sx, sy);
            }
        }
    }
}

u16 GOTHAM_PARTICLES_getActiveCount(void)
{
    return sActiveCount;
}

Projectile* GOTHAM_PARTICLES_getProjectiles(void)
{
    return sProjectiles;
}

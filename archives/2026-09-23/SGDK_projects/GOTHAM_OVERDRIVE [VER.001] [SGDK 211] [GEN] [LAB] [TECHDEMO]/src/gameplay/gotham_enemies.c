#include "gameplay/gotham_enemies.h"
#include "gameplay/gotham_particles.h"
#include "resources.h"
#include "system/audio.h"

static GothamDrone sDrones[MAX_DRONES];
static u16 sSpawnTimer = 0;

void GOTHAM_ENEMIES_init(void)
{
    u16 i;
    for (i = 0; i < MAX_DRONES; i++) {
        sDrones[i].active = FALSE;
        sDrones[i].sprite = SPR_addSprite(&spr_drone, -32, -32, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
        if (sDrones[i].sprite) {
            SPR_setVisibility(sDrones[i].sprite, HIDDEN);
            SPR_setAutoAnimation(sDrones[i].sprite, FALSE);
        }
    }
    sSpawnTimer = 60;
}

void GOTHAM_ENEMIES_reset(void)
{
    u16 i;
    for (i = 0; i < MAX_DRONES; i++) {
        sDrones[i].active = FALSE;
        if (sDrones[i].sprite) {
            SPR_setVisibility(sDrones[i].sprite, HIDDEN);
            SPR_setPosition(sDrones[i].sprite, -32, -32);
        }
    }
    sSpawnTimer = 60;
}

void GOTHAM_ENEMIES_update(GothamRasterFx* rasterFx, s16 playerX, s16 playerY)
{
    u16 i;
    u16 j;
    Projectile* projs;

    sSpawnTimer++;
    // Spawn wave every 180 frames (3 seconds)
    if (sSpawnTimer >= 180) {
        sSpawnTimer = 0;
        for (i = 0; i < 2; i++) {
            for (j = 0; j < MAX_DRONES; j++) {
                if (!sDrones[j].active) {
                    sDrones[j].active = TRUE;
                    sDrones[j].x = FIX16(i == 0 ? 30 : 260);
                    sDrones[j].y = FIX16(30);
                    sDrones[j].vx = (i == 0) ? FIX16(1.5) : FIX16(-1.5);
                    sDrones[j].vy = FIX16(0.8);
                    sDrones[j].health = 12;
                    sDrones[j].fireCooldown = 30 + (j * 15);
                    sDrones[j].swoopPhase = (u8)(j * 40);
                    if (sDrones[j].sprite) {
                        SPR_setPosition(sDrones[j].sprite, F16_toInt(sDrones[j].x), F16_toInt(sDrones[j].y));
                        SPR_setVisibility(sDrones[j].sprite, VISIBLE);
                    }
                    break;
                }
            }
        }
    }

    projs = GOTHAM_PARTICLES_getProjectiles();

    for (i = 0; i < MAX_DRONES; i++) {
        if (sDrones[i].active) {
            sDrones[i].swoopPhase += 3;
            sDrones[i].x += sDrones[i].vx + (sinFix16(sDrones[i].swoopPhase << 2) >> 13);
            sDrones[i].y += sDrones[i].vy;

            // Attack cooldown
            if (sDrones[i].fireCooldown > 0) {
                sDrones[i].fireCooldown--;
            } else {
                s16 dx = F16_toInt(sDrones[i].x);
                s16 dy = F16_toInt(sDrones[i].y);
                if (dy > 40 && dy < 160) {
                    GOTHAM_PARTICLES_spawnProjectile(PROJ_ENEMY_LASER, sDrones[i].x + FIX16(12), sDrones[i].y + FIX16(12), 0, FIX16(3.5), playerX, playerY);
                    sDrones[i].fireCooldown = 50;
                }
            }

            // Check collision against player projectiles
            {
                s16 dx = F16_toInt(sDrones[i].x);
                s16 dy = F16_toInt(sDrones[i].y);

                for (j = 0; j < MAX_PROJECTILES; j++) {
                    if (projs[j].type == PROJ_PLAYER_VULCAN || projs[j].type == PROJ_PLAYER_MISSILE) {
                        s16 px = F16_toInt(projs[j].x);
                        s16 py = F16_toInt(projs[j].y);
                        if (px >= dx && px <= dx + 24 && py >= dy && py <= dy + 16) {
                            sDrones[i].health -= projs[j].damage;
                            GOTHAM_PARTICLES_spawnParticle(PART_SPARK, projs[j].x, projs[j].y, 0, FIX16(-1), 6);
                            projs[j].type = PROJ_NONE;
                            if (projs[j].sprite) {
                                SPR_setVisibility(projs[j].sprite, HIDDEN);
                                SPR_setPosition(projs[j].sprite, -32, -32);
                            }

                            if (sDrones[i].health <= 0) {
                                sDrones[i].active = FALSE;
                                GOTHAM_PARTICLES_spawnExplosion(dx + 12, dy + 8, 4);
                                GOTHAM_RASTER_triggerShake(rasterFx, 2, 4);
                                AUDIO_playCue(AUDIO_CUE_STRIKE);
                                if (sDrones[i].sprite) {
                                    SPR_setVisibility(sDrones[i].sprite, HIDDEN);
                                    SPR_setPosition(sDrones[i].sprite, -32, -32);
                                }
                                break;
                            }
                        }
                    }
                }

                // Boundary check
                if (sDrones[i].active) {
                    if (dx < -32 || dx > 336 || dy > 220) {
                        sDrones[i].active = FALSE;
                        if (sDrones[i].sprite) {
                            SPR_setVisibility(sDrones[i].sprite, HIDDEN);
                            SPR_setPosition(sDrones[i].sprite, -32, -32);
                        }
                    } else if (sDrones[i].sprite) {
                        SPR_setPosition(sDrones[i].sprite, dx, dy);
                        SPR_setFrame(sDrones[i].sprite, (rasterFx->frameCount >> 2) & 1);
                    }
                }
            }
        }
    }
}

u16 GOTHAM_ENEMIES_getActiveCount(void)
{
    u16 count = 0;
    u16 i;
    for (i = 0; i < MAX_DRONES; i++) {
        if (sDrones[i].active) count++;
    }
    return count;
}

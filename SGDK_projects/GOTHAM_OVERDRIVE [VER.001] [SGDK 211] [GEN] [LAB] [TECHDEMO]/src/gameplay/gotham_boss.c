#include "gameplay/gotham_boss.h"
#include "gameplay/gotham_particles.h"
#include "resources.h"
#include "system/audio.h"

#define BOSS_START_X 128
#define BOSS_START_Y 40
#define BOSS_COMBAT_Y 72

static GothamBoss sBoss;

void GOTHAM_BOSS_init(void)
{
    sBoss.x = FIX16(BOSS_START_X);
    sBoss.y = FIX16(BOSS_START_Y);
    sBoss.vx = 0;
    sBoss.vy = 0;
    sBoss.health = 200;
    sBoss.maxHealth = 200;
    sBoss.state = BOSS_STATE_INTRO;
    sBoss.stateTimer = 0;
    sBoss.attackCooldown = 40;
    sBoss.turretAngleFrame = 0;
    sBoss.treadAnimFrame = 0;
    sBoss.flashTimer = 0;
    sBoss.defeatTimer = 0;
    sBoss.missilePodOpen = FALSE;
    sBoss.active = TRUE;

    // Allocate 5 modular sprites
    sBoss.sprChassis = SPR_addSprite(&spr_boss_chassis, BOSS_START_X, BOSS_START_Y, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
    sBoss.sprTurret = SPR_addSprite(&spr_boss_turret, BOSS_START_X + 16, BOSS_START_Y + 8, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
    sBoss.sprLeftTread = SPR_addSprite(&spr_boss_tread_left, BOSS_START_X - 4, BOSS_START_Y + 32, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
    sBoss.sprRightTread = SPR_addSprite(&spr_boss_tread_right, BOSS_START_X + 36, BOSS_START_Y + 32, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
    sBoss.sprMissilePod = SPR_addSprite(&spr_boss_missile_pod, BOSS_START_X + 38, BOSS_START_Y - 4, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));

    if (sBoss.sprChassis) SPR_setAutoAnimation(sBoss.sprChassis, FALSE);
    if (sBoss.sprTurret) SPR_setAutoAnimation(sBoss.sprTurret, FALSE);
    if (sBoss.sprLeftTread) SPR_setAutoAnimation(sBoss.sprLeftTread, FALSE);
    if (sBoss.sprRightTread) SPR_setAutoAnimation(sBoss.sprRightTread, FALSE);
    if (sBoss.sprMissilePod) SPR_setAutoAnimation(sBoss.sprMissilePod, FALSE);
}

void GOTHAM_BOSS_reset(void)
{
    sBoss.x = FIX16(BOSS_START_X);
    sBoss.y = FIX16(BOSS_START_Y);
    sBoss.vx = 0;
    sBoss.vy = 0;
    sBoss.health = 200;
    sBoss.state = BOSS_STATE_INTRO;
    sBoss.stateTimer = 0;
    sBoss.attackCooldown = 40;
    sBoss.turretAngleFrame = 0;
    sBoss.treadAnimFrame = 0;
    sBoss.flashTimer = 0;
    sBoss.defeatTimer = 0;
    sBoss.missilePodOpen = FALSE;
    sBoss.active = TRUE;

    if (sBoss.sprChassis) SPR_setVisibility(sBoss.sprChassis, VISIBLE);
    if (sBoss.sprTurret) SPR_setVisibility(sBoss.sprTurret, VISIBLE);
    if (sBoss.sprLeftTread) SPR_setVisibility(sBoss.sprLeftTread, VISIBLE);
    if (sBoss.sprRightTread) SPR_setVisibility(sBoss.sprRightTread, VISIBLE);
    if (sBoss.sprMissilePod) SPR_setVisibility(sBoss.sprMissilePod, VISIBLE);
}

void GOTHAM_BOSS_damage(s16 amount, GothamRasterFx* rasterFx)
{
    if (sBoss.state == BOSS_STATE_DEFEATED || !sBoss.active) return;

    sBoss.health -= amount;
    sBoss.flashTimer = 4;
    GOTHAM_RASTER_triggerShake(rasterFx, 4, 6);

    if (sBoss.health <= 0) {
        sBoss.health = 0;
        sBoss.state = BOSS_STATE_DEFEATED;
        sBoss.stateTimer = 0;
        GOTHAM_RASTER_triggerShake(rasterFx, 12, 45);
        GOTHAM_RASTER_triggerFlash(rasterFx, 8);
        AUDIO_playCue(AUDIO_CUE_STRIKE);
    }
}

void GOTHAM_BOSS_update(GothamRasterFx* rasterFx, s16 playerX, s16 playerY)
{
    s16 bx;
    s16 by;
    s16 dx;
    Projectile* projs;
    u16 i;

    if (!sBoss.active) return;

    sBoss.stateTimer++;
    if (sBoss.flashTimer > 0) sBoss.flashTimer--;
    if (sBoss.attackCooldown > 0) sBoss.attackCooldown--;

    bx = F16_toInt(sBoss.x);
    by = F16_toInt(sBoss.y);

    // Tread animation
    if ((rasterFx->frameCount & 3) == 0) {
        sBoss.treadAnimFrame = (u8)((sBoss.treadAnimFrame + 1) & 3);
    }

    // Aim turret at player
    dx = playerX - (bx + 24);
    if (dx < -40) sBoss.turretAngleFrame = 3;      // Hard left
    else if (dx < -15) sBoss.turretAngleFrame = 2; // Mid left
    else if (dx < 0) sBoss.turretAngleFrame = 1;   // Soft left
    else if (dx > 40) sBoss.turretAngleFrame = 7;  // Hard right
    else if (dx > 15) sBoss.turretAngleFrame = 6;  // Mid right
    else if (dx > 0) sBoss.turretAngleFrame = 5;   // Soft right
    else sBoss.turretAngleFrame = 0;               // Center

    // Boss State Machine
    switch (sBoss.state) {
        case BOSS_STATE_INTRO:
            if (by < BOSS_COMBAT_Y) {
                sBoss.y += FIX16(0.5);
            } else {
                sBoss.state = BOSS_STATE_STRAFE_CANNON;
                sBoss.stateTimer = 0;
                sBoss.vx = FIX16(1.2);
            }
            break;

        case BOSS_STATE_STRAFE_CANNON:
            sBoss.x += sBoss.vx;
            if (bx > 190) sBoss.vx = -FIX16(1.5);
            else if (bx < 60) sBoss.vx = FIX16(1.5);

            // Fire Heavy Plasma Cannon
            if (sBoss.attackCooldown == 0) {
                GOTHAM_PARTICLES_spawnProjectile(PROJ_BOSS_PLASMA, FIX16(bx + 24), FIX16(by + 28), (sBoss.vx >> 1), FIX16(3.5), playerX, playerY);
                sBoss.attackCooldown = 35;
                GOTHAM_RASTER_triggerShake(rasterFx, 3, 8);
                AUDIO_playCue(AUDIO_CUE_STRIKE);
            }

            if (sBoss.stateTimer > 200) {
                sBoss.state = (sBoss.health < 80) ? BOSS_STATE_OVERHEAT_RAGE : BOSS_STATE_MISSILE_BARRAGE;
                sBoss.stateTimer = 0;
                sBoss.attackCooldown = 15;
            }
            break;

        case BOSS_STATE_MISSILE_BARRAGE:
            sBoss.missilePodOpen = TRUE;
            // Launch cluster missiles
            if (sBoss.attackCooldown == 0 && sBoss.stateTimer < 100) {
                GOTHAM_PARTICLES_spawnProjectile(PROJ_ENEMY_LASER, FIX16(bx + 44), FIX16(by + 4), FIX16(-1.5), FIX16(2.5), playerX, playerY);
                GOTHAM_PARTICLES_spawnProjectile(PROJ_ENEMY_LASER, FIX16(bx + 48), FIX16(by + 4), FIX16(1.5), FIX16(2.5), playerX, playerY);
                sBoss.attackCooldown = 18;
                GOTHAM_PARTICLES_spawnParticle(PART_SMOKE, FIX16(bx + 46), FIX16(by + 8), 0, FIX16(-1.0), 14);
                AUDIO_playCue(AUDIO_CUE_LAND);
            }

            if (sBoss.stateTimer > 120) {
                sBoss.missilePodOpen = FALSE;
                sBoss.state = BOSS_STATE_RAM_CHARGE;
                sBoss.stateTimer = 0;
            }
            break;

        case BOSS_STATE_RAM_CHARGE:
            if (sBoss.stateTimer < 40) {
                // Warning rev up
                GOTHAM_PARTICLES_spawnParticle(PART_SPARK, FIX16(bx + 16), FIX16(by + 40), FIX16(-1), FIX16(1), 8);
                GOTHAM_PARTICLES_spawnParticle(PART_SPARK, FIX16(bx + 48), FIX16(by + 40), FIX16(1), FIX16(1), 8);
            } else if (sBoss.stateTimer < 90) {
                // Charge forward
                sBoss.y += FIX16(1.8);
                GOTHAM_RASTER_triggerShake(rasterFx, 5, 4);
            } else if (sBoss.stateTimer < 140) {
                // Retreat back
                sBoss.y -= FIX16(1.4);
            } else {
                sBoss.y = FIX16(BOSS_COMBAT_Y);
                sBoss.state = BOSS_STATE_STRAFE_CANNON;
                sBoss.stateTimer = 0;
                sBoss.attackCooldown = 30;
            }
            break;

        case BOSS_STATE_OVERHEAT_RAGE:
            sBoss.missilePodOpen = TRUE;
            sBoss.x += sBoss.vx * 2;
            if (bx > 200) sBoss.vx = -FIX16(1.8);
            else if (bx < 50) sBoss.vx = FIX16(1.8);

            // Emit toxic smoke and sparks from damaged core
            if ((rasterFx->frameCount & 7) == 0) {
                GOTHAM_PARTICLES_spawnParticle(PART_SMOKE, FIX16(bx + 32), FIX16(by + 20), 0, FIX16(-1.0), 16);
                GOTHAM_PARTICLES_spawnParticle(PART_SPARK, FIX16(bx + 28), FIX16(by + 16), FIX16(-1), FIX16(-1), 10);
            }

            if (sBoss.attackCooldown == 0) {
                GOTHAM_PARTICLES_spawnProjectile(PROJ_BOSS_PLASMA, FIX16(bx + 24), FIX16(by + 28), 0, FIX16(4.0), playerX, playerY);
                GOTHAM_PARTICLES_spawnProjectile(PROJ_ENEMY_LASER, FIX16(bx + 44), FIX16(by + 4), FIX16(2.0), FIX16(3.0), playerX, playerY);
                sBoss.attackCooldown = 22;
            }

            if (sBoss.stateTimer > 250) {
                sBoss.missilePodOpen = FALSE;
                sBoss.state = BOSS_STATE_RAM_CHARGE;
                sBoss.stateTimer = 0;
            }
            break;

        case BOSS_STATE_DEFEATED:
            sBoss.defeatTimer++;
            sBoss.y -= FIX16(0.2); // Slowly drift back into distance
            if ((sBoss.defeatTimer & 7) == 0) {
                s16 rx = bx + (sBoss.defeatTimer % 50);
                s16 ry = by + (sBoss.defeatTimer % 30);
                GOTHAM_PARTICLES_spawnExplosion(rx, ry, 6);
                GOTHAM_RASTER_triggerShake(rasterFx, 6, 8);
            }
            if (sBoss.defeatTimer > 180) {
                sBoss.active = FALSE;
                if (sBoss.sprChassis) SPR_setVisibility(sBoss.sprChassis, HIDDEN);
                if (sBoss.sprTurret) SPR_setVisibility(sBoss.sprTurret, HIDDEN);
                if (sBoss.sprLeftTread) SPR_setVisibility(sBoss.sprLeftTread, HIDDEN);
                if (sBoss.sprRightTread) SPR_setVisibility(sBoss.sprRightTread, HIDDEN);
                if (sBoss.sprMissilePod) SPR_setVisibility(sBoss.sprMissilePod, HIDDEN);
                return;
            }
            break;
    }

    // Check collision against player projectiles
    projs = GOTHAM_PARTICLES_getProjectiles();
    for (i = 0; i < MAX_PROJECTILES; i++) {
        if (projs[i].type == PROJ_PLAYER_VULCAN || projs[i].type == PROJ_PLAYER_MISSILE) {
            s16 px = F16_toInt(projs[i].x);
            s16 py = F16_toInt(projs[i].y);
            // Bounding box for boss hull (bx to bx + 64, by to by + 48)
            if (px >= bx && px <= bx + 64 && py >= by && py <= by + 48) {
                GOTHAM_BOSS_damage(projs[i].damage, rasterFx);
                GOTHAM_PARTICLES_spawnParticle(PART_SPARK, projs[i].x, projs[i].y, FIX16(0), FIX16(-1), 8);
                // Consume projectile
                projs[i].type = PROJ_NONE;
                if (projs[i].sprite) {
                    SPR_setVisibility(projs[i].sprite, HIDDEN);
                    SPR_setPosition(projs[i].sprite, -32, -32);
                }
            }
        }
    }

    // Update Modular Hardware Sprites Positions
    bx = F16_toInt(sBoss.x);
    by = F16_toInt(sBoss.y);

    if (sBoss.sprChassis) {
        SPR_setPosition(sBoss.sprChassis, bx, by);
    }
    if (sBoss.sprTurret) {
        SPR_setPosition(sBoss.sprTurret, bx + 16, by + 8);
        SPR_setFrame(sBoss.sprTurret, sBoss.turretAngleFrame);
    }
    if (sBoss.sprLeftTread) {
        SPR_setPosition(sBoss.sprLeftTread, bx - 4, by + 32);
        SPR_setFrame(sBoss.sprLeftTread, sBoss.treadAnimFrame);
    }
    if (sBoss.sprRightTread) {
        SPR_setPosition(sBoss.sprRightTread, bx + 36, by + 32);
        SPR_setFrame(sBoss.sprRightTread, sBoss.treadAnimFrame);
    }
    if (sBoss.sprMissilePod) {
        SPR_setPosition(sBoss.sprMissilePod, bx + 38, by - 4);
        SPR_setFrame(sBoss.sprMissilePod, sBoss.missilePodOpen ? 1 : 0);
    }
}

s16 GOTHAM_BOSS_getHealth(void)
{
    return sBoss.health;
}

s16 GOTHAM_BOSS_getMaxHealth(void)
{
    return sBoss.maxHealth;
}

GothamBoss* GOTHAM_BOSS_getState(void)
{
    return &sBoss;
}

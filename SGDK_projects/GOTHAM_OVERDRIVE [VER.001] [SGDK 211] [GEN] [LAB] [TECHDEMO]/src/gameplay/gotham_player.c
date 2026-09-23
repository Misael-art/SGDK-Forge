#include "gameplay/gotham_player.h"
#include "gameplay/gotham_particles.h"
#include "resources.h"
#include "system/input.h"
#include "system/audio.h"

#define PLAYER_START_X 136
#define PLAYER_START_Y 176
#define PLAYER_MIN_X   32
#define PLAYER_MAX_X   240
#define PLAYER_MIN_Y   130
#define PLAYER_MAX_Y   192

#define PLAYER_SPEED_X (FIX16(3.2))
#define PLAYER_SPEED_Y (FIX16(2.2))
#define PLAYER_ACCEL   (FIX16(0.6))
#define PLAYER_FRICTION (FIX16(0.3))

static GothamPlayer sPlayer;

void GOTHAM_PLAYER_init(void)
{
    sPlayer.x = FIX16(PLAYER_START_X);
    sPlayer.y = FIX16(PLAYER_START_Y);
    sPlayer.vx = 0;
    sPlayer.vy = 0;
    sPlayer.health = 100;
    sPlayer.maxHealth = 100;
    sPlayer.energy = 100;
    sPlayer.maxEnergy = 100;
    sPlayer.vulcanCooldown = 0;
    sPlayer.missileCooldown = 0;
    sPlayer.turboTimer = 0;
    sPlayer.invulnerableTimer = 0;
    sPlayer.animFrame = 0;
    sPlayer.isTurboActive = FALSE;

    sPlayer.sprite = SPR_addSprite(&spr_batmobile, PLAYER_START_X, PLAYER_START_Y, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    if (sPlayer.sprite != NULL) {
        SPR_setAutoAnimation(sPlayer.sprite, FALSE);
        SPR_setFrame(sPlayer.sprite, 0);
        SPR_setVisibility(sPlayer.sprite, VISIBLE);
    }
}

void GOTHAM_PLAYER_reset(void)
{
    sPlayer.x = FIX16(PLAYER_START_X);
    sPlayer.y = FIX16(PLAYER_START_Y);
    sPlayer.vx = 0;
    sPlayer.vy = 0;
    sPlayer.health = 100;
    sPlayer.energy = 100;
    sPlayer.vulcanCooldown = 0;
    sPlayer.missileCooldown = 0;
    sPlayer.turboTimer = 0;
    sPlayer.invulnerableTimer = 0;
    sPlayer.animFrame = 0;
    sPlayer.isTurboActive = FALSE;
    if (sPlayer.sprite != NULL) {
        SPR_setPosition(sPlayer.sprite, PLAYER_START_X, PLAYER_START_Y);
        SPR_setFrame(sPlayer.sprite, 0);
        SPR_setVisibility(sPlayer.sprite, VISIBLE);
    }
}

void GOTHAM_PLAYER_damage(s16 amount, GothamRasterFx* rasterFx)
{
    if (sPlayer.invulnerableTimer > 0) return;

    sPlayer.health -= amount;
    if (sPlayer.health < 0) sPlayer.health = 0;
    sPlayer.invulnerableTimer = 30; // 0.5s invulnerability

    GOTHAM_RASTER_triggerShake(rasterFx, 6, 12);
    GOTHAM_RASTER_triggerFlash(rasterFx, 3);
    GOTHAM_PARTICLES_spawnExplosion(F16_toInt(sPlayer.x) + 24, F16_toInt(sPlayer.y) + 12, 6);
    AUDIO_playCue(AUDIO_CUE_STRIKE);
}

void GOTHAM_PLAYER_update(GothamRasterFx* rasterFx)
{
    bool movingLeft = FALSE;
    bool movingRight = FALSE;
    fix16 targetSpeedX = PLAYER_SPEED_X;
    fix16 targetSpeedY = PLAYER_SPEED_Y;

    if (sPlayer.invulnerableTimer > 0) {
        sPlayer.invulnerableTimer--;
    }

    // Weapon cooldown ticks
    if (sPlayer.vulcanCooldown > 0) sPlayer.vulcanCooldown--;
    if (sPlayer.missileCooldown > 0) sPlayer.missileCooldown--;

    // Turbo boost recharge & handling
    if (INPUT_pressed(BUTTON_C) && sPlayer.energy >= 25 && sPlayer.turboTimer == 0) {
        sPlayer.turboTimer = 45;
        sPlayer.energy -= 25;
        sPlayer.isTurboActive = TRUE;
        GOTHAM_RASTER_triggerShake(rasterFx, 3, 20);
        AUDIO_playCue(AUDIO_CUE_JUMP);
    }

    if (sPlayer.turboTimer > 0) {
        sPlayer.turboTimer--;
        sPlayer.isTurboActive = TRUE;
        targetSpeedX = FIX16(5.0);
        targetSpeedY = FIX16(3.5);
        rasterFx->speed = 8;
        // Turbo sparks trail
        if ((sPlayer.turboTimer & 3) == 0) {
            GOTHAM_PARTICLES_spawnParticle(PART_SPARK, sPlayer.x + FIX16(24), sPlayer.y + FIX16(20), FIX16(-1), FIX16(2), 10);
        }
    } else {
        sPlayer.isTurboActive = FALSE;
        rasterFx->speed = 4;
        // Natural energy recharge
        if ((rasterFx->frameCount & 7) == 0 && sPlayer.energy < sPlayer.maxEnergy) {
            sPlayer.energy++;
        }
    }

    // Steering input
    if (INPUT_held(BUTTON_LEFT)) {
        sPlayer.vx -= PLAYER_ACCEL;
        if (sPlayer.vx < -targetSpeedX) sPlayer.vx = -targetSpeedX;
        movingLeft = TRUE;
        rasterFx->targetCurve = -32;
        rasterFx->rollAngle = -8;
    } else if (INPUT_held(BUTTON_RIGHT)) {
        sPlayer.vx += PLAYER_ACCEL;
        if (sPlayer.vx > targetSpeedX) sPlayer.vx = targetSpeedX;
        movingRight = TRUE;
        rasterFx->targetCurve = 32;
        rasterFx->rollAngle = 8;
    } else {
        if (sPlayer.vx > 0) {
            sPlayer.vx -= PLAYER_FRICTION;
            if (sPlayer.vx < 0) sPlayer.vx = 0;
        } else if (sPlayer.vx < 0) {
            sPlayer.vx += PLAYER_FRICTION;
            if (sPlayer.vx > 0) sPlayer.vx = 0;
        }
        rasterFx->targetCurve = 0;
        rasterFx->rollAngle = 0;
    }

    // Throttle / Brake input
    if (INPUT_held(BUTTON_UP)) {
        sPlayer.vy -= PLAYER_ACCEL;
        if (sPlayer.vy < -targetSpeedY) sPlayer.vy = -targetSpeedY;
    } else if (INPUT_held(BUTTON_DOWN)) {
        sPlayer.vy += PLAYER_ACCEL;
        if (sPlayer.vy > targetSpeedY) sPlayer.vy = targetSpeedY;
    } else {
        if (sPlayer.vy > 0) {
            sPlayer.vy -= PLAYER_FRICTION;
            if (sPlayer.vy < 0) sPlayer.vy = 0;
        } else if (sPlayer.vy < 0) {
            sPlayer.vy += PLAYER_FRICTION;
            if (sPlayer.vy > 0) sPlayer.vy = 0;
        }
    }

    // Update position with boundaries
    sPlayer.x += sPlayer.vx;
    sPlayer.y += sPlayer.vy;

    if (sPlayer.x < FIX16(PLAYER_MIN_X)) {
        sPlayer.x = FIX16(PLAYER_MIN_X);
        sPlayer.vx = 0;
    } else if (sPlayer.x > FIX16(PLAYER_MAX_X)) {
        sPlayer.x = FIX16(PLAYER_MAX_X);
        sPlayer.vx = 0;
    }

    if (sPlayer.y < FIX16(PLAYER_MIN_Y)) {
        sPlayer.y = FIX16(PLAYER_MIN_Y);
        sPlayer.vy = 0;
    } else if (sPlayer.y > FIX16(PLAYER_MAX_Y)) {
        sPlayer.y = FIX16(PLAYER_MAX_Y);
        sPlayer.vy = 0;
    }

    // Animation frame selection
    if (sPlayer.isTurboActive) {
        sPlayer.animFrame = 3; // Boost frame
    } else if (movingLeft) {
        sPlayer.animFrame = 1; // Tilt left
    } else if (movingRight) {
        sPlayer.animFrame = 2; // Tilt right
    } else {
        sPlayer.animFrame = 0; // Straight
    }

    // Weapon: Dual Vulcan Cannons (Button A)
    if (INPUT_held(BUTTON_A) && sPlayer.vulcanCooldown == 0) {
        s16 px = F16_toInt(sPlayer.x);
        s16 py = F16_toInt(sPlayer.y);
        // Left cannon & Right cannon
        GOTHAM_PARTICLES_spawnProjectile(PROJ_PLAYER_VULCAN, FIX16(px + 10), FIX16(py + 4), 0, FIX16(-8.0), 0, 0);
        GOTHAM_PARTICLES_spawnProjectile(PROJ_PLAYER_VULCAN, FIX16(px + 32), FIX16(py + 4), 0, FIX16(-8.0), 0, 0);
        sPlayer.vulcanCooldown = 6; // High rate of fire
    }

    // Weapon: Batarang Micro-Missiles (Button B)
    if (INPUT_pressed(BUTTON_B) && sPlayer.missileCooldown == 0) {
        s16 px = F16_toInt(sPlayer.x);
        s16 py = F16_toInt(sPlayer.y);
        GOTHAM_PARTICLES_spawnProjectile(PROJ_PLAYER_MISSILE, FIX16(px + 6), FIX16(py + 8), FIX16(-2.0), FIX16(-5.0), 160, 60);
        GOTHAM_PARTICLES_spawnProjectile(PROJ_PLAYER_MISSILE, FIX16(px + 36), FIX16(py + 8), FIX16(2.0), FIX16(-5.0), 160, 60);
        sPlayer.missileCooldown = 20;
        GOTHAM_PARTICLES_spawnParticle(PART_SMOKE, FIX16(px + 24), FIX16(py + 16), 0, FIX16(1.0), 12);
        AUDIO_playCue(AUDIO_CUE_LAND);
    }

    // Sprite update with invulnerability flicker
    if (sPlayer.sprite != NULL) {
        s16 sx = F16_toInt(sPlayer.x);
        s16 sy = F16_toInt(sPlayer.y);
        if (sPlayer.invulnerableTimer > 0 && (sPlayer.invulnerableTimer & 2)) {
            SPR_setVisibility(sPlayer.sprite, HIDDEN);
        } else {
            SPR_setVisibility(sPlayer.sprite, VISIBLE);
            SPR_setFrame(sPlayer.sprite, sPlayer.animFrame);
            SPR_setPosition(sPlayer.sprite, sx, sy);
        }
    }
}

s16 GOTHAM_PLAYER_getX(void)
{
    return F16_toInt(sPlayer.x);
}

s16 GOTHAM_PLAYER_getY(void)
{
    return F16_toInt(sPlayer.y);
}

GothamPlayer* GOTHAM_PLAYER_getState(void)
{
    return &sPlayer;
}

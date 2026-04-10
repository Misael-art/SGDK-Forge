/**
 * player.c — Player physics, animation state machine, damage system
 *
 * Physics model: Sonic-style tiered accel/decel using fix32.
 * Animation driven by velocity state, not by input directly.
 * Invulnerability frames prevent rapid damage.
 */

#include <genesis.h>

#include "player.h"
#include "camera.h"
#include "effects.h"
#include "enemy.h"
#include "hud.h"
#include "game_config.h"

#include "res_sprite.h"
#include "res_sound.h"

/* =========================================================================
 * State
 * ========================================================================= */
fix32   playerPosX;
fix32   playerPosY;
fix32   playerMovX;
fix32   playerMovY;

bool    playerOnGround;
bool    playerFacingRight;
s16     playerInvulnTimer;
u8      playerHP;
u8      playerLives;
u32     playerScore;

Sprite* playerSpr;

/* Input tracking */
static s16 xOrder;
static s16 yOrder;
static bool jumpPressed;

/* Coyote time: allow jump a few frames after walking off ledge */
static u8 coyoteFrames;
#define COYOTE_TIME 6

/* =========================================================================
 * Init
 * ========================================================================= */
u16 PLAYER_init(u16 vramIndex) {
    playerSpr = SPR_addSprite(&player_sprite,
        100, 100, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));

    SPR_setAnim(playerSpr, ANIM_STAND);

    /* Load player palette from sprite */
    PAL_setPalette(PAL2, player_sprite.palette->data, CPU);

    return vramIndex; /* sprites use dynamic VRAM, no manual tracking needed */
}

/* =========================================================================
 * Reset (called when starting a new game)
 * ========================================================================= */
void PLAYER_reset(void) {
    playerPosX = FIX32(80);
    playerPosY = GROUND_Y;
    playerMovX = 0;
    playerMovY = 0;
    playerOnGround = TRUE;
    playerFacingRight = TRUE;
    playerInvulnTimer = 0;
    playerHP = PLAYER_MAX_HP;
    playerLives = 3;
    playerScore = 0;
    coyoteFrames = 0;
    xOrder = 0;
    yOrder = 0;
    jumpPressed = FALSE;

    HUD_updateScore(0);
    HUD_updateLives(3);
}

/* =========================================================================
 * Input (called with polled joypad state — per-frame held buttons)
 * ========================================================================= */
void PLAYER_handleInput(u16 pad) {
    if (pad & BUTTON_LEFT)  xOrder = -1;
    else if (pad & BUTTON_RIGHT) xOrder = 1;
    else xOrder = 0;

    if (pad & BUTTON_UP)   yOrder = -1;
    else if (pad & BUTTON_DOWN) yOrder = 1;
    else yOrder = 0;
}

/* =========================================================================
 * Joy event (called on button press/release — for instant-response actions)
 * ========================================================================= */
void PLAYER_doJoyEvent(u16 joy, u16 changed, u16 state) {
    /* Jump: A, B or C while on ground (or within coyote time) */
    if (changed & state & (BUTTON_A | BUTTON_B | BUTTON_C)) {
        if (playerOnGround || coyoteFrames > 0) {
            playerMovY = JUMP_SPEED;
            playerOnGround = FALSE;
            coyoteFrames = 0;
            XGM2_playPCM(snd_jump, sizeof(snd_jump), SOUND_PCM_CH2);
        }
    }
}

/* =========================================================================
 * Damage
 * ========================================================================= */
void PLAYER_takeDamage(void) {
    if (playerInvulnTimer > 0) return; /* invulnerable */

    playerHP--;
    playerInvulnTimer = PLAYER_INVULN_TIME;

    EFFECTS_startShake(SHAKE_MAGNITUDE, SHAKE_DURATION);
    EFFECTS_startFlash(FLASH_DURATION);
    XGM2_playPCM(snd_hit, sizeof(snd_hit), SOUND_PCM_CH3);

    if (playerHP == 0) {
        playerLives--;
        HUD_updateLives(playerLives);
        XGM2_playPCM(snd_die, sizeof(snd_die), SOUND_PCM_CH2);

        if (playerLives > 0) {
            /* Respawn */
            playerHP = PLAYER_MAX_HP;
            playerPosX = FIX32(80);
            playerPosY = GROUND_Y;
            playerMovX = 0;
            playerMovY = 0;
        }
    }
}

/* =========================================================================
 * Score
 * ========================================================================= */
void PLAYER_addScore(u32 points) {
    playerScore += points;
    HUD_updateScore(playerScore);
}

/* =========================================================================
 * Physics + animation update (called once per frame)
 * ========================================================================= */
void PLAYER_update(void) {

    /* --- Horizontal movement: Sonic-style tiered accel/decel --- */
    if (xOrder > 0) {
        playerMovX += ACCEL;
        if (playerMovX < 0) playerMovX += ACCEL;   /* quick turn boost */
        if (playerMovX > MAX_MOVE_X) playerMovX = MAX_MOVE_X;
        playerFacingRight = TRUE;
    } else if (xOrder < 0) {
        playerMovX -= ACCEL;
        if (playerMovX > 0) playerMovX -= ACCEL;
        if (playerMovX < -MAX_MOVE_X) playerMovX = -MAX_MOVE_X;
        playerFacingRight = FALSE;
    } else {
        /* Tiered deceleration — feels natural, not instant stop */
        if (playerMovX > FIX32(0.1)) {
            playerMovX -= DEACCEL;
            if (playerMovX < 0) playerMovX = 0;
        } else if (playerMovX < FIX32(-0.1)) {
            playerMovX += DEACCEL;
            if (playerMovX > 0) playerMovX = 0;
        } else {
            playerMovX = 0;
        }
    }

    /* Apply horizontal movement */
    playerPosX += playerMovX;

    /* --- Vertical physics: gravity --- */
    if (!playerOnGround) {
        playerMovY += GRAVITY;
        /* Terminal velocity */
        if (playerMovY > FIX32(12)) playerMovY = FIX32(12);
    }

    playerPosY += playerMovY;

    /* --- Ground collision --- */
    if (playerPosY >= GROUND_Y) {
        playerPosY = GROUND_Y;
        playerMovY = 0;
        if (!playerOnGround) {
            playerOnGround = TRUE;
            coyoteFrames = 0;
        }
    } else {
        if (playerOnGround) {
            /* Just walked off ledge — start coyote timer */
            playerOnGround = FALSE;
            coyoteFrames = COYOTE_TIME;
        } else if (coyoteFrames > 0) {
            coyoteFrames--;
        }
    }

    /* --- World bounds clip --- */
    if (playerPosX < MIN_WORLD_X) {
        playerPosX = MIN_WORLD_X;
        playerMovX = 0;
    }
    if (playerPosX > MAX_WORLD_X) {
        playerPosX = MAX_WORLD_X;
        playerMovX = 0;
    }

    /* --- Invulnerability countdown --- */
    if (playerInvulnTimer > 0) {
        playerInvulnTimer--;
        /* Blink sprite during invulnerability */
        SPR_setVisibility(playerSpr,
            (playerInvulnTimer & 4) ? HIDDEN : VISIBLE);
    } else {
        SPR_setVisibility(playerSpr, VISIBLE);
    }

    /* --- Animation state machine --- */
    if (!playerOnGround) {
        /* In air — always roll */
        SPR_setAnim(playerSpr, ANIM_ROLL);
    } else {
        fix32 absMovX = (playerMovX < 0) ? -playerMovX : playerMovX;

        if (absMovX >= BRAKE_SPEED &&
            ((playerMovX > 0 && xOrder < 0) || (playerMovX < 0 && xOrder > 0))) {
            /* Braking: moving but input is opposite direction */
            SPR_setAnim(playerSpr, ANIM_BRAKE);
        } else if (absMovX >= RUN_SPEED) {
            SPR_setAnim(playerSpr, ANIM_RUN);
        } else if (absMovX > FIX32(0.1)) {
            SPR_setAnim(playerSpr, ANIM_WALK);
        } else {
            /* Idle / directional idle */
            if (yOrder < 0)      SPR_setAnim(playerSpr, ANIM_UP);
            else if (yOrder > 0) SPR_setAnim(playerSpr, ANIM_CROUCH);
            else                 SPR_setAnim(playerSpr, ANIM_STAND);
        }
    }

    /* Flip sprite based on movement direction */
    SPR_setHFlip(playerSpr, !playerFacingRight);
}

/* =========================================================================
 * Update sprite screen position (after camera is resolved)
 * ========================================================================= */
void PLAYER_updateScreenPos(void) {
    s16 sx = F32_toInt(playerPosX) - camX;
    s16 sy = F32_toInt(playerPosY) - camY - 32; /* -32 because posY is feet */
    SPR_setPosition(playerSpr, sx, sy);
}

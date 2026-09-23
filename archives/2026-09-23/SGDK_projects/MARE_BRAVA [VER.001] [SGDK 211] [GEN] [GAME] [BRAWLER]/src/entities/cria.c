#include "entities/cria.h"

#include "resources.h"
#include "system/audio.h"

#define CRIA_SPAWN_X 288
#define CRIA_MIN_X 48
#define CRIA_PIVOT_X 24
#define CRIA_GROUND_Y 60
#define CRIA_WORLD_Y 192
#define CRIA_AGGRO_PX 200
#define CRIA_STRIKE_PX 40
#define CRIA_LANE_PX 12
#define CRIA_COOLDOWN_FRAMES 24
#define CRIA_KNOCKBACK_PX (-8)
#define CRIA_MAX_HP 40
#define CRIA_HURT_FRAMES 12
#define CRIA_IFRAME_FRAMES 8
#define CRIA_PLAYER_HIT_RANGE 56
#define CRIA_IDLE_COUNT 4
#define CRIA_WALK_COUNT 4
#define CRIA_TEL_COUNT 4
#define CRIA_HIT_COUNT 4
#define CRIA_REC_COUNT 4

typedef enum CriaAiState {
    CRIA_AI_IDLE = 0,
    CRIA_AI_APPROACH,
    CRIA_AI_TELEGRAPH,
    CRIA_AI_ATTACK,
    CRIA_AI_RECOVER,
    CRIA_AI_HURT
} CriaAiState;

static Sprite *sSprite;
static fix16 sX;
static CriaAiState sState;
static u8 sFrame;
static u8 sTicks;
static u8 sCooldown;
static u8 sHealth;
static u8 sHurtFrames;
static u8 sIframes;
static fix16 sKnockbackVelocity;
static bool sActive;
static bool sHitLanded;
static const u8 sIdleDuration[CRIA_IDLE_COUNT] = { 8, 7, 8, 7 };
static const u8 sWalkDuration[CRIA_WALK_COUNT] = { 5, 4, 5, 4 };
static const u8 sTelDuration[CRIA_TEL_COUNT] = { 3, 3, 4, 2 };
static const u8 sHitDuration[CRIA_HIT_COUNT] = { 3, 4, 6, 5 };
static const u8 sRecDuration[CRIA_REC_COUNT] = { 4, 5, 6, 8 };

static const SpriteDefinition *criaDefinition(CriaAiState state)
{
    if (state == CRIA_AI_APPROACH) {
        return &spr_cria_walk_lean;
    }
    if (state == CRIA_AI_TELEGRAPH) {
        return &spr_cria_telegraph_lean;
    }
    if (state == CRIA_AI_ATTACK) {
        return &spr_cria_hit_lean;
    }
    if (state == CRIA_AI_RECOVER) {
        return &spr_cria_recover_lean;
    }
    return &spr_cria_idle_lean;
}

static bool criaSetState(CriaAiState state)
{
    if (sSprite == NULL) {
        return FALSE;
    }
    if (!SPR_setDefinition(sSprite, criaDefinition(state))) {
        VDP_drawTextFill("CRIA SPRITE ALLOC FAILED", 7, 11, 23);
        return FALSE;
    }
    SPR_setAutoAnimation(sSprite, FALSE);
    SPR_setAnimAndFrame(sSprite, 0, 0);
    sState = state;
    sFrame = 0;
    sTicks = 0;
    sHitLanded = FALSE;
    return TRUE;
}

static void criaClampWorldX(void)
{
    if (F16_toInt(sX) < CRIA_MIN_X) {
        sX = FIX16(CRIA_MIN_X);
        sKnockbackVelocity = 0;
    }
}

static s16 criaDeltaX(fix16 playerX)
{
    return F16_toInt(sX) - F16_toInt(playerX);
}

static bool criaInFront(fix16 playerX)
{
    return F16_toInt(playerX) < F16_toInt(sX);
}

static bool criaInAggro(s16 dx)
{
    if (dx < 0) {
        dx = (s16) (-dx);
    }
    return dx <= CRIA_AGGRO_PX;
}

static bool criaInStrike(s16 dx)
{
    return (dx > 0) && (dx <= CRIA_STRIKE_PX);
}

static bool criaSameLane(fix16 playerY)
{
    s16 dy = F16_toInt(playerY) - CRIA_WORLD_Y;

    if (dy < 0) {
        dy = (s16) (-dy);
    }
    return dy <= CRIA_LANE_PX;
}

static void criaTickIdle(void)
{
    sTicks++;
    if (sTicks < sIdleDuration[sFrame]) {
        return;
    }
    sTicks = 0;
    sFrame++;
    if (sFrame >= CRIA_IDLE_COUNT) {
        sFrame = 0;
    }
    SPR_setFrame(sSprite, sFrame);
}

static void criaTickWalk(void)
{
    sTicks++;
    if (sTicks < sWalkDuration[sFrame]) {
        return;
    }
    sTicks = 0;
    sFrame++;
    if (sFrame >= CRIA_WALK_COUNT) {
        sFrame = 0;
    }
    SPR_setFrame(sSprite, sFrame);
}

static bool criaTickOnce(const u8 *duration, u8 lastIndex)
{
    sTicks++;
    if (sTicks < duration[sFrame]) {
        return FALSE;
    }
    sTicks = 0;
    if (sFrame >= lastIndex) {
        return TRUE;
    }
    sFrame++;
    SPR_setFrame(sSprite, sFrame);
    return FALSE;
}

bool CRIA_enter(s16 cameraX)
{
    sX = FIX16(CRIA_SPAWN_X);
    sState = CRIA_AI_IDLE;
    sFrame = 0;
    sTicks = 0;
    sCooldown = 0;
    sHealth = CRIA_MAX_HP;
    sHurtFrames = 0;
    sIframes = 0;
    sKnockbackVelocity = 0;
    sActive = TRUE;
    sHitLanded = FALSE;
    sSprite = SPR_addSprite(
        &spr_cria_idle_lean,
        CRIA_SPAWN_X - cameraX - CRIA_PIVOT_X,
        CRIA_WORLD_Y - CRIA_GROUND_Y,
        TILE_ATTR(PAL3, TRUE, FALSE, FALSE)
    );
    if (sSprite == NULL) {
        return FALSE;
    }
    SPR_setAnim(sSprite, 0);
    SPR_setAutoAnimation(sSprite, FALSE);
    SPR_setFrame(sSprite, 0);
    return TRUE;
}

bool CRIA_receiveHit(fix16 attackerX, bool attackerFacingRight, u8 damage, s16 knockbackPx)
{
    s16 distance;

    if (!sActive || (sSprite == NULL) || (sIframes > 0)) {
        return FALSE;
    }

    distance = F16_toInt(sX) - F16_toInt(attackerX);
    if ((attackerFacingRight && ((distance < 0) || (distance > CRIA_PLAYER_HIT_RANGE))) ||
        (!attackerFacingRight && ((distance > 0) || (distance < -CRIA_PLAYER_HIT_RANGE)))) {
        return FALSE;
    }

    if (damage >= sHealth) {
        sHealth = 0;
        sActive = FALSE;
        sKnockbackVelocity = 0;
        SPR_setPosition(sSprite, -64, -64);
        return TRUE;
    }

    sHealth -= damage;
    sIframes = CRIA_IFRAME_FRAMES;
    sHurtFrames = CRIA_HURT_FRAMES;
    sKnockbackVelocity = FIX16(knockbackPx);
    criaSetState(CRIA_AI_HURT);
    return TRUE;
}

bool CRIA_isActive(void)
{
    return sActive;
}

u8 CRIA_getHealth(void)
{
    return sHealth;
}

void CRIA_update(fix16 playerX, fix16 playerY, bool playerGrounded, s16 cameraX, s16 *knockbackX)
{
    s16 dx;

    if (knockbackX != NULL) {
        *knockbackX = 0;
    }
    if (sSprite == NULL) {
        return;
    }
    if (!sActive) {
        SPR_setPosition(sSprite, -64, -64);
        return;
    }

    if (sIframes > 0) {
        sIframes--;
    }

    if (sState == CRIA_AI_HURT) {
        sX += sKnockbackVelocity;
        if (sKnockbackVelocity > 0) {
            sKnockbackVelocity -= FIX16(1) >> 2;
            if (sKnockbackVelocity < 0) {
                sKnockbackVelocity = 0;
            }
        } else if (sKnockbackVelocity < 0) {
            sKnockbackVelocity += FIX16(1) >> 2;
            if (sKnockbackVelocity > 0) {
                sKnockbackVelocity = 0;
            }
        }
        criaClampWorldX();
        if (sHurtFrames > 0) {
            sHurtFrames--;
        }
        if (sHurtFrames == 0) {
            sCooldown = CRIA_COOLDOWN_FRAMES;
            criaSetState(CRIA_AI_IDLE);
        }
        SPR_setPosition(
            sSprite,
            F16_toInt(sX) - cameraX - CRIA_PIVOT_X,
            CRIA_WORLD_Y - CRIA_GROUND_Y
        );
        return;
    }

    dx = criaDeltaX(playerX);

    switch (sState) {
        case CRIA_AI_IDLE:
            if (sCooldown > 0) {
                sCooldown--;
                criaTickIdle();
                break;
            }
            if (criaInFront(playerX) && criaInStrike(dx) && criaSameLane(playerY) && playerGrounded) {
                criaSetState(CRIA_AI_TELEGRAPH);
                break;
            }
            if (criaInFront(playerX) && criaInAggro(dx)) {
                criaSetState(CRIA_AI_APPROACH);
                break;
            }
            criaTickIdle();
            break;

        case CRIA_AI_APPROACH:
            if (!criaInFront(playerX) || !criaInAggro(dx)) {
                criaSetState(CRIA_AI_IDLE);
                break;
            }
            if (criaInStrike(dx) && criaSameLane(playerY) && playerGrounded) {
                criaSetState(CRIA_AI_TELEGRAPH);
                break;
            }
            if (criaInStrike(dx)) {
                criaTickWalk();
                break;
            }
            sX -= FIX16(1) + (FIX16(1) >> 1);
            criaClampWorldX();
            criaTickWalk();
            break;

        case CRIA_AI_TELEGRAPH:
            if (criaTickOnce(sTelDuration, CRIA_TEL_COUNT - 1)) {
                criaSetState(CRIA_AI_ATTACK);
            }
            break;

        case CRIA_AI_ATTACK:
            if (!sHitLanded && (sFrame >= 1) && criaInStrike(dx) && criaSameLane(playerY)) {
                sHitLanded = TRUE;
                AUDIO_playCue(AUDIO_CUE_STRIKE);
                if (knockbackX != NULL) {
                    *knockbackX = CRIA_KNOCKBACK_PX;
                }
            }
            if (criaTickOnce(sHitDuration, 2)) {
                criaSetState(CRIA_AI_RECOVER);
            }
            break;

        case CRIA_AI_RECOVER:
            if (criaTickOnce(sRecDuration, CRIA_REC_COUNT - 1)) {
                sCooldown = CRIA_COOLDOWN_FRAMES;
                criaSetState(CRIA_AI_IDLE);
            }
            break;

        /* Handled before this switch so hurt recoil cannot run normal AI. */
        case CRIA_AI_HURT:
            break;
    }

    SPR_setPosition(
        sSprite,
        F16_toInt(sX) - cameraX - CRIA_PIVOT_X,
        CRIA_WORLD_Y - CRIA_GROUND_Y
    );
}

void CRIA_exit(void)
{
    sSprite = NULL;
    sState = CRIA_AI_IDLE;
    sFrame = 0;
    sTicks = 0;
    sCooldown = 0;
    sHealth = 0;
    sHurtFrames = 0;
    sIframes = 0;
    sKnockbackVelocity = 0;
    sActive = FALSE;
    sHitLanded = FALSE;
}

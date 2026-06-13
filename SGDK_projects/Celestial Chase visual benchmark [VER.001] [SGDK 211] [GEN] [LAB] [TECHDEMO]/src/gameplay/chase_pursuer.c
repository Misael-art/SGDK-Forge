#include <genesis.h>

#include "gameplay/chase_pursuer.h"
#include "resources.h"

#define CHASE_RIG_FRAME_TICK_TABLE_SIZE 6
#define CHASE_DUST_FRAME_TICK_TABLE_SIZE 5
#define CHASE_SHAKE_COUNT 8
#define CHASE_SHAKE_MAX 5
#define CHASE_PURSUER_HEAD_X_OFFSET 8
#define CHASE_PURSUER_HEAD_Y_OFFSET -18
#define CHASE_PURSUER_HEAD_SWING_SHIFT 2
#define CHASE_PURSUER_BOB_SHIFT 2

static const u8 CHASE_RIG_FRAME_TICKS[CHASE_RIG_FRAME_TICK_TABLE_SIZE] = { 6, 5, 5, 7, 5, 5 };
static const u8 CHASE_DUST_FRAME_TICKS[CHASE_DUST_FRAME_TICK_TABLE_SIZE] = { 2, 2, 2, 3, 3 };
static const s16 CHASE_SHAKE_X[CHASE_SHAKE_COUNT] = { 4, -4, 3, -3, 2, -2, 1, 0 };
static const s16 CHASE_SHAKE_Y[CHASE_SHAKE_COUNT] = { -3, 3, -2, 2, -1, 1, 0, 0 };
static const s8 CHASE_RIG_SINE[32] = {
    0, 2, 4, 6, 7, 8, 9, 10,
    10, 10, 9, 8, 7, 6, 4, 2,
    0, -2, -4, -6, -7, -8, -9, -10,
    -10, -10, -9, -8, -7, -6, -4, -2
};

static Sprite* sTorso;
static Sprite* sHead;
static Sprite* sClawNear;
static Sprite* sClawFar;
static Sprite* sClawShadowNear;
static Sprite* sClawShadowFar;
static Sprite* sDust;
static Sprite* sPulse;
static u32 sMotionFrame;
static u16 sPursuerFrame;
static u16 sPursuerTick;
static u16 sDustFrame;
static u16 sDustTick;
static u16 sPulseFrame;
static u16 sPulseTick;
static u16 sPulseFrames;
static u16 sShakeIndex;
static u8 sRigFrameCount;
static u8 sDustFrameCount;
static u8 sPulseFrameCount;
static bool sDustActive;
static bool sShakeActive;
static bool sVisible;

static u8 chaseSpriteDefinitionFrameCount(const SpriteDefinition* definition)
{
    if (definition == NULL || definition->numAnimation == 0 || definition->animations == NULL || definition->animations[0] == NULL) {
        return 1;
    }
    if (definition->animations[0]->numFrame == 0) {
        return 1;
    }
    return definition->animations[0]->numFrame;
}

static u16 chaseTickForFrame(const u8* table, u16 tableSize, u16 frame, u16 defaultTick)
{
    if (table != NULL && tableSize > 0 && frame < tableSize) {
        u16 tick = table[frame];
        return (tick == 0) ? defaultTick : tick;
    }
    return defaultTick;
}

static void chasePursuerSetRigVisibility(bool visible, u16 pressure)
{
    bool showFarClaw = visible && sPulseFrames == 0 && pressure < 90;

    if (sTorso != NULL) SPR_setVisibility(sTorso, visible ? VISIBLE : HIDDEN);
    if (sHead != NULL) SPR_setVisibility(sHead, visible ? VISIBLE : HIDDEN);
    if (sClawNear != NULL) SPR_setVisibility(sClawNear, visible ? VISIBLE : HIDDEN);
    if (sClawFar != NULL) SPR_setVisibility(sClawFar, showFarClaw ? VISIBLE : HIDDEN);
    if (sClawShadowNear != NULL) SPR_setVisibility(sClawShadowNear, visible ? VISIBLE : HIDDEN);
    if (sClawShadowFar != NULL) SPR_setVisibility(sClawShadowFar, showFarClaw ? VISIBLE : HIDDEN);
}

static void chasePursuerPlaceRig(u16 pressure)
{
    u16 phase = (u16)((sMotionFrame >> 1) & 31u);
    s16 bob = CHASE_RIG_SINE[phase] >> CHASE_PURSUER_BOB_SHIFT;
    s16 headSwing = CHASE_RIG_SINE[(phase + 6u) & 31u] >> CHASE_PURSUER_HEAD_SWING_SHIFT;
    s16 reach = CHASE_RIG_SINE[(phase + 10u) & 31u];
    s16 rootX = 112;
    s16 rootY = 44 + (s16)(pressure / 24u) + bob;

    if (sTorso != NULL) SPR_setPosition(sTorso, rootX, rootY);
    if (sHead != NULL) {
        SPR_setPosition(
            sHead,
            rootX + CHASE_PURSUER_HEAD_X_OFFSET + headSwing,
            rootY + CHASE_PURSUER_HEAD_Y_OFFSET - (bob >> 1)
        );
    }
    if (sClawNear != NULL) SPR_setPosition(sClawNear, rootX + 54 + reach, rootY + 34 - bob);
    if (sClawFar != NULL) SPR_setPosition(sClawFar, rootX - 34 - (reach >> 1), rootY + 24 + (bob >> 1));
    if (sClawShadowNear != NULL) SPR_setPosition(sClawShadowNear, rootX + 78 + reach, rootY + 92);
    if (sClawShadowFar != NULL) SPR_setPosition(sClawShadowFar, rootX - 10 - (reach >> 1), rootY + 82);
}

static void chasePursuerAdvanceRigFrames(bool allowAnimationUpload)
{
    sPursuerTick++;
    if (!allowAnimationUpload || sPursuerTick < chaseTickForFrame(CHASE_RIG_FRAME_TICKS, CHASE_RIG_FRAME_TICK_TABLE_SIZE, sPursuerFrame, 5)) {
        return;
    }

    sPursuerTick = 0;
    sPursuerFrame++;
    if (sPursuerFrame >= sRigFrameCount) {
        sPursuerFrame = 0;
    }

    if (sTorso != NULL) SPR_setFrame(sTorso, sPursuerFrame);
    if (sHead != NULL) SPR_setFrame(sHead, sPursuerFrame);
    if (sClawNear != NULL) SPR_setFrame(sClawNear, sPursuerFrame);
    if (sClawFar != NULL) SPR_setFrame(sClawFar, sPursuerFrame);
}

static void chasePursuerUpdateDust(void)
{
    if (!sDustActive || sDust == NULL) {
        return;
    }

    sDustTick++;
    if (sDustTick < chaseTickForFrame(CHASE_DUST_FRAME_TICKS, CHASE_DUST_FRAME_TICK_TABLE_SIZE, sDustFrame, 2)) {
        return;
    }

    sDustTick = 0;
    sDustFrame++;
    if (sDustFrame >= sDustFrameCount) {
        sDustActive = FALSE;
        sDustFrame = 0;
        SPR_setVisibility(sDust, HIDDEN);
        SPR_setFrame(sDust, 0);
    } else {
        SPR_setFrame(sDust, sDustFrame);
    }
}

static void chasePursuerUpdatePulse(void)
{
    if (sPulseFrames == 0 || sPulse == NULL) {
        return;
    }

    sPulseFrames--;
    sPulseTick++;
    if (sPulseTick >= 3) {
        sPulseTick = 0;
        if ((u16)(sPulseFrame + 1) < (u16)sPulseFrameCount) {
            sPulseFrame++;
            SPR_setFrame(sPulse, sPulseFrame);
        }
    }

    if (sPulseFrames == 0) {
        SPR_setVisibility(sPulse, HIDDEN);
        SPR_setFrame(sPulse, 0);
        sPulseFrame = 0;
    }
}

void CHASE_PURSUER_enter(void)
{
    sMotionFrame = 0;
    sPursuerFrame = 0;
    sPursuerTick = 0;
    sDustFrame = 0;
    sDustTick = 0;
    sPulseFrame = 0;
    sPulseTick = 0;
    sPulseFrames = 0;
    sShakeIndex = 0;
    sRigFrameCount = chaseSpriteDefinitionFrameCount(&spr_chase_pursuer_torso_v011);
    {
        u8 headFrames = chaseSpriteDefinitionFrameCount(&spr_chase_pursuer_head_v009);
        u8 clawFrames = chaseSpriteDefinitionFrameCount(&spr_chase_pursuer_claw_v009);
        if (headFrames < sRigFrameCount) sRigFrameCount = headFrames;
        if (clawFrames < sRigFrameCount) sRigFrameCount = clawFrames;
    }
    sDustFrameCount = chaseSpriteDefinitionFrameCount(&spr_chase_pursuer_dust_impact);
    sPulseFrameCount = chaseSpriteDefinitionFrameCount(&spr_chase_pulse_impact_v009);
    sDustActive = FALSE;
    sShakeActive = FALSE;
    sVisible = TRUE;

    sTorso = SPR_addSprite(&spr_chase_pursuer_torso_v011, 112, 48, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    sHead = SPR_addSprite(&spr_chase_pursuer_head_v009, 120, 24, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    sClawNear = SPR_addSprite(&spr_chase_pursuer_claw_v009, 164, 80, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    sClawFar = NULL;
    sClawShadowNear = SPR_addSprite(
        &spr_chase_contact_shadow_v011,
        -96,
        -96,
        TILE_ATTR(PAL3, TRUE, FALSE, FALSE)
    );
    sClawShadowFar = NULL;
    sDust = SPR_addSprite(&spr_chase_pursuer_dust_impact, -96, -96, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    sPulse = SPR_addSprite(&spr_chase_pulse_impact_v009, -96, -96, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));

    if (sTorso != NULL) {
        SPR_setAutoAnimation(sTorso, FALSE);
        SPR_setFrame(sTorso, 0);
        SPR_setAlwaysAtBottom(sTorso);
    }
    if (sHead != NULL) {
        SPR_setAutoAnimation(sHead, FALSE);
        SPR_setFrame(sHead, 0);
        SPR_setDepth(sHead, 70);
    }
    if (sClawNear != NULL) {
        const u16 sharedClawTileIndex = sClawNear->attribut & TILE_INDEX_MASK;
        SPR_setAutoAnimation(sClawNear, FALSE);
        SPR_setFrame(sClawNear, 0);
        SPR_setDepth(sClawNear, 50);
        sClawFar = SPR_addSpriteEx(
            &spr_chase_pursuer_claw_v009,
            78,
            72,
            TILE_ATTR_FULL(PAL2, FALSE, FALSE, TRUE, sharedClawTileIndex),
            0
        );
    }
    if (sClawFar != NULL) {
        SPR_setAutoAnimation(sClawFar, FALSE);
        SPR_setFrame(sClawFar, 0);
        SPR_setHFlip(sClawFar, TRUE);
        SPR_setAlwaysAtBottom(sClawFar);
    }
    if (sClawShadowNear != NULL) {
        const u16 sharedShadowTileIndex = sClawShadowNear->attribut & TILE_INDEX_MASK;
        SPR_setAutoAnimation(sClawShadowNear, FALSE);
        SPR_setFrame(sClawShadowNear, 2);
        SPR_setAlwaysAtBottom(sClawShadowNear);
        sClawShadowFar = SPR_addSpriteEx(
            &spr_chase_contact_shadow_v011,
            -96,
            -96,
            TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, sharedShadowTileIndex),
            0
        );
    }
    if (sClawShadowFar != NULL) {
        SPR_setAutoAnimation(sClawShadowFar, FALSE);
        SPR_setFrame(sClawShadowFar, 2);
        SPR_setAlwaysAtBottom(sClawShadowFar);
    }
    if (sDust != NULL) {
        SPR_setAutoAnimation(sDust, FALSE);
        SPR_setFrame(sDust, 0);
        SPR_setVisibility(sDust, HIDDEN);
    }
    if (sPulse != NULL) {
        SPR_setAutoAnimation(sPulse, FALSE);
        SPR_setFrame(sPulse, 0);
        SPR_setVisibility(sPulse, HIDDEN);
    }

    chasePursuerPlaceRig(22);
    chasePursuerSetRigVisibility(TRUE, 22);
}

void CHASE_PURSUER_update(u16 pressure, bool allowAnimationUpload)
{
    sMotionFrame++;
    chasePursuerPlaceRig(pressure);
    chasePursuerAdvanceRigFrames(allowAnimationUpload);
    chasePursuerUpdateDust();
    chasePursuerUpdatePulse();
    chasePursuerSetRigVisibility(sVisible, pressure);
}

void CHASE_PURSUER_startImpact(s16 x, s16 y)
{
    sDustActive = TRUE;
    sDustFrame = 0;
    sDustTick = 0;
    sShakeActive = TRUE;
    sShakeIndex = 0;
    if (sDust != NULL) {
        SPR_setPosition(sDust, x, y + 26);
        SPR_setFrame(sDust, 0);
        SPR_setVisibility(sDust, VISIBLE);
    }
}

void CHASE_PURSUER_startPulse(s16 x, s16 y)
{
    sPulseFrame = 0;
    sPulseTick = 0;
    sPulseFrames = 22;
    sShakeActive = TRUE;
    sShakeIndex = 0;
    if (sPulse != NULL) {
        SPR_setPosition(sPulse, x, y + 20);
        SPR_setFrame(sPulse, 0);
        SPR_setVisibility(sPulse, VISIBLE);
    }
}

void CHASE_PURSUER_consumeShake(ChaseCameraShake* shake)
{
    shake->x = 0;
    shake->y = 0;

    if (!sShakeActive) {
        return;
    }

    shake->x = CHASE_SHAKE_X[sShakeIndex];
    shake->y = CHASE_SHAKE_Y[sShakeIndex];
    if (shake->x > CHASE_SHAKE_MAX) shake->x = CHASE_SHAKE_MAX;
    if (shake->x < -CHASE_SHAKE_MAX) shake->x = -CHASE_SHAKE_MAX;
    if (shake->y > CHASE_SHAKE_MAX) shake->y = CHASE_SHAKE_MAX;
    if (shake->y < -CHASE_SHAKE_MAX) shake->y = -CHASE_SHAKE_MAX;
    sShakeIndex++;
    if (sShakeIndex >= CHASE_SHAKE_COUNT) {
        sShakeActive = FALSE;
        sShakeIndex = 0;
    }
}

bool CHASE_PURSUER_isPulseActive(void)
{
    return sPulseFrames > 0;
}

void CHASE_PURSUER_hideFx(void)
{
    sDustActive = FALSE;
    sPulseFrames = 0;
    sShakeActive = FALSE;
    if (sDust != NULL) SPR_setVisibility(sDust, HIDDEN);
    if (sPulse != NULL) SPR_setVisibility(sPulse, HIDDEN);
}

void CHASE_PURSUER_setVisible(bool visible)
{
    sVisible = visible;
    chasePursuerSetRigVisibility(visible, 0);
}

void CHASE_PURSUER_exit(void)
{
    sTorso = NULL;
    sHead = NULL;
    sClawNear = NULL;
    sClawFar = NULL;
    sClawShadowNear = NULL;
    sClawShadowFar = NULL;
    sDust = NULL;
    sPulse = NULL;
}

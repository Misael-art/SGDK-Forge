#include <genesis.h>

#include "gameplay/chase_player.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"

#define CHASE_PLAYER_FRAME_TICK_TABLE_SIZE 4
#define CHASE_PLAYER_GROUND_Y 136

static const s16 CHASE_PLAYER_LANE_X[3] = { 80, 128, 176 };
static const u8 CHASE_PLAYER_FRAME_TICKS[CHASE_PLAYER_FRAME_TICK_TABLE_SIZE] = { 4, 3, 4, 3 };

static Sprite* sPlayer;
static Sprite* sPlayerShadow;
static Sprite* sGhostNear;
static Sprite* sGhostFar;
static s16 sPlayerX;
static s16 sJumpOffset;
static s16 sJumpVelocity;
static s16 sGhostX[2];
static s16 sGhostY[2];
static u16 sFrame;
static u16 sFrameTick;
static u16 sAfterimageFrames;
static u8 sFrameCount;
static u8 sLane;
static u8 sTargetLane;
static u8 sShadowFrame;

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

static void chasePlayerSetGhostVisibility(bool visible)
{
    if (sGhostNear != NULL) {
        SPR_setVisibility(sGhostNear, visible ? VISIBLE : HIDDEN);
    }
    if (sGhostFar != NULL) {
        SPR_setVisibility(sGhostFar, visible ? VISIBLE : HIDDEN);
    }
}

void CHASE_PLAYER_enter(void)
{
    sLane = 1;
    sTargetLane = 1;
    sPlayerX = CHASE_PLAYER_LANE_X[sLane];
    sJumpOffset = 0;
    sJumpVelocity = 0;
    sFrame = 0;
    sFrameTick = 0;
    sAfterimageFrames = 0;
    sFrameCount = chaseSpriteDefinitionFrameCount(&spr_chase_hero_run_v009);
    sShadowFrame = 2;
    sGhostX[0] = sPlayerX;
    sGhostX[1] = sPlayerX;
    sGhostY[0] = CHASE_PLAYER_GROUND_Y;
    sGhostY[1] = CHASE_PLAYER_GROUND_Y;

    sPlayer = SPR_addSprite(
        &spr_chase_hero_run_v009,
        sPlayerX,
        CHASE_PLAYER_GROUND_Y,
        TILE_ATTR(PAL1, TRUE, FALSE, FALSE)
    );
    sPlayerShadow = SPR_addSprite(
        &spr_chase_contact_shadow_v011,
        sPlayerX + 24,
        CHASE_PLAYER_GROUND_Y + 72,
        TILE_ATTR(PAL3, TRUE, FALSE, FALSE)
    );
    sGhostNear = SPR_addSprite(&spr_chase_hero_ghost_v009, sPlayerX, CHASE_PLAYER_GROUND_Y, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
    sGhostFar = NULL;
    if (sPlayer != NULL) {
        SPR_setAutoAnimation(sPlayer, FALSE);
        SPR_setFrame(sPlayer, 0);
        SPR_setAlwaysOnTop(sPlayer);
    }
    if (sPlayerShadow != NULL) {
        SPR_setAutoAnimation(sPlayerShadow, FALSE);
        SPR_setFrame(sPlayerShadow, sShadowFrame);
        SPR_setAlwaysAtBottom(sPlayerShadow);
    }
    if (sGhostNear != NULL) {
        const u16 sharedGhostTileIndex = sGhostNear->attribut & TILE_INDEX_MASK;
        SPR_setAutoAnimation(sGhostNear, FALSE);
        SPR_setFrame(sGhostNear, 0);
        SPR_setAlwaysAtBottom(sGhostNear);
        sGhostFar = SPR_addSpriteEx(
            &spr_chase_hero_ghost_v009,
            sPlayerX,
            CHASE_PLAYER_GROUND_Y,
            TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, sharedGhostTileIndex),
            0
        );
    }
    if (sGhostFar != NULL) {
        SPR_setAutoAnimation(sGhostFar, FALSE);
        SPR_setFrame(sGhostFar, 0);
        SPR_setAlwaysAtBottom(sGhostFar);
    }
    chasePlayerSetGhostVisibility(FALSE);
}

void CHASE_PLAYER_update(bool controlEnabled, bool allowAnimationUpload)
{
    s16 targetX;
    s16 playerY;
    bool showAfterimage;

    sGhostX[1] = sGhostX[0];
    sGhostY[1] = sGhostY[0];
    sGhostX[0] = sPlayerX;
    sGhostY[0] = CHASE_PLAYER_GROUND_Y + sJumpOffset;

    if (controlEnabled) {
        if (INPUT_pressed(BUTTON_LEFT) && sTargetLane > 0) {
            sTargetLane--;
        } else if (INPUT_pressed(BUTTON_RIGHT) && sTargetLane < 2) {
            sTargetLane++;
        }

        if (INPUT_pressed(BUTTON_A) && sJumpOffset == 0) {
            sJumpVelocity = -9;
            AUDIO_playCue(AUDIO_CUE_JUMP);
        }
    }

    targetX = CHASE_PLAYER_LANE_X[sTargetLane];
    if (sPlayerX < targetX) {
        sPlayerX += 4;
        if (sPlayerX > targetX) sPlayerX = targetX;
    } else if (sPlayerX > targetX) {
        sPlayerX -= 4;
        if (sPlayerX < targetX) sPlayerX = targetX;
    }
    if (sPlayerX == targetX) {
        sLane = sTargetLane;
    }

    if (sJumpOffset != 0 || sJumpVelocity != 0) {
        sJumpOffset += sJumpVelocity;
        sJumpVelocity++;
        if (sJumpOffset >= 0) {
            sJumpOffset = 0;
            sJumpVelocity = 0;
            AUDIO_playCue(AUDIO_CUE_LAND);
        }
    }

    playerY = CHASE_PLAYER_GROUND_Y + sJumpOffset;
    if (sPlayer != NULL) {
        SPR_setPosition(sPlayer, sPlayerX, playerY);
    }
    if (sPlayerShadow != NULL) {
        u8 targetShadowFrame = 2;
        if (sJumpOffset < -32) {
            targetShadowFrame = 0;
        } else if (sJumpOffset < -8) {
            targetShadowFrame = 1;
        }
        SPR_setPosition(sPlayerShadow, sPlayerX + 24, CHASE_PLAYER_GROUND_Y + 72);
        if (sShadowFrame != targetShadowFrame) {
            sShadowFrame = targetShadowFrame;
            SPR_setFrame(sPlayerShadow, sShadowFrame);
        }
    }
    if (sGhostNear != NULL) {
        SPR_setPosition(sGhostNear, sGhostX[0] - 2, sGhostY[0] + 2);
    }
    if (sGhostFar != NULL) {
        SPR_setPosition(sGhostFar, sGhostX[1] - 5, sGhostY[1] + 4);
    }

    showAfterimage = sAfterimageFrames > 0 || sPlayerX != targetX || sJumpOffset != 0;
    chasePlayerSetGhostVisibility(showAfterimage);
    if (sAfterimageFrames > 0) {
        sAfterimageFrames--;
    }

    sFrameTick++;
    if (allowAnimationUpload && sFrameTick >= chaseTickForFrame(CHASE_PLAYER_FRAME_TICKS, CHASE_PLAYER_FRAME_TICK_TABLE_SIZE, sFrame, 4)) {
        sFrameTick = 0;
        sFrame++;
        if (sFrame >= sFrameCount) {
            sFrame = 0;
        }
        if (sPlayer != NULL) {
            SPR_setFrame(sPlayer, sFrame);
        }
    }
}

void CHASE_PLAYER_triggerAfterimage(u16 frames)
{
    if (frames > sAfterimageFrames) {
        sAfterimageFrames = frames;
    }
}

void CHASE_PLAYER_exit(void)
{
    sPlayer = NULL;
    sPlayerShadow = NULL;
    sGhostNear = NULL;
    sGhostFar = NULL;
}

void CHASE_PLAYER_setVisible(bool visible)
{
    if (sPlayer != NULL) {
        SPR_setVisibility(sPlayer, visible ? VISIBLE : HIDDEN);
    }
    if (sPlayerShadow != NULL) {
        SPR_setVisibility(sPlayerShadow, visible ? VISIBLE : HIDDEN);
    }
    if (!visible) {
        chasePlayerSetGhostVisibility(FALSE);
    }
}

u8 CHASE_PLAYER_lane(void)
{
    return sLane;
}

bool CHASE_PLAYER_isAirborne(void)
{
    return sJumpOffset < -12;
}

s16 CHASE_PLAYER_x(void)
{
    return sPlayerX;
}

s16 CHASE_PLAYER_y(void)
{
    return CHASE_PLAYER_GROUND_Y + sJumpOffset;
}

#include <genesis.h>

#include "gameplay/chase_obstacles.h"
#include "gameplay/chase_player.h"
#include "resources.h"

#define CHASE_OBSTACLE_POOL_SIZE 3
#define CHASE_PICKUP_FRAME_COUNT 4
#define CHASE_OBSTACLE_DEPTH_STAGE_COUNT 16
#define CHASE_OBSTACLE_CONTACT_Z_MIN 208
#define CHASE_OBSTACLE_CONTACT_Z_MAX 240
#define CHASE_OBSTACLE_DESPAWN_Z 255

typedef enum ChaseObstacleKind {
    CHASE_OBSTACLE_BOULDER = 0,
    CHASE_OBSTACLE_BRAND,
    CHASE_OBSTACLE_PICKUP
} ChaseObstacleKind;

typedef struct ChaseObstacleSlot {
    Sprite* sprite;
    Sprite* shadow;
    ChaseObstacleKind kind;
    u16 obstacleZ;
    u16 telegraphFrames;
    u8 lane;
    u8 zSpeed;
    u8 scaleFrame;
    u8 shadowFrame;
    bool active;
} ChaseObstacleSlot;

static const s16 CHASE_OBSTACLE_DEPTH_Y[CHASE_OBSTACLE_DEPTH_STAGE_COUNT] = {
    48, 50, 53, 56, 60, 65, 71, 78,
    86, 95, 105, 116, 128, 141, 155, 170
};
static const s16 CHASE_OBSTACLE_LANE_SPREAD[CHASE_OBSTACLE_DEPTH_STAGE_COUNT] = {
    4, 6, 8, 10, 13, 16, 20, 24,
    28, 32, 36, 40, 43, 45, 47, 48
};
static const s8 CHASE_OBSTACLE_BOUNCE_Y[CHASE_OBSTACLE_DEPTH_STAGE_COUNT] = {
    0, -1, -2, -3, -4, -3, -2, -1,
    0, 1, 2, 1, 0, -1, 0, 1
};
static const s8 CHASE_OBSTACLE_RICOCHET_X[CHASE_OBSTACLE_DEPTH_STAGE_COUNT] = {
    0, 1, 2, 3, 2, 1, 0, -1,
    -2, -3, -2, -1, 0, 1, 0, -1
};
static const u8 CHASE_OBSTACLE_SCALE_FRAME[CHASE_OBSTACLE_DEPTH_STAGE_COUNT] = {
    0, 0, 0, 0, 0, 1, 1, 1,
    1, 2, 2, 2, 2, 3, 3, 3
};
static ChaseObstacleSlot sSlots[CHASE_OBSTACLE_POOL_SIZE];
static u16 sHazardTimer;
static u16 sPickupTimer;
static u16 sPickupAnimTick;
static u8 sLaneSequence;
static u8 sKindSequence;
static u8 sPickupAnimFrame;

static u8 chaseObstacleDepthIndex(const ChaseObstacleSlot* slot)
{
    u16 index = slot->obstacleZ >> 4;
    if (index >= CHASE_OBSTACLE_DEPTH_STAGE_COUNT) {
        index = CHASE_OBSTACLE_DEPTH_STAGE_COUNT - 1;
    }
    return (u8) index;
}

static s16 chaseObstacleLaneX(const ChaseObstacleSlot* slot, u8 depthIndex)
{
    s16 x = 128;
    if (slot->lane == 0) {
        x -= CHASE_OBSTACLE_LANE_SPREAD[depthIndex];
    } else if (slot->lane == 2) {
        x += CHASE_OBSTACLE_LANE_SPREAD[depthIndex];
    }
    if (slot->kind == CHASE_OBSTACLE_PICKUP) {
        x += 16;
    } else if (slot->kind == CHASE_OBSTACLE_BRAND) {
        x += CHASE_OBSTACLE_RICOCHET_X[depthIndex];
    }
    return x;
}

static s16 chaseObstacleY(const ChaseObstacleSlot* slot, u8 depthIndex)
{
    s16 y = CHASE_OBSTACLE_DEPTH_Y[depthIndex];
    if (slot->kind == CHASE_OBSTACLE_PICKUP) {
        y += 16;
    } else {
        y += CHASE_OBSTACLE_BOUNCE_Y[depthIndex];
    }
    return y;
}

static void chaseObstacleHide(ChaseObstacleSlot* slot)
{
    slot->active = FALSE;
    slot->telegraphFrames = 0;
    if (slot->sprite != NULL) {
        SPR_setVisibility(slot->sprite, HIDDEN);
    }
    if (slot->shadow != NULL) {
        SPR_setVisibility(slot->shadow, HIDDEN);
    }
}

static ChaseObstacleSlot* chaseObstacleFind(ChaseObstacleKind kind)
{
    u16 i;
    for (i = 0; i < CHASE_OBSTACLE_POOL_SIZE; i++) {
        if (!sSlots[i].active && sSlots[i].kind == kind) {
            return &sSlots[i];
        }
    }
    return NULL;
}

static u16 chaseObstacleActiveHazards(void)
{
    u16 i;
    u16 count = 0;
    for (i = 0; i < CHASE_OBSTACLE_POOL_SIZE; i++) {
        if (sSlots[i].active && sSlots[i].kind != CHASE_OBSTACLE_PICKUP) {
            count++;
        }
    }
    return count;
}

static void chaseObstacleSpawn(ChaseObstacleKind kind, u8 lane, u8 zSpeed, u16 telegraphFrames)
{
    ChaseObstacleSlot* slot = chaseObstacleFind(kind);
    u8 depthIndex;

    if (slot == NULL) {
        return;
    }

    slot->active = TRUE;
    slot->lane = lane;
    slot->zSpeed = zSpeed;
    slot->telegraphFrames = telegraphFrames;
    slot->obstacleZ = 0;
    slot->scaleFrame = 0;
    slot->shadowFrame = 0;
    depthIndex = chaseObstacleDepthIndex(slot);

    if (slot->sprite != NULL) {
        SPR_setFrame(slot->sprite, (kind == CHASE_OBSTACLE_PICKUP) ? sPickupAnimFrame : 0);
        SPR_setHFlip(slot->sprite, FALSE);
        SPR_setPosition(slot->sprite, chaseObstacleLaneX(slot, depthIndex), chaseObstacleY(slot, depthIndex));
        SPR_setVisibility(slot->sprite, VISIBLE);
    }
    if (slot->shadow != NULL) {
        SPR_setFrame(slot->shadow, 0);
        SPR_setPosition(
            slot->shadow,
            chaseObstacleLaneX(slot, depthIndex) + 24,
            chaseObstacleY(slot, depthIndex) + 42
        );
        SPR_setVisibility(slot->shadow, VISIBLE);
    }
}

void CHASE_OBSTACLES_enter(void)
{
    u16 i;

    for (i = 0; i < CHASE_OBSTACLE_POOL_SIZE; i++) {
        sSlots[i].active = FALSE;
        sSlots[i].lane = 0;
        sSlots[i].obstacleZ = 0;
        sSlots[i].telegraphFrames = 0;
        sSlots[i].zSpeed = 0;
        sSlots[i].scaleFrame = 0;
        sSlots[i].shadowFrame = 0;

        if ((i % 3) == 0) {
            sSlots[i].kind = CHASE_OBSTACLE_BOULDER;
            sSlots[i].sprite = SPR_addSprite(&spr_chase_obstacle_boulder_v011, -96, -96, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
        } else if ((i % 3) == 1) {
            sSlots[i].kind = CHASE_OBSTACLE_BRAND;
            sSlots[i].sprite = SPR_addSprite(&spr_chase_obstacle_brand_v011, -96, -96, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
        } else {
            sSlots[i].kind = CHASE_OBSTACLE_PICKUP;
            sSlots[i].sprite = SPR_addSprite(&spr_chase_energy_star_v009, -96, -96, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
        }

        if (sSlots[i].sprite != NULL) {
            SPR_setAutoAnimation(sSlots[i].sprite, FALSE);
            SPR_setFrame(sSlots[i].sprite, 0);
            SPR_setVisibility(sSlots[i].sprite, HIDDEN);
        }

        sSlots[i].shadow = NULL;
        if (sSlots[i].kind != CHASE_OBSTACLE_PICKUP) {
            sSlots[i].shadow = SPR_addSprite(
                &spr_chase_contact_shadow_v011,
                -96,
                -96,
                TILE_ATTR(PAL3, TRUE, FALSE, FALSE)
            );
        }
        if (sSlots[i].shadow != NULL) {
            SPR_setAutoAnimation(sSlots[i].shadow, FALSE);
            SPR_setFrame(sSlots[i].shadow, 0);
            SPR_setAlwaysAtBottom(sSlots[i].shadow);
            SPR_setVisibility(sSlots[i].shadow, HIDDEN);
        }
    }

    sHazardTimer = 60;
    sPickupTimer = 240;
    sPickupAnimTick = 0;
    sPickupAnimFrame = 0;
    sLaneSequence = 0;
    sKindSequence = 0;
}

ChaseObstacleEvents CHASE_OBSTACLES_update(const ChaseRulesState* rules, bool allowScaleUpload)
{
    ChaseObstacleEvents events = { FALSE, FALSE };
    u16 i;
    u16 hazardInterval;
    u8 zSpeed;
    bool scaleUploadConsumed = FALSE;

    if (!CHASE_RULES_isPlaying(rules)) {
        return events;
    }

    if (rules->flow == CHASE_FLOW_INTRO) {
        hazardInterval = 105;
        zSpeed = 2;
    } else if (rules->flow == CHASE_FLOW_PRESSURE) {
        hazardInterval = 82;
        zSpeed = 3;
    } else {
        hazardInterval = 64;
        zSpeed = 4;
    }

    if (sHazardTimer > 0) sHazardTimer--;
    if (sPickupTimer > 0) sPickupTimer--;
    sPickupAnimTick++;
    if (sPickupAnimTick >= 6) {
        sPickupAnimTick = 0;
        sPickupAnimFrame = (sPickupAnimFrame + 1) % CHASE_PICKUP_FRAME_COUNT;
    }

    if (sHazardTimer == 0 && chaseObstacleActiveHazards() < 2) {
        chaseObstacleSpawn(
            (sKindSequence & 1) ? CHASE_OBSTACLE_BRAND : CHASE_OBSTACLE_BOULDER,
            sLaneSequence % 3,
            zSpeed,
            28
        );
        sKindSequence++;
        sLaneSequence += 2;
        sHazardTimer = hazardInterval;
    }

    if (sPickupTimer == 0) {
        chaseObstacleSpawn(CHASE_OBSTACLE_PICKUP, (sLaneSequence + 1) % 3, 2, 0);
        sPickupTimer = rules->targetFps * 6u;
    }

    for (i = 0; i < CHASE_OBSTACLE_POOL_SIZE; i++) {
        ChaseObstacleSlot* slot = &sSlots[i];
        u8 depthIndex;
        u8 targetScaleFrame;
        s16 x;
        s16 y;

        if (!slot->active) {
            continue;
        }

        if (slot->telegraphFrames > 0) {
            slot->telegraphFrames--;
            if (slot->sprite != NULL) {
                SPR_setVisibility(slot->sprite, ((slot->telegraphFrames >> 2) & 1) ? HIDDEN : VISIBLE);
            }
            if (slot->shadow != NULL) {
                SPR_setVisibility(slot->shadow, ((slot->telegraphFrames >> 2) & 1) ? HIDDEN : VISIBLE);
            }
            continue;
        }

        slot->obstacleZ += slot->zSpeed;
        if (slot->obstacleZ > CHASE_OBSTACLE_DESPAWN_Z) {
            slot->obstacleZ = CHASE_OBSTACLE_DESPAWN_Z;
        }
        depthIndex = chaseObstacleDepthIndex(slot);
        targetScaleFrame = CHASE_OBSTACLE_SCALE_FRAME[depthIndex];
        x = chaseObstacleLaneX(slot, depthIndex);
        y = chaseObstacleY(slot, depthIndex);
        if (slot->sprite != NULL) {
            SPR_setVisibility(slot->sprite, VISIBLE);
            SPR_setPosition(slot->sprite, x, y);
            if (slot->kind == CHASE_OBSTACLE_PICKUP && sPickupAnimTick == 0) {
                SPR_setFrame(slot->sprite, sPickupAnimFrame);
            } else if (
                slot->kind != CHASE_OBSTACLE_PICKUP
                && slot->scaleFrame != targetScaleFrame
                && allowScaleUpload
                && !scaleUploadConsumed
            ) {
                slot->scaleFrame = targetScaleFrame;
                SPR_setFrame(slot->sprite, slot->scaleFrame);
                scaleUploadConsumed = TRUE;
            }
            if (slot->kind != CHASE_OBSTACLE_PICKUP) {
                SPR_setHFlip(slot->sprite, ((slot->obstacleZ >> 3) & 1u) != 0);
            }
        }
        if (slot->shadow != NULL) {
            u8 targetShadowFrame = targetScaleFrame;
            if (targetShadowFrame > 2) {
                targetShadowFrame = 2;
            }
            SPR_setPosition(slot->shadow, x + 24, y + 42);
            SPR_setVisibility(slot->shadow, VISIBLE);
            if (slot->shadowFrame != targetShadowFrame) {
                slot->shadowFrame = targetShadowFrame;
                SPR_setFrame(slot->shadow, slot->shadowFrame);
            }
        }

        if (
            slot->obstacleZ >= CHASE_OBSTACLE_CONTACT_Z_MIN
            && slot->obstacleZ <= CHASE_OBSTACLE_CONTACT_Z_MAX
            && slot->lane == CHASE_PLAYER_lane()
        ) {
            if (slot->kind == CHASE_OBSTACLE_PICKUP) {
                events.pickup = TRUE;
                chaseObstacleHide(slot);
            } else if (!CHASE_PLAYER_isAirborne()) {
                events.damage = TRUE;
                chaseObstacleHide(slot);
            }
        } else if (slot->obstacleZ >= CHASE_OBSTACLE_DESPAWN_Z) {
            chaseObstacleHide(slot);
        }
    }

    return events;
}

void CHASE_OBSTACLES_clearThreats(void)
{
    u16 i;
    for (i = 0; i < CHASE_OBSTACLE_POOL_SIZE; i++) {
        chaseObstacleHide(&sSlots[i]);
    }
}

void CHASE_OBSTACLES_exit(void)
{
    u16 i;
    for (i = 0; i < CHASE_OBSTACLE_POOL_SIZE; i++) {
        sSlots[i].sprite = NULL;
        sSlots[i].shadow = NULL;
        sSlots[i].active = FALSE;
    }
}

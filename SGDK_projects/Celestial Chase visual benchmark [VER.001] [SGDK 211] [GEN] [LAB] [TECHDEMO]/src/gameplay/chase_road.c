#include <genesis.h>

#include "gameplay/chase_road.h"
#include "resources.h"

#define CHASE_ROAD_LINES 224
#define CHASE_ROAD_COLUMNS 20
#define CHASE_ROAD_HORIZON 88
#define CHASE_ROAD_CLIMAX_Y 26
#define CHASE_ROAD_BASE_HSCROLL -96
#define CHASE_SKY_ZONE_END 96
#define CHASE_CLOUD_ZONE_END 144

static s16 sBgALineScroll[CHASE_ROAD_LINES];
static s16 sBgBLineScroll[CHASE_ROAD_LINES];
static s16 sBgAColumnScroll[CHASE_ROAD_COLUMNS];
static s16 sBgBColumnScroll[CHASE_ROAD_COLUMNS];
static Sprite* sCloudNear;
static Sprite* sCloudFar;
static u16 sLetterboxTileIndex;
static s16 sCloudNearX;
static s16 sCloudNearY;
static s16 sCloudFarX;
static s16 sCloudFarY;
static bool sClimax;

static s16 chaseRoadTriangle(u16 phase)
{
    u16 normalized = phase & 63u;
    if (normalized < 32u) {
        return (s16) normalized - 16;
    }
    return 48 - (s16) normalized;
}

static void chaseRoadDrawClimaxBar(bool active)
{
    const u16 planeWidth = VDP_getPlaneWidth();
    const u16 firstRow = CHASE_ROAD_CLIMAX_Y * planeWidth;

    if (active) {
        const u16 tile = TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, sLetterboxTileIndex);
        VDP_fillTileMap(VDP_BG_A, tile, firstRow, planeWidth);
        VDP_fillTileMap(VDP_BG_A, tile, firstRow + planeWidth, planeWidth);
    } else {
        VDP_clearTileMap(VDP_BG_A, firstRow, planeWidth, TRUE);
        VDP_clearTileMap(VDP_BG_A, firstRow + planeWidth, planeWidth, TRUE);
    }
}

static void chaseRoadUpdateClouds(bool advance, s16 shakeX, s16 shakeY)
{
    if (advance) {
        sCloudNearX -= 1;
        sCloudNearY += 1;
        if (sCloudNearX < -72 || sCloudNearY > 102) {
            sCloudNearX = 304;
            sCloudNearY = 34;
        }

        if ((sCloudNearX & 1) == 0) {
            sCloudFarX += 1;
        }
        if ((sCloudNearY & 3) == 0) {
            sCloudFarY += 1;
        }
        if (sCloudFarX > 328 || sCloudFarY > 82) {
            sCloudFarX = -68;
            sCloudFarY = 18;
        }
    }

    if (sCloudNear != NULL) {
        SPR_setPosition(sCloudNear, sCloudNearX + (shakeX >> 1), sCloudNearY + (shakeY >> 1));
    }
    if (sCloudFar != NULL) {
        SPR_setPosition(sCloudFar, sCloudFarX + (shakeX >> 2), sCloudFarY + (shakeY >> 2));
    }
}

void CHASE_ROAD_enter(u16 letterboxTileIndex)
{
    sLetterboxTileIndex = letterboxTileIndex;
    sClimax = FALSE;
    sCloudNearX = 272;
    sCloudNearY = 38;
    sCloudFarX = -52;
    sCloudFarY = 18;

    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_COLUMN);

    sCloudNear = SPR_addSprite(&spr_chase_cloud_v009, sCloudNearX, sCloudNearY, TILE_ATTR(PAL0, FALSE, FALSE, FALSE));
    sCloudFar = NULL;
    if (sCloudNear != NULL) {
        const u16 sharedCloudTileIndex = sCloudNear->attribut & TILE_INDEX_MASK;
        SPR_setAutoAnimation(sCloudNear, FALSE);
        SPR_setFrame(sCloudNear, 0);
        SPR_setAlwaysAtBottom(sCloudNear);
        sCloudFar = SPR_addSpriteEx(
            &spr_chase_cloud_v009,
            sCloudFarX,
            sCloudFarY,
            TILE_ATTR_FULL(PAL0, FALSE, FALSE, TRUE, sharedCloudTileIndex),
            0
        );
    }
    if (sCloudFar != NULL) {
        SPR_setAutoAnimation(sCloudFar, FALSE);
        SPR_setFrame(sCloudFar, 0);
        SPR_setAlwaysAtBottom(sCloudFar);
        SPR_setVisibility(sCloudFar, VISIBLE);
    }
}

void CHASE_ROAD_update(u32 frame, u8 phase, s16 shakeX, s16 shakeY, bool advance)
{
    u16 line;
    u16 column;
    s16 curve = chaseRoadTriangle((u16)(frame >> 2));
    s16 roadBeat = (s16)((frame >> 1) & 15u);
    s32 bendNumerator = 0;
    s32 bendDelta = curve;
    s32 streakNumerator = 0;
    s16 bendAcceleration = curve << 1;
    s16 streakStep = roadBeat * phase;

    chaseRoadUpdateClouds(advance, shakeX, shakeY);
    if (advance && (frame & 1u) != 0 && shakeX == 0 && shakeY == 0) {
        return;
    }

    for (line = 0; line < CHASE_ROAD_LINES; line++) {
        if (line < CHASE_ROAD_HORIZON) {
            sBgALineScroll[line] = CHASE_ROAD_BASE_HSCROLL + shakeX;
        } else {
            s16 bend = (s16)(bendNumerator >> 14);
            s16 streak = (s16)(streakNumerator >> 8);
            sBgALineScroll[line] = CHASE_ROAD_BASE_HSCROLL + bend - streak + shakeX;
            bendNumerator += bendDelta;
            bendDelta += bendAcceleration;
            streakNumerator += streakStep;
        }
        if (line < CHASE_SKY_ZONE_END) {
            sBgBLineScroll[line] = CHASE_ROAD_BASE_HSCROLL + (shakeX >> 2);
        } else if (line < CHASE_CLOUD_ZONE_END) {
            sBgBLineScroll[line] = CHASE_ROAD_BASE_HSCROLL + (curve >> 3) + (shakeX >> 2);
        } else {
            sBgBLineScroll[line] = CHASE_ROAD_BASE_HSCROLL - (curve >> 2) + (shakeX >> 2);
        }
    }

    for (column = 0; column < CHASE_ROAD_COLUMNS; column++) {
        sBgAColumnScroll[column] = (s16)(-((roadBeat * phase) >> 2) + shakeY);
        sBgBColumnScroll[column] = shakeY >> 2;
    }

    VDP_setHorizontalScrollLine(BG_A, 0, sBgALineScroll, CHASE_ROAD_LINES, DMA_QUEUE);
    VDP_setHorizontalScrollLine(BG_B, 0, sBgBLineScroll, CHASE_ROAD_LINES, DMA_QUEUE);
    VDP_setVerticalScrollTile(BG_A, 0, sBgAColumnScroll, CHASE_ROAD_COLUMNS, DMA_QUEUE);
    VDP_setVerticalScrollTile(BG_B, 0, sBgBColumnScroll, CHASE_ROAD_COLUMNS, DMA_QUEUE);
}

void CHASE_ROAD_setClimax(bool active)
{
    if (sClimax == active) {
        return;
    }

    sClimax = active;
    chaseRoadDrawClimaxBar(active);
}

void CHASE_ROAD_exit(void)
{
    chaseRoadDrawClimaxBar(FALSE);
    sCloudNear = NULL;
    sCloudFar = NULL;
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
}

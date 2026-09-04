#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/scene_native_art_review.h"
#include "system/input.h"

/*
 * This is deliberately a review scene, not a gameplay replacement.  It owns
 * one runtime-review SPRITE resource and three non-authoritative backdrop modes
 * so the 32x32 read can be judged in context. This scene is a review candidate,
 * not a visual acceptance gate.
 */
typedef enum NativeReviewBackground {
    NATIVE_REVIEW_BG_CONTEXT = 0,
    NATIVE_REVIEW_BG_CLEAR = 1,
    NATIVE_REVIEW_BG_DARK = 2
} NativeReviewBackground;

static Sprite* s_idleSprite;
static u16 s_tileNext;
static u16 s_reviewFrame;
static u16 s_reviewTimer;
static NativeReviewBackground s_background;

static void SCENE_nativeArtReviewDrawContext(void)
{
    PAL_setPalette(PAL0, img_ph_sky.palette->data, DMA);
    PAL_setPalette(PAL1, img_ph_terrain.palette->data, DMA);
    PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);

    /* The placeholder sky uses index 0 as transparent; give empty cells a
     * deliberate cool backdrop so the review never presents chroma-key pink
     * as if it were scene art. */
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x224466));
    VDP_setBackgroundColor(0);
    VDP_drawImageEx(BG_B, &img_ph_sky,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 0, FALSE, TRUE);
    s_tileNext += img_ph_sky.tileset->numTile;
    VDP_drawImageEx(BG_B, &img_ph_mount,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 8, FALSE, TRUE);
    s_tileNext += img_ph_mount.tileset->numTile;
    VDP_drawImageEx(BG_B, &img_ph_hills,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 15, FALSE, TRUE);
    s_tileNext += img_ph_hills.tileset->numTile;
    VDP_drawImageEx(BG_A, &img_ph_terrain,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, s_tileNext),
                    0, 22, FALSE, TRUE);
}

static void SCENE_nativeArtReviewDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    s_tileNext = TILE_USER_INDEX;

    if (s_background == NATIVE_REVIEW_BG_CONTEXT)
    {
        SCENE_nativeArtReviewDrawContext();
    }
    else
    {
        PAL_setColor(0, (s_background == NATIVE_REVIEW_BG_CLEAR)
                         ? RGB24_TO_VDPCOLOR(0xEEEEEE)
                         : RGB24_TO_VDPCOLOR(0x000022));
        PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);
        PAL_setPalette(PAL3, palette_grey, DMA);
        VDP_setBackgroundColor(0);
    }

    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL3);
    VDP_drawText("V10 VISUAL REVIEW", 11, 1);
    VDP_drawText("A/B: BACKGROUND   START: TITLE", 5, 26);
}

void SCENE_nativeArtReviewEnter(void)
{
    SPR_reset();
    SPR_update();
    s_background = NATIVE_REVIEW_BG_CONTEXT;
    s_reviewFrame = 0u;
    s_reviewTimer = 0u;
    SCENE_nativeArtReviewDraw();

    /* Position is top-left; pivot contract remains (16,31), baseline y=30. */
    s_idleSprite = SPR_addSprite(&spr_ph_kirby, 144, 96,
                                 TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    SPR_setFrame(s_idleSprite, s_reviewFrame);
}

void SCENE_nativeArtReviewUpdate(void)
{
    if (INPUT_pressed(BUTTON_A))
    {
        s_background = (NativeReviewBackground)
            (((u8) s_background + 1u) % 3u);
        SPR_reset();
        SPR_update();
        SCENE_nativeArtReviewDraw();
        s_idleSprite = SPR_addSprite(&spr_ph_kirby, 144, 96,
                                     TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
        SPR_setFrame(s_idleSprite, s_reviewFrame);
    }
    else if (INPUT_pressed(BUTTON_B))
    {
        s_background = (s_background == NATIVE_REVIEW_BG_CONTEXT)
            ? NATIVE_REVIEW_BG_DARK
            : (NativeReviewBackground) ((u8) s_background - 1u);
        SPR_reset();
        SPR_update();
        SCENE_nativeArtReviewDraw();
        s_idleSprite = SPR_addSprite(&spr_native_idle_elite, 144, 96,
                                     TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    }

    s_reviewTimer++;
    if (s_reviewTimer >= 8u)
    {
        s_reviewTimer = 0u;
        s_reviewFrame = (s_reviewFrame + 1u) % 16u;
        SPR_setFrame(s_idleSprite, s_reviewFrame);
    }

    if (INPUT_pressed(BUTTON_START))
    {
        APP_changeScene(APP_SCENE_TITLE);
    }
}

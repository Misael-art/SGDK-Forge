#include <genesis.h>

#include "audio/xgm_router.h"
#include "core/app.h"
#include "resources.h"
#include "scenes/scene_title.h"
#include "system/input.h"
#include "system/probe_stage.h"
#include "systems/raster.h"

/*
 * Title screen. Design brief: doc/art/AI_IMAGE_PROMPT_PACK.md request R1-07.
 *
 * This is the last piece of the literal FASE 1 criterion from the project brief
 * (title -> stage -> boss -> game over/continue), and it also RETIRES the
 * template's branding/menu/demo scenes, which are where the 11 baselined audio
 * violations live.
 *
 * Shadow/Highlight is OFF here, same as the game over screen and for the same
 * reason: this scene has no effect that needs pseudo-transparency, and the SGDK
 * font does not coexist with global S/H without special handling.
 *
 * Two attempts before this one, both recorded because they cost a capture each:
 *   1. text on the WINDOW plane -- never appeared. The window has no size until
 *      VDP_setWindowVPos is called, so the draw went nowhere.
 *   2. text on BG_A with VDP_setTextPriority(TRUE) -- rendered as a solid grey
 *      block instead of glyphs.
 * doc/PALETTES.md 2.2 locks S/H on for GAMEPLAY scenes because the inhale vortex
 * needs it. A title screen has no such need, so turning it off is the cheap and
 * correct answer rather than fighting the font.
 */

#define TITLE_STAR_DRIFT_PERIOD 4u   /* frames per 1px of star drift */

static u16 s_tileNext;
static u16 s_frames;
static s16 s_starScroll;

void SCENE_titleEnter(void)
{
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    s_tileNext = TILE_USER_INDEX;
    s_frames = 0u;
    s_starScroll = 0;

    PAL_setPalette(PAL0, img_ph_title_hill.palette->data, DMA);
    PAL_setPalette(PAL1, img_ph_title_logo.palette->data, DMA);
    PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);

    /* Stars on BG_B so they can drift independently of the foreground hill. */
    VDP_drawImageEx(BG_B, &img_ph_title_stars,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 2, FALSE, TRUE);
    s_tileNext += img_ph_title_stars.tileset->numTile;

    VDP_drawImageEx(BG_A, &img_ph_title_hill,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 20, FALSE, TRUE);
    s_tileNext += img_ph_title_hill.tileset->numTile;

    /* Logo in the upper third, the space the art brief reserved for it. */
    VDP_drawImageEx(BG_A, &img_ph_title_logo,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, s_tileNext),
                    6, 4, FALSE, TRUE);
    s_tileNext += img_ph_title_logo.tileset->numTile;

    RASTER_setNightSky(TRUE);
    RASTER_initStage();
    RASTER_updateScroll(0);

    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL2);

    VDP_setHilightShadow(FALSE);
    PROBE_STAGE_reset();
    PROBE_STAGE_publishShadowHighlight(FALSE);
    PROBE_STAGE_publishCamera(0);

    VDP_drawText("PRESS START", 14, 24);

    AUDIO_playMusic(mus_stage_valley);
}

void SCENE_titleUpdate(void)
{
    RASTER_frameStart();
    s_frames++;

    /* Slow star drift: the only motion on screen, so the title reads as alive
     * rather than as a still image. One pixel every 4 frames. */
    if ((s_frames % TITLE_STAR_DRIFT_PERIOD) == 0u)
    {
        s_starScroll--;
        VDP_setHorizontalScroll(BG_B, s_starScroll);
    }

    /*
     * The prompt does NOT blink.
     *
     * A blinking prompt is nice, but a static screenshot cannot prove a blink --
     * it can only catch it off, which is indistinguishable from broken. Two
     * captures were spent on exactly that ambiguity. Drawn once in Enter, always
     * visible: the affordance is essential, the animation is not.
     */

    if ((gInput.pressed & (BUTTON_START | BUTTON_A)) != 0)
    {
        RASTER_setNightSky(FALSE);
        /* MISSAO 2026-08-24: o START abre a ABERTURA (intro cinematic), que
         * entrega o MENU. O fluxo canonical do jogo passa a ser
         * TITLE -> INTRO -> MENU -> (HISTORIA | FASES | MINIGAMES). */
        APP_changeScene(APP_SCENE_INTRO);
        return;
    }

    PROBE_STAGE_publishActors(0u, 0, 0, s_frames);
    PROBE_STAGE_tick();
    if ((s_frames % 60u) == 59u) PROBE_STAGE_exportToSram();
}

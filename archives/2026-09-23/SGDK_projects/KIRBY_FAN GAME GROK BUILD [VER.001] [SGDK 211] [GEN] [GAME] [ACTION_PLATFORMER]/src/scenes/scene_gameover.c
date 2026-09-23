#include <genesis.h>

#include "core/app.h"
#include "scenes/scene_gameover.h"
#include "system/input.h"
#include "system/probe_stage.h"
#include "resources.h"
#include "systems/journey.h"
#include "systems/raster.h"

/*
 * Game over / victory, with continue.
 *
 * Shadow/Highlight is DELIBERATELY OFF here. This scene is text on a flat
 * background, and the SGDK font tiles are written at priority 0 -- under global
 * S/H every one of them would render at half brightness and the screen would
 * look broken. doc/PALETTES.md section 2.2 locks S/H on for gameplay scenes
 * because the inhale vortex needs it; a text screen has no such need, so the
 * cheapest correct answer is to turn it off for the duration.
 */

#define GAMEOVER_CONTINUE_SECONDS 9u
#define GAMEOVER_INPUT_LOCK 45u     /* frames before input is accepted */

static GameOutcome s_outcome;
static u16 s_countdown;             /* in frames */
static u16 s_lock;

void SCENE_setOutcome(GameOutcome outcome) { s_outcome = outcome; }

void SCENE_gameoverEnter(void)
{
    u16 tileNext;

    SPR_reset();

    VDP_setHilightShadow(FALSE);
    PROBE_STAGE_publishShadowHighlight(FALSE);

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    /*
     * The world stays on screen behind the message.
     *
     * The first version was a flat colour with text on it, and the canonical
     * screenshot gate rejected the capture as `blank_or_low_information_capture`.
     * It was right: for an AAA target a game over screen that is a void is a
     * real complaint, not a false positive. Keeping the valley visible also says
     * something the void could not -- you failed IN a place.
     */
    tileNext = TILE_USER_INDEX;

    PAL_setPalette(PAL0, img_ph_sky.palette->data, DMA);
    PAL_setPalette(PAL1, img_ph_terrain.palette->data, DMA);
    PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);

    VDP_drawImageEx(BG_B, &img_ph_mount,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, tileNext),
                    0, 8, FALSE, TRUE);
    tileNext += img_ph_mount.tileset->numTile;

    VDP_drawImageEx(BG_B, &img_ph_hills,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, tileNext),
                    0, 15, FALSE, TRUE);
    tileNext += img_ph_hills.tileset->numTile;

    VDP_drawImageEx(BG_A, &img_ph_terrain,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, tileNext),
                    0, 22, FALSE, TRUE);
    tileNext += img_ph_terrain.tileset->numTile;

    /* The sky gradient carries the mood: warm for victory, cold for defeat.
     * RASTER_initStage owns CRAM 0 from here on. */
    RASTER_initStage();
    RASTER_updateScroll(0);

    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL2);

    if (s_outcome == OUTCOME_VICTORY)
    {
        VDP_drawText("WHISPY WOODS DEFEATED", 9, 10);
        VDP_drawText("ROUTE 3 UNLOCKED - GO!", 8, 12);
    }
    else
    {
        /* MISSAO 2026-08-24: o retry devolve ao contexto real (fase atual ou
         * boss), nao mais sempre a fase 1. */
        VDP_drawText("GAME OVER", 15, 10);
    }

    s_countdown = GAMEOVER_CONTINUE_SECONDS * 60u;
    s_lock = GAMEOVER_INPUT_LOCK;

    PROBE_STAGE_reset();
    PROBE_STAGE_publishCamera(0);
}

void SCENE_gameoverUpdate(void)
{
    RASTER_frameStart();

    const u16 seconds = (u16) (s_countdown / 60u);
    char line[24];

    if (s_lock > 0u) s_lock--;

    /* The countdown is redrawn only when the displayed second changes, so this
     * screen does not spend a text blit every frame for nothing. */
    if ((s_countdown % 60u) == 0u)
    {
        strclr(line);
        strcat(line, "CONTINUE?  ");
        intToStr((s32) seconds, line + 11, 1);
        VDP_drawText(line, 14, 15);
        VDP_drawText("PRESS START", 14, 17);
    }

    if (s_countdown > 0u) s_countdown--;

    /* Input is locked briefly so the button that killed you cannot also burn
     * the continue prompt in the same breath. */
    if ((s_lock == 0u) &&
        ((gInput.pressed & (BUTTON_START | BUTTON_A)) != 0))
    {
        /* MISSAO 2026-08-24: vitoria de boss avanca a jornada; derrota repete
         * o contexto atual (fase ou boss). */
        const AppScene next = (s_outcome == OUTCOME_VICTORY)
                              ? JOURNEY_sceneAfterBossVictory()
                              : JOURNEY_retryScene();

        APP_changeScene(next);
        return;
    }

    if (s_countdown == 0u)
    {
        /* Countdown spent: back to the title, which is where a real arcade
         * loop goes. Continue (START/A) is what restarts the stage. */
        APP_changeScene(APP_SCENE_TITLE);
        return;
    }

    PROBE_STAGE_publishActors((u16) s_outcome, 0, 0, seconds);
    PROBE_STAGE_tick();
    if ((gApp.sceneFrames % 60u) == 59u) PROBE_STAGE_exportToSram();
}

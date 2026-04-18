/**
 * MEGABLADE MD
 * An elite-quality Mega Drive action platformer.
 *
 * Architecture:
 *  - FSM game states (Title -> Gameplay -> GameOver -> Title)
 *  - Dual-layer parallax (BGA foreground MAP + BGB background MAP)
 *  - fix32 physics (no float)
 *  - Pre-allocated enemy pool (no runtime malloc)
 *  - XGM2 music + PCM SFX
 *  - Screen shake + palette flash effects
 *  - Sine-wave line scroll on BGB (raster effect)
 *  - Window plane for HUD (no map conflict)
 *
 * Built with SGDK v2.11
 */

#include <genesis.h>

#include "game_config.h"
#include "player.h"
#include "enemy.h"
#include "camera.h"
#include "hud.h"
#include "effects.h"

/* Generated resource headers */
#include "res_gfx.h"
#include "res_sprite.h"
#include "res_sound.h"

/* =========================================================================
 * FSM
 * ========================================================================= */

StateFunction currentStateUpdate = NULL;

void set_state(StateFunction nextState) {
    currentStateUpdate = nextState;
}

/* =========================================================================
 * Maps (BGA = foreground scroll, BGB = slow parallax background)
 * ========================================================================= */
Map* bga;
Map* bgb;

/* =========================================================================
 * VBlank callback — raster effects run here
 * ========================================================================= */
static void vblankCB(void) {
    CAMERA_onVBlank();
}

/* =========================================================================
 * Joy event handler — instant button press (jump etc.)
 * ========================================================================= */
static void joyEvent(u16 joy, u16 changed, u16 state) {
    if (joy != JOY_1) return;
    PLAYER_doJoyEvent(joy, changed, state);
}

/* =========================================================================
 * TITLE STATE
 * ========================================================================= */
static u16 titleTimer = 0;

void state_title_update(void) {
    titleTimer++;

    /* Flash "PRESS START" using timer */
    if ((titleTimer & 32) == 0)
        HUD_showMessage("PRESS START", 14, 14);
    else
        HUD_clearMessage(14, 14, 11);

    u16 pad = JOY_readJoypad(JOY_1);
    if (pad & BUTTON_START) {
        HUD_clearMessage(14, 14, 11);
        PLAYER_reset();
        ENEMY_spawnAll();
        XGM2_play(stage_music);
        XGM2_fadeIn(30);
        set_state(state_gameplay_update);
        titleTimer = 0;
    }
}

/* =========================================================================
 * GAMEOVER STATE
 * ========================================================================= */
static u16 gameoverTimer = 0;

void state_gameover_update(void) {
    gameoverTimer++;

    if (gameoverTimer == 1) {
        XGM2_fadeOut(60);
        HUD_showMessage("GAME  OVER", 15, 13);
        HUD_showMessage("PRESS START", 14, 15);
    }

    if (gameoverTimer > 120) {
        u16 pad = JOY_readJoypad(JOY_1);
        if (pad & BUTTON_START) {
            HUD_clearMessage(15, 13, 10);
            HUD_clearMessage(14, 15, 11);
            gameoverTimer = 0;
            set_state(state_title_update);
        }
    }
}

/* =========================================================================
 * GAMEPLAY STATE
 * ========================================================================= */
void state_gameplay_update(void) {
    u16 pad = JOY_readJoypad(JOY_1);
    PLAYER_handleInput(pad);

    PLAYER_update();

    /* Camera tracks player position */
    CAMERA_centerOn(F32_toInt(playerPosX), F32_toInt(playerPosY));

    ENEMY_update();

    /* Update sprite screen positions after camera is resolved */
    PLAYER_updateScreenPos();
    ENEMY_updateScreenPos();

    EFFECTS_update();

    /* Scroll BGA (foreground) and BGB (parallax background) */
    MAP_scrollTo(bga, camX + shakeOffsetX, camY + shakeOffsetY);
    MAP_scrollTo(bgb, (camX >> 3) + shakeOffsetX, (camY >> 5) + shakeOffsetY);

    /* Transition to game over when out of lives */
    if (playerLives == 0) {
        gameoverTimer = 0;
        set_state(state_gameover_update);
    }
}

/* =========================================================================
 * INIT
 * ========================================================================= */
static void GAME_init(void) {
    u16 ind = TILE_USER_INDEX;

    /* Expand DMA buffer for bulk loading */
    DMA_setBufferSize(10000);
    DMA_setMaxTransferSize(10000);

    /* Load fg tileset into VRAM */
    VDP_loadTileSet(&fg_tileset, ind, DMA);
    bga = MAP_create(&fg_map, BG_A, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, ind));
    ind += fg_tileset.numTile;

    /* Load bg tileset into VRAM */
    VDP_loadTileSet(&bg_tileset, ind, DMA);
    bgb = MAP_create(&bg_map, BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, ind));
    ind += bg_tileset.numTile;

    /* Restore DMA defaults */
    DMA_setBufferSizeToDefault();
    DMA_setMaxTransferSizeToDefault();

    /* Set all 4 palettes from the fg image palette */
    PAL_setPalette(PAL0, palette_fg.data, CPU);
    PAL_setPalette(PAL1, palette_fg.data, CPU);

    /* Window plane: top 2 tile rows reserved for HUD */
    VDP_setWindowVPos(FALSE, 2);

    /* Init subsystems */
    CAMERA_init();
    EFFECTS_init();
    ind = PLAYER_init(ind);
    ind = ENEMY_init(ind);
    HUD_init();

    /* Scroll both maps to origin */
    MAP_scrollTo(bga, 0, 0);
    MAP_scrollTo(bgb, 0, 0);
}

/* =========================================================================
 * MAIN
 * ========================================================================= */
int main(bool hardReset) {
    u16 palette[64];

    VDP_setScreenWidth320();

    /* Black screen during load */
    PAL_setColors(0, (u16*)palette_black, 64, CPU);

    /* Init sprite engine */
    SPR_init();

    /* Load all game resources and init systems */
    GAME_init();

    /* Set palette and fade in */
    memcpy(&palette[0],  palette_fg.data, 32);  /* PAL0 + PAL1 from fg */
    memcpy(&palette[32], palette_fg.data, 32);  /* PAL2 + PAL3 from fg */
    PAL_fadeIn(0, 63, palette, 20, TRUE);

    /* Set handlers */
    JOY_setEventHandler(joyEvent);
    SYS_setVBlankCallback(vblankCB);

    /* Show CPU usage in dev (remove for release) */
    SYS_showFrameLoad(TRUE);

    /* Show title screen */
    HUD_showMessage("  MEGABLADE MD  ", 12, 10);
    HUD_showMessage(" ACTION PLATFORMER", 11, 12);
    set_state(state_title_update);

    /* ===== MAIN GAME LOOP ===== */
    while (TRUE) {
        if (currentStateUpdate) currentStateUpdate();

        /* MUST call SPR_update BEFORE SYS_doVBlankProcess */
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

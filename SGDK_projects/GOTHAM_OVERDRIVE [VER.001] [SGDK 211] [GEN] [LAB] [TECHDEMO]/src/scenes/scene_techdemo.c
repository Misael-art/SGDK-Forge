#include "scenes/scene_techdemo.h"
#include "core/app.h"
#include "game_vars.h"
#include "gameplay/gotham_raster.h"
#include "gameplay/gotham_player.h"
#include "gameplay/gotham_boss.h"
#include "gameplay/gotham_enemies.h"
#include "gameplay/gotham_particles.h"
#include "system/telemetry.h"
#include "system/input.h"
#include "system/audio.h"
#include "resources.h"

#define GOTHAM_BG_B_TILE_INDEX TILE_USER_INDEX

static GothamRasterFx sRasterFx;
static u16 sBgATileIndex;

static void techdemoResetScreen(void)
{
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
    VDP_setWindowOff();
    VDP_setHilightShadow(FALSE);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL1);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_COLUMN);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setPalette(PAL0, palette_black, CPU);
    PAL_setPalette(PAL1, palette_black, CPU);
    PAL_setPalette(PAL2, palette_black, CPU);
    PAL_setPalette(PAL3, palette_black, CPU);
    VDP_setBackgroundColor(0);
}

static void techdemoLoadBackgrounds(void)
{
    sBgATileIndex = GOTHAM_BG_B_TILE_INDEX + img_gotham_skyline_bgb.tileset->numTile;

    VDP_drawImageEx(
        BG_B,
        &img_gotham_skyline_bgb,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, GOTHAM_BG_B_TILE_INDEX),
        0,
        0,
        TRUE,
        FALSE
    );

    VDP_drawImageEx(
        BG_A,
        &img_gotham_roadway_bga,
        TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, sBgATileIndex),
        0,
        0,
        TRUE,
        FALSE
    );

    PAL_setPalette(PAL0, img_gotham_skyline_bgb.palette->data, CPU);
    PAL_setPalette(PAL1, img_gotham_roadway_bga.palette->data, CPU);
    PAL_setPalette(PAL2, spr_batmobile.palette->data, CPU);
    PAL_setPalette(PAL3, spr_boss_chassis.palette->data, CPU);
}

void SCENE_techdemoEnter(void)
{
    gApp.showDebugHud = FALSE;
    gApp.paused = FALSE;

    techdemoResetScreen();
    techdemoLoadBackgrounds();

    sRasterFx.curveAngle = 0;
    sRasterFx.targetCurve = 0;
    sRasterFx.rollAngle = 0;
    sRasterFx.speed = 4;
    sRasterFx.frameCount = 0;
    sRasterFx.shakeX = 0;
    sRasterFx.shakeY = 0;
    sRasterFx.shakeTimer = 0;
    sRasterFx.flashTimer = 0;
    sRasterFx.signalSweepPhase = 0;

    GOTHAM_RASTER_init(sBgATileIndex, GOTHAM_BG_B_TILE_INDEX);
    GOTHAM_PARTICLES_init();
    GOTHAM_PLAYER_init();
    GOTHAM_BOSS_init();
    GOTHAM_ENEMIES_init();
    TELEMETRY_init();

    GOTHAM_RASTER_update(&sRasterFx, FALSE);
}

void SCENE_techdemoExit(void)
{
    GOTHAM_PARTICLES_clear();
    GOTHAM_RASTER_reset();
    AUDIO_stopAll();
}

static void techdemoDrawPause(void)
{
    VDP_drawTextFill("===== PAUSED =====", 12, 11, 18);
    VDP_drawTextFill("START: Resume Pursuit", 10, 13, 22);
}

void SCENE_techdemoUpdate(void)
{
    s16 px;
    s16 py;
    GothamPlayer* playerState;
    GothamBoss* bossState;
    u16 activeProjCount;
    u16 activeEnemyCount;

    if (INPUT_pressed(BUTTON_START)) {
        gApp.paused = !gApp.paused;
        AUDIO_playCue(AUDIO_CUE_PAUSE);
        if (!gApp.paused) {
            VDP_clearTextArea(10, 11, 22, 3);
        }
        return;
    }

    if (gApp.paused) {
        techdemoDrawPause();
        return;
    }

    if (INPUT_pressed(BUTTON_MODE) || INPUT_pressed(BUTTON_X)) {
        TELEMETRY_toggleOverlay();
    }

    px = GOTHAM_PLAYER_getX();
    py = GOTHAM_PLAYER_getY();

    // Update Raster engine (Multi-axis pseudo-3D & scanline deformation)
    GOTHAM_RASTER_update(&sRasterFx, TRUE);

    // Update Player Batmobile
    GOTHAM_PLAYER_update(&sRasterFx);

    // Update Modular Boss (Two-Face Siege Dreadnought)
    GOTHAM_BOSS_update(&sRasterFx, px, py);

    // Update Escort Drones
    GOTHAM_ENEMIES_update(&sRasterFx, px, py);

    // Update Particle and Projectile Pool
    GOTHAM_PARTICLES_update();

    // Check boss projectile collisions against player
    {
        Projectile* projs = GOTHAM_PARTICLES_getProjectiles();
        u16 i;
        for (i = 0; i < MAX_PROJECTILES; i++) {
            if (projs[i].type == PROJ_BOSS_PLASMA || projs[i].type == PROJ_ENEMY_LASER) {
                s16 projX = F16_toInt(projs[i].x);
                s16 projY = F16_toInt(projs[i].y);
                // Batmobile Hitbox (px + 6 to px + 42, py + 4 to py + 20)
                if (projX >= px + 6 && projX <= px + 42 && projY >= py + 4 && projY <= py + 20) {
                    GOTHAM_PLAYER_damage(projs[i].damage, &sRasterFx);
                    projs[i].type = PROJ_NONE;
                    if (projs[i].sprite) {
                        SPR_setVisibility(projs[i].sprite, HIDDEN);
                        SPR_setPosition(projs[i].sprite, -32, -32);
                    }
                }
            }
        }
    }

    // Telemetry & Diagnostics
    playerState = GOTHAM_PLAYER_getState();
    bossState = GOTHAM_BOSS_getState();
    activeProjCount = GOTHAM_PARTICLES_getActiveCount();
    activeEnemyCount = GOTHAM_ENEMIES_getActiveCount();

    TELEMETRY_update();
    TELEMETRY_drawHud(playerState, bossState, activeProjCount, activeEnemyCount);
}

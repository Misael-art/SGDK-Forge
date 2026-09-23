#include <genesis.h>

#include "audio/xgm_router.h"
#include "core/app.h"
#include "game_vars.h"
#include "minigames/mg_common.h"
#include "scenes/scene_branding.h"
#include "scenes/scene_boot.h"
#include "scenes/scene_demo.h"
#include "scenes/scene_ending.h"
#include "scenes/scene_intro.h"
#include "scenes/scene_menu.h"
#include "scenes/scene_boss.h"
#include "scenes/scene_gameover.h"
#include "scenes/scene_stage.h"
#include "scenes/scene_title.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"
#include "systems/journey.h"

/*
 * APP_SCENE_COUNT agora vive em game_vars.h (fonte unica). O ifndef abaixo
 * permanece como cinto de seguranca para headers legados.
 */
#ifndef APP_SCENE_COUNT
#define APP_SCENE_COUNT 21
#endif

static void APP_drawDebugHud(void)
{
    char line[40];
    const char* regionName = (gApp.region == APP_REGION_PAL) ? "PAL" : "NTSC";

    /* Canonical single-row HUD at row 26. Row 27 is reserved for scene hints. */
    sprintf(line, "SCN:%-8s FRM:%05lu %s", APP_sceneName(gApp.currentScene), gApp.totalFrames, regionName);
    VDP_drawTextFill(line, HUD_TEXT_X, HUD_ROW_HUD_GLOBAL, HUD_TEXT_LEN);
}

static void APP_drawTransitionHud(void)
{
    char line[40];

    if (gApp.transitionFrames == 0) {
        VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 1);
        return;
    }

    sprintf(line, ">> %s", APP_sceneName(gApp.transitionTarget));
    VDP_drawTextFill(line, 1, 0, 38);
}

void APP_boot(bool hardReset)
{
    AppScene bootScene;

    (void) hardReset;

    /*
     * Harness hook: must run BEFORE PROBE_init() so the probe knows whether
     * the host locked a capture target. With no SBIS request in SRAM this
     * returns the fallback and boot behaviour is unchanged.
     */
    bootScene = (AppScene) PROBE_resolveBootScene((u16) APP_SCENE_TITLE,
                                                  (u16) APP_SCENE_COUNT);

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setBackgroundColor(0);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x121224));

    JOY_init();
    INPUT_init();
    AUDIO_init();
    /* Router last: it is the single owner and its state must win. */
    AUDIO_routerInit();
    SPR_init();

    gApp.currentScene = bootScene;
    gApp.previousScene = bootScene;
    gApp.transitionTarget = bootScene;
    gApp.totalFrames = 0;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 0;
    gApp.region = SYS_isPAL() ? APP_REGION_PAL : APP_REGION_NTSC;
    gApp.targetFps = (gApp.region == APP_REGION_PAL) ? 50 : 60;
    gApp.sceneNeedsEnter = TRUE;
    gApp.showDebugHud = FALSE;
    gApp.paused = FALSE;

    /* MISSAO 2026-08-24: estado da jornada (fase ativa, unlocks, RNG). */
    JOURNEY_resetNewGame();
    /* Instrumentacao de lab: override de fase para capturas de variante. */
    JOURNEY_applySramOverride();

    PROBE_init();
    PROBE_setSceneId((u16) gApp.currentScene);
}

void SCENE_cleanupLineScroll(VDPPlane plane)
{
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(plane, 0);
    VDP_setVerticalScroll(plane, 0);
}

void APP_changeScene(AppScene nextScene)
{
    /*
     * Canonical SAT scrub on every scene transition: SPR_reset invalidates the
     * internal sprite list, SPR_update commits an empty list to VRAM SAT so no
     * stale hardware sprites from the previous scene bleed into the next one.
     */
    SPR_reset();
    SPR_update();

    if (gApp.currentScene == nextScene) {
        gApp.sceneFrames = 0;
        gApp.sceneNeedsEnter = TRUE;
        PROBE_setSceneId((u16) nextScene);
        return;
    }

    gApp.previousScene = gApp.currentScene;
    gApp.currentScene = nextScene;
    gApp.transitionTarget = nextScene;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 12;
    gApp.sceneNeedsEnter = TRUE;
    gApp.paused = FALSE;

    PROBE_setSceneId((u16) nextScene);
}

const char* APP_sceneName(AppScene scene)
{
    switch (scene)
    {
        case APP_SCENE_BRANDING: return "BRAND";
        case APP_SCENE_BOOT: return "BOOT";
        case APP_SCENE_MENU: return "MENU";
        case APP_SCENE_DEMO: return "DEMO";
        case APP_SCENE_STAGE: return "STAGE";
        case APP_SCENE_STAGE_PLAYTEST: return "PLAYTEST";
        case APP_SCENE_BOSS: return "BOSS";
        case APP_SCENE_BOSS_PLAYTEST: return "BOSSTEST";
        case APP_SCENE_GAMEOVER: return "GAMEOVER";
        case APP_SCENE_TITLE: return "TITLE";
        case APP_SCENE_LAKE: return "LAKE";
        case APP_SCENE_INTRO: return "INTRO";
        case APP_SCENE_ENDING: return "ENDING";
        case APP_SCENE_MGHUB: return "MGHUB";
        case APP_SCENE_MG_QUICKDRAW: return "MGQDRAW";
        case APP_SCENE_MG_STARFALL: return "MGSTAR";
        case APP_SCENE_MG_PUNCH: return "MGPUNCH";
        case APP_SCENE_MG_DODGE: return "MGDODGE";
        case APP_SCENE_MG_SIMON: return "MGSIMON";
        case APP_SCENE_MG_HIGHJUMP: return "MGJUMP";
        case APP_SCENE_MG_RHYTHM: return "MGRHYTH";
        default: return "UNKNOWN";
    }
}

void APP_update(void)
{
    if (INPUT_pressed(BUTTON_C)) {
        gApp.showDebugHud = !gApp.showDebugHud;
        if (!gApp.showDebugHud) {
            /* Clear only the canonical HUD row; row 27 is owned by scene hints. */
            VDP_clearTextArea(0, HUD_ROW_HUD_GLOBAL, VDP_TEXT_COLS, HUD_ROWS);
        }
    }

    if (gApp.sceneNeedsEnter)
    {
        switch (gApp.currentScene)
        {
            case APP_SCENE_BRANDING: SCENE_brandingEnter(); break;
            case APP_SCENE_BOOT: SCENE_bootEnter(); break;
            case APP_SCENE_MENU: SCENE_menuEnter(); break;
            case APP_SCENE_DEMO: SCENE_demoEnter(); break;
            case APP_SCENE_STAGE: SCENE_stageEnter(); break;
            case APP_SCENE_STAGE_PLAYTEST: SCENE_stagePlaytestEnter(); break;
            case APP_SCENE_BOSS: SCENE_bossEnter(); break;
            case APP_SCENE_BOSS_PLAYTEST: SCENE_bossPlaytestEnter(); break;
            case APP_SCENE_GAMEOVER: SCENE_gameoverEnter(); break;
            case APP_SCENE_TITLE: SCENE_titleEnter(); break;
            case APP_SCENE_LAKE: SCENE_stageLakeEnter(); break;
            case APP_SCENE_INTRO: SCENE_introEnter(); break;
            case APP_SCENE_ENDING: SCENE_endingEnter(); break;
            case APP_SCENE_MGHUB: SCENE_mgHubEnter(); break;
            case APP_SCENE_MG_QUICKDRAW: SCENE_mgQuickdrawEnter(); break;
            case APP_SCENE_MG_STARFALL: SCENE_mgStarfallEnter(); break;
            case APP_SCENE_MG_PUNCH: SCENE_mgPunchEnter(); break;
            case APP_SCENE_MG_DODGE: SCENE_mgDodgeEnter(); break;
            case APP_SCENE_MG_SIMON: SCENE_mgSimonEnter(); break;
            case APP_SCENE_MG_HIGHJUMP: SCENE_mgHighjumpEnter(); break;
            case APP_SCENE_MG_RHYTHM: SCENE_mgRhythmEnter(); break;
            default: SCENE_bootEnter(); break;
        }
        gApp.sceneNeedsEnter = FALSE;
    }

    PROBE_beginSection(PROBE_SECTION_SCENE);
    switch (gApp.currentScene)
    {
        case APP_SCENE_BRANDING: SCENE_brandingUpdate(); break;
        case APP_SCENE_BOOT: SCENE_bootUpdate(); break;
        case APP_SCENE_MENU: SCENE_menuUpdate(); break;
        case APP_SCENE_DEMO: SCENE_demoUpdate(); break;
        case APP_SCENE_STAGE: SCENE_stageUpdate(); break;
        case APP_SCENE_STAGE_PLAYTEST: SCENE_stageUpdate(); break;
        case APP_SCENE_BOSS: SCENE_bossUpdate(); break;
        case APP_SCENE_BOSS_PLAYTEST: SCENE_bossUpdate(); break;
        case APP_SCENE_GAMEOVER: SCENE_gameoverUpdate(); break;
        case APP_SCENE_TITLE: SCENE_titleUpdate(); break;
        case APP_SCENE_LAKE: SCENE_stageUpdate(); break;
        case APP_SCENE_INTRO: SCENE_introUpdate(); break;
        case APP_SCENE_ENDING: SCENE_endingUpdate(); break;
        case APP_SCENE_MGHUB: SCENE_mgHubUpdate(); break;
        case APP_SCENE_MG_QUICKDRAW: SCENE_mgQuickdrawUpdate(); break;
        case APP_SCENE_MG_STARFALL: SCENE_mgStarfallUpdate(); break;
        case APP_SCENE_MG_PUNCH: SCENE_mgPunchUpdate(); break;
        case APP_SCENE_MG_DODGE: SCENE_mgDodgeUpdate(); break;
        case APP_SCENE_MG_SIMON: SCENE_mgSimonUpdate(); break;
        case APP_SCENE_MG_HIGHJUMP: SCENE_mgHighjumpUpdate(); break;
        case APP_SCENE_MG_RHYTHM: SCENE_mgRhythmUpdate(); break;
        default: SCENE_bootUpdate(); break;
    }
    PROBE_endSection(PROBE_SECTION_SCENE);

    if (gApp.showDebugHud) {
        APP_drawDebugHud();
    }

    if (gApp.transitionFrames > 0) {
        APP_drawTransitionHud();
        gApp.transitionFrames--;
        if (gApp.transitionFrames == 0) {
            VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 1);
        }
    }

    PROBE_beginSection(PROBE_SECTION_AUDIO);
    AUDIO_update();
    AUDIO_routerTick();
    PROBE_endSection(PROBE_SECTION_AUDIO);

    gApp.totalFrames++;
    gApp.sceneFrames++;
}

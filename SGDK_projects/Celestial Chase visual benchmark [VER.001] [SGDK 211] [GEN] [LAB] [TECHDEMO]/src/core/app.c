#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "scenes/scene_branding.h"
#include "scenes/scene_boot.h"
#include "scenes/scene_chase.h"
#include "scenes/scene_demo.h"
#include "scenes/scene_menu.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"

void APP_boot(bool hardReset)
{
    (void) hardReset;

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
    SPR_initEx(680);

    gApp.currentScene = APP_SCENE_BRANDING;
    gApp.previousScene = APP_SCENE_BRANDING;
    gApp.transitionTarget = APP_SCENE_BRANDING;
    gApp.totalFrames = 0;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 0;
    gApp.region = SYS_isPAL() ? APP_REGION_PAL : APP_REGION_NTSC;
    gApp.targetFps = (gApp.region == APP_REGION_PAL) ? 50 : 60;
    gApp.sceneNeedsEnter = TRUE;
    gApp.showDebugHud = FALSE;
    gApp.paused = FALSE;
    gApp.chaseMode = CHASE_MODE_RUN;
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
        return;
    }

    gApp.previousScene = gApp.currentScene;
    gApp.currentScene = nextScene;
    gApp.transitionTarget = nextScene;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 12;
    gApp.sceneNeedsEnter = TRUE;
    gApp.paused = FALSE;
}

const char* APP_sceneName(AppScene scene)
{
    switch (scene)
    {
        case APP_SCENE_BRANDING: return "BRAND";
        case APP_SCENE_BOOT: return "BOOT";
        case APP_SCENE_MENU: return "MENU";
        case APP_SCENE_DEMO: return "DEMO";
        case APP_SCENE_CHASE: return "CHASE";
        default: return "UNKNOWN";
    }
}

void APP_update(void)
{
    bool holdSceneUpdate;

    if (gApp.sceneNeedsEnter)
    {
        switch (gApp.currentScene)
        {
            case APP_SCENE_BRANDING: SCENE_brandingEnter(); break;
            case APP_SCENE_BOOT: SCENE_bootEnter(); break;
            case APP_SCENE_MENU: SCENE_menuEnter(); break;
            case APP_SCENE_DEMO: SCENE_demoEnter(); break;
            case APP_SCENE_CHASE: SCENE_chaseEnter(); break;
            default: SCENE_bootEnter(); break;
        }
        gApp.sceneNeedsEnter = FALSE;
    }

    holdSceneUpdate = MDRuntimeProbe_shouldHoldScene();
    if (!holdSceneUpdate) {
        switch (gApp.currentScene)
        {
            case APP_SCENE_BRANDING: SCENE_brandingUpdate(); break;
            case APP_SCENE_BOOT: SCENE_bootUpdate(); break;
            case APP_SCENE_MENU: SCENE_menuUpdate(); break;
            case APP_SCENE_DEMO: SCENE_demoUpdate(); break;
            case APP_SCENE_CHASE: SCENE_chaseUpdate(); break;
            default: SCENE_bootUpdate(); break;
        }
    }

    if (!holdSceneUpdate && gApp.transitionFrames > 0) {
        gApp.transitionFrames--;
    }

    AUDIO_update();

    gApp.totalFrames++;
    if (!holdSceneUpdate) {
        gApp.sceneFrames++;
    }
}


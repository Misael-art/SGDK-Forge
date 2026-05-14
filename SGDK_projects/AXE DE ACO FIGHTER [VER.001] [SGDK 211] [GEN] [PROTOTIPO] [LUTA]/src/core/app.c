#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "scenes/scene_fight.h"
#include "system/input.h"
#include "system/runtime_probe.h"

void APP_boot(bool hardReset)
{
    (void) hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL3);
    VDP_setTextPriority(TRUE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setBackgroundColor(0);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x220044));

    JOY_init();
    INPUT_init();
    SPR_initEx(420);
    PSG_reset();

    gApp.currentScene = APP_SCENE_FIGHT;
    gApp.previousScene = APP_SCENE_FIGHT;
    gApp.totalFrames = 0;
    gApp.sceneFrames = 0;
    gApp.sceneNeedsEnter = TRUE;
    gApp.showDebugHud = FALSE;

    MDRuntimeProbe_init();
}

void SCENE_cleanupLineScroll(VDPPlane plane)
{
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(plane, 0);
    VDP_setVerticalScroll(plane, 0);
}

void APP_changeScene(AppScene nextScene)
{
    SPR_reset();
    SPR_update();

    gApp.previousScene = gApp.currentScene;
    gApp.currentScene = nextScene;
    gApp.sceneFrames = 0;
    gApp.sceneNeedsEnter = TRUE;
}

const char* APP_sceneName(AppScene scene)
{
    switch (scene)
    {
        case APP_SCENE_BOOT: return "BOOT";
        case APP_SCENE_MENU: return "MENU";
        case APP_SCENE_DEMO: return "DEMO";
        case APP_SCENE_FIGHT: return "FIGHT";
        default: return "UNKNOWN";
    }
}

void APP_update(void)
{
    if (gApp.sceneNeedsEnter)
    {
        SCENE_fightEnter();
        gApp.sceneNeedsEnter = FALSE;
    }

    SCENE_fightUpdate();

    gApp.totalFrames++;
    gApp.sceneFrames++;
}

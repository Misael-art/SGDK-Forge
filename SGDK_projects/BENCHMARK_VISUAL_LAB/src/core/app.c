#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "scenes/scene_boot.h"
#include "scenes/scene_demo.h"
#include "scenes/scene_menu.h"
#include "scenes/scene_parallax.h"
#include "scenes/scene_sunny_land.h"
#include "scenes/scene_sprite_anim.h"
#include "scenes/scene_character_design.h"
#include "scenes/scene_multiplane.h"
#include "system/input.h"

static void APP_drawDebugHud(void)
{
    char line[40];

    VDP_drawText("DEBUG HUD", 1, 26);
    sprintf(line, "SCENE: %-8s", APP_sceneName(gApp.currentScene));
    VDP_drawText(line, 1, 27);
    sprintf(line, "FRAME: %lu", gApp.totalFrames);
    VDP_drawText(line, 1, 28);
}

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
    SPR_initEx(768);

    gApp.currentScene = APP_SCENE_BOOT;
    gApp.previousScene = APP_SCENE_BOOT;
    gApp.totalFrames = 0;
    gApp.sceneFrames = 0;
    gApp.sceneNeedsEnter = TRUE;
    gApp.showDebugHud = TRUE;
}

void APP_changeScene(AppScene nextScene)
{
    if (gApp.currentScene == nextScene) {
        gApp.sceneFrames = 0;
        gApp.sceneNeedsEnter = TRUE;
        return;
    }

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
        case APP_SCENE_PARALLAX: return "PARALLAX";
        case APP_SCENE_SUNNY_LAND: return "SUNNY";
        case APP_SCENE_SPRITE_ANIM: return "SPR_ANIM";
        case APP_SCENE_CHAR_DESIGN: return "CHR_DSGN";
        case APP_SCENE_MULTIPLANE: return "MLTPLANE";
        default: return "UNKNOWN";
    }
}

void APP_update(void)
{
    if (INPUT_pressed(BUTTON_C)) {
        gApp.showDebugHud = !gApp.showDebugHud;
        if (!gApp.showDebugHud) {
            VDP_clearTextArea(0, 26, 40, 3);
        }
    }

    if (gApp.sceneNeedsEnter)
    {
        switch (gApp.currentScene)
        {
            case APP_SCENE_BOOT: SCENE_bootEnter(); break;
            case APP_SCENE_MENU: SCENE_menuEnter(); break;
            case APP_SCENE_DEMO: SCENE_demoEnter(); break;
            case APP_SCENE_PARALLAX: SCENE_parallaxEnter(); break;
            case APP_SCENE_SUNNY_LAND: SCENE_sunnyLandEnter(); break;
            case APP_SCENE_SPRITE_ANIM: SCENE_spriteAnimEnter(); break;
            case APP_SCENE_CHAR_DESIGN: SCENE_characterDesignEnter(); break;
            case APP_SCENE_MULTIPLANE: SCENE_multiplaneEnter(); break;
            default: SCENE_bootEnter(); break;
        }
        gApp.sceneNeedsEnter = FALSE;
    }

    switch (gApp.currentScene)
    {
        case APP_SCENE_BOOT: SCENE_bootUpdate(); break;
        case APP_SCENE_MENU: SCENE_menuUpdate(); break;
        case APP_SCENE_DEMO: SCENE_demoUpdate(); break;
        case APP_SCENE_PARALLAX: SCENE_parallaxUpdate(); break;
        case APP_SCENE_SUNNY_LAND: SCENE_sunnyLandUpdate(); break;
        case APP_SCENE_SPRITE_ANIM: SCENE_spriteAnimUpdate(); break;
        case APP_SCENE_CHAR_DESIGN: SCENE_characterDesignUpdate(); break;
        case APP_SCENE_MULTIPLANE: SCENE_multiplaneUpdate(); break;
        default: SCENE_bootUpdate(); break;
    }

    if (gApp.showDebugHud) {
        APP_drawDebugHud();
    }

    gApp.totalFrames++;
    gApp.sceneFrames++;
}

#include <genesis.h>

#include "core/app.h"
#include "core/scene_registry.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/overlay.h"
#include "system/runtime_probe.h"

static void APP_drawDebugHud(void)
{
    char line[40];

    /* Canonical single-row HUD at row 26. Row 27 is reserved for scene hints. */
    sprintf(line, "SCN:%-8s FRM:%05lu", APP_sceneName(gApp.currentScene), gApp.totalFrames);
    VDP_drawTextFill(line, HUD_TEXT_X, HUD_ROW_HUD_GLOBAL, HUD_TEXT_LEN);
}

static void APP_exitCurrentScene(void)
{
    const SceneDefinition* scene = SCENE_REGISTRY_find(gApp.currentScene);

    if ((scene != NULL) && (scene->exit != NULL))
    {
        scene->exit();
    }
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
    APP_exitCurrentScene();

    /*
     * Canonical SAT scrub on every scene transition: SPR_reset invalidates the
     * internal sprite list, SPR_update commits an empty list to VRAM SAT so no
     * stale hardware sprites from the previous scene bleed into the next one.
     */
    SPR_reset();
    SPR_update();
    SCENE_overlayWindowTeardown();
    SCENE_cleanupLineScroll(BG_A);
    SCENE_cleanupLineScroll(BG_B);

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
    const SceneDefinition* definition = SCENE_REGISTRY_find(scene);

    if (definition != NULL)
    {
        return definition->runtime_name;
    }

    return "UNKNOWN";
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
        const SceneDefinition* scene = SCENE_REGISTRY_find(gApp.currentScene);

        if ((scene != NULL) && (scene->enter != NULL))
        {
            scene->enter();
        }
        gApp.sceneNeedsEnter = FALSE;
    }

    {
        const SceneDefinition* scene = SCENE_REGISTRY_find(gApp.currentScene);

        if ((scene != NULL) && (scene->update != NULL))
        {
            scene->update();
        }
    }

    if (gApp.showDebugHud) {
        APP_drawDebugHud();
    }
    else {
        VDP_clearTextArea(0, HUD_ROW_HUD_GLOBAL, VDP_TEXT_COLS, HUD_ROWS);
    }

    MDRuntimeProbe_tick();
    gApp.totalFrames++;
    gApp.sceneFrames++;
}

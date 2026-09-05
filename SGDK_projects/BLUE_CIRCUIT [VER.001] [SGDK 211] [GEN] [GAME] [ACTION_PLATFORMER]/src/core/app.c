#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "scenes/scene_branding.h"
#include "scenes/scene_boot.h"
#include "scenes/scene_demo.h"
#include "scenes/scene_menu.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"

#define APP_SCENE_BOOTSTRAP_OFFSET 0x120u
#define APP_SCENE_BOOTSTRAP_MAGIC_TEXT "SBIS"
#define APP_SCENE_BOOTSTRAP_SCHEMA 1u
#define APP_SCENE_BOOTSTRAP_LENGTH 12u
#define APP_SCENE_BOOTSTRAP_CHECK_BASE 0xA55Au

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

static u16 APP_readSramU16BE(u32 offset)
{
    u16 hi = (u16) SRAM_readByte(offset);
    u16 lo = (u16) SRAM_readByte(offset + 1u);
    return (u16)((hi << 8) | lo);
}

static bool APP_readSceneBootstrap(AppScene* scene)
{
    bool accepted = FALSE;
    u16 schema;
    u16 length;
    u16 sceneId;
    u16 checksum;
    u16 expected;

    SRAM_enableRO();

    if (SRAM_readByte(APP_SCENE_BOOTSTRAP_OFFSET + 0u) == (u8) 'S' &&
        SRAM_readByte(APP_SCENE_BOOTSTRAP_OFFSET + 1u) == (u8) 'B' &&
        SRAM_readByte(APP_SCENE_BOOTSTRAP_OFFSET + 2u) == (u8) 'I' &&
        SRAM_readByte(APP_SCENE_BOOTSTRAP_OFFSET + 3u) == (u8) 'S') {
        schema = APP_readSramU16BE(APP_SCENE_BOOTSTRAP_OFFSET + 4u);
        length = APP_readSramU16BE(APP_SCENE_BOOTSTRAP_OFFSET + 6u);
        sceneId = APP_readSramU16BE(APP_SCENE_BOOTSTRAP_OFFSET + 8u);
        checksum = APP_readSramU16BE(APP_SCENE_BOOTSTRAP_OFFSET + 10u);
        expected = (u16)(APP_SCENE_BOOTSTRAP_CHECK_BASE ^ schema ^ length ^ sceneId);

        if (schema == APP_SCENE_BOOTSTRAP_SCHEMA &&
            length == APP_SCENE_BOOTSTRAP_LENGTH &&
            checksum == expected &&
            sceneId <= (u16) APP_SCENE_DEMO) {
            *scene = (AppScene) sceneId;
            accepted = TRUE;
        }
    }

    SRAM_disable();
    return accepted;
}

void APP_boot(bool hardReset)
{
    AppScene bootScene = APP_SCENE_MENU;
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
    SPR_init();

    if (APP_readSceneBootstrap(&bootScene)) {
        gApp.showDebugHud = TRUE;
    } else {
        gApp.showDebugHud = FALSE;
    }

    gApp.currentScene = bootScene;
    gApp.previousScene = bootScene;
    gApp.transitionTarget = bootScene;
    gApp.totalFrames = 0;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 0;
    gApp.region = SYS_isPAL() ? APP_REGION_PAL : APP_REGION_NTSC;
    gApp.targetFps = (gApp.region == APP_REGION_PAL) ? 50 : 60;
    gApp.sceneNeedsEnter = TRUE;
    gApp.paused = FALSE;

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
            default: SCENE_bootEnter(); break;
        }
        gApp.sceneNeedsEnter = FALSE;
    }

    switch (gApp.currentScene)
    {
        case APP_SCENE_BRANDING: SCENE_brandingUpdate(); break;
        case APP_SCENE_BOOT: SCENE_bootUpdate(); break;
        case APP_SCENE_MENU: SCENE_menuUpdate(); break;
        case APP_SCENE_DEMO: SCENE_demoUpdate(); break;
        default: SCENE_bootUpdate(); break;
    }

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

    AUDIO_update();

    gApp.totalFrames++;
    gApp.sceneFrames++;
}

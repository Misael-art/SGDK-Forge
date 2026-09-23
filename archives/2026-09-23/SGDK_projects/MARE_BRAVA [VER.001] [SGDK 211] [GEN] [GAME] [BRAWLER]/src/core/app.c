#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "scenes/scene_branding.h"
#include "scenes/scene_boot.h"
#include "scenes/scene_demo.h"
#include "scenes/scene_menu.h"
#include "system/audio.h"
#include "system/camera.h"
#include "system/input.h"
#include "system/runtime_probe.h"

#define APP_EVIDENCE_BOOT_OFFSET 0x120
#define APP_EVIDENCE_BOOT_VERSION 1
#define APP_EVIDENCE_BOOT_LENGTH 12
#define APP_EVIDENCE_BOOT_CHECK_SEED 0xA55A

static u16 APP_readSramU16BE(u32 offset)
{
    return ((u16) SRAM_readByte(offset) << 8) | SRAM_readByte(offset + 1);
}

static AppScene APP_consumeEvidenceBootScene(void)
{
    AppScene selected = APP_SCENE_BRANDING;
    u16 version;
    u16 length;
    u16 scene;
    u16 checksum;

    SRAM_enable();

    if (SRAM_readByte(APP_EVIDENCE_BOOT_OFFSET + 0) == 'S' &&
        SRAM_readByte(APP_EVIDENCE_BOOT_OFFSET + 1) == 'B' &&
        SRAM_readByte(APP_EVIDENCE_BOOT_OFFSET + 2) == 'I' &&
        SRAM_readByte(APP_EVIDENCE_BOOT_OFFSET + 3) == 'S') {
        version = APP_readSramU16BE(APP_EVIDENCE_BOOT_OFFSET + 4);
        length = APP_readSramU16BE(APP_EVIDENCE_BOOT_OFFSET + 6);
        scene = APP_readSramU16BE(APP_EVIDENCE_BOOT_OFFSET + 8);
        checksum = APP_readSramU16BE(APP_EVIDENCE_BOOT_OFFSET + 10);

        if (version == APP_EVIDENCE_BOOT_VERSION &&
            length == APP_EVIDENCE_BOOT_LENGTH &&
            scene <= APP_SCENE_DEMO &&
            checksum == (APP_EVIDENCE_BOOT_CHECK_SEED ^ version ^ length ^ scene)) {
            selected = (AppScene) scene;
        }
    }

    /* One-shot test hook: never persist a forced boot into later normal runs. */
    SRAM_writeByte(APP_EVIDENCE_BOOT_OFFSET + 0, 0);
    SRAM_writeByte(APP_EVIDENCE_BOOT_OFFSET + 1, 0);
    SRAM_writeByte(APP_EVIDENCE_BOOT_OFFSET + 2, 0);
    SRAM_writeByte(APP_EVIDENCE_BOOT_OFFSET + 3, 0);
    SRAM_disable();

    return selected;
}

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

    gApp.currentScene = APP_consumeEvidenceBootScene();
    gApp.previousScene = gApp.currentScene;
    gApp.transitionTarget = gApp.currentScene;
    gApp.totalFrames = 0;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 0;
    gApp.region = SYS_isPAL() ? APP_REGION_PAL : APP_REGION_NTSC;
    gApp.targetFps = (gApp.region == APP_REGION_PAL) ? 50 : 60;
    gApp.sceneNeedsEnter = TRUE;
    gApp.showDebugHud = FALSE;
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
    CAMERA_reset();

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
    if (INPUT_pressed(BUTTON_X)) {
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

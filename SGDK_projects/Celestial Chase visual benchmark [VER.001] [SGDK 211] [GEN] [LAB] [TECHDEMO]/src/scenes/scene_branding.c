#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"

#define BRAND_PHASE_ENGINE 0
#define BRAND_PHASE_AUTHOR 1
#define BRAND_PHASE_PROJECT 2

#define BRAND_ENGINE_END 150
#define BRAND_AUTHOR_END 315
#define BRAND_PROJECT_END 520

#define BRAND_TILE_FX TILE_USER_INDEX
#define BRAND_TILE_LOGO (TILE_USER_INDEX + 128)
#define BRAND_TILE_PRESENTS (TILE_USER_INDEX + 512)

static u8 sBrandPhase;
static s16 sBrandLineScroll[224];

static const u16 BRAND_ENGINE_SHIMMER[4] = {
    0x08AE, 0x0ACE, 0x0EEE, 0x0ACE
};

static const u16 BRAND_AUTHOR_SCAN[4] = {
    0x0040, 0x0080, 0x00C0, 0x0EE0
};

static const u16 BRAND_PROJECT_FLASH[5] = {
    0x0E40, 0x0E80, 0x0EA0, 0x0EE0, 0x0EEE
};

static void brandStopAudio(void)
{
    AUDIO_stopAll();
}

static void brandPulseAudio(u8 channel, u16 tone, u8 envelope)
{
    (void)tone;
    (void)envelope;
    if (channel == 2) {
        AUDIO_playCue(AUDIO_CUE_STRIKE);
    } else if (channel == 1) {
        AUDIO_playCue(AUDIO_CUE_PICKUP);
    } else {
        AUDIO_playCue(AUDIO_CUE_MENU);
    }
}

static void brandResetScroll(void)
{
    u16 i;

    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);

    for (i = 0; i < 224; i++) {
        sBrandLineScroll[i] = 0;
    }
}

static void brandResetScreen(void)
{
    SPR_reset();
    SPR_update();
    brandResetScroll();
    VDP_clearTileMapRect(BG_A, 0, 0, 64, 32);
    VDP_clearTileMapRect(BG_B, 0, 0, 64, 32);
    PAL_setPalette(PAL0, palette_black, CPU);
    PAL_setPalette(PAL1, palette_black, CPU);
    PAL_setPalette(PAL2, palette_black, CPU);
    PAL_setPalette(PAL3, palette_black, CPU);
    VDP_setTextPalette(PAL1);
    VDP_setBackgroundColor(0);
}

static void brandDrawFxTiles(void)
{
    u16 x;
    u16 y;
    bool loadPalette = TRUE;
    const u16 attr = TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, BRAND_TILE_FX);

    for (y = 0; y < 28; y += 4) {
        for (x = 0; x < 48; x += 16) {
            VDP_drawImageEx(BG_B, &img_brand_fx_tiles, attr, x, y, loadPalette, FALSE);
            loadPalette = FALSE;
        }
    }
}

static void brandAnimateFx(u16 frame, s16 speed)
{
    VDP_setHorizontalScroll(BG_B, (s16)((frame >> 1) & 31) * speed);
    VDP_setVerticalScroll(BG_B, (s16)((frame >> 3) & 3));
}

static void brandEnterEngine(void)
{
    brandResetScreen();
    brandDrawFxTiles();
    PAL_setPalette(PAL1, img_brand_engine_logo.palette->data, CPU);
    VDP_drawImageEx(
        BG_A,
        &img_brand_engine_logo,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, BRAND_TILE_LOGO),
        6,
        9,
        TRUE,
        FALSE
    );
    VDP_setVerticalScroll(BG_A, 42);
    brandPulseAudio(0, 260, 2);
    brandPulseAudio(1, 520, 6);
}

static void brandUpdateEngine(u16 frame)
{
    s16 rise = 42 - (s16)frame;

    if (rise < 0) {
        rise = 0;
    }

    VDP_setVerticalScroll(BG_A, rise);
    brandAnimateFx(frame, -1);

    if ((frame & 7) == 0) {
        PAL_setColor(16 + 14, BRAND_ENGINE_SHIMMER[(frame >> 3) & 3]);
    }

    if (frame == 18) {
        brandPulseAudio(0, 210, 1);
    } else if (frame == 46) {
        brandPulseAudio(1, 780, 4);
    } else if (frame == 76) {
        brandStopAudio();
    }
}

static void brandEnterAuthor(void)
{
    brandResetScreen();
    brandDrawFxTiles();
    PAL_setPalette(PAL1, img_brand_author_logo.palette->data, CPU);
    VDP_drawImageEx(
        BG_A,
        &img_brand_author_logo,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, BRAND_TILE_LOGO),
        6,
        10,
        TRUE,
        FALSE
    );
    VDP_setHorizontalScroll(BG_A, 0);
    brandPulseAudio(0, 640, 4);
}

static void brandUpdateAuthor(u16 frame)
{
    u16 cursorX;

    VDP_setHorizontalScroll(BG_A, 0);
    brandAnimateFx(frame, 1);

    if ((frame & 3) == 0) {
        PAL_setColor(16 + 6, BRAND_AUTHOR_SCAN[(frame >> 2) & 3]);
    }

    if (frame > 42 && frame < 126) {
        cursorX = 8 + ((frame >> 2) & 23);
        VDP_drawText(" ", 7 + (((frame >> 2) - 1) & 23), 18);
        VDP_drawText("|", cursorX, 18);
    }

    if (frame == 34) {
        brandPulseAudio(1, 920, 5);
    } else if (frame == 68) {
        brandPulseAudio(0, 700, 6);
    } else if (frame == 100) {
        brandStopAudio();
    }
}

static s16 brandWaveOffset(u16 frame, u16 line, u16 amplitude)
{
    u16 phase = (u16)((line + (frame << 2)) & 31);
    s16 centered = (phase < 16) ? (s16)phase : (s16)(31 - phase);
    centered -= 8;
    return (centered * (s16)amplitude) >> 3;
}

static void brandEnterProject(void)
{
    brandResetScreen();
    brandDrawFxTiles();
    PAL_setPalette(PAL1, img_brand_project_logo.palette->data, CPU);
    VDP_drawImageEx(
        BG_A,
        &img_brand_project_logo,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, BRAND_TILE_LOGO),
        5,
        7,
        TRUE,
        FALSE
    );
    VDP_drawImageEx(
        BG_A,
        &img_brand_presents_text,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, BRAND_TILE_PRESENTS),
        13,
        19,
        TRUE,
        FALSE
    );
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
    brandPulseAudio(0, 190, 1);
    brandPulseAudio(1, 380, 5);
}

static void brandUpdateProject(u16 frame)
{
    u16 i;
    u16 amplitude;

    if (frame < 36) {
        amplitude = 2;
    } else {
        amplitude = 0;
    }

    for (i = 0; i < 224; i++) {
        if (i < 48 || i > 178) {
            sBrandLineScroll[i] = 0;
        } else {
            sBrandLineScroll[i] = brandWaveOffset(frame, i, amplitude);
        }
    }

    VDP_setHorizontalScrollLine(BG_A, 0, sBrandLineScroll, 224, CPU);
    brandAnimateFx(frame, -1);

    if (frame < 48) {
        PAL_setColor(16 + 10, BRAND_PROJECT_FLASH[(frame / 8) % 5]);
        PAL_setColor(16 + 11, BRAND_PROJECT_FLASH[(frame / 6) % 5]);
    } else if ((frame & 15) == 0) {
        PAL_setColor(16 + 9, BRAND_PROJECT_FLASH[(frame >> 4) & 3]);
    }

    if (frame == 28) {
        brandPulseAudio(2, 1160, 4);
    } else if (frame == 62) {
        brandPulseAudio(0, 150, 1);
    } else if (frame == 112) {
        brandStopAudio();
    }
}

static void brandSetPhase(u8 phase)
{
    if (sBrandPhase == phase) {
        return;
    }

    sBrandPhase = phase;

    if (phase == BRAND_PHASE_ENGINE) {
        brandEnterEngine();
    } else if (phase == BRAND_PHASE_AUTHOR) {
        brandEnterAuthor();
    } else {
        brandEnterProject();
    }
}

static void brandExitToBoot(void)
{
    brandStopAudio();
    brandResetScroll();
    APP_changeScene(APP_SCENE_BOOT);
}

void SCENE_brandingEnter(void)
{
    gApp.showDebugHud = FALSE;
    sBrandPhase = 0xFF;
    brandStopAudio();
    brandResetScreen();
}

void SCENE_brandingUpdate(void)
{
    const u16 frame = gApp.sceneFrames;

    if (INPUT_pressed(BUTTON_START) || INPUT_pressed(BUTTON_A)) {
        brandExitToBoot();
        return;
    }

    if (frame < BRAND_ENGINE_END) {
        brandSetPhase(BRAND_PHASE_ENGINE);
        brandUpdateEngine(frame);
        return;
    }

    if (frame < BRAND_AUTHOR_END) {
        brandSetPhase(BRAND_PHASE_AUTHOR);
        brandUpdateAuthor(frame - BRAND_ENGINE_END);
        return;
    }

    if (frame < BRAND_PROJECT_END) {
        brandSetPhase(BRAND_PHASE_PROJECT);
        brandUpdateProject(frame - BRAND_AUTHOR_END);
        return;
    }

    brandExitToBoot();
}

#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/overlay.h"

static void SCENE_fxLineScrollWaterV2DrawOverlay(void)
{
    SCENE_overlayWindowBegin();
    VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 3);
    VDP_drawTextFill("S1.2 AGUA LINE SCROLL", 10, 0, 20);
    VDP_drawTextFill("Placeholder para HSCROLL_LINE com telemetria segura.", 0, 1, 40);
    VDP_drawTextFill("Contrato: warmup READY e retorno limpo ao menu.", 0, 2, 40);
    SCENE_overlayWindowEnd();
}

static void SCENE_fxLineScrollWaterV2DrawBody(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_drawTextFill("Objetivo visual futuro:", 2, 6, 22);
    VDP_drawTextFill("faixas de agua com oscilacao horizontal por linha", 1, 8, 39);
    VDP_drawTextFill("Risco VDP previsto: sobra de scroll-table entre cenas.", 1, 11, 39);
    VDP_drawTextFill("A/START: reiniciar  B: menu", 6, HUD_ROW_HINT_PRIMARY, 28);
}

void SCENE_fxLineScrollWaterV2Enter(void)
{
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x103024));
    SCENE_fxLineScrollWaterV2DrawBody();
    SCENE_fxLineScrollWaterV2DrawOverlay();
}

void SCENE_fxLineScrollWaterV2Update(void)
{
    char line[40];
    u16 phaseA = (u16)((gApp.sceneFrames * 2u) & 63u);
    u16 phaseB = (u16)((gApp.sceneFrames * 5u) & 63u);
    u16 crest = (u16)((gApp.sceneFrames / 4u) % 24u);
    char wave[25];
    u16 i;

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_FX_LINE_SCROLL_WATER);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    for (i = 0; i < 24; i++) {
        wave[i] = (i == crest) ? '~' : '-';
    }
    wave[24] = '\0';

    sprintf(line, "Wave phase A: %02u", phaseA);
    VDP_drawTextFill(line, 2, 14, 28);
    sprintf(line, "Wave phase B: %02u", phaseB);
    VDP_drawTextFill(line, 2, 16, 28);
    sprintf(line, "Surface trace: %s", wave);
    VDP_drawTextFill(line, 2, 18, 38);
}

void SCENE_fxLineScrollWaterV2Exit(void)
{
    SCENE_overlayWindowTeardown();
    SCENE_cleanupLineScroll(BG_A);
    SCENE_cleanupLineScroll(BG_B);
}

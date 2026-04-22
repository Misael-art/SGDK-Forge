#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/overlay.h"

static void SCENE_multiplaneShowcaseV2DrawOverlay(void)
{
    SCENE_overlayWindowBegin();
    VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 3);
    VDP_drawTextFill("S1.1 MULTIPLANE CURADO", 9, 0, 22);
    VDP_drawTextFill("Placeholder tecnico com contrato de overlay/window.", 0, 1, 40);
    VDP_drawTextFill("Evidencia alvo: READY + menu navegavel + cena viva.", 0, 2, 40);
    SCENE_overlayWindowEnd();
}

static void SCENE_multiplaneShowcaseV2DrawBody(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_drawTextFill("Objetivo visual futuro:", 2, 6, 22);
    VDP_drawTextFill("foreground denso + fundo profundo + overlay seguro", 1, 8, 39);
    VDP_drawTextFill("Budget alvo inicial: placeholder sem assets finais.", 1, 11, 39);
    VDP_drawTextFill("A/START: reiniciar  B: menu", 6, HUD_ROW_HINT_PRIMARY, 28);
}

void SCENE_multiplaneShowcaseV2Enter(void)
{
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102438));
    SCENE_multiplaneShowcaseV2DrawBody();
    SCENE_multiplaneShowcaseV2DrawOverlay();
}

void SCENE_multiplaneShowcaseV2Update(void)
{
    char line[40];
    u16 nearPhase = (u16)((gApp.sceneFrames * 3u) & 63u);
    u16 farPhase = (u16)((gApp.sceneFrames * 2u) & 31u);
    u16 marker = (u16)((gApp.sceneFrames / 8u) % 20u);
    char bar[21];
    u16 i;

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_MULTIPLANE_SHOWCASE);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    for (i = 0; i < 20; i++) {
        bar[i] = (i == marker) ? '#' : '.';
    }
    bar[20] = '\0';

    sprintf(line, "Near plane phase: %02u", nearPhase);
    VDP_drawTextFill(line, 2, 14, 30);
    sprintf(line, "Far  plane phase: %02u", farPhase);
    VDP_drawTextFill(line, 2, 16, 30);
    sprintf(line, "Depth cadence: %s", bar);
    VDP_drawTextFill(line, 2, 18, 38);
}

void SCENE_multiplaneShowcaseV2Exit(void)
{
    SCENE_overlayWindowTeardown();
    SCENE_cleanupLineScroll(BG_A);
    SCENE_cleanupLineScroll(BG_B);
}

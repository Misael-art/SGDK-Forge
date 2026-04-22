#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/overlay.h"

static void SCENE_depthTowerShowcaseV2DrawOverlay(void)
{
    SCENE_overlayWindowBegin();
    VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 3);
    VDP_drawTextFill("S1.3 DEPTH TOWER", 12, 0, 16);
    VDP_drawTextFill("Placeholder para profundidade vertical por colunas.", 0, 1, 40);
    VDP_drawTextFill("Contrato: limpeza de scroll ao sair e heartbeat vivo.", 0, 2, 40);
    SCENE_overlayWindowEnd();
}

static void SCENE_depthTowerShowcaseV2DrawBody(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_drawTextFill("Objetivo visual futuro:", 2, 6, 22);
    VDP_drawTextFill("torres em camadas com leitura de profundidade", 2, 8, 36);
    VDP_drawTextFill("Risco VDP previsto: estado residual de vscroll column.", 1, 11, 39);
    VDP_drawTextFill("A/START: reiniciar  B: menu", 6, HUD_ROW_HINT_PRIMARY, 28);
}

void SCENE_depthTowerShowcaseV2Enter(void)
{
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x241830));
    SCENE_depthTowerShowcaseV2DrawBody();
    SCENE_depthTowerShowcaseV2DrawOverlay();
}

void SCENE_depthTowerShowcaseV2Update(void)
{
    char line[40];
    char depthA[17];
    char depthB[17];
    u16 headA = (u16)((gApp.sceneFrames / 6u) % 16u);
    u16 headB = (u16)((gApp.sceneFrames / 10u) % 16u);
    u16 i;

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEPTH_TOWER_SHOWCASE);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    for (i = 0; i < 16; i++) {
        depthA[i] = (i <= headA) ? '|' : '.';
        depthB[i] = (i <= headB) ? '|' : '.';
    }
    depthA[16] = '\0';
    depthB[16] = '\0';

    sprintf(line, "Near tower depth: %s", depthA);
    VDP_drawTextFill(line, 2, 14, 38);
    sprintf(line, "Far  tower depth: %s", depthB);
    VDP_drawTextFill(line, 2, 16, 38);
    sprintf(line, "Cadence delta: %02u", (u16)((headA + 16u - headB) & 15u));
    VDP_drawTextFill(line, 2, 18, 28);
}

void SCENE_depthTowerShowcaseV2Exit(void)
{
    SCENE_overlayWindowTeardown();
    SCENE_cleanupLineScroll(BG_A);
    SCENE_cleanupLineScroll(BG_B);
}

#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

static void SCENE_demoDrawStatic(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_drawText("DEMO TECNICA EDITAVEL", 9, 4);
    VDP_drawText("Use esta cena para experimentar logica, UI e fluxo.", 1, 8);
    VDP_drawText("A: reiniciar a cena", 11, 20);
    VDP_drawText("B: voltar para menu", 11, 22);
    VDP_drawText("C: alternar HUD", 12, 24);
}

void SCENE_demoEnter(void)
{
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x241212));
    SCENE_demoDrawStatic();
}

void SCENE_demoUpdate(void)
{
    char line[40];
    u16 markerX = 2 + (gApp.sceneFrames % 34);
    u16 colorBand = (gApp.sceneFrames / 16) & 3;
    u16 backdrop;

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    switch (colorBand)
    {
        case 0: backdrop = RGB24_TO_VDPCOLOR(0x241212); break;
        case 1: backdrop = RGB24_TO_VDPCOLOR(0x242412); break;
        case 2: backdrop = RGB24_TO_VDPCOLOR(0x122424); break;
        default: backdrop = RGB24_TO_VDPCOLOR(0x181824); break;
    }
    PAL_setColor(0, backdrop);

    VDP_clearTextArea(0, 11, 40, 6);
    sprintf(line, "Scene frame: %u", gApp.sceneFrames);
    VDP_drawText(line, 2, 11);
    sprintf(line, "Held: 0x%04X  Pressed: 0x%04X", gInput.held, gInput.pressed);
    VDP_drawText(line, 2, 13);
    VDP_drawText("Pedagogical marker:", 2, 15);
    VDP_drawText("<*>", markerX, 17);
}

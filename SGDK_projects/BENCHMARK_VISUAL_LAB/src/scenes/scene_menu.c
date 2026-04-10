#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

static void SCENE_menuDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    VDP_drawText("MENU INICIAL", 13, 4);
    VDP_drawText("1. Edite src/scenes para criar novas telas.", 2, 8);
    VDP_drawText("2. Edite src/system para infraestrutura.", 2, 10);
    VDP_drawText("3. Coloque assets brutos em res/data/.", 2, 12);
    VDP_drawText("4. Declare recursos reais quando necessario.", 2, 14);
    VDP_drawText("A: cena demo", 14, 18);
    VDP_drawText("START: S1 PARALLAX POC", 9, 20);
    VDP_drawText("RIGHT: SUNNY LAND PROOF", 7, 22);
    VDP_drawText("B: voltar para boot", 10, 24);
}

void SCENE_menuEnter(void)
{
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102410));
    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    if (INPUT_pressed(BUTTON_A)) {
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    if (INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_PARALLAX);
        return;
    }

    if (INPUT_pressed(BUTTON_RIGHT)) {
        APP_changeScene(APP_SCENE_SUNNY_LAND);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_BOOT);
    }
}

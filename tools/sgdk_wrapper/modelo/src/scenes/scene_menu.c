#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

static void SCENE_menuDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);

    VDP_drawTextFill("MENU INICIAL", 13, 4, 14);
    VDP_drawTextFill("1. Edite src/scenes para criar novas telas.", 2, 8, 38);
    VDP_drawTextFill("2. Edite src/system para infraestrutura.", 2, 10, 38);
    VDP_drawTextFill("3. Coloque assets brutos em res/data/.", 2, 12, 38);
    VDP_drawTextFill("4. Declare recursos reais quando necessario.", 2, 14, 38);
    VDP_drawTextFill("A ou START: abrir cena demo", 6, 19, 34);
    VDP_drawTextFill("B: voltar para boot", 10, 21, 30);
    VDP_drawTextFill("C: alternar HUD", 12, HUD_ROW_HINT_PRIMARY, 28);
}

void SCENE_menuEnter(void)
{
    /*
     * Canonical scene-enter pattern:
     *   1) SPR_reset + SPR_update => safety net in case we were re-entered via
     *      a code path that bypasses APP_changeScene.
     *   2) PAL3 = palette_grey with VDP_setTextPalette(PAL3) guarantees high-
     *      contrast overlay text regardless of the currently loaded BG palettes.
     */
    SPR_reset();
    SPR_update();

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102410));
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);

    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_BOOT);
    }
}

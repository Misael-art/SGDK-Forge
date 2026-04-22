#include <genesis.h>

#include "core/app.h"
#include "core/scene_registry.h"
#include "game_vars.h"
#include "system/input.h"

static u16 sMenuIndex = 0;

static void SCENE_menuDraw(void)
{
    u16 menuCount = SCENE_REGISTRY_menuCount();
    u16 index;

    VDP_clearPlane(BG_A, TRUE);

    VDP_drawTextFill("MENU CURADO V2", 13, 4, 14);
    VDP_drawTextFill("Slice 1 navegavel com placeholders tecnicos.", 1, 7, 39);

    for (index = 0; index < menuCount; index++)
    {
        const SceneDefinition* scene = SCENE_REGISTRY_menuAt(index);
        char line[40];

        if (scene == NULL)
        {
            continue;
        }

        sprintf(line, "%c %u. %-28s", (index == sMenuIndex) ? '>' : ' ', index + 1, scene->menu_label);
        VDP_drawTextFill(line, 2, (u16)(10 + (index * 2)), 36);
    }

    VDP_drawTextFill("UP/DOWN: selecionar", 9, 20, 22);
    VDP_drawTextFill("A ou START: abrir cena", 8, 22, 24);
    VDP_drawTextFill("B: voltar ao boot   C: alternar HUD", 3, HUD_ROW_HINT_PRIMARY, 34);
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

    sMenuIndex = 0;
    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    u16 menuCount = SCENE_REGISTRY_menuCount();

    if (INPUT_pressed(BUTTON_UP)) {
        if (sMenuIndex == 0) {
            sMenuIndex = (u16)(menuCount - 1);
        } else {
            sMenuIndex--;
        }
        SCENE_menuDraw();
        return;
    }

    if (INPUT_pressed(BUTTON_DOWN)) {
        sMenuIndex = (u16)((sMenuIndex + 1) % menuCount);
        SCENE_menuDraw();
        return;
    }

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        const SceneDefinition* scene = SCENE_REGISTRY_menuAt(sMenuIndex);

        if (scene != NULL) {
            APP_changeScene(scene->scene_id);
        }
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_BOOT);
    }
}

#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

typedef struct MenuEntry {
    const char* label;
    AppScene scene;
} MenuEntry;

static const MenuEntry sMenuEntries[] = {
    { "Demo tecnica editavel", APP_SCENE_DEMO },
    { "S1.1 Sprite Animation", APP_SCENE_SPRITE_ANIM },
    { "S1.2 Character Design", APP_SCENE_CHAR_DESIGN },
    { "S1.3 Multiplane", APP_SCENE_MULTIPLANE },
    { "Sunny Land Proof", APP_SCENE_SUNNY_LAND },
    { "S1 Parallax POC", APP_SCENE_PARALLAX },
    { "fx_line_scroll_water_lab", APP_SCENE_FX_LINE_SCROLL_WATER },
    { "boss_kinematics_lab", APP_SCENE_BOSS_KINEMATICS },
    { "pseudo3d_tower_lab", APP_SCENE_PSEUDO3D_TOWER },
    { "masked_light_lab", APP_SCENE_MASKED_LIGHT },
    { "audio_xgm2_lab", APP_SCENE_AUDIO_XGM2 }
};

static u16 sMenuCursor = 0;

static void SCENE_menuDraw(void)
{
    const u16 entryCount = (u16)(sizeof(sMenuEntries) / sizeof(sMenuEntries[0]));
    u16 i;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearTextArea(0, 0, 40, 28);

    VDP_drawText("BENCHMARK VISUAL LAB", 10, 1);
    VDP_drawText("SHOWROOM MENU", 13, 2);

    for (i = 0; i < entryCount; i++)
    {
        char line[40];
        sprintf(line, "%c %02u %s", (i == sMenuCursor) ? '>' : ' ', i + 1, sMenuEntries[i].label);
        VDP_drawText(line, 1, 4 + i);
    }

    VDP_drawText("UP/DOWN select  A/START enter  B boot", 1, 27);
}

void SCENE_menuEnter(void)
{
    sMenuCursor = 0;
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102410));
    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    const u16 entryCount = (u16)(sizeof(sMenuEntries) / sizeof(sMenuEntries[0]));
    bool redraw = FALSE;

    if (INPUT_pressed(BUTTON_UP))
    {
        if (sMenuCursor == 0) sMenuCursor = entryCount - 1;
        else sMenuCursor--;
        redraw = TRUE;
    }

    if (INPUT_pressed(BUTTON_DOWN))
    {
        sMenuCursor++;
        if (sMenuCursor >= entryCount) sMenuCursor = 0;
        redraw = TRUE;
    }

    if (INPUT_pressed(BUTTON_C))
    {
        sMenuCursor++;
        if (sMenuCursor >= entryCount) sMenuCursor = 0;
        redraw = TRUE;
    }

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START))
    {
        APP_changeScene(sMenuEntries[sMenuCursor].scene);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_BOOT);
        return;
    }

    if (redraw)
    {
        SCENE_menuDraw();
    }
}

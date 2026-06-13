#include <genesis.h>

#include "core/app.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"

#define TILEMAP_FIXTURE_TILE_BASE TILE_USER_INDEX

static void tilemapFixtureDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_B, 0);

    PAL_setPalette(PAL0, img_fixture_scene_tilemap.palette->data, CPU);
    VDP_drawImageEx(
        BG_A,
        &img_fixture_scene_tilemap,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILEMAP_FIXTURE_TILE_BASE),
        0,
        0,
        TRUE,
        FALSE
    );

    VDP_drawTextFill("CENA TILEMAP FIXTURE", 10, 1, 20);
    VDP_drawTextFill("B ou MODE: menu", 12, HUD_ROW_HINT_PRIMARY, 16);
}

void SCENE_tilemapFixtureEnter(void)
{
    SPR_reset();
    SPR_update();

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x0b1220));
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);

    tilemapFixtureDraw();
}

void SCENE_tilemapFixtureUpdate(void)
{
    if (INPUT_pressed(BUTTON_B) || INPUT_pressed(BUTTON_MODE)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(APP_SCENE_MENU);
    }
}

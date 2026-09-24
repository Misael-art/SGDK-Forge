#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/branding_v2.h"
#include "system/audio.h"
#include "system/input.h"

/*
 * Front-end da marca: a forja fica no fundo, o FORGE e o titulo, o texto
 * vive no WINDOW com ouro sobre barra opaca. VDP_drawText em PAL0 da forja
 * era a distorcao — a fonte SGDK lia as cores de brasa como glifo.
 */

static void menuShadowText(u16 x, u16 y, const char *s)
{
    VDP_setTextPalette(PAL0);
    VDP_drawText(s, (s16)(x + 1), (s16)(y + 1));
    VDP_setTextPalette(PAL3);
    VDP_drawText(s, (s16)x, (s16)y);
}

static void menuTeardown(void)
{
    VDP_setTextPlane(BG_A);
    VDP_setWindowOff();
    VDP_setHilightShadow(FALSE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
}

static void menuDraw(void)
{
    u16 vramB;
    u16 vramA;
    u16 vramLogo;
    u16 vramBar;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);

    PAL_setPalette(BRAND_V2_PAL_FORGE, img_forge_bg_b.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_METAL, img_logo_engine_v2.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_WORDMARK, img_logo_author_v2.palette->data, DMA);
    PAL_setColor(0, 0x0000);
    PAL_setColor((BRAND_V2_PAL_FORGE * 16) + 15, 0x0000);

    VDP_loadFont(&font_default, CPU);
    PAL_setPalette(PAL3, palette_grey, DMA);
    PAL_setColor((PAL3 * 16) + 15, 0x00EE);
    PAL_setColor((PAL3 * 16) + 1, 0x00EE);

    vramB = TILE_USER_INDEX;
    vramA = vramB + img_forge_bg_b.tileset->numTile;
    vramLogo = vramA + img_forge_bg_a_props.tileset->numTile;
    vramBar = vramLogo + img_logo_engine_v2.tileset->numTile;

    VDP_drawImageEx(BG_B, &img_forge_bg_b,
                    TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, FALSE, FALSE, FALSE, vramB),
                    0, 0, FALSE, TRUE);
    VDP_drawImageEx(BG_A, &img_forge_bg_a_props,
                    TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, TRUE, FALSE, FALSE, vramA),
                    0, 0, FALSE, TRUE);
    VDP_drawImageEx(BG_A, &img_logo_engine_v2,
                    TILE_ATTR_FULL(BRAND_V2_PAL_METAL, TRUE, FALSE, FALSE, vramLogo),
                    6, 8, FALSE, TRUE);
    VDP_loadTileSet(img_presents_bar_v2.tileset, vramBar, DMA);

    VDP_setTextPlane(BG_A);
    VDP_setTextPriority(TRUE);
    VDP_fillTileMapRect(BG_A,
                        TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, TRUE, FALSE, FALSE, vramBar),
                        0, 22, 40, 5);
    menuShadowText(5, 23, "START  ENTRAR NA DEMO");
    menuShadowText(5, 25, "B  REVER A MARCA");
}

void SCENE_menuEnter(void)
{
    SPR_reset();
    SPR_update();
    gApp.showDebugHud = FALSE;
    menuTeardown();
    menuDraw();
    AUDIO_startBrandBgm();
}

void SCENE_menuUpdate(void)
{
    if ((gApp.sceneFrames & 7) == 0) {
        static const u16 CYCLE[4] = { 0x0048, 0x006A, 0x008C, 0x004A };
        u16 i;
        for (i = 0; i < 4; i++) {
            PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST + i,
                         CYCLE[(i + (gApp.sceneFrames >> 3)) & 3]);
        }
    }

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        menuTeardown();
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        menuTeardown();
        APP_changeScene(APP_SCENE_BRANDING);
    }
}

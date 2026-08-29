#include <genesis.h>
#include "resources.h"

/*
 * LIVE_BAR_FR2 — lab fixture for palette roles (R2).
 * PAL0 player, PAL1 enemy, PAL2 dock BG, PAL3 spare FX.
 * lab_not_delivery: sprites are native-grid translations of Imagine
 * sources, not elite redraws.
 */

int main(bool hardReset)
{
    u16 tileIndex;
    Sprite *hero;
    Sprite *thug;
    Sprite *fx;
    u16 frame = 0;

    (void)hardReset;

    VDP_setScreenWidth320();
    SPR_init();

    PAL_setPalette(PAL0, spr_hero.palette->data, DMA);
    PAL_setPalette(PAL1, spr_thug.palette->data, DMA);
    PAL_setPalette(PAL2, img_dock.palette->data, DMA);
    PAL_setPalette(PAL3, spr_fx.palette->data, DMA);

    tileIndex = TILE_USER_INDEX;
    VDP_drawImageEx(
        BG_B,
        &img_dock,
        TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, tileIndex),
        0,
        0,
        FALSE,
        TRUE
    );

    hero = SPR_addSprite(&spr_hero, 72, 144, TILE_ATTR(PAL0, TRUE, FALSE, FALSE));
    thug = SPR_addSprite(&spr_thug, 200, 144, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    fx = SPR_addSprite(&spr_fx, 152, 96, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));

    VDP_setTextPalette(PAL3);
    VDP_drawText("FR2 PAL0 hero PAL1 thug", 1, 0);
    VDP_drawText("PAL2 dock PAL3 fx LAB", 1, 1);

    while (TRUE)
    {
        frame++;
        if (fx != NULL)
        {
            SPR_setVisibility(fx, (frame & 8) ? VISIBLE : HIDDEN);
        }
        (void)hero;
        (void)thug;
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

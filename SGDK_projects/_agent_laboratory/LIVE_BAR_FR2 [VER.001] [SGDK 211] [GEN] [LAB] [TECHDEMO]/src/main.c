#include <genesis.h>
#include "resources.h"

/*
 * LIVE_BAR_FR2 — lab fixture for palette roles (R2).
 * PAL0 player, PAL1 enemy, PAL2 dock BG, PAL3 spare FX.
 * lab_not_delivery: idle + walk strips; dock 8x8 compare_flat.
 * PAL2 water slots 4-6 cycle. Anim 0 idle, anim 1 walk (2s each).
 */

int main(bool hardReset)
{
    u16 tileIndex;
    Sprite *hero;
    Sprite *thug;
    Sprite *fx;
    u16 frame = 0;
    u16 pal2[16];
    u16 i;
    s16 lastAnim = -1;
    s16 want;

    (void)hardReset;

    VDP_setScreenWidth320();
    SPR_init();

    PAL_setPalette(PAL0, spr_hero.palette->data, DMA);
    PAL_setPalette(PAL1, spr_thug.palette->data, DMA);
    PAL_setPalette(PAL2, img_dock.palette->data, DMA);
    PAL_setPalette(PAL3, spr_fx.palette->data, DMA);
    /* Plane index 0 is transparent; backdrop must not be PAL0 magenta. PAL2 fog = 32+11. */
    VDP_setBackgroundColor(43);
    for (i = 0; i < 16; i++)
        pal2[i] = img_dock.palette->data[i];

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
    if (hero != NULL)
        SPR_setAnim(hero, 0);
    if (thug != NULL)
        SPR_setAnim(thug, 0);

    VDP_setTextPalette(PAL3);
    VDP_drawText("FR2 idle/walk PAL0-3 LAB", 1, 0);
    VDP_drawText("PAL2 water cycle", 1, 1);

    while (TRUE)
    {
        frame++;
        if (fx != NULL)
        {
            SPR_setVisibility(fx, (frame & 8) ? VISIBLE : HIDDEN);
        }
        if ((frame & 31) == 0)
        {
            u16 tmp = pal2[4];
            pal2[4] = pal2[5];
            pal2[5] = pal2[6];
            pal2[6] = tmp;
            PAL_setPalette(PAL2, pal2, DMA);
        }
        want = (s16)((frame / 120) & 1);
        if (want != lastAnim)
        {
            if (hero != NULL)
                SPR_setAnim(hero, want);
            if (thug != NULL)
                SPR_setAnim(thug, want);
            lastAnim = want;
        }
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

#include <genesis.h>
#include "resources.h"

static u16 bgBase;
static u16 fgBase;

int main(void)
{
    VDP_setPlanSize(64, 32);

    bgBase = TILE_USER_INDEX;
    VDP_drawImageEx(BG_B, &scene_bg_b, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, bgBase), 0, 0, FALSE, TRUE);

    fgBase = bgBase + scene_bg_b.tileset->numTile;
    VDP_drawImageEx(BG_A, &scene_bg_a, TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, fgBase), 0, 0, FALSE, TRUE);

    while (TRUE)
    {
        SYS_doVBlankProcess();
    }

    return 0;
}

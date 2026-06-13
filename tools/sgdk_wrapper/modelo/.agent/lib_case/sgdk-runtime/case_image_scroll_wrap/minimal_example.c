#include <genesis.h>
#include "resources.h"

static s16 scrollX;

int main(void)
{
    VDP_drawImageEx(BG_B, &bg_far, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX), 0, 0, FALSE, TRUE);

    while (TRUE)
    {
        scrollX++;
        VDP_setHorizontalScroll(BG_B, -scrollX);
        SYS_doVBlankProcess();
    }

    return 0;
}

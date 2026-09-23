#include <genesis.h>
#include "resources.h"

static Map *mapA;
static Map *mapB;
static s16 camX;

int main(void)
{
    mapA = MAP_create(&fg_map, BG_A, TILE_ATTR(PAL0, FALSE, FALSE, FALSE));
    mapB = MAP_create(&bg_map, BG_B, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));

    while (TRUE)
    {
        camX++;
        MAP_scrollTo(mapA, camX, 0);
        MAP_scrollTo(mapB, camX >> 1, 0);
        SYS_doVBlankProcess();
    }

    return 0;
}

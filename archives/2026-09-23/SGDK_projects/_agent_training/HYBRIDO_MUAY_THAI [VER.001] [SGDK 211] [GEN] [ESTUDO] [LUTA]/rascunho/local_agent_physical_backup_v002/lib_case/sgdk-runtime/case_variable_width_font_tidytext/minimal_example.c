#include <genesis.h>

static u32 stringTiles[64 * 8];

u16 buildStringTiles(const char* str, u32* outTiles);

int main(void)
{
    const u16 baseTile = TILE_USER_INDEX;
    u16 usedTiles = buildStringTiles("PRESS START", stringTiles);

    VDP_loadTileData(stringTiles, baseTile, usedTiles, DMA);
    VDP_setTileMapXY(BG_B, TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, baseTile), 4, 4);

    while (TRUE)
        SYS_doVBlankProcess();

    return 0;
}

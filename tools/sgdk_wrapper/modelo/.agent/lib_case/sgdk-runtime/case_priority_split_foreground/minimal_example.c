#include <genesis.h>

static u16 topAttr(u16 tile)
{
    return TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, tile);
}

static u16 bottomAttr(u16 tile)
{
    return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, tile);
}

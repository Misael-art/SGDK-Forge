#include <genesis.h>

typedef struct
{
    u16 mapTile;
    u16 planeTile;
    u16 count;
} TileMatch;

static TileMatch cache[256];

u16 tileCache_fetchTile(u16 mapTile);
void tileCache_releaseTile(u16 planeTile);

void tileCache_callback(u16* buf, u16 size)
{
    while (size--)
    {
        u16 tileData = *buf;
        u16 planeTile = tileCache_fetchTile(tileData & TILE_INDEX_MASK);
        *buf++ = (tileData & ~TILE_INDEX_MASK) | planeTile;
    }
}

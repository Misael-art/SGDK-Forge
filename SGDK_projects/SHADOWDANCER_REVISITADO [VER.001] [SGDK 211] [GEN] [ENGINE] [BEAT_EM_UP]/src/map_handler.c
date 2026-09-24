#include "map_handler.h"

#include <resources.h>

#define SCREEN_TILES_W 42
#define SCREEN_TILES_H 32
#define TILE_CACHE_CAPACITY 576
#define MAP_TILE_LOOKUP_CAPACITY 20480

typedef struct
{
    u16 mapTile;
    u16 planeTile;
    u16 count;
} TileMatch;

/* Fixed storage prevents heap fragmentation in the gameplay loop. */
static TileMatch tileCacheStorage[TILE_CACHE_CAPACITY];
static u16 mapTileToPlaneTileStorage[MAP_TILE_LOOKUP_CAPACITY];
static u16 planeCache[SCREEN_TILES_W][SCREEN_TILES_H];

static TileMatch *tileCache;
static u16 *mapTileToPlaneTile;
static u16 tileVram;
static u16 activeTiles;
static u16 totalTiles;
static u16 lowestFree;
static u16 highestFree;
static u16 bump;
static u16 maxTilesEver;
static u16 frameAllocations;
static const TileSet *tileSet;
static bool tileCacheReady;

static void invalidateCache(void)
{
    u16 i;

    for (i = 0; i < activeTiles; i++)
    {
        tileCache[i].mapTile = 0xFFFF;
        tileCache[i].planeTile = 0xFFFF;
        tileCache[i].count = 0;
    }
    memset(planeCache, 0xFF, sizeof(planeCache));
    memset(mapTileToPlaneTile, 0xFF, (u32) totalTiles * sizeof(u16));
}

u16 tileCache_init(u16 vram, const TileSet *ts, u16 maxTiles)
{
    if ((ts == NULL) || (maxTiles == 0) || (maxTiles > TILE_CACHE_CAPACITY) ||
        (ts->numTile > MAP_TILE_LOOKUP_CAPACITY))
    {
        tileCacheReady = FALSE;
        return 0xFFFF;
    }

    tileVram = vram;
    activeTiles = maxTiles;
    totalTiles = ts->numTile;
    tileSet = ts;
    tileCache = tileCacheStorage;
    mapTileToPlaneTile = mapTileToPlaneTileStorage;
    bump = 0;
    lowestFree = 0;
    highestFree = activeTiles - 1;
    maxTilesEver = 0;
    frameAllocations = 0;
    tileCacheReady = TRUE;
    invalidateCache();
    return (u16) (tileVram + activeTiles);
}

void tileCache_reset(void)
{
    if (!tileCacheReady) return;
    bump = 0;
    lowestFree = 0;
    highestFree = activeTiles - 1;
    maxTilesEver = 0;
    frameAllocations = 0;
    invalidateCache();
}

void tileCache_shutdown(void)
{
    /* Static storage is retained; reset is deterministic and allocation-free. */
    tileCacheReady = FALSE;
    tileCache = NULL;
    mapTileToPlaneTile = NULL;
    tileSet = NULL;
}

static u16 tileCache_fetchTile(u16 mapTile)
{
    u16 planeTile;
    u16 i;

    if (!tileCacheReady || (mapTile >= totalTiles)) return 0xFFFF;

    planeTile = mapTileToPlaneTile[mapTile];
    if (planeTile != 0xFFFF)
    {
        tileCache[planeTile].count++;
        return planeTile;
    }

    if (bump < activeTiles)
        planeTile = bump++;
    else
    {
        planeTile = 0xFFFF;
        for (i = lowestFree; i < activeTiles; i++)
        {
            if (tileCache[i].count == 0)
            {
                planeTile = i;
                lowestFree = (u16) (i + 1);
                break;
            }
        }
    }

    if (planeTile == 0xFFFF) return 0xFFFF;

    mapTileToPlaneTile[mapTile] = planeTile;
    tileCache[planeTile].mapTile = mapTile;
    tileCache[planeTile].planeTile = planeTile;
    tileCache[planeTile].count = 1;

    /* MAP callbacks run before VBlank: defer tile uploads to the DMA queue. */
    if (!DMA_queueDma(DMA_VRAM, (void *) &tileSet->tiles[(u32) mapTile * 8],
                      (u16) ((tileVram + planeTile) * 32), 16, 2))
    {
        mapTileToPlaneTile[mapTile] = 0xFFFF;
        tileCache[planeTile].mapTile = 0xFFFF;
        tileCache[planeTile].planeTile = 0xFFFF;
        tileCache[planeTile].count = 0;
        return 0xFFFF;
    }

    frameAllocations++;
    return planeTile;
}

static void tileCache_releaseTile(u16 planeTile)
{
    u16 mapTile;

    if (!tileCacheReady || (planeTile == 0xFFFF) || (planeTile >= activeTiles)) return;
    if (tileCache[planeTile].count > 0) tileCache[planeTile].count--;
    if (tileCache[planeTile].count != 0) return;

    mapTile = tileCache[planeTile].mapTile;
    if (mapTile != 0xFFFF) mapTileToPlaneTile[mapTile] = 0xFFFF;
    tileCache[planeTile].mapTile = 0xFFFF;
    tileCache[planeTile].planeTile = 0xFFFF;
    if (planeTile < lowestFree) lowestFree = planeTile;
    if (planeTile > highestFree) highestFree = planeTile;
    if ((planeTile + 1) == bump) bump--;
}

void tileCache_callback(Map *map, u16 *buf, u16 x, u16 y,
                        MapUpdateType updateType, u16 size)
{
    u16 *dst = buf;
    u16 i = size;
    u16 xt = (u16) (x % SCREEN_TILES_W);
    u16 yt = (u16) (y % SCREEN_TILES_H);

    (void) map;

    while (i--)
    {
        u16 tileData = *dst;
        u16 tileIndex = tileData & TILE_INDEX_MASK;
        u16 oldTile = planeCache[xt][yt];

        if (oldTile != 0xFFFF)
        {
            tileCache_releaseTile(oldTile);
            planeCache[xt][yt] = 0xFFFF;
        }

        tileIndex = tileCache_fetchTile(tileIndex);
        planeCache[xt][yt] = tileIndex;
        if (tileIndex != 0xFFFF)
            *dst = (tileData & ~TILE_INDEX_MASK) | (tileVram + tileIndex);
        else
            *dst = 0;

        if (updateType == ROW_UPDATE)
        {
            xt++;
            if (xt >= SCREEN_TILES_W) xt = 0;
        }
        else
        {
            yt++;
            if (yt >= SCREEN_TILES_H) yt = 0;
        }
        dst++;
    }

    if (frameAllocations > maxTilesEver) maxTilesEver = frameAllocations;
    frameAllocations = 0;
}

u16 tileCache_getUsage(void)
{
    u16 used = 0;
    u16 i;

    if (!tileCacheReady) return 0;
    for (i = 0; i < activeTiles; i++)
        if (tileCache[i].count != 0) used++;
    if (used > maxTilesEver) maxTilesEver = used;
    return maxTilesEver;
}

u16 tileCache_getMemoryBytes(void)
{
    return (u16) (sizeof(tileCacheStorage) + sizeof(mapTileToPlaneTileStorage) +
                  sizeof(planeCache));
}

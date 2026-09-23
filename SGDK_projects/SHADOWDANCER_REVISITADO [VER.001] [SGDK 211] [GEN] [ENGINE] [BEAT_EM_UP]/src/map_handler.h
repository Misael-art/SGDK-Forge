#pragma once

#include <genesis.h>

u16 tileCache_init(u16 vram, const TileSet *ts, u16 maxTiles);
void tileCache_reset(void);
void tileCache_shutdown(void);
void tileCache_callback(Map *map, u16 *buf, u16 x, u16 y,
                        MapUpdateType updateType, u16 size);
u16 tileCache_getUsage(void);
u16 tileCache_getMemoryBytes(void);

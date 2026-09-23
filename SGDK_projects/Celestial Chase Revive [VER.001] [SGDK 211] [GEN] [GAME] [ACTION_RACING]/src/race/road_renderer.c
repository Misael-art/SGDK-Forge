#include "road_renderer.h"
#include "res/resources.h"

#define TILE_ROAD_DARK      0
#define TILE_ROAD_LANE      1
#define TILE_ROAD_CURB_L    2
#define TILE_ROAD_CURB_R    3
#define TILE_ROAD_LINE      4
#define TILE_ROAD_LINE_THIN 5
#define TILE_ROAD_DARK_VAR  6
#define TILE_ROAD_CRACK     7
#define TILE_SKY_STARS2     8
#define TILE_SKY_STARS3     9
#define TILE_SKY_HORIZON    10
#define TILE_SKY_STRUCT     11
#define TILE_SKY_CITY_L     12
#define TILE_SKY_CITY_R     13
#define TILE_SKY_MOUNTAIN   14
#define TILE_SKY_CLOUD      15

#define TILE_USER_BASE TILE_USER_INDEX

#define MAP_W 64
#define MAP_H 28

static u16 road_tilemap_data[MAP_W * MAP_H];

static void fill_sky(u16 base)
{
    for (u16 y = 0; y < 3; y++)
    {
        for (u16 x = 0; x < MAP_W; x++)
        {
            u16 tile = TILE_SKY_STARS3;
            if ((x % 7) == 0) tile = TILE_SKY_STARS2;
            if ((x % 11) == 0) tile = TILE_SKY_STRUCT;
            if ((x % 5) == 0) tile = TILE_SKY_HORIZON;
            road_tilemap_data[y * MAP_W + x] =
                TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, base + tile);
        }
    }
}

static void fill_road(u16 base)
{
    for (u16 yi = 0; yi < 5; yi++)
    {
        u16 y = 3 + yi;
        for (u16 x = 0; x < MAP_W; x++)
        {
            u16 tile;
            if (x < 10 || x > 53)
            {
                tile = TILE_ROAD_DARK;
            }
            else if (x == 10 || x == 53)
            {
                tile = TILE_ROAD_CURB_L;
            }
            else if (x == 11 || x == 52)
            {
                tile = TILE_ROAD_CURB_R;
            }
            else
            {
                u16 lw = (52 - 11) / 3;
                u16 l1 = 12 + lw;
                u16 l2 = 12 + lw * 2;
                if ((yi == 0 || yi == 4) && (x == l1 || x == l1 + 1 || x == l2 || x == l2 + 1))
                {
                    tile = TILE_ROAD_LINE;
                }
                else if (x == 12 + lw / 2 || x == 12 + lw * 2 + lw / 2)
                {
                    tile = TILE_ROAD_LINE_THIN;
                }
                else if (x == 31)
                {
                    tile = TILE_ROAD_CRACK;
                }
                else if ((x + yi) % 4 == 0)
                {
                    tile = TILE_ROAD_DARK_VAR;
                }
                else
                {
                    tile = TILE_ROAD_DARK;
                }
            }
            road_tilemap_data[y * MAP_W + x] =
                TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, base + tile);
        }
    }
}

void Road_init(void)
{
    u16 base = TILE_USER_BASE;
    VDP_loadTileSet(img_road_tiles.tileset, TILE_USER_BASE, DMA);

    for (u16 i = 0; i < MAP_W * MAP_H; i++)
    {
        road_tilemap_data[i] =
            TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, base + TILE_ROAD_DARK);
    }

    fill_sky(base);
    fill_road(base);

    VDP_setTileMapDataRect(BG_A, road_tilemap_data, 0, 0, MAP_W, MAP_H, MAP_W, DMA);
}

void Road_update(s32 scroll_x)
{
    VDP_setHorizontalScroll(BG_A, -scroll_x);
}

void Road_drawTilemap(void)
{
    VDP_setTileMapDataRect(BG_A, road_tilemap_data, 0, 0, MAP_W, MAP_H, MAP_W, DMA);
}

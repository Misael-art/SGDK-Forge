#include <genesis.h>

#define SCREEN_LINES 224
#define TILE_BASE TILE_USER_INDEX
#define TILE_SKY 0
#define TILE_CLOUD 1
#define TILE_HILL 2
#define TILE_FOREGROUND 3

static s16 sBgBScroll[SCREEN_LINES];
static s16 sBgAScroll[SCREEN_LINES];
static s16 sCameraX;

static const u32 sSolidTiles[4][8] =
{
    { 0x11111111, 0x11111111, 0x11111111, 0x11111111, 0x11111111, 0x11111111, 0x11111111, 0x11111111 },
    { 0x22222222, 0x22222222, 0x20222220, 0x20022200, 0x20222220, 0x22222222, 0x22222222, 0x22222222 },
    { 0x33333333, 0x33303333, 0x33000333, 0x30000033, 0x33333333, 0x33333333, 0x33333333, 0x33333333 },
    { 0x44444444, 0x40444044, 0x44404444, 0x44044404, 0x44444444, 0x40444444, 0x44440444, 0x44444444 }
};

static void loadPalette(void)
{
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x000000));
    PAL_setColor(1, RGB24_TO_VDPCOLOR(0x102060));
    PAL_setColor(2, RGB24_TO_VDPCOLOR(0x4060A0));
    PAL_setColor(3, RGB24_TO_VDPCOLOR(0x608850));
    PAL_setColor(4, RGB24_TO_VDPCOLOR(0xA07038));
}

static void loadTiles(void)
{
    VDP_loadTileData(&sSolidTiles[0][0], TILE_BASE, 4, DMA);

    VDP_fillTileMapRect(BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_BASE + TILE_SKY), 0, 0, 64, 8);
    VDP_fillTileMapRect(BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_BASE + TILE_CLOUD), 0, 8, 64, 8);
    VDP_fillTileMapRect(BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_BASE + TILE_HILL), 0, 16, 64, 12);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, TILE_BASE + TILE_FOREGROUND), 0, 20, 64, 8);
}

static void buildScrollTables(void)
{
    u16 line;

    for (line = 0; line < SCREEN_LINES; line++)
    {
        if (line < 56)
        {
            sBgBScroll[line] = -(sCameraX >> 3);
            sBgAScroll[line] = 0;
        }
        else if (line < 112)
        {
            sBgBScroll[line] = -(sCameraX >> 2);
            sBgAScroll[line] = 0;
        }
        else if (line < 160)
        {
            sBgBScroll[line] = -(sCameraX >> 1);
            sBgAScroll[line] = 0;
        }
        else
        {
            sBgBScroll[line] = -sCameraX;
            sBgAScroll[line] = -sCameraX;
        }
    }
}

static void resetSceneFx(void)
{
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
}

int main(void)
{
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);

    loadPalette();
    loadTiles();

    while (TRUE)
    {
        sCameraX++;
        buildScrollTables();

        VDP_setHorizontalScrollLine(BG_B, 0, sBgBScroll, SCREEN_LINES, DMA);
        VDP_setHorizontalScrollLine(BG_A, 0, sBgAScroll, SCREEN_LINES, DMA);

        SYS_doVBlankProcess();
    }

    resetSceneFx();
    return 0;
}

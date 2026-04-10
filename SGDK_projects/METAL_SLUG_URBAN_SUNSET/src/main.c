#include <genesis.h>

#include "resources.h"

#define VLAB_SCENE_ID 2
#define VLAB_VERSION 6
#define VLAB_BLOCK_SIZE 160
#define VIEWPORT_WIDTH 320
#define VIEWPORT_HEIGHT 224
#define SCENE_WIDTH 584
#define INITIAL_CAMERA_X 128
#define CAMERA_MAX_X (SCENE_WIDTH - VIEWPORT_WIDTH)

#define BG_B_RUNTIME_WIDTH 128
#define BG_B_REPEAT_WIDTH_TILES 16
#define BG_B_STAMP_COUNT 4
#define SKY_LAST_LINE 95

static Map* gBgAMap = NULL;

static bool gShowOverlay = FALSE;
static bool gParallaxPaused = FALSE;
static u16 gPrevInput = 0;
static u32 gFrameCounter = 0;
static s16 gCameraX = INITIAL_CAMERA_X;
static s16 gCameraStep = 1;
static s16 gBgBLineScroll[VIEWPORT_HEIGHT];
static u16 gVramOffsetBgB = TILE_USER_INDEX;
static u16 gBgAVramBase = TILE_USER_INDEX;


static void sramWriteU16BE(const u32 offset, const u16 value)
{
    SRAM_writeByte(offset, (u8) ((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8) (value & 0xFF));
}


static void sramWriteU32BE(const u32 offset, const u32 value)
{
    SRAM_writeByte(offset, (u8) ((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8) ((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8) ((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8) (value & 0xFF));
}


static void sramWriteAscii(const u32 offset, const char* text, const u16 maxLen)
{
    u16 index = 0;

    while ((index < maxLen) && text[index])
    {
        SRAM_writeByte(offset + index, (u8) text[index]);
        index++;
    }

    while (index < maxLen)
    {
        SRAM_writeByte(offset + index, 0);
        index++;
    }
}


static u16 getActiveTileCount(void)
{
    return bg_b_elite.tileset->numTile + bg_a_elite_tileset.numTile;
}


static void writeVisualEvidenceBlock(void)
{
    u16 pal0[16];
    u16 pal1[16];
    u16 index;
    u8 flags = 0;

    if (gShowOverlay) flags |= 0x01;
    if (gParallaxPaused) flags |= 0x02;
    flags |= 0x04; /* FG_C segue staged_only nesta ROM. */

    PAL_getPalette(PAL0, pal0);
    PAL_getPalette(PAL1, pal1);

    SRAM_enable();

    SRAM_writeByte(0, 'V');
    SRAM_writeByte(1, 'L');
    SRAM_writeByte(2, 'A');
    SRAM_writeByte(3, 'B');
    sramWriteU16BE(4, VLAB_VERSION);
    sramWriteU16BE(6, VLAB_BLOCK_SIZE);
    sramWriteU32BE(8, gFrameCounter);
    SRAM_writeByte(12, flags);
    SRAM_writeByte(13, VLAB_SCENE_ID);
    SRAM_writeByte(14, 0);
    SRAM_writeByte(15, 0);
    sramWriteU16BE(16, getActiveTileCount());
    sramWriteU16BE(18, 0);
    sramWriteU16BE(20, VDP_getPlaneAddress(BG_B, 0, 0));
    sramWriteU16BE(22, VDP_getPlaneAddress(BG_A, 0, 0));

    for (index = 0; index < 16; index++)
    {
        sramWriteU16BE(24 + (index * 2), pal0[index]);
        sramWriteU16BE(56 + (index * 2), pal1[index]);
    }

    sramWriteAscii(88, "metal_slug_urban_sunset", 32);
    sramWriteU32BE(120, (u32) SCENE_WIDTH);
    sramWriteU32BE(124, (u32) CAMERA_MAX_X);
    sramWriteU32BE(128, (u32) BG_B_RUNTIME_WIDTH);
    sramWriteAscii(132, "bg_b_repeat128x4+bg_a_map", 24);
    sramWriteAscii(156, "MD", 2);
    SRAM_writeByte(158, 6);
    SRAM_writeByte(159, 0);

    SRAM_disable();
}


static void drawOverlay(void)
{
    VDP_clearTextArea(0, 0, 40, 6);

    if (!gShowOverlay)
    {
        VDP_setWindowOff();
        return;
    }

    VDP_setWindowOnTop(6);
    VDP_drawText("METAL SLUG URBAN SUNSET", 3, 1);
    VDP_drawText("BG_B: SKY + SKYLINE", 3, 2);
    VDP_drawText("BG_A: MAP 584X224", 3, 3);
    VDP_drawText("FG_C: STAGED ONLY", 3, 4);
    VDP_drawText(gParallaxPaused ? "B: RUN  A: OVERLAY" : "B: PAUSE A: OVERLAY", 3, 5);
}


static void rebuildBgBScrollTable(void)
{
    u16 line;
    const s16 skyScroll = -(gCameraX >> 3);
    const s16 skylineScroll = -(gCameraX >> 2);

    for (line = 0; line < VIEWPORT_HEIGHT; line++)
    {
        gBgBLineScroll[line] = (line <= SKY_LAST_LINE) ? skyScroll : skylineScroll;
    }
}


static void applyBgBScrollTable(const TransferMethod tm)
{
    VDP_setHorizontalScrollLine(BG_B, 0, gBgBLineScroll, VIEWPORT_HEIGHT, tm);
}


static void loadBgBPlane(void)
{
    u16 stampIndex;

    gVramOffsetBgB = TILE_USER_INDEX;
    VDP_loadTileSet(bg_b_elite.tileset, gVramOffsetBgB, CPU);

    for (stampIndex = 0; stampIndex < BG_B_STAMP_COUNT; stampIndex++)
    {
        VDP_setTileMapEx(
            BG_B,
            bg_b_elite.tilemap,
            TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, gVramOffsetBgB),
            BG_B_REPEAT_WIDTH_TILES * stampIndex,
            0,
            0,
            0,
            BG_B_REPEAT_WIDTH_TILES,
            28,
            CPU
        );
    }
}


static void initBgAMap(void)
{
    gBgAVramBase = gVramOffsetBgB + bg_b_elite.tileset->numTile;
    VDP_loadTileSet(&bg_a_elite_tileset, gBgAVramBase, CPU);
    gBgAMap = MAP_create(&bg_a_elite_map, BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, gBgAVramBase));
    MAP_scrollToEx(gBgAMap, gCameraX, 0, TRUE);
}


static void drawScene(void)
{
    VDP_setEnable(FALSE);
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);

    PAL_setPalette(PAL0, bg_b_elite.palette->data, CPU);
    PAL_setPalette(PAL1, bg_a_elite_pal.palette->data, CPU);
    VDP_setBackgroundColor(0);

    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_setWindowOff();

    loadBgBPlane();
    initBgAMap();
    rebuildBgBScrollTable();
    applyBgBScrollTable(CPU);
    drawOverlay();
    writeVisualEvidenceBlock();

    VDP_setEnable(TRUE);
}


static void updateInput(void)
{
    const u16 state = JOY_readJoypad(JOY_1);
    const u16 pressed = state & ~gPrevInput;

    if (pressed & BUTTON_A)
    {
        gShowOverlay = !gShowOverlay;
        drawOverlay();
    }

    if (pressed & BUTTON_B)
    {
        gParallaxPaused = !gParallaxPaused;
        drawOverlay();
        writeVisualEvidenceBlock();
    }

    gPrevInput = state;
}


static void updateCameraAndParallax(void)
{
    if (!gParallaxPaused)
    {
        gCameraX += gCameraStep;

        if (gCameraX >= CAMERA_MAX_X)
        {
            gCameraX = CAMERA_MAX_X;
            gCameraStep = -1;
        }
        else if (gCameraX <= 0)
        {
            gCameraX = 0;
            gCameraStep = 1;
        }
    }

    if (gBgAMap != NULL)
    {
        MAP_scrollTo(gBgAMap, (u32) gCameraX, 0);
    }

    rebuildBgBScrollTable();
    applyBgBScrollTable(DMA_QUEUE);
}


int main(bool hardReset)
{
    const bool ignoredHardReset = hardReset;
    (void) ignoredHardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(WINDOW);
    VDP_setTextPriority(TRUE);
    JOY_init();

    drawScene();
    SYS_doVBlankProcess();

    while (TRUE)
    {
        updateInput();
        updateCameraAndParallax();
        gFrameCounter++;

        if ((gFrameCounter & 0x000F) == 0)
        {
            writeVisualEvidenceBlock();
        }

        SYS_doVBlankProcess();
    }

    return 0;
}

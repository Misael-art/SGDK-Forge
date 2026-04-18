#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/input.h"

#define WATER_SCENE_ID 8
#define WATER_VLAB_VERSION 2
#define WATER_VLAB_BLOCK_SIZE 160
#define WATER_SCROLL_LINES 224

static s16 sLineScroll[WATER_SCROLL_LINES];
static s16 sCameraX = 0;
static u16 sPhase = 0;
static bool sOverlay = TRUE;

static void SCENE_waterSramWriteU16BE(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static void SCENE_waterSramWriteU32BE(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8)((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8)(value & 0xFF));
}

static void SCENE_waterSramWriteAscii(u32 offset, const char* text, u16 maxLen)
{
    u16 i = 0;
    while ((i < maxLen) && text[i])
    {
        SRAM_writeByte(offset + i, (u8)text[i]);
        i++;
    }
    while (i < maxLen)
    {
        SRAM_writeByte(offset + i, 0);
        i++;
    }
}

static void SCENE_waterWriteEvidenceBlock(void)
{
    u16 pal0[16];
    u16 pal1[16];
    u16 index;
    u8 flags = 0;

    if (sOverlay) flags |= 0x01;

    PAL_getPalette(PAL0, pal0);
    PAL_getPalette(PAL1, pal1);

    SRAM_enable();

    SRAM_writeByte(0, 'V');
    SRAM_writeByte(1, 'L');
    SRAM_writeByte(2, 'A');
    SRAM_writeByte(3, 'B');
    SCENE_waterSramWriteU16BE(4, WATER_VLAB_VERSION);
    SCENE_waterSramWriteU16BE(6, WATER_VLAB_BLOCK_SIZE);
    SCENE_waterSramWriteU32BE(8, gApp.totalFrames);
    SRAM_writeByte(12, flags);
    SRAM_writeByte(13, WATER_SCENE_ID);
    SRAM_writeByte(14, (u8)(sPhase & 0xFF));
    SRAM_writeByte(15, (u8)(sCameraX & 0xFF));
    SCENE_waterSramWriteU16BE(16, bg_b_sky.tileset->numTile + bg_a_ground.tileset->numTile);
    SCENE_waterSramWriteU16BE(18, 0);
    SCENE_waterSramWriteU16BE(20, VDP_getPlaneAddress(BG_B, 0, 0));
    SCENE_waterSramWriteU16BE(22, VDP_getPlaneAddress(BG_A, 0, 0));

    for (index = 0; index < 16; index++)
    {
        SCENE_waterSramWriteU16BE(24 + (index * 2), pal0[index]);
        SCENE_waterSramWriteU16BE(56 + (index * 2), pal1[index]);
    }

    SCENE_waterSramWriteAscii(88, "fx_line_scroll_water_lab", 32);
    SCENE_waterSramWriteU32BE(120, 224);
    SCENE_waterSramWriteU32BE(124, 360);
    SCENE_waterSramWriteU32BE(128, (u32)sPhase);
    SCENE_waterSramWriteAscii(132, "hscroll_line_bg_b", 24);
    SCENE_waterSramWriteAscii(156, "MD", 2);
    SRAM_writeByte(158, 3);
    SRAM_writeByte(159, 8);

    SRAM_disable();
}

static void SCENE_waterDrawOverlay(void)
{
    char line[40];

    VDP_clearTextArea(0, 0, 40, 3);
    if (!sOverlay) return;

    VDP_drawText("FX LINE SCROLL WATER LAB", 8, 0);
    sprintf(line, "phase:%u cam:%d", sPhase, sCameraX);
    VDP_drawText(line, 2, 1);
    VDP_drawText("LEFT/RIGHT camera  A overlay  B menu", 1, 2);
}

void SCENE_fxLineScrollWaterLabEnter(void)
{
    u16 base = TILE_USER_INDEX;

    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);

    PAL_setPalette(PAL0, bg_b_sky.palette->data, DMA);
    PAL_setPalette(PAL1, bg_a_ground.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);

    VDP_loadTileSet(bg_b_sky.tileset, base, DMA);
    VDP_setTileMapEx(BG_B, bg_b_sky.tilemap,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, base),
        0, 0, 0, 0, 64, 32, DMA);
    base += bg_b_sky.tileset->numTile;

    VDP_loadTileSet(bg_a_ground.tileset, base, DMA);
    VDP_setTileMapEx(BG_A, bg_a_ground.tilemap,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, base),
        0, 0, 0, 0, 64, 32, DMA);

    sCameraX = 0;
    sPhase = 0;
    sOverlay = TRUE;
    SCENE_waterWriteEvidenceBlock();
    SCENE_waterDrawOverlay();
}

void SCENE_fxLineScrollWaterLabUpdate(void)
{
    u16 i;

    if (INPUT_pressed(BUTTON_B))
    {
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
        VDP_setHorizontalScroll(BG_A, 0);
        VDP_setHorizontalScroll(BG_B, 0);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (INPUT_pressed(BUTTON_A)) {
        sOverlay = !sOverlay;
    }

    if (INPUT_held(BUTTON_LEFT)) {
        sCameraX -= 2;
    } else if (INPUT_held(BUTTON_RIGHT)) {
        sCameraX += 2;
    }

    for (i = 0; i < WATER_SCROLL_LINES; i++)
    {
        fix16 waveA = F16_sin(FIX16(((i * 3) + sPhase) % 360));
        fix16 waveB = F16_sin(FIX16(((i * 7) + (sPhase >> 1)) % 360));
        s16 wobbleA = F16_toInt(F16_mul(waveA, FIX16(8)));
        s16 wobbleB = F16_toInt(F16_mul(waveB, FIX16(3)));
        sLineScroll[i] = (s16)(-sCameraX + wobbleA + wobbleB);
    }

    VDP_setHorizontalScrollLine(BG_B, 0, sLineScroll, WATER_SCROLL_LINES, DMA_QUEUE);
    VDP_setHorizontalScroll(BG_A, -sCameraX);

    if ((gApp.sceneFrames & 63u) == 0u) SCENE_waterWriteEvidenceBlock();

    sPhase = (u16)((sPhase + 3) % 360);
    SCENE_waterDrawOverlay();
}

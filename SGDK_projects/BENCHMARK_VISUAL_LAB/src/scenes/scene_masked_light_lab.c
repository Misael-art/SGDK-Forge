#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/hint_arbiter.h"
#include "system/input.h"

#define MASKED_SCENE_ID 11
#define MASKED_VLAB_VERSION 2
#define MASKED_VLAB_BLOCK_SIZE 160

static u16 sDarkPal[16];
static u16 sLitPal[16];
static bool sOverlay;
static u16 sSplitLine;
static s16 sMaskX;

static void SCENE_maskedSramWriteU16BE(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static void SCENE_maskedSramWriteU32BE(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8)((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8)(value & 0xFF));
}

static void SCENE_maskedSramWriteAscii(u32 offset, const char* text, u16 maxLen)
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

static void SCENE_maskedWriteEvidenceBlock(void)
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
    SCENE_maskedSramWriteU16BE(4, MASKED_VLAB_VERSION);
    SCENE_maskedSramWriteU16BE(6, MASKED_VLAB_BLOCK_SIZE);
    SCENE_maskedSramWriteU32BE(8, gApp.totalFrames);
    SRAM_writeByte(12, flags);
    SRAM_writeByte(13, MASKED_SCENE_ID);
    SRAM_writeByte(14, (u8)(sSplitLine & 0xFF));
    SRAM_writeByte(15, (u8)(sMaskX & 0xFF));
    SCENE_maskedSramWriteU16BE(16, bg_b_sky.tileset->numTile + bg_a_ground.tileset->numTile);
    SCENE_maskedSramWriteU16BE(18, 0);
    SCENE_maskedSramWriteU16BE(20, VDP_getPlaneAddress(BG_B, 0, 0));
    SCENE_maskedSramWriteU16BE(22, VDP_getPlaneAddress(BG_A, 0, 0));

    for (index = 0; index < 16; index++)
    {
        SCENE_maskedSramWriteU16BE(24 + (index * 2), pal0[index]);
        SCENE_maskedSramWriteU16BE(56 + (index * 2), pal1[index]);
    }

    SCENE_maskedSramWriteAscii(88, "masked_light_lab", 32);
    SCENE_maskedSramWriteU32BE(120, 224);
    SCENE_maskedSramWriteU32BE(124, 224);
    SCENE_maskedSramWriteU32BE(128, (u32)sSplitLine);
    SCENE_maskedSramWriteAscii(132, "hint_palette_split", 24);
    SCENE_maskedSramWriteAscii(156, "MD", 2);
    SRAM_writeByte(158, 3);
    SRAM_writeByte(159, 11);

    SRAM_disable();
}

HINTERRUPT_CALLBACK SCENE_maskedHintCallback(void)
{
    PAL_setColors(16, sLitPal, 16, CPU);
}

static void SCENE_maskedBuildPalettes(void)
{
    u16 i;
    for (i = 0; i < 16; i++)
    {
        u16 c = bg_a_ground.palette->data[i];
        u16 rb = c & 0x00EE;
        u16 g = c & 0x0E00;
        sLitPal[i] = c;
        sDarkPal[i] = (u16)((rb >> 1) | (g >> 1));
    }
    sDarkPal[0] = bg_a_ground.palette->data[0];
}

static void SCENE_maskedDrawOverlay(void)
{
    char line[40];
    VDP_clearTextArea(0, 0, 40, 3);
    if (!sOverlay) return;

    VDP_drawText("MASKED LIGHT LAB", 12, 0);
    sprintf(line, "split:%u maskX:%d", sSplitLine, sMaskX);
    VDP_drawText(line, 2, 1);
    VDP_drawText("UP/DOWN split  LEFT/RIGHT mask  B menu", 1, 2);
}

void SCENE_maskedLightLabEnter(void)
{
    u16 base = TILE_USER_INDEX;
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

    PAL_setPalette(PAL0, bg_b_sky.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    VDP_setHilightShadow(TRUE);

    VDP_loadTileSet(bg_b_sky.tileset, base, DMA);
    VDP_setTileMapEx(BG_B, bg_b_sky.tilemap,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, base),
        0, 0, 0, 0, 64, 32, DMA);
    base += bg_b_sky.tileset->numTile;

    VDP_loadTileSet(bg_a_ground.tileset, base, DMA);
    VDP_setTileMapEx(BG_A, bg_a_ground.tilemap,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, base),
        0, 0, 0, 0, 64, 32, DMA);

    SCENE_maskedBuildPalettes();
    PAL_setColors(16, sDarkPal, 16, DMA);

    sSplitLine = 104;
    sMaskX = 80;
    sOverlay = TRUE;

    HINT_acquire(HINT_OWNER_MASKED_LIGHT, SCENE_maskedHintCallback, sSplitLine);
    SCENE_maskedWriteEvidenceBlock();
    SCENE_maskedDrawOverlay();
}

void SCENE_maskedLightLabUpdate(void)
{
    if (INPUT_pressed(BUTTON_B))
    {
        HINT_release(HINT_OWNER_MASKED_LIGHT);
        VDP_setHilightShadow(FALSE);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (INPUT_pressed(BUTTON_A)) sOverlay = !sOverlay;
    if (INPUT_held(BUTTON_UP) && sSplitLine > 24) sSplitLine--;
    if (INPUT_held(BUTTON_DOWN) && sSplitLine < 180) sSplitLine++;
    if (INPUT_held(BUTTON_LEFT) && sMaskX > 8) sMaskX -= 2;
    if (INPUT_held(BUTTON_RIGHT) && sMaskX < 304) sMaskX += 2;

    HINT_setCounter(sSplitLine);

    SYS_disableInts();
    PAL_setColors(16, sDarkPal, 16, CPU);
    VDP_clearTextArea(0, 14, 40, 1);
    VDP_drawText("||||", sMaskX >> 3, 14);
    SYS_enableInts();

    if ((gApp.sceneFrames & 63u) == 0u) SCENE_maskedWriteEvidenceBlock();

    SCENE_maskedDrawOverlay();
}

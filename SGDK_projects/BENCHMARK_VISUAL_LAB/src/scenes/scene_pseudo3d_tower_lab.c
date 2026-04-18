#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/input.h"

#define TOWER_COLUMNS 20
#define TOWER_SCENE_ID 10
#define TOWER_VLAB_VERSION 2
#define TOWER_VLAB_BLOCK_SIZE 160

static s16 sColumnScroll[TOWER_COLUMNS];
static s16 sBaseScroll;
static u16 sPhase;
static bool sOverlay;

static void SCENE_towerSramWriteU16BE(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static void SCENE_towerSramWriteU32BE(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8)((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8)(value & 0xFF));
}

static void SCENE_towerSramWriteAscii(u32 offset, const char* text, u16 maxLen)
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

static void SCENE_towerWriteEvidenceBlock(void)
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
    SCENE_towerSramWriteU16BE(4, TOWER_VLAB_VERSION);
    SCENE_towerSramWriteU16BE(6, TOWER_VLAB_BLOCK_SIZE);
    SCENE_towerSramWriteU32BE(8, gApp.totalFrames);
    SRAM_writeByte(12, flags);
    SRAM_writeByte(13, TOWER_SCENE_ID);
    SRAM_writeByte(14, (u8)(sBaseScroll & 0xFF));
    SRAM_writeByte(15, (u8)(sPhase & 0xFF));
    SCENE_towerSramWriteU16BE(16, bg_b_sky.tileset->numTile + bg_a_ground.tileset->numTile);
    SCENE_towerSramWriteU16BE(18, 0);
    SCENE_towerSramWriteU16BE(20, VDP_getPlaneAddress(BG_B, 0, 0));
    SCENE_towerSramWriteU16BE(22, VDP_getPlaneAddress(BG_A, 0, 0));

    for (index = 0; index < 16; index++)
    {
        SCENE_towerSramWriteU16BE(24 + (index * 2), pal0[index]);
        SCENE_towerSramWriteU16BE(56 + (index * 2), pal1[index]);
    }

    SCENE_towerSramWriteAscii(88, "pseudo3d_tower_lab", 32);
    SCENE_towerSramWriteU32BE(120, 224);
    SCENE_towerSramWriteU32BE(124, TOWER_COLUMNS);
    SCENE_towerSramWriteU32BE(128, (u32)sBaseScroll);
    SCENE_towerSramWriteAscii(132, "vscroll_column_bg_a", 24);
    SCENE_towerSramWriteAscii(156, "MD", 2);
    SRAM_writeByte(158, 3);
    SRAM_writeByte(159, 20);

    SRAM_disable();
}

static void SCENE_towerDrawOverlay(void)
{
    char line[40];
    VDP_clearTextArea(0, 0, 40, 3);
    if (!sOverlay) return;

    VDP_drawText("PSEUDO3D TOWER LAB", 10, 0);
    sprintf(line, "base:%d phase:%u", sBaseScroll, sPhase);
    VDP_drawText(line, 3, 1);
    VDP_drawText("LEFT/RIGHT depth  A overlay  B menu", 1, 2);
}

void SCENE_pseudo3dTowerLabEnter(void)
{
    u16 base = TILE_USER_INDEX;
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_COLUMN);

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

    sBaseScroll = 16;
    sPhase = 0;
    sOverlay = TRUE;
    SCENE_towerWriteEvidenceBlock();
    SCENE_towerDrawOverlay();
}

void SCENE_pseudo3dTowerLabUpdate(void)
{
    u16 i;
    if (INPUT_pressed(BUTTON_B))
    {
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
        VDP_setVerticalScroll(BG_A, 0);
        VDP_setVerticalScroll(BG_B, 0);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (INPUT_pressed(BUTTON_A)) sOverlay = !sOverlay;
    if (INPUT_held(BUTTON_LEFT)) sBaseScroll--;
    if (INPUT_held(BUTTON_RIGHT)) sBaseScroll++;

    if (sBaseScroll < 0) sBaseScroll = 0;
    if (sBaseScroll > 48) sBaseScroll = 48;

    for (i = 0; i < TOWER_COLUMNS; i++)
    {
        fix16 wobble = F16_sin(FIX16((sPhase + (i * 13)) % 360));
        s16 depth = (s16)(sBaseScroll + i);
        sColumnScroll[i] = (s16)(F16_toInt(F16_mul(wobble, FIX16(6))) + depth);
    }

    VDP_setVerticalScrollTile(BG_A, 0, sColumnScroll, TOWER_COLUMNS, DMA_QUEUE);
    VDP_setHorizontalScroll(BG_B, -(sPhase >> 1));
    sPhase = (u16)((sPhase + 2) % 360);

    if ((gApp.sceneFrames & 63u) == 0u) SCENE_towerWriteEvidenceBlock();

    SCENE_towerDrawOverlay();
}

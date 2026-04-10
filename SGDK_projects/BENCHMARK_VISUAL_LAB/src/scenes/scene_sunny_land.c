#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/input.h"

#define SUNNY_VLAB_SCENE_ID 4
#define SUNNY_VLAB_VERSION 2
#define SUNNY_VLAB_BLOCK_SIZE 160
#define SUNNY_BG_SCROLL_INITIAL 43
#define SUNNY_BG_SCROLL_MIN 0
#define SUNNY_BG_SCROLL_MAX 64

static bool sShowOverlay = TRUE;
static bool sAutoDrift = TRUE;
static s16 sBgScroll = SUNNY_BG_SCROLL_INITIAL;
static s16 sBgVelocity = 1;

static void SCENE_sunnyLandSramWriteU16BE(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8) ((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8) (value & 0xFF));
}

static void SCENE_sunnyLandSramWriteU32BE(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8) ((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8) ((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8) ((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8) (value & 0xFF));
}

static void SCENE_sunnyLandSramWriteAscii(u32 offset, const char* text, u16 maxLen)
{
    u16 i = 0;

    while ((i < maxLen) && text[i])
    {
        SRAM_writeByte(offset + i, (u8) text[i]);
        i++;
    }

    while (i < maxLen)
    {
        SRAM_writeByte(offset + i, 0);
        i++;
    }
}

static void SCENE_sunnyLandWriteEvidenceBlock(void)
{
    u16 pal0[16];
    u16 pal1[16];
    u16 index;
    u8 flags = 0;

    if (sShowOverlay) flags |= 0x01;
    if (sAutoDrift) flags |= 0x02;

    PAL_getPalette(PAL0, pal0);
    PAL_getPalette(PAL1, pal1);

    SRAM_enable();

    SRAM_writeByte(0, 'V');
    SRAM_writeByte(1, 'L');
    SRAM_writeByte(2, 'A');
    SRAM_writeByte(3, 'B');
    SCENE_sunnyLandSramWriteU16BE(4, SUNNY_VLAB_VERSION);
    SCENE_sunnyLandSramWriteU16BE(6, SUNNY_VLAB_BLOCK_SIZE);
    SCENE_sunnyLandSramWriteU32BE(8, gApp.totalFrames);
    SRAM_writeByte(12, flags);
    SRAM_writeByte(13, SUNNY_VLAB_SCENE_ID);
    SRAM_writeByte(14, (u8) sBgScroll);
    SRAM_writeByte(15, (u8) (sBgVelocity & 0xFF));
    SCENE_sunnyLandSramWriteU16BE(16, sunny_land_bg_b.tileset->numTile + sunny_land_bg_a.tileset->numTile);
    SCENE_sunnyLandSramWriteU16BE(18, 0);
    SCENE_sunnyLandSramWriteU16BE(20, VDP_getPlaneAddress(BG_B, 0, 0));
    SCENE_sunnyLandSramWriteU16BE(22, VDP_getPlaneAddress(BG_A, 0, 0));

    for (index = 0; index < 16; index++)
    {
        SCENE_sunnyLandSramWriteU16BE(24 + (index * 2), pal0[index]);
        SCENE_sunnyLandSramWriteU16BE(56 + (index * 2), pal1[index]);
    }

    SCENE_sunnyLandSramWriteAscii(88, "sunny_land", 32);
    SCENE_sunnyLandSramWriteU32BE(120, 320);
    SCENE_sunnyLandSramWriteU32BE(124, SUNNY_BG_SCROLL_MAX);
    SCENE_sunnyLandSramWriteU32BE(128, (u32) sBgScroll);
    SCENE_sunnyLandSramWriteAscii(132, "proof-bg_b-parallax-bg_a", 24);
    SCENE_sunnyLandSramWriteAscii(156, "MD", 2);
    SRAM_writeByte(158, 3);
    SRAM_writeByte(159, 20);

    SRAM_disable();
}

static void SCENE_sunnyLandApplyScroll(void)
{
    VDP_setHorizontalScroll(BG_B, -sBgScroll);
    VDP_setHorizontalScroll(BG_A, 0);
}

static void SCENE_sunnyLandDrawOverlay(void)
{
    char line[40];

    VDP_clearTextArea(0, 0, 40, 3);

    if (!sShowOverlay)
    {
        return;
    }

    VDP_drawText("SUNNY LAND PROOF", 12, 0);
    sprintf(line, "SCROLL %02d  %s", sBgScroll, sAutoDrift ? "AUTO" : "MANUAL");
    VDP_drawText(line, 8, 1);
    VDP_drawText("A overlay  LEFT/RIGHT scroll  B menu", 1, 2);
}

void SCENE_sunnyLandEnter(void)
{
    const u16 bgBase = TILE_USER_INDEX;
    const u16 fgBase = bgBase + sunny_land_bg_b.tileset->numTile;

    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setPlaneSize(64, 32, TRUE);

    PAL_setPalette(PAL0, sunny_land_bg_b.palette->data, DMA);
    PAL_setPalette(PAL1, sunny_land_bg_a.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    VDP_setBackgroundColor(0);
    PAL_setColor(0, sunny_land_bg_b.palette->data[0]);

    VDP_drawImageEx(BG_B, &sunny_land_bg_b, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, bgBase), 0, 0, FALSE, TRUE);
    VDP_drawImageEx(BG_A, &sunny_land_bg_a, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, fgBase), 0, 0, FALSE, TRUE);

    sShowOverlay = TRUE;
    sAutoDrift = TRUE;
    sBgScroll = SUNNY_BG_SCROLL_INITIAL;
    sBgVelocity = 1;

    SCENE_sunnyLandApplyScroll();
    SCENE_sunnyLandWriteEvidenceBlock();
    SCENE_sunnyLandDrawOverlay();
}

void SCENE_sunnyLandUpdate(void)
{
    if (INPUT_pressed(BUTTON_B))
    {
        VDP_clearPlane(BG_A, TRUE);
        VDP_clearPlane(BG_B, TRUE);
        VDP_setHorizontalScroll(BG_A, 0);
        VDP_setHorizontalScroll(BG_B, 0);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (INPUT_pressed(BUTTON_A))
    {
        sShowOverlay = !sShowOverlay;
    }

    if (INPUT_pressed(BUTTON_START))
    {
        sAutoDrift = !sAutoDrift;
    }

    if (INPUT_held(BUTTON_LEFT))
    {
        sBgScroll--;
        sAutoDrift = FALSE;
    }
    else if (INPUT_held(BUTTON_RIGHT))
    {
        sBgScroll++;
        sAutoDrift = FALSE;
    }

    if (sAutoDrift && ((gApp.sceneFrames & 1u) == 0u))
    {
        sBgScroll += sBgVelocity;
        if (sBgScroll <= SUNNY_BG_SCROLL_MIN)
        {
            sBgScroll = SUNNY_BG_SCROLL_MIN;
            sBgVelocity = 1;
        }
        else if (sBgScroll >= SUNNY_BG_SCROLL_MAX)
        {
            sBgScroll = SUNNY_BG_SCROLL_MAX;
            sBgVelocity = -1;
        }
    }

    if (sBgScroll < SUNNY_BG_SCROLL_MIN)
    {
        sBgScroll = SUNNY_BG_SCROLL_MIN;
    }
    else if (sBgScroll > SUNNY_BG_SCROLL_MAX)
    {
        sBgScroll = SUNNY_BG_SCROLL_MAX;
    }

    SCENE_sunnyLandApplyScroll();
    SCENE_sunnyLandWriteEvidenceBlock();
    SCENE_sunnyLandDrawOverlay();
}

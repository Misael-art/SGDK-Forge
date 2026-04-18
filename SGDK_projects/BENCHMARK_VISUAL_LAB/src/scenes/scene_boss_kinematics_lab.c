#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/input.h"

#define FK_SEGMENTS 4
#define FK_SCENE_ID 9
#define FK_VLAB_VERSION 2
#define FK_VLAB_BLOCK_SIZE 160

static Sprite* sBossRoot = NULL;
static Sprite* sChain[FK_SEGMENTS];
static fix16 sRootX;
static fix16 sRootY;
static u16 sPhase;
static bool sOverlay;

static void SCENE_fkSramWriteU16BE(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static void SCENE_fkSramWriteU32BE(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8)((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8)(value & 0xFF));
}

static void SCENE_fkSramWriteAscii(u32 offset, const char* text, u16 maxLen)
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

static void SCENE_fkWriteEvidenceBlock(void)
{
    u16 palBoss[16];
    u16 palChain[16];
    u16 index;
    u8 flags = 0;

    if (sOverlay) flags |= 0x01;

    PAL_getPalette(PAL2, palBoss);
    PAL_getPalette(PAL1, palChain);

    SRAM_enable();

    SRAM_writeByte(0, 'V');
    SRAM_writeByte(1, 'L');
    SRAM_writeByte(2, 'A');
    SRAM_writeByte(3, 'B');
    SCENE_fkSramWriteU16BE(4, FK_VLAB_VERSION);
    SCENE_fkSramWriteU16BE(6, FK_VLAB_BLOCK_SIZE);
    SCENE_fkSramWriteU32BE(8, gApp.totalFrames);
    SRAM_writeByte(12, flags);
    SRAM_writeByte(13, FK_SCENE_ID);
    SRAM_writeByte(14, (u8)(sPhase & 0xFF));
    SRAM_writeByte(15, (u8)(F16_toInt(sRootX) & 0xFF));
    SCENE_fkSramWriteU16BE(16, 0);
    SCENE_fkSramWriteU16BE(18, (u16)(FK_SEGMENTS + 1));
    SCENE_fkSramWriteU16BE(20, 0);
    SCENE_fkSramWriteU16BE(22, 0);

    for (index = 0; index < 16; index++)
    {
        SCENE_fkSramWriteU16BE(24 + (index * 2), palBoss[index]);
        SCENE_fkSramWriteU16BE(56 + (index * 2), palChain[index]);
    }

    SCENE_fkSramWriteAscii(88, "boss_kinematics_lab", 32);
    SCENE_fkSramWriteU32BE(120, 224);
    SCENE_fkSramWriteU32BE(124, FK_SEGMENTS);
    SCENE_fkSramWriteU32BE(128, (u32)sPhase);
    SCENE_fkSramWriteAscii(132, "fix16_fk_chain", 24);
    SCENE_fkSramWriteAscii(156, "MD", 2);
    SRAM_writeByte(158, 3);
    SRAM_writeByte(159, 4);

    SRAM_disable();
}

static void SCENE_fkDrawOverlay(void)
{
    char line[40];
    VDP_clearTextArea(0, 0, 40, 3);
    if (!sOverlay) return;

    VDP_drawText("BOSS KINEMATICS LAB", 10, 0);
    sprintf(line, "phase:%u root:%d,%d", sPhase, F16_toInt(sRootX), F16_toInt(sRootY));
    VDP_drawText(line, 1, 1);
    VDP_drawText("D-PAD move root  A overlay  B menu", 1, 2);
}

void SCENE_bossKinematicsLabEnter(void)
{
    u16 i;
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x141018));
    PAL_setPalette(PAL2, spr_gaira.palette->data, DMA);
    PAL_setPalette(PAL1, spr_hero.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);

    sRootX = FIX16(136);
    sRootY = FIX16(88);
    sPhase = 0;
    sOverlay = TRUE;

    sBossRoot = SPR_addSprite(&spr_gaira, F16_toInt(sRootX), F16_toInt(sRootY), TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    SPR_setAnim(sBossRoot, 0);

    for (i = 0; i < FK_SEGMENTS; i++)
    {
        sChain[i] = SPR_addSprite(&spr_hero, 0, 0, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
        SPR_setAnim(sChain[i], 0);
    }

    SCENE_fkWriteEvidenceBlock();
    SCENE_fkDrawOverlay();
}

void SCENE_bossKinematicsLabUpdate(void)
{
    u16 i;
    fix16 parentX;
    fix16 parentY;
    const fix16 segmentLen = FIX16(20);

    if (INPUT_pressed(BUTTON_B))
    {
        SPR_reset();
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (INPUT_pressed(BUTTON_A)) {
        sOverlay = !sOverlay;
    }

    if (INPUT_held(BUTTON_LEFT)) sRootX -= FIX16(1);
    if (INPUT_held(BUTTON_RIGHT)) sRootX += FIX16(1);
    if (INPUT_held(BUTTON_UP)) sRootY -= FIX16(1);
    if (INPUT_held(BUTTON_DOWN)) sRootY += FIX16(1);

    if (sRootX < FIX16(24)) sRootX = FIX16(24);
    if (sRootX > FIX16(264)) sRootX = FIX16(264);
    if (sRootY < FIX16(24)) sRootY = FIX16(24);
    if (sRootY > FIX16(150)) sRootY = FIX16(150);

    SPR_setPosition(sBossRoot, F16_toInt(sRootX), F16_toInt(sRootY));

    parentX = sRootX + FIX16(20);
    parentY = sRootY + FIX16(32);

    for (i = 0; i < FK_SEGMENTS; i++)
    {
        u16 ang = (u16)((sPhase + (i * 40)) % 360);
        fix16 sx = F16_cos(FIX16(ang));
        fix16 sy = F16_sin(FIX16(ang));
        fix16 childX = parentX + F16_mul(sx, segmentLen);
        fix16 childY = parentY + F16_mul(sy, segmentLen);
        SPR_setPosition(sChain[i], F16_toInt(childX), F16_toInt(childY));
        SPR_setHFlip(sChain[i], sx < 0);
        parentX = childX;
        parentY = childY;
    }

    sPhase = (u16)((sPhase + 3) % 360);
    if ((gApp.sceneFrames & 63u) == 0u) SCENE_fkWriteEvidenceBlock();

    SCENE_fkDrawOverlay();
    SPR_update();
}

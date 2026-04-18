#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

#define AUDIO_SCENE_ID 12
#define AUDIO_VLAB_VERSION 2
#define AUDIO_VLAB_BLOCK_SIZE 160

static bool sOverlay;
static bool sPaused;
static bool sPcmInit;

static u8 sPcmA[256] __attribute__((aligned(256)));
static u8 sPcmB[256] __attribute__((aligned(256)));
static u8 sPcmC[256] __attribute__((aligned(256)));

static void SCENE_audioSramWriteU16BE(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static void SCENE_audioSramWriteU32BE(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8)((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8)(value & 0xFF));
}

static void SCENE_audioSramWriteAscii(u32 offset, const char* text, u16 maxLen)
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

static void SCENE_audioWriteEvidenceBlock(void)
{
    u16 pal0[16];
    u16 pal1[16];
    u16 index;
    u8 flags = 0;
    u16 driver = Z80_getLoadedDriver();
    u8 pcmMask = XGM2_isPlayingPCM(SOUND_PCM_CH1_MSK | SOUND_PCM_CH2_MSK | SOUND_PCM_CH3_MSK);

    if (sOverlay) flags |= 0x01;
    if (sPaused) flags |= 0x02;
    if (XGM2_isPlaying()) flags |= 0x04;

    PAL_getPalette(PAL0, pal0);
    for (index = 0; index < 16; index++) pal1[index] = 0;

    SRAM_enable();

    SRAM_writeByte(0, 'V');
    SRAM_writeByte(1, 'L');
    SRAM_writeByte(2, 'A');
    SRAM_writeByte(3, 'B');
    SCENE_audioSramWriteU16BE(4, AUDIO_VLAB_VERSION);
    SCENE_audioSramWriteU16BE(6, AUDIO_VLAB_BLOCK_SIZE);
    SCENE_audioSramWriteU32BE(8, gApp.totalFrames);
    SRAM_writeByte(12, flags);
    SRAM_writeByte(13, AUDIO_SCENE_ID);
    SRAM_writeByte(14, (u8)(driver & 0xFF));
    SRAM_writeByte(15, pcmMask);
    SCENE_audioSramWriteU16BE(16, 0);
    SCENE_audioSramWriteU16BE(18, 0);
    SCENE_audioSramWriteU16BE(20, 0);
    SCENE_audioSramWriteU16BE(22, 0);

    for (index = 0; index < 16; index++)
    {
        SCENE_audioSramWriteU16BE(24 + (index * 2), pal0[index]);
        SCENE_audioSramWriteU16BE(56 + (index * 2), pal1[index]);
    }

    SCENE_audioSramWriteAscii(88, "audio_xgm2_lab", 32);
    SCENE_audioSramWriteU32BE(120, 224);
    SCENE_audioSramWriteU32BE(124, driver);
    SCENE_audioSramWriteU32BE(128, pcmMask);
    SCENE_audioSramWriteAscii(132, "xgm2_pcm_multiplex", 24);
    SCENE_audioSramWriteAscii(156, "MD", 2);
    SRAM_writeByte(158, 1);
    SRAM_writeByte(159, 0);

    SRAM_disable();
}

static void SCENE_audioDrawOverlay(void)
{
    char line[40];
    u16 driver = Z80_getLoadedDriver();
    u8 pcmMask = XGM2_isPlayingPCM(SOUND_PCM_CH1_MSK | SOUND_PCM_CH2_MSK | SOUND_PCM_CH3_MSK);

    VDP_clearTextArea(0, 0, 40, 8);
    if (!sOverlay) return;

    VDP_drawText("AUDIO XGM2 LAB", 13, 0);
    sprintf(line, "driver:%u xgm2_play:%s", driver, XGM2_isPlaying() ? "yes" : "no");
    VDP_drawText(line, 1, 1);
    sprintf(line, "pcm_mask:%u paused:%s", pcmMask, sPaused ? "yes" : "no");
    VDP_drawText(line, 1, 2);
    VDP_drawText("D-PAD play PCM (prio test)", 6, 4);
    VDP_drawText("A pause/resume  START stop", 6, 5);
    VDP_drawText("C reload driver  B menu", 8, 6);
    VDP_drawText("PCM uses CH2/CH3 + priorities", 3, 7);
}

void SCENE_audioXgm2LabEnter(void)
{
    u16 i;
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101018));
    PAL_setPalette(PAL0, palette_grey, DMA);
    VDP_setTextPalette(PAL0);

    Z80_loadDriver(Z80_DRIVER_XGM2, TRUE);
    sOverlay = TRUE;
    sPaused = FALSE;
    sPcmInit = TRUE;

    for (i = 0; i < 256; i++)
    {
        sPcmA[i] = (u8)i;
        sPcmB[i] = (u8)(255 - i);
        sPcmC[i] = (u8)((i & 31) << 3);
    }
    XGM2_playPCMEx(sPcmC, sizeof(sPcmC), SOUND_PCM_CH3, 6, TRUE, FALSE);
    SCENE_audioWriteEvidenceBlock();
    SCENE_audioDrawOverlay();
}

void SCENE_audioXgm2LabUpdate(void)
{
    if (INPUT_pressed(BUTTON_B))
    {
        XGM2_stop();
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (INPUT_pressed(BUTTON_A))
    {
        if (sPaused)
        {
            XGM2_resume();
            sPaused = FALSE;
        }
        else
        {
            XGM2_pause();
            sPaused = TRUE;
        }
    }

    if (INPUT_pressed(BUTTON_START))
    {
        XGM2_stop();
        XGM2_stopPCM(SOUND_PCM_CH2);
        XGM2_stopPCM(SOUND_PCM_CH3);
        sPaused = FALSE;
    }

    if (INPUT_pressed(BUTTON_C))
    {
        Z80_loadDriver(Z80_DRIVER_XGM2, TRUE);
        XGM2_stopPCM(SOUND_PCM_CH2);
        XGM2_stopPCM(SOUND_PCM_CH3);
        sPaused = FALSE;
    }

    if (sPcmInit)
    {
        if (INPUT_pressed(BUTTON_LEFT))
        {
            XGM2_playPCMEx(sPcmA, sizeof(sPcmA), SOUND_PCM_CH2, 2, FALSE, FALSE);
        }
        if (INPUT_pressed(BUTTON_RIGHT))
        {
            XGM2_playPCMEx(sPcmB, sizeof(sPcmB), SOUND_PCM_CH2, 12, FALSE, FALSE);
        }
        if (INPUT_pressed(BUTTON_UP))
        {
            XGM2_playPCMEx(sPcmC, sizeof(sPcmC), SOUND_PCM_CH3, 6, TRUE, FALSE);
        }
        if (INPUT_pressed(BUTTON_DOWN))
        {
            XGM2_playPCMEx(sPcmC, sizeof(sPcmC), SOUND_PCM_CH3, 14, TRUE, FALSE);
        }
    }

    if ((gApp.sceneFrames & 63u) == 0u) SCENE_audioWriteEvidenceBlock();

    SCENE_audioDrawOverlay();
}

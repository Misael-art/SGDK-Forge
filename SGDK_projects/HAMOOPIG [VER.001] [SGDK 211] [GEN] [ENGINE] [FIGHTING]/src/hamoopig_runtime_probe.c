#include <genesis.h>
#include <sprite_eng.h>
#include "hamoopig_runtime_probe.h"

#define HPRB_OFFSET 0x500u
#define HPRB_WORDS 21u
#define HPRB_SCHEMA 5u
#define HPRB_BYTES (8u + (HPRB_WORDS * 2u))
static u32 probeFrame;
static u32 probePeakDmaFrame, probePeakScanlineFrame;
static u16 probeMaxDma, probeMaxActive, probeMaxVdp, probeMaxScanline, probeSamples;
static u16 probeMaxPreSpriteDma, probeMaxSpriteDmaDelta;
static u16 probeMaxStageDma[5];
static u16 probeCurrentPreSpriteDma, probeCurrentSpriteDmaDelta;
static u16 probePeakPreAtMaxDma, probePeakSpriteDeltaAtMaxDma;

static void writeBE16(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)(value >> 8));
    SRAM_writeByte(offset + 1u, (u8)value);
}

static u16 scanlinePeak(void)
{
    u8 lines[224];
    Sprite *sprite = firstSprite;
    u16 line, peak = 0;
    for (line = 0; line < 224u; line++) lines[line] = 0;
    while (sprite)
    {
        if (sprite->frame && sprite->visibility != HIDDEN)
        {
            u16 index, count = (u16)(sprite->frame->numSprite & 0x7F);
            for (index = 0; index < count; index++)
            {
                const FrameVDPSprite *part = &sprite->frame->frameVDPSprites[index];
                s16 start = (s16)(sprite->y - 0x80) + (s16)part->offsetY;
                s16 end = start + (s16)(((part->size & 0x03u) + 1u) << 3);
                if (end <= 0 || start >= 224) continue;
                if (start < 0) start = 0;
                if (end > 224) end = 224;
                for (line = (u16)start; line < (u16)end; line++)
                {
                    if (lines[line] < 0xFFu) lines[line]++;
                    if (lines[line] > peak) peak = lines[line];
                }
            }
        }
        sprite = sprite->next;
    }
    return peak;
}

static void exportProbe(u8 scene)
{
    u32 offset = HPRB_OFFSET;
    SRAM_enable();
    SRAM_writeByte(offset + 0u, 'H'); SRAM_writeByte(offset + 1u, 'P');
    SRAM_writeByte(offset + 2u, 'R'); SRAM_writeByte(offset + 3u, 'B');
    writeBE16(offset + 4u, HPRB_SCHEMA); writeBE16(offset + 6u, HPRB_BYTES);
    offset += 8u;
    writeBE16(offset, (u16)(probeFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probeFrame); offset += 2u;
    writeBE16(offset, (u16)(probePeakDmaFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakDmaFrame); offset += 2u;
    writeBE16(offset, (u16)(probePeakScanlineFrame >> 16)); offset += 2u;
    writeBE16(offset, (u16)probePeakScanlineFrame); offset += 2u;
    writeBE16(offset, probeMaxDma); offset += 2u;
    writeBE16(offset, probeMaxActive); offset += 2u;
    writeBE16(offset, probeMaxVdp); offset += 2u;
    writeBE16(offset, probeMaxScanline); offset += 2u;
    writeBE16(offset, probeSamples); offset += 2u;
    writeBE16(offset, (u16)(scene | (SYS_isPAL() ? 0x8000u : 0u)));
    offset += 2u;
    writeBE16(offset, probeMaxPreSpriteDma); offset += 2u;
    writeBE16(offset, probeMaxSpriteDmaDelta); offset += 2u;
    writeBE16(offset, probeMaxStageDma[0]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[1]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[2]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[3]); offset += 2u;
    writeBE16(offset, probeMaxStageDma[4]); offset += 2u;
    writeBE16(offset, probePeakPreAtMaxDma); offset += 2u;
    writeBE16(offset, probePeakSpriteDeltaAtMaxDma);
    SRAM_disable();
}

void HAMOOPIG_probeInit(void)
{
    probeFrame = 0; probePeakDmaFrame = 0; probePeakScanlineFrame = 0;
    probeMaxDma = 0; probeMaxActive = 0;
    probeMaxVdp = 0; probeMaxScanline = 0; probeSamples = 0;
    probeMaxPreSpriteDma = 0; probeMaxSpriteDmaDelta = 0;
    probeMaxStageDma[0] = 0; probeMaxStageDma[1] = 0; probeMaxStageDma[2] = 0;
    probeMaxStageDma[3] = 0; probeMaxStageDma[4] = 0;
    probeCurrentPreSpriteDma = 0; probeCurrentSpriteDmaDelta = 0;
    probePeakPreAtMaxDma = 0; probePeakSpriteDeltaAtMaxDma = 0;
}

void HAMOOPIG_probeSpriteDma(u16 dmaBeforeSpriteUpdate)
{
    u16 dmaAfter = DMA_getQueueTransferSize();
    u16 delta = (dmaAfter >= dmaBeforeSpriteUpdate) ? (u16)(dmaAfter - dmaBeforeSpriteUpdate) : 0;
    probeCurrentPreSpriteDma = dmaBeforeSpriteUpdate;
    probeCurrentSpriteDmaDelta = delta;
    if (dmaBeforeSpriteUpdate > probeMaxPreSpriteDma) probeMaxPreSpriteDma = dmaBeforeSpriteUpdate;
    if (delta > probeMaxSpriteDmaDelta) probeMaxSpriteDmaDelta = delta;
}

void HAMOOPIG_probeStageDma(u8 stage, u16 dmaBeforeStage)
{
    u16 dmaAfter = DMA_getQueueTransferSize();
    u16 delta = (dmaAfter >= dmaBeforeStage) ? (u16)(dmaAfter - dmaBeforeStage) : 0;
    if (stage >= 1u && stage <= 5u && delta > probeMaxStageDma[stage - 1u])
        probeMaxStageDma[stage - 1u] = delta;
}

void HAMOOPIG_probeTick(u8 scene)
{
    u16 dma = DMA_getQueueTransferSize();
    u16 active = SPR_getNumActiveSprite();
    u16 vdp = SPR_getUsedVDPSprite();
    u16 scanline = scanlinePeak();
    probeFrame++;
    if (dma > probeMaxDma) {
        probeMaxDma = dma; probePeakDmaFrame = probeFrame;
        probePeakPreAtMaxDma = probeCurrentPreSpriteDma;
        probePeakSpriteDeltaAtMaxDma = probeCurrentSpriteDmaDelta;
    }
    if (active > probeMaxActive) probeMaxActive = active;
    if (vdp > probeMaxVdp) probeMaxVdp = vdp;
    if (scanline > probeMaxScanline) { probeMaxScanline = scanline; probePeakScanlineFrame = probeFrame; }
    if (probeSamples != 0xFFFFu) probeSamples++;
    if ((probeFrame % 30u) == 0u) exportProbe(scene);
}

u16 HAMOOPIG_probePeakDma(void) { return probeMaxDma; }
u16 HAMOOPIG_probePeakActiveSprites(void) { return probeMaxActive; }
u16 HAMOOPIG_probePeakScanlineSprites(void) { return probeMaxScanline; }
u16 HAMOOPIG_probePeakVdpSprites(void) { return probeMaxVdp; }

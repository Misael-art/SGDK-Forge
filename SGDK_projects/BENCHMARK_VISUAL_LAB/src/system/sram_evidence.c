#include "system/sram_evidence.h"

void EVIDENCE_writeU16BE(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8) ((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8) (value & 0xFF));
}

void EVIDENCE_writeU32BE(u32 offset, u32 value)
{
    SRAM_writeByte(offset, (u8) ((value >> 24) & 0xFF));
    SRAM_writeByte(offset + 1, (u8) ((value >> 16) & 0xFF));
    SRAM_writeByte(offset + 2, (u8) ((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 3, (u8) (value & 0xFF));
}

void EVIDENCE_writeAscii(u32 offset, const char* text, u16 maxLen)
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

void EVIDENCE_writeHeader(u16 version, u16 blockSize, u32 totalFrames, u8 sceneId)
{
    SRAM_writeByte(0, 'V');
    SRAM_writeByte(1, 'L');
    SRAM_writeByte(2, 'A');
    SRAM_writeByte(3, 'B');
    EVIDENCE_writeU16BE(4, version);
    EVIDENCE_writeU16BE(6, blockSize);
    EVIDENCE_writeU32BE(8, totalFrames);
    SRAM_writeByte(12, 0);
    SRAM_writeByte(13, sceneId);
}

void EVIDENCE_writePalette(u32 offset, u16 palIndex)
{
    u16 colors[16];
    u16 i;

    PAL_getPalette(palIndex, colors);

    for (i = 0; i < 16; i++)
    {
        EVIDENCE_writeU16BE(offset + (i * 2), colors[i]);
    }
}

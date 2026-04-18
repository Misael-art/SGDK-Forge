#ifndef SRAM_EVIDENCE_H
#define SRAM_EVIDENCE_H

#include <genesis.h>

void EVIDENCE_writeU16BE(u32 offset, u16 value);
void EVIDENCE_writeU32BE(u32 offset, u32 value);
void EVIDENCE_writeAscii(u32 offset, const char* text, u16 maxLen);
void EVIDENCE_writeHeader(u16 version, u16 blockSize, u32 totalFrames, u8 sceneId);
void EVIDENCE_writePalette(u32 offset, u16 palIndex);

#endif

#ifndef BLAZE_RUNTIME_PROBE_H
#define BLAZE_RUNTIME_PROBE_H

#include <genesis.h>

/* VLAB v1: 52 runtime words followed by 64 CRAM words. */
#define BLAZE_PROBE_METRIC_WORDS 52
#define BLAZE_PROBE_PALETTE_WORDS 64
#define BLAZE_PROBE_WARMUP_FRAMES 90
#define BLAZE_PROBE_EXPORT_PERIOD 60
#define BLAZE_PROBE_SRAM_OFFSET 0x200
#define BLAZE_PROBE_RANGE_WORD_OFFSET 43
#define BLAZE_PROBE_RANGE_CAPACITY 4

void BLAZE_RuntimeProbeInit(void);
void BLAZE_RuntimeProbeTick(void);
void BLAZE_RuntimeProbeRecordTileRange(u16 startTile, u16 tileCount);

/* Link-time wrapper used by main.c so every code-side tileset upload is measured. */
u16 BLAZE_VDP_loadTileSet(const TileSet *tileset, u16 index, TransferMethod tm);

#endif

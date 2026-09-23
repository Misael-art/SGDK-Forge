#ifndef SYSTEM_RUNTIME_PROBE_H
#define SYSTEM_RUNTIME_PROBE_H

#include <genesis.h>

/*
 * ROM-side measurement probe (FASE 3 harness).
 *
 * This module is INSTRUMENTATION ONLY. It owns no gameplay state and does not
 * include any game header. The game hands it a scene id; it never reads one.
 *
 * ---------------------------------------------------------------------------
 * SRAM MAP (logical byte offsets as seen by SRAM_readByte/SRAM_writeByte)
 * ---------------------------------------------------------------------------
 *   0x000 .. 0x0B7  VLAB  visual/telemetry block consumed by
 *                         tools/sgdk_wrapper/seal_fresh_evidence_bundle.py
 *                         layout: 'V','L','A','B', u16 schema, u16 total_bytes,
 *                         then (total_bytes-8)/2 big-endian u16 words:
 *                         words[0..23]  = metrics (fixed order, see below)
 *                         words[24..87] = 64 CRAM entries (PAL_getColors)
 *   0x100 .. 0x107  READY heartbeat ('R','E','A','D','Y' + 3-byte counter)
 *   0x120 .. 0x12B  SBIS QA bootstrap request (written by the HOST before
 *                         launch, consumed + cleared by the ROM at boot)
 *   0x200 .. 0x289  MDRT raw probe dump ('M','D','R','T', u16 schema,
 *                         u16 total_bytes, u16 word_count, then word_count
 *                         big-endian u16 words = g_mdRuntimeProbe[])
 *
 * The VLAB metric word order is DICTATED by the sealer. Do not reorder:
 *   0  scene id                    12 sprite list address
 *   1  frame counter, high 16      13 hscroll table address
 *   2  frame counter, low 16       14 background color
 *   3  screen width                15 frame counter snapshot (low 16)
 *   4  screen height               16 sample count
 *   5  plane width                 17 over-budget frames
 *   6  plane height                18 max cpu load
 *   7  hscroll mode                19 max cpu jitter
 *   8  vscroll mode                20 max sprites on a sampled scanline
 *   9  BG_A address                21 max used hardware VDP sprites
 *   10 BG_B address                22 active SGDK sprites
 *   11 window address              23 target fps
 *
 * ---------------------------------------------------------------------------
 * g_mdRuntimeProbe[] WORD MAP (MDRT payload)
 * ---------------------------------------------------------------------------
 *   0  'MD' magic            12 last cpu load
 *   1  'RT' magic            13 max cpu jitter
 *   2  schema version        14 max sprites on a sampled scanline
 *   3  REQUESTED scene id    15 reserved
 *      (0xFFFF = host asked for nothing)
 *   4  target fps            16 max used hardware VDP sprites
 *   5  ACTUAL scene id       17 active SGDK sprites
 *      measured this window
 *   6  frame counter hi      18..22 per-section peak raster-line cost
 *   7  reserved              23 cpu budget threshold
 *   8  frame counter lo      24 section count
 *   9  sample count          25 flags (bit0 bootstrap applied)
 *   10 over-budget frames    26..31 reserved
 *   11 max cpu load
 *   32.. cpu load samples (MD_RUNTIME_PROBE_MAX_SAMPLES entries)
 */

#define MD_RUNTIME_PROBE_VLAB_OFFSET 0x000u
#define MD_RUNTIME_PROBE_HEARTBEAT_OFFSET 0x100u
#define MD_RUNTIME_PROBE_BOOTSTRAP_OFFSET 0x120u
#define MD_RUNTIME_PROBE_SRAM_OFFSET 0x200u
#define MD_RUNTIME_PROBE_HEARTBEAT_PERIOD 30u

#define MD_RUNTIME_PROBE_MAX_SAMPLES 32u
#define MD_RUNTIME_PROBE_SAMPLE_OFFSET 32u
#define MD_RUNTIME_PROBE_WORD_COUNT \
    (MD_RUNTIME_PROBE_SAMPLE_OFFSET + MD_RUNTIME_PROBE_MAX_SAMPLES)

/* Per-subsystem raster-line attribution slots. */
#define PROBE_SECTION_COUNT 5u
#define PROBE_SECTION_INPUT 0u
#define PROBE_SECTION_SCENE 1u
#define PROBE_SECTION_AUDIO 2u
#define PROBE_SECTION_SPRITE 3u
#define PROBE_SECTION_VBLANK 4u

#define PROBE_FLAG_BOOTSTRAP_APPLIED 0x0001u

extern volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

/*
 * Tiny public API. Call PROBE_init() once at boot and PROBE_tick() exactly
 * once per main-loop iteration, AFTER SYS_doVBlankProcess().
 */
void PROBE_init(void);
void PROBE_tick(void);
void PROBE_setSceneId(u16 sceneId);
u16 PROBE_getSceneId(void);

/*
 * Raster-line attribution. Resolution is ONE SCANLINE (~488 68k cycles on
 * NTSC, ~0.4% of a frame): anything cheaper than a scanline reads as 0 or 1.
 * The measurement is wall-clock raster time, so any HInt/VInt that fires
 * inside the section is charged to the section. Cost of the instrumentation
 * itself is 2 VDP HV-counter reads per section per frame.
 */
void PROBE_beginSection(u8 section);
void PROBE_endSection(u8 section);

/*
 * Host-driven scene isolation. Reads the SBIS block the capture harness
 * writes into SRAM before launch and returns the requested scene id, or
 * `fallbackScene` when no valid request is present. The block is cleared on
 * read so a warm reset does not silently repeat it. When a request is honored
 * the probe LOCKS onto that scene id and stops resetting its metrics on scene
 * change, so the sampled window belongs to exactly one scene.
 */
u16 PROBE_resolveBootScene(u16 fallbackScene, u16 sceneCount);
bool PROBE_bootstrapWasApplied(void);

/* Explicit flushes; PROBE_tick() already schedules both periodically. */
void PROBE_exportMdrtToSram(void);
void PROBE_exportVlabToSram(void);
void PROBE_writeHeartbeat(void);

/* Legacy names kept so existing call sites keep building. */
#define MDRuntimeProbe_init PROBE_init
#define MDRuntimeProbe_tick PROBE_tick
#define MDRuntimeProbe_exportToSRAM PROBE_exportMdrtToSram
#define MDRuntimeProbe_writeHeartbeat PROBE_writeHeartbeat

#endif

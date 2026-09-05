#ifndef SYSTEM_PROBE_STAGE_H
#define SYSTEM_PROBE_STAGE_H

#include <genesis.h>

/*
 * Project-specific telemetry block: "KRB1" at SRAM 0x300.
 *
 * WHY A SECOND BLOCK instead of extending VLAB: the canonical sealer
 * tools/sgdk_wrapper/seal_fresh_evidence_bundle.py reads VLAB as
 * "words[0..23] are metrics, words[24..] are the 64 CRAM entries". Appending
 * metric words to VLAB would shift the palette and silently corrupt every
 * colour gate in the workspace. That sealer is shared canonical tooling and
 * AGENTS.md forbids changing it without human approval, so this project adds
 * its own block and its own reader in tools/harness/.
 *
 * WHAT THIS CAN AND CANNOT PROVE -- read before trusting a gate built on it:
 *  - cameraX and the HScroll samples are read from the values the ROM actually
 *    programmed this frame. They are DIRECT evidence of parallax speed and
 *    replace the screenshot forensics that failed on 2026-07-30.
 *  - the DMA counters come from DMA_getQueueTransferSize(), so they measure what
 *    was QUEUED, which is what the VBlank flush will move. Direct enough.
 *  - the Shadow/Highlight flag is a SHADOW COPY of what the ROM asked for.
 *    SGDK 2.11 exposes no way to read VDP register 0x0C back, so this proves
 *    INTENT, not hardware state. A gate on it must say so.
 *  - the priority-bit count is SAMPLED from a few nametable entries via raw VDP
 *    reads, not exhaustive.
 */

#define PROBE_STAGE_SRAM_OFFSET 0x300u
#define PROBE_STAGE_SCHEMA 1u
#define PROBE_STAGE_WORDS 23u

/* Scanlines sampled from the HScroll table, one per parallax band. */
#define PROBE_STAGE_HS_SKY_LINE 30u
#define PROBE_STAGE_HS_MOUNT_LINE 90u
#define PROBE_STAGE_HS_HILL_LINE 180u
#define PROBE_STAGE_HS_TERRAIN_LINE 200u

/* Published by the scene once per frame, before PROBE_tick(). */
void PROBE_STAGE_publishCamera(s16 cameraX);
void PROBE_STAGE_publishHScroll(s16 sky, s16 mount, s16 hill, s16 terrain);
void PROBE_STAGE_publishActors(u16 kirbyState, s16 kirbyX, s16 kirbyY,
                               u16 enemiesAlive);
void PROBE_STAGE_publishShadowHighlight(bool enabled);
void PROBE_STAGE_publishPlaytest(u16 visited, u16 step, bool finished);

void PROBE_STAGE_reset(void);
void PROBE_STAGE_tick(void);
void PROBE_STAGE_exportToSram(void);

#endif

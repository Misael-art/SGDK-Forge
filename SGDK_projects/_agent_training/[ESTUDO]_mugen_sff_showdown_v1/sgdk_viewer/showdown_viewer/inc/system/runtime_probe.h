#ifndef SYSTEM_RUNTIME_PROBE_H
#define SYSTEM_RUNTIME_PROBE_H

#include <genesis.h>

/*
 * Canonical ROM-side readiness probe for the SGDK wrapper.
 *
 * Contract (aligned with tools/sgdk_wrapper/.agent/ARCHITECTURE.md):
 *   - `SRAM_HEARTBEAT_OFFSET` (default 0x100) holds an ASCII "READY" tag
 *     followed by a 3-byte rolling frame counter. The tag is re-asserted
 *     every `MD_RUNTIME_PROBE_HEARTBEAT_PERIOD` frames AFTER the warmup
 *     window so one-shot emission is never a single point of failure.
 *   - The wrapper side (lib/blastem_automation.psm1) polls fresh SRAM
 *     snapshots under the project sandbox and uses FileSystemWatcher as
 *     fast-path; `press_until_ready:*` is the only canonical navigation
 *     step to reach a scene before capture.
 *
 * Adoption:
 *   Projects that want the canonical handshake copy both
 *   `inc/system/runtime_probe.h` and `src/system/runtime_probe.c` into
 *   their tree and call `MDRuntimeProbe_init()` once at APP_boot, then
 *   `MDRuntimeProbe_tick()` once per main-loop iteration.
 */

#define MD_RUNTIME_PROBE_WORD_COUNT 64
#define MD_RUNTIME_PROBE_MAX_SAMPLES 32
#define MD_RUNTIME_PROBE_SRAM_OFFSET 0
#define MD_RUNTIME_PROBE_HEARTBEAT_OFFSET 0x100
#define MD_RUNTIME_PROBE_HEARTBEAT_PERIOD 30

extern volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

void MDRuntimeProbe_init(void);
void MDRuntimeProbe_tick(void);
void MDRuntimeProbe_exportToSRAM(void);
void MDRuntimeProbe_writeHeartbeat(void);

#endif

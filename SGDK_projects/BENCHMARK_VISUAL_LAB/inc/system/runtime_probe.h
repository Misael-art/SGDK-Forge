#ifndef RUNTIME_PROBE_H
#define RUNTIME_PROBE_H

#include <genesis.h>

/*
 * Memory layout consumed by tools/sgdk_wrapper/bizhawk_runtime_capture.lua.
 * Offsets are 16-bit words; sample ring starts at word 32.
 */
#define MD_RUNTIME_PROBE_MAX_SAMPLES 2048
#define MD_RUNTIME_PROBE_WORD_COUNT (32 + MD_RUNTIME_PROBE_MAX_SAMPLES)
#define MD_RUNTIME_PROBE_SRAM_OFFSET 0x200

extern volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

void MDRuntimeProbe_init(void);
void MDRuntimeProbe_tick(void);
void MDRuntimeProbe_exportToSRAM(void);

#endif

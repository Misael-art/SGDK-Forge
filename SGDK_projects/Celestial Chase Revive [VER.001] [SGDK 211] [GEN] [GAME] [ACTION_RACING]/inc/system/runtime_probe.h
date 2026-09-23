#ifndef SYSTEM_RUNTIME_PROBE_H
#define SYSTEM_RUNTIME_PROBE_H

#include <genesis.h>

#define MD_RUNTIME_PROBE_MAX_SAMPLES 1800u
#define MD_RUNTIME_PROBE_SAMPLE_OFFSET 32u
#define MD_RUNTIME_PROBE_WORD_COUNT \
    (MD_RUNTIME_PROBE_SAMPLE_OFFSET + MD_RUNTIME_PROBE_MAX_SAMPLES)

#define MD_RUNTIME_PROBE_VLAB_OFFSET 0x000u
#define MD_RUNTIME_PROBE_HEARTBEAT_OFFSET 0x100u
#define MD_RUNTIME_PROBE_SRAM_OFFSET 0x200u
#define MD_RUNTIME_PROBE_HEARTBEAT_PERIOD 30u

extern volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

void MDRuntimeProbe_init(void);
void MDRuntimeProbe_tick(void);
void MDRuntimeProbe_exportToSRAM(void);
void MDRuntimeProbe_writeHeartbeat(void);
bool MDRuntimeProbe_shouldHoldScene(void);

#endif

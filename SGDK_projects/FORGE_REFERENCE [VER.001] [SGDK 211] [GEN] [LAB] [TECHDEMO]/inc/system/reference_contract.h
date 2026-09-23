#ifndef REFERENCE_CONTRACT_H
#define REFERENCE_CONTRACT_H

#include <genesis.h>

#define REF_STATE_MOVED 0x0001u
#define REF_STATE_AIRBORNE 0x0002u
#define REF_STATE_STATIC_TABLE_SKIPPED 0x0004u
#define REF_REQUIRED_STATES (REF_STATE_MOVED | REF_STATE_AIRBORNE | REF_STATE_STATIC_TABLE_SKIPPED)

void REF_init(s16 initialX, s16 initialY, s16 initialCameraX);
u16 REF_scriptHeld(u32 sceneFrame);
u16 REF_scriptPressed(u32 sceneFrame);
void REF_observe(s16 playerX, s16 playerY, bool grounded, s16 cameraX);
void REF_export(void);

#endif

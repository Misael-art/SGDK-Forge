#ifndef SYSTEM_TELEMETRY_H
#define SYSTEM_TELEMETRY_H

#include <genesis.h>
#include "gameplay/gotham_player.h"
#include "gameplay/gotham_boss.h"

typedef struct TelemetryData {
    u16 cpuLoad;        // 0..100%
    u16 fps;            // 60
    u16 activeSprites;  // HW sprites count
    u16 activeObjects;  // Total simulated entities
    u16 dmaBytesQueued; // VBlank DMA traffic
    bool showDetailedOverlay;
} TelemetryData;

void TELEMETRY_init(void);
void TELEMETRY_update(void);
void TELEMETRY_drawHud(GothamPlayer* player, GothamBoss* boss, u16 activeProjectiles, u16 activeEnemies);
void TELEMETRY_toggleOverlay(void);

#endif

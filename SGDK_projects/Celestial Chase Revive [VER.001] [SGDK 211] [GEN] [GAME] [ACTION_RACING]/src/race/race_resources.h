#ifndef RACE_RESOURCES_H
#define RACE_RESOURCES_H

#include <genesis.h>

typedef struct {
    u8 integrity;
    u8 lumen;
    u16 pressure;
    u8 pulse_cooldown;
    u8 pulse_active;
    u8 focus;
    u8 lumen_band;
    u16 pressure_accumulator;
} ResourceState;

void Resources_init(void);
void Resources_update(void);
void Resources_addLumen(u8 amount);
void Resources_addPressure(u8 amount);
void Resources_applyDamage(void);
void Resources_updatePressure(u16 rate_per_sec);
bool Resources_usePulse(void);
u8 Resources_getLumenBand(void);
bool Resources_isDead(void);
u8 Resources_getIntegrity(void);
u8 Resources_getLumen(void);
u16 Resources_getPressure(void);
u8 Resources_getFocus(void);
void Resources_setPulseActive(u8 frames);
bool Resources_isPulseReady(void);
void Resources_setExtraPressurePerSecond(u8 extra);
u8 Resources_getExtraPressurePerSecond(void);

#endif

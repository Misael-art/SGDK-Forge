#ifndef SYSTEM_CAMERA_H
#define SYSTEM_CAMERA_H

#include <genesis.h>

void CAMERA_init(s16 minX, s16 maxX, s16 initialX);
void CAMERA_update(fix16 targetWorldX, bool facingRight);
void CAMERA_reset(void);
s16 CAMERA_getX(void);

#endif

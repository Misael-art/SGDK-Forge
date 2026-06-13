#ifndef GAMEPLAY_CHASE_ROAD_H
#define GAMEPLAY_CHASE_ROAD_H

#include <genesis.h>

void CHASE_ROAD_enter(u16 letterboxTileIndex);
void CHASE_ROAD_update(u32 frame, u8 phase, s16 shakeX, s16 shakeY, bool advance);
void CHASE_ROAD_setClimax(bool active);
void CHASE_ROAD_exit(void);

#endif

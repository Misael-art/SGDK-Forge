#ifndef GAMEPLAY_CHASE_PLAYER_H
#define GAMEPLAY_CHASE_PLAYER_H

#include <genesis.h>

void CHASE_PLAYER_enter(void);
void CHASE_PLAYER_update(bool controlEnabled, bool allowAnimationUpload);
void CHASE_PLAYER_triggerAfterimage(u16 frames);
void CHASE_PLAYER_setVisible(bool visible);
void CHASE_PLAYER_exit(void);
u8 CHASE_PLAYER_lane(void);
bool CHASE_PLAYER_isAirborne(void);
s16 CHASE_PLAYER_x(void);
s16 CHASE_PLAYER_y(void);

#endif

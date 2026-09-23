#ifndef ENTITIES_CRIA_H
#define ENTITIES_CRIA_H

#include <genesis.h>

bool CRIA_enter(s16 cameraX);
void CRIA_update(fix16 playerX, fix16 playerY, bool playerGrounded, s16 cameraX, s16 *knockbackX);
bool CRIA_receiveHit(fix16 attackerX, bool attackerFacingRight, u8 damage, s16 knockbackPx);
bool CRIA_isActive(void);
u8 CRIA_getHealth(void);
void CRIA_exit(void);

#endif

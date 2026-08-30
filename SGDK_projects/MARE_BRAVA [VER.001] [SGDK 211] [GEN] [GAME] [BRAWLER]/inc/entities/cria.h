#ifndef ENTITIES_CRIA_H
#define ENTITIES_CRIA_H

#include <genesis.h>

bool CRIA_enter(s16 cameraX);
void CRIA_update(fix16 playerX, fix16 playerY, bool playerGrounded, s16 cameraX, s16 *knockbackX);
void CRIA_exit(void);

#endif

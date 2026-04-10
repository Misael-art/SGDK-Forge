#ifndef PLAYER_H
#define PLAYER_H

#include <genesis.h>

typedef struct {
    Sprite* sprite;
    int x, y;
    int moveFrame;
    int frameCounter;
} Player;

void PLAYER_init(Player* p);
void PLAYER_handleInput(void* context);

#endif

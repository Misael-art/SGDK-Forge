#ifndef GAME_VARS_H
#define GAME_VARS_H

#include <genesis.h>

typedef enum
{
    TELA_DEMO_INTRO = 0,
    GAMEPLAY = 1
} Room;

extern Room gRoom;
extern u32 gFrames;

#endif


#ifndef GAME_VARS_H
#define GAME_VARS_H

#include <genesis.h>

typedef enum
{
    LAB_BOOT = 0
} Room;

typedef enum
{
    SILHOUETTE_LAB = 0,
    LAYER_CONTRAST_LAB = 1,
    ANIMATION_READABILITY_LAB = 2,
    LAB_MODE_COUNT = 3
} VisualLabMode;

extern Room gRoom;
extern VisualLabMode gLabMode;
extern u32 gFrames;
extern u16 gPrevInput;

#endif

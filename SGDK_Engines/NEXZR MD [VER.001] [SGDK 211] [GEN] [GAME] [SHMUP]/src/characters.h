#ifndef CHARACTERS_H
#define CHARACTERS_H

#include <genesis.h>
#include "resources.h"

typedef enum {
    FONT_ACTIVE = 0,
    FONT_INACTIVE = 2
} FontState;

void Characters_init();
void Characters_prepareToPrint();
void Characters_print(const char* str, u16 x, u16 y, FontState state);
void Characters_clearXY(u16 x, u16 y, u16 width);

#endif
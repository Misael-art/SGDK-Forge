#include <genesis.h>

#include "game_vars.h"
#include "system/input.h"

static u16 sPrevState = 0;

void INPUT_init(void)
{
    sPrevState = 0;
    gInput.held = 0;
    gInput.pressed = 0;
    gInput.released = 0;
}

void INPUT_update(void)
{
    u16 current = JOY_readJoypad(JOY_1);
    gInput.pressed = current & ~sPrevState;
    gInput.released = sPrevState & ~current;
    gInput.held = current;
    sPrevState = current;
}

bool INPUT_pressed(u16 buttonMask)
{
    return (gInput.pressed & buttonMask) != 0;
}

bool INPUT_held(u16 buttonMask)
{
    return (gInput.held & buttonMask) != 0;
}

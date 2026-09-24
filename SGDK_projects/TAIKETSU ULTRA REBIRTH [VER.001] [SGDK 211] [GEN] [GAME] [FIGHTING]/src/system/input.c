#include <genesis.h>

#include "game_vars.h"
#include "system/input.h"

static u16 sPrevState = 0;
static u8 sHeldFrames[16];

#define INPUT_REPEAT_DELAY 18
#define INPUT_REPEAT_PERIOD 5

void INPUT_init(void)
{
    JOY_setSupport(PORT_1, JOY_SUPPORT_6BTN);
    sPrevState = 0;
    gInput.held = 0;
    gInput.pressed = 0;
    gInput.released = 0;
    gInput.repeat = 0;
    gInput.sixButton = (JOY_getJoypadType(JOY_1) == JOY_TYPE_PAD6);
    memset(sHeldFrames, 0, sizeof(sHeldFrames));
}

void INPUT_update(void)
{
    u16 current = JOY_readJoypad(JOY_1);
    gInput.pressed = current & ~sPrevState;
    gInput.released = sPrevState & ~current;
    gInput.held = current;
    gInput.repeat = gInput.pressed;
    {
        u16 bit = 1;
        u8 i;
        for (i = 0; i < 16; i++) {
            if (current & bit) {
                if (sHeldFrames[i] < 255) sHeldFrames[i]++;
                if (sHeldFrames[i] >= INPUT_REPEAT_DELAY
                    && ((sHeldFrames[i] - INPUT_REPEAT_DELAY) % INPUT_REPEAT_PERIOD) == 0) {
                    gInput.repeat |= bit;
                }
            } else {
                sHeldFrames[i] = 0;
            }
            bit <<= 1;
        }
    }
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

bool INPUT_released(u16 buttonMask)
{
    return (gInput.released & buttonMask) != 0;
}

bool INPUT_repeat(u16 buttonMask)
{
    return (gInput.repeat & buttonMask) != 0;
}

bool INPUT_hasSixButtonPad(void)
{
    return gInput.sixButton;
}

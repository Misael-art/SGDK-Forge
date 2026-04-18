/* =========================================================================
 * input.c — Joypad handling with pressed/held/released masks
 * ========================================================================= */

#include "pp2.h"

static u16 s_prev = 0;

void Input_init(void)
{
    JOY_init();
    s_prev = 0;
    g_ctx.joyHeld     = 0;
    g_ctx.joyPressed  = 0;
    g_ctx.joyReleased = 0;
}

void Input_update(void)
{
    u16 held = JOY_readJoypad(JOY_1);

    g_ctx.joyHeld     = held;
    g_ctx.joyPressed  = held & ~s_prev;    /* newly pressed this frame */
    g_ctx.joyReleased = s_prev & ~held;    /* released this frame */

    s_prev = held;
}

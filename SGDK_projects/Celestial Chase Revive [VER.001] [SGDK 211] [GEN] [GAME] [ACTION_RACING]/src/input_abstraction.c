#include "input_abstraction.h"

static u16 current_joy_state = 0;
static u16 previous_joy_state = 0;
static u16 observed_joy_state = 0;
static bool input_locked = false;

static const u16 action_button_map[INPUT_ACTION_COUNT] = {
    BUTTON_UP,    /* INPUT_ACTION_UP */
    BUTTON_DOWN,  /* INPUT_ACTION_DOWN */
    BUTTON_A,     /* INPUT_ACTION_A */
    BUTTON_B,     /* INPUT_ACTION_B */
    BUTTON_START  /* INPUT_ACTION_START */
};

void IO_init(void)
{
    JOY_init();
    current_joy_state = 0;
    previous_joy_state = 0;
    observed_joy_state = 0;
    input_locked = false;
}

void IO_update(void)
{
    previous_joy_state = current_joy_state;
    JOY_update();

    if (input_locked)
    {
        current_joy_state = 0;
    }
    else
    {
        current_joy_state = JOY_readJoypad(JOY_1);
        observed_joy_state |= current_joy_state;
    }
}

InputState IO_getState(InputAction action)
{
    InputState state = { false, false, false };

    if (action >= INPUT_ACTION_COUNT)
    {
        return state;
    }

    u16 raw_button = action_button_map[action];
    bool cur = (current_joy_state & raw_button) != 0;
    bool prev = (previous_joy_state & raw_button) != 0;

    state.held = cur;
    state.pressed = cur && !prev;
    state.released = !cur && prev;

    return state;
}

void IO_setLocked(bool locked)
{
    input_locked = locked;
    if (locked)
    {
        current_joy_state = 0;
        previous_joy_state = 0;
    }
}

u16 IO_getRawState(void)
{
    return current_joy_state;
}

u16 IO_getObservedState(void)
{
    return observed_joy_state;
}

bool IO_isLocked(void)
{
    return input_locked;
}

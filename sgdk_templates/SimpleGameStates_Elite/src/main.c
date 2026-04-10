#include <genesis.h>

#include "game_states.h"

/**
 * ELITE MODULAR FSM TEMPLATE
 * Objective: Clean separation of game states using function pointers.
 */

int main(bool hardReset)
{
    // Start at the menu state
    set_state(state_menu_update);

    while(TRUE)
    {
        // Execute the logic of the current state
        if (currentStateUpdate) {
            currentStateUpdate();
        }

        SYS_doVBlankProcess();
    }
    return 0;
}

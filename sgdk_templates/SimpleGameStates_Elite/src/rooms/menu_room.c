#include "game_states.h"

void state_menu_update() {
    VDP_drawText("MENU - Pressione START", 10, 13);
    
    u16 joy = JOY_readJoypad(JOY_1);
    if (joy & BUTTON_START) {
        VDP_clearTextArea(10, 13, 30, 1);
        set_state(state_game_update);
    }
}

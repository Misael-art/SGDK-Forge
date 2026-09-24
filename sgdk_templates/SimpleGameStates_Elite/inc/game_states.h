#ifndef GAME_STATES_H
#define GAME_STATES_H

#include <genesis.h>

typedef void StateFunction();

extern StateFunction* currentStateUpdate;

void set_state(StateFunction* nextState);

// State Prototypes (Rooms)
void state_menu_update();
void state_game_update();

#endif

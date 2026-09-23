#include "game_states.h"

StateFunction* currentStateUpdate = NULL;

void set_state(StateFunction* nextState) {
    currentStateUpdate = nextState;
}

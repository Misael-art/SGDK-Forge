#ifndef INPUT_ABSTRACTION_H
#define INPUT_ABSTRACTION_H

#include <genesis.h>

typedef enum {
    INPUT_ACTION_UP,
    INPUT_ACTION_DOWN,
    INPUT_ACTION_A,
    INPUT_ACTION_B,
    INPUT_ACTION_START,
    INPUT_ACTION_COUNT
} InputAction;

typedef struct {
    bool pressed;
    bool held;
    bool released;
} InputState;

void IO_init(void);
void IO_update(void);
InputState IO_getState(InputAction action);
void IO_setLocked(bool locked);
u16 IO_getRawState(void);
u16 IO_getObservedState(void);
bool IO_isLocked(void);

#endif /* INPUT_ABSTRACTION_H */

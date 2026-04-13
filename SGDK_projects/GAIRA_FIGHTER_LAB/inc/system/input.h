#ifndef SYSTEM_INPUT_H
#define SYSTEM_INPUT_H

#include <genesis.h>

void INPUT_init(void);
void INPUT_update(void);
bool INPUT_pressed(u16 buttonMask);
bool INPUT_held(u16 buttonMask);

#endif

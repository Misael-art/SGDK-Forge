#ifndef SYSTEM_HINT_ARBITER_H
#define SYSTEM_HINT_ARBITER_H

#include <genesis.h>

typedef enum HINT_Owner {
    HINT_OWNER_NONE = 0,
    HINT_OWNER_MASKED_LIGHT = 1
} HINT_Owner;

bool HINT_acquire(HINT_Owner owner, VoidCallback* cb, u16 counter);
void HINT_release(HINT_Owner owner);
HINT_Owner HINT_getOwner(void);
void HINT_setCounter(u16 counter);

#endif

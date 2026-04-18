#include <genesis.h>

#include "system/hint_arbiter.h"

static HINT_Owner sOwner = HINT_OWNER_NONE;

bool HINT_acquire(HINT_Owner owner, VoidCallback* cb, u16 counter)
{
    if (owner == HINT_OWNER_NONE) return FALSE;
    if (sOwner != HINT_OWNER_NONE && sOwner != owner) return FALSE;

    sOwner = owner;
    VDP_setHIntCounter(counter);
    SYS_setHIntCallback(cb);
    VDP_setHInterrupt(TRUE);
    return TRUE;
}

void HINT_release(HINT_Owner owner)
{
    if (owner == HINT_OWNER_NONE) return;
    if (sOwner != owner) return;

    VDP_setHInterrupt(FALSE);
    SYS_setHIntCallback(NULL);
    sOwner = HINT_OWNER_NONE;
}

HINT_Owner HINT_getOwner(void)
{
    return sOwner;
}

void HINT_setCounter(u16 counter)
{
    if (sOwner == HINT_OWNER_NONE) return;
    VDP_setHIntCounter(counter);
}

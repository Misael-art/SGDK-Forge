#ifndef RACE_HUD_H
#define RACE_HUD_H

#include <genesis.h>
#include "race_resources.h"

void Hud_init(void);
void Hud_update(const ResourceState* res, bool pulse_ready);
void Hud_setVisible(bool visible);
void Hud_drawStatic(void);

#endif

#ifndef EFFECTS_H
#define EFFECTS_H

#include <genesis.h>

/* =========================================================================
 * EFFECTS — Screen shake, palette flash, ambient effects
 * ========================================================================= */

extern s16 shakeOffsetX;
extern s16 shakeOffsetY;

void EFFECTS_init(void);
void EFFECTS_update(void);
void EFFECTS_startShake(u16 magnitude, u16 duration);
void EFFECTS_startFlash(u16 duration);

#endif /* EFFECTS_H */

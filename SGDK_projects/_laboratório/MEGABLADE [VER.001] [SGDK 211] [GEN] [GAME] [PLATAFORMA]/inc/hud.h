#ifndef HUD_H
#define HUD_H

#include <genesis.h>

/* =========================================================================
 * HUD — Score, lives, status text on Window plane
 * ========================================================================= */

void HUD_init(void);
void HUD_updateScore(u32 score);
void HUD_updateLives(u8 lives);
void HUD_showMessage(const char* msg, u16 x, u16 y);
void HUD_clearMessage(u16 x, u16 y, u16 len);

#endif /* HUD_H */

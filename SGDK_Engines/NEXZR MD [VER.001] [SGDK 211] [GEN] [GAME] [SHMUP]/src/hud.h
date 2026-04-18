#ifndef HUD_H
#define HUD_H

#include <genesis.h>

void HUD_init();
void HUD_clear();
void HUD_setScore(unsigned int score);
void HUD_setLives(u8 lives);
void HUD_showPaused();

#endif
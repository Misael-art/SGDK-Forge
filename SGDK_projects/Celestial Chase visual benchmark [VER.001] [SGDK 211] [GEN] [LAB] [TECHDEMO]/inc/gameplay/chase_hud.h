#ifndef GAMEPLAY_CHASE_HUD_H
#define GAMEPLAY_CHASE_HUD_H

#include <genesis.h>

#include "gameplay/chase_rules.h"

void CHASE_HUD_enter(void);
void CHASE_HUD_update(const ChaseRulesState* rules);
void CHASE_HUD_setCinematic(bool active);
void CHASE_HUD_showPause(bool paused);
void CHASE_HUD_showResult(const ChaseRulesState* rules, u32 score, u32 highscore, bool newRecord);
void CHASE_HUD_exit(void);

#endif

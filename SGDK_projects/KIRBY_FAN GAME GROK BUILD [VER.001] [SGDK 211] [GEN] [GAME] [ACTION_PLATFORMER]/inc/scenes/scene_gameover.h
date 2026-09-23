#ifndef SCENES_SCENE_GAMEOVER_H
#define SCENES_SCENE_GAMEOVER_H

#include <genesis.h>

/* Outcome the previous scene handed over. */
typedef enum GameOutcome {
    OUTCOME_DEFEAT = 0,
    OUTCOME_VICTORY = 1
} GameOutcome;

void SCENE_setOutcome(GameOutcome outcome);

void SCENE_gameoverEnter(void);
void SCENE_gameoverUpdate(void);

#endif

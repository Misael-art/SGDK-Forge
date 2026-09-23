#ifndef GAMEPLAY_CHASE_OBSTACLES_H
#define GAMEPLAY_CHASE_OBSTACLES_H

#include <genesis.h>

#include "gameplay/chase_rules.h"

typedef struct ChaseObstacleEvents {
    bool damage;
    bool pickup;
} ChaseObstacleEvents;

void CHASE_OBSTACLES_enter(void);
ChaseObstacleEvents CHASE_OBSTACLES_update(const ChaseRulesState* rules, bool allowScaleUpload);
void CHASE_OBSTACLES_clearThreats(void);
void CHASE_OBSTACLES_exit(void);

#endif

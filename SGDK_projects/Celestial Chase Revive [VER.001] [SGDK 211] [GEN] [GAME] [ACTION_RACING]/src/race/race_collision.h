#ifndef RACE_COLLISION_H
#define RACE_COLLISION_H

#include <genesis.h>
#include "player/lane_movement.h"

void Collision_init(void);
bool Collision_overlap(const AABB* a, const AABB* b);

#endif

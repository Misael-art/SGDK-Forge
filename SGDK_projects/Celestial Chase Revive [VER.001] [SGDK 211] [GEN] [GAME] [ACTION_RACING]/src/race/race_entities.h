#ifndef RACE_ENTITIES_H
#define RACE_ENTITIES_H

#include <genesis.h>
#include "data/track_data.h"

typedef struct {
    u8 kind;
    u8 lane;
    u8 active;
    u8 variant;
    s16 value;
    u16 spawn_frame;
    u16 active_start_frame;
    u16 active_end_frame;
    u16 telegraph_start_frame;
    u8 telegraph_duration;
    u8 active_duration;
    s16 screen_x;
    s16 screen_y;
    u8 pool;
    u8 index_in_pool;
} Entity;

typedef struct {
    s16 x;
    s16 y;
    u16 w;
    u16 h;
    u8 layer;
    u8 entity_index;
    u8 kind;
} EntityCollisionData;

void Entities_init(void);
void Entities_spawnFromEvent(const TrackEvent* event, u16 current_frame);
void Entities_update(u16 current_frame, u16 scroll_x);
u8 Entities_getActiveCollisionData(EntityCollisionData* buffer, u8 max_count);
void Entities_despawn(u8 pool, u8 index);
void Entities_clearAll(void);
const Entity* Entities_getHazard(u8 index);
const Entity* Entities_getPickup(u8 index);
u8 Entities_getHazardCount(void);
u8 Entities_getPickupCount(void);
u8 Entities_getLaneFromMask(u8 lane_mask);
u8 Entities_getEntityLayer(u8 kind);

#endif

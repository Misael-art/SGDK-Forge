#include "race_entities.h"
#include "race/race_track.h"

static Entity hazards[ENTITY_POOL_HAZARDS];
static Entity pickups[ENTITY_POOL_PICKUPS];
static Entity fx_particles[ENTITY_POOL_FX];

static u8 hazard_count = 0;
static u8 pickup_count = 0;
static u8 fx_count = 0;

static const s16 lane_x_px[TRACK_LANES] = {
    TRACK_LANE_X_PX_0, TRACK_LANE_X_PX_1, TRACK_LANE_X_PX_2
};

void Entities_init(void)
{
    for (u8 i = 0; i < ENTITY_POOL_HAZARDS; i++)
    {
        hazards[i].active = 0;
        hazards[i].kind = EV_NONE;
        hazards[i].lane = 0;
    }
    for (u8 i = 0; i < ENTITY_POOL_PICKUPS; i++)
    {
        pickups[i].active = 0;
        pickups[i].kind = EV_NONE;
        pickups[i].lane = 0;
    }
    for (u8 i = 0; i < ENTITY_POOL_FX; i++)
    {
        fx_particles[i].active = 0;
    }
    hazard_count = 0;
    pickup_count = 0;
    fx_count = 0;
}

u8 Entities_getLaneFromMask(u8 lane_mask)
{
    if (lane_mask & LANE_LEFT) return 0;
    if (lane_mask & LANE_CENTER) return 1;
    if (lane_mask & LANE_RIGHT) return 2;
    return 1;
}

u8 Entities_getEntityLayer(u8 kind)
{
    switch (kind)
    {
        case EV_LOW_STONE:
            return COLLISION_LAYER_LOW_HAZARD;
        case EV_ASTRAL_MARK:
        case EV_PULSE_TUTORIAL:
            return COLLISION_LAYER_SOLID_HAZARD;
        case EV_LUMEN_ORB:
        case EV_BEACON_KEY:
            return COLLISION_LAYER_PICKUP;
        case EV_PURSUER_SHADOW:
        case EV_PRESSURE_GATE:
            return COLLISION_LAYER_TRIGGER;
        default:
            return COLLISION_LAYER_SOLID_HAZARD;
    }
}

void Entities_spawnFromEvent(const TrackEvent* event, u16 current_frame)
{
    u8 kind = event->event_kind;
    u8 layer = Entities_getEntityLayer(kind);

    u16 telegraph_frame = event->start_step * TRACK_STEP_FRAMES_NTSC;
    u16 active_start = (event->start_step + event->telegraph_steps) * TRACK_STEP_FRAMES_NTSC;
    u16 active_end = (event->start_step + event->telegraph_steps + event->active_steps) * TRACK_STEP_FRAMES_NTSC;

    Entity* pool = NULL;
    u8 pool_size = 0;
    u8* pool_count = NULL;
    u8 pool_id = 0;

    if (layer == COLLISION_LAYER_PICKUP || kind == EV_BEACON_KEY)
    {
        pool = pickups;
        pool_size = ENTITY_POOL_PICKUPS;
        pool_count = &pickup_count;
        pool_id = 1;
    }
    else
    {
        pool = hazards;
        pool_size = ENTITY_POOL_HAZARDS;
        pool_count = &hazard_count;
        pool_id = 0;
    }

    u8 lane_mask = event->lane_mask;
    for (u8 lane = 0; lane < TRACK_LANES; lane++)
    {
        if (!(lane_mask & (1 << lane)))
        {
            continue;
        }

        for (u8 i = 0; i < pool_size; i++)
        {
            if (!pool[i].active)
            {
                pool[i].active = 1;
                pool[i].kind = kind;
                pool[i].lane = lane;
                pool[i].variant = event->variant;
                pool[i].value = event->value;
                pool[i].spawn_frame = current_frame;
                pool[i].telegraph_start_frame = telegraph_frame;
                pool[i].telegraph_duration = event->telegraph_steps;
                pool[i].active_start_frame = active_start;
                pool[i].active_duration = event->active_steps;
                pool[i].active_end_frame = active_end;
                pool[i].screen_x = lane_x_px[lane];
                pool[i].screen_y = TRACK_TELEGRAPH_Y;
                pool[i].pool = pool_id;
                pool[i].index_in_pool = i;
                if (pool_count != NULL)
                {
                    (*pool_count)++;
                }
                break;
            }
        }
    }
}

void Entities_update(u16 current_frame, u16 scroll_x)
{
    (void)scroll_x;

    for (u8 i = 0; i < ENTITY_POOL_HAZARDS; i++)
    {
        Entity* e = &hazards[i];
        if (!e->active)
        {
            continue;
        }

        u16 active_start = e->active_start_frame;
        u16 active_end = e->active_end_frame;
        u16 telegraph_start = e->telegraph_start_frame;

        if (current_frame < telegraph_start)
        {
            e->screen_y = -32;
            e->active = 0;
            hazard_count--;
            continue;
        }

        if (current_frame < active_start)
        {
            u16 telegraph_elapsed = current_frame - telegraph_start;
            u16 telegraph_total = e->telegraph_duration * TRACK_STEP_FRAMES_NTSC;
            if (telegraph_total > 0)
            {
                s16 y_range = TRACK_TELEGRAPH_Y - (-16);
                e->screen_y = -16 + (y_range * telegraph_elapsed) / telegraph_total;
            }
            else
            {
                e->screen_y = TRACK_TELEGRAPH_Y;
            }
            e->screen_x = lane_x_px[e->lane];
            continue;
        }

        if (current_frame < active_end)
        {
            u16 active_elapsed = current_frame - active_start;
            u16 active_total = active_end - active_start;
            if (active_total > 0)
            {
                s16 y_range = TRACK_PLAYER_Y_PX - TRACK_TELEGRAPH_Y;
                e->screen_y = TRACK_TELEGRAPH_Y + (y_range * active_elapsed) / active_total;
            }
            else
            {
                e->screen_y = TRACK_PLAYER_Y_PX;
            }
            e->screen_x = lane_x_px[e->lane];
            continue;
        }

        e->active = 0;
        if (hazard_count > 0)
        {
            hazard_count--;
        }
    }

    for (u8 i = 0; i < ENTITY_POOL_PICKUPS; i++)
    {
        Entity* e = &pickups[i];
        if (!e->active)
        {
            continue;
        }

        u16 active_start = e->active_start_frame;
        u16 active_end = e->active_end_frame;
        u16 telegraph_start = e->telegraph_start_frame;

        if (current_frame < telegraph_start)
        {
            e->active = 0;
            pickup_count--;
            continue;
        }

        if (current_frame < active_start)
        {
            e->screen_y = TRACK_TELEGRAPH_Y;
            e->screen_x = lane_x_px[e->lane];
            continue;
        }

        if (current_frame < active_end)
        {
            u16 active_elapsed = current_frame - active_start;
            u16 active_total = active_end - active_start;
            if (active_total > 0)
            {
                s16 y_range = TRACK_PLAYER_Y_PX - TRACK_TELEGRAPH_Y;
                e->screen_y = TRACK_TELEGRAPH_Y + (y_range * active_elapsed) / active_total;
            }
            else
            {
                e->screen_y = TRACK_PLAYER_Y_PX;
            }
            e->screen_x = lane_x_px[e->lane];
            continue;
        }

        e->active = 0;
        if (pickup_count > 0)
        {
            pickup_count--;
        }
    }

    for (u8 i = 0; i < ENTITY_POOL_FX; i++)
    {
        Entity* e = &fx_particles[i];
        if (!e->active)
        {
            continue;
        }
        e->active = 0;
        if (fx_count > 0)
        {
            fx_count--;
        }
    }
}

u8 Entities_getActiveCollisionData(EntityCollisionData* buffer, u8 max_count)
{
    u8 count = 0;

    for (u8 i = 0; i < ENTITY_POOL_HAZARDS && count < max_count; i++)
    {
        Entity* e = &hazards[i];
        if (!e->active)
        {
            continue;
        }
        if (e->kind == EV_PURSUER_SHADOW)
        {
            continue;
        }

        buffer[count].entity_index = i;
        buffer[count].kind = e->kind;
        buffer[count].layer = Entities_getEntityLayer(e->kind);
        buffer[count].x = e->screen_x;
        buffer[count].y = e->screen_y;

        switch (e->kind)
        {
            case EV_LOW_STONE:
                buffer[count].x += ENTITY_LOW_STONE_HIT_X;
                buffer[count].y += ENTITY_LOW_STONE_HIT_Y;
                buffer[count].w = ENTITY_LOW_STONE_HIT_W;
                buffer[count].h = ENTITY_LOW_STONE_HIT_H;
                break;
            case EV_ASTRAL_MARK:
            case EV_PULSE_TUTORIAL:
            case EV_PRESSURE_GATE:
                buffer[count].x += ENTITY_ASTRAL_MARK_HIT_X;
                buffer[count].y += ENTITY_ASTRAL_MARK_HIT_Y;
                buffer[count].w = ENTITY_ASTRAL_MARK_HIT_W;
                buffer[count].h = ENTITY_ASTRAL_MARK_HIT_H;
                break;
            default:
                buffer[count].x += ENTITY_LUMEN_COLLECT_X;
                buffer[count].y += ENTITY_LUMEN_COLLECT_Y;
                buffer[count].w = ENTITY_LUMEN_COLLECT_W;
                buffer[count].h = ENTITY_LUMEN_COLLECT_H;
                break;
        }
        count++;
    }

    for (u8 i = 0; i < ENTITY_POOL_PICKUPS && count < max_count; i++)
    {
        Entity* e = &pickups[i];
        if (!e->active)
        {
            continue;
        }

        buffer[count].entity_index = i;
        buffer[count].kind = e->kind;
        buffer[count].layer = COLLISION_LAYER_PICKUP;
        buffer[count].x = e->screen_x;
        buffer[count].y = e->screen_y;

        if (e->kind == EV_BEACON_KEY)
        {
            buffer[count].x += ENTITY_BEACON_COLLECT_X;
            buffer[count].y += ENTITY_BEACON_COLLECT_Y;
            buffer[count].w = ENTITY_BEACON_COLLECT_W;
            buffer[count].h = ENTITY_BEACON_COLLECT_H;
        }
        else
        {
            buffer[count].x += ENTITY_LUMEN_COLLECT_X;
            buffer[count].y += ENTITY_LUMEN_COLLECT_Y;
            buffer[count].w = ENTITY_LUMEN_COLLECT_W;
            buffer[count].h = ENTITY_LUMEN_COLLECT_H;
        }
        count++;
    }

    return count;
}

void Entities_despawn(u8 pool, u8 index)
{
    if (pool == 0 && index < ENTITY_POOL_HAZARDS)
    {
        if (hazards[index].active)
        {
            hazards[index].active = 0;
            if (hazard_count > 0)
            {
                hazard_count--;
            }
        }
    }
    else if (pool == 1 && index < ENTITY_POOL_PICKUPS)
    {
        if (pickups[index].active)
        {
            pickups[index].active = 0;
            if (pickup_count > 0)
            {
                pickup_count--;
            }
        }
    }
}

void Entities_clearAll(void)
{
    for (u8 i = 0; i < ENTITY_POOL_HAZARDS; i++)
    {
        hazards[i].active = 0;
        hazards[i].kind = EV_NONE;
    }
    for (u8 i = 0; i < ENTITY_POOL_PICKUPS; i++)
    {
        pickups[i].active = 0;
        pickups[i].kind = EV_NONE;
    }
    for (u8 i = 0; i < ENTITY_POOL_FX; i++)
    {
        fx_particles[i].active = 0;
    }
    hazard_count = 0;
    pickup_count = 0;
    fx_count = 0;
}

const Entity* Entities_getHazard(u8 index)
{
    if (index < ENTITY_POOL_HAZARDS)
    {
        return &hazards[index];
    }
    return NULL;
}

const Entity* Entities_getPickup(u8 index)
{
    if (index < ENTITY_POOL_PICKUPS)
    {
        return &pickups[index];
    }
    return NULL;
}

u8 Entities_getHazardCount(void)
{
    return hazard_count;
}

u8 Entities_getPickupCount(void)
{
    return pickup_count;
}

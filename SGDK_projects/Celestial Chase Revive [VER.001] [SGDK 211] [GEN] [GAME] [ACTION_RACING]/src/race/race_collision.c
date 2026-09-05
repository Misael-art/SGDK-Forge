#include "race_collision.h"

void Collision_init(void)
{
}

bool Collision_overlap(const AABB* a, const AABB* b)
{
    if (a->x + (s16)a->w <= b->x)
    {
        return false;
    }
    if (b->x + (s16)b->w <= a->x)
    {
        return false;
    }
    if (a->y + (s16)a->h <= b->y)
    {
        return false;
    }
    if (b->y + (s16)b->h <= a->y)
    {
        return false;
    }
    return true;
}

#include <genesis.h>

#include "entities/enemy.h"
#include "systems/stage_map.h"

/* Inhale reach and strength. Tunables; nothing here is validated by playtest. */
#define INHALE_REACH   FIX16(72)
#define INHALE_HEIGHT  FIX16(20)
#define INHALE_PULL    FIX16(1.6)
#define SWALLOW_RANGE  FIX16(12)

#define ENEMY_WALK_SPEED FIX16(0.45)
#define ENEMY_ANIM_SPEED 10u

static Enemy s_pool[ENEMY_POOL_SIZE];

void ENEMY_initPool(void)
{
    u16 i;
    for (i = 0u; i < ENEMY_POOL_SIZE; i++)
    {
        s_pool[i].state = ENEMY_DEAD;
        s_pool[i].grants = ABILITY_NONE;
        s_pool[i].animFrame = 0u;
        s_pool[i].animTimer = 0u;
    }
}

Enemy* ENEMY_get(u16 index)
{
    return (index < ENEMY_POOL_SIZE) ? &s_pool[index] : NULL;
}

void ENEMY_spawn(u16 index, fix16 x, fix16 y, fix16 vx, CopyAbility grants)
{
    Enemy* e;
    if (index >= ENEMY_POOL_SIZE) return;

    e = &s_pool[index];
    e->x = x;
    e->y = y;
    e->vx = vx;
    e->state = ENEMY_WALK;
    e->grants = grants;
    e->animFrame = 0u;
    e->animTimer = 0u;
}

static bool inhale_zone(const Enemy* e, fix16 kx, fix16 ky, bool facingLeft)
{
    const fix16 dx = e->x - kx;
    const fix16 dy = (e->y > ky) ? (e->y - ky) : (ky - e->y);

    if (dy > INHALE_HEIGHT) return FALSE;

    /* The vortex is a cone in FRONT of Kirby only. */
    if (facingLeft) return (dx < FIX16(0)) && (dx > -INHALE_REACH);
    return (dx > FIX16(0)) && (dx < INHALE_REACH);
}

void ENEMY_updateAll(fix16 kirbyX, fix16 kirbyY, bool inhaling, bool facingLeft)
{
    u16 i;

    for (i = 0u; i < ENEMY_POOL_SIZE; i++)
    {
        Enemy* e = &s_pool[i];
        fix16 groundY;

        if (e->state == ENEMY_DEAD || e->state == ENEMY_SWALLOWED) continue;

        if (inhaling && inhale_zone(e, kirbyX, kirbyY, facingLeft))
        {
            e->state = ENEMY_PULLED;
        }
        else if (e->state == ENEMY_PULLED)
        {
            /* Released before being swallowed: back to walking. */
            e->state = ENEMY_WALK;
        }

        if (e->state == ENEMY_PULLED)
        {
            const fix16 dx = kirbyX - e->x;
            const fix16 dy = kirbyY - e->y;

            e->x += (dx > FIX16(0)) ? INHALE_PULL : -INHALE_PULL;
            if (dy > FIX16(2))       e->y += FIX16(0.8);
            else if (dy < FIX16(-2)) e->y -= FIX16(0.8);

            if (((dx < SWALLOW_RANGE) && (dx > -SWALLOW_RANGE)) &&
                ((dy < SWALLOW_RANGE) && (dy > -SWALLOW_RANGE)))
            {
                e->state = ENEMY_SWALLOWED;
            }
            continue;
        }

        /* --- walking: turn at ledges and at the plane edges -------------- */
        e->x += e->vx;

        if (!STAGE_groundAt(F16_toInt(e->x), &groundY) ||
            (e->x < FIX16(12)) || (e->x > FIX16(500)))
        {
            e->x -= e->vx;
            e->vx = -e->vx;
        }
        else
        {
            e->y = groundY + FIX16(6);
        }

        e->animTimer++;
        if (e->animTimer >= ENEMY_ANIM_SPEED)
        {
            e->animTimer = 0u;
            e->animFrame ^= 1u;
        }
    }
}

CopyAbility ENEMY_collectSwallowed(void)
{
    u16 i;
    for (i = 0u; i < ENEMY_POOL_SIZE; i++)
    {
        if (s_pool[i].state == ENEMY_SWALLOWED)
        {
            const CopyAbility a = s_pool[i].grants;
            s_pool[i].state = ENEMY_DEAD;
            return a;
        }
    }
    return ABILITY_NONE;
}

u16 ENEMY_aliveCount(void)
{
    u16 i, n = 0u;
    for (i = 0u; i < ENEMY_POOL_SIZE; i++)
        if (s_pool[i].state != ENEMY_DEAD) n++;
    return n;
}

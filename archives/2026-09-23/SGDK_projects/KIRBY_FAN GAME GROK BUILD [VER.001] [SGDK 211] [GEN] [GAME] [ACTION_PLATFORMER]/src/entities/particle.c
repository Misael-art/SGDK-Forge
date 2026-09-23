#include <genesis.h>

#include "entities/particle.h"

static Particle s_pool[PARTICLE_POOL_SIZE];

void PARTICLE_initPool(void)
{
    u16 i;

    for (i = 0u; i < PARTICLE_POOL_SIZE; i++)
    {
        s_pool[i].alive = FALSE;
        s_pool[i].life = 0u;
        s_pool[i].frame = 0u;
        s_pool[i].timer = 0u;
    }
}

static Particle* PARTICLE_alloc(void)
{
    u16 i;

    for (i = 0u; i < PARTICLE_POOL_SIZE; i++)
    {
        if (!s_pool[i].alive) return &s_pool[i];
    }
    /* Steal oldest (lowest life). */
    {
        u16 worst = 0u;
        u8 minLife = 255u;

        for (i = 0u; i < PARTICLE_POOL_SIZE; i++)
        {
            if (s_pool[i].life < minLife)
            {
                minLife = s_pool[i].life;
                worst = i;
            }
        }
        return &s_pool[worst];
    }
}

void PARTICLE_spawnDust(fix16 x, fix16 y, bool faceLeft)
{
    Particle* p = PARTICLE_alloc();

    p->alive = TRUE;
    p->x = x;
    /* Kirby.y is body centre; dust reads at the feet (+12). */
    p->y = y + FIX16(12);
    p->vx = faceLeft ? FIX16(-0.7) : FIX16(0.7);
    p->vy = FIX16(-0.5);
    p->life = PARTICLE_LIFE;
    p->frame = 0u;
    p->timer = 0u;
}

void PARTICLE_spawnLand(fix16 x, fix16 y)
{
    /* Two puffs outward at feet — cheap, readable, ≤2 sprites. */
    Particle* a = PARTICLE_alloc();
    Particle* b = PARTICLE_alloc();
    const fix16 feetY = y + FIX16(12);

    a->alive = TRUE;
    a->x = x - FIX16(6);
    a->y = feetY;
    a->vx = FIX16(-1.0);
    a->vy = FIX16(-0.6);
    a->life = PARTICLE_LIFE;
    a->frame = 0u;
    a->timer = 0u;

    b->alive = TRUE;
    b->x = x + FIX16(6);
    b->y = feetY;
    b->vx = FIX16(1.0);
    b->vy = FIX16(-0.6);
    b->life = PARTICLE_LIFE;
    b->frame = 0u;
    b->timer = 0u;
}

void PARTICLE_updateAll(void)
{
    u16 i;

    for (i = 0u; i < PARTICLE_POOL_SIZE; i++)
    {
        Particle* p = &s_pool[i];

        if (!p->alive) continue;

        p->x += p->vx;
        p->y += p->vy;
        p->vy += FIX16(0.06); /* light gravity so puffs settle */
        if (p->life > 0u) p->life--;
        p->timer++;
        /* Hold each frame a bit longer so expansion reads on-screen. */
        if (p->timer >= 6u)
        {
            p->timer = 0u;
            if (p->frame < (PARTICLE_FRAMES - 1u)) p->frame++;
        }
        if (p->life == 0u) p->alive = FALSE;
    }
}

const Particle* PARTICLE_get(u16 i)
{
    if (i >= PARTICLE_POOL_SIZE) return NULL;
    return &s_pool[i];
}

u16 PARTICLE_aliveCount(void)
{
    u16 i;
    u16 n = 0u;

    for (i = 0u; i < PARTICLE_POOL_SIZE; i++)
    {
        if (s_pool[i].alive) n++;
    }
    return n;
}

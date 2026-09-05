#include <genesis.h>

#include "entities/ability.h"

/* Per-ability tuning. These exist to be argued with and measured, not because
 * they are right -- same standing as the game feel table in ARCHITECTURE.md 7. */
#define FIRE_SPEED   FIX16(2.2)
#define FIRE_LIFE    18u
#define FIRE_COOLDOWN 6u

#define BEAM_SPEED   FIX16(0)     /* no travel: it simply exists in front */
#define BEAM_LIFE    10u
#define BEAM_COOLDOWN 14u

#define CUTTER_SPEED FIX16(3.4)
#define CUTTER_LIFE  70u
#define CUTTER_COOLDOWN 40u

#define STONE_LIFE   45u
#define STONE_COOLDOWN 60u

#define SWORD_SPEED  FIX16(1.2)
#define SWORD_LIFE   14u
#define SWORD_COOLDOWN 20u

static AbilityShot s_pool[ABILITY_SHOT_POOL];
static u16 s_cooldown;

void ABILITY_init(void)
{
    u16 i;
    for (i = 0u; i < ABILITY_SHOT_POOL; i++) s_pool[i].active = FALSE;
    s_cooldown = 0u;
}

static AbilityShot* alloc_shot(void)
{
    u16 i;
    for (i = 0u; i < ABILITY_SHOT_POOL; i++)
        if (!s_pool[i].active) return &s_pool[i];
    return NULL;   /* pool full: the shot is simply lost, never allocated */
}

bool ABILITY_fire(u8 ability, fix16 kirbyX, fix16 kirbyY, bool facingLeft)
{
    AbilityShot* s;
    const fix16 dir = facingLeft ? FIX16(-1) : FIX16(1);

    if ((ability == ABILITY_NONE) || (s_cooldown > 0u)) return FALSE;

    s = alloc_shot();
    if (s == NULL) return FALSE;

    s->active = TRUE;
    s->kind = ability;
    s->frame = 0u;
    s->returning = FALSE;
    s->y = kirbyY;

    switch (ability)
    {
        case ABILITY_FIRE:
            s->x = kirbyX + (dir * 14);
            s->vx = F16_mul(FIRE_SPEED, dir);
            s->life = FIRE_LIFE;
            s_cooldown = FIRE_COOLDOWN;
            break;
        case ABILITY_BEAM:
            s->x = kirbyX + (dir * 22);
            s->vx = BEAM_SPEED;
            s->life = BEAM_LIFE;
            s_cooldown = BEAM_COOLDOWN;
            break;
        case ABILITY_CUTTER:
            s->x = kirbyX + (dir * 14);
            s->vx = F16_mul(CUTTER_SPEED, dir);
            s->life = CUTTER_LIFE;
            s_cooldown = CUTTER_COOLDOWN;
            break;
        case ABILITY_STONE:
            /* STONE does not throw anything: the shot IS Kirby, parked on him,
             * so the same pool and the same collision code cover it. */
            s->x = kirbyX;
            s->vx = FIX16(0);
            s->life = STONE_LIFE;
            s_cooldown = STONE_COOLDOWN;
            break;
        case ABILITY_SWORD:
            s->x = kirbyX + (dir * 18);
            s->vx = F16_mul(SWORD_SPEED, dir);
            s->life = SWORD_LIFE;
            s_cooldown = SWORD_COOLDOWN;
            break;
        default:
            s->active = FALSE;
            return FALSE;
    }
    return TRUE;
}

void ABILITY_update(fix16 kirbyX, fix16 kirbyY)
{
    u16 i;

    if (s_cooldown > 0u) s_cooldown--;

    for (i = 0u; i < ABILITY_SHOT_POOL; i++)
    {
        AbilityShot* s = &s_pool[i];
        if (!s->active) continue;

        if (s->kind == ABILITY_STONE)
        {
            /* Rides Kirby: it is a state, not a projectile. */
            s->x = kirbyX;
            s->y = kirbyY;
        }
        else if (s->kind == ABILITY_CUTTER)
        {
            /* Travels out, then comes BACK. The return is what makes cutter a
             * commitment: the player has to still be there to catch it. */
            s->x += s->vx;
            if (!s->returning && (s->life < (CUTTER_LIFE / 2u)))
            {
                s->returning = TRUE;
                s->vx = -s->vx;
            }
        }
        else
        {
            s->x += s->vx;
            if (s->kind == ABILITY_SWORD) s->y = kirbyY;
        }

        s->frame = (u8) ((s->frame + 1u) % 3u);
        if (s->life > 0u) s->life--;
        if (s->life == 0u) s->active = FALSE;
    }
}

const AbilityShot* ABILITY_get(u16 index)
{
    return (index < ABILITY_SHOT_POOL) ? &s_pool[index] : NULL;
}

u16 ABILITY_activeCount(void)
{
    u16 i, n = 0u;
    for (i = 0u; i < ABILITY_SHOT_POOL; i++) if (s_pool[i].active) n++;
    return n;
}

u16 ABILITY_cooldown(void) { return s_cooldown; }

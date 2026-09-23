#include <genesis.h>

#include "entities/kirby.h"
#include "systems/stage_map.h"

/* --- Tunables. doc/ARCHITECTURE.md section 7. --------------------------- */
#define K_RUN_ACCEL      FIX16(0.30)
#define K_RUN_MAX        FIX16(2.00)
#define K_FRICTION       FIX16(0.22)
#define K_GRAVITY        FIX16(0.25)
#define K_GRAVITY_FLOAT  FIX16(0.05)   /* puff descent is almost weightless */
#define K_FALL_MAX       FIX16(4.00)
#define K_FALL_MAX_FLOAT FIX16(0.90)
#define K_JUMP_IMPULSE   FIX16(-3.60)
#define K_PUFF_IMPULSE   FIX16(-1.10)
#define K_AIR_ACCEL      FIX16(0.18)

#define K_COYOTE_FRAMES  4u
#define K_JUMPBUF_FRAMES 5u

/* Animation review strip: idle 2, run 4, jump 4, float 2, inhale 4. */
#define K_ANIM_IDLE      0u
#define K_ANIM_IDLE_COUNT 2u
#define K_ANIM_RUN_FIRST 2u
#define K_ANIM_RUN_COUNT 4u
#define K_ANIM_JUMP_FIRST 6u
#define K_ANIM_JUMP_COUNT 4u
#define K_ANIM_FLOAT_FIRST 10u
#define K_ANIM_FLOAT_COUNT 2u
#define K_ANIM_RUN_SPEED 5u
#define K_ANIM_JUMP_SPEED 6u
#define K_ANIM_FLOAT_SPEED 8u
#define K_ANIM_INHALE_FIRST 12u
#define K_ANIM_INHALE_COUNT 4u
#define K_ANIM_IDLE_SPEED 18u
#define K_ANIM_INHALE_SPEED 8u

void KIRBY_init(Kirby* k, fix16 x, fix16 y)
{
    k->x = x;
    k->y = y;
    k->vx = FIX16(0);
    k->vy = FIX16(0);
    k->state = KIRBY_IDLE;
    k->onGround = FALSE;
    k->facingLeft = FALSE;
    k->coyote = 0u;
    k->jumpBuffer = 0u;
    k->animFrame = 0u;
    k->animTimer = 0u;
    k->hitStop = 0u;
    k->inhaling = FALSE;
    k->ability = 0u;
    k->health = KIRBY_MAX_HEALTH;
    k->invuln = 0u;
    k->defeated = FALSE;
}

/*
 * Knockback arc from doc/ARCHITECTURE.md section 7: vy -2.5 px/f with gravity
 * 0.25 px/f2, all in fix16. The horizontal component pushes AWAY from the
 * source, which is why the caller has to say which side the hit came from.
 */
bool KIRBY_damage(Kirby* k, bool fromLeft)
{
    if (k->defeated || (k->invuln > 0u)) return FALSE;

    k->health = (k->health > 0u) ? (u8) (k->health - 1u) : 0u;
    k->invuln = KIRBY_INVULN_FRAMES;
    k->vy = FIX16(-2.5);
    k->vx = fromLeft ? FIX16(2.0) : FIX16(-2.0);
    k->onGround = FALSE;
    k->state = KIRBY_JUMP;
    KIRBY_applyHitStop(k, 4u);

    if (k->health == 0u) k->defeated = TRUE;
    return TRUE;
}

void KIRBY_applyHitStop(Kirby* k, u8 frames)
{
    if (frames > k->hitStop) k->hitStop = frames;
}

static void KIRBY_animate(Kirby* k)
{
    k->animTimer++;

    switch (k->state)
    {
        case KIRBY_IDLE:
            if (k->animTimer >= K_ANIM_IDLE_SPEED)
            {
                k->animTimer = 0u;
                k->animFrame = (u8) ((k->animFrame + 1u) & 1u);
            }
            break;

        case KIRBY_RUN:
            if (k->animTimer >= K_ANIM_RUN_SPEED)
            {
                k->animTimer = 0u;
                k->animFrame = (u8) ((k->animFrame + 1u) % K_ANIM_RUN_COUNT);
            }
            break;

        case KIRBY_JUMP:
            if (k->animTimer >= K_ANIM_JUMP_SPEED)
            {
                k->animTimer = 0u;
                if (k->animFrame + 1u < K_ANIM_JUMP_COUNT) k->animFrame++;
            }
            break;

        case KIRBY_FLOAT:
            if (k->animTimer >= K_ANIM_FLOAT_SPEED)
            {
                k->animTimer = 0u;
                k->animFrame = (u8) ((k->animFrame + 1u) % K_ANIM_FLOAT_COUNT);
            }
            break;

        case KIRBY_INHALE:
            if (k->animTimer >= K_ANIM_INHALE_SPEED)
            {
                k->animTimer = 0u;
                if (k->animFrame + 1u < K_ANIM_INHALE_COUNT) k->animFrame++;
            }
            break;

        default:
            k->animFrame = 0u;
            break;
    }
}

void KIRBY_update(Kirby* k, u16 held, u16 pressed)
{
    if (k->invuln > 0u) k->invuln--;

    fix16 groundY;
    bool wantLeft;
    bool wantRight;

    /*
     * Hit-stop freezes the entity but NOT the frame. doc/ARCHITECTURE.md
     * section 7 wants 4 frames on a normal hit; during those frames physics
     * and animation stop so the impact reads.
     */
    if (k->hitStop > 0u)
    {
        k->hitStop--;
        return;
    }

    k->inhaling = (held & BUTTON_B) != 0;

    /* Inhaling roots Kirby: the vortex is a commitment, not a free action. */
    wantLeft = (!k->inhaling) && ((held & BUTTON_LEFT) != 0);
    wantRight = (!k->inhaling) && ((held & BUTTON_RIGHT) != 0);

    /* --- horizontal ---------------------------------------------------- */
    if (wantLeft && !wantRight)
    {
        k->vx -= k->onGround ? K_RUN_ACCEL : K_AIR_ACCEL;
        if (k->vx < -K_RUN_MAX) k->vx = -K_RUN_MAX;
        k->facingLeft = TRUE;
    }
    else if (wantRight && !wantLeft)
    {
        k->vx += k->onGround ? K_RUN_ACCEL : K_AIR_ACCEL;
        if (k->vx > K_RUN_MAX) k->vx = K_RUN_MAX;
        k->facingLeft = FALSE;
    }
    else if (k->onGround)
    {
        if (k->vx > K_FRICTION)       k->vx -= K_FRICTION;
        else if (k->vx < -K_FRICTION) k->vx += K_FRICTION;
        else                          k->vx = FIX16(0);
    }

    /* --- jump buffer and coyote time ----------------------------------- */
    if ((pressed & BUTTON_A) != 0)
    {
        k->jumpBuffer = K_JUMPBUF_FRAMES;
    }
    else if (k->jumpBuffer > 0u)
    {
        k->jumpBuffer--;
    }

    if (k->onGround) k->coyote = K_COYOTE_FRAMES;
    else if (k->coyote > 0u) k->coyote--;

    if ((k->jumpBuffer > 0u) && (k->coyote > 0u))
    {
        k->vy = K_JUMP_IMPULSE;
        k->onGround = FALSE;
        k->jumpBuffer = 0u;
        k->coyote = 0u;
        k->state = KIRBY_JUMP;
    }
    else if (!k->onGround &&
             ((held & BUTTON_A) != 0) &&
             (k->vy > FIX16(-0.6)))
    {
        /*
         * The float. Holding jump while falling puffs Kirby up. This is the
         * character's signature verb, so it is deliberately generous: it can
         * be sustained indefinitely, exactly like the source game.
         */
        k->vy = K_PUFF_IMPULSE;
        k->state = KIRBY_FLOAT;
    }

    /* --- gravity -------------------------------------------------------- */
    if (k->state == KIRBY_FLOAT)
    {
        k->vy += K_GRAVITY_FLOAT;
        if (k->vy > K_FALL_MAX_FLOAT) k->vy = K_FALL_MAX_FLOAT;
    }
    else
    {
        k->vy += K_GRAVITY;
        if (k->vy > K_FALL_MAX) k->vy = K_FALL_MAX;
    }

    /* --- integrate and resolve ground ---------------------------------- */
    k->x += k->vx;
    k->y += k->vy;

    if (k->x < FIX16(8))   { k->x = FIX16(8);   k->vx = FIX16(0); }
    if (k->x > FIX16(504)) { k->x = FIX16(504); k->vx = FIX16(0); }

    if (STAGE_groundAt(F16_toInt(k->x), &groundY) && (k->vy >= FIX16(0)) &&
        (k->y >= groundY))
    {
        k->y = groundY;
        k->vy = FIX16(0);
        if (!k->onGround) k->state = KIRBY_IDLE;
        k->onGround = TRUE;
    }
    else
    {
        k->onGround = FALSE;
    }

    /* Fell down a gap: respawn rather than leave the player stuck. */
    if (k->y > FIX16(260))
    {
        KIRBY_init(k, FIX16(48), FIX16(120));
        return;
    }

    /* --- state for animation ------------------------------------------- */
    if (k->inhaling)
    {
        k->state = KIRBY_INHALE;
    }
    else if (k->onGround)
    {
        k->state = (k->vx > FIX16(0.2) || k->vx < FIX16(-0.2))
                 ? KIRBY_RUN : KIRBY_IDLE;
    }
    else if (k->state != KIRBY_FLOAT)
    {
        k->state = KIRBY_JUMP;
    }

    KIRBY_animate(k);
}

s16 KIRBY_screenX(const Kirby* k, s16 cameraX)
{
    return (s16) (F16_toInt(k->x) - cameraX);
}

u16 KIRBY_animIndex(const Kirby* k)
{
    switch (k->state)
    {
        case KIRBY_RUN:   return K_ANIM_RUN_FIRST + (k->animFrame % K_ANIM_RUN_COUNT);
        case KIRBY_JUMP:  return K_ANIM_JUMP_FIRST + (k->animFrame % K_ANIM_JUMP_COUNT);
        case KIRBY_FLOAT: return K_ANIM_FLOAT_FIRST + (k->animFrame % K_ANIM_FLOAT_COUNT);
        case KIRBY_INHALE: return K_ANIM_INHALE_FIRST + (k->animFrame % K_ANIM_INHALE_COUNT);
        default:          return K_ANIM_IDLE + (k->animFrame % K_ANIM_IDLE_COUNT);
    }
}

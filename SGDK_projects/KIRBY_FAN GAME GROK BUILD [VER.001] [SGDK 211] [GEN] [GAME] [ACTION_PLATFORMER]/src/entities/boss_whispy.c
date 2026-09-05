#include <genesis.h>
#include <maths.h>

#include "entities/boss_whispy.h"

#define SEG_LENGTH 12              /* pixels between segment centres */
#define ANGLE_LERP_SHIFT 3         /* angle += (target - angle) >> 3 */
#define APPLE_GRAVITY FIX16(0.22)

/* Resting pose: branches fan out two per side. */
static const fix16 REST_ANGLE[BOSS_BRANCH_COUNT] = {
    FIX16(200), FIX16(160), FIX16(340), FIX16(20)
};
static const s16 ORIGIN_DX[BOSS_BRANCH_COUNT] = { -28, -28, 28, 28 };
static const s16 ORIGIN_DY[BOSS_BRANCH_COUNT] = { -18, 6, -18, 6 };

static fix16 approach(fix16 value, fix16 target)
{
    const fix16 delta = target - value;
    if ((delta < FIX16(0.5)) && (delta > FIX16(-0.5))) return target;
    return value + (delta >> ANGLE_LERP_SHIFT);
}

/*
 * Forward kinematics: each segment inherits the accumulated angle of the one
 * before it, so a single `curl` value bends the whole branch smoothly. This is
 * why smoothness costs nothing extra per segment -- it is one add per joint.
 */
static void solve_branch(BossBranch* br)
{
    fix16 angle = br->baseAngle;
    s16 x = br->originX;
    s16 y = br->originY;
    u16 i;

    for (i = 0u; i < BOSS_SEGMENTS_PER_BRANCH; i++)
    {
        br->seg[i].x = x;
        br->seg[i].y = y;

        /*
         * F16_cos/F16_sin STAY. On 2026-08-06 I replaced them with a 64-entry
         * table expecting the same win the water effect got, and it went the
         * other way: cpu p99 92% -> 107%, over-budget frames 3 -> 225.
         *
         * The reason is that my index helper did `deg % 360` and `* 64 / 360`,
         * i.e. TWO 32-bit divisions per segment, and the 68000 has no fast
         * divide. SGDK's F16_cos is already a table with cheap indexing.
         *
         * A table is not automatically faster than a function. It was faster in
         * raster.c because the index there was a mask (`& 63`); here it needed
         * division, and division ate the entire saving and more.
         */
        x += (s16) F16_toInt(F16_mul(F16_cos(angle), FIX16(SEG_LENGTH)));
        y += (s16) F16_toInt(F16_mul(F16_sin(angle), FIX16(SEG_LENGTH)));
        angle += br->curl;
    }
}

void BOSS_init(Boss* b, s16 x, s16 y)
{
    u16 i, j;

    b->phase = BOSS_IDLE;
    b->phaseTimer = 0u;
    b->hp = BOSS_MAX_HP;
    b->hitStop = 0u;
    b->faceFrame = 0u;
    b->solveToggle = 0u;
    b->x = x;
    b->y = y;

    for (i = 0u; i < BOSS_BRANCH_COUNT; i++)
    {
        BossBranch* br = &b->branch[i];
        br->baseAngle = REST_ANGLE[i];
        br->targetAngle = REST_ANGLE[i];
        br->curl = FIX16(6);
        br->targetCurl = FIX16(6);
        br->originX = x + ORIGIN_DX[i];
        br->originY = y + ORIGIN_DY[i];
        solve_branch(br);
    }

    for (j = 0u; j < BOSS_APPLE_POOL; j++) b->apple[j].active = FALSE;
}

static void set_branch_targets(Boss* b, fix16 angleBias, fix16 curl)
{
    u16 i;
    for (i = 0u; i < BOSS_BRANCH_COUNT; i++)
    {
        b->branch[i].targetAngle = REST_ANGLE[i] + angleBias;
        b->branch[i].targetCurl = curl;
    }
}

static void drop_apple(Boss* b, s16 x)
{
    u16 j;
    for (j = 0u; j < BOSS_APPLE_POOL; j++)
    {
        if (!b->apple[j].active)
        {
            b->apple[j].active = TRUE;
            b->apple[j].x = FIX16(x);
            b->apple[j].y = FIX16(40);
            b->apple[j].vy = FIX16(0);
            return;
        }
    }
}

void BOSS_damage(Boss* b, u16 amount)
{
    if ((b->phase == BOSS_DEFEATED) || (b->hitStop > 0u)) return;

    b->hp = (b->hp > amount) ? (u16) (b->hp - amount) : 0u;
    /* Hit-stop and the flash come from doc/ARCHITECTURE.md section 7. */
    b->hitStop = 8u;
    b->phase = (b->hp == 0u) ? BOSS_DEFEATED : BOSS_HURT;
    b->phaseTimer = 0u;
}

void BOSS_update(Boss* b, fix16 kirbyX)
{
    u16 i, j;

    if (b->hitStop > 0u)
    {
        b->hitStop--;
        return;                    /* the whole boss freezes: that is the point */
    }

    b->phaseTimer++;

    switch (b->phase)
    {
        case BOSS_IDLE:
            set_branch_targets(b, FIX16(0), FIX16(6));
            b->faceFrame = 0u;
            if (b->phaseTimer > 90u)
            {
                b->phase = BOSS_WINDUP;
                b->phaseTimer = 0u;
            }
            break;

        case BOSS_WINDUP:
            set_branch_targets(b, FIX16(-25), FIX16(14));   /* curl back */
            b->faceFrame = 1u;
            if (b->phaseTimer > 40u)
            {
                b->phase = BOSS_WHIP;
                b->phaseTimer = 0u;
            }
            break;

        case BOSS_WHIP:
            set_branch_targets(b, FIX16(35), FIX16(-10));   /* lash forward */
            if (b->phaseTimer > 35u)
            {
                b->phase = BOSS_DROP_APPLES;
                b->phaseTimer = 0u;
            }
            break;

        case BOSS_DROP_APPLES:
            set_branch_targets(b, FIX16(0), FIX16(6));
            if ((b->phaseTimer % 18u) == 1u)
            {
                /* Aim loosely at Kirby so the fight reacts to the player. */
                drop_apple(b, (s16) (F16_toInt(kirbyX) - 20 +
                                     (s16) (b->phaseTimer & 31u)));
            }
            if (b->phaseTimer > 90u)
            {
                b->phase = BOSS_IDLE;
                b->phaseTimer = 0u;
            }
            break;

        case BOSS_HURT:
            b->faceFrame = 1u;
            if (b->phaseTimer > 30u)
            {
                b->phase = BOSS_IDLE;
                b->phaseTimer = 0u;
            }
            break;

        case BOSS_DEFEATED:
            set_branch_targets(b, FIX16(0), FIX16(22));     /* branches wilt */
            b->faceFrame = 1u;
            break;

        default:
            break;
    }

    /*
     * DEGRADATION LEVER 1 from doc/ARCHITECTURE.md section 5.1, applied against
     * a real measurement on 2026-08-06: solving all four chains every frame put
     * cpu p99 at 87% and pushed 2 frames over the budget, failing
     * zero_over_budget_frames. Solving every OTHER frame halves the trig cost;
     * the segments simply hold their pose for one frame, which at 60 Hz is not
     * visible. The remaining levers, in order, are: 5 segments per branch, then
     * 3 branches. The face animation is never cut.
     */
    b->solveToggle ^= 1u;
    if (b->solveToggle == 0u)
    {
        for (i = 0u; i < BOSS_BRANCH_COUNT; i++)
        {
            BossBranch* br = &b->branch[i];
            /* Two frames of interpolation are applied at once so the motion
             * keeps the same speed as the every-frame version. */
            br->baseAngle = approach(br->baseAngle, br->targetAngle);
            br->baseAngle = approach(br->baseAngle, br->targetAngle);
            br->curl = approach(br->curl, br->targetCurl);
            br->curl = approach(br->curl, br->targetCurl);
            solve_branch(br);
        }
    }

    for (j = 0u; j < BOSS_APPLE_POOL; j++)
    {
        BossApple* a = &b->apple[j];
        if (!a->active) continue;
        a->vy += APPLE_GRAVITY;
        a->y += a->vy;
        if (a->y > FIX16(200)) a->active = FALSE;
    }
}

u16 BOSS_activeAppleCount(const Boss* b)
{
    u16 j, n = 0u;
    for (j = 0u; j < BOSS_APPLE_POOL; j++) if (b->apple[j].active) n++;
    return n;
}

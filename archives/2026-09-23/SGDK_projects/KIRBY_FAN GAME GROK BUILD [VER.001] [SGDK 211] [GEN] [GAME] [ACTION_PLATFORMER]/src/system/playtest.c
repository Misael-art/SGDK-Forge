#include <genesis.h>

#include "entities/kirby.h"
#include "system/playtest.h"

/*
 * The recorded script. Each entry holds the buttons to keep held for a number
 * of frames. Durations are generous on purpose: this is a coverage script, not
 * a speedrun, and a tight script would break every time a tunable changes.
 *
 * The enemies spawn walking toward Kirby, so "stand still and inhale" is enough
 * to make one arrive and be swallowed. That is deliberate -- the script must not
 * depend on Kirby chasing an enemy at a precise speed.
 */
typedef struct PlaytestStep {
    u16 frames;
    u16 buttons;
} PlaytestStep;

static const PlaytestStep SCRIPT[] = {
    {  30u, 0u },                            /* settle on the ground: IDLE, GROUNDED */
    {  45u, BUTTON_RIGHT },                  /* RUN, FACE_R */
    {  30u, 0u },
    {  45u, BUTTON_LEFT },                   /* RUN, FACE_L */
    {  20u, 0u },
    {  10u, BUTTON_A },                      /* JUMP, AIRBORNE */
    {  40u, 0u },                            /* fall back down */
    {  10u, BUTTON_A },
    {  12u, 0u },
    {  10u, BUTTON_A },                      /* second press in the air: FLOAT */
    {  50u, BUTTON_A },
    {  40u, 0u },
    {  60u, BUTTON_RIGHT },                  /* walk toward the enemies */
    { 240u, BUTTON_B },                      /* INHALE, and hold long enough to
                                              * pull an enemy in and swallow it */
    {  40u, 0u },
    /*
     * With an ability in hand B stops inhaling and starts ATTACKING, so the
     * same button now proves a different state. Fired in bursts because the
     * ability has a cooldown: holding it down would only spawn one shot and
     * then look identical to doing nothing.
     */
    {  20u, BUTTON_B },
    {  20u, 0u },
    {  20u, BUTTON_B },
    {  20u, 0u },
    {  20u, BUTTON_B },
    {  40u, 0u },
    {  60u, BUTTON_LEFT },
    {  20u, 0u },
    /* Late hop so land-dust is still alive when the harness grabs the frame. */
    {  10u, BUTTON_A },
    {  28u, 0u },
    {  12u, 0u },
};

#define SCRIPT_LENGTH (sizeof(SCRIPT) / sizeof(SCRIPT[0]))

/*
 * Boss script. Whispy aims his apples loosely at Kirby, so the winning line is
 * to stand under the tree and hold inhale: every apple that arrives gets
 * swallowed and costs the boss a hit point. Holding B for a long stretch is
 * deliberate -- the script has to survive the boss's whole phase cycle
 * (idle 90 + windup 40 + whip 35 + apples 90 = 255 frames) several times over,
 * because 6 HP means at least 6 apples.
 */
static const PlaytestStep BOSS_SCRIPT[] = {
    {  40u, 0u },
    {  70u, BUTTON_RIGHT },      /* walk under the canopy */
    /*
     * Stand there WITHOUT inhaling first. Holding B swallows every apple before
     * it lands, so a script that inhales from the start never demonstrates the
     * damage-to-Kirby path -- measured: kirby_hurt stayed NO. Taking a hit on
     * purpose is the only way to prove that path actually works.
     */
    { 300u, 0u },
    {  40u, BUTTON_LEFT },
    { 900u, BUTTON_B },          /* now fight back: inhale and counter */
    {  40u, 0u },
    { 260u, BUTTON_B },
};
/* Total ~1610 frames = ~27 s at 60 Hz. It MUST fit inside the capture warmup or
 * playtest_completed fails: measured, a 2400-frame script under a 32 s capture
 * reached only step 6 of 7. */

#define BOSS_SCRIPT_LENGTH (sizeof(BOSS_SCRIPT) / sizeof(BOSS_SCRIPT[0]))

static const PlaytestStep* s_script;
static u16 s_scriptLen;

static bool s_active;
static u16 s_step;
static u16 s_frameInStep;
static u16 s_prevButtons;
static u16 s_visited;

static void playtest_reset(const PlaytestStep* script, u16 length)
{
    s_script = script;
    s_scriptLen = length;
    s_active = TRUE;
    s_step = 0u;
    s_frameInStep = 0u;
    s_prevButtons = 0u;
    s_visited = 0u;
}

void PLAYTEST_beginBoss(void)
{
    playtest_reset(BOSS_SCRIPT, BOSS_SCRIPT_LENGTH);
}

/* Let a scene record a state the generic observer cannot see. */
void PLAYTEST_mark(u16 stateBits)
{
    if (s_active) s_visited |= stateBits;
}

void PLAYTEST_begin(void)
{
    playtest_reset(SCRIPT, SCRIPT_LENGTH);
    s_active = TRUE;
    s_step = 0u;
    s_frameInStep = 0u;
    s_prevButtons = 0u;
    s_visited = 0u;
}

bool PLAYTEST_active(void) { return s_active; }

u16 PLAYTEST_poll(u16* pressed)
{
    u16 buttons;

    if (!s_active || (s_script == NULL) || (s_step >= s_scriptLen))
    {
        if (pressed != NULL) *pressed = 0u;
        s_prevButtons = 0u;
        return 0u;
    }

    buttons = s_script[s_step].buttons;

    if (pressed != NULL)
    {
        /* Edge detection, same contract the pad path uses. */
        *pressed = (u16) (buttons & ~s_prevButtons);
    }
    s_prevButtons = buttons;

    s_frameInStep++;
    if (s_frameInStep >= s_script[s_step].frames)
    {
        s_frameInStep = 0u;
        s_step++;
    }

    return buttons;
}

void PLAYTEST_observe(u16 kirbyState, bool onGround, bool facingLeft,
                      bool swallowed, bool abilityGranted)
{
    if (!s_active) return;

    switch (kirbyState)
    {
        case KIRBY_IDLE:   s_visited |= PLAYTEST_STATE_IDLE;   break;
        case KIRBY_RUN:    s_visited |= PLAYTEST_STATE_RUN;    break;
        case KIRBY_JUMP:   s_visited |= PLAYTEST_STATE_JUMP;   break;
        case KIRBY_FLOAT:  s_visited |= PLAYTEST_STATE_FLOAT;  break;
        case KIRBY_INHALE: s_visited |= PLAYTEST_STATE_INHALE; break;
        default: break;
    }

    s_visited |= onGround ? PLAYTEST_STATE_GROUNDED : PLAYTEST_STATE_AIRBORNE;
    s_visited |= facingLeft ? PLAYTEST_STATE_FACE_L : PLAYTEST_STATE_FACE_R;

    if (swallowed)      s_visited |= PLAYTEST_STATE_SWALLOW;
    if (abilityGranted) s_visited |= PLAYTEST_STATE_ABILITY;
}

u16 PLAYTEST_visited(void) { return s_visited; }
u16 PLAYTEST_step(void) { return s_step; }
bool PLAYTEST_finished(void) { return s_active && (s_step >= s_scriptLen); }

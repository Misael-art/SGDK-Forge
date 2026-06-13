#include <genesis.h>

#include "gameplay/chase_rules.h"

static void chaseRulesResolveResult(ChaseRulesState* state)
{
    if (state->integrity == 0 || state->pressure >= CHASE_MAX_PRESSURE) {
        state->flow = CHASE_FLOW_FAILURE;
    } else if (state->roundLength > 0 && state->roundFrame >= state->roundLength) {
        state->flow = CHASE_FLOW_VICTORY;
    }
}

void CHASE_RULES_reset(ChaseRulesState* state, u16 targetFps, ChaseMode mode)
{
    state->mode = mode;
    state->flow = CHASE_FLOW_INTRO;
    state->pausedFrom = CHASE_FLOW_INTRO;
    state->roundFrame = 0;
    state->targetFps = targetFps;
    state->roundLength = (mode == CHASE_MODE_RUN) ? (u32)targetFps * 75u : 0;
    state->pressurePhaseStart = (u32)targetFps * 20u;
    state->climaxPhaseStart = (u32)targetFps * 50u;
    state->difficulty = 0;
    state->pressure = 22;
    state->energy = 0;
    state->invulnerabilityFrames = 0;
    state->hitstopFrames = 0;
    state->integrity = CHASE_MAX_INTEGRITY;
    state->pulsesUsed = 0;
    state->score = 0;
    state->phaseChanged = TRUE;
}

void CHASE_RULES_update(ChaseRulesState* state)
{
    u32 basePeriod;
    u32 pressurePeriod;
    u32 minPeriod;
    u32 difficultyInterval;

    state->phaseChanged = FALSE;
    if (!CHASE_RULES_isPlaying(state)) {
        return;
    }

    if (state->invulnerabilityFrames > 0) {
        state->invulnerabilityFrames--;
    }

    state->roundFrame++;

    if (state->mode == CHASE_MODE_ENDLESS) {
        state->score++;
        difficultyInterval = (u32)state->targetFps * 10u;
        if (difficultyInterval > 0 && state->roundFrame != 0 && (state->roundFrame % difficultyInterval) == 0) {
            if (state->difficulty < 0xFFFFu) {
                state->difficulty++;
            }
        }
    }

    if (state->roundFrame >= state->climaxPhaseStart && state->flow != CHASE_FLOW_CLIMAX) {
        state->flow = CHASE_FLOW_CLIMAX;
        state->phaseChanged = TRUE;
    } else if (state->roundFrame >= state->pressurePhaseStart && state->flow == CHASE_FLOW_INTRO) {
        state->flow = CHASE_FLOW_PRESSURE;
        state->phaseChanged = TRUE;
    }

    if (state->flow == CHASE_FLOW_INTRO) {
        basePeriod = (u32)state->targetFps * 5u;
    } else if (state->flow == CHASE_FLOW_PRESSURE) {
        basePeriod = (u32)state->targetFps * 2u;
    } else {
        basePeriod = state->targetFps;
    }

    pressurePeriod = basePeriod;
    if (state->mode == CHASE_MODE_ENDLESS) {
        minPeriod = state->targetFps / 2u;
        if (minPeriod == 0) {
            minPeriod = 1;
        }
        pressurePeriod = basePeriod / ((u32)state->difficulty + 1u);
        if (pressurePeriod < minPeriod) {
            pressurePeriod = minPeriod;
        }
    }

    if (pressurePeriod > 0 && (state->roundFrame % pressurePeriod) == 0) {
        if (state->pressure < CHASE_MAX_PRESSURE) {
            state->pressure++;
        }
    }

    chaseRulesResolveResult(state);
}

bool CHASE_RULES_damage(ChaseRulesState* state)
{
    u16 newPressure;

    if (!CHASE_RULES_isPlaying(state) || state->invulnerabilityFrames > 0) {
        return FALSE;
    }

    if (state->integrity > 0) {
        state->integrity--;
    }

    newPressure = state->pressure + 18;
    state->pressure = (newPressure > CHASE_MAX_PRESSURE) ? CHASE_MAX_PRESSURE : newPressure;
    state->invulnerabilityFrames = (state->targetFps * 5u) / 4u;
    state->hitstopFrames = 4;
    chaseRulesResolveResult(state);
    return TRUE;
}

void CHASE_RULES_collectEnergy(ChaseRulesState* state)
{
    u16 newEnergy = state->energy + 25;
    state->energy = (newEnergy > CHASE_MAX_ENERGY) ? CHASE_MAX_ENERGY : newEnergy;
    if (state->mode == CHASE_MODE_ENDLESS) {
        state->score += 25;
    }
}

bool CHASE_RULES_usePulse(ChaseRulesState* state)
{
    if (!CHASE_RULES_isPlaying(state) || state->energy < CHASE_MAX_ENERGY) {
        return FALSE;
    }

    state->energy = 0;
    state->pressure = (state->pressure > 28) ? state->pressure - 28 : 0;
    state->pulsesUsed++;
    state->hitstopFrames = 5;
    if (state->mode == CHASE_MODE_ENDLESS) {
        state->score += 50;
    }
    return TRUE;
}

bool CHASE_RULES_togglePause(ChaseRulesState* state)
{
    if (state->flow == CHASE_FLOW_PAUSED) {
        state->flow = state->pausedFrom;
        return FALSE;
    }

    if (CHASE_RULES_isPlaying(state)) {
        state->pausedFrom = state->flow;
        state->flow = CHASE_FLOW_PAUSED;
        return TRUE;
    }

    return FALSE;
}

bool CHASE_RULES_tickHitstop(ChaseRulesState* state)
{
    if (state->hitstopFrames == 0) {
        return FALSE;
    }

    state->hitstopFrames--;
    return TRUE;
}

bool CHASE_RULES_isPlaying(const ChaseRulesState* state)
{
    return state->flow == CHASE_FLOW_INTRO
        || state->flow == CHASE_FLOW_PRESSURE
        || state->flow == CHASE_FLOW_CLIMAX;
}

bool CHASE_RULES_isResult(const ChaseRulesState* state)
{
    return state->flow == CHASE_FLOW_VICTORY || state->flow == CHASE_FLOW_FAILURE;
}

u8 CHASE_RULES_phaseNumber(const ChaseRulesState* state)
{
    if (state->flow == CHASE_FLOW_CLIMAX) {
        return 3;
    }
    if (state->flow == CHASE_FLOW_PRESSURE) {
        return 2;
    }
    return 1;
}

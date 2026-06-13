#ifndef GAMEPLAY_CHASE_RULES_H
#define GAMEPLAY_CHASE_RULES_H

#include <genesis.h>

#include "gameplay/chase_mode.h"

#define CHASE_MAX_INTEGRITY 3
#define CHASE_MAX_PRESSURE 100
#define CHASE_MAX_ENERGY 100

typedef enum ChaseFlowState {
    CHASE_FLOW_INTRO = 0,
    CHASE_FLOW_PRESSURE,
    CHASE_FLOW_CLIMAX,
    CHASE_FLOW_PAUSED,
    CHASE_FLOW_VICTORY,
    CHASE_FLOW_FAILURE
} ChaseFlowState;

typedef struct ChaseRulesState {
    ChaseMode mode;
    u32 score;
    u16 difficulty;
    ChaseFlowState flow;
    ChaseFlowState pausedFrom;
    u32 roundFrame;
    u32 roundLength;
    u32 pressurePhaseStart;
    u32 climaxPhaseStart;
    u16 targetFps;
    u16 pressure;
    u16 energy;
    u16 invulnerabilityFrames;
    u16 hitstopFrames;
    u8 integrity;
    u8 pulsesUsed;
    bool phaseChanged;
} ChaseRulesState;

void CHASE_RULES_reset(ChaseRulesState* state, u16 targetFps, ChaseMode mode);
void CHASE_RULES_update(ChaseRulesState* state);
bool CHASE_RULES_damage(ChaseRulesState* state);
void CHASE_RULES_collectEnergy(ChaseRulesState* state);
bool CHASE_RULES_usePulse(ChaseRulesState* state);
bool CHASE_RULES_togglePause(ChaseRulesState* state);
bool CHASE_RULES_tickHitstop(ChaseRulesState* state);
bool CHASE_RULES_isPlaying(const ChaseRulesState* state);
bool CHASE_RULES_isResult(const ChaseRulesState* state);
u8 CHASE_RULES_phaseNumber(const ChaseRulesState* state);

#endif

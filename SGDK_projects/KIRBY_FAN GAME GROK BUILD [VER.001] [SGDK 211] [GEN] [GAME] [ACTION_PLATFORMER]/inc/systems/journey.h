#ifndef SYSTEMS_JOURNEY_H
#define SYSTEMS_JOURNEY_H

#include <genesis.h>

#include "game_vars.h"
#include "systems/stage_map.h"

/*
 * MISSAO 2026-08-24: progressao da jornada de 5 fases.
 *
 * Fluxo canonico:
 *   TITLE -> INTRO -> MENU
 *   MENU(HISTORIA)  -> STAGE(0) -> ... -> STAGE(1) -> BOSS(Whispy)
 *                   -> STAGE(2) -> STAGE(3) -> STAGE(4) -> BOSS(Fury final)
 *                   -> ENDING -> TITLE
 *   GAMEOVER derrota      -> repete o contexto atual (fase ou boss)
 *   GAMEOVER vitoria boss -> avanca para a fase seguinte
 *
 * A variedade visual entre fases vem de PALETA (recolor das mesmas camadas),
 * agua (R3/R4), ceu noturno (raster) e layout de inimigos/vaos. Zero arte nova
 * nesta etapa: a diretriz de bloqueio estetico segue valendo e a arte final e
 * FASE 2 do brief.
 */

#define JOURNEY_STAGE_COUNT 5

typedef struct {
    s16 x0;
    s16 x1;
} JourneyGap;

typedef struct {
    const char* name;
    /* NULL = usa o master canonical (fase 0). Senao, override por indice. */
    const u8 (*pal0)[3];   /* {step r,g,b} em lattice RGB333; indice 0 preservado */
    const u8 (*pal1)[3];
    bool water;            /* R3/R4: waterline + CRAM words */
    bool night;            /* gradiente noturno do raster */
    u8 enemyCount;
    const s16* enemyX;
    const u8* enemyAbility;/* CopyAbility id por slot */
    u8 gapCount;
    const JourneyGap* gaps;
} StageDef;

typedef struct JourneyState {
    u8 stageIndex;        /* 0..JOURNEY_STAGE_COUNT-1 */
    u8 unlockedMask;      /* bit N = fase N selecionavel no menu */
    bool bossPending;     /* o proximo goal e um boss */
    bool finalBoss;       /* boss em cena e o final (Fury) */
    bool journeyDone;
    bool introSeen;
    u16 rngSeed;
} JourneyState;

extern JourneyState gJourney;

void JOURNEY_resetNewGame(void);

const StageDef* JOURNEY_stageDef(u8 idx);

/* Transicoes. Cada uma devolve a cena que o fluxo deve abrir. */
AppScene JOURNEY_sceneAfterStageGoal(void);
AppScene JOURNEY_sceneAfterBossVictory(void);
AppScene JOURNEY_retryScene(void);

/* RNG deterministico sem float, semeado pelo input humano. */
u16 JOURNEY_rand(void);
void JOURNEY_seedFromInput(void);

/*
 * INSTRUMENTACAO DE LABORATORIO (mesma familia dos probes SRAM existentes).
 *
 * Offset 0x140 da SRAM (faixa livre entre o bootstrap SBIS em 0x120 e os dados
 * do probe em 0x200): magic "JBOY" + u8 stageIndex + u8 flags (bit0 =
 * bossPending, bit1 = finalBoss). Consumido uma unica vez no boot e zerado,
 * para que warm reset nao replique. NAO faz parte do contrato de bootstrap
 * compartilhado; so o driver de captura local escreve aqui.
 */
void JOURNEY_applySramOverride(void);

#endif

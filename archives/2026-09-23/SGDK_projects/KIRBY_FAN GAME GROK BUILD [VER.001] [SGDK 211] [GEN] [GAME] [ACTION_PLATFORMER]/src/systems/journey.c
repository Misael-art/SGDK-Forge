#include <genesis.h>

#include "systems/journey.h"

/*
 * MISSAO 2026-08-24: tabela das 5 fases da jornada.
 *
 * Regra de scanline respeitada: ENEMY_POOL_SIZE e 6 e permanece o teto de
 * inimigos por fase. A medicao de 2026-08-06 (19/20 com 6 inimigos + Kirby +
 * tufts) e o piso; nenhuma fase aqui pode aumentar a pressao da faixa do chao,
 * apenas variar composicao. Vaos e spawns foram escolhidos para nao se
 * sobreporem: nenhum inimigo nasce dentro de um vao.
 *
 * Paletas sao overrides RGB333 sobre os masters canonicals (indice 0 sempre
 * preservado do master - ver scene_stage.c). Zero arte nova nesta etapa;
 * diretriz de bloqueio estetico segue valendo para a FASE 2.
 */

/* ------------------------------------------------------------------ */
/* Layouts de inimigos: x em plane space, ability por slot.           */
/* ------------------------------------------------------------------ */

static const s16 EX_S0[] = { 200, 260, 330, 400, 460, 500 };
static const u8  EA_S0[] = { 1, 2, 3, 4, 5, 0 };   /* FIRE,BEAM,CUTTER,STONE,SWORD,NONE */

static const s16 EX_S1[] = { 210, 270, 340, 410, 470, 510 };
static const u8  EA_S1[] = { 2, 3, 4, 5, 1, 0 };

static const s16 EX_S2[] = { 185, 245, 285, 365, 430, 500 };
static const u8  EA_S2[] = { 3, 4, 5, 1, 2, 0 };

static const s16 EX_S3[] = { 225, 285, 350, 425, 485, 505 };
static const u8  EA_S3[] = { 4, 5, 1, 2, 3, 0 };

static const s16 EX_S4[] = { 195, 240, 315, 385, 462, 505 };
static const u8  EA_S4[] = { 5, 1, 2, 3, 4, 0 };

/* ------------------------------------------------------------------ */
/* Vaos por fase (mesmo contrato do build_placeholder_art: chao plano   */
/* com vaos; colisao le estas tabelas via stage_map.c).                */
/* ------------------------------------------------------------------ */

static const JourneyGap GAPS_S0[] = { { 160, 208 }, { 320, 352 } };
static const JourneyGap GAPS_S1[] = { { 150, 190 }, { 360, 392 } };
static const JourneyGap GAPS_S2[] = { { 120, 160 }, { 310, 342 } };
static const JourneyGap GAPS_S3[] = { { 170, 210 }, { 380, 412 } };
static const JourneyGap GAPS_S4[] = { { 140, 176 }, { 260, 296 }, { 420, 452 } };

/* ------------------------------------------------------------------ */
/* Overrides de paleta RGB333 (steps 0..7). Indice 0 e preservado do    */
/* master na aplicacao, entao a entrada [0] aqui e morta.              */
/* ------------------------------------------------------------------ */

#define PAL16(name) static const u8 name[16][3]

PAL16(PAL0_LAGO) = {
    {0,0,0}, {4,6,7}, {3,5,7}, {2,4,6}, {1,3,5}, {6,7,7}, {5,6,7}, {1,3,6}, {0,2,5}, {1,2,4}, {0,3,3}, {0,2,2}, {0,3,2}, {1,4,2}, {2,5,3}, {0,0,0}
};
PAL16(PAL1_LAGO) = {
    {0,0,0}, {5,5,2}, {6,6,3}, {7,7,4}, {4,4,2}, {3,3,2}, {5,4,1}, {2,3,2}, {1,2,2}, {6,7,5}, {3,4,3}, {2,4,4}, {1,3,3}, {4,5,4}, {6,6,4}, {2,2,1}
};
PAL16(PAL0_CREPUSCULO) = {
    {0,0,0}, {7,7,5}, {7,6,3}, {7,5,2}, {7,4,1}, {6,3,1}, {5,2,1}, {4,1,2}, {3,1,3}, {2,1,3}, {3,1,0}, {2,1,0}, {5,2,1}, {4,2,1}, {3,1,1}, {0,0,0}
};
PAL16(PAL1_CREPUSCULO) = {
    {0,0,0}, {5,3,1}, {6,4,2}, {7,5,3}, {4,2,1}, {3,2,1}, {2,1,1}, {6,3,2}, {5,2,1}, {7,6,4}, {4,3,2}, {3,2,2}, {2,1,2}, {5,4,3}, {6,5,4}, {3,3,2}
};
PAL16(PAL0_NOITE) = {
    {0,0,0}, {0,0,1}, {0,0,2}, {0,1,3}, {1,1,4}, {0,0,3}, {1,1,2}, {0,0,2}, {0,0,1}, {1,0,2}, {0,1,1}, {0,0,1}, {0,1,2}, {0,1,3}, {1,2,4}, {0,0,0}
};
PAL16(PAL1_NOITE) = {
    {0,0,0}, {2,2,3}, {3,3,4}, {4,4,5}, {2,2,2}, {1,1,2}, {3,2,4}, {2,1,3}, {4,3,5}, {5,5,6}, {3,3,3}, {2,2,4}, {1,1,3}, {4,4,4}, {5,4,5}, {2,2,1}
};
PAL16(PAL0_AURORA) = {
    {0,0,0}, {1,6,5}, {0,5,5}, {1,4,6}, {2,3,6}, {0,6,4}, {3,5,7}, {2,2,6}, {1,1,5}, {3,2,6}, {0,3,4}, {0,2,3}, {1,5,3}, {2,6,4}, {3,6,5}, {0,0,0}
};
PAL16(PAL1_AURORA) = {
    {0,0,0}, {4,2,5}, {5,3,6}, {6,4,7}, {3,2,4}, {2,1,3}, {4,3,6}, {3,1,5}, {5,2,6}, {6,5,7}, {4,4,6}, {3,3,5}, {2,2,4}, {5,5,7}, {6,6,7}, {3,2,3}
};

/* ------------------------------------------------------------------ */

static const StageDef STAGES[JOURNEY_STAGE_COUNT] = {
    /* 0 */ { "VALE VERDE",     NULL,               NULL,               FALSE, FALSE, 6, EX_S0, EA_S0, 2, GAPS_S0 },
    /* 1 */ { "LAGO ESPELHADO", PAL0_LAGO,          PAL1_LAGO,          TRUE,  FALSE, 6, EX_S1, EA_S1, 2, GAPS_S1 },
    /* 2 */ { "CREPUSCULO",     PAL0_CREPUSCULO,    PAL1_CREPUSCULO,    FALSE, FALSE, 6, EX_S2, EA_S2, 2, GAPS_S2 },
    /* 3 */ { "NOITE SEM LUA",  PAL0_NOITE,         PAL1_NOITE,         FALSE, TRUE,  6, EX_S3, EA_S3, 2, GAPS_S3 },
    /* 4 */ { "AURORA FINAL",   PAL0_AURORA,        PAL1_AURORA,        FALSE, TRUE,  6, EX_S4, EA_S4, 3, GAPS_S4 },
};

JourneyState gJourney;

void JOURNEY_resetNewGame(void)
{
    gJourney.stageIndex = 0u;
    gJourney.unlockedMask = 0x01u;
    gJourney.bossPending = FALSE;
    gJourney.finalBoss = FALSE;
    gJourney.journeyDone = FALSE;
    gJourney.introSeen = FALSE;
    gJourney.rngSeed = 0x2A5Fu;
}

const StageDef* JOURNEY_stageDef(u8 idx)
{
    if (idx >= JOURNEY_STAGE_COUNT) idx = 0u;
    return &STAGES[idx];
}

AppScene JOURNEY_sceneAfterStageGoal(void)
{
    /*
     * Whispy guarda a saida da fase 2 (idx 1); o Fury final guarda a saida da
     * fase 5 (idx 4). Demais goals apenas avancam a fase.
     */
    if (gJourney.stageIndex == 1u)
    {
        gJourney.bossPending = TRUE;
        gJourney.finalBoss = FALSE;
        return APP_SCENE_BOSS;
    }
    if (gJourney.stageIndex >= (JOURNEY_STAGE_COUNT - 1u))
    {
        gJourney.bossPending = TRUE;
        gJourney.finalBoss = TRUE;
        return APP_SCENE_BOSS;
    }

    gJourney.stageIndex++;
    gJourney.unlockedMask |= (u8) (1u << gJourney.stageIndex);
    return APP_SCENE_STAGE;
}

AppScene JOURNEY_sceneAfterBossVictory(void)
{
    if (!gJourney.finalBoss)
    {
        /* Whispy caiu: abre a fase 3 (idx 2). */
        gJourney.stageIndex = 2u;
        gJourney.unlockedMask |= (u8) (1u << 2u);
        gJourney.bossPending = FALSE;
        return APP_SCENE_STAGE;
    }

    gJourney.journeyDone = TRUE;
    gJourney.bossPending = FALSE;
    return APP_SCENE_ENDING;
}

AppScene JOURNEY_retryScene(void)
{
    return gJourney.bossPending ? APP_SCENE_BOSS : APP_SCENE_STAGE;
}

u16 JOURNEY_rand(void)
{
    /* LCG 16 bits deterministico; sem float, sem divisao. */
    gJourney.rngSeed = (u16) ((gJourney.rngSeed * 20077u) + 12345u);
    return gJourney.rngSeed;
}

void JOURNEY_seedFromInput(void)
{
    gJourney.rngSeed = (u16) (gApp.totalFrames | 0x0001u);
}

void JOURNEY_applySramOverride(void)
{
    const u32 offset = 0x140u;
    bool magicOk;

    SRAM_enable();
    magicOk = ((SRAM_readByte(offset + 0u) == (u8) 'J') &&
               (SRAM_readByte(offset + 1u) == (u8) 'B') &&
               (SRAM_readByte(offset + 2u) == (u8) 'O') &&
               (SRAM_readByte(offset + 3u) == (u8) 'Y'));

    if (magicOk)
    {
        u8 idx = SRAM_readByte(offset + 4u);
        u8 flags = SRAM_readByte(offset + 5u);

        if (idx >= JOURNEY_STAGE_COUNT) idx = 0u;

        gJourney.stageIndex = idx;
        gJourney.bossPending = ((flags & 1u) != 0u);
        gJourney.finalBoss = ((flags & 2u) != 0u);

        /* Consome o pedido: warm reset nao replique. */
        SRAM_writeByte(offset + 0u, 0u);
        SRAM_writeByte(offset + 1u, 0u);
    }
    SRAM_disable();
}

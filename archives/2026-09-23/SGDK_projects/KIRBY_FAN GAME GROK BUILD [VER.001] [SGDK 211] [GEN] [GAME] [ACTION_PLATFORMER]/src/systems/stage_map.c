#include <genesis.h>

#include "systems/stage_map.h"

/*
 * Gaps must match data/builders/build_placeholder_art.py build_terrain().
 * Duplicated constants are a drift risk, so the gate in FASE 1 closeout
 * compares them; see doc/14-plano-de-provas-qa.md.
 *
 * MISSAO 2026-08-24: a tabela passou a ser instalavel por fase (journey.c).
 * O default abaixo e exatamente a tabela original da FASE 1, preservada para
 * que o comportamento das capturas seladas continue valido.
 */

#define STAGE_MAX_GAPS 4

typedef struct { s16 x0; s16 x1; } StageGap;

static StageGap s_gaps[STAGE_MAX_GAPS] = {
    { 160, 208 },
    { 320, 352 },
};

static u8 s_gapCount = 2u;

void STAGE_installGaps(const s16* pairsX0X1, u8 gapCount)
{
    u8 i;

    if (gapCount > STAGE_MAX_GAPS) gapCount = STAGE_MAX_GAPS;
    if ((pairsX0X1 == NULL) || (gapCount == 0u))
    {
        /* Volta ao default canonical da FASE 1. */
        s_gaps[0].x0 = 160; s_gaps[0].x1 = 208;
        s_gaps[1].x0 = 320; s_gaps[1].x1 = 352;
        s_gapCount = 2u;
        return;
    }

    for (i = 0u; i < gapCount; i++)
    {
        s_gaps[i].x0 = pairsX0X1[(u16) i * 2u];
        s_gaps[i].x1 = pairsX0X1[((u16) i * 2u) + 1u];
    }
    s_gapCount = gapCount;
}

bool STAGE_groundAt(s16 planeX, fix16* outCentreY)
{
    u8 i;

    if ((planeX < 0) || (planeX >= STAGE_PLANE_WIDTH)) return FALSE;

    for (i = 0u; i < s_gapCount; i++)
    {
        if ((planeX >= s_gaps[i].x0) && (planeX < s_gaps[i].x1)) return FALSE;
    }

    *outCentreY = FIX16(STAGE_GROUND_TOP - STAGE_FOOT_OFFSET);
    return TRUE;
}

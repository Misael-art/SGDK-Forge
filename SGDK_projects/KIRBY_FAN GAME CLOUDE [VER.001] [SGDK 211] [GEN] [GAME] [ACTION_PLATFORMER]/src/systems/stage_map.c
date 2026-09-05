#include <genesis.h>

#include "systems/stage_map.h"

/*
 * Gaps must match data/builders/build_placeholder_art.py build_terrain().
 * Duplicated constants are a drift risk, so the gate in FASE 1 closeout
 * compares them; see doc/14-plano-de-provas-qa.md.
 */
typedef struct { s16 x0; s16 x1; } StageGap;

static const StageGap GAPS[] = {
    { 160, 208 },
    { 320, 352 },
};

#define GAP_COUNT (sizeof(GAPS) / sizeof(GAPS[0]))

bool STAGE_groundAt(s16 planeX, fix16* outCentreY)
{
    u16 i;

    if ((planeX < 0) || (planeX >= STAGE_PLANE_WIDTH)) return FALSE;

    for (i = 0u; i < GAP_COUNT; i++)
    {
        if ((planeX >= GAPS[i].x0) && (planeX < GAPS[i].x1)) return FALSE;
    }

    *outCentreY = FIX16(STAGE_GROUND_TOP - STAGE_FOOT_OFFSET);
    return TRUE;
}

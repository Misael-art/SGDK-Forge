#ifndef FIGHT_STAGE_H
#define FIGHT_STAGE_H
/* H40, 64x32: A and WINDOW intentionally share a stationary UI map.
 * Must be entered with display disabled, before HUD construction. */
void FIGHT_STAGE_setup(void);
bool FIGHT_STAGE_init(u16 lowBase);
void FIGHT_STAGE_update(void);
u16 FIGHT_STAGE_restoreCount(void);
bool FIGHT_STAGE_takeHudInvalidation(void);
#ifndef MG_STAGE_SOURCE_STREAM
/* Runtime facts, exported by diagnostic ROMs; tile counts are not estimates. */
enum { STAGE_INIT_PENDING, STAGE_INIT_READY, STAGE_INIT_CAPACITY,
       STAGE_INIT_COMPRESSED, STAGE_INIT_DIMENSIONS, STAGE_INIT_MAP,
       STAGE_INIT_NO_TRANSPARENT_TILE };
typedef struct {
    u16 status, lowBase, spriteStart, capacity, required, farTiles, nearTiles;
} FightStageInitDiagnostics;
const FightStageInitDiagnostics *FIGHT_STAGE_initDiagnostics(void);
#endif
#ifdef MG_STAGE_SOURCE_STREAM
void FIGHT_STAGE_streamStats(u16 *capacity, u16 *resident, u16 *peakWanted,
                             u16 *overflows, u16 *restores, u16 *uploadBytes,
                             u16 *mapBytes, u16 *scrollBytes,
                             u16 *peakUploadBytes, u16 *peakMapBytes,
                             u16 *peakScrollBytes, u16 *peakTotalBytes);
#endif
#endif

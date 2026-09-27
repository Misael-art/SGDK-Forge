#ifndef FIGHT_STAGE_H
#define FIGHT_STAGE_H
/* H40, 64x32: A and WINDOW intentionally share a stationary UI map.
 * Must be entered with display disabled, before HUD construction. */
void FIGHT_STAGE_setup(void);
bool FIGHT_STAGE_init(u16 lowBase);
void FIGHT_STAGE_update(void);
u16 FIGHT_STAGE_restoreCount(void);
bool FIGHT_STAGE_takeHudInvalidation(void);
#ifdef MG_STAGE_SOURCE_STREAM
void FIGHT_STAGE_streamStats(u16 *capacity, u16 *resident, u16 *peakWanted,
                             u16 *overflows, u16 *restores, u16 *uploadBytes,
                             u16 *mapBytes, u16 *scrollBytes,
                             u16 *peakUploadBytes, u16 *peakMapBytes,
                             u16 *peakScrollBytes, u16 *peakTotalBytes);
#endif
#endif

#ifndef AUDIO_XGM_ROUTER_H
#define AUDIO_XGM_ROUTER_H

#include <genesis.h>

/*
 * SINGLE OWNER of FM, PSG and PCM. doc/ARCHITECTURE.md section 6.1.
 *
 * Nothing outside this module may call PSG_*, write a YM2612 register, or touch
 * SOUND_PCM_CH1. Those three prohibitions are enforced by
 * tools/harness/audio_gates.py (gates A1-A3).
 *
 * doc/SOUNDMAP.md section 2: SFX never steals a music channel -- not by policy,
 * by ARCHITECTURE. FM1-6 and PSG belong to the XGM2 music driver; every SFX
 * goes out over PCM channels 2 and 3. PCM1 is reserved for the music's own
 * samples.
 *
 * That leaves TWO usable SFX channels, so the priority table below is what
 * decides which sound the player actually hears.
 */

typedef enum SfxId {
    SFX_INHALE = 0,
    SFX_SWALLOW,
    SFX_HURT,
    SFX_COUNT
} SfxId;

/* Priority tiers from doc/SOUNDMAP.md section 3. Values are the 0..15 scale
 * XGM2_playPCMEx expects; a new sound replaces the current one when its
 * priority is >= the one playing. */
#define SFX_PRIO_STATE      15   /* death, boss defeat: irreversible */
#define SFX_PRIO_DAMAGE     13   /* Kirby or boss took a hit */
#define SFX_PRIO_PLAYER_VERB 11  /* inhale, swallow, spit, ability gained */
#define SFX_PRIO_ABILITY     9
#define SFX_PRIO_ENEMY       7
#define SFX_PRIO_MOVEMENT    5
#define SFX_PRIO_AMBIENT     3
#define SFX_PRIO_UI          1

void AUDIO_routerInit(void);

/* Music. Passing NULL stops playback. */
void AUDIO_playMusic(const u8* song);
void AUDIO_stopMusic(void);

/* Fire an SFX. Returns FALSE when priority lost the arbitration. */
bool AUDIO_playSfx(SfxId id, u16 priority);

/* Once per frame, after the scene has run. Drives ducking and the one-slot
 * queue for high-priority sounds. */
void AUDIO_routerTick(void);

/* Telemetry for the harness. */
u16 AUDIO_getDuckFrames(void);
u16 AUDIO_getRejectedCount(void);

#endif

#include <genesis.h>

#include "audio/xgm_router.h"
#include "resources.h"

/*
 * Ducking table, doc/SOUNDMAP.md section 6.
 *
 * Nothing below priority 9 ducks. Ducking on an ability attack -- which fires
 * several times a second -- would make the music pulse continuously, and that
 * reads as a defect rather than as emphasis.
 */
#define DUCK_HEAVY_PRIO 13
#define DUCK_HEAVY_VOL 50
#define DUCK_HEAVY_FRAMES 12

#define DUCK_LIGHT_PRIO 11
#define DUCK_LIGHT_VOL 75
#define DUCK_LIGHT_FRAMES 8

#define MUSIC_VOL_FULL 100

/* Enemy-death anti-machinegun window, doc/SOUNDMAP.md section 3.1. Three deaths
 * in three frames would otherwise retrigger the same sample three times and
 * sound like a bug. */
#define SFX_REPEAT_LOCK 4

typedef struct SfxDef {
    const u8* data;
    u32 len;
    SoundPCMChannel channel;
} SfxDef;

static SfxDef s_sfx[SFX_COUNT];
static u8 s_repeatLock[SFX_COUNT];

static u16 s_duckFrames;
static u16 s_duckVolume;
static u16 s_rejected;

/* One-slot queue: a priority >= 11 sound is never dropped silently, it waits a
 * single frame. A queue deeper than one would let audio drift away from the
 * event that caused it, which is worse than losing it. */
static SfxId s_queued;
static u16 s_queuedPrio;
static bool s_hasQueued;

/* MISSAO 2026-08-24: tom de UI dos minigames. Canal fixo do PSG so e valido
 * com a musica parada; ver contrato em xgm_router.h. */
#define UI_TONE_CHANNEL 3u          /* PSG4 e ruido; canais 1..3 sao tom */
static u16 s_uiToneFrames;
static bool s_musicOn;

void AUDIO_routerInit(void)
{
    u16 i;

    XGM2_loadDriver(TRUE);

    s_sfx[SFX_INHALE].data = sfx_inhale;
    s_sfx[SFX_INHALE].len = sizeof(sfx_inhale);
    s_sfx[SFX_INHALE].channel = SOUND_PCM_CH3;

    s_sfx[SFX_SWALLOW].data = sfx_swallow;
    s_sfx[SFX_SWALLOW].len = sizeof(sfx_swallow);
    s_sfx[SFX_SWALLOW].channel = SOUND_PCM_CH2;

    s_sfx[SFX_HURT].data = sfx_hurt;
    s_sfx[SFX_HURT].len = sizeof(sfx_hurt);
    s_sfx[SFX_HURT].channel = SOUND_PCM_CH2;

    for (i = 0u; i < SFX_COUNT; i++) s_repeatLock[i] = 0u;

    s_duckFrames = 0u;
    s_duckVolume = MUSIC_VOL_FULL;
    s_rejected = 0u;
    s_hasQueued = FALSE;

    XGM2_setFMVolume(MUSIC_VOL_FULL);
    XGM2_setPSGVolume(MUSIC_VOL_FULL);
}

void AUDIO_playMusic(const u8* song)
{
    if (song == NULL) { XGM2_stop(); s_musicOn = FALSE; return; }
    XGM2_play(song);
    XGM2_setFMVolume(MUSIC_VOL_FULL);
    XGM2_setPSGVolume(MUSIC_VOL_FULL);
    s_musicOn = TRUE;
    s_duckFrames = 0u;
    s_duckVolume = MUSIC_VOL_FULL;
}

void AUDIO_stopMusic(void) { XGM2_stop(); s_musicOn = FALSE; }

bool AUDIO_playUiTone(u16 hz, u8 frames)
{
    u32 div;

    /* Contrato do header: com musica tocando, o PSG nao e nosso. */
    if (s_musicOn || (hz == 0u)) return FALSE;

    /* PSG clock: 3579545 Hz / 32 por passo do tone register => ~111861. */
    div = 111861UL / (u32) hz;
    if (div == 0u) div = 1u;
    if (div > 1023u) div = 1023u;

    PSG_setFrequency(UI_TONE_CHANNEL, (u16) div);
    PSG_setEnvelope(UI_TONE_CHANNEL, PSG_ENVELOPE_MAX);   /* volume maximo */
    s_uiToneFrames = frames ? (u16) frames : 1u;
    return TRUE;
}

static void apply_duck(u16 priority)
{
    if (priority >= DUCK_HEAVY_PRIO)
    {
        s_duckVolume = DUCK_HEAVY_VOL;
        s_duckFrames = DUCK_HEAVY_FRAMES;
    }
    else if (priority >= DUCK_LIGHT_PRIO)
    {
        if (s_duckVolume > DUCK_LIGHT_VOL)
        {
            s_duckVolume = DUCK_LIGHT_VOL;
            s_duckFrames = DUCK_LIGHT_FRAMES;
        }
    }
    else
    {
        return;              /* below 11: no ducking, on purpose */
    }

    XGM2_setFMVolume(s_duckVolume);
    XGM2_setPSGVolume(s_duckVolume);
}

static bool fire(SfxId id, u16 priority)
{
    const SfxDef* def = &s_sfx[id];
    if (def->data == NULL) return FALSE;

    if (!XGM2_playPCMEx(def->data, def->len, def->channel,
                        (u8) priority, FALSE, FALSE))
    {
        return FALSE;
    }

    s_repeatLock[id] = SFX_REPEAT_LOCK;
    apply_duck(priority);
    return TRUE;
}

bool AUDIO_playSfx(SfxId id, u16 priority)
{
    if (id >= SFX_COUNT) return FALSE;

    /* Same sample retriggered inside the lock window is dropped outright. */
    if (s_repeatLock[id] > 0u) return FALSE;

    if (fire(id, priority)) return TRUE;

    /* Lost the arbitration. Priority >= 11 gets one frame of grace. */
    if ((priority >= DUCK_LIGHT_PRIO) && !s_hasQueued)
    {
        s_queued = id;
        s_queuedPrio = priority;
        s_hasQueued = TRUE;
        return FALSE;
    }

    s_rejected++;
    return FALSE;
}

void AUDIO_routerTick(void)
{
    u16 i;

    for (i = 0u; i < SFX_COUNT; i++)
        if (s_repeatLock[i] > 0u) s_repeatLock[i]--;

    /* MISSAO 2026-08-24: expiracao do tom de UI dos minigames. */
    if (s_uiToneFrames > 0u)
    {
        s_uiToneFrames--;
        if (s_uiToneFrames == 0u)
        {
            PSG_setEnvelope(UI_TONE_CHANNEL, PSG_ENVELOPE_MIN);
        }
    }

    if (s_hasQueued)
    {
        s_hasQueued = FALSE;
        if (!fire(s_queued, s_queuedPrio)) s_rejected++;
    }

    if (s_duckFrames > 0u)
    {
        s_duckFrames--;
        if (s_duckFrames == 0u)
        {
            s_duckVolume = MUSIC_VOL_FULL;
            XGM2_setFMVolume(MUSIC_VOL_FULL);
            XGM2_setPSGVolume(MUSIC_VOL_FULL);
        }
    }
}

u16 AUDIO_getDuckFrames(void) { return s_duckFrames; }
u16 AUDIO_getRejectedCount(void) { return s_rejected; }

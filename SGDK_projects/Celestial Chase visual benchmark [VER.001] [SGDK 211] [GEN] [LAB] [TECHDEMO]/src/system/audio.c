#include <genesis.h>

#include "game_vars.h"
#include "resources.h"
#include "system/audio.h"

#define AUDIO_PCM_CH_FX_PRIMARY SOUND_PCM_CH2
#define AUDIO_PCM_CH_FX_UI SOUND_PCM_CH3
#define AUDIO_PROBE_SRAM_OFFSET 0x800
#define AUDIO_PROBE_SCHEMA_VERSION 1
#define AUDIO_PROBE_WORDS 13
#define AUDIO_PROBE_TOTAL_BYTES (8 + (AUDIO_PROBE_WORDS * 2))
#define AUDIO_PROBE_SAMPLE_PERIOD 4
#define AUDIO_PROBE_EXPORT_SAMPLES 15

static bool sScorePlaying;
static bool sPaused;
static u8 sIntensity;
static u16 sPressureCueTimer;
static AudioMusicState sMusicState;
static u16 sProbeFrameCadence;
static u16 sProbeSamples;
static u16 sProbeMaxCpuLoad;
static u16 sProbeMaxDmaWait;
static u16 sProbeMaxMissedFrames;
static u16 sProbeSimultaneousSamples;
static u16 sProbeCueRequests;
static u16 sProbeCueAccepted;

static bool AUDIO_isBedState(AudioMusicState state)
{
    return (state == AUDIO_MUSIC_MENU)
        || (state == AUDIO_MUSIC_INTRO)
        || (state == AUDIO_MUSIC_PRESSURE)
        || (state == AUDIO_MUSIC_CLIMAX);
}

static void AUDIO_writeProbeWord(u32* offset, u16 value)
{
    SRAM_writeByte(*offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(*offset + 1, (u8)(value & 0xFF));
    *offset += 2;
}

static void AUDIO_exportProbe(void)
{
    u32 offset = AUDIO_PROBE_SRAM_OFFSET;
    u16 pcmMask = XGM2_isPlayingPCM(SOUND_PCM_CH2_MSK | SOUND_PCM_CH3_MSK);

    SRAM_enable();
    SRAM_writeByte(offset + 0, 'A');
    SRAM_writeByte(offset + 1, 'U');
    SRAM_writeByte(offset + 2, 'D');
    SRAM_writeByte(offset + 3, '2');
    SRAM_writeByte(offset + 4, 0);
    SRAM_writeByte(offset + 5, AUDIO_PROBE_SCHEMA_VERSION);
    SRAM_writeByte(offset + 6, 0);
    SRAM_writeByte(offset + 7, AUDIO_PROBE_TOTAL_BYTES);
    offset += 8;
    AUDIO_writeProbeWord(&offset, (u16)gApp.currentScene);
    AUDIO_writeProbeWord(&offset, (u16)sMusicState);
    AUDIO_writeProbeWord(&offset, XGM2_isPlaying() ? 1 : 0);
    AUDIO_writeProbeWord(&offset, pcmMask);
    AUDIO_writeProbeWord(&offset, sProbeSamples);
    AUDIO_writeProbeWord(&offset, sProbeMaxCpuLoad);
    AUDIO_writeProbeWord(&offset, sProbeMaxDmaWait);
    AUDIO_writeProbeWord(&offset, sProbeMaxMissedFrames);
    AUDIO_writeProbeWord(&offset, sProbeSimultaneousSamples);
    AUDIO_writeProbeWord(&offset, sProbeCueRequests);
    AUDIO_writeProbeWord(&offset, sProbeCueAccepted);
    AUDIO_writeProbeWord(&offset, XGM2_getDebugFrameCounter());
    AUDIO_writeProbeWord(&offset, gApp.targetFps);
    SRAM_disable();
}

static void AUDIO_sampleProbe(void)
{
    u16 cpuLoad;
    u16 dmaWait;
    u16 missedFrames;
    u16 pcmMask;

    sProbeFrameCadence++;
    if (sProbeFrameCadence < AUDIO_PROBE_SAMPLE_PERIOD) {
        return;
    }
    sProbeFrameCadence = 0;

    cpuLoad = XGM2_getCPULoad(TRUE);
    dmaWait = XGM2_getDMAWaitTime(TRUE);
    missedFrames = XGM2_getDebugMissedFrames();
    pcmMask = XGM2_isPlayingPCM(SOUND_PCM_CH2_MSK | SOUND_PCM_CH3_MSK);
    sProbeSamples++;
    if (cpuLoad > sProbeMaxCpuLoad) sProbeMaxCpuLoad = cpuLoad;
    if (dmaWait > sProbeMaxDmaWait) sProbeMaxDmaWait = dmaWait;
    if (missedFrames > sProbeMaxMissedFrames) sProbeMaxMissedFrames = missedFrames;
    if (XGM2_isPlaying() && pcmMask != 0) sProbeSimultaneousSamples++;

    if ((sProbeSamples % AUDIO_PROBE_EXPORT_SAMPLES) == 0) {
        AUDIO_exportProbe();
    }
}

static bool AUDIO_playPCM(
    const u8* sample,
    u32 length,
    SoundPCMChannel channel,
    u8 priority
)
{
    bool accepted;

    sProbeCueRequests++;
    accepted = XGM2_playPCMEx(sample, length, channel, priority, FALSE, FALSE);
    if (accepted) sProbeCueAccepted++;
    return accepted;
}

static void AUDIO_applyMusicState(AudioMusicState state, bool forceRestart)
{
    bool bed;
    u16 fmVolume;
    u16 psgVolume;

    bed = AUDIO_isBedState(state);
    sPressureCueTimer = 0;

    if (bed) {
        switch (state)
        {
            case AUDIO_MUSIC_MENU:
                sIntensity = 1;
                fmVolume = 55;
                psgVolume = 45;
                break;
            case AUDIO_MUSIC_PRESSURE:
                sIntensity = 2;
                fmVolume = 85;
                psgVolume = 75;
                break;
            case AUDIO_MUSIC_CLIMAX:
                sIntensity = 3;
                fmVolume = 100;
                psgVolume = 90;
                break;
            case AUDIO_MUSIC_INTRO:
            default:
                sIntensity = 1;
                fmVolume = 72;
                psgVolume = 60;
                break;
        }
        if (forceRestart || !XGM2_isPlaying()) {
            XGM2_setLoopNumber(-1);
            XGM2_play(mus_chase_core);
        }
        XGM2_setFMVolume(fmVolume);
        XGM2_setPSGVolume(psgVolume);
        sScorePlaying = TRUE;
        return;
    }

    XGM2_stop();
    sScorePlaying = FALSE;
    sIntensity = 0;
    switch (state)
    {
        case AUDIO_MUSIC_VICTORY:
            AUDIO_playPCM(snd_chase_victory, sizeof(snd_chase_victory), AUDIO_PCM_CH_FX_PRIMARY, 15);
            break;
        case AUDIO_MUSIC_FAILURE:
            AUDIO_playPCM(snd_chase_failure, sizeof(snd_chase_failure), AUDIO_PCM_CH_FX_PRIMARY, 15);
            break;
        default:
            break;
    }
}

void AUDIO_stopAll(void)
{
    AUDIO_exportProbe();
    XGM2_stop();
    XGM2_stopPCM(AUDIO_PCM_CH_FX_PRIMARY);
    XGM2_stopPCM(AUDIO_PCM_CH_FX_UI);
    sScorePlaying = FALSE;
    sPaused = FALSE;
    sIntensity = 1;
    sPressureCueTimer = 0;
    sMusicState = AUDIO_MUSIC_MENU;
}

void AUDIO_init(void)
{
    Z80_loadDriver(Z80_DRIVER_XGM2, TRUE);
    sScorePlaying = FALSE;
    sPaused = FALSE;
    sIntensity = 1;
    sPressureCueTimer = 0;
    sMusicState = AUDIO_MUSIC_MENU;
    sProbeFrameCadence = 0;
    sProbeSamples = 0;
    sProbeMaxCpuLoad = 0;
    sProbeMaxDmaWait = 0;
    sProbeMaxMissedFrames = 0;
    sProbeSimultaneousSamples = 0;
    sProbeCueRequests = 0;
    sProbeCueAccepted = 0;
}

void AUDIO_setMusicState(AudioMusicState state)
{
    AudioMusicState previous = sMusicState;
    bool enteringBed = !AUDIO_isBedState(previous) && AUDIO_isBedState(state);

    if (previous == state
        && !sPaused
        && (!AUDIO_isBedState(state) || XGM2_isPlaying())) {
        return;
    }
    sMusicState = state;
    if (!sPaused) {
        AUDIO_applyMusicState(state, enteringBed);
    }
}

AudioMusicState AUDIO_musicState(void)
{
    return sMusicState;
}

void AUDIO_startChaseScore(void)
{
    sPaused = FALSE;
    AUDIO_setMusicState(AUDIO_MUSIC_INTRO);
}

void AUDIO_stopChaseScore(void)
{
    XGM2_stop();
    sScorePlaying = FALSE;
    sPressureCueTimer = 0;
}

void AUDIO_pause(void)
{
    if (sScorePlaying) XGM2_pause();
    XGM2_stopPCM(AUDIO_PCM_CH_FX_PRIMARY);
    XGM2_stopPCM(AUDIO_PCM_CH_FX_UI);
    sPaused = TRUE;
}

void AUDIO_resume(void)
{
    if (sPaused) {
        sPaused = FALSE;
        if (sScorePlaying) XGM2_resume();
        AUDIO_applyMusicState(sMusicState, FALSE);
    }
}

void AUDIO_setIntensity(u8 intensity)
{
    u8 clamped = (intensity > 3) ? 3 : intensity;

    if (clamped <= 1) {
        AUDIO_setMusicState(AUDIO_MUSIC_INTRO);
        return;
    }
    if (clamped == 2) {
        AUDIO_setMusicState(AUDIO_MUSIC_PRESSURE);
        return;
    }
    AUDIO_setMusicState(AUDIO_MUSIC_CLIMAX);
}

void AUDIO_playCue(AudioCue cue)
{
    switch (cue)
    {
        case AUDIO_CUE_MENU:
            AUDIO_playPCM(snd_chase_menu, sizeof(snd_chase_menu), AUDIO_PCM_CH_FX_UI, 5);
            break;
        case AUDIO_CUE_JUMP:
            AUDIO_playPCM(snd_chase_jump, sizeof(snd_chase_jump), AUDIO_PCM_CH_FX_UI, 5);
            break;
        case AUDIO_CUE_LAND:
            AUDIO_playPCM(snd_chase_land, sizeof(snd_chase_land), AUDIO_PCM_CH_FX_UI, 4);
            break;
        case AUDIO_CUE_STRIKE:
            AUDIO_playPCM(snd_chase_hit, sizeof(snd_chase_hit), AUDIO_PCM_CH_FX_PRIMARY, 13);
            break;
        case AUDIO_CUE_PAUSE:
            AUDIO_playPCM(snd_chase_menu, sizeof(snd_chase_menu), AUDIO_PCM_CH_FX_UI, 8);
            break;
        case AUDIO_CUE_PULSE:
            AUDIO_playPCM(snd_chase_pulse, sizeof(snd_chase_pulse), AUDIO_PCM_CH_FX_PRIMARY, 15);
            break;
        case AUDIO_CUE_PICKUP:
            AUDIO_playPCM(snd_chase_pickup, sizeof(snd_chase_pickup), AUDIO_PCM_CH_FX_UI, 7);
            break;
        case AUDIO_CUE_VICTORY:
            AUDIO_playPCM(snd_chase_victory, sizeof(snd_chase_victory), AUDIO_PCM_CH_FX_PRIMARY, 15);
            break;
        case AUDIO_CUE_FAILURE:
            AUDIO_playPCM(snd_chase_failure, sizeof(snd_chase_failure), AUDIO_PCM_CH_FX_PRIMARY, 15);
            break;
        case AUDIO_CUE_PRESSURE:
            AUDIO_playPCM(snd_chase_pressure, sizeof(snd_chase_pressure), AUDIO_PCM_CH_FX_UI, 6);
            break;
        default:
            break;
    }
}

void AUDIO_update(void)
{
    u16 interval;

    AUDIO_sampleProbe();
    if (!sScorePlaying || sPaused || sIntensity < 2) {
        return;
    }

    interval = (sIntensity >= 3) ? 180 : 300;
    sPressureCueTimer++;
    if (sPressureCueTimer >= interval) {
        sPressureCueTimer = 0;
        AUDIO_playCue(AUDIO_CUE_PRESSURE);
    }
}

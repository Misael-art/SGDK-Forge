#include <genesis.h>

#include "resources.h"
#include "system/audio.h"

#define AUDIO_PCM_CH_MUSIC SOUND_PCM_CH1
#define AUDIO_PCM_CH_FX_PRIMARY SOUND_PCM_CH2
#define AUDIO_PCM_CH_FX_UI SOUND_PCM_CH3

static bool sScorePlaying;
static bool sPaused;
static u8 sIntensity;
static u16 sPressureCueTimer;
static AudioMusicState sMusicState;

static void AUDIO_applyMusicState(AudioMusicState state, bool forceRestart)
{
    bool bed;
    u8 volume;

    bed = (state == AUDIO_MUSIC_MENU) || (state == AUDIO_MUSIC_INTRO) || (state == AUDIO_MUSIC_PRESSURE) || (state == AUDIO_MUSIC_CLIMAX);
    if (!forceRestart && state == sMusicState && ((bed && sScorePlaying) || (!bed && !sScorePlaying))) {
        return;
    }

    XGM2_stopPCM(AUDIO_PCM_CH_MUSIC);
    sScorePlaying = FALSE;
    sPressureCueTimer = 0;

    if (bed) {
        switch (state)
        {
            case AUDIO_MUSIC_MENU:
                sIntensity = 1;
                volume = 4;
                break;
            case AUDIO_MUSIC_PRESSURE:
                sIntensity = 2;
                volume = 7;
                break;
            case AUDIO_MUSIC_CLIMAX:
                sIntensity = 3;
                volume = 9;
                break;
            case AUDIO_MUSIC_INTRO:
            default:
                sIntensity = 1;
                volume = 6;
                break;
        }
        XGM2_playPCMEx(snd_chase_score_loop, sizeof(snd_chase_score_loop), AUDIO_PCM_CH_MUSIC, volume, FALSE, TRUE);
        sScorePlaying = TRUE;
        return;
    }

    sIntensity = 0;
    switch (state)
    {
        case AUDIO_MUSIC_VICTORY:
            XGM2_playPCMEx(snd_chase_victory, sizeof(snd_chase_victory), AUDIO_PCM_CH_MUSIC, 15, FALSE, FALSE);
            break;
        case AUDIO_MUSIC_FAILURE:
            XGM2_playPCMEx(snd_chase_failure, sizeof(snd_chase_failure), AUDIO_PCM_CH_MUSIC, 15, FALSE, FALSE);
            break;
        default:
            break;
    }
}

void AUDIO_stopAll(void)
{
    XGM2_stopPCM(AUDIO_PCM_CH_MUSIC);
    XGM2_stopPCM(AUDIO_PCM_CH_FX_PRIMARY);
    XGM2_stopPCM(AUDIO_PCM_CH_FX_UI);
    PSG_setEnvelope(0, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(1, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(2, PSG_ENVELOPE_MIN);
    sScorePlaying = FALSE;
    sPaused = FALSE;
    sIntensity = 1;
    sPressureCueTimer = 0;
    sMusicState = AUDIO_MUSIC_MENU;
}

void AUDIO_init(void)
{
    Z80_loadDriver(Z80_DRIVER_XGM2, TRUE);
    PSG_reset();
    sScorePlaying = FALSE;
    sPaused = FALSE;
    sIntensity = 1;
    sPressureCueTimer = 0;
    sMusicState = AUDIO_MUSIC_MENU;
}

void AUDIO_setMusicState(AudioMusicState state)
{
    AudioMusicState previous = sMusicState;

    sMusicState = state;
    if (!sPaused) {
        AUDIO_applyMusicState(state, previous != state);
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
    XGM2_stopPCM(AUDIO_PCM_CH_MUSIC);
    sScorePlaying = FALSE;
    sPressureCueTimer = 0;
}

void AUDIO_pause(void)
{
    XGM2_stopPCM(AUDIO_PCM_CH_MUSIC);
    XGM2_stopPCM(AUDIO_PCM_CH_FX_PRIMARY);
    XGM2_stopPCM(AUDIO_PCM_CH_FX_UI);
    sPaused = TRUE;
}

void AUDIO_resume(void)
{
    if (sPaused) {
        sPaused = FALSE;
        AUDIO_applyMusicState(sMusicState, TRUE);
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
            XGM2_playPCMEx(snd_chase_menu, sizeof(snd_chase_menu), AUDIO_PCM_CH_FX_UI, 5, FALSE, FALSE);
            break;
        case AUDIO_CUE_JUMP:
            XGM2_playPCMEx(snd_chase_jump, sizeof(snd_chase_jump), AUDIO_PCM_CH_FX_UI, 5, FALSE, FALSE);
            break;
        case AUDIO_CUE_LAND:
            XGM2_playPCMEx(snd_chase_land, sizeof(snd_chase_land), AUDIO_PCM_CH_FX_UI, 4, FALSE, FALSE);
            break;
        case AUDIO_CUE_STRIKE:
            XGM2_playPCMEx(snd_chase_hit, sizeof(snd_chase_hit), AUDIO_PCM_CH_FX_PRIMARY, 13, FALSE, FALSE);
            break;
        case AUDIO_CUE_PAUSE:
            XGM2_playPCMEx(snd_chase_menu, sizeof(snd_chase_menu), AUDIO_PCM_CH_FX_UI, 8, FALSE, FALSE);
            break;
        case AUDIO_CUE_PULSE:
            XGM2_playPCMEx(snd_chase_pulse, sizeof(snd_chase_pulse), AUDIO_PCM_CH_FX_PRIMARY, 15, FALSE, FALSE);
            break;
        case AUDIO_CUE_PICKUP:
            XGM2_playPCMEx(snd_chase_pickup, sizeof(snd_chase_pickup), AUDIO_PCM_CH_FX_UI, 7, FALSE, FALSE);
            break;
        case AUDIO_CUE_VICTORY:
            XGM2_playPCMEx(snd_chase_victory, sizeof(snd_chase_victory), AUDIO_PCM_CH_FX_PRIMARY, 15, FALSE, FALSE);
            break;
        case AUDIO_CUE_FAILURE:
            XGM2_playPCMEx(snd_chase_failure, sizeof(snd_chase_failure), AUDIO_PCM_CH_FX_PRIMARY, 15, FALSE, FALSE);
            break;
        case AUDIO_CUE_PRESSURE:
            XGM2_playPCMEx(snd_chase_pressure, sizeof(snd_chase_pressure), AUDIO_PCM_CH_FX_UI, 6, FALSE, FALSE);
            break;
        default:
            break;
    }
}

void AUDIO_update(void)
{
    u16 interval;

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

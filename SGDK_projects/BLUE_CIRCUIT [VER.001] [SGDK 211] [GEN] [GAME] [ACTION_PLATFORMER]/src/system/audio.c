#include <genesis.h>

#include "resources.h"
#include "system/audio.h"

static u8 sCueFrames = 0;

static void audioStopPsg(void)
{
    PSG_setEnvelope(0, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(1, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(2, PSG_ENVELOPE_MIN);
}

static void audioPulsePsg(u8 channel, u16 tone, u8 envelope, u8 frames)
{
    PSG_setFrequency(channel, tone);
    PSG_setEnvelope(channel, envelope);
    sCueFrames = frames;
}

void AUDIO_stopAll(void)
{
    audioStopPsg();
    XGM2_stopPCM(SOUND_PCM_CH1);
    XGM2_stopPCM(SOUND_PCM_CH2);
    XGM2_stopPCM(SOUND_PCM_CH3);
}

void AUDIO_init(void)
{
    PSG_reset();
    XGM2_loadDriver(TRUE);
    AUDIO_stopAll();
    sCueFrames = 0;
}

void AUDIO_playCue(AudioCue cue)
{
    switch (cue)
    {
        case AUDIO_CUE_MENU:
            AUDIO_stopAll();
            audioPulsePsg(0, 440, 5, 5);
            break;
        case AUDIO_CUE_JUMP:
            AUDIO_stopAll();
            audioPulsePsg(0, 720, 3, 6);
            break;
        case AUDIO_CUE_LAND:
            AUDIO_stopAll();
            PSG_setNoise(PSG_NOISE_TYPE_PERIODIC, PSG_NOISE_FREQ_CLOCK8);
            PSG_setEnvelope(2, 6);
            sCueFrames = 4;
            break;
        case AUDIO_CUE_STRIKE:
            AUDIO_stopAll();
            audioPulsePsg(1, 180, 2, 8);
            break;
        case AUDIO_CUE_PAUSE:
            AUDIO_stopAll();
            audioPulsePsg(0, 320, 4, 4);
            break;
        case AUDIO_CUE_BRAND_ENGINE_HIT:
            XGM2_playPCMEx(brand_bell_forge, sizeof(brand_bell_forge), SOUND_PCM_CH2, 12, FALSE, FALSE);
            audioPulsePsg(0, 260, 2, 14);
            break;
        case AUDIO_CUE_BRAND_AUTHOR_CLICK:
            XGM2_playPCMEx(brand_typewriter_click, sizeof(brand_typewriter_click), SOUND_PCM_CH3, 4, TRUE, FALSE);
            audioPulsePsg(1, 920, 7, 2);
            break;
        case AUDIO_CUE_BRAND_AUTHOR_BELL:
            XGM2_playPCMEx(brand_bell_terminal, sizeof(brand_bell_terminal), SOUND_PCM_CH2, 10, FALSE, FALSE);
            audioPulsePsg(0, 700, 5, 10);
            break;
        case AUDIO_CUE_BRAND_PROJECT_WHOOSH:
            XGM2_playPCMEx(brand_stamp_whoosh, sizeof(brand_stamp_whoosh), SOUND_PCM_CH2, 11, FALSE, FALSE);
            audioPulsePsg(0, 190, 2, 12);
            break;
        case AUDIO_CUE_BRAND_PROJECT_TAIL:
            XGM2_playPCMEx(brand_reverb_tail, sizeof(brand_reverb_tail), SOUND_PCM_CH3, 8, FALSE, FALSE);
            audioPulsePsg(2, 1160, 4, 8);
            break;
        default:
            sCueFrames = 0;
            break;
    }
}

void AUDIO_update(void)
{
    if (sCueFrames == 0) {
        return;
    }

    sCueFrames--;
    if (sCueFrames == 0) {
        audioStopPsg();
    }
}

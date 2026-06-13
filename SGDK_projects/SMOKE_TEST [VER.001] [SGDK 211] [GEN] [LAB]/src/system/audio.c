#include <genesis.h>

#include "resources.h"
#include "system/audio.h"

static u8 sCueFrames = 0;

void AUDIO_stopAll(void)
{
    PSG_setEnvelope(0, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(1, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(2, PSG_ENVELOPE_MIN);
    XGM2_stopPCM(SOUND_PCM_CH1);
    XGM2_stopPCM(SOUND_PCM_CH2);
    XGM2_stopPCM(SOUND_PCM_CH3);
}

void AUDIO_init(void)
{
    Z80_loadDriver(Z80_DRIVER_XGM2, TRUE);
    PSG_reset();
    AUDIO_stopAll();
    sCueFrames = 0;
}

void AUDIO_playCue(AudioCue cue)
{
    switch (cue)
    {
        case AUDIO_CUE_MENU:
            PSG_setFrequency(0, 440);
            PSG_setEnvelope(0, 5);
            sCueFrames = 5;
            break;
        case AUDIO_CUE_JUMP:
            PSG_setFrequency(0, 720);
            PSG_setEnvelope(0, 3);
            sCueFrames = 6;
            break;
        case AUDIO_CUE_LAND:
            PSG_setNoise(PSG_NOISE_TYPE_PERIODIC, PSG_NOISE_FREQ_CLOCK8);
            PSG_setEnvelope(2, 6);
            sCueFrames = 4;
            break;
        case AUDIO_CUE_STRIKE:
            PSG_setFrequency(1, 180);
            PSG_setEnvelope(1, 2);
            sCueFrames = 8;
            break;
        case AUDIO_CUE_PAUSE:
            PSG_setFrequency(0, 320);
            PSG_setEnvelope(0, 4);
            sCueFrames = 4;
            break;
        case AUDIO_CUE_BRAND_ENGINE_HIT:
            XGM2_playPCMEx(brand_bell_forge, sizeof(brand_bell_forge),
                           SOUND_PCM_CH2, 12, FALSE, FALSE);
            break;
        case AUDIO_CUE_BRAND_AUTHOR_CLICK:
            XGM2_playPCMEx(brand_typewriter_click, sizeof(brand_typewriter_click),
                           SOUND_PCM_CH3, 4, TRUE, FALSE);
            break;
        case AUDIO_CUE_BRAND_AUTHOR_BELL:
            XGM2_playPCMEx(brand_bell_terminal, sizeof(brand_bell_terminal),
                           SOUND_PCM_CH2, 10, FALSE, FALSE);
            break;
        case AUDIO_CUE_BRAND_PROJECT_WHOOSH:
            XGM2_playPCMEx(brand_stamp_whoosh, sizeof(brand_stamp_whoosh),
                           SOUND_PCM_CH2, 11, FALSE, FALSE);
            break;
        case AUDIO_CUE_BRAND_PROJECT_TAIL:
            XGM2_playPCMEx(brand_reverb_tail, sizeof(brand_reverb_tail),
                           SOUND_PCM_CH3, 8, FALSE, FALSE);
            break;
        default:
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
        AUDIO_stopAll();
    }
}

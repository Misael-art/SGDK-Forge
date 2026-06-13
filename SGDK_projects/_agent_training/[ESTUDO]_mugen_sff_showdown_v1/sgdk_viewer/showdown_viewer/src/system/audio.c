#include <genesis.h>

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
}

void AUDIO_init(void)
{
    PSG_reset();
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

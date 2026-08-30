#include <genesis.h>

#include "system/audio.h"

static u8 sCueFrames;

static void stop_psg(void)
{
    PSG_setEnvelope(0, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(1, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(2, PSG_ENVELOPE_MIN);
}

void AUDIO_stopAll(void)
{
    stop_psg();
}

void AUDIO_init(void)
{
    PSG_reset();
    stop_psg();
    sCueFrames = 0;
}

void AUDIO_playCue(AudioCue cue)
{
    u16 tone = 440u;
    u8 channel = 0u;

    switch (cue)
    {
        case AUDIO_CUE_JUMP: tone = 720u; break;
        case AUDIO_CUE_LAND: tone = 220u; channel = 2u; break;
        case AUDIO_CUE_STRIKE: tone = 180u; channel = 1u; break;
        case AUDIO_CUE_PAUSE: tone = 320u; break;
        default: tone = 440u; break;
    }
    PSG_setFrequency(channel, tone);
    PSG_setEnvelope(channel, 4u);
    sCueFrames = 5u;
}

void AUDIO_update(void)
{
    if (sCueFrames > 0u && --sCueFrames == 0u) {
        stop_psg();
    }
}

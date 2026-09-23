#ifndef SYSTEM_AUDIO_H
#define SYSTEM_AUDIO_H

#include <genesis.h>

typedef enum AudioCue {
    AUDIO_CUE_MENU = 0,
    AUDIO_CUE_JUMP,
    AUDIO_CUE_LAND,
    AUDIO_CUE_STRIKE,
    AUDIO_CUE_PAUSE
} AudioCue;

void AUDIO_init(void);
void AUDIO_update(void);
void AUDIO_stopAll(void);
void AUDIO_playCue(AudioCue cue);

#endif

#ifndef SYSTEM_AUDIO_H
#define SYSTEM_AUDIO_H

#include <genesis.h>

typedef enum AudioCue {
    AUDIO_CUE_MENU = 0,
    AUDIO_CUE_JUMP,
    AUDIO_CUE_LAND,
    AUDIO_CUE_STRIKE,
    AUDIO_CUE_PAUSE,
    AUDIO_CUE_BRAND_ENGINE_HIT,
    AUDIO_CUE_BRAND_AUTHOR_CLICK,
    AUDIO_CUE_BRAND_AUTHOR_BELL,
    AUDIO_CUE_BRAND_PROJECT_WHOOSH,
    AUDIO_CUE_BRAND_PROJECT_TAIL,
    AUDIO_CUE_BRAND_HAMMER_SLAM
} AudioCue;

void AUDIO_init(void);
void AUDIO_update(void);
void AUDIO_stopAll(void);
void AUDIO_playCue(AudioCue cue);
void AUDIO_startBrandBgm(void);

#endif

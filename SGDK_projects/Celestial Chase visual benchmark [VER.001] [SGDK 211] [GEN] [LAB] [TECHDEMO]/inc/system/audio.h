#ifndef SYSTEM_AUDIO_H
#define SYSTEM_AUDIO_H

#include <genesis.h>

typedef enum AudioCue {
    AUDIO_CUE_MENU = 0,
    AUDIO_CUE_JUMP,
    AUDIO_CUE_LAND,
    AUDIO_CUE_STRIKE,
    AUDIO_CUE_PAUSE,
    AUDIO_CUE_PULSE,
    AUDIO_CUE_PICKUP,
    AUDIO_CUE_VICTORY,
    AUDIO_CUE_FAILURE,
    AUDIO_CUE_PRESSURE
} AudioCue;

typedef enum AudioMusicState {
    AUDIO_MUSIC_MENU = 0,
    AUDIO_MUSIC_INTRO,
    AUDIO_MUSIC_PRESSURE,
    AUDIO_MUSIC_CLIMAX,
    AUDIO_MUSIC_VICTORY,
    AUDIO_MUSIC_FAILURE
} AudioMusicState;

void AUDIO_init(void);
void AUDIO_update(void);
void AUDIO_stopAll(void);
void AUDIO_playCue(AudioCue cue);
void AUDIO_setMusicState(AudioMusicState state);
AudioMusicState AUDIO_musicState(void);
void AUDIO_startChaseScore(void);
void AUDIO_stopChaseScore(void);
void AUDIO_pause(void);
void AUDIO_resume(void);
void AUDIO_setIntensity(u8 intensity);

#endif


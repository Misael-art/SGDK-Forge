#ifndef RACE_SCENE_H
#define RACE_SCENE_H

#include "scene_types.h"
#include <genesis.h>

extern const Scene race_scene;

typedef struct {
    u16 total_frames;
    u8  final_integrity;
    u8  lumen_collected;
    u16 max_pressure;
    u8  pulse_used;
    u8  stars_earned;
} RaceResult;

#endif

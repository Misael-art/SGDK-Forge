#include "data/track_data.h"

const TrackSegment sector_01_segments[4] = {
    { 0u, 24u, 320u, 128u, 0, 0, 0, SEG_FLAG_TUTORIAL_SAFE },
    { 24u, 28u, 384u, 192u, 1, 1, 1, SEG_FLAG_FIRST_COMBINATION },
    { 52u, 24u, 448u, 256u, -1, 2, 2, SEG_FLAG_PULSE_TEACH },
    { 76u, 20u, 512u, 320u, 0, 3, 3, SEG_FLAG_BEACON_REWARD }
};

const TrackEvent sector_01_events[18] = {
    { 4u,  LANE_CENTER,          EV_LUMEN_ORB,       0, 0u, 4u,  5,  EV_FLAG_FIRST_PICKUP },
    { 6u,  LANE_ALL,             EV_PURSUER_SHADOW,  0, 1u, 3u,  0,  EV_FLAG_FIRST_PURSUER | EV_FLAG_NON_DAMAGING },
    { 8u,  LANE_LEFT,            EV_LUMEN_ORB,       0, 0u, 4u,  5,  EV_FLAG_ENCOURAGE_LEFT },
    { 12u, LANE_RIGHT,           EV_LUMEN_ORB,       0, 0u, 4u,  5,  EV_FLAG_ENCOURAGE_RIGHT },
    { 16u, LANE_CENTER,          EV_LOW_STONE,       0, 3u, 2u,  1,  0u },
    { 22u, LANE_LEFT|LANE_RIGHT, EV_LUMEN_ORB,       1, 0u, 4u,  5,  EV_FLAG_CHOICE_REWARD },
    { 28u, LANE_LEFT,            EV_ASTRAL_MARK,     0, 3u, 2u,  1,  0u },
    { 32u, LANE_CENTER,          EV_LUMEN_ORB,       0, 0u, 4u,  5,  0u },
    { 36u, LANE_RIGHT,           EV_LOW_STONE,       0, 3u, 2u,  1,  0u },
    { 42u, LANE_CENTER,          EV_PRESSURE_GATE,   0, 2u, 4u,  8,  0u },
    { 48u, LANE_ALL,             EV_LUMEN_ORB,       2, 0u, 4u,  10, 0u },
    { 56u, LANE_LEFT|LANE_RIGHT, EV_ASTRAL_MARK,     1, 3u, 3u,  1,  0u },
    { 60u, LANE_CENTER,          EV_PULSE_TUTORIAL,  0, 4u, 5u,  0,  EV_FLAG_CLEARABLE_BY_PULSE },
    { 66u, LANE_RIGHT,           EV_LUMEN_ORB,       0, 0u, 4u,  5,  0u },
    { 70u, LANE_LEFT|LANE_CENTER, EV_LOW_STONE,      1, 3u, 2u,  1,  0u },
    { 78u, LANE_CENTER,          EV_BEACON_KEY,      0, 1u, 6u,  1,  EV_FLAG_SECTOR_GOAL },
    { 84u, LANE_ALL,             EV_PRESSURE_GATE,   1, 4u, 4u,  10, EV_FLAG_NON_DAMAGING },
    { 90u, LANE_CENTER,          EV_LUMEN_ORB,       2, 0u, 4u,  10, 0u }
};

const u16 sector_01_segment_count = 4;
const u16 sector_01_event_count = 18;

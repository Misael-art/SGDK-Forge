#ifndef RACE_TRACK_H
#define RACE_TRACK_H

#include <genesis.h>
#include "data/track_data.h"

void Track_init(void);
void Track_update(void);
u16 Track_getStep(void);
u16 Track_getFrame(void);
u16 Track_getSpeed(void);
s32 Track_getScrollX(void);
u16 Track_getPressureRate(void);
u8 Track_getActiveEventCount(void);
u8 Track_getActiveEventIndex(u8 slot);
const TrackEvent* Track_getActiveEvent(u8 slot);
const TrackSegment* Track_getCurrentSegment(void);
u8 Track_getVisualState(void);
s8 Track_getRoadCurve(void);
bool Track_isComplete(void);
bool Track_isEventTelegraphing(u8 event_index);
bool Track_isEventActive(u8 event_index);

#endif

#include "race/race_track.h"

static u16 global_frame = 0;
static u16 global_step = 0;
static u16 current_speed_q8_8 = 0;
static u16 current_pressure_rate = 0;
static s32 scroll_x_accum = 0;
static s32 scroll_x = 0;
static u8 active_event_count = 0;
static u8 active_event_slots[TRACK_MAX_ACTIVE];
static u8 next_event_index = 0;
static const TrackSegment* current_segment = NULL;
static u8 current_visual_state = 0;
static s8 current_road_curve = 0;

static u8 find_current_segment_index(void)
{
    for (u8 i = 0; i < sector_01_segment_count; i++)
    {
        const TrackSegment* seg = &sector_01_segments[i];
        if (global_step >= seg->start_step &&
            global_step < seg->start_step + seg->duration_steps)
        {
            return i;
        }
    }
    return 0;
}

void Track_init(void)
{
    global_frame = 0;
    global_step = 0;
    current_speed_q8_8 = sector_01_segments[0].speed_q8_8;
    current_pressure_rate = sector_01_segments[0].pressure_rate_q8_8_per_sec;
    scroll_x_accum = 0;
    scroll_x = 0;
    active_event_count = 0;
    next_event_index = 0;
    current_segment = &sector_01_segments[0];
    current_visual_state = 0;
    current_road_curve = 0;

    for (u8 i = 0; i < TRACK_MAX_ACTIVE; i++)
    {
        active_event_slots[i] = 0xFF;
    }
}

void Track_update(void)
{
    global_frame++;

    global_step = global_frame / TRACK_STEP_FRAMES_NTSC;
    if (global_step >= 96)
    {
        global_step = 96;
        return;
    }

    u8 seg_idx = find_current_segment_index();
    current_segment = &sector_01_segments[seg_idx];
    current_speed_q8_8 = current_segment->speed_q8_8;
    current_pressure_rate = current_segment->pressure_rate_q8_8_per_sec;
    current_visual_state = current_segment->visual_state;
    current_road_curve = current_segment->road_curve;

    scroll_x_accum += current_speed_q8_8;
    scroll_x = scroll_x_accum >> 8;

    while (next_event_index < sector_01_event_count)
    {
        const TrackEvent* ev = &sector_01_events[next_event_index];
        u16 event_start_step = ev->start_step;
        if (global_step >= event_start_step)
        {
            if (active_event_count < TRACK_MAX_ACTIVE)
            {
                active_event_slots[active_event_count] = next_event_index;
                active_event_count++;
            }
            next_event_index++;
        }
        else
        {
            break;
        }
    }

    for (s16 i = (s16)active_event_count - 1; i >= 0; i--)
    {
        u8 ei = active_event_slots[(u8)i];
        const TrackEvent* ev = &sector_01_events[ei];
        u16 end_step = ev->start_step + ev->telegraph_steps + ev->active_steps;
        if (global_step >= end_step)
        {
            for (u8 j = (u8)i; j < active_event_count - 1; j++)
            {
                active_event_slots[j] = active_event_slots[j + 1];
            }
            active_event_count--;
        }
    }
}

u16 Track_getStep(void)
{
    return global_step;
}

u16 Track_getFrame(void)
{
    return global_frame;
}

u16 Track_getSpeed(void)
{
    return current_speed_q8_8;
}

s32 Track_getScrollX(void)
{
    return scroll_x;
}

u16 Track_getPressureRate(void)
{
    return current_pressure_rate;
}

u8 Track_getActiveEventCount(void)
{
    return active_event_count;
}

u8 Track_getActiveEventIndex(u8 slot)
{
    if (slot < active_event_count)
    {
        return active_event_slots[slot];
    }
    return 0xFF;
}

const TrackEvent* Track_getActiveEvent(u8 slot)
{
    if (slot < active_event_count)
    {
        u8 ei = active_event_slots[slot];
        return &sector_01_events[ei];
    }
    return NULL;
}

const TrackSegment* Track_getCurrentSegment(void)
{
    return current_segment;
}

u8 Track_getVisualState(void)
{
    return current_visual_state;
}

s8 Track_getRoadCurve(void)
{
    return current_road_curve;
}

bool Track_isComplete(void)
{
    return global_step >= 96;
}

bool Track_isEventTelegraphing(u8 event_index)
{
    if (event_index >= sector_01_event_count)
    {
        return false;
    }
    const TrackEvent* ev = &sector_01_events[event_index];
    u16 telegraph_start = ev->start_step;
    u16 telegraph_end = ev->start_step + ev->telegraph_steps;
    if (ev->telegraph_steps == 0)
    {
        return false;
    }
    return (global_step >= telegraph_start) && (global_step < telegraph_end);
}

bool Track_isEventActive(u8 event_index)
{
    if (event_index >= sector_01_event_count)
    {
        return false;
    }
    const TrackEvent* ev = &sector_01_events[event_index];
    u16 active_start = ev->start_step + ev->telegraph_steps;
    u16 active_end = ev->start_step + ev->telegraph_steps + ev->active_steps;
    return (global_step >= active_start) && (global_step < active_end);
}

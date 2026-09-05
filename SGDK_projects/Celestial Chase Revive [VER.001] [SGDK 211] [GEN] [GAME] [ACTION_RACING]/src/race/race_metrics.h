#ifndef RACE_METRICS_H
#define RACE_METRICS_H

#include <genesis.h>

typedef struct {
    u32 total_frames;
    u16 avg_pressure;
    u8  integrity_end;
    u8  lumen_end;
    u16 max_pressure;
    u8  pulse_used;
    u8  stars_earned;
    bool sector_cleared;
} MetricsReport;

void Metrics_init(void);
void Metrics_frameBegin(void);
void Metrics_frameEnd(u16 current_pressure);
void Metrics_raceComplete(u8 final_integrity, u8 final_lumen, u16 max_pressure,
                          u8 pulse_used, bool cleared);
MetricsReport Metrics_getReport(void);

#endif

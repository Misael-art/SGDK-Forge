#include "race/race_metrics.h"
#include "data/track_data.h"
#include "project_config.h"

static u32 total_frames = 0;
static u32 pressure_sum = 0;
static u16 pressure_samples = 0;
static u16 max_pressure = 0;
static u8 integrity_end = 0;
static u8 lumen_end = 0;
static u8 pulse_used = 0;
static bool sector_cleared = false;

void Metrics_init(void)
{
    total_frames = 0;
    pressure_sum = 0;
    pressure_samples = 0;
    max_pressure = 0;
    integrity_end = 0;
    lumen_end = 0;
    pulse_used = 0;
    sector_cleared = false;
}

void Metrics_frameBegin(void)
{
}

void Metrics_frameEnd(u16 current_pressure)
{
    total_frames++;
    pressure_sum += current_pressure;
    pressure_samples++;

    if (current_pressure > max_pressure)
    {
        max_pressure = current_pressure;
    }
}

void Metrics_raceComplete(u8 final_integrity, u8 final_lumen, u16 final_max_pressure,
                          u8 pulse_used_count, bool cleared)
{
    integrity_end = final_integrity;
    lumen_end = final_lumen;
    max_pressure = final_max_pressure;
    pulse_used = pulse_used_count;
    sector_cleared = cleared;

    u16 avg_pressure = 0;
    if (pressure_samples > 0)
    {
        avg_pressure = (u16)(pressure_sum / pressure_samples);
    }

    SRAM_enable();
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 0, (u8)'M');
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 1, (u8)'T');
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 2, (u8)'R');
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 3, sector_cleared ? 1u : 0u);
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 4, (u8)((total_frames >> 24) & 0xFF));
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 5, (u8)((total_frames >> 16) & 0xFF));
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 6, (u8)((total_frames >> 8) & 0xFF));
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 7, (u8)(total_frames & 0xFF));
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 8, (u8)((avg_pressure >> 8) & 0xFF));
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 9, (u8)(avg_pressure & 0xFF));
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 10, integrity_end);
    SRAM_writeByte(PROJECT_RACE_SRAM_OFFSET + 11, lumen_end);
    SRAM_disable();
}

MetricsReport Metrics_getReport(void)
{
    MetricsReport report;
    report.total_frames = total_frames;
    report.avg_pressure = (pressure_samples > 0) ? (u16)(pressure_sum / pressure_samples) : 0;
    report.integrity_end = integrity_end;
    report.lumen_end = lumen_end;
    report.max_pressure = max_pressure;
    report.pulse_used = pulse_used;
    report.sector_cleared = sector_cleared;

    u8 stars = 0;
    if (sector_cleared && integrity_end >= 3)
    {
        stars = 3;
    }
    else if (sector_cleared && integrity_end >= 2)
    {
        stars = 2;
    }
    else if (sector_cleared)
    {
        stars = 1;
    }
    report.stars_earned = stars;

    return report;
}

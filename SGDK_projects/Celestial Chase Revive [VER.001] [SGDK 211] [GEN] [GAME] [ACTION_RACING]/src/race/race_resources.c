#include "race/race_resources.h"
#include "data/track_data.h"

static ResourceState res;
static u8 extra_pressure_per_sec = 0;

static const u8 band_extra[4] = { 0, 1, 2, 3 };

void Resources_init(void)
{
    res.integrity = PLAYER_MAX_INTEGRITY;
    res.lumen = 0;
    res.pressure = 0;
    res.pulse_cooldown = 0;
    res.pulse_active = 0;
    res.focus = 0;
    res.lumen_band = 0;
    res.pressure_accumulator = 0;
    extra_pressure_per_sec = 0;
}

void Resources_update(void)
{
    if (res.pulse_cooldown > 0)
    {
        res.pulse_cooldown--;
    }
    if (res.pulse_active > 0)
    {
        res.pulse_active--;
    }
}

void Resources_addLumen(u8 amount)
{
    u16 new_lumen = (u16)res.lumen + (u16)amount;
    if (new_lumen > PLAYER_MAX_LUMEN)
    {
        new_lumen = PLAYER_MAX_LUMEN;
    }
    res.lumen = (u8)new_lumen;
    res.lumen_band = Resources_getLumenBand();
}

void Resources_addPressure(u8 amount)
{
    u16 new_pressure = res.pressure + amount;
    res.pressure = (new_pressure > 100) ? 100 : new_pressure;
}

void Resources_applyDamage(void)
{
    if (res.integrity > 0)
    {
        res.integrity--;
    }
    Resources_addPressure(15);

    if (res.lumen >= 10)
    {
        res.lumen -= 10;
    }
    else
    {
        res.lumen = 0;
    }
    res.lumen_band = Resources_getLumenBand();
}

void Resources_updatePressure(u16 rate_per_sec)
{
    if (res.pressure >= 100)
    {
        return;
    }

    u16 total_rate = rate_per_sec;
    total_rate += (u16)(extra_pressure_per_sec * 256);
    total_rate += (u16)(band_extra[res.lumen_band] * 256);

    res.pressure_accumulator += total_rate;

    while (res.pressure_accumulator >= 15360)
    {
        res.pressure_accumulator -= 15360;
        if (res.pressure < 100)
        {
            res.pressure++;
        }
    }
}

bool Resources_usePulse(void)
{
    if (res.pulse_cooldown > 0)
    {
        return false;
    }
    if (res.lumen < PLAYER_PULSE_COST_LUMEN)
    {
        return false;
    }

    res.lumen -= PLAYER_PULSE_COST_LUMEN;
    res.lumen_band = Resources_getLumenBand();
    res.pulse_cooldown = PLAYER_PULSE_COOLDOWN_FRAMES;

    if (res.pressure >= PLAYER_PULSE_PRESSURE_REDUCTION)
    {
        res.pressure -= PLAYER_PULSE_PRESSURE_REDUCTION;
    }
    else
    {
        res.pressure = 0;
    }

    return true;
}

void Resources_setPulseActive(u8 frames)
{
    res.pulse_active = frames;
}

u8 Resources_getLumenBand(void)
{
    u8 band = 0;
    if (res.lumen >= 60)
    {
        band = 3;
    }
    else if (res.lumen >= 40)
    {
        band = 2;
    }
    else if (res.lumen >= 20)
    {
        band = 1;
    }
    return band;
}

bool Resources_isDead(void)
{
    return res.integrity == 0;
}

u8 Resources_getIntegrity(void)
{
    return res.integrity;
}

u8 Resources_getLumen(void)
{
    return res.lumen;
}

u16 Resources_getPressure(void)
{
    return res.pressure;
}

u8 Resources_getFocus(void)
{
    return res.focus;
}

bool Resources_isPulseReady(void)
{
    return (res.pulse_cooldown == 0) && (res.lumen >= PLAYER_PULSE_COST_LUMEN);
}

void Resources_setExtraPressurePerSecond(u8 extra)
{
    extra_pressure_per_sec = extra;
}

u8 Resources_getExtraPressurePerSecond(void)
{
    return extra_pressure_per_sec;
}

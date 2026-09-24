#include "race/race_hud.h"
#include "res/resources.h"

#define HUD_BG_TILE_ATTR TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, TILE_SYSTEM_INDEX + 1)

static bool visible = true;
static u8 last_integrity = 0xFF;
static u8 last_lumen = 0xFF;
static u16 last_pressure = 0xFFFF;
static u8 last_pulse_ready = 0xFF;

void Hud_init(void)
{
    VDP_setWindowOnTop(3);
    VDP_setTextPlane(WINDOW);
    VDP_setTextPriority(TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_fillTileMapRect(WINDOW, HUD_BG_TILE_ATTR, 0, 0, 40, 3);
    last_integrity = 0xFF;
    last_lumen = 0xFF;
    last_pressure = 0xFFFF;
    last_pulse_ready = 0xFF;
    visible = true;
}

static void draw_value_2_tile(u8 value, u16 col, u16 row)
{
    if (value > 99) value = 99;
    char text[4];
    uintToStr((u32)value, text, 2);
    VDP_fillTileMapRect(WINDOW, HUD_BG_TILE_ATTR, col, row, 2, 1);
    VDP_drawText(text, col, row);
}

static void draw_value_3_tile(u16 value, u16 col, u16 row)
{
    if (value > 999) value = 999;
    char text[5];
    uintToStr((u32)value, text, 3);
    VDP_fillTileMapRect(WINDOW, HUD_BG_TILE_ATTR, col, row, 3, 1);
    VDP_drawText(text, col, row);
}

void Hud_drawStatic(void)
{
    VDP_drawText("INT", 0, 0);
    VDP_drawText("LUM", 6, 0);
    VDP_drawText("PRS", 12, 0);
    VDP_drawText("PUL", 19, 0);
}

void Hud_update(const ResourceState* res, bool pulse_ready)
{
    if (!visible) return;

    if (res->integrity != last_integrity)
    {
        draw_value_2_tile(res->integrity, 3, 0);
        last_integrity = res->integrity;
    }

    if (res->lumen != last_lumen)
    {
        draw_value_2_tile(res->lumen, 9, 0);
        last_lumen = res->lumen;
    }

    if (res->pressure != last_pressure)
    {
        draw_value_3_tile((u16)res->pressure, 15, 0);
        last_pressure = res->pressure;
    }

    u8 pulse_state = pulse_ready ? 1 : 0;
    if (pulse_state != last_pulse_ready)
    {
        VDP_fillTileMapRect(WINDOW, HUD_BG_TILE_ATTR, 22, 0, 4, 1);
        if (pulse_ready)
        {
            VDP_drawText("RDY", 22, 0);
        }
        else
        {
            VDP_drawText("COLD", 22, 0);
        }
        last_pulse_ready = pulse_state;
    }
}

void Hud_setVisible(bool vis)
{
    visible = vis;
}

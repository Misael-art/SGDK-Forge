#include <genesis.h>
#include "result_scene.h"
#include "scene_manager.h"
#include "input_abstraction.h"
#include "race/race_metrics.h"

static u16 grace_timer = 0;
static MetricsReport result_data;

static const u16 result_palette[64] = {
    RGB24_TO_VDPCOLOR(0x000018),
    RGB24_TO_VDPCOLOR(0x102850),
    RGB24_TO_VDPCOLOR(0x50C8FF),
    RGB24_TO_VDPCOLOR(0xF0F8FF),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, RGB24_TO_VDPCOLOR(0xF0F8FF),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void result_enter(void)
{
    result_data = Metrics_getReport();

    grace_timer = 60;
    VDP_setTextPlane(BG_A);

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(WINDOW, TRUE);

    if (result_data.sector_cleared)
    {
        VDP_drawText("SECTOR 01 COMPLETE", 10, 4);
    }
    else
    {
        VDP_drawText("SECTOR 01 FAILED", 11, 4);
    }
    VDP_drawText("------------------", 10, 5);

    VDP_drawText("INTEGRITY REMAINING:", 4, 8);
    {
        char buf[4];
        uintToStr((u32)result_data.integrity_end, buf, 1);
        VDP_drawText(buf, 30, 8);
        VDP_drawText("/3", 32, 8);
    }

    VDP_drawText("LUMEN COLLECTED:", 4, 10);
    {
        char buf[4];
        uintToStr((u32)result_data.lumen_end, buf, 3);
        VDP_drawText(buf, 24, 10);
    }

    VDP_drawText("MAX PRESSURE:", 4, 12);
    {
        char buf[4];
        uintToStr((u32)result_data.max_pressure, buf, 3);
        VDP_drawText(buf, 22, 12);
    }

    VDP_drawText("RATING:", 4, 14);
    {
        char stars[4];
        u8 i;
        for (i = 0; i < result_data.stars_earned; i++)
        {
            stars[i] = '*';
        }
        stars[i] = 0;
        VDP_drawText(stars, 14, 14);
    }

    VDP_drawText("PRESS START TO CONTINUE", 6, 20);
}

void result_update(void)
{
    if (grace_timer > 0)
    {
        grace_timer--;
        return;
    }

    if (IO_getState(INPUT_ACTION_START).pressed)
    {
        SM_requestTransition(APP_SCENE_TITLE);
    }
}

void result_exit(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
}

const Scene result_scene = {
    .enter = result_enter,
    .update = result_update,
    .exit = result_exit,
    .palette = result_palette,
    .enterFade = true,
    .exitFade = true
};

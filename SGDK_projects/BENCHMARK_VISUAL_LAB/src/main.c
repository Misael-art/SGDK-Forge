/**
 * main.c — BENCHMARK_VISUAL_LAB entry point.
 * Delegates to the scene framework (app.c).
 */
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/runtime_probe.h"

int main(bool hardReset)
{
    APP_boot(hardReset);
    MDRuntimeProbe_init();

    while (TRUE)
    {
        INPUT_update();
        APP_update();
        MDRuntimeProbe_tick();
        SYS_doVBlankProcess();
    }

    return 0;
}

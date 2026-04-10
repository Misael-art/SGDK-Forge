/**
 * main.c — BENCHMARK_VISUAL_LAB entry point.
 * Delegates to the scene framework (app.c).
 */
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

int main(bool hardReset)
{
    APP_boot(hardReset);

    while (TRUE)
    {
        INPUT_update();
        APP_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

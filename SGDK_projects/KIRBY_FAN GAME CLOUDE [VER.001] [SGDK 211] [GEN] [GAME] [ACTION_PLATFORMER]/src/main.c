#include <genesis.h>

#include "core/app.h"
#include "system/input.h"
#include "system/runtime_probe.h"

int main(bool hardReset)
{
    APP_boot(hardReset);

    while (TRUE)
    {
        PROBE_beginSection(PROBE_SECTION_INPUT);
        INPUT_update();
        PROBE_endSection(PROBE_SECTION_INPUT);

        APP_update();

        PROBE_beginSection(PROBE_SECTION_SPRITE);
        SPR_update();
        PROBE_endSection(PROBE_SECTION_SPRITE);

        /*
         * PROBE_SECTION_VBLANK spans the whole wait-for-vblank, so its raster
         * cost is IDLE HEADROOM, not work. A large value here is good.
         */
        PROBE_beginSection(PROBE_SECTION_VBLANK);
        SYS_doVBlankProcess();
        PROBE_endSection(PROBE_SECTION_VBLANK);

        PROBE_tick();
    }

    return 0;
}

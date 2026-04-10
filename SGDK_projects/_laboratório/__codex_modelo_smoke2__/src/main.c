#include <genesis.h>

#include "core/app.h"
#include "system/input.h"
#include "system/runtime_probe_bridge.h"

int main(bool hardReset)
{
    APP_boot(hardReset);

    while (TRUE)
    {
        MD_RT_FrameBegin();
        INPUT_update();
        APP_update();
        SPR_update();
        MD_RT_FrameEnd();
        SYS_doVBlankProcess();
    }

    return 0;
}

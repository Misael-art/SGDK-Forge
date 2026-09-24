#include <genesis.h>

#include "core/app.h"
#include "system/input.h"
#include "system/runtime_probe.h"

int main(bool hardReset)
{
    APP_boot(hardReset);

    while (TRUE)
    {
        INPUT_update();
        APP_update();
        SPR_update();
        MDRuntimeProbe_noteDmaQueue(
            DMA_getQueueTransferSize(),
            DMA_getQueueSize(),
            DMA_getMaxTransferSize());
        SYS_doVBlankProcess();
        MDRuntimeProbe_tick();
    }

    return 0;
}

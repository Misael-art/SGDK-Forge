#include <genesis.h>

#include "core/app.h"
#include "system/input.h"

int main(bool hardReset)
{
    APP_boot(hardReset);

    while (TRUE)
    {
        INPUT_update();
        APP_update();
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

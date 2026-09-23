#include <genesis.h>
#include "resources.h"

static u8 palID;

static void nextPalette(void)
{
    palID = (palID + 1) & 1;

    if (palID == 0)
        PAL_setPalette(PAL2, fighter_pal1.data, DMA);
    else
        PAL_setPalette(PAL2, fighter_pal2.data, DMA);
}

int main(void)
{
    while (TRUE)
    {
        if (JOY_readJoypad(JOY_1) & BUTTON_C)
            nextPalette();

        SYS_doVBlankProcess();
    }

    return 0;
}

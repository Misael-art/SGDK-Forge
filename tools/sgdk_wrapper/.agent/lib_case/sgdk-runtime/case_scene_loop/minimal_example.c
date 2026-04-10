#include <genesis.h>

static void APP_update(void)
{
    /* scene update */
}

int main(void)
{
    while (TRUE)
    {
        INPUT_update();
        APP_update();
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

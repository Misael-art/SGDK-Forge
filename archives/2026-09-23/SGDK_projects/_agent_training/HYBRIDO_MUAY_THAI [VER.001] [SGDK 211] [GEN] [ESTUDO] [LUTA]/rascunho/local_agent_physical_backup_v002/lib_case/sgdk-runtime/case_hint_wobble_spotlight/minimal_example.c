#include <genesis.h>

static fix16 lineBuffer[224];
static vu16 lineDisplay;
static vs16 lineGraphics;

static void vblank_cb(void)
{
    lineDisplay = 0;
    lineGraphics = 0;
    VDP_setVerticalScroll(BG_B, 0);
}

static void hint_cb(void)
{
    VDP_setVerticalScroll(BG_B, fix16ToInt(lineGraphics) - lineDisplay);
    lineGraphics += lineBuffer[lineDisplay++];
}

int main(void)
{
    SYS_setVBlankCallback(vblank_cb);
    SYS_setHIntCallback(hint_cb);
    VDP_setHIntCounter(0);
    VDP_setHInterrupt(TRUE);

    while (TRUE)
        SYS_doVBlankProcess();

    return 0;
}

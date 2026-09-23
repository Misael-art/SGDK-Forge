#include <genesis.h>

#include "system/overlay.h"

void SCENE_overlayWindowBegin(void)
{
    VDP_setWindowHPos(TRUE, 0);
    VDP_setWindowVPos(FALSE, 3);
    VDP_setTextPlane(WINDOW);
}

void SCENE_overlayWindowEnd(void)
{
    VDP_setTextPlane(BG_A);
}

void SCENE_overlayWindowTeardown(void)
{
    VDP_setWindowHPos(0, 0);
    VDP_setWindowVPos(0, 0);
    VDP_setTextPlane(BG_A);
}

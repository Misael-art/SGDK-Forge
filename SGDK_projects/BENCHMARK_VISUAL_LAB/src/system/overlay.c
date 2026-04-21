#include <genesis.h>

#include "system/overlay.h"

/*
 * Window covers columns 0..39 (all) across rows 0..2. BG_A remains unchanged.
 *   VDP_setWindowHPos(TRUE, 0)   -> columns [0..39]
 *   VDP_setWindowVPos(FALSE, 3)  -> rows    [0..2]
 */
void SCENE_overlayWindowBegin(void)
{
    VDP_setWindowHPos(TRUE, 0);
    VDP_setWindowVPos(FALSE, 3);
    VDP_setTextPlane(WINDOW);
}

void SCENE_overlayWindowEnd(void)
{
    /*
     * Restore BG_A as the default text plane so APP_drawDebugHud writes its
     * canonical single-row HUD at row 26 on BG_A (not on the window, which
     * only spans rows 0..2).
     */
    VDP_setTextPlane(BG_A);
}

void SCENE_overlayWindowTeardown(void)
{
    /*
     * Disable the window plane entirely: with right=0/pos=0 the window has
     * empty horizontal range and is not displayed. Also reset the text plane
     * to BG_A so the next scene starts in a deterministic state.
     */
    VDP_setWindowHPos(0, 0);
    VDP_setWindowVPos(0, 0);
    VDP_setTextPlane(BG_A);
}

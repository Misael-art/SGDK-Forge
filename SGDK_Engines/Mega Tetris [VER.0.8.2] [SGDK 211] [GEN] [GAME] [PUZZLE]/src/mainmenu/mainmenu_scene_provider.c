#include <genesis.h>
#include <resources.h>

void loadAndShowMainMenuGraphicsWithFadeIn();

void loadAndShowMainMenuGraphicsWithFadeIn() {
    PAL_setColors(PAL0, (u16*)palette_black, 64, DMA);

    VDP_drawImageEx(
        BG_B, 
        &mainmenu_scene_background, 
        TILE_ATTR_FULL(PAL0, 0, FALSE, FALSE, 1), 0, 0, FALSE, DMA);

    PAL_fadeInAll(mainmenu_scene_background.palette->data, 40, FALSE);
    PAL_waitFadeCompletion();

    PAL_setPalette(PAL0, 
        mainmenu_scene_background.palette->data, DMA);
    
    VDP_drawTextBG(BG_A, "v0.8.2", 30, 26);
    VDP_drawTextBG(BG_A, "@kikutano", 30, 27);
}
#include <genesis.h>
#include "resources.h"

int main(void)
{
    PAL_setPalette(PAL0, customFont_PAL.data, DMA);
    VDP_loadFont(custom_font.tileset, DMA);
    VDP_drawText("SCORE 0000", 2, 2);

    while (TRUE)
        SYS_doVBlankProcess();

    return 0;
}

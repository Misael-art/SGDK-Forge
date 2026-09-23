#include <genesis.h>
#include "resources.h"

static Sprite *player;
static u16 frameIndex;

int main(void)
{
    SPR_init();
    player = SPR_addSprite(&player_sprite, 120, 120, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));

    while (TRUE)
    {
        if (JOY_readJoypad(JOY_1) & BUTTON_A)
            SPR_setAnimAndFrame(player, 1, frameIndex++ & 3);

        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

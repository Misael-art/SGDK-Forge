#include "fighters.h"
#include "sprites.h"
#include "estruturas.h"
#include "game_vars.h"

void playerState_Johnny(int numPlayer, u16 State)
{
    switch (State)
    {
    case PARADO:
        player[numPlayer].y = gAlturaDoPiso;
        player[numPlayer].w = 16 * 8;
        player[numPlayer].h = 15 * 8;
        player[numPlayer].dataAnim[1] = 5;
        player[numPlayer].dataAnim[2] = 5;
        player[numPlayer].dataAnim[3] = 5;
        player[numPlayer].dataAnim[4] = 5;
        player[numPlayer].dataAnim[5] = 5;
        player[numPlayer].dataAnim[6] = 5;
        player[numPlayer].dataAnim[7] = 5;
        player[numPlayer].animFrameTotal = 7;
        player[numPlayer].sprite = SPR_addSpriteExSafe(&spr_jcage, player[numPlayer].x - player[numPlayer].axisX,
                                                       player[numPlayer].y - player[numPlayer].axisY,
                                                       TILE_ATTR(player[numPlayer].paleta, FALSE, FALSE, FALSE),
                                                       SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE | SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
        break;

    default:
        break;
    }

    if(player[numPlayer].direcao == 1)
    {
        PAL_setPalette(PAL2, spr_jcage.palette->data, DMA);
    } else {
        PAL_setPalette(PAL3, spr_jcage.palette->data, DMA);
    }
}
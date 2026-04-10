#include <genesis.h>
#include "palace_gates_room.h"
#include "stages.h"
#include "game_vars.h"

#define PALACE_GATES_W 928
#define PALACE_GATES_H 232

void initPalaceGatesRoom(void)
{
    // carrego as informações do cenário.
    if (gFrames == 1)
    {
        // defino o tamanho do meu cenário para rolagem
        gBG_Width = PALACE_GATES_W;
        gBG_Height = PALACE_GATES_H;

        // 304
        gScrollValue = (gBG_Width - VDP_getScreenWidth()) / 2;

        // s16 startX = (VDP_getScreenWidth() - gBG_Width) / 2;
        s16 startY = -(gBG_Height - VDP_getScreenHeight());

        // BGA
        VDP_loadTileSet(pg_bga.tileset, gInd_tileset, DMA);
        // VDP_setTileMapEx(BG_A, pg_bga.tilemap, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, gInd_tileset), startX / 8, startY / 8, 0, 0, gBG_Width / 8, 29, DMA);
        VDP_setTileMapEx(BG_A, pg_bga.tilemap, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, gInd_tileset),
                         0, 0, 0, 0, gBG_Width / 8, 29, DMA_QUEUE);
        PAL_setPalette(PAL0, pg_bga.palette->data, DMA);
        gInd_tileset += pg_bga.tileset->numTile;
        // BGB
        VDP_loadTileSet(pg_bgb.tileset, gInd_tileset, DMA);
        VDP_setTileMapEx(BG_B, pg_bgb.tilemap, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, gInd_tileset),
                         0, startY / 8, 0, 0, 64, 29, DMA);
        PAL_setPalette(PAL1, pg_bgb.palette->data, DMA);
        gInd_tileset += pg_bgb.tileset->numTile;
    }
}

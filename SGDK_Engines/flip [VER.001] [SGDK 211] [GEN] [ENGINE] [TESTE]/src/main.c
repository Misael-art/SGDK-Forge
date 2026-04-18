// SGDK
#include <genesis.h>

// Resources
#include "bg.h"

/**
 * @brief espelha o tilemap na vertical
 * 
 * @param map tilemap a ser espelhado
 * @param altura alutra do tile map em tiles
 * @param largura largura do tilemap em tiles
 * @param index index do tileset
 * @param pos_x cordenada x em tiles onde a imagem sera desenhada
 * @param pos_y cordenada Y em tiles onde a imagem sera desenhada
 * @param plane plano onde a imagem sera desenhada
 */
void flipVTilemap(TileMap *map, u16 altura, u16 largura, u16 index, u16 pos_x, u16 pos_y, VDPPlane plane)
{
	for(u16 i = 0; i < altura; i++)
	{
		VDP_setTileMapEx(plane,map,TILE_ATTR_FULL(PAL0,FALSE,TRUE,FALSE,index), pos_x, pos_y+i, 0, altura-i-1, largura, 1, DMA_QUEUE);
	}
}

/**
 * @brief espelha o tilemap na horizontal
 * 
 * @param map tilemap a ser espelhado
 * @param altura alutra do tile map em tiles
 * @param largura largura do tilemap em tiles
 * @param index index do tileset
 * @param pos_x cordenada x em tiles onde a imagem sera desenhada
 * @param pos_y cordenada Y em tiles onde a imagem sera desenhada
 * @param plane plano onde a imagem sera desenhada
 */
void flipHTilemap(TileMap *map, u16 altura, u16 largura, u16 index, u16 pos_x, u16 pos_y, VDPPlane plane)
{
	for(u16 i = 0; i < largura; i++)
	{
		VDP_setTileMapEx(plane,map,TILE_ATTR_FULL(PAL0,FALSE,FALSE,TRUE,index), pos_x + i, pos_y, largura-i- 1, 0, 1, altura, DMA_QUEUE);
	}
}

/**
 * @brief espelha o tilemap na vertical e na horizontal
 * 
 * @param map tilemap a ser espelhado
 * @param altura alutra do tile map em tiles
 * @param largura largura do tilemap em tiles
 * @param index index do tileset
 * @param pos_x cordenada x em tiles onde a imagem sera desenhada
 * @param pos_y cordenada Y em tiles onde a imagem sera desenhada
 * @param plane plano onde a imagem sera desenhada
 */
void flipVHTilemap(TileMap *map, u16 altura, u16 largura, u16 index, u16 pos_x, u16 pos_y, VDPPlane plane)
{
	for(u16 i = 0; i < largura; i++)
	{
        for(u16 j = 0; j < altura; j++)
        {
		    VDP_setTileMapEx(plane,map,TILE_ATTR_FULL(PAL0,FALSE,TRUE,TRUE,index), pos_x + i, pos_y + j, largura-i-1, altura-j-1, 1, 1, CPU);
        }
	}
}

int main()
{
    int frame = 0;
    VDP_init();
    VDP_loadTileSet(sonic_cover.tileset,1, DMA);
    PAL_setPalette(PAL0, sonic_cover.palette->data, DMA);
    //desenha a imagem sem espelhamentos
    VDP_setTileMapEx(BG_B,sonic_cover.tilemap, TILE_ATTR_FULL(PAL0,FALSE,FALSE,FALSE,1), 7, 1, 0, 0 , 13, 13, DMA_QUEUE);

    while (TRUE)
    {
        frame++;

        if(frame == 10)
        {
            //espelhamento horizontal
            flipHTilemap(sonic_cover.tilemap, 13, 13, 1, 20, 1, BG_B);
        }
        else if(frame == 20)
        {
            //espelhamento vertical
            flipVTilemap(sonic_cover.tilemap, 13, 13, 1, 7, 14, BG_B);
        }
        else if(frame == 30)
        {
            //espelhamento em ambos
            flipVHTilemap(sonic_cover.tilemap, 13, 13, 1, 20, 14, BG_B);
        }
        SYS_doVBlankProcess();
    }
}

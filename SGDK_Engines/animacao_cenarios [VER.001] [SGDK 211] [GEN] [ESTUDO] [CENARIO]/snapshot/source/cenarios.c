#include "include/cenarios.h"
#include "gfx.h"
#include "maths.h"
#include "cenarios_res.h"

static TileMap* Cenario_tilemap;
static int img_num = 0;

void CEN_Anima(enum CENARIOS gBG_Choice, u8 ping)
{
	if(gBG_Choice==CENARIO_7_1)
	{
		if(ping == 9)
		{
			CEN_AnimaEx(0, 14, 64, 8, 4);
		}
	}
	
	if(gBG_Choice==CENARIO_LONDON)
	{
		if(ping == 9)
		{
			CEN_AnimaEx(22, 3, 43, 14, 4);
		}
	}

	if(gBG_Choice==CENARIO_KOREA)
	{
		if(ping == 9)
		{
			CEN_AnimaEx(12, 9, 40, 7, 4);
		}
	}

	if(gBG_Choice==CENARIO_GEESE)
	{
		if(ping == 9)
		{
			CEN_AnimaEx(14, 8, 57, 10, 4);
		}
	}
	if(gBG_Choice==CENARIO_KRAUZER)
	{
		if(ping == 9)
		{
			CEN_AnimaEx(15, 13, 49, 5, 4);
		}
	}
	if(gBG_Choice==CENARIO_MAI)
	{
		if(ping == 9)
		{
			CEN_AnimaEx(26, 19, 45, 3, 4);
		}
	}
	if(gBG_Choice==CENARIO_JOE)
	{
		if(ping == 9)
		{
			CEN_AnimaEx(0, 8, 59, 14, 4);
		}
	}
}

void CEN_AnimaEx(u16 x, u16 y, u16 x_len, u16 y_len, u8 frames_num)
{
	DEBUG_PRINT("funcao anima mapa");

    VDP_setTileMapEx(BG_B,Cenario_tilemap,TILE_ATTR_FULL(PAL0,0,FALSE,FALSE,0),x,y,x,(32*img_num+y),x_len,y_len,DMA_QUEUE);
    img_num++;
    if(img_num == frames_num)
    {
        img_num = 0;
    }
}

u16 CEN_init(enum CENARIOS gBG_Choice)
{
    const u16 gBG_Width = 512;
    
    u16 tileset_size = 0;
    if(Cenario_tilemap != NULL) //se cenario_tilemap já estiver alocado desaloca para novo carregamento
	{
		MEM_free(Cenario_tilemap);
		Cenario_tilemap = NULL;
		DEBUG_PRINT("cenario_tilemap desalocado");
		MEM_pack();
	}

    if(gBG_Choice==CENARIO_7_1){ 
		Cenario_tilemap =  unpackTileMap(gfx_bgb1.tilemap, NULL);
		VDP_loadTileSet(gfx_bgb1.tileset,0,DMA);
		PAL_setPalette(PAL0, gfx_bgb1.palette->data, DMA);
        tileset_size = gfx_bgb1.tileset->numTile;
	}

    //Load the tileset 'BGB2'
	if(gBG_Choice==CENARIO_LONDON){ 
		Cenario_tilemap =  unpackTileMap(gfx_bgb2.tilemap, NULL);
		VDP_loadTileSet(gfx_bgb2.tileset,0,DMA);
		PAL_setPalette(PAL0, gfx_bgb2.palette->data, DMA);
		tileset_size= gfx_bgb2.tileset->numTile;
	} 
	
	//Load the tileset 'BGB3'
	if(gBG_Choice==CENARIO_KOREA){ 
		Cenario_tilemap =  unpackTileMap(gfx_bgb3.tilemap, NULL);
		VDP_loadTileSet(gfx_bgb3.tileset,0,DMA); 
		PAL_setPalette(PAL0, gfx_bgb3.palette->data, DMA);
		tileset_size = gfx_bgb3.tileset->numTile;
	}
	//Load the tileset 'BGB4'
	if(gBG_Choice==CENARIO_GEESE){ 
		Cenario_tilemap =  unpackTileMap(gfx_bgb4.tilemap, NULL);
		VDP_loadTileSet(gfx_bgb4.tileset,0,DMA); 
		PAL_setPalette(PAL0, gfx_bgb4.palette->data, DMA);
		tileset_size = gfx_bgb4.tileset->numTile;
	}
	//Load the tileset 'BGB5'
	if(gBG_Choice==CENARIO_KRAUZER){ 
		Cenario_tilemap =  unpackTileMap(gfx_bgb5.tilemap, NULL);
		VDP_loadTileSet(gfx_bgb5.tileset,0,DMA); 
		PAL_setPalette(PAL0, gfx_bgb5.palette->data, DMA);
		tileset_size = gfx_bgb5.tileset->numTile;
	}
	if(gBG_Choice==CENARIO_MAI){ 
		Cenario_tilemap =  unpackTileMap(gfx_bgb6.tilemap, NULL);
		VDP_loadTileSet(gfx_bgb6.tileset,0,DMA); 
		PAL_setPalette(PAL0, gfx_bgb6.palette->data, DMA);
		tileset_size = gfx_bgb6.tileset->numTile;
	}
	if(gBG_Choice==CENARIO_JOE){ 
		Cenario_tilemap =  unpackTileMap(gfx_bgb7.tilemap, NULL);
		VDP_loadTileSet(gfx_bgb7.tileset,0,DMA); 
		PAL_setPalette(PAL0, gfx_bgb7.palette->data, DMA);
		tileset_size = gfx_bgb7.tileset->numTile;
	}

    if(Cenario_tilemap != NULL)
    {
        VDP_setTileMapEx(BG_B,Cenario_tilemap,TILE_ATTR_FULL(PAL0,0,FALSE,FALSE,0),0,0,0,0,64,32,DMA_QUEUE);
		VDP_setVerticalScrollVSync(BG_B, 32);
    }
    else
    {
        DEBUG_PRINT("Erro ao carregar o tilemap do BGB2");
    }
	 KLog_S2("bgb escolhido: ", gBG_Choice, " total de tiles: ", tileset_size);

    return tileset_size;
}
#include <genesis.h>
#include "gfx.h"

Map *map_a; //variavel ponteiro para o mapa_a ou seja o mapa 01
s32 camPosY; //coordenadas do mapa na tela
fix16 offsetY = FIX16(0);//Utilizado no scroll das Nuvens
float scroll = 488;// inicia o scroll do mapa na posição y= 488, o range do mapa vai de 488 pixels ate -488 pixels pq o scroll está diminuindo pra fazer o mapa descer
int ind = TILE_USER_INDEX;
static void scroll_mapa()
{

	while (scroll>= -488)
	{

    MAP_scrollTo( map_a, 0, camPosY ); camPosY= scroll; //faz o scroll na coordenada y para o ponto especificado na variavel scroll


    scroll--;
    if (scroll == 0 ){scroll=488;}//reinicia o looping quando a variavel y chega no pixel 0

    offsetY = offsetY -35;
    VDP_setVerticalScroll(BG_A, F16_toInt( offsetY ));
    SYS_doVBlankProcess();
    }


}

int main(u16 hard)
{


    //inicializacao da VDP (Video Display Processor)
	SYS_disableInts();

    VDP_init();
    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 64, TRUE);

    PAL_setPalette( PAL0, plane_pal.data, DMA);
    VDP_loadTileSet( &plane_a_tileset, ind, DMA);
	map_a = MAP_create( &plane_a_map, BG_B, TILE_ATTR_FULL( PAL0, FALSE, FALSE, FALSE, ind ) ); //cria o mapa 01 utilizando a mapa01.png
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

    VDP_loadTileSet(bga_nuvens.tileset,1056,DMA); //0x0000 = 0 dec
    VDP_setTileMapEx(BG_A,bga_nuvens.tilemap,TILE_ATTR_FULL(PAL1,0,FALSE,FALSE,1056),0,0,0,0,40,32,DMA_QUEUE);
    PAL_setPalette(PAL1, bga_nuvens.palette->data, DMA_QUEUE);

	SYS_enableInts();



    while(TRUE)
    {
   scroll_mapa();
    }
    return 0; MAP_release(map_a);//se necessário essa variavel vai limberar o mapa da memória VDP, muito util quando se utiliza varios mapas.
}

#include <genesis.h>
#include "imagens.h"

s16 vector_bola[19] = { 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21}; // taxa um tile por vez

s16 vector_triang[19] = { 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21};


int main(){

VDP_setScreenWidth320();
VDP_setScreenHeight224();

int ind_tileset = 1;

VDP_drawImageEx(BG_B, &gfx_bola, TILE_ATTR_FULL(PAL0,FALSE,FALSE,FALSE,ind_tileset),0,6,FALSE,TRUE);
ind_tileset += gfx_bola.tileset->numTile;
PAL_setPalette(PAL0,gfx_bola.palette->data, DMA);

VDP_drawImageEx(BG_A, &gfx_triangulo, TILE_ATTR_FULL(PAL1,FALSE,FALSE,FALSE,ind_tileset),36,10,FALSE,TRUE);
ind_tileset += gfx_triangulo.tileset->numTile;
PAL_setPalette(PAL1,gfx_triangulo.palette->data, DMA);

VDP_setScrollingMode( HSCROLL_TILE , VSCROLL_COLUMN);


while(1){


VDP_setHorizontalScrollTile(BG_B, 3, vector_bola, 19, DMA);

for(int i=0;i<19;i++) vector_bola[i]+=1;


if(vector_bola[0] == 90) break;


VDP_setHorizontalScrollTile(BG_A, 3, vector_triang, 19, DMA);

for(int i=0;i<19;i++) vector_triang[i]-=2;




SYS_doVBlankProcess();

}

return(0);

}

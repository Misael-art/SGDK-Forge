#include <genesis.h>
#include "gfx.h"

s16 offsetA = 0;

s16 vectorA[80];
s16 vectorB[80];


int main(){

VDP_drawImage(BG_A, &bga_nuv, 0, 0);

VDP_setScrollingMode( HSCROLL_LINE, VSCROLL_PLANE);


while(1){

 VDP_setHorizontalScrollLine(BG_A, 0, vectorA, 80, CPU);
 for(int i = 0; i < 80; i++) vectorA[i] = offsetA;
 offsetA--;

 VDP_setHorizontalScrollLine(BG_A, 144, vectorB, 80, CPU);
 for(int i = 0; i < 80; i++) vectorB[i] = offsetA;
 offsetA--;



SYS_doVBlankProcess();

}

return(0);

}

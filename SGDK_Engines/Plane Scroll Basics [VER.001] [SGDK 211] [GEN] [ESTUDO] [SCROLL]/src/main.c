#include <genesis.h>
#include "arquivos.h"



int main(){

fix16 offsetY = FIX16(0);

VDP_drawImage(BG_A, &gfx_cachoeira, 0, 0);

VDP_setScrollingMode(HSCROLL_PLANE,VSCROLL_PLANE);


while(1){

        offsetY = ((offsetY) + (FIX16(-1)));
        VDP_setVerticalScroll(BG_A, F16_toInt( offsetY ));



  SYS_doVBlankProcess();

}


return(0);

}

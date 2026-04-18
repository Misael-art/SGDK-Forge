 #include <genesis.h>

void initFont() {
    VDP_loadFont(&font_tileset, DMA); // Carrega a fonte
}


int main(bool hardReset) //--- MAIN ---//
{

    //inicializacao da VDP (Video Display Processor)
    SYS_disableInts();
     VDP_init();
     initFont();// <---Carrega a fonte alternativa
     SYS_enableInts();
}

// VDP_setTextPalette(Paleta desejada);
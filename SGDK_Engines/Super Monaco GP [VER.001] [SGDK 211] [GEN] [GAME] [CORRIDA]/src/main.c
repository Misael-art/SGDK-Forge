#include "genesis.h"

// Este e o menor exemplo possivel de um programa SGDK.
// Ele escreve um texto e mantem o console sincronizado a cada quadro.
int main(bool hardReset){
    VDP_drawText("Hello SGDK!", 12, 12);
    while(TRUE) {
        // O VBlank e o momento seguro para o SGDK aplicar atualizacoes de video.
        SYS_doVBlankProcess();
    }
    return 0;
}

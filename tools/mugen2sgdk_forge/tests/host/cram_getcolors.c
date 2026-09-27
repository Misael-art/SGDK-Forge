/* O stub de host precisa ler CRAM de verdade: sem isso, nenhum teste consegue provar
 * que um "borrow" de paleta devolve a linha exatamente como encontrou. */
#include "mg/mg_runtime.h"
u32 host_sound_plays, host_def_switches;
int main(void)
{
    u16 src[16] = { 0x111,0x222,0x333,0x444,0x555,0x666,0x777,0x888,
                    0x999,0xAAA,0xBBB,0xCCC,0xDDD,0xEEE,0xFFF,0x000 };
    PAL_setColors(16, src, 16, DMA);                 /* PAL1 inteira */
    host_vblank();
    u16 back[16] = { 0 };
    PAL_getColors(16, back, 16);
    int ok = !memcmp(src, back, sizeof src);
    /* clamp: pedir alem do fim de CRAM nao pode ler fora nem escrever no buffer do chamador */
    u16 tail[4] = { 0xBAD,0xBAD,0xBAD,0xBAD };
    PAL_getColors(62, tail, 4);
    int clamped = tail[0] == host_cram[62] && tail[1] == host_cram[63] &&
                  tail[2] == 0xBAD && tail[3] == 0xBAD;
    printf("{\"getcolors_roundtrip\": %d, \"clamped\": %d}\n", ok, clamped);
    return !(ok && clamped);
}

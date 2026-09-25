/* O emprestimo de PAL0 do super era devolvido so quando o explod morria. Um round que
 * termina sob o super deixava a linha do cenario/HUD com as cores do fundo do super.
 * Aqui o emprestimo e forcado e devolvido na transicao de round, sem explod morrer. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;

int main(void)
{
    MG_fightInit(&mg_char_ken, 0, &mg_char_ken, 0, 0);
    host_vblank();
    /* linha do cenario/HUD com cores DISTINTAS: sem isso todo roundtrip compara zeros e
     * um restore desalinhado passa (sonda de mutacao: pal0_saved[1] -> [2] sobrevivia) */
    for (int k = 0; k < 16; k++) host_cram[k] = (u16)(0x100 + k);
    u16 before[16]; PAL_getColors(0, before, 16);       /* stub fiel (Task 2) le PAL0 real */
    int bad = 0;

    mg_fight.bgfx_active = 1;                           /* forca o emprestimo declarado */
    cram_save(&CRAM_SUPER_BGFX, &mg_fight.pal0_saved[1]);   /* save de producao: antes de escrever */
    for (int k = 1; k < 15; k++) if (mg_fight.pal0_saved[k] != before[k]) bad++;  /* snapshot = original */
    u16 steal[14]; for (int i = 0; i < 14; i++) steal[i] = 0x0EE;
    cram_write(&CRAM_SUPER_BGFX, &steal[0]);            /* base = 1 -> PAL0[1..14] */
    host_vblank();
    for (int k = 1; k <= 8; k++) if (host_cram[k] != 0x0EE) bad++;   /* index 0 fora da faixa */
    if (host_cram[0] != before[0]) bad++;

    bgfx_release();                                     /* deve devolver PAL0[1..14] exatos */
    host_vblank();
    for (int k = 1; k < 15; k++) if (host_cram[k] != before[k]) bad++;
    if (host_cram[0] != before[0]) bad++;
    if (mg_fight.bgfx_active) bad++;
    bgfx_release(); bgfx_release();                     /* idempotente: nao escreve de novo */
    host_vblank();
    for (int k = 1; k < 15; k++) if (host_cram[k] != before[k]) bad++;
    if (host_cram[0] != before[0]) bad++;

    printf("{\"bad\": %d}\n", bad);
    return bad != 0;
}

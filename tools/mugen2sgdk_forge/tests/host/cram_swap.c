/* A primitiva e a unica porta de escrita de CRAM de um consumidor: ela nao pode
 * alcancar indice fora de [lo..hi] nem escrever quando a faixa estiver vazia. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
u32 host_sound_plays, host_def_switches;

int main(void)
{
    MG_fightInit(&mg_char_ken, 0, &mg_char_ken, 0, 0);   /* preenche host_cram com as linhas reais */
    host_vblank();

    u16 mark[16]; for (int i = 0; i < 16; i++) mark[i] = 0x0AD;
    int bad = 0;

    /* 1. escreve so a faixa declarada: CRAM_FX_PAL3 possui 0..15; usar um sub-consumidor 5..9 */
    const CramConsumer mid = { 3, 5, 9, 0, 0 };
    cram_write(&mid, mark); host_vblank();
    for (int k = 0; k < 5; k++)  if (host_cram[48 + k] == 0x0AD) bad++;   /* abaixo de lo: intacto */
    for (int k = 10; k < 16; k++) if (host_cram[48 + k] == 0x0AD) bad++;  /* acima de hi: intacto */
    for (int k = 5; k <= 9; k++)  if (host_cram[48 + k] != 0x0AD) bad++;  /* dentro: escrito */

    /* 2. faixa vazia (reserva de indice) nao escreve nada */
    const CramConsumer empty = { 1, 0, 0, 0, 0 };
    u16 before[64]; memcpy(before, host_cram, sizeof before);
    cram_write(&empty, mark); host_vblank();
    if (memcmp(before, host_cram, sizeof before)) bad++;

    /* 3. save/restore devolve a linha exatamente (depende do stub fiel da Task 2) */
    const CramConsumer *c = &CRAM_SUPER_BGFX;
    u16 saved[16]; cram_save(c, saved);
    cram_write(c, mark); host_vblank();
    cram_restore(c, saved); host_vblank();
    u16 now[16]; PAL_getColors((u16)(c->line * 16 + c->lo), now, cram_span(c));
    for (int k = 0; k < cram_span(c); k++) if (now[k] != saved[k]) bad++;

    /* 4. posse declarada: flash nao pode tocar a linha FX nem o emprestimo do super */
    if (CRAM_FLASH_P1.line != 1 || CRAM_FLASH_P1.lo != 1 || CRAM_FLASH_P1.hi != 15) bad++;
    if (CRAM_FLASH_P2.line != 2 || CRAM_FLASH_P2.borrow || CRAM_SUPER_BGFX.borrow != 1) bad++;
    if (CRAM_SUPER_BGFX.line != 0 || CRAM_SUPER_BGFX.lo != 1 || CRAM_SUPER_BGFX.hi != 14) bad++;
    /* pin das reservas: alargar uma faixa sobre a vizinha na PAL0 nao pode passar despercebido */
    if (CRAM_STAGERES.line != 0 || CRAM_STAGERES.lo != 1 || CRAM_STAGERES.hi != 8 || CRAM_STAGERES.borrow) bad++;
    if (CRAM_HUDRES.line != 0 || CRAM_HUDRES.lo != 9 || CRAM_HUDRES.hi != 15 || CRAM_HUDRES.borrow) bad++;
    if (CRAM_PORTRAIT_P2.line != 2 || CRAM_PORTRAIT_P2.lo || CRAM_PORTRAIT_P2.hi || CRAM_PORTRAIT_P2.borrow) bad++;

    /* 5. a convensao de reserva vazia nao confunde lo==0 com faixa vazia */
    if (cram_span(&CRAM_PORTRAIT_P1) != 0) bad++;
    if (cram_span(&CRAM_FX_PAL3) != 16) bad++;      /* possui lo==0: span 16, nao 0 */

    printf("{\"bad\": %d}\n", bad);
    return bad != 0;
}

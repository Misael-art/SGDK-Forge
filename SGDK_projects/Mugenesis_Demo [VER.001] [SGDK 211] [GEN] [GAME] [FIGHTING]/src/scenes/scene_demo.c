/* scene_demo.c -- cena de luta do Mugenesis_Demo.
 * Hospeda o runtime generico mugen2sgdk_forge (src/mg/) com personagens gerados (src/mg_gen/).
 * Cenario: nenhum stage convertido ainda (Etapa 4); fundo e cor solida, HUD e texto transitorio.
 */
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/audio.h"
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"
#include "scenes/fight_hud.h"

#define FIGHT_SPR_VRAM 600   /* projeteis/explods (partes de efeitos grandes); corpos e fundo usam VRAM fixa */
#define ATTRACT_IDLE_FRAMES 300   /* 5 s sem entrada no P1: CPU assume (modo demonstracao) */

static u16 sIdleFrames;

#ifdef MG_TEST_SCRIPT
/* ROM de teste: roteiro de entrada real para o P1 (evidencia de efeitos de super no emulador).
 * c+z = Special Mode (anel 30100); ~D,DB,B,D,DB,B,x = bola de fogo super (KO -> fundo 730). */
typedef struct { u16 pad; u8 frames; } ScriptStep;
#if defined(MG_TEST_COMBO)
static const ScriptStep kScript[] = {          /* P1: combo de socos na mesma regiao (faiscas) */
    { BUTTON_RIGHT, 40 },
    { BUTTON_X, 2 }, { 0, 12 }, { BUTTON_RIGHT, 6 },
    { BUTTON_X, 2 }, { 0, 12 }, { BUTTON_RIGHT, 6 },
    { BUTTON_X, 2 }, { 0, 12 }, { BUTTON_RIGHT, 6 },
    { BUTTON_X, 2 }, { 0, 12 }, { BUTTON_RIGHT, 6 },
    { 0, 60 },
};
#elif defined(MG_TEST_RING)
static const ScriptStep kScript[] = {          /* so o Special Mode (anel 30100 / grupo 8000) */
    { 0, 60 }, { BUTTON_C | BUTTON_Z, 2 }, { 0, 250 },
};
#else
static const ScriptStep kScript[] = {
    { 0, 60 },
    { BUTTON_DOWN, 1 }, { BUTTON_DOWN | BUTTON_LEFT, 1 }, { BUTTON_LEFT, 1 },
    { BUTTON_DOWN, 5 }, { BUTTON_DOWN | BUTTON_LEFT, 5 }, { BUTTON_LEFT, 1 },
    { BUTTON_LEFT | BUTTON_X, 2 }, { 0, 250 },
    { BUTTON_C | BUTTON_Z, 2 }, { 0, 250 },
};
#endif
static u8 sStep, sLeft;

static u16 scriptPad(void)
{
    if (mg_fight.round_state != 1) { sStep = 0; sLeft = kScript[0].frames; return 0; }
    if (sLeft == 0) {
        sStep = (sStep + 1) % (sizeof(kScript) / sizeof(kScript[0]));
        sLeft = kScript[sStep].frames;
    }
    sLeft--;
    /* o roteiro assume o P1 olhando para a direita; espelha se estiver virado */
    u16 pad = kScript[sStep].pad;
    if (mg_fight.p[0].facing < 0 && (pad & (BUTTON_LEFT | BUTTON_RIGHT)))
        pad ^= BUTTON_LEFT | BUTTON_RIGHT;
    return pad;
}
#endif

#ifdef MG_PCPROF
/* Amostrador de PC por H-Int (so ROM de perfil): a cada 8 linhas o handler le o PC
 * empilhado pela excecao e soma 1 no balde de 64 bytes do codigo. Exporta para
 * SRAM 0x2000 a cada 600 quadros. Vies conhecido: nao amostra o vblank nem trechos
 * com interrupcao mascarada (a amostra cai logo depois de reabilitar). */
#define PCPROF_BUCKETS 4096
#define PCPROF_LIST 48
#define SPIKE_BUCKETS 2048          /* 128 bytes por balde */
u16 mg_pc_hist[PCPROF_BUCKETS];
u32 mg_pc_list[PCPROF_LIST];
u16 mg_pc_n;
static u16 sSpikeHist[SPIKE_BUCKETS];
static u16 sSpikeFrames, sFrames;
extern void mg_pcprof_hint(void);
__asm__(
    ".globl mg_pcprof_hint\n"
    "mg_pcprof_hint:\n"
    "    movem.l %d0-%d1/%a0,-(%sp)\n"
    "    move.l 14(%sp),%d0\n"
    "    move.w mg_pc_n,%d1\n"
    "    cmp.w #48,%d1\n"
    "    bhs.s 2f\n"
    "    addq.w #1,mg_pc_n\n"
    "    add.w %d1,%d1\n"
    "    add.w %d1,%d1\n"
    "    lea mg_pc_list,%a0\n"
    "    move.l %d0,(%a0,%d1.w)\n"
    "2:  cmp.l #0x40000,%d0\n"
    "    bhs.s 1f\n"
    "    lsr.l #5,%d0\n"
    "    and.w #0xFFFE,%d0\n"
    "    lea mg_pc_hist,%a0\n"
    "    addq.w #1,(%a0,%d0.l)\n"
    "1:  movem.l (%sp)+,%d0-%d1/%a0\n"
    "    rte\n");
/* Chamado no inicio de cada quadro: as amostras do quadro anterior entram no
 * histograma de picos se aquele quadro passou do orcamento. */
static void pcprof_frame(void)
{
    const u16 load = SYS_getCPULoad();
    const u16 n = mg_pc_n;
    sFrames++;
    if (load > 100) {
        sSpikeFrames++;
        for (u16 i = 0; i < n; i++) {
            const u32 pc = mg_pc_list[i];
            if (pc < 0x40000) sSpikeHist[pc >> 7]++;
        }
    }
    mg_pc_n = 0;
}
static void pcprof_export(void)
{
    SRAM_enable();
    SRAM_writeByte(0x2000, 'P'); SRAM_writeByte(0x2001, 'C'); SRAM_writeByte(0x2002, 'H'); SRAM_writeByte(0x2003, 'S');
    for (u16 i = 0; i < PCPROF_BUCKETS; i++) SRAM_writeWord(0x2004 + i * 2, mg_pc_hist[i]);
    SRAM_writeWord(0x4004, sFrames);
    SRAM_writeWord(0x4006, sSpikeFrames);
    for (u16 i = 0; i < SPIKE_BUCKETS; i++) SRAM_writeWord(0x4008 + i * 2, sSpikeHist[i]);
    SRAM_disable();
}
#endif

void SCENE_demoEnter(void)
{

    AUDIO_stopAll();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setTextPlane(BG_A);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x202838));

    SPR_end();
    SPR_initEx(FIGHT_SPR_VRAM);
    JOY_setSupport(PORT_2, JOY_SUPPORT_6BTN);

#ifdef MG_TEST_SCRIPT
    /* ROM de teste: P2 parado para o roteiro do P1 executar sem interrupcao */
    MG_fightInit(&mg_char_ken, mg_char_ken.default_pal, &mg_char_ken, mg_char_ken.default_pal, FALSE);
#else
    MG_fightInit(&mg_char_ken, mg_char_ken.default_pal, &mg_char_ken, mg_char_ken.default_pal, TRUE);
#endif
    sIdleFrames = 0;
    FIGHT_HUD_init();
#ifdef MG_PCPROF
    SYS_disableInts();
    SYS_setHIntCallback(mg_pcprof_hint);
    VDP_setHIntCounter(7);
    VDP_setHInterrupt(TRUE);
    SYS_enableInts();
#endif
}

void SCENE_demoUpdate(void)
{
#ifdef MG_PCPROF
    {   static u16 f;
        pcprof_frame();
        if (++f == 600) { f = 0; VDP_setHInterrupt(FALSE); pcprof_export(); VDP_setHInterrupt(TRUE); mg_pc_n = 0; } }
#endif
    u16 pad1 = JOY_readJoypad(JOY_1);
#ifdef MG_TEST_SCRIPT
    pad1 = scriptPad();
    mg_fight.p[0].is_cpu = 0;
#endif
    if (pad1) sIdleFrames = 0;
    else if (sIdleFrames < ATTRACT_IDLE_FRAMES) sIdleFrames++;
#ifndef MG_TEST_SCRIPT
    mg_fight.p[0].is_cpu = sIdleFrames >= ATTRACT_IDLE_FRAMES;
#endif
#ifdef MG_TEST_SCRIPT
    MG_fightUpdate(pad1, 0);
#else
    MG_fightUpdate(pad1, JOY_readJoypad(JOY_2));
#endif
    MG_fightRender();
#ifdef MG_PROFILE
    { u32 th = getSubTick(); FIGHT_HUD_update(); mg_prof[13] += getSubTick() - th; }
#else
    FIGHT_HUD_update();
#endif
#ifdef MG_TEST_SCRIPT
    {   /* diagnostico na tela: explods ativos (anim, elemento, sprite SGDK alocado); tamanho limitado */
        char l[41];
        u8 len = 0;
        for (u8 i = 0; i < MG_MAX_EXPLOD && len < 30; i++) {
            MgExplod *e = &mg_fight.explod[i];
            if (!e->active) continue;
            char t[16];
            u8 np = 0;
            for (u8 k = 0; k < MG_MAX_PARTS; k++) if (e->dr.spr[k]) np++;
            sprintf(t, "%d:%d/%d%c ", mg_char_ken.anims[e->anim_idx].id, e->elem, np,
                    e->bgfx >= 0 ? 'B' : ' ');
            for (u8 k = 0; t[k] && len < 39; k++) l[len++] = t[k];
        }
        while (len < 39) l[len++] = ' ';
        l[39] = 0;
        VDP_drawText(l, 0, 3);
        sprintf(l, "VRAM livre %u maior %u spr %u   ", SPR_getFreeVRAM(), SPR_getLargestFreeVRAMBlock(),
                SPR_getNumActiveSprite());
        VDP_drawText(l, 0, 4);
    }
#endif
#ifdef MG_PROFILE
    /* a cada 60 quadros: % medio por etapa; e a composicao do PIOR quadro da janela */
    {
        static u16 n;
        static u32 last[13], worst[13], worst_tot, last13;
        u32 t0 = getSubTick();
        SPR_update();
        mg_prof[7] += getSubTick() - t0;
        u32 cur[13], tot = 0;
        for (u8 i = 0; i < 13; i++) { cur[i] = mg_prof[i] - last[i]; last[i] = mg_prof[i]; }
        for (u8 i = 0; i < 8; i++) tot += cur[i];
        if (tot > worst_tot) { worst_tot = tot; for (u8 i = 0; i < 13; i++) worst[i] = cur[i]; }
        /* Acumulado da luta inteira e composicao do pior quadro em SRAM 0x400
         * ("MGPF"), lidos da captura BlastEm sem depender de ler a tela. */
        {
            static u32 acc[14], wr[14], wr_tot, frames;
            frames++;
            for (u8 i = 0; i < 13; i++) acc[i] += cur[i];
            acc[13] += mg_prof[13] - last13;
            last13 = mg_prof[13];
            if (tot > wr_tot) { wr_tot = tot; for (u8 i = 0; i < 13; i++) wr[i] = cur[i]; }
            if (n == 59) {
                u32 o = 0x400;
                SRAM_enable();
                SRAM_writeByte(o++, 'M'); SRAM_writeByte(o++, 'G'); SRAM_writeByte(o++, 'P'); SRAM_writeByte(o++, 'F');
                SRAM_writeLong(o, frames); o += 4;
                for (u8 i = 0; i < 14; i++) { SRAM_writeLong(o, acc[i]); o += 4; }
                for (u8 i = 0; i < 13; i++) { SRAM_writeLong(o, wr[i]); o += 4; }
                SRAM_writeLong(o, wr_tot);
                SRAM_disable();
            }
        }
        if (++n == 60) {
            char l[41];
            last13 = 0;
            #define PCT(v) ((v) * 100 / (1280UL * 60))
            #define PCW(v) ((v) * 100 / 1280UL)
            sprintf(l, "IN%lu LG%lu PH%lu HT%lu RD%lu SU%lu T%lu  ", PCT(mg_prof[0]), PCT(mg_prof[1]),
                    PCT(mg_prof[2]), PCT(mg_prof[4]), PCT(mg_prof[6]), PCT(mg_prof[7]),
                    PCT(mg_prof[0] + mg_prof[1] + mg_prof[2] + mg_prof[3] + mg_prof[4] + mg_prof[5] + mg_prof[6] + mg_prof[7]));
            VDP_drawText(l, 0, 26);
            sprintf(l, "HUD%lu MX IN%lu CU%lu RD%lu SU%lu T%lu ", PCT(mg_prof[13]), PCW(worst[0]), PCW(worst[11]),
                    PCW(worst[6]), PCW(worst[7]), PCW(worst_tot));
            VDP_drawText(l, 0, 25);
            memset(mg_prof, 0, sizeof(mg_prof));
            memset(last, 0, sizeof(last));
            worst_tot = 0;
            n = 0;
        }
    }
#endif
}

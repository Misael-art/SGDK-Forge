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
}

void SCENE_demoUpdate(void)
{
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
        static u32 last[13], worst[13], worst_tot;
        u32 t0 = getSubTick();
        SPR_update();
        mg_prof[7] += getSubTick() - t0;
        u32 cur[13], tot = 0;
        for (u8 i = 0; i < 13; i++) { cur[i] = mg_prof[i] - last[i]; last[i] = mg_prof[i]; }
        for (u8 i = 0; i < 8; i++) tot += cur[i];
        if (tot > worst_tot) { worst_tot = tot; for (u8 i = 0; i < 13; i++) worst[i] = cur[i]; }
        if (++n == 60) {
            char l[41];
            #define PCT(v) ((v) * 100 / (1280UL * 60))
            #define PCW(v) ((v) * 100 / 1280UL)
            sprintf(l, "IN%lu LG%lu PH%lu HT%lu RD%lu SU%lu T%lu  ", PCT(mg_prof[0]), PCT(mg_prof[1]),
                    PCT(mg_prof[2]), PCT(mg_prof[4]), PCT(mg_prof[6]), PCT(mg_prof[7]),
                    PCT(mg_prof[0] + mg_prof[1] + mg_prof[2] + mg_prof[3] + mg_prof[4] + mg_prof[5] + mg_prof[6] + mg_prof[7]));
            VDP_drawText(l, 0, 26);
            sprintf(l, "MX IN%lu CU%lu NG%lu PJ%lu RD%lu SU%lu T%lu ", PCW(worst[0]), PCW(worst[11]), PCW(worst[10]),
                    PCW(worst[3]), PCW(worst[6]), PCW(worst[7]), PCW(worst_tot));
            VDP_drawText(l, 0, 25);
            memset(mg_prof, 0, sizeof(mg_prof));
            memset(last, 0, sizeof(last));
            worst_tot = 0;
            n = 0;
        }
    }
#endif
}

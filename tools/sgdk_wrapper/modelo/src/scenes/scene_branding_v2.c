#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/branding_v2.h"
#include "system/audio.h"
#include "system/input.h"

/*
 * branding_sequence_v2 — "A FORJA".
 *
 * Contrato: doc/branding_sequence_contract.json
 * Coreografia medida: doc/branding_v2_cinematic_storyboard.json
 * Orcamento de DMA: doc/branding_v2_dma_queue_contract.json
 *
 * Tomada continua de tres atos, sem VDP_clearPlane entre eles. Os numeros de
 * coreografia aqui nao sao gosto: sairam da varredura no vdp_scanline_simulator,
 * que reprovou a primeira versao com 36 sprites numa scanline. Mudar spawn,
 * stagger ou recuo do martelo exige medir de novo.
 */

/* ---- Coreografia medida (nao alterar sem re-medir) --------------------- */

#define SHARD_COUNT            56
#define SHARD_COLS              8
#define SHARD_ROWS              7
#define SHARD_SPAWN_PER_FRAME   2
#define SHARD_ROW_STAGGER       5
#define SHARD_JITTER_MOD        5
#define SHARD_SPAWN_BASE      122
#define SHARD_CONV_BASE       152
#define SHARD_RADIUS           70
#define HAMMER_RECOIL_FRAMES   10

#define EMBER_GHOSTS            5
#define ANVIL_X               128
#define ANVIL_Y               104
#define LOGO_X0                48
#define LOGO_Y0                80
#define LOGO_W                224
#define LOGO_H                 64

#define SWEEP_WIDTH            24
#define SWEEP_SPEED             3
#define HAZE_LINES             48
#define HAZE_AMP_START          6
#define CURTAIN_COLUMNS        20

/* ---- Estado ------------------------------------------------------------ */

static u8   sAct;
static u16  sHIntLine;
static s16  sHScroll[224];
static s16  sVScroll[CURTAIN_COLUMNS];
static Sprite *sEmber;
static Sprite *sGhost[EMBER_GHOSTS];
static Sprite *sHammer;
static Sprite *sShard[SHARD_COUNT];
static u8   sShardLanded[SHARD_COUNT];
static s16  sEmberTrailX[EMBER_GHOSTS * 2 + 2];
static s16  sEmberTrailY[EMBER_GHOSTS * 2 + 2];
static u8   sTrailHead;
static u8   sHammerFrame;
static u8   sShakeLeft;

/* Rampa de brasa de PAL0[9..12]: o ciclo precisa fechar, senao aparece salto. */
static const u16 EMBER_CYCLE[BRAND_V2_EMBER_CYCLE_COUNT] = {
    0x0048, 0x006A, 0x008C, 0x004A
};

/* Bandas de calor do ato 1. Uma cor por banda, aplicada no indice de piso. */
static const u16 HINT_BANDS[BRAND_V2_HINT_BANDS] = {
    0x0000, 0x0200, 0x0402, 0x0604, 0x0826, 0x0048, 0x006A
};

/* ---- H-Int: owner unico da cena ---------------------------------------- */

static void brandHIntHandler(void)
{
    u16 band = sHIntLine;

    if (band < BRAND_V2_HINT_BANDS) {
        PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST, HINT_BANDS[band]);
        sHIntLine = band + 1;
    }
}

static void brandAcquireHInt(void)
{
    sHIntLine = 0;
    VDP_setHIntCounter(224 / BRAND_V2_HINT_BANDS);
    SYS_setHIntCallback(brandHIntHandler);
    VDP_setHInterrupt(TRUE);
}

static void brandReleaseHInt(void)
{
    VDP_setHInterrupt(FALSE);
    SYS_setHIntCallback(NULL);
    sHIntLine = 0;
}

/* ---- Utilitarios ------------------------------------------------------- */

static s16 brandLerp(s16 from, s16 to, u16 num, u16 den)
{
    if (den == 0) return to;
    return from + (s16)(((s32)(to - from) * (s32)num) / (s32)den);
}

static void brandShardTarget(u16 index, s16 *outX, s16 *outY)
{
    const u16 col = index % SHARD_COLS;
    const u16 row = index / SHARD_COLS;

    *outX = LOGO_X0 + 4 + (s16)(col * ((LOGO_W - 16) / (SHARD_COLS - 1)));
    *outY = LOGO_Y0 + (s16)(row * ((LOGO_H - 16) / (SHARD_ROWS - 1)));
}

/*
 * Leque radial sem trigonometria de ponto flutuante: a tabela cobre um giro
 * completo em 16 passos e o indice do estilhaco escolhe o setor.
 */
static const s16 FAN_COS[16] = { 64, 59, 45, 24, 0, -24, -45, -59, -64, -59, -45, -24, 0, 24, 45, 59 };
static const s16 FAN_SIN[16] = { 0, 24, 45, 59, 64, 59, 45, 24, 0, -24, -45, -59, -64, -59, -45, -24 };

static void brandShardExplodePos(u16 index, u16 age, s16 *outX, s16 *outY)
{
    const u16 sector = (index * 16u) / SHARD_COUNT;
    u16 t = (age > 16) ? 16 : age;
    const s16 radius = (s16)((SHARD_RADIUS * t) / 16);

    /* horizontal alongado: o impacto espalha mais na largura que na altura */
    *outX = ANVIL_X + (s16)(((s32)FAN_COS[sector] * radius * 3) / 128);
    *outY = ANVIL_Y + (s16)(((s32)FAN_SIN[sector] * radius) / 64);
}

/* ---- Ato 1: ignicao ---------------------------------------------------- */

static void brandEnterIgnition(void)
{
    u16 i;

    SPR_reset();
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHilightShadow(TRUE);

    PAL_setPalette(BRAND_V2_PAL_FORGE, img_forge_bg_b.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_METAL, img_logo_engine_v2.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_WORDMARK, img_logo_author_v2.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_FX, spr_forge_ember.palette->data, DMA);

    VDP_drawImageEx(BG_B, &img_forge_bg_b,
                    TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, FALSE, FALSE, FALSE, TILE_USER_INDEX),
                    0, 0, FALSE, TRUE);
    VDP_drawImageEx(BG_A, &img_forge_bg_a_props,
                    TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, TRUE, FALSE, FALSE,
                                   TILE_USER_INDEX + 1093),
                    0, 0, FALSE, TRUE);

    sEmber = SPR_addSprite(&spr_forge_ember, 232, -16,
                           TILE_ATTR(BRAND_V2_PAL_FX, TRUE, FALSE, FALSE));
    for (i = 0; i < EMBER_GHOSTS; i++) {
        sGhost[i] = SPR_addSprite(&spr_forge_ember, -32, -32,
                                  TILE_ATTR(BRAND_V2_PAL_FX, FALSE, FALSE, FALSE));
        SPR_setVisibility(sGhost[i], HIDDEN);
    }
    sHammer = SPR_addSprite(&spr_forge_hammer, 150, -48,
                            TILE_ATTR(BRAND_V2_PAL_METAL, TRUE, FALSE, FALSE));
    SPR_setVisibility(sHammer, HIDDEN);

    sTrailHead = 0;
    sHammerFrame = 0;
    brandAcquireHInt();
    AUDIO_playCue(AUDIO_CUE_BRAND_ENGINE_HIT);
}

static void brandUpdateIgnition(u16 f)
{
    /* PAL0[9..12] gira em CRAM: a forja respira antes da primeira imagem. */
    if ((f & 7) == 0) {
        u16 i;
        for (i = 0; i < BRAND_V2_EMBER_CYCLE_COUNT; i++) {
            PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST + i,
                         EMBER_CYCLE[(i + (f >> 3)) & (BRAND_V2_EMBER_CYCLE_COUNT - 1)]);
        }
    }

    if (f >= BRAND_V2_EMBER_FALL_START && f <= BRAND_V2_EMBER_FALL_END) {
        const u16 t = f - BRAND_V2_EMBER_FALL_START;
        const u16 span = BRAND_V2_EMBER_FALL_END - BRAND_V2_EMBER_FALL_START;
        /* horizontal linear com arrasto; vertical acelerando: peso legivel */
        const s16 x = brandLerp(232, ANVIL_X, t, span);
        const s16 y = (s16)(-16 + (((s32)(ANVIL_Y + 16) * t * t) / ((s32)span * span)));
        u16 g;

        SPR_setPosition(sEmber, x, y);
        SPR_setFrame(sEmber, (f >> 2) & 3);

        sEmberTrailX[sTrailHead] = x;
        sEmberTrailY[sTrailHead] = y;
        sTrailHead = (u8)((sTrailHead + 1) % (EMBER_GHOSTS * 2 + 2));

        for (g = 0; g < EMBER_GHOSTS; g++) {
            const u8 back = (u8)((sTrailHead + (EMBER_GHOSTS * 2 + 2)
                                  - ((g + 1) * 2)) % (EMBER_GHOSTS * 2 + 2));
            if (t > (g + 1) * 2) {
                SPR_setVisibility(sGhost[g], VISIBLE);
                SPR_setPosition(sGhost[g], sEmberTrailX[back], sEmberTrailY[back]);
                SPR_setFrame(sGhost[g], (f >> 2) & 3);
            }
        }
    } else if (f > BRAND_V2_EMBER_FALL_END) {
        u16 g;
        for (g = 0; g < EMBER_GHOSTS; g++) SPR_setVisibility(sGhost[g], HIDDEN);
        SPR_setPosition(sEmber, ANVIL_X, ANVIL_Y);
        SPR_setFrame(sEmber, (f & 8) ? 5 : 4);   /* esmagamento e assentamento */
    }

    /* Antecipacao: o martelo sobe carregando o golpe. */
    if (f >= 96) {
        const u16 t = f - 96;
        SPR_setVisibility(sHammer, VISIBLE);
        SPR_setPosition(sHammer, 150, (s16)(ANVIL_Y - 56 - (t * 2)));
        sHammerFrame = (t < 12) ? 1u : 2u;
        SPR_setFrame(sHammer, sHammerFrame);
    }
}

/* ---- Ato 2: o golpe ---------------------------------------------------- */

static void brandEnterStrike(void)
{
    u16 i;

    for (i = 0; i < SHARD_COUNT; i++) {
        sShard[i] = SPR_addSprite(&spr_forge_shard, -32, -32,
                                  TILE_ATTR(BRAND_V2_PAL_FX, TRUE, FALSE, FALSE));
        SPR_setVisibility(sShard[i], HIDDEN);
        sShardLanded[i] = 0;
    }
    sShakeLeft = 6;
    AUDIO_playCue(AUDIO_CUE_BRAND_PROJECT_WHOOSH);
}

static void brandStrikeFlashAndShake(u16 t)
{
    /* Flash de 2 quadros com mascara: escrevemos so a rampa quente, o que evita
     * varrer a CRAM inteira e reduz o risco de CRAM dots. */
    if (t < 2) {
        u16 i;
        for (i = 0; i < BRAND_V2_EMBER_CYCLE_COUNT; i++)
            PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST + i, 0x0EEE);
    } else if (t == 2) {
        u16 i;
        for (i = 0; i < BRAND_V2_EMBER_CYCLE_COUNT; i++)
            PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST + i, EMBER_CYCLE[i]);
    }

    if (sShakeLeft) {
        static const s16 SHAKE[6] = { 3, 2, 2, 1, 1, 0 };
        const s16 dy = SHAKE[6 - sShakeLeft];
        VDP_setVerticalScroll(BG_A, dy);
        VDP_setVerticalScroll(BG_B, (s16)(dy >> 1));
        sShakeLeft--;
        if (!sShakeLeft) {
            VDP_setVerticalScroll(BG_A, 0);
            VDP_setVerticalScroll(BG_B, 0);
        }
    }
}

static void brandUpdateShards(u16 f)
{
    u16 i;

    for (i = 0; i < SHARD_COUNT; i++) {
        const u16 born = SHARD_SPAWN_BASE + (i / SHARD_SPAWN_PER_FRAME);
        const u16 row = i / SHARD_COLS;
        const u16 convStart = SHARD_CONV_BASE + (row * SHARD_ROW_STAGGER)
                            + ((i % SHARD_JITTER_MOD) * 2);
        const u16 dur = 26 - (row * 2);

        if (sShardLanded[i] || f < born) continue;

        if (f < convStart) {
            s16 x, y;
            brandShardExplodePos(i, f - born, &x, &y);
            SPR_setVisibility(sShard[i], VISIBLE);
            SPR_setPosition(sShard[i], x, y);
            SPR_setFrame(sShard[i], (u8)((f >> 3) & 3));
        } else {
            const u16 t = f - convStart;
            if (t >= dur) {
                /* Pouso progressivo: vira tile do logo e sai do SAT na hora.
                 * A populacao de sprites CAI durante a montagem. */
                SPR_setVisibility(sShard[i], HIDDEN);
                sShardLanded[i] = 1;
            } else {
                s16 ex, ey, tx, ty;
                const u16 e = (t * t) / dur;        /* ease-in inteiro */
                brandShardExplodePos(i, 16, &ex, &ey);
                brandShardTarget(i, &tx, &ty);
                SPR_setVisibility(sShard[i], VISIBLE);
                SPR_setPosition(sShard[i], brandLerp(ex, tx, e, dur),
                                brandLerp(ey, ty, e, dur));
                SPR_setFrame(sShard[i], (u8)((f >> 3) & 3));
            }
        }
    }
}

static void brandHeatHaze(u16 t)
{
    u16 line;
    const s16 amp = (s16)(HAZE_AMP_START - ((t * (HAZE_AMP_START - 1)) / 120));

    for (line = 0; line < 224; line++) {
        if (line < (224 - HAZE_LINES)) {
            sHScroll[line] = 0;
        } else {
            const u16 phase = (line + t) & 15;
            const s16 wave = (phase < 8) ? (s16)phase : (s16)(15 - phase);
            sHScroll[line] = (s16)(((wave - 4) * amp) >> 2);
        }
    }
    /* DMA no VBlank, nunca por CPU: e a correcao do spike medido no v1. */
    VDP_setHorizontalScrollLine(BG_B, 0, sHScroll, 224, DMA_QUEUE);
}

static void brandSpecularSweep(u16 t)
{
    /* A coluna de highlight anda sobre os tiles do logo. O operador de
     * Shadow/Highlight clareia a cor de saida: por isso o asset precisa do
     * degrau com folga em PAL1[13..14]. */
    const s16 head = (s16)(LOGO_X0 - SWEEP_WIDTH + (t * SWEEP_SPEED));
    u16 tx;

    for (tx = 0; tx < (LOGO_W / 8); tx++) {
        const s16 px = (s16)(LOGO_X0 + (tx * 8));
        const bool lit = (px >= head) && (px < (head + SWEEP_WIDTH));
        u16 ty;
        for (ty = 0; ty < (LOGO_H / 8); ty++) {
            VDP_setTileMapXY(BG_A,
                TILE_ATTR_FULL(BRAND_V2_PAL_METAL, lit, FALSE, FALSE,
                               TILE_USER_INDEX + 1397 + (ty * (LOGO_W / 8)) + tx),
                (u16)((LOGO_X0 / 8) + tx), (u16)((LOGO_Y0 / 8) + ty));
        }
    }
}

static void brandUpdateStrike(u16 f)
{
    const u16 t = f - BRAND_V2_ACT_STRIKE_START;

    brandStrikeFlashAndShake(t);

    if (f < BRAND_V2_ACT_STRIKE_START + HAMMER_RECOIL_FRAMES) {
        SPR_setFrame(sHammer, (t < 2) ? 4u : 5u);      /* contato em smear */
        SPR_setPosition(sHammer, 150, (s16)(ANVIL_Y - 56 - (t * 10)));
    } else if (f == BRAND_V2_ACT_STRIKE_START + HAMMER_RECOIL_FRAMES) {
        SPR_setVisibility(sHammer, HIDDEN);
    }

    if (f >= SHARD_SPAWN_BASE) brandUpdateShards(f);

    if (f >= BRAND_V2_LOGO_LOCK) {
        const u16 st = f - BRAND_V2_LOGO_LOCK;
        brandSpecularSweep(st);
        brandHeatHaze(st);
    }
}

/* ---- Ato 3: assinatura ------------------------------------------------- */

static void brandEnterSignature(void)
{
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_COLUMN);
    VDP_drawImageEx(BG_A, &img_logo_author_v2,
                    TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, FALSE, FALSE, FALSE,
                                   TILE_USER_INDEX + 1579),
                    8, 12, FALSE, TRUE);
}

static void brandUpdateSignature(u16 f)
{
    const u16 t = f - BRAND_V2_ACT_SIGNATURE_START;
    u16 c;

    if (t <= 60) {
        /* Cortina por coluna: offsets escalonados do centro para as bordas.
         * Uniforme leria como slide de software. */
        for (c = 0; c < CURTAIN_COLUMNS; c++) {
            const u16 dist = (c < (CURTAIN_COLUMNS / 2))
                           ? ((CURTAIN_COLUMNS / 2) - c) : (c - (CURTAIN_COLUMNS / 2));
            const s16 delay = (s16)(dist * 2);
            const s16 prog = (s16)t - delay;
            sVScroll[c] = (prog <= 0) ? 0 : (s16)(prog * 4);
        }
        VDP_setVerticalScrollTile(BG_B, 0, sVScroll, CURTAIN_COLUMNS, DMA_QUEUE);
    }

    if (f == 430) {
        VDP_drawImageEx(BG_A, &img_logo_project_v2,
                        TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, FALSE, FALSE, FALSE,
                                       TILE_USER_INDEX + 1640),
                        6, 10, FALSE, TRUE);
    }

    if (f == BRAND_V2_PRESENTS_IN) {
        /* O presents vive no plano WINDOW: imovel enquanto a cortina move os
         * planos por baixo. O v1 e o v2 deixavam esse plano 100% ocioso. */
        VDP_setWindowVPos(FALSE, 22);
        VDP_drawImageEx(WINDOW, &img_presents_text_v2,
                        TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, FALSE, FALSE, FALSE,
                                       TILE_USER_INDEX + 1783),
                        14, 23, FALSE, TRUE);
    }

    /* Entrega por fade de paleta, sem corte a preto. */
    if (f >= (BRAND_V2_END - 10)) {
        const u16 step = f - (BRAND_V2_END - 10);
        PAL_fadeOutAll(10 - step, TRUE);
    }
}

/* ---- Ciclo de vida ----------------------------------------------------- */

void SCENE_brandingV2Enter(void)
{
    gApp.showDebugHud = FALSE;
    sAct = 0xFF;
    sShakeLeft = 0;
    memset(sShardLanded, 0, sizeof(sShardLanded));
    AUDIO_stopAll();
}

void SCENE_brandingV2Exit(void)
{
    brandReleaseHInt();
    VDP_setHilightShadow(FALSE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_setWindowVPos(FALSE, 0);
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
}

void SCENE_brandingV2Update(void)
{
    const u16 f = gApp.sceneFrames;

    if (INPUT_pressed(BUTTON_START) || INPUT_pressed(BUTTON_A)) {
        SCENE_brandingV2Exit();
        APP_changeScene(APP_SCENE_BOOT);
        return;
    }

    if (f < BRAND_V2_ACT_STRIKE_START) {
        if (sAct != 0) { sAct = 0; brandEnterIgnition(); }
        brandUpdateIgnition(f);
    } else if (f < BRAND_V2_ACT_SIGNATURE_START) {
        if (sAct != 1) { sAct = 1; brandEnterStrike(); }
        brandUpdateStrike(f);
    } else if (f < BRAND_V2_END) {
        if (sAct != 2) { sAct = 2; brandEnterSignature(); }
        brandUpdateSignature(f);
    } else {
        SCENE_brandingV2Exit();
        APP_changeScene(APP_SCENE_BOOT);
        return;
    }

    SPR_update();
}

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
#define SHARD_ROW_STAGGER       6
#define SHARD_JITTER_MOD        5
#define SHARD_SPAWN_BASE      122
#define SHARD_CONV_BASE       152
#define SHARD_RADIUS           70
#define HAMMER_CONTACT_HOLD     8
#define HAMMER_RECOIL_FRAMES   16

#define EMBER_GHOSTS            5
#define ANVIL_X               128
#define ANVIL_Y               104
#define LOGO_X0                48
#define LOGO_Y0                64
#define LOGO_W                224
#define LOGO_H                 64
#define HAMMER_X              108
#define HAMMER_CONTACT_Y       68
#define HAMMER_WINDUP_Y        (-12)

#define SWEEP_WIDTH            24
#define SWEEP_SPEED             3
#define HAZE_LINES             48
#define HAZE_AMP_START          6
#define CURTAIN_COLUMNS        20

/* ---- Layout de VRAM: manual, porque o pool automatico nao cabe ----------
 *
 * O crash da primeira versao foi SPR_addSprite auto-alocando 1292 tiles contra
 * uma reserva de 320: o pool esgota, SPR_addSprite devolve NULL e a chamada
 * seguinte derruba a CPU. Aqui cada sprite aponta para tiles compartilhados.
 *
 * Os 56 estilhacos usam UM conjunto de 16 tiles, nao 56 copias de 4 quadros.
 * O martelo usa a janela dupla de 72 tiles que o dma_queue_contract decidiu.
 */
#define HAMMER_SLOT_TILES 36
#define HAMMER_WINDOW_SLOTS 2
#define EMBER_FRAME_MAX 6
#define SHARD_FRAME_MAX 4

/*
 * Os offsets sao DERIVADOS de tileset->numTile, nunca escritos a mao. A versao
 * anterior hardcodou 304 tiles para o bg_a e o ResComp gerou 309: os cinco de
 * diferenca sobrepuseram o logo e encheram a tela de tiles de lixo.
 */
static u16 sVramBgB, sVramBgA, sVramLogo, sVramShard, sVramEmber, sVramHammer;
static u16 sVramAuthor, sVramProject, sVramPresents;
static u16 sEmberFrameBase[EMBER_FRAME_MAX];
static u16 sShardFrameBase[SHARD_FRAME_MAX];
static u8  sEmberFrameCount;
static u8  sShardFrameCount;

/* ---- Estado ------------------------------------------------------------ */

static u8   sAct;
static u8   sHIntArmed;
static u8   sHIntReady;
static u16  sHIntLine;
static s16  sHScroll[224];
static s16  sVScroll[CURTAIN_COLUMNS];
static Sprite *sEmber;
static Sprite *sGhost[EMBER_GHOSTS];
static Sprite *sHammer;
static Sprite *sShard[SHARD_COUNT];
static u8   sShardLanded[SHARD_COUNT];
/*
 * Precomputo por estilhaco. O loop de update fazia, POR QUADRO E POR ESTILHACO:
 * um modulo por 5, uma divisao (t*t)/dur e duas divisoes de 32 bits no lerp,
 * mais duas chamadas recomputando posicao de explosao e alvo que sao
 * constantes. Sao ~128 divisoes por quadro no 68000, onde DIVS custa ~150
 * ciclos: sozinhas comiam perto de 15% do orcamento do quadro.
 * Tudo isso vira tabela preenchida uma vez em brandEnterStrike.
 */
static u16  sShardBorn[SHARD_COUNT];
static u16  sShardConv[SHARD_COUNT];
static u16  sShardDur[SHARD_COUNT];
static s16  sShardEX[SHARD_COUNT], sShardEY[SHARD_COUNT];
static s16  sShardTX[SHARD_COUNT], sShardTY[SHARD_COUNT];
static u16  sShardRecip[SHARD_COUNT];   /* 65536 / (dur*dur), fixo por estilhaco */
static s16  sEmberTrailX[EMBER_GHOSTS * 2 + 2];
static s16  sEmberTrailY[EMBER_GHOSTS * 2 + 2];
static u8   sTrailHead;
static u8   sHammerFrame;
static u8   sHammerSlotLoaded[HAMMER_WINDOW_SLOTS];
static u8   sHammerSlotFrame[HAMMER_WINDOW_SLOTS];
static u8   sShakeLeft;
static u8   sLogoDrawn;
static u8   sHazeArmed;

/* Rampa de brasa de PAL0[9..12]: o ciclo precisa fechar, senao aparece salto. */
static const u16 EMBER_CYCLE[BRAND_V2_EMBER_CYCLE_COUNT] = {
    0x0048, 0x006A, 0x008C, 0x004A
};

/* Bandas de calor do ato 1. Uma cor por banda, aplicada no indice de piso. */
static const u16 HINT_BANDS[BRAND_V2_HINT_BANDS] = {
    0x0000, 0x0200, 0x0402, 0x0604, 0x0826, 0x0048, 0x006A
};

/* ---- H-Int: owner unico da cena ----------------------------------------
 *
 * PORQUE a bisseccao via 0x23080000: o handler era `void` e o GCC emitia RTS.
 * H-Int e excecao de nivel 4; a pilha tem SR+PC. RTS so desempilha PC e o
 * SR (tipicamente 0x2308) vira a word alta do endereco seguinte: 0x23080000.
 * SGDK documenta isso em sys.h: HINTERRUPT_CALLBACK = attribute((interrupt)),
 * que emite RTE. PAL_setColor / escrita direta no CRAM nao eram a causa do
 * vetor — eram um segundo risco (DMA/VDP_CTRL no meio do IRQ).
 *
 * Armadura:
 *  1. HINTERRUPT_CALLBACK (RTE).
 *  2. Nao ligar o H-Int em enter(): o DMA da carga ainda nao foi flushado.
 *  3. V-Int mascara o H-Int para o flush do VBlank nao ser interrompido.
 *  4. VBlank callback (depois do DMA) escreve a banda 0 e rearma.
 */

static void brandHintWrite(u16 color)
{
    *((vu32*) VDP_CTRL_PORT) = VDP_WRITE_CRAM_ADDR((u32)(BRAND_V2_EMBER_CYCLE_FIRST * 2));
    *((vu16*) VDP_DATA_PORT) = color;
}

static HINTERRUPT_CALLBACK brandHIntHandler(void)
{
    u16 band = sHIntLine;

    if (band < BRAND_V2_HINT_BANDS) {
        brandHintWrite(HINT_BANDS[band]);
        sHIntLine = band + 1;
    }
}

static void brandVIntMaskHInt(void)
{
    VDP_setHInterrupt(FALSE);
}

static void brandVBlankRearmHInt(void)
{
    if (!sHIntArmed) return;

    /* Primeiro VBlank so drena o DMA de enter(); o H-Int sobe no seguinte. */
    if (!sHIntReady) {
        sHIntReady = 1;
        return;
    }

    brandHintWrite(HINT_BANDS[0]);
    sHIntLine = 1;
    VDP_setHInterrupt(TRUE);
}

static void brandAcquireHInt(void)
{
    sHIntLine = 0;
    sHIntReady = 0;
    sHIntArmed = 1;
    /* Counter e "linhas entre IRQs": 32 linhas => valor 31. */
    VDP_setHIntCounter((u8)((224 / BRAND_V2_HINT_BANDS) - 1));
    SYS_setHIntCallback(brandHIntHandler);
    SYS_setVIntCallback(brandVIntMaskHInt);
    SYS_setVBlankCallback(brandVBlankRearmHInt);
}

static void brandReleaseHInt(void)
{
    VDP_setHInterrupt(FALSE);
    SYS_setHIntCallback(NULL);
    SYS_setVIntCallback(NULL);
    SYS_setVBlankCallback(NULL);
    sHIntLine = 0;
    sHIntReady = 0;
    sHIntArmed = 0;
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
    /*
     * Setor por stride coprimo de 16, nao por divisao com SHARD_COUNT.
     *
     * PORQUE: `(index * 16) / SHARD_COUNT` com 32 estilhacos dava index/2, e
     * como `born` tambem e index/2, todo par 2k e 2k+1 nascia no mesmo quadro
     * NO MESMO SETOR — 16 pares perfeitamente sobrepostos. Os 32 sprites do SAT
     * rendiam 16 posicoes visiveis, gastando metade do orcamento em duplicatas
     * que o espectador nunca via.
     *
     * Stride 5 e coprimo de 16, entao visita os 16 setores antes de repetir.
     * Pares consecutivos ficam a 5 setores de distancia; pares que repetem setor
     * (i e i+16) tem `born` separado por 8 quadros, logo raios diferentes.
     */
    const u16 sector = (index * 5u) & 15u;
    u16 t = (age > 16) ? 16 : age;
    const s16 radius = (s16)((SHARD_RADIUS * t) / 16);

    /* horizontal alongado: o impacto espalha mais na largura que na altura */
    *outX = ANVIL_X + (s16)(((s32)FAN_COS[sector] * radius * 3) / 128);
    *outY = ANVIL_Y + (s16)(((s32)FAN_SIN[sector] * radius) / 64);
}

/*
 * Streaming do martelo: janela dupla de 72 tiles. O quadro pedido e carregado
 * no slot (frame & 1) e o sprite passa a apontar para la. E o que o
 * dma_queue_contract decidiu e o que a primeira versao do runtime ignorou.
 */
static u16 brandLoadAnimFrames(const SpriteDefinition *def, u16 vram,
                               u16 *bases, u8 maxFrames, u8 *outCount)
{
    const Animation *anim = def->animations[0];
    u16 cursor = vram;
    u8 i;
    u8 n = anim->numFrame;

    if (n > maxFrames) n = maxFrames;
    for (i = 0; i < n; i++) {
        const TileSet *ts = anim->frames[i]->tileset;
        bases[i] = cursor;
        VDP_loadTileSet(ts, cursor, DMA);
        cursor += ts->numTile;
    }
    *outCount = n;
    return cursor;
}

static void brandSetSharedFrame(Sprite *spr, const u16 *bases, u8 count, u8 frame)
{
    if (spr == NULL) return;
    if (frame >= count) frame = (u8)(count - 1);
    SPR_setVRAMTileIndex(spr, (s16)bases[frame]);
    SPR_setFrame(spr, frame);
}

static void brandHammerSetFrame(u8 frame)
{
    const u8 slot = (u8)(frame & 1u);
    const u16 base = sVramHammer + (slot * HAMMER_SLOT_TILES);

    if (!sHammerSlotLoaded[slot] || sHammerSlotFrame[slot] != frame) {
        const Animation *anim = spr_forge_hammer.animations[0];
        if (frame < anim->numFrame) {
            VDP_loadTileSet(anim->frames[frame]->tileset, base, DMA_QUEUE);
            sHammerSlotLoaded[slot] = 1;
            sHammerSlotFrame[slot] = frame;
        }
    }
    SPR_setVRAMTileIndex(sHammer, (s16)base);
    SPR_setFrame(sHammer, frame);
    sHammerFrame = frame;
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

    VDP_setBackgroundColor(0);
    sVramBgB    = TILE_USER_INDEX;
    sVramBgA    = sVramBgB + img_forge_bg_b.tileset->numTile;
    sVramLogo   = sVramBgA + img_forge_bg_a_props.tileset->numTile;
    sVramShard  = sVramLogo + img_logo_engine_v2.tileset->numTile;
    VDP_loadTileSet(img_logo_engine_v2.tileset, sVramLogo, DMA);
    /* Todos os quadros, nao so o 0: maxNumTile e o teto DE UM quadro. */
    sVramEmber  = brandLoadAnimFrames(&spr_forge_shard, sVramShard,
                                      sShardFrameBase, SHARD_FRAME_MAX,
                                      &sShardFrameCount);
    sVramHammer = brandLoadAnimFrames(&spr_forge_ember, sVramEmber,
                                      sEmberFrameBase, EMBER_FRAME_MAX,
                                      &sEmberFrameCount);

    VDP_drawImageEx(BG_B, &img_forge_bg_b,
                    TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, FALSE, FALSE, FALSE, sVramBgB),
                    0, 0, FALSE, TRUE);
    VDP_drawImageEx(BG_A, &img_forge_bg_a_props,
                    TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, TRUE, FALSE, FALSE, sVramBgA),
                    0, 0, FALSE, TRUE);

    PAL_setColor(0, 0x0000);   /* depois das paletas: o magenta nao vai para a borda */

    sEmber = SPR_addSpriteEx(&spr_forge_ember, 232, -16,
                             TILE_ATTR(BRAND_V2_PAL_FX, TRUE, FALSE, FALSE), 0);
    SPR_setVRAMTileIndex(sEmber, (s16)sEmberFrameBase[0]);
    SPR_setAutoTileUpload(sEmber, FALSE);
    for (i = 0; i < EMBER_GHOSTS; i++) {
        sGhost[i] = SPR_addSpriteEx(&spr_forge_ember, -32, -32,
                                    TILE_ATTR(BRAND_V2_PAL_FX, FALSE, FALSE, FALSE), 0);
        SPR_setVRAMTileIndex(sGhost[i], (s16)sEmberFrameBase[0]);
        SPR_setAutoTileUpload(sGhost[i], FALSE);
        SPR_setVisibility(sGhost[i], HIDDEN);
    }
    sHammer = SPR_addSpriteEx(&spr_forge_hammer, 150, -48,
                              TILE_ATTR(BRAND_V2_PAL_METAL, TRUE, FALSE, FALSE), 0);
    SPR_setAutoTileUpload(sHammer, FALSE);
    sHammerSlotLoaded[0] = 0;
    sHammerSlotLoaded[1] = 0;
    brandHammerSetFrame(0);
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
        brandSetSharedFrame(sEmber, sEmberFrameBase, sEmberFrameCount, (u8)((f >> 2) & 3));

        sEmberTrailX[sTrailHead] = x;
        sEmberTrailY[sTrailHead] = y;
        sTrailHead = (u8)((sTrailHead + 1) % (EMBER_GHOSTS * 2 + 2));

        for (g = 0; g < EMBER_GHOSTS; g++) {
            const u8 back = (u8)((sTrailHead + (EMBER_GHOSTS * 2 + 2)
                                  - ((g + 1) * 2)) % (EMBER_GHOSTS * 2 + 2));
            if (t > (g + 1) * 2) {
                SPR_setVisibility(sGhost[g], VISIBLE);
                SPR_setPosition(sGhost[g], sEmberTrailX[back], sEmberTrailY[back]);
                brandSetSharedFrame(sGhost[g], sEmberFrameBase, sEmberFrameCount,
                                    (u8)((f >> 2) & 3));
            }
        }
    } else if (f > BRAND_V2_EMBER_FALL_END) {
        u16 g;
        for (g = 0; g < EMBER_GHOSTS; g++) SPR_setVisibility(sGhost[g], HIDDEN);
        SPR_setPosition(sEmber, ANVIL_X, ANVIL_Y);
        brandSetSharedFrame(sEmber, sEmberFrameBase, sEmberFrameCount,
                            (u8)((f & 8) ? 5 : 4));   /* esmagamento e assentamento */
    }

    /* Windup sobe, depois o martelo CAI na bigorna. A versao anterior so
     * subia e o contacto nunca acontecia (y minimo = 48, face em 104). */
    if (f >= 96) {
        const u16 t = f - 96;
        s16 y;
        u8 frame;

        SPR_setVisibility(sHammer, VISIBLE);
        if (t < 12) {
            y = brandLerp(HAMMER_CONTACT_Y - 8, HAMMER_WINDUP_Y, t, 12);
            frame = (t < 6) ? 1u : 2u;
        } else {
            y = brandLerp(HAMMER_WINDUP_Y, HAMMER_CONTACT_Y, (u16)(t - 12), 12);
            frame = 3u;
        }
        SPR_setPosition(sHammer, HAMMER_X, y);
        brandHammerSetFrame(frame);
    }
}

/* ---- Ato 2: o golpe ---------------------------------------------------- */

static void brandEnsureShard(u16 i)
{
    if (sShard[i] != NULL) return;
    sShard[i] = SPR_addSpriteEx(&spr_forge_shard, -32, -32,
                                TILE_ATTR(BRAND_V2_PAL_FX, TRUE, FALSE, FALSE), 0);
    if (sShard[i] == NULL) return;
    SPR_setVRAMTileIndex(sShard[i], (s16)sShardFrameBase[0]);
    SPR_setAutoTileUpload(sShard[i], FALSE);
}

static void brandEnterStrike(void)
{
    u16 i;

    /* Flash e ciclo de brasa precisam do indice 9 inteiro; o raster sai. */
    brandReleaseHInt();
    for (i = 0; i < SHARD_COUNT; i++) {
        sShard[i] = NULL;
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
        const u16 born = sShardBorn[i];
        const u16 convStart = sShardConv[i];
        const u16 dur = sShardDur[i];

        if (sShardLanded[i] || f < born) continue;

        brandEnsureShard(i);
        if (sShard[i] == NULL) continue;

        if (f < convStart) {
            s16 x, y;
            brandShardExplodePos(i, f - born, &x, &y);
            SPR_setVisibility(sShard[i], VISIBLE);
            SPR_setPosition(sShard[i], x, y);
            brandSetSharedFrame(sShard[i], sShardFrameBase, sShardFrameCount,
                                (u8)((f >> 3) & 3));
        } else {
            const u16 t = f - convStart;
            if (t >= dur) {
                /* Pouso so retira o sprite. O wordmark entra inteiro pelo
                 * tilemap do IMAGE em LOGO_LOCK — carimbo parcial + unpack
                 * LZ4W por estilhaco estourava CPU e sujava o F. */
                SPR_setVisibility(sShard[i], HIDDEN);
                sShardLanded[i] = 1;
            } else {
                /* ease-in sem divisao: (delta * t^2) * (65536/dur^2) >> 16 */
                const u32 tt = (u32)t * (u32)t;
                const u32 k  = tt * (u32)sShardRecip[i];
                const s16 ex = sShardEX[i], ey = sShardEY[i];
                const s16 x  = ex + (s16)((((s32)(sShardTX[i] - ex)) * (s32)(k >> 8)) >> 8);
                const s16 y  = ey + (s16)((((s32)(sShardTY[i] - ey)) * (s32)(k >> 8)) >> 8);
                SPR_setVisibility(sShard[i], VISIBLE);
                SPR_setPosition(sShard[i], x, y);
                brandSetSharedFrame(sShard[i], sShardFrameBase, sShardFrameCount,
                                    (u8)((f >> 3) & 3));
            }
        }
    }
}

static void brandHeatHaze(u16 t)
{
    u16 line;
    const s16 amp = (s16)(HAZE_AMP_START - ((t * (HAZE_AMP_START - 1)) / 120));
    const u16 y0 = (u16)(224 - HAZE_LINES);

    if (!sHazeArmed) {
        /* Sem isto o upload de 224 linhas no modo PLANE invade VRAM e
         * nasce sujeira a esquerda do FORGE. */
        VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
        sHazeArmed = 1;
    }
    if (t & 1) return;

    for (line = 0; line < HAZE_LINES; line++) {
        const u16 phase = (line + t) & 15;
        const s16 wave = (phase < 8) ? (s16)phase : (s16)(15 - phase);
        sHScroll[line] = (s16)(((wave - 4) * amp) >> 2);
    }
    VDP_setHorizontalScrollLine(BG_B, y0, sHScroll, HAZE_LINES, DMA_QUEUE);
}

static void brandDrawLogo(void)
{
    u16 i;

    /* Tiles ja residentes. drawImageEx descompactava APLIB+LZ4W no display
     * e recarregava o tileset por cima do martelo/FX. */
    VDP_setTileMapEx(BG_A, img_logo_engine_v2.tilemap,
                     TILE_ATTR_FULL(BRAND_V2_PAL_METAL, TRUE, FALSE, FALSE, sVramLogo),
                     LOGO_X0 / 8, LOGO_Y0 / 8,
                     0, 0, LOGO_W / 8, LOGO_H / 8, DMA_QUEUE);
    for (i = 0; i < SHARD_COUNT; i++) {
        if (sShard[i] != NULL) SPR_setVisibility(sShard[i], HIDDEN);
        sShardLanded[i] = 1;
    }
    sLogoDrawn = 1;
}

static void brandSpecularSweep(u16 t)
{
    (void)t;
    if (!sLogoDrawn) brandDrawLogo();
}

static void brandUpdateStrike(u16 f)
{
    const u16 t = f - BRAND_V2_ACT_STRIKE_START;

    brandStrikeFlashAndShake(t);

    if (f < BRAND_V2_ACT_STRIKE_START + HAMMER_RECOIL_FRAMES) {
        s16 y;
        u8 frame;

        if (t < HAMMER_CONTACT_HOLD) {
            y = HAMMER_CONTACT_Y;
            frame = 4u;
        } else {
            y = brandLerp(HAMMER_CONTACT_Y, HAMMER_WINDUP_Y,
                          (u16)(t - HAMMER_CONTACT_HOLD),
                          (u16)(HAMMER_RECOIL_FRAMES - HAMMER_CONTACT_HOLD));
            frame = 5u;
        }
        brandHammerSetFrame(frame);
        SPR_setPosition(sHammer, HAMMER_X, y);
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
    /* Sprites do golpe sairam; reusa a VRAM de BG_A+logo+FX para os wordmarks. */
    SPR_reset();
    sVramAuthor   = sVramBgA;
    sVramProject  = sVramAuthor + img_logo_author_v2.tileset->numTile;
    sVramPresents = sVramProject + img_logo_project_v2.tileset->numTile;

    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_COLUMN);
    VDP_drawImageEx(BG_A, &img_logo_author_v2,
                    TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, FALSE, FALSE, FALSE,
                                   sVramAuthor),
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
                                       sVramProject),
                        6, 10, FALSE, TRUE);
    }

    if (f == BRAND_V2_PRESENTS_IN) {
        /* O presents vive no plano WINDOW: imovel enquanto a cortina move os
         * planos por baixo. O v1 e o v2 deixavam esse plano 100% ocioso. */
        VDP_setWindowVPos(FALSE, 22);
        VDP_drawImageEx(WINDOW, &img_presents_text_v2,
                        TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, FALSE, FALSE, FALSE,
                                       sVramPresents),
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
    sLogoDrawn = 0;
    sHazeArmed = 0;
    sHIntArmed = 0;
    sHIntReady = 0;
    memset(sShard, 0, sizeof(sShard));
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

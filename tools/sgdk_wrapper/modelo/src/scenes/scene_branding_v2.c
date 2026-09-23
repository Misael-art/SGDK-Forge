#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/branding_v2.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"

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

/* ---- Zonas de tela do storyboard (doc/act3_storyboard.md) --------------
 * PAREDE     y   0..64    wordmarks do ato 3; BG_A transparente
 * FORJA      y  64..200   bigorna e brasa; permanece a cena toda
 * ASSINATURA y 200..224   plano WINDOW; fogo travado + PRESENTS
 *
 * VSCROLL_COLUMN foi retirado: nao consegue levantar so a COIFA, move o fogo
 * e envolve o topo preto por baixo da bigorna. Wipe de palco em y>=64 apaga
 * o ferro — FORGE sai por restore do tilemap de props.
 */

/*
 * A bigorna em BG_A comeca em y=64. Qualquer wipe/clear nessa faixa apaga o
 * ferro. Os nomes do ato 3 vivem na parede (BG_A e transparente em y<64),
 * alinhados pela base em y=56 — um tijolo acima da bigorna.
 */
#define NAME_TX                 6
#define NAME_TY                 1      /* y 8   */
#define NAME_TW                28
#define NAME_TH                 7      /* y 8..64, nao toca a bigorna */
#define AUTHOR_TILE_X           8      /* 192px centrado em 320 */
#define AUTHOR_TILE_Y           3      /* base 24+32  = 56 */
#define AUTHOR_TW              24
#define AUTHOR_TH               4
#define PROJECT_TILE_X          6      /* 224px centrado em 320 */
#define PROJECT_TILE_Y          1      /* base  8+48  = 56 */
#define PROJECT_TW             28
#define PROJECT_TH              6
#define PRESENTS_TW            12
#define PRESENTS_TH             2

#define ACT3_FORGE_FADE_OUT   300      /* FORGE comeca a sair sob a cortina */
#define ACT3_AUTHOR_WIPE      318      /* varredura do FORGE, 1 fileira/quadro */
#define ACT3_AUTHOR_IN        330      /* MISAEL entra no palco vazio         */
#define ACT3_AUTHOR_FADE_OUT  420      /* MISAEL cede o palco                */
#define ACT3_PROJECT_WIPE     428      /* varredura do MISAEL, 1 fileira/quadro */
#define ACT3_PROJECT_IN       440      /* MASTER entra no palco vazio         */

/*
 * Limpeza e desenho ficam em quadros SEPARADOS de proposito. Juntos, o clear de
 * 280 tiles somado ao draw de 168 num unico quadro levou over_budget_frames de
 * 0 para 8 e o cpu_load de 96 para 104. Dividir o custo em dois quadros e a
 * correcao; a troca continua imperceptivel a 60fps.
 */

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
static u16 sVramStars, sVramBgB, sVramBgA, sVramLogo, sVramShard, sVramEmber, sVramHammer;
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
static u16  sShardSpawned;
static u16  sShardFailed;
static Sprite *sSpark[BRAND_V2_SPARK_COUNT];
static s16  sSparkX[BRAND_V2_SPARK_COUNT];
static s16  sSparkY[BRAND_V2_SPARK_COUNT];
static s16  sSparkVX[BRAND_V2_SPARK_COUNT];
static s16  sSparkVY[BRAND_V2_SPARK_COUNT];
static u8   sSparkKind[BRAND_V2_SPARK_COUNT];
static u8   sSparkOn[BRAND_V2_SPARK_COUNT];
static s16  sSkyScrollX;
static s16  sSkyScrollY;
static u8   sWallDrawn;
static u8   sHit2Done;
/*
 * Tilemaps da parede/logo descompactados no preludio. VDP_setTileMapEx em
 * IMAGE BEST desempacota o APLIB inteiro a cada chamada — F154/F155 mediram
 * o pico de cpu 160 / over_budget 9 na janela F151-F211. O probe ignora os
 * primeiros 90 quadros; o unpack vive la. Sem malloc: buffers estaticos.
 */
#define BRAND_MAP_CAP          (40 * 28)
#define BRAND_LOGO_MAP_CAP     ((LOGO_W / 8) * (LOGO_H / 8))
static u16 sMapB[BRAND_MAP_CAP];
static u16 sMapA[BRAND_MAP_CAP];
static u16 sMapLogo[BRAND_LOGO_MAP_CAP];
static TileMap sTmB;
static TileMap sTmA;
static TileMap sTmLogo;
static u8 sMapsReady;   /* bit0=B bit1=A bit2=logo */

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

static u16 brandNibble(u16 color, u16 shift)
{
    return (color >> shift) & 0x000E;
}

static u16 brandLerpColor(u16 from, u16 to, u16 num, u16 den)
{
    u16 r, g, b;

    if (den == 0) return to;
    r = brandNibble(from, 0) + (u16)(((s16)brandNibble(to, 0) - (s16)brandNibble(from, 0)) * (s16)num / (s16)den);
    g = brandNibble(from, 4) + (u16)(((s16)brandNibble(to, 4) - (s16)brandNibble(from, 4)) * (s16)num / (s16)den);
    b = brandNibble(from, 8) + (u16)(((s16)brandNibble(to, 8) - (s16)brandNibble(from, 8)) * (s16)num / (s16)den);
    return (u16)((r & 0x000E) | ((g & 0x000E) << 4) | ((b & 0x000E) << 8));
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

static void brandHammerLoadSlot(u8 frame)
{
    const u8 slot = (u8)(frame & 1u);
    const u16 base = sVramHammer + (slot * HAMMER_SLOT_TILES);
    const Animation *anim;

    if (sHammerSlotLoaded[slot] && sHammerSlotFrame[slot] == frame) return;
    anim = spr_forge_hammer.animations[0];
    if (frame >= anim->numFrame) return;
    VDP_loadTileSet(anim->frames[frame]->tileset, base, DMA_QUEUE);
    sHammerSlotLoaded[slot] = 1;
    sHammerSlotFrame[slot] = frame;
}

static void brandHammerSetFrame(u8 frame)
{
    const u8 slot = (u8)(frame & 1u);
    const u16 base = sVramHammer + (slot * HAMMER_SLOT_TILES);

    brandHammerLoadSlot(frame);
    SPR_setVRAMTileIndex(sHammer, (s16)base);
    SPR_setFrame(sHammer, frame);
    sHammerFrame = frame;
}

static u8 brandPrepMap(TileMap *dst, u16 *buf, u16 cap, const TileMap *src)
{
    const u32 cells = (u32)src->w * (u32)src->h;

    if (cells == 0 || cells > cap) return 0;
    dst->tilemap = buf;
    return (unpackTileMap(src, dst) != NULL) ? 1 : 0;
}

static void brandBakeMap(u16 *buf, u16 cells, u16 pal, u16 prio, u16 vram)
{
    u16 i;
    const u16 base = TILE_ATTR_FULL(pal, prio, FALSE, FALSE, vram);

    /* Assa paleta/prioridade/indice no preludio. O reveal usa
     * VDP_setTileMapDataRect (sem override por celula). */
    for (i = 0; i < cells; i++) buf[i] = (u16)(base + buf[i]);
}

static void brandUnpackNextMap(void)
{
    /* Um mapa por quadro: cada APLIB 40x28 foi o pico medido no display. */
    if (!(sMapsReady & 1u)) {
        if (brandPrepMap(&sTmB, sMapB, BRAND_MAP_CAP, img_forge_bg_b.tilemap)) {
            brandBakeMap(sMapB, (u16)((u32)sTmB.w * (u32)sTmB.h),
                         BRAND_V2_PAL_FORGE, FALSE, sVramBgB);
            sMapsReady |= 1u;
        }
        return;
    }
    if (!(sMapsReady & 2u)) {
        if (brandPrepMap(&sTmA, sMapA, BRAND_MAP_CAP, img_forge_bg_a_props.tilemap)) {
            brandBakeMap(sMapA, (u16)((u32)sTmA.w * (u32)sTmA.h),
                         BRAND_V2_PAL_FORGE, TRUE, sVramBgA);
            sMapsReady |= 2u;
        }
        return;
    }
    if (!(sMapsReady & 4u)) {
        if (brandPrepMap(&sTmLogo, sMapLogo, BRAND_LOGO_MAP_CAP,
                         img_logo_engine_v2.tilemap)) {
            brandBakeMap(sMapLogo, (u16)((u32)sTmLogo.w * (u32)sTmLogo.h),
                         BRAND_V2_PAL_METAL, TRUE, sVramLogo);
            sMapsReady |= 4u;
        }
    }
}

/* ---- Fagulhas: o fio condutor dos quatro atos -------------------------- */

static void brandSparkInit(void)
{
    u16 i;

    for (i = 0; i < BRAND_V2_SPARK_COUNT; i++) {
        sSparkKind[i] = (u8)(i & 1u);
        sSparkX[i] = (s16)((20 + (i * 23)) << 2);
        sSparkY[i] = (s16)((-24 - (s16)(i * 11)) << 2);
        if (sSparkKind[i]) {
            sSparkVX[i] = (s16)(((i & 3) - 1));
            sSparkVY[i] = (s16)(2 + (i & 3));
        } else {
            sSparkVX[i] = 0;
            sSparkVY[i] = 1;
        }
        sSparkOn[i] = 0;
        sSpark[i] = SPR_addSpriteEx(&spr_forge_ember, -32, -32,
                                    TILE_ATTR(BRAND_V2_PAL_FX, TRUE, FALSE, FALSE), 0);
        if (sSpark[i] != NULL) {
            SPR_setVRAMTileIndex(sSpark[i], (s16)sEmberFrameBase[0]);
            SPR_setAutoTileUpload(sSpark[i], FALSE);
            SPR_setVisibility(sSpark[i], HIDDEN);
        }
    }
}

static void brandSparkWake(u16 maxOn)
{
    u16 i;

    if (maxOn > BRAND_V2_SPARK_COUNT) maxOn = BRAND_V2_SPARK_COUNT;
    for (i = 0; i < maxOn; i++) {
        if (!sSparkOn[i] && sSpark[i] != NULL) {
            sSparkOn[i] = 1;
            SPR_setVisibility(sSpark[i], VISIBLE);
        }
    }
}

static void brandSparkKick(void)
{
    u16 i;

    for (i = 0; i < BRAND_V2_SPARK_COUNT; i++) {
        const u16 sector = (i * 5u) & 15u;
        sSparkOn[i] = 1;
        sSparkX[i] = (s16)(ANVIL_X << 2);
        sSparkY[i] = (s16)(ANVIL_Y << 2);
        sSparkVX[i] = (s16)((FAN_COS[sector] * 3) / 16);
        sSparkVY[i] = (s16)((FAN_SIN[sector] * 2) / 16) - 3;
        if (sSpark[i] != NULL) SPR_setVisibility(sSpark[i], VISIBLE);
    }
}

static void brandSparkConverge(u16 t, u16 dur)
{
    u16 i;

    if (dur == 0) dur = 1;
    for (i = 0; i < BRAND_V2_SPARK_COUNT; i++) {
        s16 tx, ty;
        brandShardTarget(i, &tx, &ty);
        sSparkX[i] = (s16)(brandLerp((s16)(sSparkX[i] >> 2), tx, t, dur) << 2);
        sSparkY[i] = (s16)(brandLerp((s16)(sSparkY[i] >> 2), ty, t, dur) << 2);
    }
}

static void brandSparkUpdate(u16 f, u8 mode)
{
    u16 i;

    for (i = 0; i < BRAND_V2_SPARK_COUNT; i++) {
        if (!sSparkOn[i] || sSpark[i] == NULL) continue;

        if (mode == 0) {
            /* preludio/descida: queda com ritmos diferentes */
            sSparkX[i] += sSparkVX[i];
            sSparkY[i] += sSparkVY[i];
            if ((sSparkY[i] >> 2) > 220) {
                sSparkY[i] = (s16)((-16 - (s16)(i * 3)) << 2);
                sSparkX[i] = (s16)((12 + ((i * 29 + f) & 255)) << 2);
            }
        } else if (mode == 1) {
            /* lock: pairar com respiracao */
            sSparkX[i] += (s16)(((f + i) & 8) ? 1 : -1);
            if (sSparkY[i] < (ANVIL_Y << 2)) sSparkY[i] += 1;
        } else if (mode == 2) {
            /* pos-impacto 1: explosao com peso */
            sSparkX[i] += sSparkVX[i];
            sSparkY[i] += sSparkVY[i];
            sSparkVY[i] += 1;
        }

        SPR_setPosition(sSpark[i], (s16)(sSparkX[i] >> 2), (s16)(sSparkY[i] >> 2));
        brandSetSharedFrame(sSpark[i], sEmberFrameBase, sEmberFrameCount,
                            sSparkKind[i] ? (u8)((f >> 2) & 3) : (u8)(4 + ((f >> 3) & 1)));
    }
}

/* ---- Ato I: preludio etereo -------------------------------------------- */

static void brandEnterIgnition(void)
{
    u16 i;

    SPR_reset();
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHilightShadow(FALSE);
    VDP_clearPlane(BG_A, TRUE);

    PAL_setPalette(BRAND_V2_PAL_FORGE, img_starfield_v2.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_METAL, img_logo_engine_v2.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_WORDMARK, img_logo_author_v2.palette->data, DMA);
    PAL_setPalette(BRAND_V2_PAL_FX, spr_forge_ember.palette->data, DMA);
    PAL_setColor(0, 0x0000);
    VDP_setBackgroundColor(0);

    sVramStars  = TILE_USER_INDEX;
    sVramBgB    = sVramStars + img_starfield_v2.tileset->numTile;
    sVramBgA    = sVramBgB + img_forge_bg_b.tileset->numTile;
    sVramLogo   = sVramBgA + img_forge_bg_a_props.tileset->numTile;
    sVramShard  = sVramLogo + img_logo_engine_v2.tileset->numTile;
    VDP_loadTileSet(img_logo_engine_v2.tileset, sVramLogo, DMA);
    sVramEmber  = brandLoadAnimFrames(&spr_forge_shard, sVramShard,
                                      sShardFrameBase, SHARD_FRAME_MAX,
                                      &sShardFrameCount);
    sVramHammer = brandLoadAnimFrames(&spr_forge_ember, sVramEmber,
                                      sEmberFrameBase, EMBER_FRAME_MAX,
                                      &sEmberFrameCount);

    VDP_loadTileSet(img_forge_bg_b.tileset, sVramBgB, DMA);
    VDP_loadTileSet(img_forge_bg_a_props.tileset, sVramBgA, DMA);
    VDP_drawImageEx(BG_B, &img_starfield_v2,
                    TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, FALSE, FALSE, FALSE, sVramStars),
                    0, 0, FALSE, TRUE);

    sEmber = NULL;
    for (i = 0; i < EMBER_GHOSTS; i++) sGhost[i] = NULL;
    sHammer = SPR_addSpriteEx(&spr_forge_hammer, HAMMER_X, HAMMER_WINDUP_Y,
                              TILE_ATTR(BRAND_V2_PAL_METAL, TRUE, FALSE, FALSE), 0);
    SPR_setAutoTileUpload(sHammer, FALSE);
    sHammerSlotLoaded[0] = 0;
    sHammerSlotLoaded[1] = 0;
    brandHammerSetFrame(0);
    SPR_setVisibility(sHammer, HIDDEN);

    sTrailHead = 0;
    sHammerFrame = 0;
    sSkyScrollX = 0;
    sSkyScrollY = 0;
    sWallDrawn = 0;
    sHit2Done = 0;
    sMapsReady = 0;
    brandSparkInit();
    AUDIO_startBrandBgm();
}

static void brandRevealWall(void)
{
    /* Quatro metades. Mapas assados no preludio: DataRect + DMA_QUEUE, sem
     * APLIB e sem override por celula. Fallback Empacotado continua 2 Ex. */
    if (sWallDrawn >= 4) return;

    if ((sMapsReady & 3u) == 3u) {
        if (sWallDrawn == 0) {
            VDP_setTileMapDataRect(BG_B, sMapB, 0, 0, 40, 14, 40, DMA_QUEUE);
        } else if (sWallDrawn == 1) {
            VDP_setTileMapDataRect(BG_B, sMapB + (14 * 40), 0, 14, 40, 14, 40, DMA_QUEUE);
            VDP_setVerticalScroll(BG_B, 0);
            VDP_setHorizontalScroll(BG_B, 0);
            sSkyScrollY = 0;
        } else if (sWallDrawn == 2) {
            VDP_setTileMapDataRect(BG_A, sMapA, 0, 0, 40, 14, 40, DMA_QUEUE);
        } else {
            VDP_setTileMapDataRect(BG_A, sMapA + (14 * 40), 0, 14, 40, 14, 40, DMA_QUEUE);
        }
        sWallDrawn++;
        return;
    }

    if (sWallDrawn == 0) {
        VDP_setTileMapEx(BG_B, img_forge_bg_b.tilemap,
                         TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, FALSE, FALSE, FALSE, sVramBgB),
                         0, 0, 0, 0, 40, 28, CPU);
        VDP_setVerticalScroll(BG_B, 0);
        VDP_setHorizontalScroll(BG_B, 0);
        sSkyScrollY = 0;
        sWallDrawn = 2;
        return;
    }
    if (sWallDrawn < 4) {
        VDP_setTileMapEx(BG_A, img_forge_bg_a_props.tilemap,
                         TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, TRUE, FALSE, FALSE, sVramBgA),
                         0, 0, 0, 0, 40, 28, CPU);
        sWallDrawn = 4;
    }
}

static void brandApplyForgeLight(u16 t, u16 span)
{
    u16 i;
    const u16 *hot = img_forge_bg_b.palette->data;

    if (span == 0) span = 1;
    if (t > span) t = span;
    for (i = 1; i < 16; i++) {
        PAL_setColor(i, brandLerpColor(0x0002, hot[i], t, span));
    }
    PAL_setColor(0, 0x0000);
}

static void brandUpdateIgnition(u16 f)
{
    /* Ato I: pulso organico + toque da criacao no mesmo quadro. */
    if (f < BRAND_V2_ACT_DESCENT_START) {
        if ((f & 7) == 0) {
            const u16 pulse = (u16)((f >> 3) & 3);
            static const u16 STAR[4] = { 0x0444, 0x0666, 0x0AAA, 0x0666 };
            PAL_setColor(1, STAR[pulse]);
            PAL_setColor(2, STAR[(pulse + 1) & 3]);
        }
        if (INPUT_held(BUTTON_LEFT))  sSkyScrollX -= 1;
        if (INPUT_held(BUTTON_RIGHT)) sSkyScrollX += 1;
        if (INPUT_held(BUTTON_UP))    sSkyScrollY -= 1;
        if (INPUT_held(BUTTON_DOWN))  sSkyScrollY += 1;
        if (sSkyScrollX > 24) sSkyScrollX = 24;
        if (sSkyScrollX < -24) sSkyScrollX = -24;
        if (sSkyScrollY > 16) sSkyScrollY = 16;
        if (sSkyScrollY < -16) sSkyScrollY = -16;
        VDP_setHorizontalScroll(BG_B, sSkyScrollX);
        VDP_setVerticalScroll(BG_B, sSkyScrollY);
        if ((f >= 8) && (f <= 10)) brandUnpackNextMap();
        /* Martelo oculto: quadro 1 no slot 1, quadro 2 no slot 0. */
        if (f == 12) brandHammerLoadSlot(1);
        if (f == 13) brandHammerLoadSlot(2);
        brandSparkWake((u16)(2 + (f / 16)));
        brandSparkUpdate(f, 0);
        return;
    }

    /* Ato II: gravidade. O ceu sai por VSCROLL; a paleta do ceu NAO vira
     * parede. A forja so acende depois do tilemap novo pousar. */
    if (f < BRAND_V2_ACT_LOCK_START) {
        const u16 t = f - BRAND_V2_ACT_DESCENT_START;
        const u16 span = BRAND_V2_ACT_LOCK_START - BRAND_V2_ACT_DESCENT_START;
        s16 fall;

        fall = (s16)(((s32)t * (s32)t * 168) / ((s32)span * (s32)span));
        if (sWallDrawn == 0) {
            VDP_setVerticalScroll(BG_B, (s16)(sSkyScrollY + fall));
            VDP_setHorizontalScroll(BG_B, sSkyScrollX);
        }
        if (f >= BRAND_V2_WALL_REVEAL) {
            brandRevealWall();
            brandApplyForgeLight((u16)(f - BRAND_V2_WALL_REVEAL),
                                 (u16)(BRAND_V2_ACT_LOCK_START - BRAND_V2_WALL_REVEAL));
        }
        brandSparkWake(BRAND_V2_SPARK_COUNT);
        brandSparkUpdate(f, 0);
        return;
    }

    /* Ato III: o mundo silencia. A bigorna respira. O martelo sobe. */
    {
        const u16 t = f - BRAND_V2_ACT_LOCK_START;
        s16 y;
        u8 frame;

        if (sWallDrawn < 4) brandRevealWall();
        VDP_setHorizontalScroll(BG_B, 0);
        VDP_setVerticalScroll(BG_B, 0);
        brandApplyForgeLight(64, 64);
        brandSparkUpdate(f, 1);

        SPR_setVisibility(sHammer, VISIBLE);
        if (t < 20) {
            y = brandLerp(HAMMER_CONTACT_Y - 8, HAMMER_WINDUP_Y, t, 20);
            frame = (t < 10) ? 1u : 2u;
        } else {
            y = brandLerp(HAMMER_WINDUP_Y, HAMMER_CONTACT_Y,
                          (u16)(t - 20),
                          (u16)(BRAND_V2_HIT1 - BRAND_V2_ACT_LOCK_START - 20));
            frame = 3u;
            /* Quadro 4 mora no slot 0; o 3 esta no slot 1. Prefetch agora
             * para o HIT1 nao descompactar FAST no mesmo quadro do slam. */
            if (t == 21) brandHammerLoadSlot(4);
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
    if (sShard[i] == NULL) {
        sShardFailed++;
        MDRuntimeProbe_noteSpriteAlloc(sShardSpawned, sShardFailed);
        return;
    }
    sShardSpawned++;
    MDRuntimeProbe_noteSpriteAlloc(sShardSpawned, sShardFailed);
    SPR_setVRAMTileIndex(sShard[i], (s16)sShardFrameBase[0]);
    SPR_setAutoTileUpload(sShard[i], FALSE);
}

static void brandPrepareShards(u16 base)
{
    u16 i;

    for (i = 0; i < SHARD_COUNT; i++) {
        const u16 row = i / SHARD_COLS;
        sShard[i] = NULL;
        sShardLanded[i] = 0;
        sShardBorn[i] = (u16)(base + (i / SHARD_SPAWN_PER_FRAME));
        sShardConv[i] = (u16)(sShardBorn[i] + 12 + (row * SHARD_ROW_STAGGER));
        sShardDur[i] = (u16)(20 + (i % 7));
        sShardRecip[i] = (u16)(65535u / ((u32)sShardDur[i] * (u32)sShardDur[i]));
        brandShardExplodePos(i, 16, &sShardEX[i], &sShardEY[i]);
        brandShardTarget(i, &sShardTX[i], &sShardTY[i]);
    }
}

static void brandEnterStrike(void)
{
    /* 1o golpe: a materia. O mundo reage; o nome ainda nao existe. */
    sShardSpawned = 0;
    sShardFailed = 0;
    MDRuntimeProbe_noteSpriteAlloc(0, 0);
    sShakeLeft = 10;
    sHit2Done = 0;
    brandSparkKick();
    /* Poeira dos seculos: tijolo estoura de luz um instante. */
    PAL_setColor(4, 0x068A);
    PAL_setColor(5, 0x08AC);
    PAL_setColor(15, 0x0AAA);
    AUDIO_playCue(AUDIO_CUE_BRAND_HAMMER_SLAM);
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
        const u16 *hot = img_forge_bg_b.palette->data;
        for (i = 0; i < BRAND_V2_EMBER_CYCLE_COUNT; i++)
            PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST + i, EMBER_CYCLE[i]);
        PAL_setColor(4, hot[4]);
        PAL_setColor(5, hot[5]);
        PAL_setColor(15, hot[15]);
    }

    if (sShakeLeft) {
        static const s16 SHAKE[10] = { 7, 5, 4, 3, 3, 2, 2, 1, 1, 0 };
        const s16 dy = SHAKE[10 - sShakeLeft];
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

    /* Tiles ja residentes. Mapa assado no preludio: DataRect sem override. */
    if (sMapsReady & 4u) {
        VDP_setTileMapDataRect(BG_A, sMapLogo,
                               LOGO_X0 / 8, LOGO_Y0 / 8,
                               LOGO_W / 8, LOGO_H / 8, sTmLogo.w, DMA_QUEUE);
    } else {
        VDP_setTileMapEx(BG_A, img_logo_engine_v2.tilemap,
                         TILE_ATTR_FULL(BRAND_V2_PAL_METAL, TRUE, FALSE, FALSE, sVramLogo),
                         LOGO_X0 / 8, LOGO_Y0 / 8,
                         0, 0, LOGO_W / 8, LOGO_H / 8, CPU);
    }
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
    const u16 t = f - BRAND_V2_HIT1;

    brandStrikeFlashAndShake(t);

    if (f < BRAND_V2_HIT2) {
        /* Recuo do 1o golpe, depois o martelo sobe de novo. */
        if (t < HAMMER_CONTACT_HOLD) {
            brandHammerSetFrame(4);
            SPR_setPosition(sHammer, HAMMER_X, HAMMER_CONTACT_Y);
        } else if (t < 40) {
            brandHammerSetFrame(5);
            SPR_setPosition(sHammer, HAMMER_X,
                            brandLerp(HAMMER_CONTACT_Y, HAMMER_WINDUP_Y,
                                      (u16)(t - HAMMER_CONTACT_HOLD), 24));
        } else {
            const u16 w = (u16)(t - 40);
            const u16 span = (u16)(BRAND_V2_HIT2 - BRAND_V2_HIT1 - 40);
            brandHammerSetFrame(3);
            SPR_setPosition(sHammer, HAMMER_X,
                            brandLerp(HAMMER_WINDUP_Y, HAMMER_CONTACT_Y, w, span));
        }
        brandSparkUpdate(f, 2);
        return;
    }

    /* 2o golpe: a identidade. As mesmas fagulhas voltam para o nome. */
    if (!sHit2Done) {
        u16 i;
        sHit2Done = 1;
        sShakeLeft = 12;
        AUDIO_playCue(AUDIO_CUE_BRAND_HAMMER_SLAM);
        sShakeLeft = 10;
        /* Sem enxame de 56 estilhacos: F331 mediu over_budget 20. As fagulhas
         * do preludio e que forjam o nome. */
        for (i = 0; i < BRAND_V2_SPARK_COUNT; i++) {
            sSparkVX[i] = 0;
            sSparkVY[i] = 0;
        }
    }

    if (f < BRAND_V2_HIT2 + HAMMER_CONTACT_HOLD) {
        brandHammerSetFrame(4);
        SPR_setPosition(sHammer, HAMMER_X, HAMMER_CONTACT_Y);
    } else if (f < BRAND_V2_HIT2 + HAMMER_RECOIL_FRAMES) {
        brandHammerSetFrame(5);
        SPR_setPosition(sHammer, HAMMER_X,
                        brandLerp(HAMMER_CONTACT_Y, HAMMER_WINDUP_Y,
                                  (u16)(f - BRAND_V2_HIT2 - HAMMER_CONTACT_HOLD),
                                  (u16)(HAMMER_RECOIL_FRAMES - HAMMER_CONTACT_HOLD)));
    } else {
        SPR_setVisibility(sHammer, HIDDEN);
    }

    if (f < BRAND_V2_LOGO_LOCK) {
        brandSparkConverge((u16)(f - BRAND_V2_HIT2),
                           (u16)(BRAND_V2_LOGO_LOCK - BRAND_V2_HIT2));
        brandSparkUpdate(f, 3);
    } else {
        u16 i;
        brandSpecularSweep((u16)(f - BRAND_V2_LOGO_LOCK));
        for (i = 0; i < BRAND_V2_SPARK_COUNT; i++) {
            if (sSpark[i] != NULL) SPR_setVisibility(sSpark[i], HIDDEN);
        }
        if ((f & 7) == 0) {
            u16 c;
            for (c = 0; c < BRAND_V2_EMBER_CYCLE_COUNT; c++) {
                PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST + c,
                             EMBER_CYCLE[(c + (f >> 3)) & 3]);
            }
        }
    }
}

/* ---- Ato 3: assinatura ------------------------------------------------- */

/*
 * FORGE sai restaurando o tilemap original de BG_A numa unica chamada.
 *
 * Uma fileira por quadro descompactava o APLIB inteiro de props 8 vezes
 * (F331: cpu 196, over_budget 10). Uma chamada so descompacta uma vez.
 */
static void brandRestoreForge(void)
{
    VDP_setTileMapEx(BG_A, img_forge_bg_a_props.tilemap,
                     TILE_ATTR_FULL(BRAND_V2_PAL_FORGE, TRUE, FALSE, FALSE, sVramBgA),
                     LOGO_X0 / 8, LOGO_Y0 / 8,
                     LOGO_X0 / 8, LOGO_Y0 / 8,
                     LOGO_W / 8, LOGO_H / 8, CPU);
}

/*
 * Nomes do ato 3 vivem em y<64, onde BG_A e transparente. Limpar essa faixa
 * so revela a parede em BG_B. Nao desce ate a bigorna.
 */
static void brandWipeNameRow(u16 step)
{
    if (step < NAME_TH) {
        VDP_clearTileMapRect(BG_A, NAME_TX, (u16)(NAME_TY + step), NAME_TW, 1);
    }
}

static void brandForgeBreathe(u16 f)
{
    /* Sem haze de linha no ato 3: HSCROLL_LINE + unpack de tilemap no mesmo
     * quadro encheu a fila (F331/F451: over_budget 17, cpu 201) e o carimbo
     * do MASTER nao chegou a pousar. A brasa continua pela CRAM. */
    if ((f & 7) == 0) {
        u16 i;
        for (i = 0; i < BRAND_V2_EMBER_CYCLE_COUNT; i++) {
            PAL_setColor(BRAND_V2_EMBER_CYCLE_FIRST + i,
                         EMBER_CYCLE[(i + (f >> 3)) & (BRAND_V2_EMBER_CYCLE_COUNT - 1)]);
        }
    }
}

static void brandWordmarkPulse(u16 f)
{
    /* PAL2[8,9,12]: ouro dos nomes e do PRESENTS. Ciclo curto, sem varrer CRAM. */
    static const u16 GOLD8[4]  = { 0x0088, 0x00AA, 0x00CC, 0x00AA };
    static const u16 GOLD9[4]  = { 0x00AA, 0x00CC, 0x00EE, 0x00CC };
    static const u16 GOLD12[4] = { 0x00CE, 0x00EE, 0x0AEE, 0x00EE };
    const u16 ph = (f >> 3) & 3u;

    if ((f & 7) != 0) return;
    PAL_setColor((BRAND_V2_PAL_WORDMARK * 16) + 8,  GOLD8[ph]);
    PAL_setColor((BRAND_V2_PAL_WORDMARK * 16) + 9,  GOLD9[ph]);
    PAL_setColor((BRAND_V2_PAL_WORDMARK * 16) + 12, GOLD12[ph]);
}

static void brandEnterSignature(void)
{
    /* Sprites do golpe saem. Wordmarks NAO reusam sVramBgA: o tilemap da
     * bigorna continua vivo e apontando para esses tiles. Bisseccao ato 3
     * ponto 6 (out/evidence/bis_6) restaurou a bigorna; pontos 1-5 nao. */
    SPR_reset();
    sVramAuthor   = sVramHammer + (HAMMER_WINDOW_SLOTS * HAMMER_SLOT_TILES);
    sVramProject  = sVramAuthor + img_logo_author_v2.tileset->numTile;
    sVramPresents = sVramProject + img_logo_project_v2.tileset->numTile;
    VDP_loadTileSet(img_logo_author_v2.tileset, sVramAuthor, DMA);
    VDP_loadTileSet(img_logo_project_v2.tileset, sVramProject, DMA);
    VDP_loadTileSet(img_presents_text_v2.tileset, sVramPresents, DMA);

    /* Sem VSCROLL_COLUMN e sem HSCROLL_LINE: a cortina de coluna corta a
     * bigorna; a haze de linha no ato 3 compete com o carimbo dos nomes. */
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    sHazeArmed = 0;
}

static void brandUpdateSignature(u16 f)
{
    brandForgeBreathe(f);
    if (f >= ACT3_AUTHOR_IN) brandWordmarkPulse(f);

    /* FORGE cede o palco restaurando a bigorna, nao abrindo um buraco. */
    if (f == ACT3_AUTHOR_WIPE) {
        brandRestoreForge();
    }

    if (f == ACT3_AUTHOR_IN) {
        /* CPU: o carimbo tem de pousar neste quadro, nao na fila. */
        VDP_setTileMapEx(BG_A, img_logo_author_v2.tilemap,
                         TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, TRUE, FALSE, FALSE,
                                        sVramAuthor),
                         AUTHOR_TILE_X, AUTHOR_TILE_Y,
                         0, 0, AUTHOR_TW, AUTHOR_TH, CPU);
        AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_BELL);
    }

    if (f >= ACT3_PROJECT_WIPE && f < ACT3_PROJECT_IN) {
        brandWipeNameRow((u16)(f - ACT3_PROJECT_WIPE));
    }

    if (f == ACT3_PROJECT_IN) {
        VDP_setTileMapEx(BG_A, img_logo_project_v2.tilemap,
                         TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, TRUE, FALSE, FALSE,
                                        sVramProject),
                         PROJECT_TILE_X, PROJECT_TILE_Y,
                         0, 0, PROJECT_TW, PROJECT_TH, CPU);
        AUDIO_playCue(AUDIO_CUE_BRAND_PROJECT_WHOOSH);
    }

    if (f == BRAND_V2_PRESENTS_IN) {
        /* Sem WINDOW: unpack do tilemap cheio de BG_B na WINDOW apagou o
         * MASTER em F511. O fogo ja esta em BG_B; BG_A e transparente
         * abaixo da bigorna (y>=210). O ouro pousa em cima do piso. */
        VDP_setWindowOff();
        VDP_setTileMapEx(BG_A, img_presents_text_v2.tilemap,
                         TILE_ATTR_FULL(BRAND_V2_PAL_WORDMARK, TRUE, FALSE, FALSE,
                                        sVramPresents),
                         14, 26, 0, 0, PRESENTS_TW, PRESENTS_TH, CPU);
        AUDIO_playCue(AUDIO_CUE_BRAND_PROJECT_TAIL);
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
    sShardSpawned = 0;
    sShardFailed = 0;
    sWallDrawn = 0;
    sHit2Done = 0;
    sMapsReady = 0;
    sSkyScrollX = 0;
    sSkyScrollY = 0;
    memset(sSpark, 0, sizeof(sSpark));
    MDRuntimeProbe_noteSpriteAlloc(0, 0);
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
    VDP_setWindowOff();
    VDP_setTextPlane(BG_A);
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
}

void SCENE_brandingV2Update(void)
{
    const u16 f = gApp.sceneFrames;

    /* START salta. A no preludio e o toque da criacao, nao skip. */
    if (INPUT_pressed(BUTTON_START)) {
        SCENE_brandingV2Exit();
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (f < BRAND_V2_HIT1) {
        if (sAct != 0) { sAct = 0; brandEnterIgnition(); }
        brandUpdateIgnition(f);
    } else if (f < BRAND_V2_END) {
        if (sAct != 1) { sAct = 1; brandEnterStrike(); }
        brandUpdateStrike(f);
    } else {
        SCENE_brandingV2Exit();
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    SPR_update();
}

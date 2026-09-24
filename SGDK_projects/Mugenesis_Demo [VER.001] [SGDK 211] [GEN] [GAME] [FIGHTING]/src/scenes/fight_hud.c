/* fight_hud.c -- HUD de luta (P4) do Mugenesis_Demo.
 *
 * Contrato: doc/hud/p4_hud_contract.md. Arte: SFA2 Lifebars (Chok) convertida por convert-hud;
 * retrato 9000,0 do personagem. Transporte: tiles no plano WINDOW (linhas 0..6) -- sprites no topo
 * estourariam 20/linha quando o lutador pula (7,4% dos ticks). Mensagens (ROUND/FIGHT/KO) = sprites.
 * Paleta: PAL0 slots 9..15 (estagio fica com 1..8). Barra estilo Street Fighter com fantasma de dano.
 * Especial (REGRA 2, estilo SSF2T): barra compacta de 1/3 da vida, centrada no RODAPE, em BG_A
 * (linha 26 = y 208..215). O WINDOW so pode ocupar o topo OU a base; a vida fica no topo. Com
 * cenario (E4) essa linha de BG_A precisa de scroll 0 (line scroll): contrato do palco.
 * Tudo por evento: so reescreve tiles cujo conteudo mudou.
 */
#include <genesis.h>

#include "mg/mg_runtime.h"
#include "mg_gen/hud_gen.h"
#include "scenes/fight_hud.h"

#define WROWS        7                 /* altura do WINDOW em tiles */
#define BAR_TILES    14
#define BAR_PX       (BAR_TILES * 8)
#define POW_TILES    5                 /* 1/3 de BAR_TILES (14/3 = 4,67 -> 5) */
#define POW_PX       (POW_TILES * 8)
#define POW_ROW      26                /* BG_A, y 208..215: abaixo do chao (200) e da sombra */
#define POW_P1_X     18                /* P1 cresce para a esquerda a partir daqui; P2 espelhado */
#define POW_P2_X     21                /* folga de 2 tiles no centro (x 19..20) */
#define GHOST_HOLD   30                /* ticks antes do fantasma comecar a drenar */
#define GHOST_SPEED  2                 /* px por tick */
#define COMBO_SHOW   90

static u16 sBase, sFace[2];
static u8 sLifePx[2], sGhostPx[2], sPowPx[2];
static u8 sGhostHold[2];
static u16 sTileCache[2][2][BAR_TILES];   /* [lado][0=vida,1=especial][tile] */
static s16 sLastTime, sLastWins[2], sLastCombo[2];
static u8 sHidden;
static s8 sMsg;                            /* mensagem visivel (-1 nenhuma) */
static Sprite *sMsgSpr[MG_HUD_MSG_PARTS];

static inline u16 attr(u16 idx, bool hflip) { return TILE_ATTR_FULL(PAL0, TRUE, FALSE, hflip, sBase + idx); }

static void putTile(u16 x, u16 y, u16 a) { VDP_setTileMapXY(WINDOW, a, x, y); }
static void putPow(u16 x, u16 a) { VDP_setTileMapXY(BG_A, a, x, POW_ROW); }

static void put2x2(u16 x, u16 y, u16 first)
{
    putTile(x, y, attr(first, FALSE));
    putTile(x + 1, y, attr(first + 1, FALSE));
    putTile(x, y + 1, attr(first + 2, FALSE));
    putTile(x + 1, y + 1, attr(first + 3, FALSE));
}

/* tile da barra de vida para o tile c (0 = junto ao centro) dados vida L e fantasma G em px */
static u16 lifeTile(u8 c, u8 L, u8 G)
{
    s16 lo = c * 8;
    s16 nl = L - lo; if (nl < 0) nl = 0; if (nl > 8) nl = 8;
    s16 ng = G - lo; if (ng < 0) ng = 0; if (ng > 8) ng = 8;
    if (nl == 8) return MG_HUD_T_BAR_LG + 8;
    if (nl > 0) return (ng == 8) ? MG_HUD_T_BAR_LG + nl : MG_HUD_T_BAR_LE + nl;
    return MG_HUD_T_BAR_GE + ng;
}

static u8 sLastL[2][2], sLastG[2][2];     /* ultimo desenho de cada barra (0xFF = forcar) */

/* So percorre os tiles entre a borda antiga e a nova: sem mudanca, custo zero (68000: laco e caro). */
static void drawBar(u8 side, u8 kind, u8 L, u8 G)
{
    u8 oL = sLastL[side][kind], oG = sLastG[side][kind];
    if (L == oL && G == oG) return;
    const u8 n = kind ? POW_TILES : BAR_TILES;
    u8 c0 = 0, c1 = n - 1;
    if (oL != 0xFF) {
        u8 lo = L, hi = L;
        if (oL < lo) lo = oL;
        if (oL > hi) hi = oL;
        if (!kind) {
            if (G < lo) lo = G;
            if (G > hi) hi = G;
            if (oG < lo) lo = oG;
            if (oG > hi) hi = oG;
        }
        c0 = lo >> 3;
        c1 = (hi >> 3) < n ? (hi >> 3) : n - 1;
    }
    sLastL[side][kind] = L;
    sLastG[side][kind] = G;
    for (u8 c = c0; c <= c1; c++) {
        u16 t;
        if (kind) {
            s16 n = L - c * 8; if (n < 0) n = 0; if (n > 8) n = 8;
            t = MG_HUD_T_BAR_SE + n;
        } else t = lifeTile(c, L, G);
        if (sTileCache[side][kind][c] == t) continue;
        sTileCache[side][kind][c] = t;
        if (kind) {                            /* especial: rodape, BG_A */
            if (side == 0) putPow(POW_P1_X - c, attr(t, FALSE));
            else putPow(POW_P2_X + c, attr(t, TRUE));
        } else if (side == 0) putTile(17 - c, 1, attr(t, FALSE));   /* vida: centro x 17, cresce p/ esquerda */
        else putTile(22 + c, 1, attr(t, TRUE));                      /* P2: centro x 22, espelhado */
    }
}

static void clearWindow(void)
{
    VDP_clearTileMapRect(WINDOW, 0, 0, 40, WROWS);
    VDP_clearTileMapRect(BG_A, POW_P1_X - POW_TILES + 1, POW_ROW, POW_P2_X + POW_TILES - (POW_P1_X - POW_TILES + 1), 1);
}

static void drawStatic(void)
{
    for (u8 s = 0; s < 2; s++) {
        const MgCharDef *d = mg_fight.p[s].def;
        if (!d->portrait || !sFace[s]) continue;
        for (u8 ty = 0; ty < 4; ty++)
            for (u8 tx = 0; tx < 4; tx++) {
                u16 i = sFace[s] + ty * 4 + tx;
                if (s == 0) putTile(tx, ty, TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, i));
                else putTile(39 - tx, ty, TILE_ATTR_FULL(PAL2, TRUE, FALSE, TRUE, i));
            }
    }
    memset(sTileCache, 0xFF, sizeof(sTileCache));
    memset(sLastL, 0xFF, sizeof(sLastL));
    memset(sLastG, 0xFF, sizeof(sLastG));
    sLastTime = sLastWins[0] = sLastWins[1] = sLastCombo[0] = sLastCombo[1] = -1;
}

static void showMsg(s8 m)
{
    if (m == sMsg) return;
    for (u8 k = 0; k < MG_HUD_MSG_PARTS; k++)
        if (sMsgSpr[k]) { SPR_releaseSprite(sMsgSpr[k]); sMsgSpr[k] = 0; }
    sMsg = m;
    if (m < 0) return;
    const MgHudMsg *msg = &mg_hud_msgs[(u8)m];
    u16 total = 0;
    for (u8 k = 0; k < msg->nparts; k++) total += msg->w[k];
    s16 x = 160 - total / 2, y = 96 - msg->h / 2;
    for (u8 k = 0; k < msg->nparts; k++) {
        sMsgSpr[k] = SPR_addSpriteEx(msg->def[k], x, y, TILE_ATTR(PAL0, TRUE, FALSE, FALSE),
                                     SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
        if (sMsgSpr[k]) SPR_setDepth(sMsgSpr[k], SPR_MIN_DEPTH);
        x += msg->w[k];
    }
}

void FIGHT_HUD_init(void)
{
    sBase = MG_fightVramNext();
    VDP_loadTileSet(&mg_hud_tiles, sBase, DMA);
    u16 next = sBase + mg_hud_tiles.numTile;
    for (u8 s = 0; s < 2; s++) {
        const MgCharDef *d = mg_fight.p[s].def;
        sFace[s] = 0;
        if (!d->portrait) continue;
        if (s == 1 && mg_fight.p[1].def == mg_fight.p[0].def) { sFace[1] = sFace[0]; continue; }
        VDP_loadTileSet(d->portrait, next, DMA);
        sFace[s] = next;
        next += d->portrait->numTile;
    }
    PAL_setColors(MG_HUD_FIRST_SLOT, &mg_hud_pal[MG_HUD_FIRST_SLOT], 16 - MG_HUD_FIRST_SLOT, DMA);
    VDP_setWindowVPos(FALSE, WROWS);
    clearWindow();
    sMsg = -1;
    for (u8 k = 0; k < MG_HUD_MSG_PARTS; k++) sMsgSpr[k] = 0;
    for (u8 s = 0; s < 2; s++) { sLifePx[s] = sGhostPx[s] = BAR_PX; sPowPx[s] = 0; sGhostHold[s] = 0; }
    sHidden = 0;
    drawStatic();
}

void FIGHT_HUD_update(void)
{
    /* fundo de super em tela cheia: HUD some (o personagem declara nobardisplay) */
    if (mg_fight.bgfx_active) {
        if (!sHidden) { clearWindow(); showMsg(-1); sHidden = 1; }
        return;
    }
    if (sHidden) { sHidden = 0; drawStatic(); }

    for (u8 s = 0; s < 2; s++) {
        const MgPlayer *p = &mg_fight.p[s];
        static s32 lastLife[2] = { -1, -1 }, lastPow[2] = { -1, -1 };
        static u8 cacheL[2], cacheP[2];
        s32 life = p->life < 0 ? 0 : p->life;
        if (life != lastLife[s]) {
            s32 maxl = p->def->consts->life >> MG_FX_SHIFT;
            lastLife[s] = life;
            cacheL[s] = maxl ? (u8)(life * BAR_PX / maxl) : 0;
        }
        u8 L = cacheL[s];
        if (L < sLifePx[s]) sGhostHold[s] = GHOST_HOLD;          /* dano novo: fantasma segura */
        if (L > sGhostPx[s]) sGhostPx[s] = L;                    /* recuperou (novo round) */
        sLifePx[s] = L;
        if (sGhostHold[s]) sGhostHold[s]--;
        else if (sGhostPx[s] > L) sGhostPx[s] = (sGhostPx[s] - L > GHOST_SPEED) ? sGhostPx[s] - GHOST_SPEED : L;
        drawBar(s, 0, sLifePx[s], sGhostPx[s]);
        if (p->power != lastPow[s]) {
            lastPow[s] = p->power;
            cacheP[s] = (u8)((p->power > 3000 ? 3000 : p->power) * POW_PX / 3000);
        }
        sPowPx[s] = cacheP[s];
        drawBar(s, 1, sPowPx[s], 0);

        /* vitorias: icone por round ganho */
        if (mg_fight.wins[s] != sLastWins[s]) {
            sLastWins[s] = mg_fight.wins[s];
            for (u8 w = 0; w < 2; w++) {
                u16 x = s ? 34 - w * 2 : 4 + w * 2;
                if (w < mg_fight.wins[s]) put2x2(x, 4, MG_HUD_T_WIN);
                else VDP_clearTileMapRect(WINDOW, x, 4, 2, 2);
            }
        }
        /* combo: "N HITS" junto a barra de quem esta combando, por COMBO_SHOW ticks */
        s16 c = (mg_fight.combo[s] >= 2 && mg_fight.ticks - mg_fight.combo_tick[s] < COMBO_SHOW) ? mg_fight.combo[s] : 0;
        if (c != sLastCombo[s]) {
            sLastCombo[s] = c;
            u16 x0 = s ? 26 : 4;
            VDP_clearTileMapRect(WINDOW, x0, 5, 10, 2);
            if (c) {
                u16 x = x0;
                if (c >= 10) { put2x2(x, 5, MG_HUD_T_COMBO_0 + (c / 10 % 10) * 4); x += 2; }
                put2x2(x, 5, MG_HUD_T_COMBO_0 + (c % 10) * 4); x += 2;
                put2x2(x, 5, MG_HUD_T_COMBO_H); put2x2(x + 2, 5, MG_HUD_T_COMBO_I);
                put2x2(x + 4, 5, MG_HUD_T_COMBO_T); put2x2(x + 6, 5, MG_HUD_T_COMBO_S);
            }
        }
    }
    /* tempo */
    s16 t = mg_fight.round_state == 1 ? mg_fight.round_timer / 60 : (mg_fight.round_state == 0 ? 99 : sLastTime);
    if (t > 99) t = 99;
    if (t < 0) t = 0;
    if (t != sLastTime) {
        sLastTime = t;
        put2x2(18, 0, MG_HUD_T_TIME_0 + (t / 10) * 4);
        put2x2(20, 0, MG_HUD_T_TIME_0 + (t % 10) * 4);
    }
    /* mensagens: ROUND n -> FIGHT! na intro; K.O./TIME OVER/DRAW no fim */
    s8 m = -1;
    if (mg_fight.round_state == 0) {
        u8 r = mg_fight.round_no > 3 ? 3 : (mg_fight.round_no < 1 ? 1 : mg_fight.round_no);
        m = mg_fight.round_timer > 40 ? (MG_HUD_MSG_ROUND1 + r - 1) : MG_HUD_MSG_FIGHT;
    } else if (mg_fight.round_state == 2 && mg_fight.round_timer > 60) {
        const MgPlayer *a = &mg_fight.p[0], *b = &mg_fight.p[1];
        if (a->life <= 0 && b->life <= 0) m = MG_HUD_MSG_DOUBLEKO;
        else if (a->life <= 0 || b->life <= 0) m = MG_HUD_MSG_KO;
        else if (a->life == b->life) m = MG_HUD_MSG_DRAW;
        else m = MG_HUD_MSG_TIMEOVER;
    }
    showMsg(m);
}

#ifndef BRANDING_V2_H
#define BRANDING_V2_H

#include <genesis.h>

/*
 * Fundamento da abertura de assinatura v2 — contrato branding_sequence_v2.
 *
 * Autoridade: doc/branding_sequence_contract.json. Se este header divergir do
 * contrato, o contrato ganha.
 *
 * ESTADO: documentado. Nada aqui esta implementado e nenhum dos 8 assets do
 * ato existe ainda. Os simbolos brand_* atuais sao placeholders desenhados por
 * primitiva e nunca podem ser promovidos a final.
 *
 * O v1 media over_budget_frames=1 com ZERO sprites, nenhum H-Int e duas
 * paletas ociosas. A causa provavel e o upload da tabela de HScroll por CPU
 * mais os VDP_drawImageEx no caminho de troca de fase. O v2 nao tem trocas de
 * fase (tomada continua) e envia a tabela por DMA no VBlank. Corrigir esse
 * spike e o passo 1 da ordem de implementacao.
 */

/* ---- Linha do tempo (NTSC, 60fps) ------------------------------------- */

#define BRAND_V2_ACT_IGNITION_START     0
#define BRAND_V2_ACT_STRIKE_START     120   /* impacto do martelo            */
#define BRAND_V2_ACT_SIGNATURE_START  300   /* cortina por coluna            */
#define BRAND_V2_END                  520   /* handoff por fade de paleta    */

#define BRAND_V2_EMBER_FALL_START       8
#define BRAND_V2_EMBER_FALL_END        96
#define BRAND_V2_FLASH_FRAMES           2   /* CRAM masked, evita CRAM dots  */
#define BRAND_V2_SHARD_SWARM_START    122
#define BRAND_V2_LOGO_LOCK            180   /* sprite -> tilemap             */
#define BRAND_V2_CURTAIN_END          360
#define BRAND_V2_PRESENTS_IN          480

/* ---- Orcamento declarado (measurement_level: estimated) ---------------- */

#define BRAND_V2_HINT_BANDS             7   /* bandas de paleta no ato 1     */
#define BRAND_V2_SHARD_COUNT           32   /* pico total de sprites         */
#define BRAND_V2_SHARD_PEAK_SCANLINE   12   /* limite fisico do VDP e 20     */
#define BRAND_V2_HAZE_SCANLINES        48   /* faixa inferior de ar quente   */
#define BRAND_V2_HAZE_AMP_START         6
#define BRAND_V2_HAZE_AMP_END           1

/*
 * Claim de scanline NUNCA pode vir de SPR_getUsedVDPSprite(): esse valor e uso
 * total de sprites VDP, nao pressao por linha. O numero acima e estimativa de
 * construcao e exige tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py
 * antes de qualquer promocao.
 */

/* ---- Posse de paleta (index 0 transparente, 15 visiveis por paleta) ---- */

#define BRAND_V2_PAL_FORGE    PAL0  /* ambiente; ciclagem de CRAM em 9..12  */
#define BRAND_V2_PAL_METAL    PAL1  /* logo engine; folga de highlight 13,14 */
#define BRAND_V2_PAL_WORDMARK PAL2  /* autor, projeto, presents             */
#define BRAND_V2_PAL_FX       PAL3  /* brasa, estilhaco, FX                 */

#define BRAND_V2_EMBER_CYCLE_FIRST      9
#define BRAND_V2_EMBER_CYCLE_COUNT      4
#define BRAND_V2_HIGHLIGHT_HEADROOM_LO 13
#define BRAND_V2_HIGHLIGHT_HEADROOM_HI 14

/*
 * shadow_highlight_slot_rule: os indices de folga acima ficam abaixo do maximo
 * na rampa autoral, senao o operador de highlight nao tem para onde clarear e a
 * varredura especular do ato 2 desaparece.
 */

/* ---- Ciclo de vida ----------------------------------------------------- */

void SCENE_brandingV2Enter(void);   /* adquire o H-Int, carrega o ato 1     */
void SCENE_brandingV2Update(void);  /* uma chamada por quadro               */
void SCENE_brandingV2Exit(void);    /* LIBERA o H-Int, entrega por fade     */

/*
 * h_int_ownership_map: scene_branding e owner UNICO do H-Int enquanto a cena
 * estiver ativa. Nenhum outro modulo pode registrar handler nesse intervalo, e
 * SCENE_brandingV2Exit precisa liberar. Violacao e blocker formal.
 */

/* ---- Regras que o runtime nao pode quebrar ---------------------------- */

/*
 * - nenhum VDP_drawText/VDP_drawTextBG em conteudo de marca: autor, projeto e
 *   "presents" sao assets de pixel art; o cursor de maquina de escrever do v1
 *   esta proibido;
 * - nenhum VDP_clearPlane entre atos: a abertura e uma tomada continua e a
 *   transicao e feita por luz, scroll e paleta;
 * - nenhum pixel de tile escrito como literal const u32 em C;
 * - DMA apenas no VBlank;
 * - sem float/double, sem malloc/free.
 */

#endif /* BRANDING_V2_H */

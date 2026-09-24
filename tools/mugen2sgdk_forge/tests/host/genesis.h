/* Stub minimo do SGDK para rodar o runtime mg_* no host (testes e profiling). Nao e o SGDK. */
#ifndef HOST_GENESIS_STUB_H
#define HOST_GENESIS_STUB_H
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t u8; typedef int8_t s8; typedef uint16_t u16; typedef int16_t s16;
typedef uint32_t u32; typedef int32_t s32; typedef u8 bool;
#define TRUE 1
#define FALSE 0
typedef struct { u16 id; u16 maxNumTile; } SpriteDefinition;
#define TILE_USER_INDEX 16
#define TILE_SPRITE_INDEX 1100
#define TILE_ATTR_FULL(p, pr, v, h, i) (TILE_ATTR(p, pr, v, h) | (i))
#define TILE_INDEX_MASK 0x7FF
typedef struct { const SpriteDefinition *def; s16 x, y; u16 frame; u8 visible; u16 attr, flags; } Sprite;
typedef enum { HIDDEN, VISIBLE, AUTO_FAST, AUTO_SLOW } SpriteVisibility;
typedef enum { SOUND_PCM_CH_AUTO = -1, SOUND_PCM_CH1, SOUND_PCM_CH2, SOUND_PCM_CH3 } SoundPCMChannel;
typedef enum { CPU, DMA, DMA_QUEUE } TransferMethod;
typedef struct { u16 compression; u16 numTile; u32 *tiles; } TileSet;
typedef struct { u16 compression; u16 w, h; u16 *tilemap; } TileMap;
typedef struct { void *palette; TileSet *tileset; TileMap *tilemap; } Image;
typedef enum { BG_B, BG_A } VDPPlane;
#define PAL0 0
#define PAL1 1
#define PAL2 2
#define PAL3 3
#define TILE_ATTR(p, pr, v, h) (((p) << 13) | ((pr) << 15))
#define SPR_FLAG_AUTO_VRAM_ALLOC 0x0800
#define SPR_MAX_DEPTH 0x7FFF
#define SPR_MIN_DEPTH (-0x8000)
#define SPR_FLAG_AUTO_TILE_UPLOAD 0x0400
#define BUTTON_UP 0x0001
#define BUTTON_DOWN 0x0002
#define BUTTON_LEFT 0x0004
#define BUTTON_RIGHT 0x0008
#define BUTTON_A 0x0040
#define BUTTON_B 0x0010
#define BUTTON_C 0x0020
#define BUTTON_START 0x0080
#define BUTTON_X 0x0400
#define BUTTON_Y 0x0200
#define BUTTON_Z 0x0100
extern u32 host_sound_plays, host_def_switches;
static inline Sprite *SPR_addSpriteEx(const SpriteDefinition *d, s16 x, s16 y, u16 a, u16 f)
{ Sprite *s = calloc(1, sizeof(Sprite)); s->def = d; s->x = x; s->y = y; s->attr = a; s->flags = f; return s; }
static inline bool SPR_setDefinition(Sprite *s, const SpriteDefinition *d) { s->def = d; host_def_switches++; return TRUE; }
static inline void SPR_setAnimAndFrame(Sprite *s, s16 a, s16 f) { (void)a; s->frame = f; }
static inline void SPR_setHFlip(Sprite *s, bool v) { (void)s; (void)v; }
static inline void SPR_setVFlip(Sprite *s, bool v) { (void)s; (void)v; }
static inline void SPR_setPalette(Sprite *s, u16 v) { (void)s; (void)v; }
static inline void SPR_setPosition(Sprite *s, s16 x, s16 y) { s->x = x; s->y = y; }
static inline void SPR_setDepth(Sprite *s, s16 v) { (void)s; (void)v; }
static inline void SPR_setVisibility(Sprite *s, SpriteVisibility v) { s->visible = v == VISIBLE; }
static inline void SPR_releaseSprite(Sprite *s) { free(s); }
__attribute__((weak)) const u8 *host_last_pcm;   /* ultimo PCM tocado (testes conferem QUAL som) */
static inline bool XGM2_playPCM(const u8 *d, u32 l, SoundPCMChannel c) { (void)l; (void)c; host_sound_plays++; host_last_pcm = d; return TRUE; }
static inline void XGM2_stopPCM(SoundPCMChannel c) { (void)c; }
__attribute__((weak)) u16 host_cram[64];          /* CRAM simulada (testes conferem as cores escritas) */
__attribute__((weak)) s16 host_scroll_b[2];       /* scroll de BG_B: [0] horizontal, [1] vertical */
/* DMA_QUEUE como no SGDK: guarda so o PONTEIRO e copia no VBlank (host_vblank). Fonte em pilha
 * morta ja foi sobrescrita quando a copia roda -- o teste pega o mesmo bug que o hardware. */
__attribute__((weak)) struct { u16 i, n; const u16 *p; } host_dmaq[32];
__attribute__((weak)) u16 host_dmaq_n;
static inline void PAL_setColors(u16 i, const u16 *p, u16 n, TransferMethod t)
{
    if (t == DMA_QUEUE && host_dmaq_n < 32) { host_dmaq[host_dmaq_n].i = i; host_dmaq[host_dmaq_n].n = n; host_dmaq[host_dmaq_n++].p = p; return; }
    for (u16 k = 0; k < n && i + k < 64; k++) host_cram[i + k] = p[k];
}
static __attribute__((noinline)) void host_clobber_stack(void) { volatile u16 junk[512]; for (u16 k = 0; k < 512; k++) junk[k] = 0xDEAD; }
static inline void host_vblank(void)
{
    host_clobber_stack();
    for (u16 q = 0; q < host_dmaq_n; q++)
        for (u16 k = 0; k < host_dmaq[q].n && host_dmaq[q].i + k < 64; k++) host_cram[host_dmaq[q].i + k] = host_dmaq[q].p[k];
    host_dmaq_n = 0;
}
static inline void VDP_setHorizontalScroll(VDPPlane pl, s16 v) { if (pl == BG_B) host_scroll_b[0] = v; }
static inline void VDP_setVerticalScroll(VDPPlane pl, s16 v) { if (pl == BG_B) host_scroll_b[1] = v; }
static inline void VDP_drawText(const char *s, u16 x, u16 y) { (void)s; (void)x; (void)y; }
static inline u16 VDP_loadTileSet(const TileSet *t, u16 i, TransferMethod m) { (void)t; (void)i; (void)m; return 1; }
static inline bool VDP_setTileMapEx(VDPPlane p, const TileMap *m, u16 b, u16 xp, u16 yp, u16 x, u16 y, u16 w, u16 h, TransferMethod t) { (void)p; (void)m; (void)b; (void)xp; (void)yp; (void)x; (void)y; (void)w; (void)h; (void)t; return 1; }
static inline void VDP_clearTileMapRect(VDPPlane p, u16 x, u16 y, u16 w, u16 h) { (void)p; (void)x; (void)y; (void)w; (void)h; }
static inline void PAL_getColors(u16 i, u16 *d, u16 n) { (void)i; memset(d, 0, n * 2); }
static inline void VDP_clearTextArea(u16 x, u16 y, u16 w, u16 h) { (void)x; (void)y; (void)w; (void)h; }
static inline u16 host_random(void) { static u32 s = 12345; s = s * 1103515245u + 12345u; return (u16)(s >> 16); }
#define random() host_random()
#endif

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
typedef struct { const SpriteDefinition *def; s16 x, y; u16 frame; u8 visible; } Sprite;
typedef enum { HIDDEN, VISIBLE, AUTO_FAST, AUTO_SLOW } SpriteVisibility;
typedef enum { SOUND_PCM_CH_AUTO = -1, SOUND_PCM_CH1, SOUND_PCM_CH2, SOUND_PCM_CH3 } SoundPCMChannel;
typedef enum { CPU, DMA, DMA_QUEUE } TransferMethod;
#define PAL0 0
#define PAL1 1
#define PAL2 2
#define PAL3 3
#define TILE_ATTR(p, pr, v, h) (((p) << 13) | ((pr) << 15))
#define SPR_FLAG_AUTO_VRAM_ALLOC 0x0800
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
{ (void)a; (void)f; Sprite *s = calloc(1, sizeof(Sprite)); s->def = d; s->x = x; s->y = y; return s; }
static inline bool SPR_setDefinition(Sprite *s, const SpriteDefinition *d) { s->def = d; host_def_switches++; return TRUE; }
static inline void SPR_setAnimAndFrame(Sprite *s, s16 a, s16 f) { (void)a; s->frame = f; }
static inline void SPR_setHFlip(Sprite *s, bool v) { (void)s; (void)v; }
static inline void SPR_setVFlip(Sprite *s, bool v) { (void)s; (void)v; }
static inline void SPR_setPalette(Sprite *s, u16 v) { (void)s; (void)v; }
static inline void SPR_setPosition(Sprite *s, s16 x, s16 y) { s->x = x; s->y = y; }
static inline void SPR_setDepth(Sprite *s, s16 v) { (void)s; (void)v; }
static inline void SPR_setVisibility(Sprite *s, SpriteVisibility v) { s->visible = v == VISIBLE; }
static inline void SPR_releaseSprite(Sprite *s) { free(s); }
static inline bool XGM2_playPCM(const u8 *d, u32 l, SoundPCMChannel c) { (void)d; (void)l; (void)c; host_sound_plays++; return TRUE; }
static inline void XGM2_stopPCM(SoundPCMChannel c) { (void)c; }
static inline void PAL_setColors(u16 i, const u16 *p, u16 n, TransferMethod t) { (void)i; (void)p; (void)n; (void)t; }
static inline void VDP_drawText(const char *s, u16 x, u16 y) { (void)s; (void)x; (void)y; }
static inline void VDP_clearTextArea(u16 x, u16 y, u16 w, u16 h) { (void)x; (void)y; (void)w; (void)h; }
static inline u16 host_random(void) { static u32 s = 12345; s = s * 1103515245u + 12345u; return (u16)(s >> 16); }
#define random() host_random()
#endif

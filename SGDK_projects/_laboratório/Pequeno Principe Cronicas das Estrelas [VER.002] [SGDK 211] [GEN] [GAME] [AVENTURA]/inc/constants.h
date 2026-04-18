#ifndef PP2_CONSTANTS_H
#define PP2_CONSTANTS_H

/* =========================================================================
 * Pequeno Príncipe VER.002 — Hardware Constants
 * ========================================================================= */

/* Screen */
#define PP2_SCREEN_W            320
#define PP2_SCREEN_H            224
#define PP2_SCREEN_TILES_W      40
#define PP2_SCREEN_TILES_H      28
#define PP2_HORIZON_Y           112

/* Scroll buffers */
#define PP2_HSCROLL_LINES       224
#define PP2_VSCROLL_COLS        20

/* Player */
#define PP2_SCARF_SEGMENTS      5
#define PP2_PLAYER_SPRITE_W     4   /* in tiles */
#define PP2_PLAYER_SPRITE_H     4
#define PP2_PLAYER_GROUND_Y     180

/* Physics (fix32 integers, no float) */
#define PP2_GRAVITY             FIX32(0.25)
#define PP2_GRAVITY_GLIDE       FIX32(0.06)
#define PP2_JUMP_FORCE          FIX32(-5.5)
#define PP2_MAX_FALL            FIX32(5.0)
#define PP2_WALK_SPEED          FIX32(1.5)
#define PP2_SCARF_DAMPING       FIX16(0.25)

/* HUD (Window plane) */
#define PP2_HUD_SPLIT_LINE      196
#define PP2_HUD_TILE_ROW        (PP2_HUD_SPLIT_LINE / 8)  /* = 24 */
#define PP2_DIALOG_MAX_LINES    4
#define PP2_DIALOG_MAX_CHARS    40

/* VRAM tile bases */
#define PP2_TILE_BASE           TILE_USER_INDEX
#define PP2_TILE_FONT           (PP2_TILE_BASE + 0)       /* 96 font tiles */
#define PP2_TILE_HUD            (PP2_TILE_BASE + 96)      /* 32 HUD tiles */
#define PP2_TILE_PLAYER         (PP2_TILE_BASE + 128)     /* 16 player tiles (4x4) */
#define PP2_TILE_SCARF          (PP2_TILE_BASE + 144)     /* 5 scarf tiles */
#define PP2_TILE_SCENE          (PP2_TILE_BASE + 160)     /* rest for scene tilesets */
#define PP2_TILE_SCENE_MAX      1184                      /* 1344 total - 160 reserved */

/* Sprite attribute helpers */
#define PP2_SPR_ATTR(pal, prio, flip_h, flip_v, tile) \
    TILE_ATTR_FULL((pal), (prio), (flip_v), (flip_h), (tile))

/* Audio channels */
#define PP2_AUDIO_CH_BGM        SOUND_PCM_CH1
#define PP2_AUDIO_CH_SFX        SOUND_PCM_CH2
#define PP2_AUDIO_CH_VOICE      SOUND_PCM_CH3
#define PP2_AUDIO_FADE_FRAMES   60

/* Travel */
#define PP2_TRAVEL_DURATION     600     /* frames */
#define PP2_TRAVEL_ASTEROID_MAX 8

/* Planets / Travels count */
#define PP2_PLANET_COUNT        12
#define PP2_TRAVEL_COUNT        11

/* Colors — 9-bit Mega Drive grid */
#define PP2_C_BLACK         0x0000
#define PP2_C_WHITE         0x0EEE
#define PP2_C_MAGENTA       0x00E0  /* index 0 transparent */
#define PP2_C_ORANGE        0x0E60
#define PP2_C_GOLD          0x00AE
#define PP2_C_SKY_DEEP      0x0C60
#define PP2_C_SKY_MID       0x0E82
#define PP2_C_SKY_LIGHT     0x0ECA
#define PP2_C_ROYAL_PURPLE  0x0A04
#define PP2_C_SAND          0x06AC
#define PP2_C_GREEN         0x00C2

/* Palette indices */
#define PP2_PAL_BG          PAL0
#define PP2_PAL_PLAYER      PAL1
#define PP2_PAL_NPC         PAL2
#define PP2_PAL_FX          PAL3

#endif /* PP2_CONSTANTS_H */

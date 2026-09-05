#ifndef SYSTEMS_RASTER_H
#define SYSTEMS_RASTER_H

#include <genesis.h>

/*
 * SINGLE OWNER of scroll + palette + raster.
 * See doc/ARCHITECTURE.md section 6.1. No other module writes the HScroll
 * table, CRAM during H-interrupt, the background colour, or the S/H register.
 *
 * The five-layer contract (doc/ARCHITECTURE.md section 3) is produced from TWO
 * hardware planes:
 *
 *   CAMADA 1  sky        backdrop lines 0..63 scroll 0        H-int gradient
 *   CAMADA 2  mountains  BG_B lines 64..119   camX / 8
 *   CAMADA 3  hills      BG_B lines 120..223  camX / 3
 *   CAMADA 4  terrain    BG_A all lines       camX / 1
 *   CAMADA 5  foreground sprites              camX * 5/4     (scene-owned)
 *
 * Camadas 1..3 are the SAME plane split by per-scanline HScroll values. There
 * is no third BG plane on this hardware; AGENTS.md lists that as a
 * hallucination.
 */

#define RASTER_SCREEN_LINES 224u

/* Band boundaries on BG_B, in scanlines. */
#define RASTER_BAND_SKY_END 64u
#define RASTER_BAND_MOUNT_END 120u

/* Sky gradient: 12 stops driven by the H-interrupt into ONE CRAM entry.
 * doc/PALETTES.md section 6.1 caps each band at 1 CRAM word. */
#define RASTER_SKY_STOPS 12u
/*
 * The gradient drives CRAM entry 0 = the BACKDROP colour, not a tile colour.
 * That is why the sky needs no opaque tiles at all: wherever BG_A and BG_B are
 * both transparent, the backdrop shows through, so ONE CRAM entry produces the
 * whole sky. Discovered by running it: driving index 1 instead left the
 * backdrop at the magenta key and painted the mountain band magenta.
 */
#define RASTER_SKY_CRAM_INDEX 0u
#define RASTER_SKY_LINES_PER_STOP 12u

void RASTER_initStage(void);
void RASTER_shutdown(void);

/* Build the next frame's HScroll table from the camera. Call once per frame in
 * the scene update; it enqueues DMA, it does not transfer immediately. */
void RASTER_updateScroll(s16 cameraX);

/* Re-arm the per-frame H-interrupt state. Call once per frame. */
void RASTER_frameStart(void);

/* Swap the sky gradient table. The title uses a night ramp; stages use day. */
void RASTER_setNightSky(bool night);

/*
 * R3 + R4 from doc/ARCHITECTURE.md section 4: the waterline.
 *
 * R3 is per-line sine distortion of BG_A below the waterline. It costs HScroll
 * table entries, which we already build every frame, so it is nearly free.
 *
 * R4 is the submerged palette swap. doc/PALETTES.md section 6.1 caps each H-int
 * band at ONE CRAM word and marks the real ceiling `[NAO MEDIDO]`; section 6.3
 * then describes a 16-word swap, which contradicts it. That tension is REAL and
 * is resolved by measuring: RASTER_setWaterCramWords lets a test scene push the
 * count up until the capture shows garbage.
 */
#define RASTER_WATER_MAX_WORDS 8u

void RASTER_setWaterline(s16 line);      /* < 0 disables the whole effect */
void RASTER_setWaterCramWords(u16 count);
u16 RASTER_getWaterCramWords(void);

u16 RASTER_getSkyStopCount(void);

#endif

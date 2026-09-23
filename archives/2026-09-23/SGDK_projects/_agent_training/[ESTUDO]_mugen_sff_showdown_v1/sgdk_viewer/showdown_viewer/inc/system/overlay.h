#ifndef SYSTEM_OVERLAY_H
#define SYSTEM_OVERLAY_H

#include <genesis.h>

/*
 * Canonical WINDOW-plane overlay helpers (rows 0..2, all columns).
 * Use when the scene loads opaque BG_A art to keep font-tile writes from
 * substituting BG_A tiles at the overlay rows. See BENCHMARK_VISUAL_LAB
 * scenes (parallax, multiplane, sunny_land, fx_line, masked_light,
 * pseudo3d_tower) for reference usage.
 */
void SCENE_overlayWindowBegin(void);
void SCENE_overlayWindowEnd(void);
void SCENE_overlayWindowTeardown(void);

#endif

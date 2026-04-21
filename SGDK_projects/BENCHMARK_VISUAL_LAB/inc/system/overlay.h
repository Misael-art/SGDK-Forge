#ifndef SYSTEM_OVERLAY_H
#define SYSTEM_OVERLAY_H

#include <genesis.h>

/*
 * Canonical WINDOW-plane overlay helpers.
 *
 * Problem: when the scene loads an opaque BG_A tilemap (arte densa), calling
 * VDP_drawText/Fill on the default text plane (BG_A) REPLACES the BG_A tile
 * at (x,y) with a font tile. Font tiles have index 0 on non-glyph pixels, so
 * the cenario behind font tiles becomes transparent and BG_B (ou backdrop)
 * vaza por tras, produzindo a sensacao de "texto cortando o cenario".
 *
 * Solution: route overlay writes to the VDP WINDOW plane, which shows its
 * OWN tilemap on top of BG_A within a rectangular region (rows 0..2 by
 * default) without disturbing BG_A content. When the overlay block ends,
 * restore BG_A as the text plane so the global HUD (row 26) keeps working.
 *
 * Usage:
 *   SCENE_overlayWindowBegin();       // in Enter and/or drawOverlay
 *   VDP_drawTextFill("TITLE", 8, 0, 31);
 *   ...                               // rows 0..2 canonical top band
 *   SCENE_overlayWindowEnd();         // restores BG_A as text plane
 *
 *   SCENE_overlayWindowTeardown();    // in Exit before APP_changeScene
 *
 * The begin/end pair is idempotent: calling begin multiple times is safe.
 * Teardown disables the window plane so subsequent scenes are unaffected.
 */
void SCENE_overlayWindowBegin(void);
void SCENE_overlayWindowEnd(void);
void SCENE_overlayWindowTeardown(void);

#endif

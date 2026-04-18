/**
 * hud.c — HUD rendering on Window plane
 *
 * The Window plane (WINDOW) overlays BGA/BGB without scrolling.
 * Top 2 tile rows (16px) reserved via VDP_setWindowVPos(FALSE, 2) in main.c.
 * Text written directly to window tiles using VDP_drawTextEx.
 */

#include <genesis.h>

#include "hud.h"
#include "game_config.h"

/* =========================================================================
 * Init
 * ========================================================================= */
void HUD_init(void) {
    /* Draw static HUD labels */
    VDP_drawTextEx(WINDOW, "SCORE:", TILE_ATTR(PAL0, TRUE, FALSE, FALSE), 1, 0, CPU);
    VDP_drawTextEx(WINDOW, "000000", TILE_ATTR(PAL0, TRUE, FALSE, FALSE), 7, 0, CPU);
    VDP_drawTextEx(WINDOW, "LIVES:", TILE_ATTR(PAL0, TRUE, FALSE, FALSE), 20, 0, CPU);
    VDP_drawTextEx(WINDOW, "3", TILE_ATTR(PAL0, TRUE, FALSE, FALSE), 26, 0, CPU);
}

/* =========================================================================
 * Update score display (call when score changes)
 * ========================================================================= */
void HUD_updateScore(u32 score) {
    char buf[7];
    intToStr(score, buf, 6);
    VDP_drawTextEx(WINDOW, buf, TILE_ATTR(PAL0, TRUE, FALSE, FALSE), 7, 0, CPU);
}

/* =========================================================================
 * Update lives display (call when lives change)
 * ========================================================================= */
void HUD_updateLives(u8 lives) {
    char buf[2] = { '0' + lives, '\0' };
    VDP_drawTextEx(WINDOW, buf, TILE_ATTR(PAL0, TRUE, FALSE, FALSE), 26, 0, CPU);
}

/* =========================================================================
 * Show / clear message text (for title, game over, etc.)
 * ========================================================================= */
void HUD_showMessage(const char* msg, u16 x, u16 y) {
    VDP_drawTextEx(WINDOW, msg, TILE_ATTR(PAL0, TRUE, FALSE, FALSE), x, y, CPU);
}

void HUD_clearMessage(u16 x, u16 y, u16 len) {
    VDP_clearTextEx(WINDOW, x, y, len);
}

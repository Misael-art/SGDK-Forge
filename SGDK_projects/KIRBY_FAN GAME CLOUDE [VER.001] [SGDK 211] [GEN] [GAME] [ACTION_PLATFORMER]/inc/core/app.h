#ifndef CORE_APP_H
#define CORE_APP_H

#include <genesis.h>

#include "game_vars.h"

/*
 * Canonical HUD / text safe-area contract.
 * 320x224 screen => 28 text rows (0..27). Row 28 is OFF-SCREEN and FORBIDDEN.
 *
 *   rows 0..2   : scene title / telemetry overlay (scene-owned)
 *   rows 3..24  : gameplay / scene content
 *   row  25     : scene secondary hint (optional, scene-owned)
 *   row  26     : global debug HUD (owned by core/app.c APP_drawDebugHud)
 *   row  27     : scene primary input hint (scene-owned)
 *   row >= 28   : FORBIDDEN
 */
#define VDP_TEXT_COLS 40
#define VDP_TEXT_SAFE_LAST_ROW 27
#define VDP_TEXT_FORBIDDEN_ROW 28

#define HUD_ROW_HINT_SECONDARY 25
#define HUD_ROW_HUD_GLOBAL 26
#define HUD_ROW_HINT_PRIMARY 27

#define HUD_ROWS 1
#define HUD_ROW_START HUD_ROW_HUD_GLOBAL
#define HUD_ROW_TITLE HUD_ROW_HUD_GLOBAL
#define HUD_ROW_SCENE HUD_ROW_HUD_GLOBAL
#define HUD_ROW_FRAME HUD_ROW_HUD_GLOBAL
#define HUD_TEXT_X 1
#define HUD_TEXT_LEN (VDP_TEXT_COLS - HUD_TEXT_X)

#define SPR_CENTER_X(def, cx) ((s16)((cx) - (s16)((def)->w * 4)))
#define SPR_CENTER_Y(def, cy) ((s16)((cy) - (s16)((def)->h * 4)))

void APP_boot(bool hardReset);
void APP_update(void);
void APP_changeScene(AppScene nextScene);
const char* APP_sceneName(AppScene scene);

void SCENE_cleanupLineScroll(VDPPlane plane);

#endif

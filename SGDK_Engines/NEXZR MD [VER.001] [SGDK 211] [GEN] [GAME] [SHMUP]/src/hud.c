#include "hud.h"
#include "game.h"
#include "resources.h"

Sprite* HUD_slasher;

void Characters_clear(u16 x, u16 y, u16 width);

void HUD_init() {
  HUD_slasher = SPR_addSprite(&hud_slasher, GAME_WINDOW_WIDTH - 32, GAME_WINDOW_HEIGHT - 32, TILE_ATTR(SLASHER_PALLETE, TRUE, FALSE, FALSE));
  HUD_setScore(0);
  HUD_setLives(Game_getLivesCount());
}

void HUD_clear() {
  SPR_releaseSprite(HUD_slasher);
  Characters_clearXY(2, 1, 10);
  Characters_clearXY(8, 2, 10);
}

void HUD_setScore(unsigned int score) {
  Characters_print("SC", 2, 1, FONT_ACTIVE);
  char sc[20];

  sprintf(sc, "%d", score);
  Characters_print(sc, 5, 2, FONT_ACTIVE);
}

void HUD_setLives(u8 lives) {
  char lvs[2];

  sprintf(lvs, "%d", lives);
  Characters_print(lvs, 38, 27, FONT_ACTIVE);
}

void HUD_showPaused() {
	if (Game_isPaused()) {
		Characters_print(TXT_PAUSED, 17, 13, FONT_ACTIVE);

	} else {		
  	Characters_clearXY(17, 13, 10);

	}
}


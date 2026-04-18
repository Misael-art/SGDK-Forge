#include "utils.h"
#include "game.h"

void Utils_wait(u8 seconds) {

  unsigned t = seconds * FRAMES_PER_SECOND;

  for (unsigned i = 0; i < t; i++)
    SYS_doVBlankProcess();
}

void Utils_loadAndfadeIn(Image img, u8 seconds) {
  unsigned t = seconds * FRAMES_PER_SECOND;

  VDP_drawImageEx(BG_A,
  &img,
  TILE_ATTR_FULL(BACKGROUND_PALLETE, FALSE, FALSE, FALSE, TILE_USER_INDEX),
  GAME_WINDOW_START_POSITION_LEFT,
  GAME_WINDOW_START_POSITION_TOP,
  FALSE,
  TRUE);

  PAL_fadeIn(0, 63, img.palette->data, t, FALSE);
  PAL_setPalette(BACKGROUND_PALLETE, img.palette->data, DMA);

  while (PAL_isDoingFade())
	 SYS_doVBlankProcess();
}

void Utils_fadeOut(u8 seconds) {
  unsigned t = seconds * FRAMES_PER_SECOND;

  PAL_fadeOut(0, 63, t, FALSE);

  while (PAL_isDoingFade())
	 SYS_doVBlankProcess();
}
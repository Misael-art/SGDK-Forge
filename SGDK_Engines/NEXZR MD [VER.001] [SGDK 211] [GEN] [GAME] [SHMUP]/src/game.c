#include "game.h"
#include "menu.h"
#include "characters.h"
#include "hud.h"
#include "intro.h"

u32 currentFrame;
u8 currentLevel;
bool game_paused;
Player player;
u8 game_lives;

void _globalJoyEventHandler(u16 joy, u16 changed, u16 state);
void initialize_screen();
void show_lives();

void (*currentInputHandler)(u16 joy, u16 changed, u16 state) = NULL;

void Game_init() {
  initialize_screen();
  SPR_init();
  JOY_setEventHandler(&_globalJoyEventHandler);

  currentFrame = 0;
  I18N_setLanguage(LANG_EN);
  game_options.difficulty = NORMAL;
  game_options.md_mode = false;
  game_options.language = LANG_EN;

  Characters_init();

  Intro_init(&Menu_init);
  currentLevel = MENU;

  game_paused = false;
  game_lives = 4;
}

void initialize_screen() {
  VDP_setScreenWidth320();
  VDP_setScreenHeight240();
}

void Game_update() {
  currentFrame++;

  Entity_executeAll();
  SPR_update();
  SYS_doVBlankProcess();
}

void Game_setJoyHandler(void (*handler)(u16 joy, u16 changed, u16 state)) {
  currentInputHandler = handler;
}

void _globalJoyEventHandler(u16 joy, u16 changed, u16 state) {
    if (currentInputHandler) {
        currentInputHandler(joy, changed, state);
    }
}

void Game_resetScreen() {
  VDP_clearPlane(BG_A, TRUE);
	VDP_clearPlane(BG_B, TRUE);
  VDP_clearPlane(WINDOW, TRUE);
  PAL_setPalette(PAL0, palette_black, DMA);
	PAL_setPalette(PAL1, palette_black, DMA);
  PAL_setPalette(PAL2, palette_black, DMA);
	PAL_setPalette(PAL3, palette_black, DMA);
}

bool Game_isPaused() {
  return game_paused;
}

void Game_pause() {
  game_paused = !game_paused;
}

void Game_over() {
  
}

void Game_loseLive() {
  game_lives--;
  show_lives();

  if (game_lives <= 0)
    Game_over();
}

void Game_addLive() {
  if (game_lives >= MAX_LIVES)
    return;

  game_lives++;
  show_lives();
}

void show_lives() {
  if (currentLevel == MENU)
    return;

  HUD_setLives(game_lives);
}

u8 Game_getLivesCount() {
  return game_lives;
}

void Game_setLives(u8 count) {
  if (count > MAX_LIVES)
    return;

  game_lives = count;
}

void Game_resetCurrentFrame() {
  currentFrame = 0;
}
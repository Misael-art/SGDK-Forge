#ifndef GAME_H
#define GAME_H

#include <genesis.h>
#include "player.h"
#include "menu.h"
#include "entitymanager.h"
#include "callback.h"
#include "resources.h"
#include "i18n.h"

#define GAME_WINDOW_START_POSITION_TOP 0
#define GAME_WINDOW_START_POSITION_LEFT 0
#define GAME_WINDOW_WIDTH 320
#define GAME_WINDOW_HEIGHT 240
#define SLASHER_PALLETE 1
#define CHARACTER_PALLETE 1
#define BACKGROUND_PALLETE 0
#define MAX_LIVES 9
#define FRAMES_PER_SECOND 60

typedef enum {
  EASY,
  NORMAL,
  HARD
} difficulties;

typedef struct {
  u8 language;
  bool md_mode;
  u8 difficulty;
} game_options_struct;

typedef enum {
  MENU,
  LEVEL_1
} levels;

static game_options_struct game_options;

//u32 globalCounter;
extern u32 currentFrame;
extern u8 currentLevel;
extern bool game_paused;

extern Player player;

void Game_init();
void Game_update();
void Game_setJoyHandler(void (*handler)(u16 joy, u16 changed, u16 state));
void Game_resetScreen();
bool Game_isPaused();
void Game_pause();
void Game_over();
void Game_loseLive();
void Game_addLive();
u8 Game_getLivesCount();
void Game_setLives(u8 count);
void Game_resetCurrentFrame();

#endif
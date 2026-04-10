#include "level_1.h"
#include "background.h"
#include "game.h"
#include "player.h"
#include "i18n.h"
#include "hud.h"
#include "entitymanager.h"

Entity* level1Entity;
unsigned long level1_frame = 0;

void level1_joyEventHandler(u16 joy, u16 changed, u16 state) ;
void level1_start(void* context);
void level1_dispose();

void Level1_init() {
  Background_init();
  PLAYER_init(&player);
  Game_setJoyHandler(level1_joyEventHandler);
  Characters_prepareToPrint();

  currentLevel = LEVEL_1;

  HUD_init();
  level1Entity = Entity_add(NULL, level1_start);
}

void level1_joyEventHandler(u16 joy, u16 changed, u16 state) {
    if (joy == JOY_1) {
        if (changed & state & BUTTON_START) {
            Game_pause();
            HUD_showPaused();
        }
    }
}

void level1_start(void* context) {

  level1_frame++;
}

void level1_dispose() {
  Entity_removeEntity(level1Entity->index);
}
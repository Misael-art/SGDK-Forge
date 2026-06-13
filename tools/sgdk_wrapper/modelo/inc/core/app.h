#ifndef CORE_APP_H
#define CORE_APP_H

#include <genesis.h>

#include "game_vars.h"

void APP_boot(bool hardReset);
void APP_update(void);
void APP_changeScene(AppScene nextScene);
const char* APP_sceneName(AppScene scene);

#endif

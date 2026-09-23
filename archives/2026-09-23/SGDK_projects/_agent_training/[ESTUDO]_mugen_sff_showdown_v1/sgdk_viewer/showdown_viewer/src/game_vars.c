#include <genesis.h>

#include "game_vars.h"

AppState gApp = {
    APP_SCENE_BRANDING,
    APP_SCENE_BRANDING,
    APP_SCENE_BRANDING,
    0,
    0,
    0,
    60,
    APP_REGION_NTSC,
    TRUE,
    FALSE,
    FALSE
};

InputSnapshot gInput = { 0, 0, 0, FALSE };

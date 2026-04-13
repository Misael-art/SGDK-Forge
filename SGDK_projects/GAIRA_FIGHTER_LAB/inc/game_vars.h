#ifndef GAME_VARS_H
#define GAME_VARS_H

#include <genesis.h>

typedef enum AppScene {
    APP_SCENE_MENU = 0,
    APP_SCENE_SPRITE_ANIM = 1,
    APP_SCENE_CHAR_DESIGN = 2,
    APP_SCENE_MULTIPLANE  = 3
} AppScene;

typedef struct InputSnapshot {
    u16 held;
    u16 pressed;
    u16 released;
} InputSnapshot;

typedef struct AppState {
    AppScene currentScene;
    AppScene previousScene;
    u32 totalFrames;
    u16 sceneFrames;
    bool sceneNeedsEnter;
    bool showDebugHud;
} AppState;

extern AppState gApp;
extern InputSnapshot gInput;

#endif

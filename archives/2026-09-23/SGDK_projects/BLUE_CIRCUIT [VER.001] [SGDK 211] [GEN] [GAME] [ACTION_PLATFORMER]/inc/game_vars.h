#ifndef GAME_VARS_H
#define GAME_VARS_H

#include <genesis.h>

typedef enum AppScene {
    APP_SCENE_BRANDING = 0,
    APP_SCENE_BOOT = 1,
    APP_SCENE_MENU = 2,
    APP_SCENE_DEMO = 3
} AppScene;

typedef enum AppRegion {
    APP_REGION_NTSC = 0,
    APP_REGION_PAL = 1
} AppRegion;

typedef struct InputSnapshot {
    u16 held;
    u16 pressed;
    u16 released;
    bool sixButton;
} InputSnapshot;

typedef struct AppState {
    AppScene currentScene;
    AppScene previousScene;
    AppScene transitionTarget;
    u32 totalFrames;
    u16 sceneFrames;
    u8 transitionFrames;
    u16 targetFps;
    AppRegion region;
    bool sceneNeedsEnter;
    bool showDebugHud;
    bool paused;
} AppState;

extern AppState gApp;
extern InputSnapshot gInput;

#endif

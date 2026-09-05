#ifndef GAME_VARS_H
#define GAME_VARS_H

#include <genesis.h>

typedef enum AppScene {
    APP_SCENE_BRANDING = 0,
    APP_SCENE_BOOT = 1,
    APP_SCENE_MENU = 2,
    APP_SCENE_DEMO = 3,
    APP_SCENE_STAGE = 4,
    /* Same stage, but driven by the recorded input script in
     * src/system/playtest.c. Exists as a separate scene id because the
     * canonical bootstrap block carries only a scene id and no flags field,
     * and that block is written by shared tooling we may not modify. */
    APP_SCENE_STAGE_PLAYTEST = 5,
    APP_SCENE_BOSS = 6,
    APP_SCENE_BOSS_PLAYTEST = 7,
    APP_SCENE_GAMEOVER = 8,
    APP_SCENE_TITLE = 9,
    APP_SCENE_LAKE = 10,
    /* Isolated visual proof only; never replaces the first playable hero. */
    APP_SCENE_NATIVE_ART_REVIEW = 11
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

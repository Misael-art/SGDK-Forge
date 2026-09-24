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
    /* MISSAO 2026-08-24: abertura, final, menu expandido e minigames.
     * Ids novos SEMPRE no fim: capturas seladas carregam ids <= 10 no SRAM
     * bootstrap block e precisam continuar validos. */
    APP_SCENE_INTRO = 11,
    APP_SCENE_ENDING = 12,
    APP_SCENE_MGHUB = 13,
    APP_SCENE_MG_QUICKDRAW = 14,
    APP_SCENE_MG_STARFALL = 15,
    APP_SCENE_MG_PUNCH = 16,
    APP_SCENE_MG_DODGE = 17,
    APP_SCENE_MG_SIMON = 18,
    APP_SCENE_MG_HIGHJUMP = 19,
    APP_SCENE_MG_RHYTHM = 20
} AppScene;

/* Fonte unica da contagem: core/app.c le este macro (guard #ifndef). */
#define APP_SCENE_COUNT 21

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

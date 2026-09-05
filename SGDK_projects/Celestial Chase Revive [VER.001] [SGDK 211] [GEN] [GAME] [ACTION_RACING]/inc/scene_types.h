#ifndef SCENE_TYPES_H
#define SCENE_TYPES_H

#include <genesis.h>

typedef enum {
    APP_SCENE_BRANDING,
    APP_SCENE_TITLE,
    APP_SCENE_OPENING_CUTSCENE,
    APP_SCENE_RACE,
    APP_SCENE_RESULT,
    APP_SCENE_CREDITS,
    APP_SCENE_COUNT
} SceneId;

typedef struct {
    void (*enter)(void);
    void (*update)(void);
    void (*exit)(void);
    const u16* palette; // Pointer to 64-color palette, or NULL
    bool enterFade;     // True if we should fade in when entering
    bool exitFade;      // True if we should fade out when exiting
} Scene;

#endif /* SCENE_TYPES_H */

#ifndef CORE_SCENE_REGISTRY_H
#define CORE_SCENE_REGISTRY_H

#include <genesis.h>

#include "game_vars.h"

#define SCENE_MENU_SLOT_NONE 0xFFFFu

typedef void (*SceneLifecycleFn)(void);

typedef enum SceneOverlayMode {
    SCENE_OVERLAY_MODE_NONE = 0,
    SCENE_OVERLAY_MODE_BG_TEXT,
    SCENE_OVERLAY_MODE_WINDOW
} SceneOverlayMode;

typedef enum SceneKind {
    SCENE_KIND_SYSTEM = 0,
    SCENE_KIND_MENU,
    SCENE_KIND_SHOWCASE_MULTIPLANE,
    SCENE_KIND_FX_LAB,
    SCENE_KIND_DEPTH_LAB
} SceneKind;

typedef struct SceneDefinition {
    AppScene scene_id;
    u16 menu_slot;
    const char* menu_label;
    const char* scene_name;
    const char* runtime_name;
    SceneLifecycleFn enter;
    SceneLifecycleFn update;
    SceneLifecycleFn exit;
    SceneOverlayMode overlay_mode;
    SceneKind scene_kind;
    const char* evidence_case_id;
} SceneDefinition;

const SceneDefinition* SCENE_REGISTRY_find(AppScene scene_id);
u16 SCENE_REGISTRY_menuCount(void);
const SceneDefinition* SCENE_REGISTRY_menuAt(u16 index);

#endif

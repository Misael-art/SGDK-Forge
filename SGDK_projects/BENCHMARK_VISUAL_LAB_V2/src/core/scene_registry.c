#include "core/scene_registry.h"

#include "scenes/scene_boot.h"
#include "scenes/scene_depth_tower_showcase_v2.h"
#include "scenes/scene_fx_line_scroll_water_v2.h"
#include "scenes/scene_menu.h"
#include "scenes/scene_multiplane_showcase_v2.h"

static const SceneDefinition sSceneRegistry[] = {
    {
        APP_SCENE_BOOT,
        SCENE_MENU_SLOT_NONE,
        "Boot",
        "scene_boot",
        "BOOT",
        SCENE_bootEnter,
        SCENE_bootUpdate,
        NULL,
        SCENE_OVERLAY_MODE_NONE,
        SCENE_KIND_SYSTEM,
        "system_boot"
    },
    {
        APP_SCENE_MENU,
        SCENE_MENU_SLOT_NONE,
        "Menu",
        "scene_menu",
        "MENU",
        SCENE_menuEnter,
        SCENE_menuUpdate,
        NULL,
        SCENE_OVERLAY_MODE_BG_TEXT,
        SCENE_KIND_MENU,
        "system_menu"
    },
    {
        APP_SCENE_MULTIPLANE_SHOWCASE,
        1,
        "S1.1 Multiplane Curado",
        "scene_multiplane_showcase_v2",
        "MULTIPLANE",
        SCENE_multiplaneShowcaseV2Enter,
        SCENE_multiplaneShowcaseV2Update,
        SCENE_multiplaneShowcaseV2Exit,
        SCENE_OVERLAY_MODE_WINDOW,
        SCENE_KIND_SHOWCASE_MULTIPLANE,
        "slice1_multiplane"
    },
    {
        APP_SCENE_FX_LINE_SCROLL_WATER,
        2,
        "S1.2 Agua Line Scroll",
        "scene_fx_line_scroll_water_v2",
        "FX_WATER",
        SCENE_fxLineScrollWaterV2Enter,
        SCENE_fxLineScrollWaterV2Update,
        SCENE_fxLineScrollWaterV2Exit,
        SCENE_OVERLAY_MODE_WINDOW,
        SCENE_KIND_FX_LAB,
        "slice1_fx_water"
    },
    {
        APP_SCENE_DEPTH_TOWER_SHOWCASE,
        3,
        "S1.3 Depth Tower",
        "scene_depth_tower_showcase_v2",
        "DEPTH",
        SCENE_depthTowerShowcaseV2Enter,
        SCENE_depthTowerShowcaseV2Update,
        SCENE_depthTowerShowcaseV2Exit,
        SCENE_OVERLAY_MODE_WINDOW,
        SCENE_KIND_DEPTH_LAB,
        "slice1_depth_tower"
    }
};

static const u16 sSceneRegistryCount = (u16)(sizeof(sSceneRegistry) / sizeof(sSceneRegistry[0]));

const SceneDefinition* SCENE_REGISTRY_find(AppScene scene_id)
{
    u16 index;

    for (index = 0; index < sSceneRegistryCount; index++)
    {
        if (sSceneRegistry[index].scene_id == scene_id)
        {
            return &sSceneRegistry[index];
        }
    }

    return NULL;
}

u16 SCENE_REGISTRY_menuCount(void)
{
    return 3;
}

const SceneDefinition* SCENE_REGISTRY_menuAt(u16 index)
{
    u16 registryIndex;
    u16 targetSlot = (u16)(index + 1);

    for (registryIndex = 0; registryIndex < sSceneRegistryCount; registryIndex++)
    {
        if (sSceneRegistry[registryIndex].menu_slot == targetSlot)
        {
            return &sSceneRegistry[registryIndex];
        }
    }

    return NULL;
}

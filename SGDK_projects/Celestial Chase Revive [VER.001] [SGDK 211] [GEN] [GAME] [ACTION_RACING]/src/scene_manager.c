#include "scene_manager.h"
#include "input_abstraction.h"

extern const Scene branding_scene;
extern const Scene title_scene;
extern const Scene credits_scene;
extern const Scene opening_cutscene;
extern const Scene race_scene;
extern const Scene result_scene;

static const Scene* const scenes[APP_SCENE_COUNT] = {
    &branding_scene,       /* APP_SCENE_BRANDING */
    &title_scene,          /* APP_SCENE_TITLE */
    &opening_cutscene,     /* APP_SCENE_OPENING_CUTSCENE */
    &race_scene,           /* APP_SCENE_RACE */
    &result_scene,         /* APP_SCENE_RESULT */
    &credits_scene         /* APP_SCENE_CREDITS */
};

static SceneId current_scene_id = APP_SCENE_COUNT;
static SceneId next_scene_id = APP_SCENE_COUNT;
static bool transition_requested = false;

static void set_all_colors_black(void)
{
    u16 black[64];
    for (u16 i = 0; i < 64u; i++)
    {
        black[i] = 0u;
    }
    PAL_setColors(0u, black, 64u, CPU);
}

void SM_init(SceneId initialScene)
{
    if (initialScene < APP_SCENE_COUNT)
    {
        current_scene_id = initialScene;
        next_scene_id = initialScene;
        transition_requested = false;

        const Scene* scene = scenes[current_scene_id];

        if (scene->enterFade)
        {
            set_all_colors_black();
        }

        scene->enter();

        if (scene->enterFade && scene->palette != NULL)
        {
            PAL_fadeInAll(scene->palette, 30, FALSE);
        }
        else if (scene->palette != NULL)
        {
            PAL_setColors(0u, scene->palette, 64u, DMA);
        }
    }
}

void SM_requestTransition(SceneId nextScene)
{
    if (nextScene < APP_SCENE_COUNT)
    {
        next_scene_id = nextScene;
        transition_requested = true;
    }
}

void SM_update(void)
{
    if (transition_requested)
    {
        transition_requested = false;

        const Scene* current_scene = scenes[current_scene_id];
        const Scene* next_scene = scenes[next_scene_id];

        /* 1. Lock input */
        IO_setLocked(true);

        /* 2. Fade out if current scene has exitFade active */
        if (current_scene->exitFade)
        {
            PAL_fadeOutAll(30, FALSE);
        }

        /* 3. Exit current scene */
        current_scene->exit();

        /* 4. Teardown / Clear VDP state */
        VDP_clearPlane(BG_A, TRUE);
        VDP_clearPlane(BG_B, TRUE);
        VDP_clearPlane(WINDOW, TRUE);

        SPR_clear();

        VDP_setHorizontalScroll(BG_A, 0);
        VDP_setVerticalScroll(BG_A, 0);
        VDP_setHorizontalScroll(BG_B, 0);
        VDP_setVerticalScroll(BG_B, 0);

        /* 5. Ensure black colors for fade-in setup */
        if (next_scene->enterFade)
        {
            set_all_colors_black();
        }

        /* 6. Enter next scene */
        current_scene_id = next_scene_id;
        next_scene->enter();

        /* 7. Fade in next scene if enterFade is true and palette is provided */
        if (next_scene->enterFade && next_scene->palette != NULL)
        {
            PAL_fadeInAll(next_scene->palette, 30, FALSE);
        }
        else if (next_scene->palette != NULL)
        {
            PAL_setColors(0u, next_scene->palette, 64u, DMA);
        }

        /* 8. Unlock input */
        IO_setLocked(false);
    }
    else
    {
        /* Update current scene */
        if (current_scene_id < APP_SCENE_COUNT)
        {
            scenes[current_scene_id]->update();
        }
    }
}

SceneId SM_getCurrentScene(void)
{
    return current_scene_id;
}

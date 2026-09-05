#include <genesis.h>
#include "branding_scene.h"
#include "scene_manager.h"
#include "input_abstraction.h"
#include "resources.h"

static u16 frame_count = 0;

static void enter(void)
{
    frame_count = 0;

    /* Desenha o logo de forma centralizada */
    const u16 tiles_w = img_brand_engine_logo.tilemap->w;
    const u16 tiles_h = img_brand_engine_logo.tilemap->h;
    const u16 x = (tiles_w < 40u) ? ((40u - tiles_w) / 2u) : 0u;
    const u16 y = (tiles_h < 28u) ? ((28u - tiles_h) / 2u) : 0u;

    /* VDP_drawImageEx carrega a paleta no PAL0 e os tiles na VRAM */
    VDP_drawImageEx(BG_A, &img_brand_engine_logo, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX), x, y, TRUE, DMA);
}

static void update(void)
{
    frame_count++;

    /* Skip se START ou A forem pressionados, ou por timeout de 180 frames (3 segundos a 60Hz) */
    if (IO_getState(INPUT_ACTION_START).pressed ||
        IO_getState(INPUT_ACTION_A).pressed ||
        frame_count >= 180)
    {
        SM_requestTransition(APP_SCENE_TITLE);
    }
}

static void exit(void)
{
    VDP_clearPlane(BG_A, TRUE);
}

const Scene branding_scene = {
    .enter = enter,
    .update = update,
    .exit = exit,
    .palette = NULL, /* exitFade nao precisa de palette explicito, PAL_fadeOutAll usa cores ativas no VRAM/CRAM */
    .enterFade = false,
    .exitFade = true
};

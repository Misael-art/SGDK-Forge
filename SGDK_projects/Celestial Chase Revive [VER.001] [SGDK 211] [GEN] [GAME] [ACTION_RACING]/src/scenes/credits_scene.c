#include <genesis.h>
#include "credits_scene.h"
#include "scene_manager.h"
#include "input_abstraction.h"

static u16 grace_frames = 0;

static const u16 credits_palette[64] = {
    /* PAL0: UI, font, HUD, menu text and title highlights */
    RGB24_TO_VDPCOLOR(0x000018), /* transparente/cor de fundo */
    RGB24_TO_VDPCOLOR(0x102850), /* azul escuro */
    RGB24_TO_VDPCOLOR(0x50C8FF), /* ciano */
    RGB24_TO_VDPCOLOR(0xF0F8FF), /* branco */
    /* cor 15 reservada para o font padrao do SGDK */
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, RGB24_TO_VDPCOLOR(0xF0F8FF),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

static void enter(void)
{
    grace_frames = 0;

    VDP_drawText("CELESTIAL CHASE REVIVE", 9, 3);
    VDP_drawText("A MEGA DRIVE PROJECT", 10, 5);
    VDP_drawText("VER.001 SGDK 2.11", 11, 7);

    VDP_drawText("DEVELOPMENT TEAM", 12, 11);
    VDP_drawText("DESIGN & CODE: ANTIGRAVITY", 7, 13);
    VDP_drawText("SOUND & MUSIC: XGM2 ARCH", 8, 15);

    VDP_drawText("PRESS B OR START TO RETURN", 7, 21);
}

static void update(void)
{
    if (grace_frames < 60)
    {
        grace_frames++;
    }
    else
    {
        if (IO_getState(INPUT_ACTION_START).pressed || IO_getState(INPUT_ACTION_B).pressed)
        {
            SM_requestTransition(APP_SCENE_TITLE);
        }
    }
}

static void exit(void)
{
    VDP_clearPlane(BG_A, TRUE);
}

const Scene credits_scene = {
    .enter = enter,
    .update = update,
    .exit = exit,
    .palette = credits_palette,
    .enterFade = true,
    .exitFade = false
};

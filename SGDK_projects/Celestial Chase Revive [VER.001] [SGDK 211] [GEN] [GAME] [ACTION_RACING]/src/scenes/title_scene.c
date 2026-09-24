#include <genesis.h>
#include "title_scene.h"
#include "scene_manager.h"
#include "input_abstraction.h"
#include "palettes.h"
#include "res/resources.h"

static u8 selected_option = 0;
static u16 title_frame_cnt = 0;
static Sprite* cursor_sprite;

#define TITLE_BG_TILE_BASE TILE_USER_INDEX
#define TITLE_LOGO_TILE_BASE (TITLE_BG_TILE_BASE + img_title_bg.tileset->numTile)

static const u16 title_palette[64] = {
    RGB24_TO_VDPCOLOR(0x000018),
    RGB24_TO_VDPCOLOR(0x102850),
    RGB24_TO_VDPCOLOR(0x50C8FF),
    RGB24_TO_VDPCOLOR(0xF0F8FF),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, RGB24_TO_VDPCOLOR(0xF0F8FF),
    RGB24_TO_VDPCOLOR(0x000000),
    RGB24_TO_VDPCOLOR(0x080828),
    RGB24_TO_VDPCOLOR(0x10103C),
    RGB24_TO_VDPCOLOR(0x2850A0),
    RGB24_TO_VDPCOLOR(0x50A0FF),
    RGB24_TO_VDPCOLOR(0xC8DCFF),
    RGB24_TO_VDPCOLOR(0xFFD000),
    RGB24_TO_VDPCOLOR(0xC0A000),
    RGB24_TO_VDPCOLOR(0xA050FF),
    RGB24_TO_VDPCOLOR(0x282850),
    RGB24_TO_VDPCOLOR(0x3C78C8),
    RGB24_TO_VDPCOLOR(0xFFFFFF),
    RGB24_TO_VDPCOLOR(0x080820),
    RGB24_TO_VDPCOLOR(0x101030),
    RGB24_TO_VDPCOLOR(0x182050),
    RGB24_TO_VDPCOLOR(0x5028A0),
    RGB24_TO_VDPCOLOR(0x00C0C0),
    RGB24_TO_VDPCOLOR(0xC0C0C0),
    RGB24_TO_VDPCOLOR(0x808080),
    RGB24_TO_VDPCOLOR(0x40FF40),
    RGB24_TO_VDPCOLOR(0xFFC800),
    RGB24_TO_VDPCOLOR(0xFF4040),
    RGB24_TO_VDPCOLOR(0xFFFFFF),
    RGB24_TO_VDPCOLOR(0x008080),
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

static void draw_menu(void)
{
    VDP_clearTextArea(9, 13, 22, 1);
    VDP_clearTextArea(9, 15, 22, 1);
    VDP_drawText(selected_option == 0 ? "> START RUN <" : "  START RUN  ", 9, 13);
    VDP_drawText(selected_option == 1 ? "> CREDITS   <" : "  CREDITS    ", 9, 15);

    if (cursor_sprite)
    {
        s16 cy = (selected_option == 0) ? 108 : 124;
        SPR_setPosition(cursor_sprite, 64, cy);
        SPR_setVisibility(cursor_sprite, VISIBLE);
    }
}

static void enter(void)
{
    selected_option = 0;
    title_frame_cnt = 0;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setTextPlane(BG_A);

    VDP_drawImageEx(BG_B, (Image*)&img_title_bg, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, TITLE_BG_TILE_BASE), 0, 0, TRUE, DMA);
    VDP_drawImageEx(BG_A, (Image*)&img_title_logo, TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, TITLE_LOGO_TILE_BASE), 10, 6, TRUE, DMA);

    cursor_sprite = SPR_addSprite(&spr_beacon_key, 64, 108, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    if (cursor_sprite)
    {
        SPR_setFrame(cursor_sprite, 0);
    }

    draw_menu();
}

static void update(void)
{
    title_frame_cnt++;

    if (cursor_sprite)
    {
        SPR_setFrame(cursor_sprite, (title_frame_cnt / 12) % 3);
    }

    if (IO_getState(INPUT_ACTION_UP).pressed)
    {
        if (selected_option > 0)
        {
            selected_option--;
            draw_menu();
        }
    }
    else if (IO_getState(INPUT_ACTION_DOWN).pressed)
    {
        if (selected_option < 1)
        {
            selected_option++;
            draw_menu();
        }
    }

    if (IO_getState(INPUT_ACTION_START).pressed || IO_getState(INPUT_ACTION_A).pressed)
    {
        if (selected_option == 0)
        {
            SM_requestTransition(APP_SCENE_OPENING_CUTSCENE);
        }
        else
        {
            SM_requestTransition(APP_SCENE_CREDITS);
        }
    }
}

static void exit(void)
{
    if (cursor_sprite)
    {
        SPR_releaseSprite(cursor_sprite);
        cursor_sprite = NULL;
    }
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
}

const Scene title_scene = {
    .enter = enter,
    .update = update,
    .exit = exit,
    .palette = title_palette,
    .enterFade = true,
    .exitFade = true
};

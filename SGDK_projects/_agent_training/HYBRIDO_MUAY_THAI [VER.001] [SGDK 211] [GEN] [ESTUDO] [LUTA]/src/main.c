#include <genesis.h>

#include "resources.h"

typedef struct
{
    const SpriteDefinition* body;
    u16 frames;
} ActionDef;

static const ActionDef ACTIONS[] = {
    { &spr_hibrido_idle_body_v010, 6 },
    { &spr_hibrido_walk_step_body_v010, 6 },
    { &spr_hibrido_guard_block_body_v010, 4 },
    { &spr_hibrido_jab_body_v010, 5 },
    { &spr_hibrido_knee_body_v010, 6 },
    { &spr_hibrido_teep_body_v010, 6 },
    { &spr_hibrido_hurt_body_v010, 3 },
};

static u16 current_action = 0;
static u16 current_frame = 0;
static u16 frame_timer = 0;

static const u16 ACTION_COUNT = sizeof(ACTIONS) / sizeof(ACTIONS[0]);

static void apply_action(Sprite* body, u16 action_index)
{
    const ActionDef* action = &ACTIONS[action_index];

    SPR_setDefinition(body, action->body);

    SPR_setPalette(body, PAL2);

    PAL_setPalette(PAL2, action->body->palette->data, DMA);

    SPR_setAutoAnimation(body, FALSE);

    current_frame = 0;
    frame_timer = 0;

    SPR_setFrame(body, 0);
}

int main(bool hardReset)
{
    (void) hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setColor(0, RGB8_8_8_TO_VDPCOLOR(0x22, 0x44, 0x44));
    VDP_setBackgroundColor(0);

    JOY_init();
    SPR_init();

    Sprite* body = SPR_addSprite(ACTIONS[0].body, 136, 120, TILE_ATTR(PAL2, 0, FALSE, FALSE));
    apply_action(body, 0);

    u16 prev = 0;

    while (TRUE)
    {
        u16 v = JOY_readJoypad(JOY_1);
        u16 pressed = (v ^ prev) & v;
        prev = v;

        if (pressed & BUTTON_RIGHT)
        {
            current_action = (current_action + 1) % ACTION_COUNT;
            apply_action(body, current_action);
        }
        else if (pressed & BUTTON_LEFT)
        {
            current_action = (current_action == 0) ? (ACTION_COUNT - 1) : (current_action - 1);
            apply_action(body, current_action);
        }

        frame_timer++;
        if (frame_timer >= 6)
        {
            frame_timer = 0;
            current_frame++;
            if (current_frame >= ACTIONS[current_action].frames) current_frame = 0;
            SPR_setFrame(body, current_frame);
        }

        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

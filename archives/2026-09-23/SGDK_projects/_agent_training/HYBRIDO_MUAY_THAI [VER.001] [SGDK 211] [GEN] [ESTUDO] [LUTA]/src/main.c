#include <genesis.h>

#include "resources.h"

typedef struct
{
    const SpriteDefinition* body;
    u16 frames;
    const SpriteDefinition* fx;
    s16 fx_x;
    s16 fx_y;
    u16 fx_start_frame;
    bool dust_on_contact;
} ActionDef;

static const ActionDef ACTIONS[] = {
    { &spr_hibrido_idle_body_v012, 4, NULL, 0, 0, 0, FALSE },
    { &spr_hibrido_walk_step_body_v012, 4, NULL, 0, 0, 0, TRUE },
    { &spr_hibrido_guard_block_body_v012, 4, &spr_hibrido_fx_hitspark_v010, 150, 128, 1, FALSE },
    { &spr_hibrido_jab_body_v012, 4, &spr_hibrido_fx_hitspark_v010, 186, 124, 2, FALSE },
    { &spr_hibrido_knee_body_v012, 4, &spr_hibrido_fx_lava_burst_v010, 166, 126, 2, TRUE },
    { &spr_hibrido_teep_body_v012, 4, &spr_hibrido_fx_lava_burst_v010, 192, 146, 2, TRUE },
    { &spr_hibrido_hurt_body_v012, 4, &spr_hibrido_fx_hitspark_v010, 128, 126, 0, FALSE },
};

static u16 current_action = 0;
static u16 current_frame = 0;
static u16 frame_timer = 0;
static u16 demo_timer = 0;

static u16 fx_timer = 0;
static u16 fx_frame = 0;
static u16 fx_frame_timer = 0;
static u16 dust_timer = 0;
static u16 dust_frame = 0;
static u16 dust_frame_timer = 0;

static const u16 ACTION_COUNT = sizeof(ACTIONS) / sizeof(ACTIONS[0]);

static void hide_fx(Sprite* fx, Sprite* dust)
{
    SPR_setVisibility(fx, HIDDEN);
    SPR_setVisibility(dust, HIDDEN);
    fx_timer = 0;
    fx_frame = 0;
    fx_frame_timer = 0;
    dust_timer = 0;
    dust_frame = 0;
    dust_frame_timer = 0;
}

static void start_fx(Sprite* fx, const SpriteDefinition* definition, s16 x, s16 y)
{
    SPR_setDefinition(fx, definition);
    SPR_setPalette(fx, PAL3);
    PAL_setPalette(PAL3, definition->palette->data, DMA);
    SPR_setAutoAnimation(fx, FALSE);
    SPR_setFrame(fx, 0);
    SPR_setPosition(fx, x, y);
    SPR_setVisibility(fx, VISIBLE);
    fx_timer = 16;
    fx_frame = 0;
    fx_frame_timer = 0;
}

static void start_dust(Sprite* dust)
{
    SPR_setDefinition(dust, &spr_hibrido_fx_dust_v010);
    SPR_setPalette(dust, PAL3);
    SPR_setAutoAnimation(dust, FALSE);
    SPR_setFrame(dust, 0);
    SPR_setPosition(dust, 132, 176);
    SPR_setVisibility(dust, VISIBLE);
    dust_timer = 12;
    dust_frame = 0;
    dust_frame_timer = 0;
}

static void tick_fx(Sprite* fx, Sprite* dust)
{
    if (fx_timer > 0)
    {
        fx_frame_timer++;
        if (fx_frame_timer >= 4)
        {
            fx_frame_timer = 0;
            if (fx_frame < 3) fx_frame++;
            SPR_setFrame(fx, fx_frame);
        }
        fx_timer--;
        if (fx_timer == 0) SPR_setVisibility(fx, HIDDEN);
    }

    if (dust_timer > 0)
    {
        dust_frame_timer++;
        if (dust_frame_timer >= 3)
        {
            dust_frame_timer = 0;
            if (dust_frame < 3) dust_frame++;
            SPR_setFrame(dust, dust_frame);
        }
        dust_timer--;
        if (dust_timer == 0) SPR_setVisibility(dust, HIDDEN);
    }
}

static void apply_action(Sprite* body, Sprite* fx, Sprite* dust, u16 action_index)
{
    const ActionDef* action = &ACTIONS[action_index];

    SPR_setDefinition(body, action->body);

    SPR_setPalette(body, PAL2);

    PAL_setPalette(PAL2, action->body->palette->data, DMA);

    SPR_setAutoAnimation(body, FALSE);

    current_frame = 0;
    frame_timer = 0;

    SPR_setFrame(body, 0);
    hide_fx(fx, dust);

    if (action->dust_on_contact) start_dust(dust);
    if ((action->fx != NULL) && (action->fx_start_frame == 0)) start_fx(fx, action->fx, action->fx_x, action->fx_y);
}

int main(bool hardReset)
{
    (void) hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setPalette(PAL0, img_hibrido_arena_stage_v012.palette->data, DMA);
    VDP_drawImageEx(BG_B, &img_hibrido_arena_stage_v012, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX), 0, 0, FALSE, DMA);
    VDP_setBackgroundColor(0);

    JOY_init();
    SPR_initEx(420);

    Sprite* body = SPR_addSprite(ACTIONS[0].body, 112, 88, TILE_ATTR(PAL2, 0, FALSE, FALSE));
    Sprite* fx = SPR_addSprite(&spr_hibrido_fx_hitspark_v010, 0, 0, TILE_ATTR(PAL3, 0, FALSE, FALSE));
    Sprite* dust = SPR_addSprite(&spr_hibrido_fx_dust_v010, 0, 0, TILE_ATTR(PAL3, 0, FALSE, FALSE));

    PAL_setPalette(PAL3, spr_hibrido_fx_hitspark_v010.palette->data, DMA);
    SPR_setVisibility(fx, HIDDEN);
    SPR_setVisibility(dust, HIDDEN);
    apply_action(body, fx, dust, 0);

    u16 prev = 0;

    while (TRUE)
    {
        u16 v = JOY_readJoypad(JOY_1);
        u16 pressed = (v ^ prev) & v;
        prev = v;

        if (pressed & BUTTON_RIGHT)
        {
            current_action = (current_action + 1) % ACTION_COUNT;
            apply_action(body, fx, dust, current_action);
            demo_timer = 0;
        }
        else if (pressed & BUTTON_LEFT)
        {
            current_action = (current_action == 0) ? (ACTION_COUNT - 1) : (current_action - 1);
            apply_action(body, fx, dust, current_action);
            demo_timer = 0;
        }
        else if (pressed & BUTTON_A)
        {
            current_action = 3;
            apply_action(body, fx, dust, current_action);
            demo_timer = 0;
        }
        else if (pressed & BUTTON_B)
        {
            current_action = 4;
            apply_action(body, fx, dust, current_action);
            demo_timer = 0;
        }
        else if (pressed & BUTTON_C)
        {
            current_action = 5;
            apply_action(body, fx, dust, current_action);
            demo_timer = 0;
        }
        else if (pressed & BUTTON_START)
        {
            current_action = 6;
            apply_action(body, fx, dust, current_action);
            demo_timer = 0;
        }

        demo_timer++;
        if (demo_timer >= 150)
        {
            demo_timer = 0;
            current_action = (current_action + 1) % ACTION_COUNT;
            apply_action(body, fx, dust, current_action);
        }

        frame_timer++;
        if (frame_timer >= 6)
        {
            frame_timer = 0;
            current_frame++;
            if (current_frame >= ACTIONS[current_action].frames) current_frame = 0;
            SPR_setFrame(body, current_frame);

            if ((ACTIONS[current_action].fx != NULL) && (current_frame == ACTIONS[current_action].fx_start_frame) && (fx_timer == 0))
            {
                start_fx(fx, ACTIONS[current_action].fx, ACTIONS[current_action].fx_x, ACTIONS[current_action].fx_y);
            }

            if (ACTIONS[current_action].dust_on_contact && ((current_frame == 0) || (current_frame == 3)) && (dust_timer == 0))
            {
                start_dust(dust);
            }
        }

        tick_fx(fx, dust);
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

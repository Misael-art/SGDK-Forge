#include <genesis.h>
#include "race_scene.h"
#include "scene_manager.h"
#include "input_abstraction.h"
#include "data/track_data.h"
#include "player/lane_movement.h"
#include "race/race_track.h"
#include "race/race_entities.h"
#include "race/race_resources.h"
#include "race/race_hud.h"
#include "race/race_collision.h"
#include "race/race_metrics.h"
#include "race/road_renderer.h"
#include "res/resources.h"

#define RSTATE_PLAYING 0
#define RSTATE_CLEAR 1
#define RSTATE_FAILED 2

#define ANIM_RUN   0
#define ANIM_JUMP  1
#define ANIM_DAMAGE 2
#define ANIM_PULSE 3
#define ANIM_IDLE  4
#define DAMAGE_FRAME_COUNT 3
#define DAMAGE_HOLD_FRAMES 6

static u8 race_state = 0;
static u16 result_timer = 0;
static u8 pulse_used_count = 0;
static u16 max_pressure_value = 0;
static bool event_spawned[18];
static u16 frame_counter = 0;
static bool beacon_collected = false;

static Sprite* player_sprite;
static Sprite* hazard_sprites[ENTITY_POOL_HAZARDS];
static Sprite* pickup_sprites[ENTITY_POOL_PICKUPS];

static bool set_sprite_definition_checked(Sprite* sprite, const SpriteDefinition* def)
{
    if (sprite == NULL)
    {
        return false;
    }
    if (sprite->definition == def)
    {
        return true;
    }
    return SPR_setDefinition(sprite, def);
}

static const u16 race_palette[64] = {
    RGB24_TO_VDPCOLOR(0x000018),
    RGB24_TO_VDPCOLOR(0x102850),
    RGB24_TO_VDPCOLOR(0x50C8FF),
    RGB24_TO_VDPCOLOR(0xF0F8FF),
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, RGB24_TO_VDPCOLOR(0xF0F8FF),
    RGB24_TO_VDPCOLOR(0x000000),
    RGB24_TO_VDPCOLOR(0xFFD8A0),
    RGB24_TO_VDPCOLOR(0x40C0FF),
    RGB24_TO_VDPCOLOR(0x2090C0),
    RGB24_TO_VDPCOLOR(0x3050C0),
    RGB24_TO_VDPCOLOR(0x1830A0),
    RGB24_TO_VDPCOLOR(0x2840B0),
    RGB24_TO_VDPCOLOR(0x142880),
    RGB24_TO_VDPCOLOR(0xFFD000),
    RGB24_TO_VDPCOLOR(0xC0A000),
    RGB24_TO_VDPCOLOR(0xFFFFFF),
    RGB24_TO_VDPCOLOR(0x4080FF),
    0,0,0,0,
    RGB24_TO_VDPCOLOR(0x303038),
    RGB24_TO_VDPCOLOR(0x505058),
    RGB24_TO_VDPCOLOR(0x404048),
    RGB24_TO_VDPCOLOR(0xC0C0C8),
    RGB24_TO_VDPCOLOR(0x282830),
    RGB24_TO_VDPCOLOR(0x383840),
    RGB24_TO_VDPCOLOR(0x080820),
    RGB24_TO_VDPCOLOR(0x101840),
    RGB24_TO_VDPCOLOR(0x101030),
    RGB24_TO_VDPCOLOR(0x181838),
    RGB24_TO_VDPCOLOR(0x181840),
    RGB24_TO_VDPCOLOR(0x0C1434),
    RGB24_TO_VDPCOLOR(0x000000),
    RGB24_TO_VDPCOLOR(0xFFCC00),
    RGB24_TO_VDPCOLOR(0xFF8800),
    RGB24_TO_VDPCOLOR(0xFFFF44),
    RGB24_TO_VDPCOLOR(0x884400),
    RGB24_TO_VDPCOLOR(0x888888),
    RGB24_TO_VDPCOLOR(0x555555),
    RGB24_TO_VDPCOLOR(0xAAAAAA),
    RGB24_TO_VDPCOLOR(0x444444),
    RGB24_TO_VDPCOLOR(0x4020A0),
    RGB24_TO_VDPCOLOR(0x8060FF),
    RGB24_TO_VDPCOLOR(0xC0A0FF),
    RGB24_TO_VDPCOLOR(0x201050),
    RGB24_TO_VDPCOLOR(0x40D0FF),
    RGB24_TO_VDPCOLOR(0x80FFFF),
    RGB24_TO_VDPCOLOR(0x2090C0)
};

static const SpriteDefinition* get_hazard_def(u8 kind)
{
    switch (kind)
    {
        case EV_LUMEN_ORB: return &spr_lumen_orb;
        case EV_LOW_STONE: return &spr_low_stone;
        case EV_ASTRAL_MARK:
        case EV_PULSE_TUTORIAL: return &spr_astral_mark;
        case EV_BEACON_KEY: return &spr_beacon_key;
        case EV_PURSUER_SHADOW: return &spr_pursuer_shadow;
        case EV_PRESSURE_GATE: return &spr_astral_mark;
        default: return &spr_low_stone;
    }
}

static u8 get_definition_frame_count(const SpriteDefinition* def)
{
    if ((def == NULL) || (def->numAnimation == 0) || (def->animations == NULL) ||
        (def->animations[0] == NULL))
    {
        return 1;
    }

    u8 num_frames = def->animations[0]->numFrame;
    return (num_frames == 0) ? 1 : num_frames;
}

static void draw_entities(void)
{
    for (u8 i = 0; i < ENTITY_POOL_HAZARDS; i++)
    {
        const Entity* e = Entities_getHazard(i);
        Sprite* sp = hazard_sprites[i];

        if (!e->active)
        {
            if (sp != NULL)
            {
                SPR_setVisibility(sp, HIDDEN);
            }
            continue;
        }
        if (sp == NULL)
        {
            continue;
        }

        const SpriteDefinition* def = get_hazard_def(e->kind);
        if (!set_sprite_definition_checked(sp, def))
        {
            SPR_setVisibility(sp, HIDDEN);
            continue;
        }

        s16 px = e->screen_x;
        s16 py = e->screen_y;

        if (e->kind == EV_LOW_STONE)
        {
            px -= 16;
        }
        else if (e->kind == EV_ASTRAL_MARK || e->kind == EV_PULSE_TUTORIAL)
        {
            px -= 20;
        }
        else if (e->kind == EV_PURSUER_SHADOW)
        {
            px -= 24;
            py -= 16;
        }
        else
        {
            px -= 8;
        }

        if (py < TRACK_PLAYFIELD_TOP)
        {
            SPR_setVisibility(sp, HIDDEN);
            continue;
        }

        SPR_setPosition(sp, px, py);
        SPR_setVisibility(sp, VISIBLE);

        u8 num_frames = get_definition_frame_count(def);
        u8 frame = (frame_counter / 8) % num_frames;
        SPR_setAnimAndFrame(sp, 0, frame);
    }

    for (u8 i = 0; i < ENTITY_POOL_PICKUPS; i++)
    {
        const Entity* e = Entities_getPickup(i);
        Sprite* sp = pickup_sprites[i];

        if (!e->active)
        {
            if (sp != NULL)
            {
                SPR_setVisibility(sp, HIDDEN);
            }
            continue;
        }
        if (sp == NULL)
        {
            continue;
        }

        const SpriteDefinition* def;
        if (e->kind == EV_BEACON_KEY)
        {
            def = &spr_beacon_key;
        }
        else
        {
            def = &spr_lumen_orb;
        }
        if (!set_sprite_definition_checked(sp, def))
        {
            SPR_setVisibility(sp, HIDDEN);
            continue;
        }

        s16 px = e->screen_x - 8;
        s16 py = e->screen_y - 8;

        if (py < TRACK_PLAYFIELD_TOP)
        {
            SPR_setVisibility(sp, HIDDEN);
            continue;
        }

        SPR_setPosition(sp, px, py);
        SPR_setVisibility(sp, VISIBLE);

        u8 num_frames = get_definition_frame_count(def);
        u8 frame = (frame_counter / 8) % num_frames;
        SPR_setAnimAndFrame(sp, 0, frame);
    }
}

static void draw_player(void)
{
    if (player_sprite == NULL)
    {
        return;
    }

    s16 px = Player_getScreenX();
    s16 py = Player_getScreenY();
    bool changing_state = false;

    px -= 12;
    py -= 28;

    if (Player_isInvulnerable())
    {
        /*
         * Damage owns the visual state while invulnerability is active.
         * The blink is sparse so the recoil frames remain observable.
         */
        SPR_setAnim(player_sprite, ANIM_DAMAGE);
        SPR_setFrame(player_sprite, (frame_counter / DAMAGE_HOLD_FRAMES) % DAMAGE_FRAME_COUNT);
        u8 blink = (frame_counter / 3) % 4;
        SPR_setVisibility(player_sprite, (blink == 0) ? HIDDEN : VISIBLE);
        changing_state = true;
    }
    else if (Player_isJumping())
    {
        SPR_setAnim(player_sprite, ANIM_JUMP);
        s16 phase = Player_getVisualYOffset();
        s16 jf = (phase == 0) ? 0 : (phase == -8) ? 1 : (phase == -16) ? 2 : (phase == -20) ? 3 : (phase == -12) ? 4 : 5;
        SPR_setFrame(player_sprite, jf);
        changing_state = true;
    }
    else if (Player_isPulseActive())
    {
        SPR_setAnim(player_sprite, ANIM_PULSE);
        SPR_setFrame(player_sprite, (frame_counter / 3) % 4);
        changing_state = true;
    }
    else if (Player_isChangingLane())
    {
        SPR_setAnim(player_sprite, ANIM_RUN);
        SPR_setFrame(player_sprite, (frame_counter / 4) % 6);
        changing_state = true;
    }

    if (!Player_isInvulnerable())
    {
        SPR_setVisibility(player_sprite, VISIBLE);
    }

    if (!changing_state && !Player_isInvulnerable())
    {
        SPR_setAnim(player_sprite, ANIM_RUN);
        SPR_setFrame(player_sprite, (frame_counter / 4) % 6);
    }

    if (player_sprite != NULL)
    {
        SPR_setPosition(player_sprite, px, py);
    }
}

static void draw_world(void)
{
    draw_entities();
    draw_player();
}

static void resolve_collisions(void)
{
    AABB hurtbox = Player_getHurtbox();
    AABB pickup_box = Player_getPickupBox();

    EntityCollisionData entities[16];
    u8 entity_count = Entities_getActiveCollisionData(entities, 16);

    bool pulse_active = Player_isPulseActive();

    for (u8 i = 0; i < entity_count; i++)
    {
        AABB entity_box;
        entity_box.x = entities[i].x;
        entity_box.y = entities[i].y;
        entity_box.w = entities[i].w;
        entity_box.h = entities[i].h;

        u8 layer = entities[i].layer;
        u8 kind = entities[i].kind;
        u8 eidx = entities[i].entity_index;

        if (layer == COLLISION_LAYER_TRIGGER && kind == EV_PRESSURE_GATE)
        {
            if (Collision_overlap(&hurtbox, &entity_box))
            {
                const Entity* trigger = Entities_getHazard(eidx);
                Resources_addPressure((trigger != NULL) ? (u8)trigger->value : 8);
                Entities_despawn(0, eidx);
            }
            continue;
        }

        if (pulse_active)
        {
            if (layer == COLLISION_LAYER_SOLID_HAZARD || layer == COLLISION_LAYER_LOW_HAZARD)
            {
                if (kind == EV_PULSE_TUTORIAL || kind == EV_LOW_STONE || kind == EV_ASTRAL_MARK)
                {
                    Entities_despawn(0, eidx);
                    continue;
                }
            }
        }

        if (layer == COLLISION_LAYER_PICKUP)
        {
            if (Collision_overlap(&pickup_box, &entity_box))
            {
                if (kind == EV_BEACON_KEY)
                {
                    Entities_despawn(1, eidx);
                    beacon_collected = true;
                    race_state = RSTATE_CLEAR;
                    result_timer = 90;
                    continue;
                }

                u8 value = 5;
                const Entity* ep = Entities_getPickup(eidx);
                if (ep != NULL)
                {
                    value = (u8)ep->value;
                }
                Resources_addLumen(value);
                Entities_despawn(1, eidx);
                continue;
            }
        }

        if (layer == COLLISION_LAYER_LOW_HAZARD || layer == COLLISION_LAYER_SOLID_HAZARD)
        {
            if (Player_isInvulnerable())
            {
                continue;
            }

            if (layer == COLLISION_LAYER_LOW_HAZARD && Player_isJumping())
            {
                continue;
            }

            if (Collision_overlap(&hurtbox, &entity_box))
            {
                if (race_state == RSTATE_PLAYING)
                {
                    Resources_applyDamage();
                    Player_applyDamage();

                    if (Resources_isDead())
                    {
                        race_state = RSTATE_FAILED;
                        result_timer = 120;
                    }
                }
                break;
            }
        }
    }
}

static void handle_pulse_input(void)
{
    if (race_state != RSTATE_PLAYING)
    {
        return;
    }

    if (!Player_isPulseActive() && (Player_getPulseTimer() == 0))
    {
        if (IO_getState(INPUT_ACTION_A).pressed)
        {
            if (Resources_usePulse())
            {
                Player_triggerPulse();
                pulse_used_count++;
            }
        }
    }
}

static void enter(void)
{
    race_state = RSTATE_PLAYING;
    result_timer = 0;
    pulse_used_count = 0;
    max_pressure_value = 0;
    frame_counter = 0;
    beacon_collected = false;

    for (u8 i = 0; i < 18; i++)
    {
        event_spawned[i] = false;
    }

    Player_init();
    Track_init();
    Entities_init();
    Resources_init();
    Hud_init();
    Metrics_init();
    Collision_init();

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setWindowVPos(FALSE, 3);
    VDP_setTextPlane(WINDOW);

    Road_init();
    Hud_drawStatic();

    player_sprite = SPR_addSprite(&spr_lio_all, 148, 140, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
    if (player_sprite != NULL)
    {
        SPR_setAnim(player_sprite, ANIM_RUN);
    }

    for (u8 i = 0; i < ENTITY_POOL_HAZARDS; i++)
    {
        hazard_sprites[i] = SPR_addSprite(&spr_low_stone, 0, 0, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
        if (hazard_sprites[i] != NULL)
        {
            SPR_setVisibility(hazard_sprites[i], HIDDEN);
        }
    }

    for (u8 i = 0; i < ENTITY_POOL_PICKUPS; i++)
    {
        pickup_sprites[i] = SPR_addSprite(&spr_lumen_orb, 0, 0, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
        if (pickup_sprites[i] != NULL)
        {
            SPR_setVisibility(pickup_sprites[i], HIDDEN);
        }
    }
}

static void update(void)
{
    frame_counter++;

    if (race_state == RSTATE_CLEAR || race_state == RSTATE_FAILED)
    {
        if (result_timer > 0)
        {
            result_timer--;
        }
        else
        {
            u8 final_int = Resources_getIntegrity();
            u8 final_lum = Resources_getLumen();
            u16 final_prs = Resources_getPressure();
            if (max_pressure_value < final_prs)
            {
                max_pressure_value = final_prs;
            }
            Metrics_raceComplete(final_int, final_lum, max_pressure_value, pulse_used_count, race_state == RSTATE_CLEAR);
            SM_requestTransition(APP_SCENE_RESULT);
        }
        return;
    }

    Player_update();
    Resources_update();

    handle_pulse_input();

    Track_update();

    u16 current_frame = Track_getFrame();

    u8 active_count = Track_getActiveEventCount();
    for (u8 i = 0; i < active_count; i++)
    {
        u8 ei = Track_getActiveEventIndex(i);
        if (ei >= 18)
        {
            continue;
        }
        if (event_spawned[ei])
        {
            continue;
        }
        const TrackEvent* ev = Track_getActiveEvent(i);
        if (ev == NULL)
        {
            continue;
        }
        event_spawned[ei] = true;
        Entities_spawnFromEvent(ev, current_frame);
    }

    s32 raw_scroll = Track_getScrollX();
    Entities_update(current_frame, (u16)raw_scroll);

    resolve_collisions();

    u16 pressure_rate = Track_getPressureRate();
    Resources_updatePressure(pressure_rate);

    u16 cur_pressure = Resources_getPressure();
    if (cur_pressure > max_pressure_value)
    {
        max_pressure_value = cur_pressure;
    }

    if (cur_pressure >= 100)
    {
        race_state = RSTATE_FAILED;
        result_timer = 120;
    }

    if (Track_isComplete() && (race_state == RSTATE_PLAYING))
    {
        race_state = beacon_collected ? RSTATE_CLEAR : RSTATE_FAILED;
        result_timer = beacon_collected ? 90 : 120;
    }

    {
        ResourceState res_state;
        res_state.integrity = Resources_getIntegrity();
        res_state.lumen = Resources_getLumen();
        res_state.pressure = Resources_getPressure();
        res_state.lumen_band = Resources_getLumenBand();
        res_state.pulse_cooldown = 0;
        res_state.pulse_active = 0;
        res_state.focus = 0;
        res_state.pressure_accumulator = 0;
        Hud_update(&res_state, Resources_isPulseReady());
    }

    Metrics_frameEnd(Resources_getPressure());

    Road_update(raw_scroll << 2);
    draw_world();
}

static void exit(void)
{
    if (player_sprite != NULL)
    {
        SPR_releaseSprite(player_sprite);
    }
    player_sprite = NULL;

    for (u8 i = 0; i < ENTITY_POOL_HAZARDS; i++)
    {
        if (hazard_sprites[i] != NULL)
        {
            SPR_releaseSprite(hazard_sprites[i]);
        }
        hazard_sprites[i] = NULL;
    }

    for (u8 i = 0; i < ENTITY_POOL_PICKUPS; i++)
    {
        if (pickup_sprites[i] != NULL)
        {
            SPR_releaseSprite(pickup_sprites[i]);
        }
        pickup_sprites[i] = NULL;
    }

    Entities_clearAll();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setWindowVPos(FALSE, 0);
    VDP_setTextPlane(BG_A);
    VDP_setTextPriority(FALSE);
}

const Scene race_scene = {
    .enter = enter,
    .update = update,
    .exit = exit,
    .palette = race_palette,
    .enterFade = true,
    .exitFade = false
};

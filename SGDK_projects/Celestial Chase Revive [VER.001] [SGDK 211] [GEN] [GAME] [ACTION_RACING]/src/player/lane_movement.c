#include "player/lane_movement.h"
#include "input_abstraction.h"

static u8 current_lane = 1;
static u8 target_lane = 1;
static u8 lane_change_timer = 0;
static s16 visual_x_offset = 0;
static s16 visual_y_offset = 0;
static u8 jump_timer = 0;
static u8 damage_timer = 0;
static u8 damage_blink_toggle = 0;
static u8 pulse_timer = 0;
static u8 pulse_active = 0;
static u8 pulse_cooldown = 0;

static const s16 lane_x_px[TRACK_LANES] = {
    TRACK_LANE_X_PX_0, TRACK_LANE_X_PX_1, TRACK_LANE_X_PX_2
};

static const s16 lane_change_curve_left[4] = { 0, -8, -24, -48 };
static const s16 lane_change_curve_right[4] = { 0, 8, 24, 48 };
static const s16 jump_curve[6] = { 0, -8, -16, -20, -12, 0 };

void Player_init(void)
{
    current_lane = 1;
    target_lane = 1;
    lane_change_timer = 0;
    visual_x_offset = 0;
    visual_y_offset = 0;
    jump_timer = 0;
    damage_timer = 0;
    damage_blink_toggle = 0;
    pulse_timer = 0;
    pulse_active = 0;
    pulse_cooldown = 0;
}

bool Player_canAct(void)
{
    return (jump_timer == 0) && (lane_change_timer == 0) &&
           (damage_timer == 0) && (pulse_timer == 0);
}

void Player_update(void)
{
    if (pulse_cooldown > 0)
    {
        pulse_cooldown--;
    }

    if (pulse_timer > 0)
    {
        pulse_timer--;
        if ((pulse_timer > PLAYER_PULSE_ACTIVE) && (pulse_timer <= (PLAYER_PULSE_STARTUP + PLAYER_PULSE_ACTIVE)))
        {
            pulse_active = 1;
        }
        else
        {
            pulse_active = 0;
        }
    }

    if (Player_canAct())
    {
        if (IO_getState(INPUT_ACTION_UP).pressed && (current_lane > 0))
        {
            target_lane = current_lane - 1;
            lane_change_timer = PLAYER_LANE_CHANGE_FRAMES;
            visual_x_offset = 0;
        }
        if (IO_getState(INPUT_ACTION_DOWN).pressed && (current_lane < 2))
        {
            target_lane = current_lane + 1;
            lane_change_timer = PLAYER_LANE_CHANGE_FRAMES;
            visual_x_offset = 0;
        }
        if (IO_getState(INPUT_ACTION_B).pressed)
        {
            jump_timer = PLAYER_JUMP_DURATION_FRAMES;
        }
    }

    if (lane_change_timer > 0)
    {
        lane_change_timer--;
        u8 phase = 3 - (lane_change_timer / 2);
        if (phase > 3)
        {
            phase = 3;
        }
        if (target_lane < current_lane)
        {
            visual_x_offset = lane_change_curve_left[phase];
        }
        else
        {
            visual_x_offset = lane_change_curve_right[phase];
        }
        if (lane_change_timer == 0)
        {
            current_lane = target_lane;
            visual_x_offset = 0;
        }
    }

    if (jump_timer > 0)
    {
        jump_timer--;
        u8 phase = (PLAYER_JUMP_DURATION_FRAMES - 1 - jump_timer) / 6;
        if (phase > 5)
        {
            phase = 5;
        }
        visual_y_offset = jump_curve[phase];
    }

    if (damage_timer > 0)
    {
        damage_timer--;
        if ((damage_timer % 4) == 0)
        {
            damage_blink_toggle = !damage_blink_toggle;
        }
    }
}

s16 Player_getScreenX(void)
{
    return lane_x_px[current_lane] + visual_x_offset;
}

s16 Player_getScreenY(void)
{
    return TRACK_PLAYER_Y_PX + visual_y_offset;
}

u8 Player_getLane(void)
{
    return current_lane;
}

bool Player_isJumping(void)
{
    return jump_timer > 0;
}

bool Player_isInvulnerable(void)
{
    return damage_timer > 0;
}

AABB Player_getHurtbox(void)
{
    AABB box;
    box.x = Player_getScreenX() + PLAYER_HURTBOX_X;
    box.y = Player_getScreenY() + PLAYER_HURTBOX_Y;
    box.w = PLAYER_HURTBOX_W;
    box.h = PLAYER_HURTBOX_H;
    return box;
}

AABB Player_getPickupBox(void)
{
    AABB box;
    box.x = Player_getScreenX() + PLAYER_PICKUPBOX_X;
    box.y = Player_getScreenY() + PLAYER_PICKUPBOX_Y;
    box.w = PLAYER_PICKUPBOX_W;
    box.h = PLAYER_PICKUPBOX_H;
    return box;
}

bool Player_isOnGround(void)
{
    return jump_timer == 0;
}

bool Player_isPulseActive(void)
{
    return pulse_active > 0;
}

u8 Player_getPulseTimer(void)
{
    return pulse_timer;
}

void Player_applyDamage(void)
{
    damage_timer = PLAYER_DAMAGE_INVULN_FRAMES;
    damage_blink_toggle = 0;
}

void Player_triggerPulse(void)
{
    pulse_timer = PLAYER_PULSE_TOTAL;
    pulse_active = 0;
    pulse_cooldown = PLAYER_PULSE_COOLDOWN_FRAMES;
}

bool Player_isChangingLane(void)
{
    return lane_change_timer > 0;
}

s16 Player_getVisualXOffset(void)
{
    return visual_x_offset;
}

s16 Player_getVisualYOffset(void)
{
    return visual_y_offset;
}

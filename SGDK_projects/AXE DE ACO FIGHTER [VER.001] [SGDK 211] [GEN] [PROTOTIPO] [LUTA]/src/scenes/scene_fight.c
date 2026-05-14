#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/scene_fight.h"
#include "system/input.h"

#define GROUND_Y 176
#define MARINA_PIVOT_X 40
#define BENTO_PIVOT_X 44
#define FIGHTER_PIVOT_Y 76
#define STAGE_MIN_X 34
#define STAGE_MAX_X 286
#define START_HP 100
#define ROUND_TIME_START 99
#define DASH_TAP_WINDOW 16

typedef enum FighterState {
    FIGHTER_IDLE = 0,
    FIGHTER_WALK_FORWARD,
    FIGHTER_WALK_BACK,
    FIGHTER_DASH,
    FIGHTER_CROUCH,
    FIGHTER_HOP,
    FIGHTER_GUARD,
    FIGHTER_LIGHT_ATTACK,
    FIGHTER_MEDIUM_ATTACK,
    FIGHTER_SWEEP_OR_THROW,
    FIGHTER_HURT,
    FIGHTER_KNOCKDOWN,
    FIGHTER_GETUP,
    FIGHTER_STATE_COUNT
} FighterState;

typedef struct Fighter {
    Sprite* sprite;
    const SpriteDefinition* const* defs;
    FighterState state;
    s16 x;
    u16 hp;
    u16 stateTimer;
    u16 aiTimer;
    u16 attackLanded;
    bool facingRight;
    bool bentoBody;
} Fighter;

static const SpriteDefinition* const s_marinaDefs[FIGHTER_STATE_COUNT] = {
    &spr_marina_idle,
    &spr_marina_walk_forward,
    &spr_marina_walk_back,
    &spr_marina_dash,
    &spr_marina_crouch,
    &spr_marina_hop,
    &spr_marina_guard,
    &spr_marina_light_attack,
    &spr_marina_medium_attack,
    &spr_marina_sweep_or_throw,
    &spr_marina_hurt,
    &spr_marina_knockdown,
    &spr_marina_getup
};

static const SpriteDefinition* const s_bentoDefs[FIGHTER_STATE_COUNT] = {
    &spr_bento_idle,
    &spr_bento_walk_forward,
    &spr_bento_walk_back,
    &spr_bento_dash,
    &spr_bento_crouch,
    &spr_bento_hop,
    &spr_bento_guard,
    &spr_bento_light_attack,
    &spr_bento_medium_attack,
    &spr_bento_sweep_or_throw,
    &spr_bento_hurt,
    &spr_bento_knockdown,
    &spr_bento_getup
};

static Fighter s_p1;
static Fighter s_p2;
static Sprite* s_hitSpark;
static Sprite* s_dust;
static u16 s_roundTimer;
static u16 s_timerTick;
static u16 s_roundPause;
static u16 s_shakeTimer;
static u16 s_fxTimer;
static u16 s_soundTimer;
static s16 s_fxX;
static s16 s_fxY;
static u32 s_lastLeftTap;
static u32 s_lastRightTap;

static s16 abs_s16(s16 value)
{
    return (value < 0) ? (s16)-value : value;
}

static s16 facing_dir(const Fighter* fighter)
{
    return fighter->facingRight ? 1 : -1;
}

static u16 fighter_pivot_x(const Fighter* fighter)
{
    return fighter->bentoBody ? BENTO_PIVOT_X : MARINA_PIVOT_X;
}

static bool state_is_locked(FighterState state)
{
    return (state == FIGHTER_DASH) ||
           (state == FIGHTER_HOP) ||
           (state == FIGHTER_LIGHT_ATTACK) ||
           (state == FIGHTER_MEDIUM_ATTACK) ||
           (state == FIGHTER_SWEEP_OR_THROW) ||
           (state == FIGHTER_HURT) ||
           (state == FIGHTER_KNOCKDOWN) ||
           (state == FIGHTER_GETUP);
}

static bool state_is_attack(FighterState state)
{
    return (state == FIGHTER_LIGHT_ATTACK) ||
           (state == FIGHTER_MEDIUM_ATTACK) ||
           (state == FIGHTER_SWEEP_OR_THROW);
}

static void set_state(Fighter* fighter, FighterState state)
{
    if (fighter->state == state) return;

    fighter->state = state;
    fighter->stateTimer = 0;
    fighter->attackLanded = FALSE;

    if (fighter->sprite)
    {
        SPR_setDefinition(fighter->sprite, fighter->defs[state]);
        SPR_setAnimAndFrame(fighter->sprite, 0, 0);
    }
}

static void clamp_fighter(Fighter* fighter)
{
    if (fighter->x < STAGE_MIN_X) fighter->x = STAGE_MIN_X;
    if (fighter->x > STAGE_MAX_X) fighter->x = STAGE_MAX_X;
}

static void face_each_other(void)
{
    s_p1.facingRight = (s_p1.x <= s_p2.x);
    s_p2.facingRight = (s_p2.x < s_p1.x);
}

static void separate_fighters(void)
{
    if (s_p1.x > (s_p2.x - 30))
    {
        s16 mid = (s_p1.x + s_p2.x) / 2;
        s_p1.x = mid - 15;
        s_p2.x = mid + 15;
    }
    clamp_fighter(&s_p1);
    clamp_fighter(&s_p2);
}

static void draw_bar(char* line, const char* leftName, u16 leftHp, const char* rightName, u16 rightHp)
{
    char lbar[13];
    char rbar[13];
    u16 i;
    u16 leftBlocks = (leftHp + 7) / 8;
    u16 rightBlocks = (rightHp + 7) / 8;

    if (leftBlocks > 12) leftBlocks = 12;
    if (rightBlocks > 12) rightBlocks = 12;

    for (i = 0; i < 12; i++)
    {
        lbar[i] = (i < leftBlocks) ? '#' : '-';
        rbar[i] = (i < rightBlocks) ? '#' : '-';
    }
    lbar[12] = 0;
    rbar[12] = 0;

    sprintf(line, "%s[%s] %02u [%s]%s", leftName, lbar, s_roundTimer, rbar, rightName);
}

static void draw_hud(void)
{
    char line[41];

    VDP_drawTextFill("MARINA R. RODA     AXE DE ACO     BENTO", 0, 0, 40);
    draw_bar(line, "P1", s_p1.hp, "P2", s_p2.hp);
    VDP_drawTextFill(line, 0, 1, 40);

    if (s_roundPause)
    {
        if (s_p1.hp == 0 && s_p2.hp == 0)
            VDP_drawTextFill("                EMPATE                  ", 0, 3, 40);
        else if (s_p2.hp == 0)
            VDP_drawTextFill("             MARINA VENCE               ", 0, 3, 40);
        else if (s_p1.hp == 0)
            VDP_drawTextFill("              BENTO VENCE               ", 0, 3, 40);
        else
            VDP_drawTextFill("              TEMPO ESGOTADO            ", 0, 3, 40);
    }
    else
    {
        VDP_clearTextArea(0, 3, 40, 1);
    }
}

static void start_hit_fx(s16 x, s16 y, bool strong)
{
    s_fxX = x;
    s_fxY = y;
    s_fxTimer = strong ? 18 : 12;
    s_shakeTimer = strong ? 10 : 4;
    s_soundTimer = strong ? 10 : 6;

    if (s_hitSpark)
    {
        SPR_setVisibility(s_hitSpark, VISIBLE);
        SPR_setAnimAndFrame(s_hitSpark, 0, 0);
    }
    if (s_dust)
    {
        SPR_setVisibility(s_dust, VISIBLE);
        SPR_setAnimAndFrame(s_dust, 0, 0);
    }

    PSG_setFrequency(0, strong ? 220 : 440);
    PSG_setEnvelope(0, strong ? 2 : 5);
    PSG_setNoise(PSG_NOISE_TYPE_WHITE, PSG_NOISE_FREQ_CLOCK8);
    PSG_setEnvelope(3, strong ? 4 : 8);
}

static bool attack_is_active(const Fighter* attacker)
{
    switch (attacker->state)
    {
        case FIGHTER_LIGHT_ATTACK:
            return attacker->stateTimer >= 5 && attacker->stateTimer <= 12;
        case FIGHTER_MEDIUM_ATTACK:
            return attacker->stateTimer >= 7 && attacker->stateTimer <= 18;
        case FIGHTER_SWEEP_OR_THROW:
            return attacker->stateTimer >= 8 && attacker->stateTimer <= 24;
        default:
            return FALSE;
    }
}

static u16 attack_damage(FighterState state)
{
    switch (state)
    {
        case FIGHTER_LIGHT_ATTACK: return 5;
        case FIGHTER_MEDIUM_ATTACK: return 9;
        case FIGHTER_SWEEP_OR_THROW: return 12;
        default: return 0;
    }
}

static s16 attack_range(FighterState state)
{
    switch (state)
    {
        case FIGHTER_LIGHT_ATTACK: return 42;
        case FIGHTER_MEDIUM_ATTACK: return 56;
        case FIGHTER_SWEEP_OR_THROW: return 62;
        default: return 0;
    }
}

static void apply_damage(Fighter* attacker, Fighter* victim)
{
    u16 damage = attack_damage(attacker->state);
    bool guarded = (victim->state == FIGHTER_GUARD);
    bool sweep = (attacker->state == FIGHTER_SWEEP_OR_THROW);
    s16 push = facing_dir(attacker) * (sweep ? 18 : 10);

    if (guarded && !sweep)
    {
        damage = 1;
        push = facing_dir(attacker) * 5;
        set_state(victim, FIGHTER_GUARD);
    }
    else if (sweep)
    {
        set_state(victim, FIGHTER_KNOCKDOWN);
    }
    else
    {
        set_state(victim, FIGHTER_HURT);
    }

    victim->hp = (victim->hp > damage) ? (victim->hp - damage) : 0;
    victim->x += push;
    attacker->x -= facing_dir(attacker) * 2;
    clamp_fighter(victim);
    clamp_fighter(attacker);
    start_hit_fx((attacker->x + victim->x) / 2, GROUND_Y - 48, sweep || attacker->state == FIGHTER_MEDIUM_ATTACK);
}

static void check_attack(Fighter* attacker, Fighter* victim)
{
    s16 dx;

    if (!state_is_attack(attacker->state)) return;
    if (!attack_is_active(attacker)) return;
    if (attacker->attackLanded) return;
    if (victim->state == FIGHTER_KNOCKDOWN || victim->state == FIGHTER_GETUP) return;

    dx = attacker->facingRight ? (victim->x - attacker->x) : (attacker->x - victim->x);
    if (dx > 0 && dx <= attack_range(attacker->state))
    {
        attacker->attackLanded = TRUE;
        apply_damage(attacker, victim);
    }
}

static void update_p1_control(void)
{
    bool left = INPUT_held(BUTTON_LEFT);
    bool right = INPUT_held(BUTTON_RIGHT);
    bool down = INPUT_held(BUTTON_DOWN);
    bool dashPressed = INPUT_pressed(BUTTON_X);
    bool doubleTapLeft = FALSE;
    bool doubleTapRight = FALSE;

    if (state_is_locked(s_p1.state)) return;

    if (INPUT_pressed(BUTTON_LEFT))
    {
        doubleTapLeft = (s_lastLeftTap != 0) && ((gApp.totalFrames - s_lastLeftTap) <= DASH_TAP_WINDOW);
        s_lastLeftTap = gApp.totalFrames;
    }
    if (INPUT_pressed(BUTTON_RIGHT))
    {
        doubleTapRight = (s_lastRightTap != 0) && ((gApp.totalFrames - s_lastRightTap) <= DASH_TAP_WINDOW);
        s_lastRightTap = gApp.totalFrames;
    }

    if (INPUT_pressed(BUTTON_A))
    {
        set_state(&s_p1, FIGHTER_LIGHT_ATTACK);
        return;
    }
    if (INPUT_pressed(BUTTON_B))
    {
        set_state(&s_p1, FIGHTER_MEDIUM_ATTACK);
        return;
    }
    if (INPUT_pressed(BUTTON_Y))
    {
        set_state(&s_p1, FIGHTER_SWEEP_OR_THROW);
        return;
    }
    if (INPUT_pressed(BUTTON_UP))
    {
        set_state(&s_p1, FIGHTER_HOP);
        return;
    }
    if (dashPressed || doubleTapLeft || doubleTapRight)
    {
        set_state(&s_p1, FIGHTER_DASH);
        return;
    }
    if (INPUT_held(BUTTON_C))
    {
        set_state(&s_p1, FIGHTER_GUARD);
        return;
    }
    if (down)
    {
        set_state(&s_p1, FIGHTER_CROUCH);
        return;
    }
    if (left && !right)
    {
        s_p1.x -= 2;
        set_state(&s_p1, s_p1.facingRight ? FIGHTER_WALK_BACK : FIGHTER_WALK_FORWARD);
        return;
    }
    if (right && !left)
    {
        s_p1.x += 2;
        set_state(&s_p1, s_p1.facingRight ? FIGHTER_WALK_FORWARD : FIGHTER_WALK_BACK);
        return;
    }

    set_state(&s_p1, FIGHTER_IDLE);
}

static void update_p2_ai(void)
{
    s16 distance = abs_s16(s_p2.x - s_p1.x);
    s16 dir = (s_p1.x > s_p2.x) ? 1 : -1;
    u16 choice;

    if (state_is_locked(s_p2.state)) return;

    if (s_p2.aiTimer > 0)
    {
        s_p2.aiTimer--;
    }

    if (distance > 74)
    {
        s_p2.x += dir * 2;
        set_state(&s_p2, FIGHTER_WALK_FORWARD);
        return;
    }

    if (distance < 42)
    {
        if ((gApp.sceneFrames & 31) < 12)
        {
            set_state(&s_p2, FIGHTER_GUARD);
        }
        else
        {
            s_p2.x -= dir * 2;
            set_state(&s_p2, FIGHTER_WALK_BACK);
        }
        return;
    }

    if (s_p2.aiTimer == 0)
    {
        choice = (gApp.sceneFrames / 47) % 4;
        if (choice == 0) set_state(&s_p2, FIGHTER_LIGHT_ATTACK);
        else if (choice == 1) set_state(&s_p2, FIGHTER_MEDIUM_ATTACK);
        else if (choice == 2) set_state(&s_p2, FIGHTER_SWEEP_OR_THROW);
        else set_state(&s_p2, FIGHTER_GUARD);
        s_p2.aiTimer = 48;
        return;
    }

    set_state(&s_p2, FIGHTER_IDLE);
}

static void update_state_machine(Fighter* fighter)
{
    switch (fighter->state)
    {
        case FIGHTER_DASH:
            fighter->x += facing_dir(fighter) * 5;
            if (fighter->stateTimer >= 13) set_state(fighter, FIGHTER_IDLE);
            break;
        case FIGHTER_HOP:
            if (fighter->stateTimer >= 24) set_state(fighter, FIGHTER_IDLE);
            break;
        case FIGHTER_LIGHT_ATTACK:
            if (fighter->stateTimer >= 21) set_state(fighter, FIGHTER_IDLE);
            break;
        case FIGHTER_MEDIUM_ATTACK:
            if (fighter->stateTimer >= 30) set_state(fighter, FIGHTER_IDLE);
            break;
        case FIGHTER_SWEEP_OR_THROW:
            if (fighter->stateTimer >= 38) set_state(fighter, FIGHTER_IDLE);
            break;
        case FIGHTER_HURT:
            if (fighter->stateTimer >= 17) set_state(fighter, fighter->hp ? FIGHTER_IDLE : FIGHTER_KNOCKDOWN);
            break;
        case FIGHTER_KNOCKDOWN:
            if (fighter->stateTimer >= 44 && fighter->hp > 0) set_state(fighter, FIGHTER_GETUP);
            break;
        case FIGHTER_GETUP:
            if (fighter->stateTimer >= 36) set_state(fighter, FIGHTER_IDLE);
            break;
        default:
            break;
    }

    clamp_fighter(fighter);
    fighter->stateTimer++;
}

static void update_fx(void)
{
    if (s_soundTimer > 0)
    {
        s_soundTimer--;
        if (s_soundTimer == 0)
        {
            PSG_setEnvelope(0, PSG_ENVELOPE_MIN);
            PSG_setEnvelope(3, PSG_ENVELOPE_MIN);
        }
    }

    if (s_fxTimer > 0)
    {
        u16 frame = (18 - s_fxTimer) >> 2;
        if (frame > 3) frame = 3;

        s_fxTimer--;
        if (s_hitSpark)
        {
            SPR_setVisibility(s_hitSpark, VISIBLE);
            SPR_setFrame(s_hitSpark, frame);
            SPR_setPosition(s_hitSpark, s_fxX - 16, s_fxY - 16);
        }
        if (s_dust)
        {
            SPR_setVisibility(s_dust, VISIBLE);
            SPR_setFrame(s_dust, frame);
            SPR_setPosition(s_dust, s_fxX - 12, GROUND_Y - 14);
        }
    }
    else
    {
        if (s_hitSpark) SPR_setVisibility(s_hitSpark, HIDDEN);
        if (s_dust) SPR_setVisibility(s_dust, HIDDEN);
    }

    if (s_shakeTimer > 0)
    {
        s_shakeTimer--;
    }
}

static void update_sprite_positions(void)
{
    s16 shake = (s_shakeTimer > 0) ? ((gApp.totalFrames & 1) ? 2 : -2) : 0;

    VDP_setHorizontalScroll(BG_A, shake);
    VDP_setHorizontalScroll(BG_B, shake / 2);

    if (s_p1.sprite)
    {
        SPR_setHFlip(s_p1.sprite, !s_p1.facingRight);
        SPR_setPosition(s_p1.sprite, s_p1.x - fighter_pivot_x(&s_p1) + shake, GROUND_Y - FIGHTER_PIVOT_Y);
    }
    if (s_p2.sprite)
    {
        SPR_setHFlip(s_p2.sprite, !s_p2.facingRight);
        SPR_setPosition(s_p2.sprite, s_p2.x - fighter_pivot_x(&s_p2) + shake, GROUND_Y - FIGHTER_PIVOT_Y);
    }
}

static void reset_round(void)
{
    s_p1.x = 84;
    s_p2.x = 236;
    s_p1.hp = START_HP;
    s_p2.hp = START_HP;
    s_p1.aiTimer = 0;
    s_p2.aiTimer = 44;
    s_p1.attackLanded = FALSE;
    s_p2.attackLanded = FALSE;
    s_p1.state = FIGHTER_STATE_COUNT;
    s_p2.state = FIGHTER_STATE_COUNT;
    s_p1.stateTimer = 0;
    s_p2.stateTimer = 0;
    s_roundTimer = ROUND_TIME_START;
    s_timerTick = 0;
    s_roundPause = 0;
    s_shakeTimer = 0;
    s_fxTimer = 0;
    s_soundTimer = 0;
    s_lastLeftTap = 0;
    s_lastRightTap = 0;
    face_each_other();
    set_state(&s_p1, FIGHTER_IDLE);
    set_state(&s_p2, FIGHTER_IDLE);
}

static void load_stage(void)
{
    u16 tileIndex = TILE_USER_INDEX;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setPalette(PAL0, img_stage_bg_b.palette->data, DMA);
    PAL_setPalette(PAL1, spr_marina_idle.palette->data, DMA);
    PAL_setPalette(PAL2, spr_bento_idle.palette->data, DMA);
    PAL_setPalette(PAL3, spr_hit_spark.palette->data, DMA);
    VDP_drawImageEx(BG_B, &img_stage_bg_b, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, tileIndex), 0, 0, FALSE, TRUE);
    tileIndex += img_stage_bg_b.tileset->numTile;
    VDP_drawImageEx(BG_A, &img_stage_bg_a, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, tileIndex), 0, 0, FALSE, TRUE);
}

void SCENE_fightEnter(void)
{
    load_stage();

    s_p1.defs = s_marinaDefs;
    s_p2.defs = s_bentoDefs;
    s_p1.bentoBody = FALSE;
    s_p2.bentoBody = TRUE;

    s_p1.sprite = SPR_addSprite(&spr_marina_idle, 84 - MARINA_PIVOT_X, GROUND_Y - FIGHTER_PIVOT_Y, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    s_p2.sprite = SPR_addSprite(&spr_bento_idle, 236 - BENTO_PIVOT_X, GROUND_Y - FIGHTER_PIVOT_Y, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    s_hitSpark = SPR_addSprite(&spr_hit_spark, 160, 100, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
    s_dust = SPR_addSprite(&spr_dust, 160, 160, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));

    if (s_hitSpark) SPR_setVisibility(s_hitSpark, HIDDEN);
    if (s_dust) SPR_setVisibility(s_dust, HIDDEN);

    reset_round();
    VDP_setTextPalette(PAL3);
    VDP_setTextPriority(TRUE);
    draw_hud();
}

void SCENE_fightUpdate(void)
{
    if (s_roundPause)
    {
        s_roundPause--;
        update_fx();
        update_sprite_positions();
        draw_hud();
        if (s_roundPause == 0)
        {
            reset_round();
        }
        return;
    }

    face_each_other();
    update_p1_control();
    update_p2_ai();
    update_state_machine(&s_p1);
    update_state_machine(&s_p2);
    separate_fighters();
    face_each_other();
    check_attack(&s_p1, &s_p2);
    check_attack(&s_p2, &s_p1);
    update_fx();
    update_sprite_positions();

    s_timerTick++;
    if (s_timerTick >= 60)
    {
        s_timerTick = 0;
        if (s_roundTimer > 0) s_roundTimer--;
    }

    if (s_p1.hp == 0 || s_p2.hp == 0 || s_roundTimer == 0)
    {
        if (s_p1.hp == 0) set_state(&s_p1, FIGHTER_KNOCKDOWN);
        if (s_p2.hp == 0) set_state(&s_p2, FIGHTER_KNOCKDOWN);
        s_roundPause = 150;
    }

    draw_hud();
}

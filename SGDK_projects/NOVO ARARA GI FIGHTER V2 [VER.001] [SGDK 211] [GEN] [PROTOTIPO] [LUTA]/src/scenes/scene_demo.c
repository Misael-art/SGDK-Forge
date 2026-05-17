#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/input.h"

#define SCREEN_W 320
#define FIGHTER_W 96
#define FIGHTER_H 112
#define GROUND_Y 92
#define MIN_X 8
#define MAX_X 216
#define LIFE_MAX 96
#define HIT_RANGE_CLOSE 58
#define HIT_RANGE_STRIKE 72
#define MAX_STATE_FRAMES 8
#define ROUND_SECONDS 99

typedef enum FighterState {
    FIGHTER_IDLE = 0,
    FIGHTER_WALK_FORWARD,
    FIGHTER_WALK_BACK,
    FIGHTER_DASH,
    FIGHTER_CROUCH,
    FIGHTER_JUMP,
    FIGHTER_GUARD,
    FIGHTER_JAB,
    FIGHTER_MEDIUM,
    FIGHTER_GRIP,
    FIGHTER_HIP_THROW,
    FIGHTER_HURT,
    FIGHTER_KNOCKDOWN,
    FIGHTER_GETUP,
    FIGHTER_STATE_COUNT
} FighterState;

typedef struct Fighter {
    Sprite* sprite;
    const SpriteDefinition* const* defs;
    FighterState state;
    FighterState previousState;
    s16 x;
    s16 y;
    s16 vx;
    bool facingRight;
    s16 life;
    u16 frameTimer;
    u16 animFrame;
    u16 stateFrames;
    bool attackDidHit;
} Fighter;

static const SpriteDefinition* const sCaioDefs[FIGHTER_STATE_COUNT] = {
    &spr_caio_idle,
    &spr_caio_walk_forward,
    &spr_caio_walk_back,
    &spr_caio_dash,
    &spr_caio_crouch,
    &spr_caio_jump,
    &spr_caio_guard,
    &spr_caio_jab,
    &spr_caio_medium,
    &spr_caio_grip,
    &spr_caio_hip_throw,
    &spr_caio_hurt,
    &spr_caio_knockdown,
    &spr_caio_getup,
};

static const SpriteDefinition* const sDaviDefs[FIGHTER_STATE_COUNT] = {
    &spr_davi_idle,
    &spr_davi_walk_forward,
    &spr_davi_walk_back,
    &spr_davi_dash,
    &spr_davi_crouch,
    &spr_davi_jump,
    &spr_davi_guard,
    &spr_davi_jab,
    &spr_davi_medium,
    &spr_davi_grip,
    &spr_davi_hip_throw,
    &spr_davi_hurt,
    &spr_davi_knockdown,
    &spr_davi_getup,
};

static const u8 sFrameCounts[FIGHTER_STATE_COUNT] = {
    6, 6, 6, 4, 2, 6, 3, 4, 5, 5, 8, 4, 6, 6
};

static const bool sLooping[FIGHTER_STATE_COUNT] = {
    TRUE, TRUE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE
};

static const u8 sFrameDurations[FIGHTER_STATE_COUNT][MAX_STATE_FRAMES] = {
    { 8, 6, 7, 8, 6, 7, 0, 0 },
    { 5, 4, 5, 5, 4, 5, 0, 0 },
    { 5, 5, 4, 5, 5, 4, 0, 0 },
    { 3, 3, 4, 6, 0, 0, 0, 0 },
    { 5, 8, 0, 0, 0, 0, 0, 0 },
    { 4, 5, 6, 5, 4, 5, 0, 0 },
    { 5, 8, 6, 0, 0, 0, 0, 0 },
    { 3, 2, 3, 6, 0, 0, 0, 0 },
    { 4, 4, 2, 4, 7, 0, 0, 0 },
    { 5, 4, 3, 5, 8, 0, 0, 0 },
    { 5, 4, 4, 2, 4, 5, 6, 8 },
    { 3, 5, 5, 7, 0, 0, 0, 0 },
    { 4, 5, 5, 8, 10, 14, 0, 0 },
    { 8, 8, 7, 6, 5, 8, 0, 0 },
};

static const u8 sActiveStart[FIGHTER_STATE_COUNT] = {
    255, 255, 255, 255, 255, 255, 255, 1, 2, 2, 3, 0, 1, 255
};

static const u8 sActiveEnd[FIGHTER_STATE_COUNT] = {
    255, 255, 255, 255, 255, 255, 255, 1, 2, 3, 4, 0, 2, 255
};

static const u8 sHitstopFrames[FIGHTER_STATE_COUNT] = {
    0, 0, 0, 0, 0, 0, 0, 4, 5, 5, 8, 4, 6, 0
};

static const s16 sJumpArc[6] = { 0, -26, -44, -36, -18, 0 };

static Fighter sP1;
static Fighter sP2;
static Sprite* sSpark;
static u16 sSparkTimer;
static s16 sSparkX;
static s16 sSparkY;
static u16 sRoundSeconds;
static u16 sRoundFrameTicks;
static u16 sShakeTimer;
static s16 sShakeX;
static u16 sHitstopTimer;

static s16 iabs16(s16 value)
{
    return (value < 0) ? -value : value;
}

static void clampFighter(Fighter* f)
{
    if (f->x < MIN_X) f->x = MIN_X;
    if (f->x > MAX_X) f->x = MAX_X;
}

static bool stateLocksMovement(FighterState state)
{
    return (state == FIGHTER_JAB) ||
           (state == FIGHTER_MEDIUM) ||
           (state == FIGHTER_GRIP) ||
           (state == FIGHTER_HIP_THROW) ||
           (state == FIGHTER_HURT) ||
           (state == FIGHTER_KNOCKDOWN) ||
           (state == FIGHTER_GETUP);
}

static bool stateIsAttack(FighterState state)
{
    return (state == FIGHTER_JAB) ||
           (state == FIGHTER_MEDIUM) ||
           (state == FIGHTER_GRIP) ||
           (state == FIGHTER_HIP_THROW);
}

static bool stateIsActiveFrame(FighterState state, u16 frame)
{
    if (sActiveStart[state] == 255) return FALSE;
    return (frame >= sActiveStart[state]) && (frame <= sActiveEnd[state]);
}

static u8 stateHitstopFrames(FighterState state)
{
    return sHitstopFrames[state];
}

static u8 stateFrameDuration(FighterState state, u16 frame)
{
    if (frame >= MAX_STATE_FRAMES) return 1;
    if (sFrameDurations[state][frame] == 0) return 1;
    return sFrameDurations[state][frame];
}

static u16 stateTotalDuration(FighterState state)
{
    u16 total = 0;
    u16 i;
    for (i = 0; i < sFrameCounts[state]; i++) {
        total += stateFrameDuration(state, i);
    }
    return total;
}

static void fighterSetState(Fighter* f, FighterState state)
{
    if (f->state == state) return;

    f->previousState = f->state;
    f->state = state;
    f->frameTimer = 0;
    f->animFrame = 0;
    f->stateFrames = 0;
    f->attackDidHit = FALSE;

    if (state != FIGHTER_JUMP) {
        f->y = GROUND_Y;
    }

    if (f->sprite != NULL) {
        if (SPR_setDefinition(f->sprite, f->defs[state])) {
            SPR_setAutoAnimation(f->sprite, FALSE);
            SPR_setAnimAndFrame(f->sprite, 0, 0);
        }
    }
}

static bool fighterStateDone(const Fighter* f)
{
    return f->stateFrames >= stateTotalDuration(f->state);
}

static void fighterTickAnimation(Fighter* f)
{
    f->stateFrames++;
    f->frameTimer++;

    if (f->state == FIGHTER_JUMP) {
        u16 frame = f->animFrame;
        if (frame > 5) frame = 5;
        f->y = GROUND_Y + sJumpArc[frame];
    }

    if (f->frameTimer >= stateFrameDuration(f->state, f->animFrame)) {
        f->frameTimer = 0;
        if (sLooping[f->state]) {
            f->animFrame = (f->animFrame + 1) % sFrameCounts[f->state];
        } else if (f->animFrame < (sFrameCounts[f->state] - 1)) {
            f->animFrame++;
        }
        if (f->sprite != NULL) {
            SPR_setFrame(f->sprite, f->animFrame);
        }
    }
}

static void fighterRecoverIfDone(Fighter* f)
{
    if (!fighterStateDone(f)) return;

    if (f->state == FIGHTER_KNOCKDOWN) {
        fighterSetState(f, FIGHTER_GETUP);
    } else if (!sLooping[f->state] || stateLocksMovement(f->state)) {
        fighterSetState(f, FIGHTER_IDLE);
    }
}

static void faceOpponent(void)
{
    sP1.facingRight = (sP1.x <= sP2.x);
    sP2.facingRight = (sP2.x < sP1.x);
}

static void syncSprite(const Fighter* f)
{
    if (f->sprite == NULL) return;
    SPR_setPosition(f->sprite, f->x + sShakeX, f->y);
    SPR_setHFlip(f->sprite, !f->facingRight);
}

static bool fightersInRange(u16 range)
{
    s16 c1 = sP1.x + (FIGHTER_W / 2);
    s16 c2 = sP2.x + (FIGHTER_W / 2);
    return iabs16(c1 - c2) < (s16)range;
}

static void triggerSpark(s16 x, s16 y)
{
    sSparkX = x;
    sSparkY = y;
    sSparkTimer = 12;
    sShakeTimer = 8;
    sShakeX = 2;
    if (sSpark != NULL) {
        SPR_setVisibility(sSpark, VISIBLE);
        SPR_setAnimAndFrame(sSpark, 0, 0);
        SPR_setPosition(sSpark, sSparkX, sSparkY);
    }
}

static void applyHit(Fighter* attacker, Fighter* target, u16 damage, bool knockdown, u16 range)
{
    s16 dir;

    if (!fightersInRange(range)) return;
    if (target->state == FIGHTER_KNOCKDOWN || target->state == FIGHTER_GETUP) return;

    dir = attacker->facingRight ? 1 : -1;
    if ((target->state == FIGHTER_GUARD) && !knockdown) {
        damage = damage / 3;
        if (damage == 0) damage = 1;
    } else {
        fighterSetState(target, knockdown ? FIGHTER_KNOCKDOWN : FIGHTER_HURT);
    }

    target->life -= (s16)damage;
    if (target->life < 0) target->life = 0;
    target->vx = dir * (knockdown ? 4 : 2);
    sHitstopTimer = stateHitstopFrames(attacker->state);
    triggerSpark(target->x + 36, target->y + 48);

    if (target->life == 0) {
        fighterSetState(target, FIGHTER_KNOCKDOWN);
    }
}

static void evaluateAttack(Fighter* attacker, Fighter* target)
{
    if (!stateIsAttack(attacker->state)) return;
    if (attacker->attackDidHit) return;
    if (!stateIsActiveFrame(attacker->state, attacker->animFrame)) return;

    switch (attacker->state)
    {
        case FIGHTER_JAB:
            applyHit(attacker, target, 5, FALSE, HIT_RANGE_STRIKE);
            break;
        case FIGHTER_MEDIUM:
            applyHit(attacker, target, 9, FALSE, HIT_RANGE_STRIKE);
            break;
        case FIGHTER_GRIP:
            applyHit(attacker, target, 6, FALSE, HIT_RANGE_CLOSE);
            break;
        case FIGHTER_HIP_THROW:
            applyHit(attacker, target, 16, TRUE, HIT_RANGE_CLOSE);
            break;
        default:
            break;
    }
    attacker->attackDidHit = TRUE;
}

static void updatePhysics(Fighter* f)
{
    if (f->vx != 0) {
        f->x += f->vx;
        if (f->vx > 0) f->vx--;
        else f->vx++;
    }
    clampFighter(f);
}

static void updateP1Control(void)
{
    bool left = INPUT_held(BUTTON_LEFT);
    bool right = INPUT_held(BUTTON_RIGHT);
    bool down = INPUT_held(BUTTON_DOWN);

    if (INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    if (stateLocksMovement(sP1.state) || sP1.state == FIGHTER_JUMP || sP1.state == FIGHTER_DASH) {
        return;
    }

    if (INPUT_pressed(BUTTON_A) && down) {
        fighterSetState(&sP1, FIGHTER_MEDIUM);
    } else if (INPUT_pressed(BUTTON_B) && down) {
        fighterSetState(&sP1, FIGHTER_HIP_THROW);
    } else if (INPUT_pressed(BUTTON_A)) {
        fighterSetState(&sP1, FIGHTER_JAB);
    } else if (INPUT_pressed(BUTTON_X)) {
        fighterSetState(&sP1, FIGHTER_MEDIUM);
    } else if (INPUT_pressed(BUTTON_B)) {
        fighterSetState(&sP1, FIGHTER_GRIP);
    } else if (INPUT_pressed(BUTTON_Y)) {
        fighterSetState(&sP1, FIGHTER_HIP_THROW);
    } else if ((INPUT_pressed(BUTTON_UP) && (left || right))) {
        sP1.vx = right ? 5 : -5;
        fighterSetState(&sP1, FIGHTER_DASH);
    } else if (INPUT_pressed(BUTTON_Z) || INPUT_pressed(BUTTON_UP)) {
        fighterSetState(&sP1, FIGHTER_JUMP);
    } else if (down) {
        fighterSetState(&sP1, FIGHTER_CROUCH);
    } else if (INPUT_held(BUTTON_C)) {
        fighterSetState(&sP1, FIGHTER_GUARD);
    } else if (left || right) {
        sP1.x += right ? 2 : -2;
        fighterSetState(&sP1, right == sP1.facingRight ? FIGHTER_WALK_FORWARD : FIGHTER_WALK_BACK);
    } else if (sP1.state != FIGHTER_IDLE) {
        fighterSetState(&sP1, FIGHTER_IDLE);
    }
}

static void updateDummy(void)
{
    s16 dist = (sP1.x + 48) - (sP2.x + 48);

    if (stateLocksMovement(sP2.state) || sP2.state == FIGHTER_DASH || sP2.state == FIGHTER_JUMP) {
        return;
    }

    if (stateIsAttack(sP1.state) && fightersInRange(HIT_RANGE_STRIKE)) {
        fighterSetState(&sP2, FIGHTER_GUARD);
    } else if (fightersInRange(HIT_RANGE_STRIKE) && ((gApp.sceneFrames % 150) == 40)) {
        fighterSetState(&sP2, FIGHTER_JAB);
    } else if (iabs16(dist) > 86) {
        sP2.x += (dist > 0) ? 1 : -1;
        fighterSetState(&sP2, FIGHTER_WALK_FORWARD);
    } else if ((gApp.sceneFrames % 120) < 30) {
        fighterSetState(&sP2, FIGHTER_GUARD);
    } else if (sP2.state != FIGHTER_IDLE) {
        fighterSetState(&sP2, FIGHTER_IDLE);
    }
}

static void updateSpark(void)
{
    if (sShakeTimer > 0) {
        sShakeTimer--;
        sShakeX = (sShakeTimer & 1) ? 2 : -2;
    } else {
        sShakeX = 0;
    }

    if (sSparkTimer > 0) {
        u16 frame = (12 - sSparkTimer) / 4;
        if (frame > 2) frame = 2;
        if (sSpark != NULL) {
            SPR_setFrame(sSpark, frame);
            SPR_setPosition(sSpark, sSparkX + sShakeX, sSparkY);
        }
        sSparkTimer--;
    } else if (sSpark != NULL) {
        SPR_setVisibility(sSpark, HIDDEN);
    }
}

static void drawBar(u16 x, u16 y, s16 life)
{
    char bar[13];
    u16 i;
    u16 filled = (life > 0) ? ((u16)life / 8) : 0;

    if (filled > 12) filled = 12;
    for (i = 0; i < 12; i++) {
        bar[i] = (i < filled) ? '#' : '-';
    }
    bar[12] = 0;
    VDP_drawTextEx(WINDOW, bar, TILE_ATTR(PAL1, TRUE, FALSE, FALSE), x, y, CPU);
}

static void drawHud(void)
{
    char timer[4];
    sprintf(timer, "%02u", sRoundSeconds);

    VDP_drawTextEx(WINDOW, "CAIO", TILE_ATTR(PAL1, TRUE, FALSE, FALSE), 1, 0, CPU);
    VDP_drawTextEx(WINDOW, "DAVI", TILE_ATTR(PAL1, TRUE, FALSE, FALSE), 35, 0, CPU);
    drawBar(1, 1, sP1.life);
    drawBar(27, 1, sP2.life);
    VDP_drawTextEx(WINDOW, timer, TILE_ATTR(PAL1, TRUE, FALSE, FALSE), 19, 1, CPU);
    VDP_drawTextEx(WINDOW, "A JAB  B GRIP  C GUARD  D+B THROW", TILE_ATTR(PAL1, TRUE, FALSE, FALSE), 2, 3, CPU);
}

static void loadStage(void)
{
    u16 bgBBase = TILE_USER_INDEX;
    u16 bgABase = bgBBase + lapa_bg_b.tileset->numTile;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);

    VDP_drawImageEx(BG_B, &lapa_bg_b, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, bgBBase), 0, 0, TRUE, TRUE);
    VDP_drawImageEx(BG_A, &lapa_bg_a, TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, bgABase), 0, 20, TRUE, TRUE);
}

void SCENE_demoEnter(void)
{
    SPR_reset();
    SPR_update();

    VDP_setWindowOnTop(4);
    VDP_setTextPlane(WINDOW);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101018));
    loadStage();

    PAL_setPalette(PAL1, spr_caio_idle.palette->data, DMA);
    PAL_setPalette(PAL3, spr_davi_idle.palette->data, DMA);

    sP1.defs = sCaioDefs;
    sP1.x = 42;
    sP1.y = GROUND_Y;
    sP1.vx = 0;
    sP1.facingRight = TRUE;
    sP1.life = LIFE_MAX;
    sP1.state = FIGHTER_IDLE;
    sP1.previousState = FIGHTER_IDLE;
    sP1.frameTimer = 0;
    sP1.animFrame = 0;
    sP1.stateFrames = 0;
    sP1.attackDidHit = FALSE;

    sP2.defs = sDaviDefs;
    sP2.x = 188;
    sP2.y = GROUND_Y;
    sP2.vx = 0;
    sP2.facingRight = FALSE;
    sP2.life = LIFE_MAX;
    sP2.state = FIGHTER_IDLE;
    sP2.previousState = FIGHTER_IDLE;
    sP2.frameTimer = 0;
    sP2.animFrame = 0;
    sP2.stateFrames = 0;
    sP2.attackDidHit = FALSE;

    sP1.sprite = SPR_addSprite(&spr_caio_idle, sP1.x, sP1.y, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    sP2.sprite = SPR_addSprite(&spr_davi_idle, sP2.x, sP2.y, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
    sSpark = SPR_addSprite(&spr_hit_spark, -32, -32, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    if (sP1.sprite != NULL) SPR_setAutoAnimation(sP1.sprite, FALSE);
    if (sP2.sprite != NULL) SPR_setAutoAnimation(sP2.sprite, FALSE);
    if (sSpark != NULL) {
        SPR_setAutoAnimation(sSpark, FALSE);
        SPR_setVisibility(sSpark, HIDDEN);
    }

    sSparkTimer = 0;
    sRoundSeconds = ROUND_SECONDS;
    sRoundFrameTicks = 0;
    sShakeTimer = 0;
    sShakeX = 0;
    sHitstopTimer = 0;

    faceOpponent();
    drawHud();
}

void SCENE_demoUpdate(void)
{
    if (sHitstopTimer > 0) {
        sHitstopTimer--;
        faceOpponent();
        syncSprite(&sP1);
        syncSprite(&sP2);
        updateSpark();
        drawHud();
        return;
    }

    updateP1Control();
    updateDummy();

    updatePhysics(&sP1);
    updatePhysics(&sP2);

    fighterTickAnimation(&sP1);
    fighterTickAnimation(&sP2);

    evaluateAttack(&sP1, &sP2);
    evaluateAttack(&sP2, &sP1);

    fighterRecoverIfDone(&sP1);
    fighterRecoverIfDone(&sP2);

    faceOpponent();
    syncSprite(&sP1);
    syncSprite(&sP2);
    updateSpark();

    sRoundFrameTicks++;
    if (sRoundFrameTicks >= 60) {
        sRoundFrameTicks = 0;
        if (sRoundSeconds > 0) sRoundSeconds--;
    }

    if ((sP1.life == 0 || sP2.life == 0 || sRoundSeconds == 0) && INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    drawHud();
}

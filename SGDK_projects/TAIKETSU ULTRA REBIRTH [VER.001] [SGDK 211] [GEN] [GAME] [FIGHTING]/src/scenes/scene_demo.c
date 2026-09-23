#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"

#define FIGHT_ARENA_W 320
#define FIGHT_FLOOR_Y 176
#define FIGHT_BODY_W 28
#define FIGHT_BODY_H 40
#define FIGHT_LEFT_BOUND 16
#define FIGHT_RIGHT_BOUND (FIGHT_ARENA_W - FIGHT_BODY_W - 16)
#define FIGHT_METER_MAX 100
#define FIGHT_HITSTOP 8
#define FIGHT_ROUND_TIME 60
#define FIGHT_ROUND_LIMIT 3
#define FIGHT_GRAVITY 1
#define FIGHT_JUMP_SPEED (-9)

typedef enum FightPhase {
    FIGHT_PHASE_CS_C = 0,
    FIGHT_PHASE_CS_D = 1,
    FIGHT_PHASE_CS_E = 2,
    FIGHT_PHASE_ROUND = 3,
    FIGHT_PHASE_CS_A = 4
} FightPhase;

typedef enum FightMotion {
    FIGHT_MOTION_IDLE = 0,
    FIGHT_MOTION_WALK,
    FIGHT_MOTION_JUMP,
    FIGHT_MOTION_ATTACK,
    FIGHT_MOTION_HIT,
    FIGHT_MOTION_KO
} FightMotion;

typedef struct FightMove {
    u8 totalFrames;
    u8 activeStart;
    u8 activeEnd;
    u8 damage;
    u8 hitstun;
    u8 hitstop;
    bool heavy;
    bool special;
} FightMove;

typedef struct FightBox {
    s16 x;
    s16 y;
    s16 w;
    s16 h;
} FightBox;

typedef struct FightFighter {
    s16 x;
    s16 y;
    s16 facing;
    u16 health;
    u16 meter;
    s16 velocityY;
    u8 motion;
    u8 attackAge;
    u8 attackFrames;
    u8 attackKind;
    u8 hitstun;
    u8 guardFlash;
    bool guarding;
    bool special;
    bool attackConnected;
} FightFighter;

static const FightMove sMoves[5] = {
    { 0, 0, 0, 0, 0, 0, FALSE, FALSE },
    { 16, 6, 8, 4, 12, 4, FALSE, FALSE },
    { 20, 8, 11, 7, 15, 6, FALSE, FALSE },
    { 24, 10, 14, 10, 18, 8, TRUE, FALSE },
    { 28, 11, 17, 18, 24, 10, TRUE, TRUE }
};

static FightFighter sJack;
static FightFighter sC1;
static Sprite *sJackSprite;
static Sprite *sC1Sprite;
static FightPhase sPhase;
static u16 sPhaseFrames;
static u16 sHitstop;
static u16 sShakeFrames;
static u8 sSpecialRefillFrames;
static FightFighter *sSpecialRefillOwner;
static u8 sRoundWinsJack;
static u8 sRoundWinsC1;
static u16 sRoundTimer;
static u8 sRoundSecondFrames;
static bool sRoundOver;

static bool fightOverlap(const FightBox *a, const FightBox *b)
{
    return (a->x < (b->x + b->w)) && ((a->x + a->w) > b->x)
        && (a->y < (b->y + b->h)) && ((a->y + a->h) > b->y);
}

static FightBox fightHurtBox(const FightFighter *fighter)
{
    FightBox box;
    box.x = fighter->x + 4;
    box.y = fighter->y - 36;
    box.w = 20;
    box.h = 34;
    return box;
}

static FightBox fightHitBox(const FightFighter *fighter)
{
    FightBox box;
    const FightMove *move = &sMoves[fighter->attackKind];
    box.x = fighter->x + ((fighter->facing > 0) ? 18 : -18);
    box.y = fighter->y - ((fighter->attackKind == 4) ? 30 : 24);
    box.w = (fighter->attackKind == 4) ? 36 : 24;
    box.h = (fighter->attackKind == 4) ? 26 : 14;
    if (fighter->facing < 0) box.x -= box.w;
    (void) move;
    return box;
}

static void fightClampPosition(FightFighter *fighter)
{
    if (fighter->x < FIGHT_LEFT_BOUND) fighter->x = FIGHT_LEFT_BOUND;
    if (fighter->x > FIGHT_RIGHT_BOUND) fighter->x = FIGHT_RIGHT_BOUND;
}

static void fightResolvePush(void)
{
    s16 distance = sC1.x - sJack.x;

    if (distance >= 0 && distance < FIGHT_BODY_W) {
        s16 correction = (s16)((FIGHT_BODY_W - distance) >> 1);
        sJack.x -= correction;
        sC1.x += correction;
    } else if (distance < 0 && distance > -FIGHT_BODY_W) {
        s16 correction = (s16)((FIGHT_BODY_W + distance) >> 1);
        sJack.x += correction;
        sC1.x -= correction;
    }
    fightClampPosition(&sJack);
    fightClampPosition(&sC1);
}

static void fightMeterAdd(FightFighter *fighter, u16 amount)
{
    if (fighter->meter + amount >= FIGHT_METER_MAX) fighter->meter = FIGHT_METER_MAX;
    else fighter->meter += amount;
}

static void fightBeginAttack(FightFighter *fighter, u8 kind)
{
    fighter->attackKind = kind;
    fighter->attackAge = 0;
    fighter->attackFrames = sMoves[kind].totalFrames;
    fighter->attackConnected = FALSE;
    fighter->special = sMoves[kind].special;
    fighter->motion = FIGHT_MOTION_ATTACK;
    if (fighter->special) {
        fighter->meter = 0;
    }
}

static void fightEndAttack(FightFighter *fighter)
{
    if (fighter->attackFrames == 0) return;
    if (!fighter->attackConnected && sMoves[fighter->attackKind].heavy) {
        if (fighter->meter >= 6) fighter->meter -= 6;
        else fighter->meter = 0;
    }
    fighter->attackFrames = 0;
    fighter->attackAge = 0;
    fighter->attackKind = 0;
    fighter->special = FALSE;
    fighter->motion = FIGHT_MOTION_IDLE;
}

static void fightApplyHit(FightFighter *attacker, FightFighter *defender)
{
    FightBox hit = fightHitBox(attacker);
    FightBox hurt = fightHurtBox(defender);
    const FightMove *move = &sMoves[attacker->attackKind];
    u8 damage = move->damage;

    if (attacker->attackFrames == 0 || attacker->attackConnected
        || attacker->attackAge < move->activeStart
        || attacker->attackAge > move->activeEnd
        || !fightOverlap(&hit, &hurt)) return;
    attacker->attackConnected = TRUE;
    if (defender->guarding) {
        if (defender->health > 1) defender->health--;
        fightMeterAdd(defender, 2);
        defender->guardFlash = 8;
        fightMeterAdd(attacker, (u16)(damage / 10));
        AUDIO_playCue(AUDIO_CUE_STRIKE);
        return;
    }

    if (defender->health > damage) defender->health -= damage;
    else defender->health = 0;
    defender->hitstun = move->hitstun;
    defender->motion = FIGHT_MOTION_HIT;
    fightMeterAdd(attacker, (u16)(damage / 10));
    fightMeterAdd(defender, (u16)(damage / 10));
    sHitstop = move->hitstop;
    sShakeFrames = attacker->special ? 18 : 8;
    AUDIO_playCue(AUDIO_CUE_STRIKE);
    if (attacker->special) {
        sPhase = FIGHT_PHASE_CS_A;
        sPhaseFrames = 20;
        sSpecialRefillFrames = 2;
        sSpecialRefillOwner = attacker;
    }
}

static void fightFinishRound(void)
{
    if (sRoundOver) return;
    sRoundOver = TRUE;
    if (sJack.health == sC1.health) {
        if (sRoundTimer == 0) sRoundTimer = 1;
    } else if (sJack.health > sC1.health) {
        sRoundWinsJack++;
        sC1.motion = FIGHT_MOTION_KO;
    } else {
        sRoundWinsC1++;
        sJack.motion = FIGHT_MOTION_KO;
    }
    if (sRoundWinsJack >= 2 || sRoundWinsC1 >= 2) {
        sPhaseFrames = FIGHT_ROUND_LIMIT;
    }
}

static void fightUpdateRoundClock(void)
{
    if (sRoundTimer == 0) return;
    sRoundSecondFrames++;
    if (sRoundSecondFrames >= 60) {
        sRoundSecondFrames = 0;
        sRoundTimer--;
    }
    if (sRoundTimer == 0 || sJack.health == 0 || sC1.health == 0) {
        if (sRoundTimer == 0 && sJack.health != sC1.health) {
            if (sJack.health > sC1.health) sC1.health = 0;
            else if (sC1.health > sJack.health) sJack.health = 0;
        }
        fightFinishRound();
    }
}

static void fightUpdateJack(void)
{
    sJack.guarding = INPUT_held(BUTTON_Z) || INPUT_held(BUTTON_DOWN);
    if (sJack.hitstun != 0) {
        sJack.hitstun--;
        sJack.motion = FIGHT_MOTION_HIT;
        return;
    }
    if (sJack.attackFrames != 0) {
        sJack.attackAge++;
        sJack.attackFrames--;
        if (sJack.attackFrames == 0) fightEndAttack(&sJack);
        return;
    }
    if (sJack.y < FIGHT_FLOOR_Y || sJack.velocityY != 0) {
        sJack.velocityY += FIGHT_GRAVITY;
        sJack.y += sJack.velocityY;
        sJack.motion = FIGHT_MOTION_JUMP;
        if (sJack.y >= FIGHT_FLOOR_Y) {
            sJack.y = FIGHT_FLOOR_Y;
            sJack.velocityY = 0;
            sJack.motion = FIGHT_MOTION_IDLE;
            AUDIO_playCue(AUDIO_CUE_LAND);
        }
        return;
    }
    if (INPUT_pressed(BUTTON_A)) fightBeginAttack(&sJack, 1);
    else if (INPUT_pressed(BUTTON_X)) fightBeginAttack(&sJack, 2);
    else if (INPUT_pressed(BUTTON_B)) fightBeginAttack(&sJack, 3);
    else if (INPUT_pressed(BUTTON_C) && sJack.meter >= FIGHT_METER_MAX) fightBeginAttack(&sJack, 4);
    else if (!sJack.guarding) {
        if (INPUT_held(BUTTON_LEFT)) { sJack.x -= 2; sJack.facing = -1; }
        if (INPUT_held(BUTTON_RIGHT)) { sJack.x += 2; sJack.facing = 1; }
        if (INPUT_pressed(BUTTON_UP)) {
            sJack.velocityY = FIGHT_JUMP_SPEED;
            sJack.motion = FIGHT_MOTION_JUMP;
            AUDIO_playCue(AUDIO_CUE_JUMP);
        } else {
            sJack.motion = (INPUT_held(BUTTON_LEFT) || INPUT_held(BUTTON_RIGHT))
                ? FIGHT_MOTION_WALK : FIGHT_MOTION_IDLE;
        }
    }
    fightClampPosition(&sJack);
}

static void fightUpdateC1(void)
{
    s16 distance = sJack.x - sC1.x;
    sC1.guarding = ((gApp.totalFrames >> 5) & 7u) == 0;
    if (sC1.hitstun != 0) {
        sC1.hitstun--;
        sC1.motion = FIGHT_MOTION_HIT;
        return;
    }
    if (sC1.attackFrames != 0) {
        sC1.attackAge++;
        sC1.attackFrames--;
        if (sC1.attackFrames == 0) fightEndAttack(&sC1);
        return;
    }
    sC1.facing = (distance >= 0) ? 1 : -1;
    if ((gApp.totalFrames % 90u) == 0u && sC1.meter >= FIGHT_METER_MAX) {
        fightBeginAttack(&sC1, 4);
    } else if ((gApp.totalFrames % 42u) == 0u && distance > -64 && distance < 64) {
        fightBeginAttack(&sC1, (distance < 28) ? 2 : 1);
    } else if (distance > 42) {
        sC1.x += (s16)(sC1.facing * 1);
        sC1.motion = FIGHT_MOTION_WALK;
    } else {
        sC1.motion = FIGHT_MOTION_IDLE;
    }
    fightClampPosition(&sC1);
}

static void fightDrawHud(void)
{
    char line[41];
    char meterLine[41];
    u16 jackBars = (u16)(sJack.meter / 10);
    u16 c1Bars = (u16)(sC1.meter / 10);
    u16 i;

    sprintf(line, "JACK %3d HP  R%d   C1 %3d HP R%d", sJack.health,
            (u16)sRoundWinsJack, sC1.health, (u16)sRoundWinsC1);
    VDP_drawTextFill(line, 1, 1, 38);
    sprintf(meterLine, "METER [          ] [          ] T%02d", sRoundTimer);
    for (i = 0; i < jackBars && i < 10; i++) meterLine[7 + i] = '#';
    for (i = 0; i < c1Bars && i < 10; i++) meterLine[20 + i] = '#';
    VDP_drawTextFill(meterLine, 1, 2, 38);
    VDP_drawTextFill("A LIGHT X MED B HEAVY C SPECIAL Z GUARD", 1, 25, 38);
}

static void fightDrawPhase(void)
{
    VDP_clearTextArea(3, 8, 34, 8);
    if (sPhase == FIGHT_PHASE_ROUND) {
        return;
    }
    if (sPhase == FIGHT_PHASE_CS_C) {
        VDP_drawTextFill("CS-C  THE FORGE DISTRICT", 8, 9, 24);
        VDP_drawTextFill("STAGE INTRO  START: FIGHT", 7, 11, 26);
    } else if (sPhase == FIGHT_PHASE_CS_D) {
        VDP_drawTextFill("CS-D  JACK // C1", 11, 9, 18);
        VDP_drawTextFill("FIGHTERS ENTER THE RING", 9, 11, 22);
    } else if (sPhase == FIGHT_PHASE_CS_E) {
        VDP_drawTextFill("CS-E  ORDERED ENCOUNTER", 8, 8, 24);
        VDP_drawTextFill("JACK: THE HEAT IS RISING", 8, 10, 24);
        VDP_drawTextFill((sPhaseFrames & 16u) ? "C1: THEN STEP CLOSER" : "C1: THEN STEP CLOSER...", 7, 12, 26);
        VDP_drawTextFill("START: SKIP", 14, 14, 12);
    } else if (sPhase == FIGHT_PHASE_CS_A) {
        VDP_drawTextFill("CS-A  COMET BREAK", 11, 9, 18);
        VDP_drawTextFill((sSpecialRefillFrames == 0)
                         ? "SPECIAL CONNECT // METER 100"
                         : "SPECIAL CONNECT // IMPACT", 3, 11, 34);
    }
}

static void fightDrawSprites(void)
{
    s16 yJack = (s16)(sJack.y - FIGHT_BODY_H);
    s16 yC1 = (s16)(sC1.y - FIGHT_BODY_H);
    s16 shake = (sShakeFrames != 0) ? (s16)((sShakeFrames & 2u) ? 2 : -2) : 0;

    if (sJackSprite != NULL) {
        SPR_setPosition(sJackSprite, (s16)(sJack.x + shake), yJack);
        SPR_setHFlip(sJackSprite, sJack.facing < 0);
        SPR_setVisibility(sJackSprite, VISIBLE);
    }
    if (sC1Sprite != NULL) {
        SPR_setPosition(sC1Sprite, (s16)(sC1.x - shake), yC1);
        SPR_setHFlip(sC1Sprite, sC1.facing < 0);
        SPR_setVisibility(sC1Sprite, VISIBLE);
    }
}

static void fightDrawScene(void)
{
    u16 vramB = TILE_USER_INDEX;
    u16 vramA = TILE_USER_INDEX + img_fighting_room_0_bgb.tileset->numTile;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setPalette(PAL0, img_fighting_room_0_bgb.palette->data, DMA);
    PAL_setPalette(PAL1, img_fighting_room_0_bga.palette->data, DMA);
    PAL_setPalette(PAL2, spr_kairo_vant_probe.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x16233B));
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL3);
    VDP_setTextPriority(TRUE);
    VDP_drawImageEx(BG_B, &img_fighting_room_0_bgb,
                    TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, vramB), 0, 0, FALSE, TRUE);
    MDRuntimeProbe_noteTileRange(vramB, img_fighting_room_0_bgb.tileset->numTile);
    VDP_drawImageEx(BG_A, &img_fighting_room_0_bga,
                    TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, vramA), 0, 0, FALSE, TRUE);
    MDRuntimeProbe_noteTileRange(vramA, img_fighting_room_0_bga.tileset->numTile);
}

static void fightResetRound(void)
{
    sJack.x = 72; sJack.y = FIGHT_FLOOR_Y; sJack.facing = 1;
    sJack.health = 100; sJack.meter = 40; sJack.attackFrames = 0;
    sJack.velocityY = 0; sJack.motion = FIGHT_MOTION_IDLE; sJack.attackAge = 0;
    sJack.attackKind = 0; sJack.hitstun = 0; sJack.guardFlash = 0;
    sJack.guarding = FALSE; sJack.special = FALSE; sJack.attackConnected = FALSE;
    sC1.x = 224; sC1.y = FIGHT_FLOOR_Y; sC1.facing = -1;
    sC1.health = 100; sC1.meter = 70; sC1.attackFrames = 0;
    sC1.velocityY = 0; sC1.motion = FIGHT_MOTION_IDLE; sC1.attackAge = 0;
    sC1.attackKind = 0; sC1.hitstun = 0; sC1.guardFlash = 0;
    sC1.guarding = FALSE; sC1.special = FALSE; sC1.attackConnected = FALSE;
    sPhase = FIGHT_PHASE_ROUND;
    sPhaseFrames = 0;
    sHitstop = 0;
    sShakeFrames = 0;
    sSpecialRefillFrames = 0;
    sSpecialRefillOwner = NULL;
    sRoundTimer = FIGHT_ROUND_TIME;
    sRoundSecondFrames = 0;
    sRoundOver = FALSE;
}

static void fightReset(void)
{
    sRoundWinsJack = 0;
    sRoundWinsC1 = 0;
    sPhase = FIGHT_PHASE_CS_C;
    sPhaseFrames = 90;
    fightResetRound();
    sPhase = FIGHT_PHASE_CS_C;
    sPhaseFrames = 90;
}

void SCENE_demoEnter(void)
{
    SPR_reset();
    SPR_update();
    gApp.showDebugHud = FALSE;
    SCENE_cleanupLineScroll(BG_A);
    SCENE_cleanupLineScroll(BG_B);
    fightReset();
    fightDrawScene();
    AUDIO_startFightBgm();
    sJackSprite = SPR_addSprite(&spr_kairo_vant_probe, sJack.x, sJack.y - FIGHT_BODY_H,
                                TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    sC1Sprite = SPR_addSpriteSafe(&spr_c1_probe, sC1.x, sC1.y - FIGHT_BODY_H,
                                  TILE_ATTR(PAL2, TRUE, FALSE, TRUE));
    fightDrawSprites();
    fightDrawHud();
    fightDrawPhase();
}

void SCENE_demoUpdate(void)
{
    if (INPUT_pressed(BUTTON_MODE)) {
        APP_changeScene(APP_SCENE_MENU);
        return;
    }
    if (INPUT_pressed(BUTTON_START)) {
        if (sRoundOver) {
            if (sRoundWinsJack >= 2 || sRoundWinsC1 >= 2) {
                fightReset();
            } else {
                fightResetRound();
            }
            fightDrawScene();
            fightDrawSprites();
            fightDrawHud();
            fightDrawPhase();
            return;
        } else if (sPhase != FIGHT_PHASE_ROUND) {
            sPhase = FIGHT_PHASE_ROUND;
            sPhaseFrames = 0;
            VDP_clearTextArea(7, 8, 26, 7);
        } else {
            gApp.paused = !gApp.paused;
        }
    }
    if (gApp.paused) {
        VDP_drawTextFill("PAUSED  START: RESUME", 9, 13, 22);
        return;
    }
    if (sPhase != FIGHT_PHASE_ROUND) {
        if (sPhaseFrames != 0) sPhaseFrames--;
        if (sPhase == FIGHT_PHASE_CS_A && sSpecialRefillFrames != 0) {
            sSpecialRefillFrames--;
            if (sSpecialRefillFrames == 0 && sSpecialRefillOwner != NULL) {
                sSpecialRefillOwner->meter = FIGHT_METER_MAX;
            }
        }
        if (sPhaseFrames == 0) {
            if (sPhase == FIGHT_PHASE_CS_C) { sPhase = FIGHT_PHASE_CS_D; sPhaseFrames = 90; }
            else if (sPhase == FIGHT_PHASE_CS_D) { sPhase = FIGHT_PHASE_CS_E; sPhaseFrames = 120; }
            else if (sPhase == FIGHT_PHASE_CS_E) { sPhase = FIGHT_PHASE_ROUND; }
            else if (sPhase == FIGHT_PHASE_CS_A) { sPhase = FIGHT_PHASE_ROUND; }
        }
        fightDrawPhase();
        fightDrawHud();
        return;
    }
    if (sHitstop != 0) sHitstop--;
    else {
        fightUpdateJack();
        fightUpdateC1();
        fightApplyHit(&sJack, &sC1);
        fightApplyHit(&sC1, &sJack);
        fightResolvePush();
        fightUpdateRoundClock();
    }
    if (sShakeFrames != 0) sShakeFrames--;
    VDP_setHorizontalScroll(BG_A, (sShakeFrames != 0) ? 1 : 0);
    VDP_setHorizontalScroll(BG_B, 0);
    fightDrawSprites();
    fightDrawHud();
    if (sRoundOver) {
        if (sRoundWinsJack >= 2 || sRoundWinsC1 >= 2) {
            VDP_drawTextFill((sRoundWinsJack >= 2) ? "JACK WINS MATCH  START" : "C1 WINS MATCH  START", 7, 18, 26);
        } else {
            VDP_drawTextFill((sJack.health == 0) ? "C1 TAKES ROUND  START" : "JACK TAKES ROUND  START", 7, 18, 26);
        }
    }
}

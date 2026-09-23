#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"

#define STAGE_WORLD_W 512
#define STAGE_CAMERA_MAX_X (STAGE_WORLD_W - 320)
#define STAGE_GROUND_Y 176
#define STAGE_LEFT_WALL 8
#define STAGE_RIGHT_WALL (STAGE_WORLD_W - 16)
#define STAGE_HAZARD_X0 140
#define STAGE_HAZARD_X1 188
#define STAGE_GOAL_X 484

#define PLAYER_ACCEL (FIX16(1) >> 3)
#define PLAYER_FRICTION (FIX16(1) >> 4)
#define PLAYER_MAX_SPEED (FIX16(2) + (FIX16(1) >> 1))
#define PLAYER_GRAVITY (FIX16(1) >> 3)
#define PLAYER_JUMP_SPEED (-FIX16(5))
#define PLAYER_SHOOT_COOLDOWN 14
#define PLAYER_JUMP_BUFFER 6
#define PLAYER_COYOTE 5

#define LINE_SENTRY_X 286
#define LINE_SENTRY_Y 150
#define BREAKER_X 446
#define BREAKER_Y 132

typedef enum StageMode {
    STAGE_MODE_PLAY = 0,
    STAGE_MODE_END = 1
} StageMode;

typedef enum PlayerVisual {
    PLAYER_VIS_IDLE = 0,
    PLAYER_VIS_RUN,
    PLAYER_VIS_JUMP,
    PLAYER_VIS_SHOOT
} PlayerVisual;

typedef enum ActorState {
    ACTOR_IDLE = 0,
    ACTOR_TELEGRAPH,
    ACTOR_FIRE,
    ACTOR_HIT,
    ACTOR_DEAD
} ActorState;

typedef struct StagePlayer {
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    bool grounded;
    bool facingLeft;
    u8 hp;
    u8 energy;
    u8 shootCooldown;
    u8 jumpBuffer;
    u8 coyoteFrames;
    PlayerVisual visual;
    Sprite* sprite;
} StagePlayer;

typedef struct StageActor {
    fix16 x;
    fix16 y;
    s16 screenX;
    s16 screenY;
    u8 hp;
    u8 timer;
    ActorState state;
    bool active;
    Sprite* sprite;
} StageActor;

typedef struct StagePulse {
    fix16 x;
    fix16 y;
    fix16 vx;
    bool active;
    Sprite* sprite;
} StagePulse;

static StagePlayer sPlayer;
static StageActor sLineSentry;
static StageActor sBreakerCore;
static StagePulse sPulse;
static StageMode sMode;
static s16 sCameraX;
static u16 sStageTimer;
static u8 sShakeFrames;

static void stageResetScroll(void)
{
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
}

static void stageDrawWorld(void)
{
    u16 ind = TILE_USER_INDEX;
    u16 attrBg;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    stageResetScroll();

    attrBg = TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, ind);
    PAL_setPalette(PAL0, img_bc_stage_bg.palette->data, CPU);
    VDP_drawImageEx(BG_B, &img_bc_stage_bg, attrBg, 0, 0, FALSE, FALSE);
    VDP_drawImageEx(BG_B, &img_bc_stage_bg, attrBg, 24, 0, FALSE, FALSE);
    ind += img_bc_stage_bg.tileset->numTile;

    VDP_setTextPlane(BG_A);
    PAL_setPalette(PAL3, palette_grey, CPU);
    VDP_setTextPalette(PAL3);
}

static void stageSetPlayerVisual(PlayerVisual visual)
{
    const SpriteDefinition* nextDef = &spr_bc_player_idle;

    if (visual == sPlayer.visual) {
        return;
    }

    if (visual == PLAYER_VIS_RUN) {
        nextDef = &spr_bc_player_run;
    } else if (visual == PLAYER_VIS_JUMP) {
        nextDef = &spr_bc_player_jump;
    } else if (visual == PLAYER_VIS_SHOOT) {
        nextDef = &spr_bc_player_shoot;
    }

    SPR_setDefinition(sPlayer.sprite, nextDef);
    SPR_setAnimAndFrame(sPlayer.sprite, 0, 0);
    sPlayer.visual = visual;
}

static void stageCreateSprites(void)
{
    PAL_setPalette(PAL1, spr_bc_player_idle.palette->data, CPU);

    sPlayer.sprite = SPR_addSprite(&spr_bc_player_idle, 24, 128, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    sLineSentry.sprite = SPR_addSprite(&spr_bc_line_sentry_idle, 250, 132, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    sBreakerCore.sprite = SPR_addSprite(&spr_bc_breaker_core_idle, 420, 100, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    sPulse.sprite = SPR_addSprite(&spr_bc_projectile_pulse, -64, -64, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));

    SPR_setVisibility(sPulse.sprite, HIDDEN);
}

static void stageReset(void)
{
    sMode = STAGE_MODE_PLAY;
    sCameraX = 0;
    sStageTimer = 0;
    sShakeFrames = 0;

    sPlayer.x = FIX16(32);
    sPlayer.y = FIX16(STAGE_GROUND_Y);
    sPlayer.vx = 0;
    sPlayer.vy = 0;
    sPlayer.grounded = TRUE;
    sPlayer.facingLeft = FALSE;
    sPlayer.hp = 8;
    sPlayer.energy = 8;
    sPlayer.shootCooldown = 0;
    sPlayer.jumpBuffer = 0;
    sPlayer.coyoteFrames = PLAYER_COYOTE;
    sPlayer.visual = PLAYER_VIS_IDLE;

    sLineSentry.x = FIX16(LINE_SENTRY_X);
    sLineSentry.y = FIX16(LINE_SENTRY_Y);
    sLineSentry.hp = 2;
    sLineSentry.timer = 0;
    sLineSentry.state = ACTOR_IDLE;
    sLineSentry.active = TRUE;

    sBreakerCore.x = FIX16(BREAKER_X);
    sBreakerCore.y = FIX16(BREAKER_Y);
    sBreakerCore.hp = 6;
    sBreakerCore.timer = 0;
    sBreakerCore.state = ACTOR_IDLE;
    sBreakerCore.active = TRUE;

    sPulse.x = 0;
    sPulse.y = 0;
    sPulse.vx = 0;
    sPulse.active = FALSE;
}

static bool stageAabb(s16 ax, s16 ay, s16 aw, s16 ah, s16 bx, s16 by, s16 bw, s16 bh)
{
    return (ax < (bx + bw)) && ((ax + aw) > bx) && (ay < (by + bh)) && ((ay + ah) > by);
}

static void stageDamagePlayer(void)
{
    if (sPlayer.hp > 0) {
        sPlayer.hp--;
        AUDIO_playCue(AUDIO_CUE_STRIKE);
        sShakeFrames = 8;
    }

    if (sPlayer.hp == 0) {
        sPlayer.x = FIX16(32);
        sPlayer.y = FIX16(STAGE_GROUND_Y);
        sPlayer.vx = 0;
        sPlayer.vy = 0;
        sPlayer.hp = 8;
    }
}

static void stageApplyHorizontalInput(void)
{
    if (INPUT_held(BUTTON_LEFT)) {
        sPlayer.vx -= PLAYER_ACCEL;
        sPlayer.facingLeft = TRUE;
    } else if (INPUT_held(BUTTON_RIGHT)) {
        sPlayer.vx += PLAYER_ACCEL;
        sPlayer.facingLeft = FALSE;
    } else if (sPlayer.vx > 0) {
        sPlayer.vx -= PLAYER_FRICTION;
        if (sPlayer.vx < 0) {
            sPlayer.vx = 0;
        }
    } else if (sPlayer.vx < 0) {
        sPlayer.vx += PLAYER_FRICTION;
        if (sPlayer.vx > 0) {
            sPlayer.vx = 0;
        }
    }

    if (sPlayer.vx > PLAYER_MAX_SPEED) {
        sPlayer.vx = PLAYER_MAX_SPEED;
    } else if (sPlayer.vx < -PLAYER_MAX_SPEED) {
        sPlayer.vx = -PLAYER_MAX_SPEED;
    }
}

static void stageFirePulse(void)
{
    if (sPulse.active || sPlayer.shootCooldown > 0) {
        return;
    }

    sPulse.active = TRUE;
    sPulse.x = sPlayer.x + (sPlayer.facingLeft ? -FIX16(18) : FIX16(18));
    sPulse.y = sPlayer.y - FIX16(18);
    sPulse.vx = sPlayer.facingLeft ? -FIX16(5) : FIX16(5);
    sPlayer.shootCooldown = PLAYER_SHOOT_COOLDOWN;
    AUDIO_playCue(AUDIO_CUE_STRIKE);
    SPR_setVisibility(sPulse.sprite, VISIBLE);
}

static void stageUpdatePlayer(void)
{
    bool wasGrounded = sPlayer.grounded;

    stageApplyHorizontalInput();

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_Y)) {
        sPlayer.jumpBuffer = PLAYER_JUMP_BUFFER;
    } else if (sPlayer.jumpBuffer > 0) {
        sPlayer.jumpBuffer--;
    }

    if (sPlayer.grounded) {
        sPlayer.coyoteFrames = PLAYER_COYOTE;
    } else if (sPlayer.coyoteFrames > 0) {
        sPlayer.coyoteFrames--;
    }

    if (sPlayer.jumpBuffer > 0 && sPlayer.coyoteFrames > 0) {
        sPlayer.vy = PLAYER_JUMP_SPEED;
        sPlayer.grounded = FALSE;
        sPlayer.jumpBuffer = 0;
        sPlayer.coyoteFrames = 0;
        AUDIO_playCue(AUDIO_CUE_JUMP);
    }

    if (INPUT_pressed(BUTTON_B) || INPUT_pressed(BUTTON_X) || INPUT_pressed(BUTTON_Z)) {
        stageFirePulse();
    }

    if (sPlayer.shootCooldown > 0) {
        sPlayer.shootCooldown--;
    }

    sPlayer.vy += PLAYER_GRAVITY;
    sPlayer.x += sPlayer.vx;
    sPlayer.y += sPlayer.vy;

    if (sPlayer.x < FIX16(STAGE_LEFT_WALL)) {
        sPlayer.x = FIX16(STAGE_LEFT_WALL);
        sPlayer.vx = 0;
    } else if (sPlayer.x > FIX16(STAGE_RIGHT_WALL)) {
        sPlayer.x = FIX16(STAGE_RIGHT_WALL);
        sPlayer.vx = 0;
    }

    if (sPlayer.y >= FIX16(STAGE_GROUND_Y)) {
        sPlayer.y = FIX16(STAGE_GROUND_Y);
        sPlayer.vy = 0;
        sPlayer.grounded = TRUE;
        if (!wasGrounded) {
            AUDIO_playCue(AUDIO_CUE_LAND);
        }
    } else {
        sPlayer.grounded = FALSE;
    }

    if (sPlayer.grounded && F16_toInt(sPlayer.x) > STAGE_HAZARD_X0 && F16_toInt(sPlayer.x) < STAGE_HAZARD_X1) {
        stageDamagePlayer();
        sPlayer.vx = sPlayer.facingLeft ? FIX16(2) : -FIX16(2);
        sPlayer.vy = -FIX16(2);
        sPlayer.grounded = FALSE;
    }
}

static void stageUpdatePulse(void)
{
    s16 pulseX;
    s16 pulseY;

    if (!sPulse.active) {
        SPR_setPosition(sPulse.sprite, -64, -64);
        return;
    }

    sPulse.x += sPulse.vx;
    pulseX = F16_toInt(sPulse.x);
    pulseY = F16_toInt(sPulse.y);

    if (pulseX < 0 || pulseX > STAGE_WORLD_W) {
        sPulse.active = FALSE;
        SPR_setVisibility(sPulse.sprite, HIDDEN);
        return;
    }

    if (sLineSentry.active && stageAabb(pulseX, pulseY, 16, 8, F16_toInt(sLineSentry.x) - 14, F16_toInt(sLineSentry.y) - 10, 28, 20)) {
        sLineSentry.hp--;
        sLineSentry.state = ACTOR_HIT;
        sLineSentry.timer = 16;
        sPulse.active = FALSE;
        SPR_setVisibility(sPulse.sprite, HIDDEN);
        AUDIO_playCue(AUDIO_CUE_STRIKE);
        if (sLineSentry.hp == 0) {
            sLineSentry.active = FALSE;
        }
        return;
    }

    if (sBreakerCore.active && stageAabb(pulseX, pulseY, 16, 8, F16_toInt(sBreakerCore.x) - 24, F16_toInt(sBreakerCore.y) - 24, 48, 48)) {
        sBreakerCore.hp--;
        sBreakerCore.state = ACTOR_HIT;
        sBreakerCore.timer = 20;
        sShakeFrames = 5;
        sPulse.active = FALSE;
        SPR_setVisibility(sPulse.sprite, HIDDEN);
        AUDIO_playCue(AUDIO_CUE_STRIKE);
        if (sBreakerCore.hp == 0) {
            sBreakerCore.active = FALSE;
            sMode = STAGE_MODE_END;
            sStageTimer = 0;
        }
    }
}

static void stageUpdateLineSentry(void)
{
    s16 playerX = F16_toInt(sPlayer.x);

    if (!sLineSentry.active) {
        SPR_setVisibility(sLineSentry.sprite, HIDDEN);
        return;
    }

    SPR_setVisibility(sLineSentry.sprite, VISIBLE);

    if (sLineSentry.timer > 0) {
        sLineSentry.timer--;
        if (sLineSentry.timer == 0 && sLineSentry.state == ACTOR_TELEGRAPH) {
            if (playerX > LINE_SENTRY_X - 80 && playerX < LINE_SENTRY_X + 80) {
                stageDamagePlayer();
            }
            sLineSentry.state = ACTOR_FIRE;
            sLineSentry.timer = 24;
        } else if (sLineSentry.timer == 0 && sLineSentry.state == ACTOR_FIRE) {
            sLineSentry.state = ACTOR_IDLE;
        }
        return;
    }

    if (sLineSentry.state == ACTOR_HIT) {
        sLineSentry.state = ACTOR_IDLE;
    }

    if (playerX > LINE_SENTRY_X - 72 && playerX < LINE_SENTRY_X + 72) {
        sLineSentry.state = ACTOR_TELEGRAPH;
        sLineSentry.timer = 34;
    }
}

static void stageUpdateBreakerCore(void)
{
    s16 playerX = F16_toInt(sPlayer.x);
    s16 playerY = F16_toInt(sPlayer.y);

    if (!sBreakerCore.active) {
        SPR_setVisibility(sBreakerCore.sprite, HIDDEN);
        return;
    }

    SPR_setVisibility(sBreakerCore.sprite, VISIBLE);

    if (sBreakerCore.timer > 0) {
        sBreakerCore.timer--;
        if (sBreakerCore.timer == 0 && sBreakerCore.state == ACTOR_TELEGRAPH) {
            if (stageAabb(playerX - 8, playerY - 28, 16, 28, BREAKER_X - 28, BREAKER_Y - 26, 56, 52)) {
                stageDamagePlayer();
            }
            sBreakerCore.state = ACTOR_FIRE;
            sBreakerCore.timer = 50;
        } else if (sBreakerCore.timer == 0 && sBreakerCore.state == ACTOR_FIRE) {
            sBreakerCore.state = ACTOR_IDLE;
        }
        return;
    }

    if (playerX > 384) {
        sBreakerCore.state = ACTOR_TELEGRAPH;
        sBreakerCore.timer = 45;
    }
}

static void stageUpdateCamera(void)
{
    s16 targetX = F16_toInt(sPlayer.x) - 136;
    s16 shake = 0;

    if (!sPlayer.facingLeft) {
        targetX += 24;
    } else {
        targetX -= 24;
    }

    if (F16_toInt(sPlayer.x) > 420) {
        targetX = STAGE_CAMERA_MAX_X;
    }

    if (targetX < 0) {
        targetX = 0;
    } else if (targetX > STAGE_CAMERA_MAX_X) {
        targetX = STAGE_CAMERA_MAX_X;
    }

    if (sCameraX < targetX) {
        sCameraX += 4;
        if (sCameraX > targetX) sCameraX = targetX;
    } else if (sCameraX > targetX) {
        sCameraX -= 4;
        if (sCameraX < targetX) sCameraX = targetX;
    }

    if (sShakeFrames > 0) {
        shake = (sShakeFrames & 1) ? 3 : -3;
        sShakeFrames--;
    }

    VDP_setHorizontalScroll(BG_B, (s16)(-sCameraX + shake));
    VDP_setHorizontalScroll(BG_A, (s16)(-sCameraX + shake));
}

static void stageRenderSprite(Sprite* sprite, fix16 x, fix16 y, s16 centerX, s16 footOffsetY)
{
    s16 sx = F16_toInt(x) - sCameraX - centerX;
    s16 sy = F16_toInt(y) - footOffsetY;
    SPR_setPosition(sprite, sx, sy);
}

static void stageRender(void)
{
    PlayerVisual visual = PLAYER_VIS_IDLE;

    if (!sPlayer.grounded) {
        visual = PLAYER_VIS_JUMP;
    } else if (sPlayer.shootCooldown > (PLAYER_SHOOT_COOLDOWN - 8)) {
        visual = PLAYER_VIS_SHOOT;
    } else if (sPlayer.vx > (FIX16(1) >> 2) || sPlayer.vx < -(FIX16(1) >> 2)) {
        visual = PLAYER_VIS_RUN;
    }

    stageSetPlayerVisual(visual);
    SPR_setHFlip(sPlayer.sprite, sPlayer.facingLeft);
    stageRenderSprite(sPlayer.sprite, sPlayer.x, sPlayer.y, 12, 32);

    stageRenderSprite(sLineSentry.sprite, sLineSentry.x, sLineSentry.y, 16, 24);
    stageRenderSprite(sBreakerCore.sprite, sBreakerCore.x, sBreakerCore.y, 24, 48);

    if (sPulse.active) {
        SPR_setVisibility(sPulse.sprite, VISIBLE);
        stageRenderSprite(sPulse.sprite, sPulse.x, sPulse.y, 8, 4);
    }
}

static void stageDrawHud(void)
{
    char line[40];
    u8 bossHp = sBreakerCore.active ? sBreakerCore.hp : 0;

    sprintf(line, "HP:%02d EN:%02d BOSS:%02d", sPlayer.hp, sPlayer.energy, bossHp);
    VDP_drawTextFill(line, 1, 1, 28);
    VDP_drawTextFill("A/Y JUMP  B/X/Z PULSE  START PAUSE", 2, HUD_ROW_HINT_PRIMARY, 36);
}

static void stageDrawPause(void)
{
    VDP_drawTextFill("PAUSE", 17, 10, 6);
    VDP_drawTextFill("START RESUME", 14, 12, 14);
}

static void stageDrawEnd(void)
{
    VDP_drawTextFill("SECTOR 01 STABILIZED", 9, 9, 22);
    VDP_drawTextFill("POWER RESTORED", 13, 12, 16);
    VDP_drawTextFill("START: TITLE", 14, HUD_ROW_HINT_PRIMARY, 14);
}

void SCENE_demoEnter(void)
{
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x000000));
    stageDrawWorld();
    stageCreateSprites();
    stageReset();
}

void SCENE_demoUpdate(void)
{
    if (INPUT_pressed(BUTTON_START)) {
        if (sMode == STAGE_MODE_END) {
            APP_changeScene(APP_SCENE_MENU);
            return;
        }
        gApp.paused = !gApp.paused;
        AUDIO_playCue(AUDIO_CUE_PAUSE);
        if (!gApp.paused) {
            VDP_clearTextArea(14, 10, 14, 3);
        }
        return;
    }

    if (INPUT_pressed(BUTTON_MODE)) {
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (gApp.paused) {
        stageDrawPause();
        return;
    }

    if (sMode == STAGE_MODE_END) {
        stageDrawEnd();
        sStageTimer++;
        if (sStageTimer > 360) {
            APP_changeScene(APP_SCENE_MENU);
        }
        return;
    }

    stageUpdatePlayer();
    stageUpdatePulse();
    stageUpdateLineSentry();
    stageUpdateBreakerCore();
    stageUpdateCamera();
    stageRender();
    stageDrawHud();
    sStageTimer++;

    if (F16_toInt(sPlayer.x) > STAGE_GOAL_X && !sBreakerCore.active) {
        sMode = STAGE_MODE_END;
        sStageTimer = 0;
    }
}

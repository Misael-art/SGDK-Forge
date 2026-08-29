#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"

#define DEMO_WORLD_TILES 64
#define DEMO_WORLD_PX (DEMO_WORLD_TILES * 8)
#define DEMO_CAMERA_MAX_X (DEMO_WORLD_PX - 320)
#define DEMO_GROUND_Y 192
#define DEMO_PLAYER_PIVOT_X 24
#define DEMO_PLAYER_GROUND_Y 60
#define DEMO_PLAYER_MIN_X DEMO_PLAYER_PIVOT_X
#define DEMO_PLAYER_MAX_X (DEMO_WORLD_PX - DEMO_PLAYER_PIVOT_X)
#define DEMO_IDLE_FRAME_COUNT 6
#define DEMO_WALK_FRAME_COUNT 6
#define DEMO_DASH_FRAME_COUNT 4
#define DEMO_JUMP_FRAME_COUNT 8
#define DEMO_JAB_PHASE_COUNT 5
#define DEMO_SCROLL_LINES 224
#define DEMO_LAMP_PALETTE_INDEX 46
#define DEMO_CRIA_WORLD_X 256
#define DEMO_CRIA_PIVOT_X 24
#define DEMO_CRIA_GROUND_Y 60
#define DEMO_CRIA_IDLE_FRAME_COUNT 4
#define DEMO_CRIA_WALK_FRAME_COUNT 4
#define DEMO_CRIA_TELEGRAPH_FRAME_COUNT 4
#define DEMO_CRIA_HIT_FRAME_COUNT 4

#define DEMO_ACCEL (FIX16(1) >> 3)
#define DEMO_FRICTION (FIX16(1) >> 4)
#define DEMO_GRAVITY (FIX16(1) >> 3)
#define DEMO_MAX_SPEED (FIX16(2))
#define DEMO_RUN_SPEED (FIX16(3))
#define DEMO_JUMP_SPEED (-FIX16(5))

typedef struct DemoPlayer {
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    bool grounded;
} DemoPlayer;

typedef enum DemoAnimationState {
    DEMO_ANIM_IDLE = 0,
    DEMO_ANIM_WALK,
    DEMO_ANIM_DASH,
    DEMO_ANIM_JUMP,
    DEMO_ANIM_JAB
} DemoAnimationState;

static DemoPlayer sPlayer;
static Sprite* sPlayerSprite;
static Sprite* sGroundShadowSprite;
static Sprite* sSmokeSprite0;
static Sprite* sSmokeSprite1;
static Sprite* sLampDustSprite0;
static Sprite* sLampDustSprite1;
static Sprite* sCriaSprite;
static s16 sCameraX;
static DemoAnimationState sAnimState;
static u8 sIdleFrame;
static u8 sIdleFrameTicks;
static const u8 sIdleFrameDuration[DEMO_IDLE_FRAME_COUNT] = { 11, 7, 10, 7, 11, 12 };
static u8 sMotionFrame;
static u8 sMotionFrameTicks;
static u8 sJumpStartTicks;
static u8 sLandingTicks;
static const u8 sWalkFrameDuration[DEMO_WALK_FRAME_COUNT] = { 5, 4, 5, 5, 4, 5 };
static const u8 sDashFrameDuration[DEMO_DASH_FRAME_COUNT] = { 3, 2, 3, 4 };
static bool sJabActive;
static u8 sJabFrame;
static u8 sJabFrameTicks;
static const u8 sJabPhaseDuration[DEMO_JAB_PHASE_COUNT] = { 3, 2, 2, 3, 4 };
static u8 sCriaIdleFrame;
static u8 sCriaIdleFrameTicks;
static const u8 sCriaIdleDuration[DEMO_CRIA_IDLE_FRAME_COUNT] = { 8, 7, 8, 7 };
static u8 sCriaWalkFrame;
static u8 sCriaWalkTicks;
static const u8 sCriaWalkDuration[DEMO_CRIA_WALK_FRAME_COUNT] = { 5, 4, 5, 4 };
static bool sCriaWalking;
static u8 sCriaMode;
static u8 sCriaTelFrame;
static u8 sCriaTelTicks;
static const u8 sCriaTelDuration[DEMO_CRIA_TELEGRAPH_FRAME_COUNT] = { 3, 3, 4, 2 };
static u8 sCriaHitFrame;
static u8 sCriaHitTicks;
static const u8 sCriaHitDuration[DEMO_CRIA_HIT_FRAME_COUNT] = { 3, 4, 6, 5 };
static u16 sCriaClock;
static s16 sBgAScrollLines[DEMO_SCROLL_LINES];
static s16 sBgBScrollLines[DEMO_SCROLL_LINES];
static const s8 sWaterWave[16] = {
    0, 0, 1, 1, 2, 2, 1, 1,
    0, 0, -1, -1, -2, -2, -1, -1
};
static const u16 sLampPulsePalette[4][2] = {
    { RGB3_3_3_TO_VDPCOLOR(6, 3, 1), RGB3_3_3_TO_VDPCOLOR(7, 6, 4) },
    { RGB3_3_3_TO_VDPCOLOR(7, 4, 1), RGB3_3_3_TO_VDPCOLOR(7, 7, 5) },
    { RGB3_3_3_TO_VDPCOLOR(7, 5, 2), RGB3_3_3_TO_VDPCOLOR(7, 7, 6) },
    { RGB3_3_3_TO_VDPCOLOR(7, 4, 1), RGB3_3_3_TO_VDPCOLOR(7, 6, 5) }
};
static const u16 sTainaBacklightPalette[16] = {
    RGB3_3_3_TO_VDPCOLOR(7, 0, 7),
    RGB3_3_3_TO_VDPCOLOR(0, 0, 1),
    RGB3_3_3_TO_VDPCOLOR(1, 0, 2),
    RGB3_3_3_TO_VDPCOLOR(2, 1, 3),
    RGB3_3_3_TO_VDPCOLOR(0, 1, 2),
    RGB3_3_3_TO_VDPCOLOR(1, 4, 4),
    RGB3_3_3_TO_VDPCOLOR(2, 1, 1),
    RGB3_3_3_TO_VDPCOLOR(4, 2, 1),
    RGB3_3_3_TO_VDPCOLOR(6, 2, 1),
    RGB3_3_3_TO_VDPCOLOR(7, 4, 2),
    RGB3_3_3_TO_VDPCOLOR(7, 5, 3),
    0, 0, 0, 0, 0
};

static void demoDrawStaticWorld(void)
{
    u16 tileIndex = TILE_USER_INDEX;
    u16 row;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    for (row = 0; row < DEMO_SCROLL_LINES; row++) {
        sBgAScrollLines[row] = -sCameraX;
        sBgBScrollLines[row] = -(sCameraX >> 3);
    }
    VDP_setHorizontalScrollLine(
        BG_A,
        0,
        sBgAScrollLines,
        DEMO_SCROLL_LINES,
        DMA_QUEUE
    );
    VDP_setHorizontalScrollLine(
        BG_B,
        0,
        sBgBScrollLines,
        DEMO_SCROLL_LINES,
        DMA_QUEUE
    );

    VDP_drawImageEx(
        BG_B,
        &img_cais01_bg_b_mar_ceu,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, tileIndex),
        0,
        0,
        FALSE,
        TRUE
    );
    tileIndex += img_cais01_bg_b_mar_ceu.tileset->numTile;
    VDP_drawImageEx(
        BG_A,
        &img_cais01_bg_a_pier_modular,
        TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, tileIndex),
        0,
        0,
        FALSE,
        TRUE
    );
}

static void demoResetPlayer(void)
{
    sPlayer.x = FIX16(224);
    sPlayer.y = FIX16(DEMO_GROUND_Y);
    sPlayer.vx = 0;
    sPlayer.vy = 0;
    sPlayer.grounded = TRUE;
    sCameraX = 80;
}

static void demoApplyHorizontalInput(void)
{
    fix16 maxSpeed = (INPUT_held(BUTTON_B) || INPUT_held(BUTTON_Z)) ? DEMO_RUN_SPEED : DEMO_MAX_SPEED;

    if (INPUT_held(BUTTON_LEFT)) {
        sPlayer.vx -= DEMO_ACCEL;
    } else if (INPUT_held(BUTTON_RIGHT)) {
        sPlayer.vx += DEMO_ACCEL;
    } else if (sPlayer.vx > 0) {
        sPlayer.vx -= DEMO_FRICTION;
        if (sPlayer.vx < 0) {
            sPlayer.vx = 0;
        }
    } else if (sPlayer.vx < 0) {
        sPlayer.vx += DEMO_FRICTION;
        if (sPlayer.vx > 0) {
            sPlayer.vx = 0;
        }
    }

    if (sPlayer.vx > maxSpeed) {
        sPlayer.vx = maxSpeed;
    } else if (sPlayer.vx < -maxSpeed) {
        sPlayer.vx = -maxSpeed;
    }
}

static void demoStartJab(void)
{
    if ((sPlayerSprite == NULL) || sJabActive || !sPlayer.grounded) {
        return;
    }

    sAnimState = DEMO_ANIM_JAB;
    sJabActive = TRUE;
    sJabFrame = 0;
    sJabFrameTicks = 0;
    SPR_setAutoAnimation(sPlayerSprite, FALSE);
    SPR_setAnimAndFrame(sPlayerSprite, 0, 0);
}

static bool demoSetAnimationDefinition(DemoAnimationState state)
{
    const SpriteDefinition* definition = &spr_taina_idle_guard;

    if (sPlayerSprite == NULL) {
        return FALSE;
    }

    switch (state) {
        case DEMO_ANIM_WALK:
            definition = &spr_taina_walk_combat_step;
            break;
        case DEMO_ANIM_DASH:
            definition = &spr_taina_dash_or_step_in;
            break;
        case DEMO_ANIM_JUMP:
            definition = &spr_taina_jump_rise_fall_landing;
            break;
        case DEMO_ANIM_IDLE:
        default:
            definition = &spr_taina_idle_guard;
            break;
    }

    if (!SPR_setDefinition(sPlayerSprite, definition)) {
        VDP_drawTextFill("MOTION SPRITE ALLOC FAILED", 7, 11, 24);
        return FALSE;
    }

    sAnimState = state;
    sMotionFrame = 0;
    sMotionFrameTicks = 0;
    SPR_setAutoAnimation(sPlayerSprite, FALSE);
    SPR_setAnimAndFrame(sPlayerSprite, 0, 0);
    return TRUE;
}

static void demoUpdatePlayer(void)
{
    bool wasGrounded = sPlayer.grounded;

    demoApplyHorizontalInput();

    if ((INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_Y)) && sPlayer.grounded) {
        sPlayer.vy = DEMO_JUMP_SPEED;
        sPlayer.grounded = FALSE;
        sJumpStartTicks = 4;
        sLandingTicks = 0;
        AUDIO_playCue(AUDIO_CUE_JUMP);
    }

    if (INPUT_pressed(BUTTON_C) || INPUT_pressed(BUTTON_X)) {
        AUDIO_playCue(AUDIO_CUE_STRIKE);
        demoStartJab();
    }

    sPlayer.vy += DEMO_GRAVITY;
    sPlayer.x += sPlayer.vx;
    sPlayer.y += sPlayer.vy;

    if (sPlayer.x < FIX16(DEMO_PLAYER_MIN_X)) {
        sPlayer.x = FIX16(DEMO_PLAYER_MIN_X);
        sPlayer.vx = 0;
    } else if (sPlayer.x > FIX16(DEMO_PLAYER_MAX_X)) {
        sPlayer.x = FIX16(DEMO_PLAYER_MAX_X);
        sPlayer.vx = 0;
    }

    if (sPlayer.y >= FIX16(DEMO_GROUND_Y)) {
        sPlayer.y = FIX16(DEMO_GROUND_Y);
        sPlayer.vy = 0;
        sPlayer.grounded = TRUE;
        if (!wasGrounded) {
            sLandingTicks = 8;
            AUDIO_playCue(AUDIO_CUE_LAND);
        }
    }
}

static void demoUpdateCamera(void)
{
    s16 targetX = F16_toInt(sPlayer.x) - 144;

    if (targetX < 0) {
        targetX = 0;
    } else if (targetX > DEMO_CAMERA_MAX_X) {
        targetX = DEMO_CAMERA_MAX_X;
    }

    sCameraX += (targetX - sCameraX) >> 3;
}

static void demoUpdateEnvironmentFx(void)
{
    u16 row;
    u16 phase = (gApp.sceneFrames >> 2) & 15;
    u8 fxFrame = (gApp.sceneFrames >> 3) & 3;

    for (row = 0; row < DEMO_SCROLL_LINES; row++) {
        s16 bgBScroll;

        sBgAScrollLines[row] = -sCameraX;
        if (row < 48) {
            bgBScroll = -(sCameraX >> 3);
        } else if (row < 80) {
            bgBScroll = -(sCameraX >> 2);
        } else if (row < 112) {
            bgBScroll = -(sCameraX >> 1);
        } else {
            s16 wave = sWaterWave[(phase + (row >> 1)) & 15];

            if (row >= 160) {
                wave <<= 1;
            }
            bgBScroll = -(sCameraX >> 2) + wave;
        }
        sBgBScrollLines[row] = bgBScroll;
    }

    VDP_setHorizontalScrollLine(
        BG_A,
        0,
        sBgAScrollLines,
        DEMO_SCROLL_LINES,
        DMA_QUEUE
    );
    VDP_setHorizontalScrollLine(
        BG_B,
        0,
        sBgBScrollLines,
        DEMO_SCROLL_LINES,
        DMA_QUEUE
    );

    if ((gApp.sceneFrames & 7) == 0) {
        PAL_setColors(
            DEMO_LAMP_PALETTE_INDEX,
            sLampPulsePalette[(gApp.sceneFrames >> 3) & 3],
            2,
            DMA_QUEUE
        );
    }

    if (sSmokeSprite0 != NULL) {
        SPR_setPosition(sSmokeSprite0, 210 - (sCameraX >> 1), 52);
        SPR_setFrame(sSmokeSprite0, fxFrame);
    }
    if (sSmokeSprite1 != NULL) {
        SPR_setPosition(sSmokeSprite1, 430 - (sCameraX >> 1), 58);
        SPR_setFrame(sSmokeSprite1, (fxFrame + 2) & 3);
    }
    if (sLampDustSprite0 != NULL) {
        SPR_setPosition(
            sLampDustSprite0,
            373 - sCameraX,
            60 + sWaterWave[(phase + 3) & 15]
        );
        SPR_setFrame(sLampDustSprite0, fxFrame);
    }
    if (sLampDustSprite1 != NULL) {
        SPR_setPosition(
            sLampDustSprite1,
            389 - sCameraX,
            72 + sWaterWave[(phase + 11) & 15]
        );
        SPR_setFrame(sLampDustSprite1, (fxFrame + 1) & 3);
    }
}

static void demoDrawPlayer(void)
{
    s16 screenPivotX;
    s16 screenGroundY;
    s16 airHeight;
    u8 shadowFrame;

    if (sPlayerSprite == NULL) {
        return;
    }

    screenPivotX = F16_toInt(sPlayer.x) - sCameraX;
    screenGroundY = F16_toInt(sPlayer.y);
    if (sGroundShadowSprite != NULL) {
        airHeight = DEMO_GROUND_Y - screenGroundY;
        shadowFrame = (airHeight > 28) ? 2 : ((airHeight > 8) ? 1 : 0);
        SPR_setPosition(
            sGroundShadowSprite,
            screenPivotX - DEMO_PLAYER_PIVOT_X,
            DEMO_GROUND_Y - 12
        );
        SPR_setFrame(sGroundShadowSprite, shadowFrame);
    }
    SPR_setPosition(
        sPlayerSprite,
        screenPivotX - DEMO_PLAYER_PIVOT_X,
        screenGroundY - DEMO_PLAYER_GROUND_Y
    );

    if (sPlayer.vx < 0) {
        SPR_setHFlip(sPlayerSprite, TRUE);
    } else if (sPlayer.vx > 0) {
        SPR_setHFlip(sPlayerSprite, FALSE);
    }
}

static void demoUpdatePlayerAnimation(void)
{
    DemoAnimationState requestedState;
    bool running;
    bool moving;

    if (sPlayerSprite == NULL) {
        return;
    }

    if (sJabActive) {
        sJabFrameTicks++;
        if (sJabFrameTicks < sJabPhaseDuration[sJabFrame]) {
            return;
        }

        sJabFrameTicks = 0;
        sJabFrame++;

        if (sJabFrame == 1) {
            if (!SPR_setDefinition(sPlayerSprite, &spr_taina_combo_hit_1_jab)) {
                sJabActive = FALSE;
                VDP_drawTextFill("JAB SPRITE ALLOC FAILED", 8, 11, 22);
                return;
            }
            SPR_setAutoAnimation(sPlayerSprite, FALSE);
            SPR_setAnimAndFrame(sPlayerSprite, 0, 0);
            return;
        }

        if (sJabFrame == 2) {
            SPR_setFrame(sPlayerSprite, 1);
            return;
        }

        if (sJabFrame == 3) {
            SPR_setFrame(sPlayerSprite, 2);
            return;
        }

        if (sJabFrame == 4) {
            if (!SPR_setDefinition(sPlayerSprite, &spr_taina_idle_guard)) {
                sJabActive = FALSE;
                VDP_drawTextFill("IDLE SPRITE ALLOC FAILED", 7, 11, 23);
                return;
            }
            SPR_setAutoAnimation(sPlayerSprite, FALSE);
            SPR_setAnimAndFrame(sPlayerSprite, 0, 0);
            return;
        }

        sJabActive = FALSE;
        sAnimState = DEMO_ANIM_IDLE;
        sIdleFrame = 0;
        sIdleFrameTicks = 0;
        return;
    }

    moving = (sPlayer.vx > DEMO_FRICTION) || (sPlayer.vx < -DEMO_FRICTION);
    running = INPUT_held(BUTTON_B) || INPUT_held(BUTTON_Z);

    if (!sPlayer.grounded || (sJumpStartTicks > 0) || (sLandingTicks > 0)) {
        requestedState = DEMO_ANIM_JUMP;
    } else if (moving && running) {
        requestedState = DEMO_ANIM_DASH;
    } else if (moving) {
        requestedState = DEMO_ANIM_WALK;
    } else {
        requestedState = DEMO_ANIM_IDLE;
    }

    if (requestedState != sAnimState) {
        if (!demoSetAnimationDefinition(requestedState)) {
            sAnimState = DEMO_ANIM_IDLE;
            return;
        }
        sIdleFrame = 0;
        sIdleFrameTicks = 0;
    }

    if (sAnimState == DEMO_ANIM_JUMP) {
        u8 requestedFrame;

        if (sJumpStartTicks > 0) {
            sJumpStartTicks--;
            requestedFrame = 0;
        } else if (!sPlayer.grounded) {
            if (sPlayer.vy < -FIX16(2)) {
                requestedFrame = 1;
            } else if (sPlayer.vy < 0) {
                requestedFrame = 2;
            } else if (sPlayer.vy < FIX16(1)) {
                requestedFrame = 3;
            } else if (sPlayer.vy < FIX16(3)) {
                requestedFrame = 4;
            } else {
                requestedFrame = 5;
            }
        } else if (sLandingTicks > 4) {
            sLandingTicks--;
            requestedFrame = 6;
        } else if (sLandingTicks > 0) {
            sLandingTicks--;
            requestedFrame = 7;
        } else {
            demoSetAnimationDefinition(DEMO_ANIM_IDLE);
            return;
        }

        if (requestedFrame != sMotionFrame) {
            sMotionFrame = requestedFrame;
            SPR_setFrame(sPlayerSprite, sMotionFrame);
        }
        return;
    }

    if (sAnimState == DEMO_ANIM_WALK) {
        sMotionFrameTicks++;
        if (sMotionFrameTicks >= sWalkFrameDuration[sMotionFrame]) {
            sMotionFrameTicks = 0;
            sMotionFrame++;
            if (sMotionFrame >= DEMO_WALK_FRAME_COUNT) {
                sMotionFrame = 0;
            }
            SPR_setFrame(sPlayerSprite, sMotionFrame);
        }
        return;
    }

    if (sAnimState == DEMO_ANIM_DASH) {
        sMotionFrameTicks++;
        if (sMotionFrameTicks >= sDashFrameDuration[sMotionFrame]) {
            sMotionFrameTicks = 0;
            sMotionFrame++;
            if (sMotionFrame >= DEMO_DASH_FRAME_COUNT) {
                sMotionFrame = 0;
            }
            SPR_setFrame(sPlayerSprite, sMotionFrame);
        }
        return;
    }

    sIdleFrameTicks++;
    if (sIdleFrameTicks < sIdleFrameDuration[sIdleFrame]) {
        return;
    }

    sIdleFrameTicks = 0;
    sIdleFrame++;
    if (sIdleFrame >= DEMO_IDLE_FRAME_COUNT) {
        sIdleFrame = 0;
    }
    SPR_setFrame(sPlayerSprite, sIdleFrame);
}

static void demoDrawHud(void)
{
    /* The first CAIS_01 visual slice keeps the combat field unobstructed.
     * Formal HUD ownership remains a later WINDOW-plane task. */
}

static const SpriteDefinition* demoCriaDefinition(u8 mode)
{
    if (mode == 1) {
        return &spr_cria_walk_lean;
    }
    if (mode == 2) {
        return &spr_cria_telegraph_lean;
    }
    if (mode == 3) {
        return &spr_cria_hit_lean;
    }
    return &spr_cria_idle_lean;
}

static void demoUpdateCria(void)
{
    u8 wantMode;

    if (sCriaSprite == NULL) {
        return;
    }

    sCriaClock++;
    wantMode = (u8)((sCriaClock / 120) % 4);
    if (wantMode != sCriaMode) {
        if (!SPR_setDefinition(sCriaSprite, demoCriaDefinition(wantMode))) {
            VDP_drawTextFill("CRIA SPRITE ALLOC FAILED", 7, 11, 23);
            return;
        }
        SPR_setAutoAnimation(sCriaSprite, FALSE);
        SPR_setAnimAndFrame(sCriaSprite, 0, 0);
        sCriaMode = wantMode;
        sCriaWalking = (wantMode == 1);
        sCriaIdleFrame = 0;
        sCriaIdleFrameTicks = 0;
        sCriaWalkFrame = 0;
        sCriaWalkTicks = 0;
        sCriaTelFrame = 0;
        sCriaTelTicks = 0;
        sCriaHitFrame = 0;
        sCriaHitTicks = 0;
    }

    SPR_setPosition(
        sCriaSprite,
        DEMO_CRIA_WORLD_X - sCameraX - DEMO_CRIA_PIVOT_X,
        DEMO_GROUND_Y - DEMO_CRIA_GROUND_Y
    );

    if (sCriaMode == 1) {
        sCriaWalkTicks++;
        if (sCriaWalkTicks < sCriaWalkDuration[sCriaWalkFrame]) {
            return;
        }
        sCriaWalkTicks = 0;
        sCriaWalkFrame++;
        if (sCriaWalkFrame >= DEMO_CRIA_WALK_FRAME_COUNT) {
            sCriaWalkFrame = 0;
        }
        SPR_setFrame(sCriaSprite, sCriaWalkFrame);
        return;
    }

    if (sCriaMode == 2) {
        if (sCriaTelFrame >= (DEMO_CRIA_TELEGRAPH_FRAME_COUNT - 1)) {
            return;
        }
        sCriaTelTicks++;
        if (sCriaTelTicks < sCriaTelDuration[sCriaTelFrame]) {
            return;
        }
        sCriaTelTicks = 0;
        sCriaTelFrame++;
        SPR_setFrame(sCriaSprite, sCriaTelFrame);
        return;
    }

    if (sCriaMode == 3) {
        /* Hold hitstop (frame 2). Recover exists on the strip for the later
         * ATTACK->RECOVER chain; the 2s showcase must stay readable as a punch. */
        if (sCriaHitFrame >= 2) {
            return;
        }
        sCriaHitTicks++;
        if (sCriaHitTicks < sCriaHitDuration[sCriaHitFrame]) {
            return;
        }
        sCriaHitTicks = 0;
        sCriaHitFrame++;
        SPR_setFrame(sCriaSprite, sCriaHitFrame);
        return;
    }

    sCriaIdleFrameTicks++;
    if (sCriaIdleFrameTicks < sCriaIdleDuration[sCriaIdleFrame]) {
        return;
    }
    sCriaIdleFrameTicks = 0;
    sCriaIdleFrame++;
    if (sCriaIdleFrame >= DEMO_CRIA_IDLE_FRAME_COUNT) {
        sCriaIdleFrame = 0;
    }
    SPR_setFrame(sCriaSprite, sCriaIdleFrame);
}

static void demoDrawPause(void)
{
    VDP_drawTextFill("==== PAUSE ====", 12, 11, 16);
    VDP_drawTextFill("PAUSE BUTTON: resume", 10, 13, 20);
}

void SCENE_demoEnter(void)
{
    PAL_setPalette(PAL0, img_cais01_bg_b_mar_ceu.palette->data, DMA);
    PAL_setPalette(PAL2, img_cais01_bg_a_pier_modular.palette->data, DMA);
    PAL_setPalette(PAL1, sTainaBacklightPalette, DMA);
    PAL_setPalette(PAL3, spr_cria_idle_lean.palette->data, DMA);
    VDP_setTextPalette(PAL0);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101828));
    demoResetPlayer();
    sIdleFrame = 0;
    sIdleFrameTicks = 0;
    sAnimState = DEMO_ANIM_IDLE;
    sMotionFrame = 0;
    sMotionFrameTicks = 0;
    sJumpStartTicks = 0;
    sLandingTicks = 0;
    sJabActive = FALSE;
    sJabFrame = 0;
    sJabFrameTicks = 0;
    demoDrawStaticWorld();

    sSmokeSprite0 = SPR_addSprite(
        &spr_cais01_smoke,
        210 - (sCameraX >> 1),
        52,
        TILE_ATTR(PAL0, FALSE, FALSE, FALSE)
    );
    if (sSmokeSprite0 != NULL) {
        SPR_setAnim(sSmokeSprite0, 0);
        SPR_setAutoAnimation(sSmokeSprite0, FALSE);
        SPR_setFrame(sSmokeSprite0, 0);
    }

    sSmokeSprite1 = SPR_addSprite(
        &spr_cais01_smoke,
        430 - (sCameraX >> 1),
        58,
        TILE_ATTR(PAL0, FALSE, FALSE, FALSE)
    );
    if (sSmokeSprite1 != NULL) {
        SPR_setAnim(sSmokeSprite1, 0);
        SPR_setAutoAnimation(sSmokeSprite1, FALSE);
        SPR_setFrame(sSmokeSprite1, 2);
    }

    sLampDustSprite0 = SPR_addSprite(
        &spr_cais01_lamp_dust,
        373 - sCameraX,
        60,
        TILE_ATTR(PAL2, FALSE, FALSE, FALSE)
    );
    if (sLampDustSprite0 != NULL) {
        SPR_setAnim(sLampDustSprite0, 0);
        SPR_setAutoAnimation(sLampDustSprite0, FALSE);
        SPR_setFrame(sLampDustSprite0, 0);
    }

    sLampDustSprite1 = SPR_addSprite(
        &spr_cais01_lamp_dust,
        389 - sCameraX,
        72,
        TILE_ATTR(PAL2, FALSE, FALSE, FALSE)
    );
    if (sLampDustSprite1 != NULL) {
        SPR_setAnim(sLampDustSprite1, 0);
        SPR_setAutoAnimation(sLampDustSprite1, FALSE);
        SPR_setFrame(sLampDustSprite1, 1);
    }

    sGroundShadowSprite = SPR_addSprite(
        &spr_taina_ground_shadow,
        F16_toInt(sPlayer.x) - DEMO_PLAYER_PIVOT_X,
        DEMO_GROUND_Y - 12,
        TILE_ATTR(PAL1, FALSE, FALSE, FALSE)
    );
    if (sGroundShadowSprite != NULL) {
        SPR_setAnim(sGroundShadowSprite, 0);
        SPR_setAutoAnimation(sGroundShadowSprite, FALSE);
        SPR_setFrame(sGroundShadowSprite, 0);
    }

    sPlayerSprite = SPR_addSprite(
        &spr_taina_idle_guard,
        F16_toInt(sPlayer.x) - DEMO_PLAYER_PIVOT_X,
        F16_toInt(sPlayer.y) - DEMO_PLAYER_GROUND_Y,
        TILE_ATTR(PAL1, TRUE, FALSE, FALSE)
    );

    if (sPlayerSprite == NULL) {
        VDP_drawTextFill("SPRITE ALLOCATION FAILED", 8, 11, 24);
    } else {
        SPR_setAnim(sPlayerSprite, 0);
        SPR_setAutoAnimation(sPlayerSprite, FALSE);
        SPR_setFrame(sPlayerSprite, 0);
    }

    sCriaIdleFrame = 0;
    sCriaIdleFrameTicks = 0;
    sCriaWalkFrame = 0;
    sCriaWalkTicks = 0;
    sCriaWalking = FALSE;
    sCriaMode = 0;
    sCriaTelFrame = 0;
    sCriaTelTicks = 0;
    sCriaHitFrame = 0;
    sCriaHitTicks = 0;
    sCriaClock = 0;
    sCriaSprite = SPR_addSprite(
        &spr_cria_idle_lean,
        DEMO_CRIA_WORLD_X - sCameraX - DEMO_CRIA_PIVOT_X,
        DEMO_GROUND_Y - DEMO_CRIA_GROUND_Y,
        TILE_ATTR(PAL3, TRUE, FALSE, FALSE)
    );
    if (sCriaSprite != NULL) {
        SPR_setAnim(sCriaSprite, 0);
        SPR_setAutoAnimation(sCriaSprite, FALSE);
        SPR_setFrame(sCriaSprite, 0);
    }
}

void SCENE_demoUpdate(void)
{
    if (INPUT_pressed(BUTTON_START)) {
        gApp.paused = !gApp.paused;
        AUDIO_playCue(AUDIO_CUE_PAUSE);
        if (!gApp.paused) {
            VDP_clearTextArea(12, 11, 16, 3);
        }
        return;
    }

    if (gApp.paused) {
        demoDrawPause();
        return;
    }

    if (INPUT_pressed(BUTTON_MODE)) {
        SCENE_cleanupLineScroll(BG_A);
        VDP_setHorizontalScroll(BG_B, 0);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    demoUpdatePlayer();
    demoUpdateCamera();
    demoUpdateEnvironmentFx();
    demoUpdatePlayerAnimation();
    demoDrawPlayer();
    demoUpdateCria();
    demoDrawHud();
}

#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/reference_contract.h"

#define DEMO_WORLD_TILES 64
#define DEMO_WORLD_PX (DEMO_WORLD_TILES * 8)
#define DEMO_CAMERA_MAX_X (DEMO_WORLD_PX - 320)
#define DEMO_GROUND_Y 160
#define DEMO_PLAYER_MIN_X 8
#define DEMO_PLAYER_MAX_X (DEMO_WORLD_PX - 16)

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

static DemoPlayer sPlayer;
static s16 sCameraX;
static u16 sPrevPlayerCol;
static u16 sPrevPlayerRow;
static bool sHadPlayerCell;

static void demoDrawStaticWorld(void)
{
    u16 x;
    u16 y;

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_B, 0);

    VDP_setTextPlane(BG_B);
    for (y = 7; y < 19; y += 2) {
        VDP_drawText("+...+...+...+...+...+...+...+...+...+...", 0, y);
    }
    for (x = 0; x < DEMO_WORLD_TILES; x++) {
        VDP_drawText("=", x, 21);
    }

    VDP_drawText("ORIGIN", 2, 19);
    VDP_drawText("SAMPLE", 24, 18);
    VDP_drawText("BOUND", 54, 18);
    VDP_drawText("|", 31, 20);
    VDP_drawText("|", 32, 20);
    VDP_drawText("[]", 55, 20);

    VDP_setTextPlane(BG_A);
    VDP_drawText("FORGE REFERENCE", 12, 3);
    VDP_drawText("A/Y jump  B/Z run  X strike", 4, HUD_ROW_HINT_SECONDARY);
    VDP_drawText("START pause   MODE menu", 7, HUD_ROW_HINT_PRIMARY);
}

static void demoResetPlayer(void)
{
    sPlayer.x = FIX16(24);
    sPlayer.y = FIX16(DEMO_GROUND_Y);
    sPlayer.vx = 0;
    sPlayer.vy = 0;
    sPlayer.grounded = TRUE;
    sCameraX = 0;
    sPrevPlayerCol = 0;
    sPrevPlayerRow = 0;
    sHadPlayerCell = FALSE;
}

static void demoApplyHorizontalInput(u16 held)
{
    fix16 maxSpeed = (held & (BUTTON_B | BUTTON_Z)) ? DEMO_RUN_SPEED : DEMO_MAX_SPEED;

    if (held & BUTTON_LEFT) {
        sPlayer.vx -= DEMO_ACCEL;
    } else if (held & BUTTON_RIGHT) {
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

static void demoUpdatePlayer(void)
{
    bool wasGrounded = sPlayer.grounded;
    u16 held = INPUT_held(BUTTON_ALL) | REF_scriptHeld(gApp.sceneFrames);
    u16 pressed = INPUT_pressed(BUTTON_ALL) | REF_scriptPressed(gApp.sceneFrames);

    demoApplyHorizontalInput(held);

    if ((pressed & (BUTTON_A | BUTTON_Y)) && sPlayer.grounded) {
        sPlayer.vy = DEMO_JUMP_SPEED;
        sPlayer.grounded = FALSE;
        AUDIO_playCue(AUDIO_CUE_JUMP);
    }

    if (pressed & BUTTON_X) {
        AUDIO_playCue(AUDIO_CUE_STRIKE);
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
    VDP_setHorizontalScroll(BG_B, -sCameraX);
}

static void demoDrawPlayer(void)
{
    s16 screenX = F16_toInt(sPlayer.x) - sCameraX;
    s16 screenY = F16_toInt(sPlayer.y);
    u16 col;
    u16 row;

    if (sHadPlayerCell) {
        VDP_drawTextFill(" ", sPrevPlayerCol, sPrevPlayerRow, 1);
        if (sPrevPlayerRow < VDP_TEXT_SAFE_LAST_ROW) {
            VDP_drawTextFill(" ", sPrevPlayerCol, sPrevPlayerRow + 1, 1);
        }
    }

    if (screenX < 0 || screenX > 312 || screenY < 0 || screenY > 208) {
        sHadPlayerCell = FALSE;
        return;
    }

    col = (u16)(screenX >> 3);
    row = (u16)(screenY >> 3);
    VDP_drawText("@", col, row);
    if (row < VDP_TEXT_SAFE_LAST_ROW) {
        VDP_drawText("_", col, row + 1);
    }

    sPrevPlayerCol = col;
    sPrevPlayerRow = row;
    sHadPlayerCell = TRUE;
}

static void demoDrawHud(void)
{
    char line[40];
    const char* pad = INPUT_hasSixButtonPad() ? "6BTN" : "3BTN";
    const char* pause = gApp.paused ? "PAUSE" : "RUN";

    sprintf(line, "X:%03d CAM:%03d %s %s", F16_toInt(sPlayer.x), sCameraX, pad, pause);
    VDP_drawTextFill(line, 1, 5, 38);
}

static void demoDrawPause(void)
{
    VDP_drawTextFill("==== PAUSE ====", 12, 11, 16);
    VDP_drawTextFill("START: resume", 13, 13, 14);
}

void SCENE_demoEnter(void)
{
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101828));
    demoResetPlayer();
    REF_init(F16_toInt(sPlayer.x), F16_toInt(sPlayer.y), sCameraX);
    demoDrawStaticWorld();
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
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    demoUpdatePlayer();
    demoUpdateCamera();
    REF_observe(F16_toInt(sPlayer.x), F16_toInt(sPlayer.y), sPlayer.grounded, sCameraX);
    demoDrawPlayer();
    demoDrawHud();
}

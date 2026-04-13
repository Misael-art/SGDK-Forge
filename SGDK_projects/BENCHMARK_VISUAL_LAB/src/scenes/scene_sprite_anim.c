/**
 * scene_sprite_anim.c — S1.1 Sprite Animation Proof
 *
 * Demonstrates mastery of SGDK 2.11 sprite animation system:
 *   - 5 distinct animation cycles (idle, walk, attack, hurt, jump)
 *   - Manual input-driven state machine
 *   - Auto-cycle demo mode
 *   - Debug overlay with frame telemetry
 *   - SRAM evidence block for validation
 */
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/sram_evidence.h"
#include "resources.h"

/* --- Animation indices (match sprite sheet row order) --- */
#define ANIM_IDLE          0
#define ANIM_WALK          1
#define ANIM_ATTACK_LIGHT  2
#define ANIM_HURT          3
#define ANIM_JUMP          4
#define ANIM_COUNT         5

#define SCENE_ID           5
#define EVIDENCE_VERSION   3
#define EVIDENCE_SIZE      64

static const char* animNames[ANIM_COUNT] = {
    "IDLE  ", "WALK  ", "ATTACK", "HURT  ", "JUMP  "
};

/* --- State --- */
static Sprite* sprGaira;
static u8  currentAnim;
static s16 gairaX;
static s16 gairaY;
static s8  gairaDir;
static bool autoMode;
static u16 autoCycleTimer;

#define GAIRA_SPEED  2
#define AUTO_PERIOD  120

/* --- Evidence --- */
static void writeEvidence(void)
{
    SRAM_enable();
    EVIDENCE_writeHeader(EVIDENCE_VERSION, EVIDENCE_SIZE, gApp.totalFrames, SCENE_ID);
    SRAM_writeByte(14, currentAnim);
    SRAM_writeByte(15, (u8) sprGaira->frameInd);
    SRAM_writeByte(16, autoMode ? 1 : 0);
    EVIDENCE_writeU16BE(18, (u16) gairaX);
    EVIDENCE_writeU16BE(20, (u16) gairaY);
    EVIDENCE_writeU16BE(22, ANIM_COUNT);
    EVIDENCE_writePalette(24, PAL2);
    EVIDENCE_writeAscii(56, "spr_anim", 8);
    SRAM_disable();
}

/* --- Debug overlay --- */
static void drawOverlay(void)
{
    char line[40];

    VDP_drawText("S1.1 SPRITE ANIMATION PROOF", 6, 0);

    sprintf(line, "ANIM:%-6s FRM:%d/%d %s",
            animNames[currentAnim],
            sprGaira->frameInd + 1,
            sprGaira->animation->numFrame,
            autoMode ? "AUTO  " : "MANUAL");
    VDP_drawText(line, 1, 1);

    sprintf(line, "POS:%d,%d DIR:%s TILES:63",
            gairaX, gairaY,
            gairaDir > 0 ? "R" : "L");
    VDP_drawText(line, 1, 2);
}

/* --- Enter --- */
void SCENE_spriteAnimEnter(void)
{
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x181830));
    PAL_setPalette(PAL2, spr_gaira.palette->data, DMA);
    PAL_setPalette(PAL0, palette_grey, DMA);
    VDP_setTextPalette(PAL0);

    gairaX = 132;
    gairaY = 130;
    gairaDir = 1;
    currentAnim = ANIM_IDLE;
    autoMode = FALSE;
    autoCycleTimer = 0;

    sprGaira = SPR_addSprite(&spr_gaira, gairaX, gairaY,
                             TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    SPR_setAnim(sprGaira, ANIM_IDLE);
    SPR_setAutoAnimation(sprGaira, TRUE);

    VDP_drawText("D-PAD:move A:atk UP:jmp DN:hurt", 4, 25);
    VDP_drawText("START:auto/manual  B:menu", 7, 26);

    writeEvidence();
}

/* --- Update --- */
void SCENE_spriteAnimUpdate(void)
{
    u8 wantAnim;

    /* Exit */
    if (INPUT_pressed(BUTTON_B))
    {
        SPR_reset();
        VDP_clearPlane(BG_A, TRUE);
        VDP_clearPlane(BG_B, TRUE);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    /* Toggle auto mode */
    if (INPUT_pressed(BUTTON_START))
    {
        autoMode = !autoMode;
        autoCycleTimer = 0;
    }

    if (autoMode)
    {
        /* Auto-cycle through animations */
        autoCycleTimer++;
        if (autoCycleTimer >= AUTO_PERIOD)
        {
            autoCycleTimer = 0;
            currentAnim = (currentAnim + 1) % ANIM_COUNT;
            SPR_setAnim(sprGaira, currentAnim);
        }
    }
    else
    {
        /* Manual input-driven animation */
        wantAnim = ANIM_IDLE;

        if (INPUT_held(BUTTON_RIGHT))
        {
            gairaX += GAIRA_SPEED;
            gairaDir = 1;
            wantAnim = ANIM_WALK;
        }
        else if (INPUT_held(BUTTON_LEFT))
        {
            gairaX -= GAIRA_SPEED;
            gairaDir = -1;
            wantAnim = ANIM_WALK;
        }

        if (INPUT_pressed(BUTTON_A))
            wantAnim = ANIM_ATTACK_LIGHT;
        else if (INPUT_pressed(BUTTON_UP))
            wantAnim = ANIM_JUMP;
        else if (INPUT_pressed(BUTTON_DOWN))
            wantAnim = ANIM_HURT;

        if (sprGaira->animInd != wantAnim)
        {
            currentAnim = wantAnim;
            SPR_setAnim(sprGaira, currentAnim);
        }
    }

    /* Clamp position */
    if (gairaX < 0) gairaX = 0;
    if (gairaX > 264) gairaX = 264;

    SPR_setHFlip(sprGaira, gairaDir < 0);
    SPR_setPosition(sprGaira, gairaX, gairaY);

    /* Debug overlay */
    drawOverlay();

    /* Evidence every 60 frames */
    if ((gApp.sceneFrames & 63u) == 0u)
        writeEvidence();

    SPR_update();
}

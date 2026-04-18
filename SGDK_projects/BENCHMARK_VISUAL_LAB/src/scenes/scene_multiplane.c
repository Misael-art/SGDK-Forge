/**
 * scene_multiplane.c — S1.3 Multi-Plane Composition Proof
 *
 * Full integration: Gaira with 5 animations in a multi-plane
 * parallax stage, demonstrating depth separation and composition.
 *
 *   BG_B: sky/mountains at 25% camera speed (PAL0)
 *   BG_A: ground/trees at 100% camera speed (PAL1)
 *   SPR:  Gaira fighter with full animation (PAL2)
 */
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/sram_evidence.h"
#include "resources.h"

/* --- Animation indices --- */
#define ANIM_IDLE          0
#define ANIM_WALK          1
#define ANIM_ATTACK_LIGHT  2
#define ANIM_HURT          3
#define ANIM_JUMP          4
#define ANIM_COUNT         5

#define SCENE_ID           7
#define EVIDENCE_VERSION   3
#define EVIDENCE_SIZE      128

#define CAM_HALF_W    160
#define GAIRA_SPEED   2
#define WORLD_W       512
#define GROUND_Y      130
#define JUMP_VELOCITY 6
#define GRAVITY       1

static const char* animNames[ANIM_COUNT] = {
    "IDLE  ", "WALK  ", "ATTACK", "HURT  ", "JUMP  "
};

/* --- State --- */
static Sprite* sprGaira;
static s16 camX;
static s16 gairaWorldX;
static s16 gairaScreenY;
static s8  gairaDir;
static u8  currentAnim;
static bool isJumping;
static s16 jumpVelocity;
static u16 lockTimer;
static u16 bgbTiles;
static u16 bgaTiles;

/* --- Evidence --- */
static void writeEvidence(void)
{
    SRAM_enable();
    EVIDENCE_writeHeader(EVIDENCE_VERSION, EVIDENCE_SIZE, gApp.totalFrames, SCENE_ID);
    SRAM_writeByte(14, currentAnim);
    SRAM_writeByte(15, (u8) sprGaira->frameInd);
    EVIDENCE_writeU16BE(16, bgbTiles);
    EVIDENCE_writeU16BE(18, bgaTiles);
    EVIDENCE_writeU16BE(20, 63);  /* sprite tiles */
    EVIDENCE_writeU16BE(22, bgbTiles + bgaTiles + 63);
    EVIDENCE_writeU16BE(24, (u16) camX);
    EVIDENCE_writeU16BE(26, (u16) gairaWorldX);
    EVIDENCE_writeU16BE(28, (u16)(-(camX >> 2)));  /* BG_B scroll */
    EVIDENCE_writeU16BE(30, (u16)(-camX));          /* BG_A scroll */
    EVIDENCE_writePalette(32, PAL0);
    EVIDENCE_writePalette(64, PAL1);
    EVIDENCE_writePalette(96, PAL2);
    SRAM_disable();
}

/* --- Debug overlay --- */
static void drawOverlay(void)
{
    char line[40];

    VDP_drawText("S1.3 MULTIPLANE PROOF", 9, 0);

    sprintf(line, "CAM:%d BGB:%d BGA:%d",
            camX, -(camX >> 2), -camX);
    VDP_drawText(line, 1, 1);

    sprintf(line, "TILES B:%d A:%d S:63 T:%d",
            bgbTiles, bgaTiles,
            bgbTiles + bgaTiles + 63);
    VDP_drawText(line, 1, 2);

    sprintf(line, "ANIM:%-6s FRM:%d SPR:1",
            animNames[currentAnim],
            sprGaira->frameInd + 1);
    VDP_drawText(line, 1, 3);
}

/* --- Enter --- */
void SCENE_multiplaneEnter(void)
{
    u16 ind;

    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);

    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setPlaneSize(64, 32, TRUE);

    /* Palettes: BG_B cold < BG_A warm < sprite vivid */
    PAL_setPalette(PAL0, bg_b_sky.palette->data, DMA);
    PAL_setPalette(PAL1, bg_a_ground.palette->data, DMA);
    PAL_setPalette(PAL2, spr_gaira.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);

    /* Load BG tilesets + tilemaps */
    ind = TILE_USER_INDEX;

    VDP_loadTileSet(bg_b_sky.tileset, ind, DMA);
    VDP_setTileMapEx(BG_B, bg_b_sky.tilemap,
                     TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, ind),
                     0, 0, 0, 0, 64, 32, DMA);
    bgbTiles = bg_b_sky.tileset->numTile;
    ind += bgbTiles;

    VDP_loadTileSet(bg_a_ground.tileset, ind, DMA);
    VDP_setTileMapEx(BG_A, bg_a_ground.tilemap,
                     TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, ind),
                     0, 0, 0, 0, 64, 32, DMA);
    bgaTiles = bg_a_ground.tileset->numTile;
    ind += bgaTiles;

    /* Initialize Gaira sprite */
    gairaWorldX = 160;
    gairaScreenY = GROUND_Y;
    gairaDir = 1;
    currentAnim = ANIM_IDLE;
    isJumping = FALSE;
    jumpVelocity = 0;
    lockTimer = 0;
    camX = 0;

    sprGaira = SPR_addSprite(&spr_gaira,
                             CAM_HALF_W - 28, gairaScreenY,
                             TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    SPR_setAnim(sprGaira, ANIM_IDLE);
    SPR_setAutoAnimation(sprGaira, TRUE);

    VDP_drawText("D-PAD:move A:atk UP:jmp B:menu", 4, 27);

    writeEvidence();
}

/* --- Update --- */
void SCENE_multiplaneUpdate(void)
{
    u8 wantAnim;

    /* Exit */
    if (INPUT_pressed(BUTTON_B))
    {
        SPR_reset();
        VDP_clearPlane(BG_A, TRUE);
        VDP_clearPlane(BG_B, TRUE);
        VDP_setHorizontalScroll(BG_A, 0);
        VDP_setHorizontalScroll(BG_B, 0);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    wantAnim = ANIM_IDLE;

    /* Jump physics */
    if (isJumping)
    {
        gairaScreenY -= jumpVelocity;
        jumpVelocity -= GRAVITY;

        if (gairaScreenY >= GROUND_Y)
        {
            gairaScreenY = GROUND_Y;
            isJumping = FALSE;
            jumpVelocity = 0;
        }
        wantAnim = ANIM_JUMP;
    }

    /* Lock timer (attack/hurt) */
    if (lockTimer > 0)
    {
        lockTimer--;
        /* Keep current animation during lock */
        wantAnim = currentAnim;
    }
    else if (!isJumping)
    {
        /* Input: attack */
        if (INPUT_pressed(BUTTON_A))
        {
            wantAnim = ANIM_ATTACK_LIGHT;
            lockTimer = 20;
        }
        /* Input: hurt */
        else if (INPUT_pressed(BUTTON_DOWN))
        {
            wantAnim = ANIM_HURT;
            lockTimer = 15;
        }
        /* Input: jump */
        else if (INPUT_pressed(BUTTON_UP) && !isJumping)
        {
            isJumping = TRUE;
            jumpVelocity = JUMP_VELOCITY;
            wantAnim = ANIM_JUMP;
        }
        /* Input: walk */
        else if (INPUT_held(BUTTON_RIGHT))
        {
            gairaWorldX += GAIRA_SPEED;
            gairaDir = 1;
            wantAnim = ANIM_WALK;
        }
        else if (INPUT_held(BUTTON_LEFT))
        {
            gairaWorldX -= GAIRA_SPEED;
            gairaDir = -1;
            wantAnim = ANIM_WALK;
        }
    }

    /* Wrap world position */
    if (gairaWorldX < 0) gairaWorldX += WORLD_W;
    if (gairaWorldX >= WORLD_W) gairaWorldX -= WORLD_W;

    /* Camera follows */
    camX = gairaWorldX - CAM_HALF_W;

    /* Apply animation only when changed */
    if (sprGaira->animInd != wantAnim)
    {
        currentAnim = wantAnim;
        SPR_setAnim(sprGaira, currentAnim);
    }

    SPR_setHFlip(sprGaira, gairaDir < 0);
    SPR_setPosition(sprGaira, CAM_HALF_W - 28, gairaScreenY);

    /* Parallax scroll: BG_B 25%, BG_A 100% */
    VDP_setHorizontalScroll(BG_B, -(camX >> 2));
    VDP_setHorizontalScroll(BG_A, -camX);

    /* Debug overlay */
    drawOverlay();

    /* Evidence every 60 frames */
    if ((gApp.sceneFrames & 63u) == 0u)
        writeEvidence();

    SPR_update();
}

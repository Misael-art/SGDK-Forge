#include <genesis.h>

#include "resources.h"

#define VIEWPORT_WIDTH     320
#define VIEWPORT_HEIGHT    224
#define PLANE_WIDTH_TILES   64
#define PLANE_HEIGHT_TILES  32

#define SCENE_WIDTH        448
#define CAMERA_MAX_X       (SCENE_WIDTH - VIEWPORT_WIDTH)

#define BGB_IMG_WIDTH_TILES  32
#define BGB_STAMP_COUNT      (PLANE_WIDTH_TILES / BGB_IMG_WIDTH_TILES)
#define BGA_MAP_HEIGHT_TILES 28

/*
 * VRAM reservada ao motor de sprites (SPR_initEx).
 * Pior caso simultaneo na demo: debris 28+26+24 + player 23 tiles = 101 <= 160.
 * Valores >160 reduzem 1536-112-N e podem fazer BG_A+BG_B (1261) exceder o tecto.
 */
#define SPRITE_VRAM_SIZE     160
#define PLAYER_SPEED           2
#define PLAYER_WIDTH          40
#define PLAYER_HEIGHT         48
#define PLAYER_GROUND_MARGIN   8
#define PLAYER_GROUND_Y      (VIEWPORT_HEIGHT - PLAYER_HEIGHT - PLAYER_GROUND_MARGIN)
#define PLAYER_JUMP_SPEED     -7
#define PLAYER_GRAVITY         1
#define PLAYER_MAX_FALL        8
#define PLAYER_LAND_TICKS      8
#define PLAYER_SHOOT_TICKS    10

/* Posicoes mundo (X) dos tres blocos de foreground composicional (Layer C) */
#define DEBRIS_01_WORLD_X   40
#define DEBRIS_02_WORLD_X  180
#define DEBRIS_03_WORLD_X  320

static s16  gCameraX       = 0;
static s16  gPlayerX       = 96;
static s16  gPlayerY       = PLAYER_GROUND_Y;
static s16  gPlayerVX      = 0;
static s16  gPlayerVY      = 0;
static bool gShowOverlay   = FALSE;
static bool gPlayerOnGround = TRUE;
static bool gPlayerFacingLeft = FALSE;
static u16  gPrevInput     = 0;
static u16  gShootTicks    = 0;
static u16  gLandTicks     = 0;

static Sprite* gPlayerSprite      = NULL;
static Sprite* gDebrisSprites[3]  = { NULL, NULL, NULL };

static u16  gBgBBaseTile;
static u16  gBgABaseTile;

typedef enum
{
    PLAYER_ANIM_IDLE = 0,
    PLAYER_ANIM_WALK = 1,
    PLAYER_ANIM_JUMP = 2,
    PLAYER_ANIM_LAND = 3,
    PLAYER_ANIM_SHOOT = 4
} PlayerAnim;

static PlayerAnim gPlayerAnim = PLAYER_ANIM_IDLE;


static void loadBgBPlane(void)
{
    u16 stamp;

    gBgBBaseTile = TILE_USER_INDEX;
    VDP_loadTileSet(sky_bg_b.tileset, gBgBBaseTile, CPU);

    for (stamp = 0; stamp < BGB_STAMP_COUNT; stamp++)
    {
        VDP_setTileMapEx(
            BG_B,
            sky_bg_b.tilemap,
            TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, gBgBBaseTile),
            stamp * BGB_IMG_WIDTH_TILES, 0,
            0, 0,
            BGB_IMG_WIDTH_TILES, BGA_MAP_HEIGHT_TILES,
            CPU
        );
    }
}


static void loadBgAPlane(void)
{
    gBgABaseTile = gBgBBaseTile + sky_bg_b.tileset->numTile;
    VDP_loadTileSet(city_bg_a.tileset, gBgABaseTile, CPU);

    VDP_setTileMapEx(
        BG_A,
        city_bg_a.tilemap,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, gBgABaseTile),
        0, 0,
        0, 0,
        PLANE_WIDTH_TILES, BGA_MAP_HEIGHT_TILES,
        CPU
    );
}


static void drawOverlay(void)
{
    VDP_clearTextArea(0, 0, 40, 5);

    if (!gShowOverlay)
    {
        VDP_setWindowOff();
        return;
    }

    VDP_setWindowOnTop(5);
    VDP_drawText("PIPELINE SKILLS - URBAN", 3, 1);
    VDP_drawText("BG_B SKY  PAL0 1/4x", 3, 2);
    VDP_drawText("BG_A CITY PAL1 1.0x", 3, 3);
    VDP_drawText("C DEBRIS PAL2 1.25x", 3, 4);
}


static void drawScene(void)
{
    VDP_setEnable(FALSE);
    VDP_setPlaneSize(PLANE_WIDTH_TILES, PLANE_HEIGHT_TILES, TRUE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

    PAL_setPalette(PAL0, sky_bg_b.palette->data, CPU);
    PAL_setPalette(PAL1, city_bg_a.palette->data, CPU);
    VDP_setBackgroundColor(0);

    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_setWindowOff();

    loadBgBPlane();
    loadBgAPlane();

    SPR_initEx(SPRITE_VRAM_SIZE);

    PAL_setPalette(PAL2, spr_debris_01.palette->data, DMA);
    PAL_setPalette(PAL3, spr_player.palette->data, DMA);

    gDebrisSprites[0] = SPR_addSprite(
        &spr_debris_01, DEBRIS_01_WORLD_X, VIEWPORT_HEIGHT - 56,
        TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
    );
    gDebrisSprites[1] = SPR_addSprite(
        &spr_debris_02, DEBRIS_02_WORLD_X, VIEWPORT_HEIGHT - 56,
        TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
    );
    gDebrisSprites[2] = SPR_addSprite(
        &spr_debris_03, DEBRIS_03_WORLD_X, VIEWPORT_HEIGHT - 56,
        TILE_ATTR(PAL2, TRUE, FALSE, FALSE)
    );
    if (gDebrisSprites[0]) SPR_setDepth(gDebrisSprites[0], 0);
    if (gDebrisSprites[1]) SPR_setDepth(gDebrisSprites[1], 0);
    if (gDebrisSprites[2]) SPR_setDepth(gDebrisSprites[2], 0);

    gPlayerSprite = SPR_addSprite(
        &spr_player, gPlayerX, gPlayerY,
        TILE_ATTR(PAL3, TRUE, FALSE, FALSE)
    );
    if (gPlayerSprite)
    {
        SPR_setDepth(gPlayerSprite, 1);
        SPR_setAnim(gPlayerSprite, PLAYER_ANIM_IDLE);
    }

    drawOverlay();

    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);

    VDP_setEnable(TRUE);
}


static void applyPlayerAnimation(PlayerAnim nextAnim)
{
    if (!gPlayerSprite)
        return;
    if (gPlayerAnim != nextAnim)
    {
        gPlayerAnim = nextAnim;
        SPR_setAnim(gPlayerSprite, (u16)gPlayerAnim);
    }
}


static void updateInput(void)
{
    const u16 state   = JOY_readJoypad(JOY_1);
    const u16 pressed = state & ~gPrevInput;

    if (pressed & BUTTON_A)
    {
        gShowOverlay = !gShowOverlay;
        drawOverlay();
    }

    gPlayerVX = 0;
    if (state & BUTTON_RIGHT)
    {
        gPlayerVX = PLAYER_SPEED;
        gPlayerFacingLeft = FALSE;
    }
    if (state & BUTTON_LEFT)
    {
        gPlayerVX = -PLAYER_SPEED;
        gPlayerFacingLeft = TRUE;
    }
    gPlayerX += gPlayerVX;

    if ((pressed & BUTTON_B) && gPlayerOnGround)
    {
        gPlayerOnGround = FALSE;
        gPlayerVY = PLAYER_JUMP_SPEED;
        gLandTicks = 0;
    }
    if (pressed & BUTTON_C)
        gShootTicks = PLAYER_SHOOT_TICKS;

    if (!gPlayerOnGround)
    {
        gPlayerVY += PLAYER_GRAVITY;
        if (gPlayerVY > PLAYER_MAX_FALL)
            gPlayerVY = PLAYER_MAX_FALL;
        gPlayerY += gPlayerVY;
        if (gPlayerY >= PLAYER_GROUND_Y)
        {
            gPlayerY = PLAYER_GROUND_Y;
            gPlayerVY = 0;
            gPlayerOnGround = TRUE;
            gLandTicks = PLAYER_LAND_TICKS;
        }
    }
    else
    {
        gPlayerY = PLAYER_GROUND_Y;
    }

    if (gShootTicks > 0)
        gShootTicks--;
    if (gLandTicks > 0)
        gLandTicks--;

    if (gPlayerX < 0) gPlayerX = 0;
    if (gPlayerX > SCENE_WIDTH - PLAYER_WIDTH)
        gPlayerX = SCENE_WIDTH - PLAYER_WIDTH;

    if (!gPlayerOnGround)
        applyPlayerAnimation(PLAYER_ANIM_JUMP);
    else if (gLandTicks > 0)
        applyPlayerAnimation(PLAYER_ANIM_LAND);
    else if (gShootTicks > 0)
        applyPlayerAnimation(PLAYER_ANIM_SHOOT);
    else if (gPlayerVX != 0)
        applyPlayerAnimation(PLAYER_ANIM_WALK);
    else
        applyPlayerAnimation(PLAYER_ANIM_IDLE);

    if (gPlayerSprite)
        SPR_setHFlip(gPlayerSprite, gPlayerFacingLeft);

    gPrevInput = state;
}


static void updateCamera(void)
{
    s16 targetCamX = gPlayerX - (VIEWPORT_WIDTH / 2);

    if (targetCamX < 0)          targetCamX = 0;
    if (targetCamX > CAMERA_MAX_X) targetCamX = CAMERA_MAX_X;

    gCameraX = targetCamX;

    VDP_setHorizontalScroll(BG_A, -gCameraX);
    VDP_setHorizontalScroll(BG_B, -(gCameraX >> 2));

    /* Parallax 1.25x no foreground composicional: desloca 1/4 extra vs camera */
    {
        const s16 debrisParallax = gCameraX + (gCameraX >> 2);

        if (gDebrisSprites[0])
            SPR_setPosition(
                gDebrisSprites[0],
                DEBRIS_01_WORLD_X - debrisParallax,
                VIEWPORT_HEIGHT - 56
            );
        if (gDebrisSprites[1])
            SPR_setPosition(
                gDebrisSprites[1],
                DEBRIS_02_WORLD_X - debrisParallax,
                VIEWPORT_HEIGHT - 56
            );
        if (gDebrisSprites[2])
            SPR_setPosition(
                gDebrisSprites[2],
                DEBRIS_03_WORLD_X - debrisParallax,
                VIEWPORT_HEIGHT - 56
            );
    }

    if (gPlayerSprite)
        SPR_setPosition(gPlayerSprite, gPlayerX - gCameraX, gPlayerY);
}


int main(bool hardReset)
{
    (void)hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(PLANE_WIDTH_TILES, PLANE_HEIGHT_TILES, TRUE);
    VDP_setTextPlane(WINDOW);
    VDP_setTextPriority(TRUE);
    JOY_init();

    drawScene();

    while (TRUE)
    {
        updateInput();
        updateCamera();

        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

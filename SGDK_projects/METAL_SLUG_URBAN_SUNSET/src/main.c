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

/* VRAM reservada ao motor de sprites: 3x debris 64x48 + player 32x64 + margem */
#define SPRITE_VRAM_SIZE   160
#define PLAYER_SPEED         2

/* Posicoes mundo (X) dos tres blocos de foreground composicional (Layer C) */
#define DEBRIS_01_WORLD_X   40
#define DEBRIS_02_WORLD_X  180
#define DEBRIS_03_WORLD_X  320

static s16  gCameraX       = 0;
static s16  gPlayerX       = 160;
static s16  gPlayerY       = 160;
static bool gShowOverlay   = FALSE;
static u16  gPrevInput     = 0;

static Sprite* gPlayerSprite      = NULL;
static Sprite* gDebrisSprites[3]  = { NULL, NULL, NULL };

static u16  gBgBBaseTile;
static u16  gBgABaseTile;


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
        SPR_setDepth(gPlayerSprite, 1);

    drawOverlay();

    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);

    VDP_setEnable(TRUE);
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

    if (state & BUTTON_RIGHT)  gPlayerX += PLAYER_SPEED;
    if (state & BUTTON_LEFT)   gPlayerX -= PLAYER_SPEED;
    if (state & BUTTON_UP)     gPlayerY -= PLAYER_SPEED;
    if (state & BUTTON_DOWN)   gPlayerY += PLAYER_SPEED;

    if (gPlayerX < 0)                    gPlayerX = 0;
    if (gPlayerX > SCENE_WIDTH - 32)     gPlayerX = SCENE_WIDTH - 32;
    if (gPlayerY < 0)                    gPlayerY = 0;
    if (gPlayerY > VIEWPORT_HEIGHT - 64) gPlayerY = VIEWPORT_HEIGHT - 64;

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

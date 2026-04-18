/**
 * scene_parallax.c — POC for Sprint 1 skills:
 *   S1.1 Sprite Animation (idle + walk with timing)
 *   S1.2 Character Design (hero sprite with palette hierarchy)
 *   S1.3 Multi-Plane Composition (BG_B + BG_A + sprite + parallax)
 *
 * Demonstrates:
 *   - BG_B (sky/mountains) at 25% camera speed
 *   - BG_A (ground/trees) at 100% camera speed
 *   - Sprite hero with idle/walk animation
 *   - Palette hierarchy: PAL0 cold < PAL1 medium < PAL2 warm
 */
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "resources.h"

/* ---------- state ---------- */
static Sprite* sprHero;

static s16 camX;
static s16 heroWorldX;
static s16 heroScreenY;
static s8  heroDir;       /* 1 = right, -1 = left */
static bool heroWalking;

#define CAM_HALF_W  160
#define HERO_SPEED  2
#define WORLD_W     512

/* ---------- enter ---------- */
void SCENE_parallaxEnter(void)
{
    u16 ind;

    /* Reset VDP state */
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);

    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setPlaneSize(64, 32, TRUE);

    /* --- Palettes: brightness hierarchy BG_B < BG_A < sprite --- */
    PAL_setPalette(PAL0, bg_b_sky.palette->data, DMA);
    PAL_setPalette(PAL1, bg_a_ground.palette->data, DMA);
    PAL_setPalette(PAL2, spr_hero.palette->data, DMA);

    /* --- Load tilesets + draw tilemaps --- */
    ind = TILE_USER_INDEX;

    /* BG_B: sky + mountains (512x256 = 64x32 tiles, fills plane exactly) */
    VDP_loadTileSet(bg_b_sky.tileset, ind, DMA);
    VDP_setTileMapEx(BG_B, bg_b_sky.tilemap,
                     TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, ind),
                     0, 0, 0, 0, 64, 32, DMA);
    ind += bg_b_sky.tileset->numTile;

    /* BG_A: ground + trees (512x256, transparent top shows BG_B) */
    VDP_loadTileSet(bg_a_ground.tileset, ind, DMA);
    VDP_setTileMapEx(BG_A, bg_a_ground.tilemap,
                     TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, ind),
                     0, 0, 0, 0, 64, 32, DMA);
    ind += bg_a_ground.tileset->numTile;

    /* --- Sprite hero (S1.1 + S1.2) --- */
    heroWorldX = 160;
    heroScreenY = 118;
    heroDir = 1;
    heroWalking = FALSE;
    camX = 0;

    sprHero = SPR_addSprite(&spr_hero, CAM_HALF_W - 16, heroScreenY,
                            TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    SPR_setAnim(sprHero, 0);  /* idle */
    SPR_setAutoAnimation(sprHero, TRUE);

    /* Info overlay */
    VDP_setTextPalette(PAL0);
    VDP_drawText("S1 POC: PARALLAX + ANIM", 8, 0);
    VDP_drawText("D-PAD:move  B:menu  C:HUD", 7, 27);
}

/* ---------- update ---------- */
void SCENE_parallaxUpdate(void)
{
    /* --- Input --- */
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

    heroWalking = FALSE;
    if (INPUT_held(BUTTON_RIGHT))
    {
        heroWorldX += HERO_SPEED;
        heroDir = 1;
        heroWalking = TRUE;
    }
    else if (INPUT_held(BUTTON_LEFT))
    {
        heroWorldX -= HERO_SPEED;
        heroDir = -1;
        heroWalking = TRUE;
    }

    /* Wrap world X within 512px plane width */
    if (heroWorldX < 0) heroWorldX += WORLD_W;
    if (heroWorldX >= WORLD_W) heroWorldX -= WORLD_W;

    /* Camera follows hero */
    camX = heroWorldX - CAM_HALF_W;

    /* --- Animation (S1.1): idle/walk swap --- */
    s16 wantAnim = heroWalking ? 1 : 0;
    if (sprHero->animInd != wantAnim)
        SPR_setAnim(sprHero, wantAnim);

    SPR_setHFlip(sprHero, heroDir < 0);
    SPR_setPosition(sprHero, CAM_HALF_W - 16, heroScreenY);

    /* --- Parallax scroll (S1.3) --- */
    /* BG_B: 25% speed — distant mountains (cold, low detail) */
    VDP_setHorizontalScroll(BG_B, -(camX >> 2));

    /* BG_A: 100% speed — gameplay layer (trees, ground) */
    VDP_setHorizontalScroll(BG_A, -camX);

    SPR_update();
}

#include <genesis.h>

#include "resources.h"

#define VIEWPORT_WIDTH       320
#define VIEWPORT_HEIGHT      224
#define PLANE_WIDTH_TILES     64
#define PLANE_HEIGHT_TILES    32
#define WINDOW_ROWS            8

#define BG_B_PARALLAX_SHIFT    2
#define SCROLL_STEP            2

typedef struct
{
    const char* name;
    const Image* bgB;
    const Image* bgA;
    u16 sceneWidthPx;
    const char* budgetLabel;
} SceneVariant;

typedef struct
{
    const char* sceneName;
    const SceneVariant* variants;
    u16 variantCount;
} SceneGroup;

static const SceneVariant sUrbanVariants[] =
{
    {
        "default_multi_plane_method",
        &urban_default_bg_b,
        &urban_default_bg_a,
        448,
        "baseline em uso no projeto"
    },
    {
        "anime_linefirst_balanced",
        &urban_linefirst_balanced_bg_b,
        &urban_linefirst_balanced_bg_a,
        448,
        "comparativo line-first balanced"
    },
    {
        "anime_linefirst_cohesive",
        &urban_linefirst_cohesive_bg_b,
        &urban_linefirst_cohesive_bg_a,
        448,
        "comparativo line-first cohesive"
    }
};

static const SceneVariant sMission1Variants[] =
{
    {
        "flat_strict15",
        &mission1_shared_bg_b,
        &mission1_flat_strict15_bg_a,
        448,
        "flat strict-15 para leitura"
    },
    {
        "flat_snap700",
        &mission1_shared_bg_b,
        &mission1_flat_snap700_bg_a,
        448,
        "flat snap700 para comparacao"
    },
    {
        "default_skylift",
        &mission1_shared_bg_b,
        &mission1_skylift_bg_a,
        448,
        "default skylift do projeto"
    }
};

static const SceneGroup sScenes[] =
{
    { "URBAN SUNSET", sUrbanVariants, 3 },
    { "MISSION 1",    sMission1Variants, 3 }
};

static u16 gSceneIndex = 0;
static u16 gVariantIndex = 0;
static s16 gScrollX = 0;
static bool gShowOverlay = TRUE;
static u16 gPrevInput = 0;

static void clearOverlayText(void)
{
    VDP_clearTextArea(0, 0, 40, 32);
}

static const SceneVariant* getCurrentVariant(void)
{
    return &sScenes[gSceneIndex].variants[gVariantIndex];
}

static s16 getScrollMaxX(void)
{
    const SceneVariant* variant = getCurrentVariant();
    const s16 maxX = (s16)variant->sceneWidthPx - VIEWPORT_WIDTH;
    return (maxX > 0) ? maxX : 0;
}

static void applyScroll(void)
{
    VDP_setHorizontalScroll(BG_A, -gScrollX);
    VDP_setHorizontalScroll(BG_B, -(gScrollX >> BG_B_PARALLAX_SHIFT));
}

static void drawOverlay(void)
{
    char line[41];
    const SceneVariant* variant = getCurrentVariant();

    clearOverlayText();
    if (!gShowOverlay)
    {
        VDP_setWindowOff();
        return;
    }

    VDP_setWindowOnTop(WINDOW_ROWS);
    VDP_drawText("ROM VIEWER SEM SPRITES", 1, 0);
    sprintf(line, "Cena: %s", sScenes[gSceneIndex].sceneName);
    VDP_drawText(line, 1, 1);
    sprintf(line, "Variante: %s", variant->name);
    VDP_drawText(line, 1, 2);
    sprintf(line, "Scroll: %d/%d", gScrollX, getScrollMaxX());
    VDP_drawText(line, 1, 3);
    sprintf(line, "Budget: %s", variant->budgetLabel);
    VDP_drawText(line, 1, 4);
    VDP_drawText("LEFT/RIGHT:SCROLL  START:RESET", 1, 5);
    VDP_drawText("A:CENA  B:VARIANTE  C:OVERLAY", 1, 6);
}

static void loadCurrentSceneVariant(void)
{
    const SceneVariant* variant = getCurrentVariant();
    u16 bgBWidthTiles;
    u16 bgBHeightTiles;
    u16 bgAWidthTiles;
    u16 bgAHeightTiles;
    u16 stamp;
    u16 stampCount;
    u16 bgBBaseTile;
    u16 bgABaseTile;
    u16 fillRow;

    VDP_setEnable(FALSE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(WINDOW, TRUE);

    PAL_setPalette(PAL0, variant->bgB->palette->data, CPU);
    PAL_setPalette(PAL1, variant->bgA->palette->data, CPU);
    /* Index 0 is often transparent/matte in these assets, so avoid showing it. */
    VDP_setBackgroundColor(1);

    bgBBaseTile = TILE_USER_INDEX;
    VDP_loadTileSet(variant->bgB->tileset, bgBBaseTile, CPU);

    bgBWidthTiles = variant->bgB->tilemap->w;
    bgBHeightTiles = variant->bgB->tilemap->h;
    stampCount = (bgBWidthTiles > 0) ? (PLANE_WIDTH_TILES / bgBWidthTiles) : 0;

    for (stamp = 0; stamp < stampCount; stamp++)
    {
        VDP_setTileMapEx(
            BG_B,
            variant->bgB->tilemap,
            TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, bgBBaseTile),
            stamp * bgBWidthTiles, 0,
            0, 0,
            bgBWidthTiles, bgBHeightTiles,
            CPU
        );
    }

    bgABaseTile = bgBBaseTile + variant->bgB->tileset->numTile;
    VDP_loadTileSet(variant->bgA->tileset, bgABaseTile, CPU);

    bgAWidthTiles = variant->bgA->tilemap->w;
    bgAHeightTiles = variant->bgA->tilemap->h;
    VDP_setTileMapEx(
        BG_A,
        variant->bgA->tilemap,
        TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, bgABaseTile),
        0, 0,
        0, 0,
        bgAWidthTiles, bgAHeightTiles,
        CPU
    );

    /*
     * The source images are 224px tall (28 tile rows) while the plane is 32 rows.
     * Repeat the last valid row to avoid exposing palette-0 matte at the bottom.
     */
    for (fillRow = bgBHeightTiles; fillRow < PLANE_HEIGHT_TILES; fillRow++)
    {
        for (stamp = 0; stamp < stampCount; stamp++)
        {
            VDP_setTileMapEx(
                BG_B,
                variant->bgB->tilemap,
                TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, bgBBaseTile),
                stamp * bgBWidthTiles, fillRow,
                0, bgBHeightTiles - 1,
                bgBWidthTiles, 1,
                CPU
            );
        }
    }

    for (fillRow = bgAHeightTiles; fillRow < PLANE_HEIGHT_TILES; fillRow++)
    {
        VDP_setTileMapEx(
            BG_A,
            variant->bgA->tilemap,
            TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, bgABaseTile),
            0, fillRow,
            0, bgAHeightTiles - 1,
            bgAWidthTiles, 1,
            CPU
        );
    }

    gScrollX = 0;
    applyScroll();
    drawOverlay();
    VDP_setEnable(TRUE);
}

static void nextScene(void)
{
    gSceneIndex++;
    if (gSceneIndex >= (sizeof(sScenes) / sizeof(sScenes[0])))
        gSceneIndex = 0;
    gVariantIndex = 0;
    loadCurrentSceneVariant();
}

static void nextVariant(void)
{
    gVariantIndex++;
    if (gVariantIndex >= sScenes[gSceneIndex].variantCount)
        gVariantIndex = 0;
    loadCurrentSceneVariant();
}

static void clampScroll(void)
{
    const s16 maxScroll = getScrollMaxX();
    if (gScrollX < 0)
        gScrollX = 0;
    if (gScrollX > maxScroll)
        gScrollX = maxScroll;
}

static void updateInput(void)
{
    const u16 state = JOY_readJoypad(JOY_1);
    const u16 pressed = state & ~gPrevInput;
    bool redrawOverlay = FALSE;

    if (state & BUTTON_LEFT)
    {
        gScrollX -= SCROLL_STEP;
        redrawOverlay = TRUE;
    }
    if (state & BUTTON_RIGHT)
    {
        gScrollX += SCROLL_STEP;
        redrawOverlay = TRUE;
    }

    if (pressed & BUTTON_START)
    {
        gScrollX = 0;
        redrawOverlay = TRUE;
    }
    if (pressed & BUTTON_A)
    {
        nextScene();
        gPrevInput = state;
        return;
    }
    if (pressed & BUTTON_B)
    {
        nextVariant();
        gPrevInput = state;
        return;
    }
    if (pressed & BUTTON_C)
    {
        gShowOverlay = !gShowOverlay;
        redrawOverlay = TRUE;
    }

    clampScroll();
    applyScroll();
    if (redrawOverlay || gShowOverlay)
        drawOverlay();
    gPrevInput = state;
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

    loadCurrentSceneVariant();

    while (TRUE)
    {
        updateInput();
        SYS_doVBlankProcess();
    }

    return 0;
}

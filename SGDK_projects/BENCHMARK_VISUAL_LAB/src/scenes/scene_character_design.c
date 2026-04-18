/**
 * scene_character_design.c — S1.2 Character Design Proof
 *
 * Demonstrates character visual quality evaluation:
 *   - Normal display with palette visualization
 *   - Silhouette mode (readability test)
 *   - Palette showcase with hex values
 *   - Animation cycling for pose evaluation
 *   - SRAM evidence block for validation
 */
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"
#include "system/sram_evidence.h"
#include "resources.h"

#define ANIM_COUNT         5
#define SCENE_ID           6
#define EVIDENCE_VERSION   3
#define EVIDENCE_SIZE      80

#define MODE_NORMAL        0
#define MODE_SILHOUETTE    1
#define MODE_PALETTE       2
#define MODE_COUNT         3

static const char* modeNames[MODE_COUNT] = {
    "NORMAL    ", "SILHOUETTE", "PALETTE   "
};

static const char* animNames[ANIM_COUNT] = {
    "IDLE  ", "WALK  ", "ATTACK", "HURT  ", "JUMP  "
};

/* Silhouette palette: index 0 transparent, 1-15 all black */
static const u16 silhouettePal[16] = {
    0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000
};

/* --- State --- */
static Sprite* sprGaira;
static u8  displayMode;
static u8  currentAnim;
static bool autoMode;
static u16 autoCycleTimer;

/* --- Evidence --- */
static void writeEvidence(void)
{
    SRAM_enable();
    EVIDENCE_writeHeader(EVIDENCE_VERSION, EVIDENCE_SIZE, gApp.totalFrames, SCENE_ID);
    SRAM_writeByte(14, displayMode);
    SRAM_writeByte(15, currentAnim);
    EVIDENCE_writeU16BE(16, 7);   /* tile width */
    EVIDENCE_writeU16BE(18, 9);   /* tile height */
    EVIDENCE_writePalette(24, PAL2);
    EVIDENCE_writeAscii(56, "chr_dsgn", 8);
    SRAM_disable();
}

/* --- Draw palette bar on screen using text --- */
static void drawPaletteInfo(void)
{
    char line[40];
    u16 colors[16];
    u16 i;

    PAL_getPalette(PAL2, colors);

    if (displayMode == MODE_PALETTE)
    {
        VDP_drawText("PALETTE ANALYSIS (PAL2)", 8, 5);
        for (i = 0; i < 16; i++)
        {
            u16 c = colors[i];
            u16 r = (c >> 1) & 0x07;
            u16 g = (c >> 5) & 0x07;
            u16 b = (c >> 9) & 0x07;
            sprintf(line, "[%2d] %03X R%d G%d B%d%s",
                    i, c, r, g, b,
                    i == 0 ? " TRANSP" : "");
            VDP_drawText(line, 2, (u16)(7 + i));
        }
    }
}

/* --- Debug overlay --- */
static void drawOverlay(void)
{
    char line[40];

    VDP_drawText("S1.2 CHARACTER DESIGN PROOF", 6, 0);

    sprintf(line, "MODE:%-10s ANIM:%-6s",
            modeNames[displayMode],
            animNames[currentAnim]);
    VDP_drawText(line, 1, 1);

    sprintf(line, "CELL:7x9 TILES:63 BBOX:56x72 %s",
            autoMode ? "AUTO" : "    ");
    VDP_drawText(line, 1, 2);
}

/* --- Enter --- */
void SCENE_characterDesignEnter(void)
{
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x0A0A1A));
    PAL_setPalette(PAL2, spr_gaira.palette->data, DMA);
    PAL_setPalette(PAL0, palette_grey, DMA);
    VDP_setTextPalette(PAL0);

    displayMode = MODE_NORMAL;
    currentAnim = 0;
    autoMode = FALSE;
    autoCycleTimer = 0;

    sprGaira = SPR_addSprite(&spr_gaira, 132, 76,
                             TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    SPR_setAnim(sprGaira, 0);
    SPR_setAutoAnimation(sprGaira, TRUE);

    VDP_drawText("A:mode L/R:anim START:auto B:menu", 3, 26);

    drawOverlay();
    writeEvidence();
}

/* --- Update --- */
void SCENE_characterDesignUpdate(void)
{
    /* Exit */
    if (INPUT_pressed(BUTTON_B))
    {
        /* Restore real palette in case we were in silhouette mode */
        PAL_setPalette(PAL2, spr_gaira.palette->data, DMA);
        SPR_reset();
        VDP_clearPlane(BG_A, TRUE);
        VDP_clearPlane(BG_B, TRUE);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    /* Cycle display mode */
    if (INPUT_pressed(BUTTON_A))
    {
        displayMode = (displayMode + 1) % MODE_COUNT;

        /* Apply palette for current mode */
        if (displayMode == MODE_SILHOUETTE)
            PAL_setPalette(PAL2, silhouettePal, DMA);
        else
            PAL_setPalette(PAL2, spr_gaira.palette->data, DMA);

        /* Clear area for palette text when entering/leaving palette mode */
        VDP_clearTextArea(0, 5, 40, 20);
    }

    /* Toggle auto-cycle */
    if (INPUT_pressed(BUTTON_START))
    {
        autoMode = !autoMode;
        autoCycleTimer = 0;
    }

    /* Cycle animations */
    if (autoMode)
    {
        autoCycleTimer++;
        if (autoCycleTimer >= 90)
        {
            autoCycleTimer = 0;
            currentAnim = (currentAnim + 1) % ANIM_COUNT;
            SPR_setAnim(sprGaira, currentAnim);
        }
    }
    else
    {
        if (INPUT_pressed(BUTTON_RIGHT))
        {
            currentAnim = (currentAnim + 1) % ANIM_COUNT;
            SPR_setAnim(sprGaira, currentAnim);
        }
        else if (INPUT_pressed(BUTTON_LEFT))
        {
            currentAnim = (currentAnim == 0) ? ANIM_COUNT - 1 : currentAnim - 1;
            SPR_setAnim(sprGaira, currentAnim);
        }
    }

    /* Draw overlays */
    drawOverlay();
    drawPaletteInfo();

    /* Evidence every 60 frames */
    if ((gApp.sceneFrames & 63u) == 0u)
        writeEvidence();

    SPR_update();
}

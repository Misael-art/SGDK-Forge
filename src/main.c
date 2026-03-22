#include <genesis.h>
#include "resources.h"

// States
#define STATE_CHAR_SELECT 0
#define STATE_ANIM_TEST 1

int currentState = STATE_CHAR_SELECT;

// Characters
#define CHAR_MEGAMAN 0
#define CHAR_KEN 1
#define CHAR_EARTHQUAKE 2
#define CHAR_BLACKHEART 3

const char* charNames[] = {
    "MegaMan (Small)",
    "Ken (Classic Fighter)",
    "Earthquake (Large)",
    "Blackheart (Render)"
};

int cursorChar = 0;
int p1Char = -1;
int p2Char = -1;
bool bgEnabled = TRUE;

Sprite* sprP1 = NULL;
Sprite* sprP2 = NULL;

const SpriteDefinition* getSpriteDef(int charId) {
    if (charId == CHAR_MEGAMAN) return &spr_megaman;
    if (charId == CHAR_KEN) return &spr_ken;
    if (charId == CHAR_EARTHQUAKE) return &spr_earthquake;
    if (charId == CHAR_BLACKHEART) return &spr_blackheart;
    return &spr_megaman;
}

void joyEvent(u16 joy, u16 changed, u16 state) {
    if (joy != JOY_1) return;

    if (currentState == STATE_CHAR_SELECT) {
        if (changed & state & BUTTON_LEFT) {
            cursorChar--;
            if (cursorChar < 0) cursorChar = 3;
        } else if (changed & state & BUTTON_RIGHT) {
            cursorChar++;
            if (cursorChar > 3) cursorChar = 0;
        } else if (changed & state & BUTTON_A) {
            p1Char = cursorChar;
        } else if (changed & state & BUTTON_B) {
            p2Char = cursorChar;
        } else if (changed & state & BUTTON_START) {
            if (p1Char != -1 && p2Char != -1) {
                currentState = STATE_ANIM_TEST;
            }
        }
    } else if (currentState == STATE_ANIM_TEST) {
        if (changed & state & BUTTON_START) {
            // Return to the menu.
            SYS_hardReset();
        } else if (changed & state & BUTTON_C) {
            bgEnabled = !bgEnabled;
            if (bgEnabled) {
                VDP_drawImageEx(BG_B, &bg_metal_slug, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, 1), 0, 0, FALSE, TRUE);
            } else {
                VDP_clearPlane(BG_B, TRUE);
            }
        }
    }
}

void stateCharSelect() {
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setTextPalette(PAL0);

    while (currentState == STATE_CHAR_SELECT) {
        VDP_drawText("--- SGDK-FORGE PIPELINE DEMO ---", 3, 2);

        char textBuf[64];
        sprintf(textBuf, "Cursor Selection: %s    ", charNames[cursorChar]);
        VDP_drawText(textBuf, 2, 6);

        sprintf(textBuf, "P1 Selected: %s    ", p1Char == -1 ? "NONE" : charNames[p1Char]);
        VDP_drawText(textBuf, 2, 8);

        sprintf(textBuf, "P2 Selected: %s    ", p2Char == -1 ? "NONE" : charNames[p2Char]);
        VDP_drawText(textBuf, 2, 10);

        VDP_drawText("Modernizing the Genesis Asset Pipeline", 1, 14);
        VDP_drawText("Controls:", 2, 16);
        VDP_drawText("LEFT/RIGHT - Move Cursor", 2, 17);
        VDP_drawText("A - Assign Player 1", 2, 18);
        VDP_drawText("B - Assign Player 2", 2, 19);
        VDP_drawText("START - Launch Demo (needs P1/P2)", 2, 20);

        SYS_doVBlankProcess();
    }
}

void stateAnimTest() {
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    // Initialize sprites.
    SPR_init();

    // Load palettes.
    const SpriteDefinition* def1 = getSpriteDef(p1Char);
    const SpriteDefinition* def2 = getSpriteDef(p2Char);

    PAL_setPalette(PAL1, def1->palette->data, DMA);
    PAL_setPalette(PAL2, def2->palette->data, DMA);
    PAL_setPalette(PAL0, bg_metal_slug.palette->data, DMA);

    sprP1 = SPR_addSprite(def1, 60, 100, TILE_ATTR(PAL1, TRUE, FALSE, FALSE));
    sprP2 = SPR_addSprite(def2, 180, 100, TILE_ATTR(PAL2, TRUE, FALSE, TRUE)); // P2 flipped horizontally.

    if (bgEnabled) {
        VDP_drawImageEx(BG_B, &bg_metal_slug, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, 1), 0, 0, FALSE, TRUE);
    }

    VDP_drawText("SGDK-FORGE | C=Toggle BG | START=Reset", 1, 2);

    while (currentState == STATE_ANIM_TEST) {
        SPR_update();
        SYS_doVBlankProcess();
    }

    SPR_end();
}

int main(bool hardReset) {
    (void) hardReset;
    JOY_init();
    JOY_setEventHandler(joyEvent);

    VDP_setScreenWidth320();

    while (1) {
        if (currentState == STATE_CHAR_SELECT) {
            stateCharSelect();
        } else if (currentState == STATE_ANIM_TEST) {
            stateAnimTest();
        }
    }

    return 0;
}

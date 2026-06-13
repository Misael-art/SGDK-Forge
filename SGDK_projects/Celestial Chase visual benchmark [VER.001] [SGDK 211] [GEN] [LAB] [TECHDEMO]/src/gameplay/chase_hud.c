#include <genesis.h>

#include "gameplay/chase_hud.h"
#include "resources.h"
#include "system/save_data.h"

static bool sHudDirty;
static bool sResultVisible;
static bool sCinematic;

void CHASE_HUD_enter(void)
{
    VDP_loadFont(&ts_chase_hud_font_v011, CPU);
    VDP_setWindowOnTop(2);
    VDP_setTextPlane(WINDOW);
    VDP_setTextPalette(PAL2);
    VDP_clearTileMapRect(WINDOW, 0, 0, 64, 32);
    sHudDirty = TRUE;
    sResultVisible = FALSE;
    sCinematic = FALSE;
}

void CHASE_HUD_update(const ChaseRulesState* rules)
{
    char line[40];
    u16 secondsLeft;
    u32 highscore;

    if (sResultVisible) {
        return;
    }

    if (!sHudDirty && (rules->roundFrame & 7u) != 0) {
        return;
    }

    secondsLeft = (rules->roundFrame < rules->roundLength)
        ? (u16)((rules->roundLength - rules->roundFrame) / rules->targetFps)
        : 0;
    sprintf(line, "CELESTIAL CHASE  P%u  %02us", CHASE_RULES_phaseNumber(rules), secondsLeft);
    VDP_drawTextFill(line, 1, 0, 38);

    sprintf(line, "LIFE:%u  PULSE:%03u  PURSUER:%03u", rules->integrity, rules->energy, rules->pressure);
    VDP_drawTextFill(line, 1, 1, 38);

    if (sCinematic) {
        VDP_drawTextFill("        FINAL CONVERGENCE", 1, 2, 38);
        VDP_drawTextFill("     B: CELESTIAL PULSE", 1, 3, 38);
    } else if (rules->mode == CHASE_MODE_ENDLESS) {
        highscore = SAVE_DATA_highscore();
        sprintf(line, "SCORE:%lu", rules->score);
        VDP_drawTextFill(line, 1, 2, 38);
        sprintf(line, "HI:%lu", highscore);
        VDP_drawTextFill(line, 1, 3, 38);
    } else {
        VDP_drawTextFill(" ", 1, 2, 38);
        VDP_drawTextFill(" ", 1, 3, 38);
    }
    sHudDirty = FALSE;
}

void CHASE_HUD_setCinematic(bool active)
{
    if (sCinematic == active || sResultVisible) {
        return;
    }

    sCinematic = active;
    VDP_setWindowOnTop(active ? 4 : 2);
    if (!active) {
        VDP_clearTileMapRect(WINDOW, 0, 2, 64, 2);
    }
    sHudDirty = TRUE;
}

void CHASE_HUD_showPause(bool paused)
{
    sHudDirty = TRUE;
    if (paused) {
        VDP_drawTextFill("PAUSED - START TO RESUME", 8, 1, 28);
    }
}

void CHASE_HUD_showResult(const ChaseRulesState* rules, u32 score, u32 highscore, bool newRecord)
{
    char line[40];

    VDP_setWindowFullScreen();
    VDP_setTextPlane(WINDOW);
    VDP_setTextPalette(PAL2);
    VDP_clearTileMapRect(WINDOW, 0, 0, 64, 32);

    if (rules->flow == CHASE_FLOW_VICTORY) {
        VDP_drawText("THE CELESTIAL GATE OPENS", 8, 9);
        VDP_drawText("YOU OUTRAN THE ANCIENT HART", 5, 12);
    } else {
        VDP_drawText("THE PURSUER CLOSES THE GAP", 6, 9);
        VDP_drawText("THE ROAD REMEMBERS YOUR FALL", 5, 12);
    }

    sprintf(line, "SCORE:%lu  HIGH:%lu", score, highscore);
    VDP_drawText(line, 6, 15);
    sprintf(line, "INTEGRITY:%u  PULSES:%u", rules->integrity, rules->pulsesUsed);
    VDP_drawText(line, 9, 16);
    if (newRecord) {
        VDP_drawText("NEW RECORD", 13, 17);
    }
    VDP_drawText("A/START: RUN AGAIN", 10, 19);
    VDP_drawText("B/MODE: RETURN TO MENU", 8, 22);
    sResultVisible = TRUE;
}

void CHASE_HUD_exit(void)
{
    VDP_setTextPlane(WINDOW);
    VDP_clearTileMapRect(WINDOW, 0, 0, 64, 32);
    VDP_setWindowOff();
    VDP_loadFont(&font_default, CPU);
    VDP_setTextPlane(BG_A);
    sHudDirty = TRUE;
    sResultVisible = FALSE;
    sCinematic = FALSE;
}

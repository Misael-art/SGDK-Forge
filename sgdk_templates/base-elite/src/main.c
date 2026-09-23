#include <genesis.h>

#include "game_vars.h"

/**
 * ELITE GOLDEN TEMPLATE - Main State Machine
 * Objective: High-performance 60FPS execution with modular room management.
 */

int main(bool hardReset)
{
    // 1. Initial VDP Configuration for Visual Excellence
    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    SPR_init();

    // 2. Global System State
    gRoom = TELA_DEMO_INTRO;
    gFrames = 0;

    while (TRUE)
    {
        // High-Level Room Switcher
        switch(gRoom)
        {
            case TELA_DEMO_INTRO:
                // processIntro();
                break;
            
            case GAMEPLAY:
                // processGameplay();
                break;
        }

        // VDP Updates & Synchronization
        gFrames++;
        SPR_update();
        SYS_doVBlankProcess();
    }

    return 0;
}

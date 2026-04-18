#include "project.h"

#include <string.h>

static void Game_applyRequestedState(GameContext *game)
{
    if (!game->stateChangePending)
    {
        return;
    }

    States_exit(game, game->currentState);
    game->previousState = game->currentState;
    game->currentState = game->requestedState;
    game->stateChangePending = false;
    game->stateTimer = 0;
    game->sceneTimer = 0;
    game->redrawScene = true;
    States_enter(game, game->currentState);
}

static void Game_vblank(void)
{
    HintFx_onVBlank();
}

void Game_requestState(GameContext *game, GameStateId nextState)
{
    game->requestedState = nextState;
    game->stateChangePending = true;
}

void Game_init(GameContext *game, bool hardReset)
{
    (void) hardReset;

    memset(game, 0, sizeof(*game));

    game->currentState = GAME_STATE_BOOT;
    game->requestedState = GAME_STATE_BOOT;
    game->currentPlanet = PLANET_B612;
    game->codexIndex = PLANET_B612;

    JOY_init();
    VDP_setScreenWidth320();
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_COLUMN);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL2);
    VDP_setTextPriority(TRUE);
    VDP_setHilightShadow(FALSE);

    Render_init();
    HintFx_init();
    Dialogue_init();
    Audio_init();

    SYS_disableInts();
    SYS_setVBlankCallback(Game_vblank);
    SYS_enableInts();

    Game_requestState(game, GAME_STATE_BOOT);
    Game_applyRequestedState(game);
}

void Game_update(GameContext *game)
{
    game->joy = JOY_readJoypad(JOY_1);
    game->joyPressed = game->joy & (~game->joyPrev);
    game->joyReleased = (~game->joy) & game->joyPrev;
    game->joyPrev = game->joy;

    Game_applyRequestedState(game);
    States_update(game);
    Game_applyRequestedState(game);

    game->stateTimer++;
    game->frameCounter++;
}

void Game_draw(GameContext *game)
{
    SYS_disableInts();
    States_draw(game);
    Render_applyScroll(game);

    if (game->currentState == GAME_STATE_PLANET)
    {
        Player_render(game);
    }
    else
    {
        Player_hideSprites();
    }

    SYS_enableInts();
}

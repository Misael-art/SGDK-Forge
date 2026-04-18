#include "project.h"

#include <string.h>

static const char *const gStoryPage0[] =
{
    "Ele cuidava de um pequeno planeta.",
    "Cada detalhe importava: a rosa, o vento,",
    "a luz do por do sol e o silencio das",
    "estrelas.",
    "",
    "Neste slice, cada mundo ensina uma",
    "tecnica do Mega Drive sem perder a alma."
};

static const char *const gStoryPage1[] =
{
    "B-612 ensina curva, cor e halo.",
    "O Rei amplia profundidade e coluna.",
    "O lampiao divide o frame com H-Int.",
    "O deserto fecha a rota com vento e miragem.",
    "",
    "A ou START avanca o livro.",
    "C sera a tecla de viagem no campo."
};

static const char *const gBootLines[] =
{
    "Slice autoral e pedagogico para SGDK 211",
    "feito para hardware real, 60 fps e estudo",
    "de scroll, H-Int, hilight e narrativa."
};

static PlanetId States_getNextPlanet(PlanetId currentPlanet)
{
    switch (currentPlanet)
    {
        case PLANET_B612: return PLANET_KING;
        case PLANET_KING: return PLANET_VAIDOSO;
        case PLANET_VAIDOSO: return PLANET_BEBADO;
        case PLANET_BEBADO: return PLANET_HOMEM_NEG;
        case PLANET_HOMEM_NEG: return PLANET_ACENDEDOR;
        case PLANET_ACENDEDOR: return PLANET_GEOGRAFO;
        case PLANET_GEOGRAFO: return PLANET_SERPENTE;
        case PLANET_SERPENTE: return PLANET_DESERTO;
        case PLANET_DESERTO: return PLANET_JARDIM;
        case PLANET_JARDIM: return PLANET_POCO;
        case PLANET_POCO: return PLANET_B612_RETORNO;
        case PLANET_B612_RETORNO: return PLANET_COUNT;
        default: return PLANET_COUNT;
    }
}

void States_exit(GameContext *game, GameStateId state)
{
    if ((state == GAME_STATE_PLANET) && (game->activeScene != NULL) && (game->activeScene->exit != NULL))
    {
        game->activeScene->exit(game);
    }
}

void States_enter(GameContext *game, GameStateId nextState)
{
    Render_clearScroll(game);
    Dialogue_close(game);

    switch (nextState)
    {
        case GAME_STATE_BOOT:
        case GAME_STATE_TITLE:
        case GAME_STATE_STORY:
        case GAME_STATE_TRAVEL:
        case GAME_STATE_PAUSE:
        case GAME_STATE_CODEX:
        case GAME_STATE_CREDITS:
            Render_clearPlayfield();
            HintFx_disable();
            VDP_setHilightShadow(FALSE);
            break;

        case GAME_STATE_PLANET:
            game->activeScene = Planet_getScene(game->currentPlanet);
            if (game->activeScene != NULL)
            {
                game->codexUnlocked[game->currentPlanet] = true;
                game->activeScene->enter(game);
            }
            break;
    }

    if (nextState == GAME_STATE_STORY)
    {
        game->storyPage = 0;
    }
    else if (nextState == GAME_STATE_TRAVEL)
    {
        game->nextPlanet = States_getNextPlanet(game->currentPlanet);
        game->currentTravel = Travel_getFromPlanets(game->currentPlanet, game->nextPlanet);
        game->travelFrame = 0;
        game->travelPrevRadius = 8;
        game->travelNextRadius = 0;
    }
    else if (nextState == GAME_STATE_PAUSE)
    {
        game->pauseSelection = 0;
    }
    else if (nextState == GAME_STATE_CODEX)
    {
        game->codexIndex = game->currentPlanet;
    }
}

static void States_updateBoot(GameContext *game)
{
    if (game->stateTimer > 64)
    {
        Game_requestState(game, GAME_STATE_TITLE);
    }
}

static void States_updateTitle(GameContext *game)
{
    if (game->joyPressed & (BUTTON_A | BUTTON_B | BUTTON_C | BUTTON_START))
    {
        Game_requestState(game, GAME_STATE_STORY);
    }
}

static void States_updateStory(GameContext *game)
{
    if (game->joyPressed & (BUTTON_A | BUTTON_B | BUTTON_C | BUTTON_START))
    {
        if (game->storyPage == 0)
        {
            game->storyPage = 1;
            game->redrawScene = true;
        }
        else
        {
            game->currentPlanet = PLANET_B612;
            Game_requestState(game, GAME_STATE_PLANET);
        }
    }
}

static void States_updatePlanet(GameContext *game)
{
    if (game->dialogueActive)
    {
        Dialogue_handleInput(game, game->joyPressed);

        if ((game->activeScene != NULL) && (game->activeScene->update != NULL))
        {
            game->activeScene->update(game);
        }

        return;
    }

    if (game->joyPressed & BUTTON_START)
    {
        Game_requestState(game, GAME_STATE_PAUSE);
        return;
    }

    if (game->activeScene == NULL)
    {
        return;
    }

    if (game->activeScene->handleInput != NULL)
    {
        game->activeScene->handleInput(game, game->joyPressed, game->joy);
    }

    Player_update(game, game->joy);

    if (game->activeScene->update != NULL)
    {
        game->activeScene->update(game);
    }
}

static void States_updateTravel(GameContext *game)
{
    if (game->joyPressed & BUTTON_START)
    {
        Game_requestState(game, GAME_STATE_PAUSE);
        return;
    }

    Travel_update(game);
}

static void States_updatePause(GameContext *game)
{
    if (game->joyPressed & (BUTTON_UP | BUTTON_LEFT))
    {
        if (game->pauseSelection > 0)
        {
            game->pauseSelection--;
        }
        game->redrawScene = true;
    }

    if (game->joyPressed & (BUTTON_DOWN | BUTTON_RIGHT))
    {
        if (game->pauseSelection < 2)
        {
            game->pauseSelection++;
        }
        game->redrawScene = true;
    }

    if (game->joyPressed & BUTTON_B)
    {
        Game_requestState(game, GAME_STATE_PLANET);
        return;
    }

    if (game->joyPressed & (BUTTON_A | BUTTON_C | BUTTON_START))
    {
        switch (game->pauseSelection)
        {
            case 0:
                Game_requestState(game, GAME_STATE_PLANET);
                break;
            case 1:
                Game_requestState(game, GAME_STATE_CODEX);
                break;
            default:
                game->currentPlanet = PLANET_B612;
                Game_requestState(game, GAME_STATE_TITLE);
                break;
        }
    }
}

static void States_updateCodex(GameContext *game)
{
    if (game->joyPressed & BUTTON_LEFT)
    {
        PlanetId idx = game->codexIndex;
        while (idx > 0)
        {
            idx--;
            if (game->codexUnlocked[idx])
            {
                game->codexIndex = idx;
                break;
            }
        }
        game->redrawScene = true;
    }

    if (game->joyPressed & BUTTON_RIGHT)
    {
        PlanetId idx = game->codexIndex;
        while (idx + 1 < PLANET_COUNT)
        {
            idx++;
            if (game->codexUnlocked[idx])
            {
                game->codexIndex = idx;
                break;
            }
        }
        game->redrawScene = true;
    }

    if (game->joyPressed & (BUTTON_B | BUTTON_START))
    {
        Game_requestState(game, GAME_STATE_PAUSE);
    }
}

static void States_updateCredits(GameContext *game)
{
    if (game->joyPressed & (BUTTON_A | BUTTON_B | BUTTON_C | BUTTON_START))
    {
        game->currentPlanet = PLANET_B612;
        memset(game->planetSolved, 0, sizeof(game->planetSolved));
        memset(game->codexUnlocked, 0, sizeof(game->codexUnlocked));
        Game_requestState(game, GAME_STATE_TITLE);
    }
}

void States_update(GameContext *game)
{
    switch (game->currentState)
    {
        case GAME_STATE_BOOT: States_updateBoot(game); break;
        case GAME_STATE_TITLE: States_updateTitle(game); break;
        case GAME_STATE_STORY: States_updateStory(game); break;
        case GAME_STATE_PLANET: States_updatePlanet(game); break;
        case GAME_STATE_TRAVEL: States_updateTravel(game); break;
        case GAME_STATE_PAUSE: States_updatePause(game); break;
        case GAME_STATE_CODEX: States_updateCodex(game); break;
        case GAME_STATE_CREDITS: States_updateCredits(game); break;
    }
}

void States_draw(GameContext *game)
{
    switch (game->currentState)
    {
        case GAME_STATE_BOOT:
            if (game->redrawScene)
            {
                Render_drawTextScreen(PAL2, "Fundacao do Slice", gBootLines, 3, 10);
                game->redrawScene = false;
            }
            break;

        case GAME_STATE_TITLE:
            Render_drawTitleScene(game);
            game->redrawScene = false;
            break;

        case GAME_STATE_STORY:
            Render_drawStoryScene(game,
                (game->storyPage == 0) ? "Cronicas das Estrelas" : "Mapa do Capitulo",
                (game->storyPage == 0) ? gStoryPage0 : gStoryPage1,
                7);
            game->redrawScene = false;
            break;

        case GAME_STATE_PLANET:
            if ((game->activeScene != NULL) && (game->activeScene->draw != NULL))
            {
                game->activeScene->draw(game);
            }
            Render_drawPlanetHud(game);
            Dialogue_draw(game);
            break;

        case GAME_STATE_TRAVEL:
            Render_drawTravelScene(game);
            game->redrawScene = false;
            break;

        case GAME_STATE_PAUSE:
            Render_drawPauseScreen(game);
            game->redrawScene = false;
            break;

        case GAME_STATE_CODEX:
            Render_drawCodexScreen(game);
            game->redrawScene = false;
            break;

        case GAME_STATE_CREDITS:
            Render_drawCreditsScreen(game);
            game->redrawScene = false;
            break;
    }
}

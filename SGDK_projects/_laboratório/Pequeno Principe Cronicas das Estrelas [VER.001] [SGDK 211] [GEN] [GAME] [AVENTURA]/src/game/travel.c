#include "project.h"

TravelId Travel_getFromPlanets(PlanetId from, PlanetId to)
{
    if (from == PLANET_B612 && to == PLANET_KING) return TRAVEL_A;
    if (from == PLANET_KING && to == PLANET_VAIDOSO) return TRAVEL_B;
    if (from == PLANET_VAIDOSO && to == PLANET_BEBADO) return TRAVEL_C;
    if (from == PLANET_BEBADO && to == PLANET_HOMEM_NEG) return TRAVEL_D;
    if (from == PLANET_HOMEM_NEG && to == PLANET_ACENDEDOR) return TRAVEL_E;
    if (from == PLANET_ACENDEDOR && to == PLANET_GEOGRAFO) return TRAVEL_F;
    if (from == PLANET_GEOGRAFO && to == PLANET_SERPENTE) return TRAVEL_G;
    if (from == PLANET_SERPENTE && to == PLANET_DESERTO) return TRAVEL_H;
    if (from == PLANET_DESERTO && to == PLANET_JARDIM) return TRAVEL_I;
    if (from == PLANET_JARDIM && to == PLANET_POCO) return TRAVEL_J;
    if (from == PLANET_POCO && to == PLANET_B612_RETORNO) return TRAVEL_K;
    return TRAVEL_COUNT;
}

void Travel_update(GameContext *game)
{
    game->travelFrame++;

    if ((game->travelFrame & 3) == 0)
    {
        if (game->travelPrevRadius > 0)
        {
            game->travelPrevRadius--;
        }
        if (game->travelNextRadius < 8)
        {
            game->travelNextRadius++;
        }
        game->redrawScene = true;
    }

    if ((game->travelFrame > 96) || (game->joyPressed & (BUTTON_A | BUTTON_C)))
    {
        if (game->nextPlanet == PLANET_COUNT)
        {
            Game_requestState(game, GAME_STATE_CREDITS);
        }
        else
        {
            game->currentPlanet = game->nextPlanet;
            Game_requestState(game, GAME_STATE_PLANET);
        }
    }
}

void Travel_draw(const GameContext *game)
{
    (void) game;
}

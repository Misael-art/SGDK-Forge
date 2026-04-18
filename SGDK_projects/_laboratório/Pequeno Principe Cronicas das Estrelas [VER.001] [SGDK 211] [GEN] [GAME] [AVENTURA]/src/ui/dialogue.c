#include "project.h"

static void Dialogue_redrawWindow(GameContext *game)
{
    u16 i;

    VDP_setWindowOnBottom(8);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_fillTileMapRect(WINDOW, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, PP_TILE_DITHER), 0, 0, PP_SCREEN_TILES_W, 8);
    VDP_fillTileMapRect(WINDOW, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, PP_TILE_PAPER), 1, 1, PP_SCREEN_TILES_W - 2, 6);
    VDP_fillTileMapRect(WINDOW, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, PP_TILE_HATCH), 0, 0, PP_SCREEN_TILES_W, 1);
    VDP_fillTileMapRect(WINDOW, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, PP_TILE_HATCH), 0, 7, PP_SCREEN_TILES_W, 1);
    VDP_fillTileMapRect(WINDOW, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, PP_TILE_FILL), 1, 1, PP_SCREEN_TILES_W - 2, 1);

    VDP_setTextPlane(WINDOW);
    VDP_drawText(game->dialogueSpeaker, 2, 1);

    for (i = 0; (i < game->dialogueLineCount) && (i < 4); i++)
    {
        VDP_drawText(game->dialogueLines[i], 2, 2 + i);
    }

    VDP_drawText("A/B/C/START fecha", 20, 6);
    VDP_setTextPlane(BG_A);
    game->dialogueDirty = false;
}

void Dialogue_init(void)
{
    VDP_setWindowOff();
    VDP_clearPlane(WINDOW, TRUE);
}

void Dialogue_open(GameContext *game, const char *speaker, const char *const *lines, u16 lineCount)
{
    game->dialogueActive = true;
    game->dialogueDirty = true;
    game->dialogueSpeaker = speaker;
    game->dialogueLines = lines;
    game->dialogueLineCount = lineCount;
}

void Dialogue_close(GameContext *game)
{
    game->dialogueActive = false;
    game->dialogueDirty = false;
    game->dialogueSpeaker = 0;
    game->dialogueLines = 0;
    game->dialogueLineCount = 0;
    VDP_setTextPlane(BG_A);
    VDP_setWindowOff();
    VDP_clearPlane(WINDOW, TRUE);
}

void Dialogue_handleInput(GameContext *game, u16 pressed)
{
    if (pressed & (BUTTON_A | BUTTON_B | BUTTON_C | BUTTON_START))
    {
        Dialogue_close(game);
    }
}

void Dialogue_draw(GameContext *game)
{
    if (!game->dialogueActive)
    {
        return;
    }

    if (game->dialogueDirty)
    {
        Dialogue_redrawWindow(game);
    }
    else
    {
        VDP_setWindowOnBottom(8);
    }
}

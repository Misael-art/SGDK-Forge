#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "minigames/mg_common.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MINIGAME 2: CHUVA DE ESTRELAS.
 * Pegue 10 estrelas antes de deixar 5 cairem. Esquerda/direita movem Kirby.
 * Grid de texto: campo x=4..35, y=8..23, chao em y=24.
 */

#define SF_MAX_STARS 6u
#define SF_GROUND_Y 24
#define SF_FIELD_X0 4
#define SF_FIELD_X1 35
#define SF_GOAL 10
#define SF_MISSES_ALLOWED 5

typedef struct { s16 x; s16 y; bool alive; } Star;   /* x = coluna, y = linha */

static Star s_stars[SF_MAX_STARS];
static s16 s_playerCol;
static u16 s_catches;
static u16 s_misses;
static u16 s_spawnTimer;

static void drawStarCell(const Star* st, char glyph)
{
    char b[2];

    if ((st->x < SF_FIELD_X0) || (st->x > SF_FIELD_X1)) return;
    if ((st->y < 6) || (st->y > 22)) return;
    b[0] = glyph;
    b[1] = '\0';
    VDP_drawText(b, (u16) st->x, (u16) st->y);
}

static void spawn(void)
{
    u8 i;

    for (i = 0u; i < SF_MAX_STARS; i++)
    {
        if (!s_stars[i].alive)
        {
            s_stars[i].alive = TRUE;
            s_stars[i].y = 8;
            s_stars[i].x = (s16) (SF_FIELD_X0 + (JOURNEY_rand() % 28u));
            return;
        }
    }
}

void SCENE_mgStarfallEnter(void)
{
    u8 i;

    MG_begin("CHUVA DE ESTRELAS");
    for (i = 0u; i < SF_MAX_STARS; i++) s_stars[i].alive = FALSE;

    s_playerCol = 20;
    s_catches = 0u;
    s_misses = 0u;
    s_spawnTimer = 0u;

    {
        /* Bordas estaticas do campo: objetos vivem em x=4..35, nunca as apagam. */
        u8 r;

        for (r = 8u; r <= SF_GROUND_Y; r++)
        {
            VDP_drawText("|", 3, r);
            VDP_drawText("|", SF_FIELD_X1 + 1, r);
        }
    }
    VDP_drawText("======================================", 4, SF_GROUND_Y);
    VDP_drawText("K", 20, SF_GROUND_Y - 1);
    VDP_drawText("PEGUE 10 - DEIXE CAIR 5 E PERDEU", 4, 5);
}

void SCENE_mgStarfallUpdate(void)
{
    char line[32];
    u8 i;

    MG_tickCommon();
    if (MG_shouldReturn()) return;
    if (MG_resultActive()) return;

    /* Player */
    VDP_drawText(" ", (u16) s_playerCol, SF_GROUND_Y - 1);
    if (INPUT_pressed(BUTTON_LEFT) && (s_playerCol > SF_FIELD_X0)) s_playerCol--;
    else if (INPUT_pressed(BUTTON_RIGHT) && (s_playerCol < SF_FIELD_X1)) s_playerCol++;
    VDP_drawText("K", (u16) s_playerCol, SF_GROUND_Y - 1);

    /* Spawn */
    s_spawnTimer++;
    if (s_spawnTimer >= 14u)
    {
        s_spawnTimer = 0u;
        spawn();
    }

    /* Queda: 1 linha a cada 2 frames */
    if ((MG_frames() & 1u) == 0u)
    {
        for (i = 0u; i < SF_MAX_STARS; i++)
        {
            Star* st = &s_stars[i];

            if (!st->alive) continue;

            drawStarCell(st, ' ');
            st->y++;

            if (st->y >= (SF_GROUND_Y - 1))
            {
                st->alive = FALSE;
                if (st->x == s_playerCol)
                {
                    s_catches++;
                    AUDIO_playUiTone(784u, 6u);
                }
                else
                {
                    s_misses++;
                    AUDIO_playUiTone(147u, 8u);
                }
            }
            else
            {
                drawStarCell(st, '*');
            }
        }

        strclr(line);
        strcat(line, "PEGAS:");
        intToStr((s32) s_catches, line + 6, 2);
        strcat(line, " PERDIDAS:");
        intToStr((s32) s_misses, line + 17, 2);
        VDP_drawText(line, 9, HUD_ROW_HINT_SECONDARY);
    }

    if (s_catches >= SF_GOAL)
    {
        MG_finish(TRUE, (s16) (s_catches + (SF_MISSES_ALLOWED * 2) - s_misses),
                  "COLECIONADOR DE ESTRELAS");
    }
    else if (s_misses >= SF_MISSES_ALLOWED)
    {
        MG_finish(FALSE, (s16) s_catches, "MUITAS ESTRELAS NO CHAO");
    }
}

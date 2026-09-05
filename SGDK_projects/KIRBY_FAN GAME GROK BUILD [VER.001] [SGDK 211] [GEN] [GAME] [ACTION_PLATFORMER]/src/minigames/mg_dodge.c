#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "minigames/mg_common.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MINIGAME 4: DESVIA OVOS.
 * Chuva de ovos do rei: sobreviva 30 segundos sem levar 3 acertos.
 * Mesma engine de grid da CHUVA DE ESTRELAS, objetivo invertido.
 */

#define DG_MAX_EGGS 7u
#define DG_GROUND_Y 24
#define DG_FIELD_X0 4
#define DG_FIELD_X1 35
#define DG_DURATION (30u * 60u)
#define DG_HITS_ALLOWED 3u

typedef struct { s16 x; s16 y; bool alive; u8 fallMask; } Egg;

static Egg s_eggs[DG_MAX_EGGS];
static s16 s_playerCol;
static u16 s_hits;

static void drawEgg(const Egg* e, char glyph)
{
    char b[2];

    if ((e->x < DG_FIELD_X0) || (e->x > DG_FIELD_X1)) return;
    if ((e->y < 6) || (e->y > 22)) return;
    b[0] = glyph;
    b[1] = '\0';
    VDP_drawText(b, (u16) e->x, (u16) e->y);
}

static void spawn(void)
{
    u8 i;

    for (i = 0u; i < DG_MAX_EGGS; i++)
    {
        if (!s_eggs[i].alive)
        {
            s_eggs[i].alive = TRUE;
            s_eggs[i].y = 6;
            s_eggs[i].x = (s16) (DG_FIELD_X0 + (JOURNEY_rand() % 28u));
            s_eggs[i].fallMask = (u8) (1u + (JOURNEY_rand() % 2u));
            return;
        }
    }
}

void SCENE_mgDodgeEnter(void)
{
    u8 i;

    MG_begin("DESVIA OVOS");
    for (i = 0u; i < DG_MAX_EGGS; i++) s_eggs[i].alive = FALSE;

    s_playerCol = 20;
    s_hits = 0u;

    {
        u8 r;

        for (r = 8u; r <= DG_GROUND_Y; r++)
        {
            VDP_drawText("|", 3, r);
            VDP_drawText("|", DG_FIELD_X1 + 1, r);
        }
    }
    VDP_drawText("======================================", 4, DG_GROUND_Y);
    VDP_drawText("K", 20, DG_GROUND_Y - 1);
    VDP_drawText("SOBREVIVA 30s - 3 ACERTOS E FIM", 5, 5);
}

void SCENE_mgDodgeUpdate(void)
{
    char line[32];
    const u16 secs = MG_frames() / 60u;
    u8 i;

    MG_tickCommon();
    if (MG_shouldReturn()) return;
    if (MG_resultActive()) return;

    if ((MG_frames() % 20u) == 0u) spawn();

    /* Player */
    VDP_drawText(" ", (u16) s_playerCol, DG_GROUND_Y - 1);
    if (INPUT_pressed(BUTTON_LEFT) && (s_playerCol > DG_FIELD_X0)) s_playerCol--;
    else if (INPUT_pressed(BUTTON_RIGHT) && (s_playerCol < DG_FIELD_X1)) s_playerCol++;
    VDP_drawText("K", (u16) s_playerCol, DG_GROUND_Y - 1);

    for (i = 0u; i < DG_MAX_EGGS; i++)
    {
        Egg* e = &s_eggs[i];

        if (!e->alive) continue;
        if ((MG_frames() & e->fallMask) != 0u) continue;

        drawEgg(e, ' ');
        e->y++;

        if (e->y >= (DG_GROUND_Y - 1))
        {
            e->alive = FALSE;
            if (e->x == s_playerCol)
            {
                s_hits++;
                AUDIO_playUiTone(147u, 12u);
            }
            else
            {
                AUDIO_playUiTone(330u, 3u);
            }
        }
        else
        {
            drawEgg(e, 'o');
        }
    }

    strclr(line);
    strcat(line, "TEMPO: ");
    intToStr((s32) (DG_DURATION / 60u - secs), line + 7, 2);
    strcat(line, "s ACERTOS: ");
    intToStr((s32) s_hits, line + strlen(line), 2);
    VDP_drawText(line, 9, HUD_ROW_HINT_SECONDARY);

    if (s_hits >= DG_HITS_ALLOWED)
    {
        MG_finish(FALSE, (s16) secs, "BANANA SPLIT...");
    }
    else if (MG_frames() >= DG_DURATION)
    {
        MG_finish(TRUE, (s16) (100 + secs), "INTOCAVEL!");
    }
}

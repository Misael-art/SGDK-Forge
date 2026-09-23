#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "minigames/mg_common.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MINIGAME 7: BATERIA PSG.
 * Notas (setas do D-pad) descem a pista em direcao ao marcador; aperte a
 * direcao certa quando a nota cruzar a zona. 20 notas; 15 acertos vence.
 * Cada acerto toca sua nota - o PSG e a bateria da partida.
 */

#define RH_NOTE_COUNT 20u
#define RH_MARKER_X 6
#define RH_SPAWN_X 34
#define RH_LANE_Y 14
#define RH_WIN_HITS 15

typedef struct { u8 dir; s16 x; bool alive; } Note;

static Note s_notes[RH_NOTE_COUNT];
static u16 s_spawned;
static u16 s_hits;
static u16 s_misses;
static char s_laneGlyphs[40];

static const char RH_GLYPH[4] = { '^', '<', '>', 'v' };
static const u16 RH_TONE[4] = { 523u, 392u, 659u, 330u };

static void laneDraw(s16 x, char glyph)
{
    if ((x < 2) || (x > 37)) return;
    VDP_drawText((char[]) { glyph, '\0' }, (u16) x, RH_LANE_Y);
}

void SCENE_mgRhythmEnter(void)
{
    u8 i;

    MG_begin("BATERIA PSG");
    for (i = 0u; i < RH_NOTE_COUNT; i++) s_notes[i].alive = FALSE;

    MG_drawBackdrop(FALSE);

    /* Pista */
    strcpy(s_laneGlyphs, "------------------------------------");
    VDP_drawText(s_laneGlyphs, 2, RH_LANE_Y);
    VDP_drawText("||", RH_MARKER_X, RH_LANE_Y);
    VDP_drawText("APERTE A DIRECAO QUANDO CRUZAR ||", 4, RH_LANE_Y + 2);

    s_spawned = 0u;
    s_hits = 0u;
    s_misses = 0u;
}

void SCENE_mgRhythmUpdate(void)
{
    char line[32];
    u8 i;

    MG_tickCommon();
    if (MG_shouldReturn()) return;
    if (MG_resultActive()) return;

    /* Spawn: uma nota nova a cada 24 frames, ate esgotar. */
    if (((MG_frames() % 24u) == 0u) && (s_spawned < RH_NOTE_COUNT))
    {
        for (i = 0u; i < RH_NOTE_COUNT; i++)
        {
            if (!s_notes[i].alive)
            {
                s_notes[i].alive = TRUE;
                s_notes[i].x = RH_SPAWN_X;
                s_notes[i].dir = (u8) (JOURNEY_rand() & 3u);
                s_spawned++;
                break;
            }
        }
    }

    /* Movimento: 1 coluna a cada 4 frames. */
    if ((MG_frames() & 3u) == 0u)
    {
        for (i = 0u; i < RH_NOTE_COUNT; i++)
        {
            Note* n = &s_notes[i];

            if (!n->alive) continue;

            laneDraw(n->x, '-');
            n->x--;

            if (n->x < (RH_MARKER_X - 1))
            {
                n->alive = FALSE;
                s_misses++;
                AUDIO_playUiTone(110u, 6u);
                continue;
            }
            laneDraw(n->x, RH_GLYPH[n->dir]);
        }
    }

    /* Input: qualquer nota na zona aceita o pad correto. */
    {
        const u16 pads[4] = { BUTTON_UP, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_DOWN };

        for (i = 0u; i < 4u; i++)
        {
            if (!INPUT_pressed(pads[i])) continue;

            {
                bool consumed = FALSE;
                u8 j;

                for (j = 0u; j < RH_NOTE_COUNT; j++)
                {
                    Note* n = &s_notes[j];
                    const s16 d = (s16) (n->x - RH_MARKER_X);

                    if (!n->alive || (d < -1) || (d > 1)) continue;

                    consumed = TRUE;
                    if ((s8) i == (s8) n->dir)
                    {
                        s_hits++;
                        AUDIO_playUiTone(RH_TONE[n->dir], 8u);
                    }
                    else
                    {
                        s_misses++;
                        AUDIO_playUiTone(147u, 10u);
                    }
                    laneDraw(n->x, '-');
                    n->alive = FALSE;
                    break;
                }
                if (!consumed)
                {
                    /* Pad solto fora de tempo: sem punicao, so silencio. */
                }
            }
        }
    }

    strclr(line);
    strcat(line, "NOTAS:");
    intToStr((s32) (s_hits + s_misses), line + 6, 2);
    strcat(line, "/20 ACERTOS:");
    intToStr((s32) s_hits, line + strlen(line), 2);
    VDP_drawText(line, 9, HUD_ROW_HINT_SECONDARY);

    if ((s_hits + s_misses) >= RH_NOTE_COUNT)
    {
        MG_finish(s_hits >= RH_WIN_HITS, (s16) s_hits, "PERFORMANCE FINAL");
    }
}

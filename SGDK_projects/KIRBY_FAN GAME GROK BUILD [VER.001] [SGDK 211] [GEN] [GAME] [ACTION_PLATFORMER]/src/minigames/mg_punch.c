#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "minigames/mg_common.h"
#include "system/input.h"
#include "resources.h"
#include "systems/journey.h"

/*
 * MINIGAME 3: SOCO MEGATON.
 * O cursor oscila na barra; acerte A na zona central. 3 socos; a forca de cada
 * um e a distancia ao centro. Total >= 33 quebra o bloco.
 */

#define PUNCH_BAR_X0 4
#define PUNCH_BAR_X1 35
#define PUNCH_CENTER 19
#define PUNCH_TARGET 33

static s16 s_cursor;
static s8  s_dir;
static u16 s_speed;
static u8  s_round;
static s16 s_total;
static Sprite* s_sprKirby;

static void drawBar(void)
{
    char bar[40];
    u8 i;

    for (i = 0u; i < 32u; i++) bar[i] = (char) ((i >= 13u && i <= 18u) ? '#' : '=');
    bar[32] = '\0';
    VDP_drawText(bar, PUNCH_BAR_X0, 10);
}

static void drawCursor(char glyph)
{
    char b[2];

    b[0] = glyph;
    b[1] = '\0';
    VDP_drawText(b, (u16) s_cursor, 12);
}

void SCENE_mgPunchEnter(void)
{
    MG_begin("SOCO MEGATON");
    VDP_drawText("ACERTE A NO CENTRO (#) - 3 SOCOS", 4, 6);
    VDP_drawText("TOTAL NECESSARIO: 33", 10, 7);
    drawBar();
    drawCursor(' ');

    MG_drawBackdrop(TRUE);
    PAL_setPalette(PAL2, spr_pal2_master.palette->data, DMA);
    s_sprKirby = SPR_addSprite(&spr_ph_kirby, 44, 128,
                               TILE_ATTR(PAL2, TRUE, FALSE, FALSE));

    s_cursor = PUNCH_BAR_X0;
    s_dir = 1;
    s_speed = 1u;
    s_round = 0u;
    s_total = 0;
}

void SCENE_mgPunchUpdate(void)
{
    char line[32];
    s16 dist;

    MG_tickCommon();
    if (MG_shouldReturn()) return;
    if (MG_resultActive()) return;

    /* Oscilacao: velocidade sobe a cada round (1,2,3 px por frame). */
    {
        u8 k;

        drawCursor(' ');
        for (k = 0u; k < s_speed; k++)
        {
            s_cursor += s_dir;
            if (s_cursor >= PUNCH_BAR_X1) { s_cursor = PUNCH_BAR_X1; s_dir = -1; }
            if (s_cursor <= PUNCH_BAR_X0) { s_cursor = PUNCH_BAR_X0; s_dir = 1; }
        }
        drawCursor('<');
    }

    if (INPUT_pressed(BUTTON_A))
    {
        dist = PUNCH_CENTER - s_cursor;
        if (dist < 0) dist = (s16) (-dist);
        dist = (s16) (15 - dist);
        if (dist < 0) dist = 0;

        s_total += dist;

        strclr(line);
        strcat(line, "SOCO ");
        intToStr((s32) (s_round + 1u), line + strlen(line), 1);
        strcat(line, ": FORCA ");
        intToStr((s32) dist, line + strlen(line), 2);

        AUDIO_playUiTone((u16) (196 + (dist * 30)), 14u);

        s_round++;
        s_speed++;
        if (s_round >= 3u)
        {
            MG_finish(s_total >= PUNCH_TARGET, s_total,
                      (s_total >= PUNCH_TARGET) ? "BLOCO QUEBRADO!" : "BLOCO AGUENTOU...");
        }
        else
        {
            VDP_drawText(line, 9, 14);
        }
    }
}

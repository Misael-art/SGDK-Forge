#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "minigames/mg_common.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MINIGAME 6: SALTO ESTELAR.
 * Segure A para carregar; solte perto do topo da barra. Melhor de 3 saltos;
 * altura >= 26 e vitoria. A barra oscila - timing, nao forca.
 */

#define HJ_MAX_POWER 32
#define HJ_WIN_HEIGHT 26
#define HJ_GROUND_ROW 22

static s16 s_power;
static s8 s_dir;
static u8 s_jump;
static s16 s_best;

void SCENE_mgHighjumpEnter(void)
{
    MG_begin("SALTO ESTELAR");
    MG_drawBackdrop(TRUE);
    VDP_drawText("SEGURE A PARA CARREGAR E SOLTE!", 4, 6);
    VDP_drawText("META: ALTURA 26 (MELHOR DE 3)", 5, 7);

    s_power = 0;
    s_dir = 2;
    s_jump = 0u;
    s_best = 0;
}

static void drawMeter(s16 value)
{
    char bar[40];
    u8 i;

    for (i = 0u; i < 32u; i++) bar[i] = ' ';
    for (i = 0u; i < 32u; i++)
    {
        if ((s16) i < value) bar[i] = '*';
    }
    if (value >= HJ_WIN_HEIGHT) { bar[HJ_WIN_HEIGHT - 1] = '|'; }
    bar[32] = '\0';
    /* Barra vertical desenhada como coluna de blocos na lateral. */
    VDP_drawText(bar, 6, HJ_GROUND_ROW);
}

static void drawKirbyRise(s16 height)
{
    u8 row;

    /* Apaga a trilha anterior e desenha o Kirby na altura alcancada. */
    for (row = 0u; row < 21u; row++) VDP_drawText(" ", 30, (u16) (HJ_GROUND_ROW - 1u - row));
    if (height > 21) height = 21;
    VDP_drawText("K", 30, (u16) (HJ_GROUND_ROW - 1u - (u16) height));
}

void SCENE_mgHighjumpUpdate(void)
{
    char line[24];
    bool charging = INPUT_held(BUTTON_A);

    MG_tickCommon();
    if (MG_shouldReturn()) return;
    if (MG_resultActive()) return;

    if (!charging && (s_jump == 0u))
    {
        strclr(line);
        strcat(line, "SEGURE A... ");
        VDP_drawText(line, 12, 12);
    }

    if (charging)
    {
        s_power += s_dir;
        if (s_power >= HJ_MAX_POWER) { s_power = HJ_MAX_POWER; s_dir = -2; }
        if (s_power <= 0)            { s_power = 0;             s_dir = 2; }

        drawMeter((s16) (s_power >> 1));
        drawKirbyRise(0);

        if (INPUT_released(BUTTON_A))
        {
            const s16 h = (s16) (s_power >> 1);

            if (h > s_best) s_best = h;
            AUDIO_playUiTone((u16) (220 + (h * 14)), 16u);

            drawKirbyRise(h > 21 ? 21 : h);
            strclr(line);
            strcat(line, "SALTO ");
            intToStr((s32) (s_jump + 1u), line + strlen(line), 1);
            strcat(line, ": ALTURA ");
            intToStr((s32) h, line + strlen(line), 2);
            VDP_drawText(line, 9, 13);

            s_jump++;
            s_power = 0;
            s_dir = 2;

            if (s_jump >= 3u)
            {
                MG_finish(s_best >= HJ_WIN_HEIGHT, s_best, "MAIOR ALTURA");
            }
        }
    }
}

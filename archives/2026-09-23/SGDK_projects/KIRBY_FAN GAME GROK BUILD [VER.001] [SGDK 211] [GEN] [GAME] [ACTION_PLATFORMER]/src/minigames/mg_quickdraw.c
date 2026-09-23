#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "minigames/mg_common.h"
#include "resources.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MINIGAME 1: DUELO RELAMPAGO.
 * Espere o sinal e atire (A). 3 duelos; reacao <= 30 frames vence o duelo.
 * Atirar antes do sinal = derrota imediata do duelo. Melhor reacao e a nota.
 * Kirby encara o inimigo no centro da tela - o duelo tem rosto, nao so texto.
 */

typedef enum { QD_WAIT = 0, QD_SIGNAL, QD_BETWEEN } QdState;

#define QD_ROUNDS 3u
#define QD_WIN_FRAMES 30

static QdState s_state;
static u16 s_delay;
static u16 s_react;
static u8 s_round;
static u8 s_wins;
static s16 s_best;
static Sprite* s_sprKirby;
static Sprite* s_sprFoe;

static void nextRound(void)
{
    s_state = QD_WAIT;
    s_delay = (u16) (90u + (JOURNEY_rand() % 210u));
    s_react = 0u;
}

void SCENE_mgQuickdrawEnter(void)
{
    MG_begin("DUELO RELAMPAGO");
    VDP_drawText("ESPERE O SINAL... E ATIRE!", 6, 6);
    VDP_drawText("(A)", 19, 20);

    MG_drawBackdrop(TRUE);
    PAL_setPalette(PAL2, spr_pal2_master.palette->data, DMA);
    s_sprKirby = SPR_addSprite(&spr_ph_kirby, 60, 140,
                               TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    s_sprFoe = SPR_addSprite(&spr_ph_enemy, 240, 144,
                             TILE_ATTR(PAL2, TRUE, FALSE, FALSE));

    s_round = 0u;
    s_wins = 0u;
    s_best = -1;
    nextRound();
}

static void endDuel(bool won, const char* msg)
{
    if (won) s_wins++;
    if ((s_best < 0) || (s_react < (u16) s_best)) s_best = (s16) s_react;

    VDP_drawText(msg, 11, 12);
    s_round++;
    if (s_round >= QD_ROUNDS)
    {
        MG_finish(s_wins >= 2u, s_best, "MELHOR REACAO EM FRAMES");
    }
    else
    {
        nextRound();
        VDP_drawText("ROUND SEGUINTE...", 9, 14);
    }
}

void SCENE_mgQuickdrawUpdate(void)
{
    char line[32];

    MG_tickCommon();
    if (MG_shouldReturn()) return;
    if (MG_resultActive()) return;

    switch (s_state)
    {
        case QD_WAIT:
            if (INPUT_pressed(BUTTON_A))
            {
                AUDIO_playUiTone(110u, 20u);
                MG_finish(FALSE, 0, "TIRO ANTES DO SINAL!");
                return;
            }
            s_delay--;
            if (s_delay == 0u)
            {
                s_state = QD_SIGNAL;
                AUDIO_playUiTone(880u, 12u);
                VDP_clearTextArea(1, 8, 38, 4);
                VDP_drawText(">> FOGO! <<", 15, 9);
            }
            break;

        case QD_SIGNAL:
            s_react++;
            /* Kirby "saca": anima o pulo de reacao enquanto o sinal queima. */
            SPR_setFrame(s_sprKirby, ((s_react >> 2) & 1u) != 0u ? 5u : 0u);
            if (INPUT_pressed(BUTTON_A))
            {
                bool won = (s_react <= QD_WIN_FRAMES);

                strclr(line);
                strcat(line, won ? "RAPIDO! " : "LENTO... ");
                intToStr((s32) s_react, line + strlen(line), 1);
                strcat(line, " F");
                endDuel(won, line);
                s_state = QD_BETWEEN;
            }
            break;

        default:
            break;
    }
}

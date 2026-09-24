#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "minigames/mg_common.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MINIGAME 5: ECO ESTELAR (memoria).
 * A sequencia de direcoes cresce ate 6; repita com o D-pad. Cada pad tem nota
 * propria no PSG - o pitch e o gameplay, nao enfeite.
 */

#define SIMON_MAX_LEN 6u

static const u16 PAD_TONE[4] = { 523u, 392u, 659u, 330u }; /* U L R D */
typedef enum { SM_SHOW = 0, SM_INPUT } SimonState;

static u8 s_seq[SIMON_MAX_LEN];
static u8 s_len;
static u8 s_showIdx;
static u16 s_timer;
static SimonState s_state;
static u8 s_inputIdx;
static s8 s_flash;      /* pad aceso, -1 nenhum */

static void drawPads(void)
{
    VDP_drawText("[ U ]", 18, 9);
    VDP_drawText("[L]", 15, 12);
    VDP_drawText("[R]", 21, 12);
    VDP_drawText("[ D ]", 17, 15);
    VDP_drawText("OBSERVE A SEQUENCIA", 10, 18);
}

static void flash(u8 pad, bool on)
{
    static const char* const off[4] = { "[ U ]", "[L]", "[R]", "[ D ]" };
    static const char* const onTxt[4] = { "< U >", "{L}", "{R}", "( D )" };

    switch (pad)
    {
        case 0: VDP_drawText(on ? onTxt[0] : off[0], 18, 9); break;
        case 1: VDP_drawText(on ? onTxt[1] : off[1], 15, 12); break;
        case 2: VDP_drawText(on ? onTxt[2] : off[2], 21, 12); break;
        default: VDP_drawText(on ? onTxt[3] : off[3], 17, 15); break;
    }
}

void SCENE_mgSimonEnter(void)
{
    MG_begin("ECO ESTELAR");
    MG_drawBackdrop(TRUE);
    drawPads();

    s_len = 3u;          /* começa em 3, cresce ate 6 */
    s_state = SM_SHOW;
    s_showIdx = 0u;
    s_timer = 30u;
    s_inputIdx = 0u;
    s_flash = -1;

    VDP_drawText("REPITA COM O D-PAD", 11, 20);
}

void SCENE_mgSimonUpdate(void)
{
    char line[24];

    MG_tickCommon();
    if (MG_shouldReturn()) return;
    if (MG_resultActive()) return;

    if (s_state == SM_SHOW)
    {
        s_timer++;
        if (s_timer >= 28u)
        {
            s_timer = 0u;
            if (s_flash >= 0) { flash((u8) s_flash, FALSE); s_flash = -1; }
            else
            {
                if (s_showIdx >= s_len)
                {
                    s_state = SM_INPUT;
                    s_inputIdx = 0u;
                    strclr(line);
                    strcat(line, "SUA VEZ! (");
                    intToStr((s32) s_len, line + strlen(line), 1);
                    strcat(line, ")");
                    VDP_drawText(line, 14, 18);
                    return;
                }
                s_seq[s_showIdx] = (u8) (JOURNEY_rand() & 3u);
                s_flash = s_seq[s_showIdx];
                flash((u8) s_flash, TRUE);
                AUDIO_playUiTone(PAD_TONE[(u8) s_flash], 12u);
                s_showIdx++;
            }
        }
        return;
    }

    /* SM_INPUT */
    {
        s8 pressedPad = -1;

        if (INPUT_pressed(BUTTON_UP))    pressedPad = 0;
        else if (INPUT_pressed(BUTTON_LEFT))  pressedPad = 1;
        else if (INPUT_pressed(BUTTON_RIGHT)) pressedPad = 2;
        else if (INPUT_pressed(BUTTON_DOWN))  pressedPad = 3;

        if (pressedPad >= 0)
        {
            if ((u8) pressedPad != s_seq[s_inputIdx])
            {
                AUDIO_playUiTone(110u, 20u);
                MG_finish(FALSE, (s16) (s_inputIdx), "ECO ERRADO...");
                return;
            }

            AUDIO_playUiTone(PAD_TONE[(u8) pressedPad], 8u);
            s_inputIdx++;

            if (s_inputIdx >= s_len)
            {
                if (s_len >= SIMON_MAX_LEN)
                {
                    MG_finish(TRUE, (s16) s_len, "MEMORIA DE ESTRELA!");
                    return;
                }
                s_len++;
                s_state = SM_SHOW;
                s_showIdx = 0u;
                s_timer = 0u;
                VDP_drawText("OBSERVE A SEQUENCIA", 10, 18);
            }
        }
    }
}

#include <genesis.h>

#include "audio/xgm_router.h"
#include "core/app.h"
#include "game_vars.h"
#include "minigames/mg_common.h"
#include "system/audio.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MISSAO 2026-08-24: HUB dos 7 minigames.
 *
 * Lista estatica, cursor piscante, B volta ao MENU. Os jogos sao sempre
 * liberados (nao dependem da jornada) - decisao de design: minigame e
 * brinquedo, e brinquedo fechado atrasta a descoberta.
 */

#define MG_HUB_COUNT 7u

static const AppScene MG_SCENES[MG_HUB_COUNT] = {
    APP_SCENE_MG_QUICKDRAW,
    APP_SCENE_MG_STARFALL,
    APP_SCENE_MG_PUNCH,
    APP_SCENE_MG_DODGE,
    APP_SCENE_MG_SIMON,
    APP_SCENE_MG_HIGHJUMP,
    APP_SCENE_MG_RHYTHM
};

static const char* const MG_NAMES[MG_HUB_COUNT] = {
    "DUELO RELAMPAGO",
    "CHUVA DE ESTRELAS",
    "SOCO MEGATON",
    "DESVIA OVOS",
    "ECO ESTELAR",
    "SALTO ESTELAR",
    "BATERIA PSG"
};

static u8 s_cursor;
static u16 s_frames;

void SCENE_mgHubEnter(void)
{
    u8 i;

    SPR_reset();
    SPR_update();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101018));
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    VDP_setTextPlane(BG_A);
    VDP_setHilightShadow(FALSE);

    VDP_drawText("MINIGAMES DO KIRBY", 11, 2);
    for (i = 0u; i < MG_HUB_COUNT; i++)
    {
        char line[32];

        strclr(line);
        line[0] = (char) ('1' + i);
        line[1] = ' ';
        line[2] = '\0';
        strcat(line, MG_NAMES[i]);
        VDP_drawText(line, 8, (u16) (6 + (i * 2)));
    }

    VDP_drawText("A/START JOGAR   B MENU", 9, HUD_ROW_HINT_PRIMARY);

    s_cursor = 0u;
    s_frames = 0u;
    AUDIO_playMusic(NULL);
}

void SCENE_mgHubUpdate(void)
{
    s_frames++;

    if ((s_frames & 7u) == 0u)
    {
        VDP_drawText(((s_frames & 8u) != 0u) ? ">" : " ", 7,
                     (u16) (6 + (s_cursor * 2)));
    }

    if (INPUT_pressed(BUTTON_UP) && (s_cursor > 0u))
    {
        s_cursor--;
        AUDIO_playCue(AUDIO_CUE_MENU);
    }
    if (INPUT_pressed(BUTTON_DOWN) && (s_cursor < (MG_HUB_COUNT - 1u)))
    {
        s_cursor++;
        AUDIO_playCue(AUDIO_CUE_MENU);
    }
    if (INPUT_pressed(BUTTON_B))
    {
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START))
    {
        JOURNEY_seedFromInput();
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(MG_SCENES[s_cursor]);
    }
}

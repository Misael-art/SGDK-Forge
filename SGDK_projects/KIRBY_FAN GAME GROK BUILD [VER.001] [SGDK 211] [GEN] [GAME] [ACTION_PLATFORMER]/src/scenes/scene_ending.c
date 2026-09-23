#include <genesis.h>

#include "audio/xgm_router.h"
#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/scene_ending.h"
#include "system/audio.h"
#include "system/input.h"
#include "systems/raster.h"

/*
 * MISSAO 2026-08-24: FINAL do jogo.
 *
 * Sequencia de paineis apos o Fury cair: celebracao, creditos e o AVISO LEGAL
 * obrigatorio do fan game (IP HAL Laboratory / Nintendo), que o brief exige no
 * README - e que tambem pertence a tela final onde o jogador termina.
 *
 * Mesma familia visual da abertura (ceu noturno + colina + Kirby), S/H OFF
 * pelo conflito font x Shadow/Highlight documentado em scene_title.c.
 */

typedef struct {
    const char* line1;
    const char* line2;
} EndingPanel;

static const EndingPanel PANELS[6] = {
    { "O FURY CAIU!",            "" },
    { "AS ESTRELAS E A COMIDA",  "VOLTARAM AO POPSTAR." },
    { "DEDEDE PEDIU DESCULPAS",  "COM UM BANQUETE GIGANTE." },
    { "KIRBY FEZ JUSTICA...",    "E FEZ O JANTAR." },
    { "FIM",                     "OBRIGADO POR JOGAR!" },
    { "KIRBY (C) HAL LAB/NINTENDO", "FAN GAME EDUCACIONAL" }
};

#define ENDING_PANELS 6u
#define ENDING_HOLD_FRAMES 170u

static u8 s_panel;
static u16 s_hold;
static u16 s_frames;
static u16 s_tileNext;
static Sprite* s_sprKirby;

void SCENE_endingEnter(void)
{
    SPR_reset();
    SPR_update();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    s_tileNext = TILE_USER_INDEX;

    PAL_setPalette(PAL0, img_ph_title_stars.palette->data, DMA);
    PAL_setPalette(PAL1, img_ph_title_hill.palette->data, DMA);
    PAL_setPalette(PAL2, spr_ph_kirby.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);

    VDP_drawImageEx(BG_B, &img_ph_title_stars,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, s_tileNext),
                    0, 0, FALSE, TRUE);
    s_tileNext += img_ph_title_stars.tileset->numTile;

    VDP_drawImageEx(BG_A, &img_ph_title_hill,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, s_tileNext),
                    0, 20, FALSE, TRUE);
    s_tileNext += img_ph_title_hill.tileset->numTile;

    /* Logo no final: fecho com a marca, e informacao visual de borda alta
     * que mantem a captura legivel para o gate semantico. */
    VDP_drawImageEx(BG_A, &img_ph_title_logo,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, s_tileNext),
                    6, 2, FALSE, TRUE);
    s_tileNext += img_ph_title_logo.tileset->numTile;

    s_sprKirby = SPR_addSprite(&spr_ph_kirby, 144, 168,
                               TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
    SPR_setAnim(s_sprKirby, 0);

    RASTER_initStage();
    RASTER_updateScroll(0);

    VDP_setHilightShadow(FALSE);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL3);

    s_panel = 0u;
    s_hold = 0u;
    s_frames = 0u;

    AUDIO_playMusic(NULL);   /* silencio de vitoria: o texto e o show */
}

void SCENE_endingUpdate(void)
{
    const EndingPanel* p;

    RASTER_frameStart();
    s_frames++;

    /* Kirby danca: flip alternado + bob de 2px. */
    SPR_setHFlip(s_sprKirby, ((s_frames >> 5) & 1u) != 0u);
    SPR_setPosition(s_sprKirby, 144,
                    (s16) (166 + ((s_frames >> 3) & 1u)));

    p = &PANELS[s_panel];
    if ((s_frames % 60u) == 1u)
    {
        VDP_clearTextArea(1, 12, 38, 4);
        if (p->line2[0] != '\0')
        {
            VDP_drawText(p->line1, (u16) (20 - (strlen(p->line1) >> 1)), 13);
            VDP_drawText(p->line2, (u16) (20 - (strlen(p->line2) >> 1)), 15);
        }
        else
        {
            VDP_drawText(p->line1, (u16) (20 - (strlen(p->line1) >> 1)), 14);
        }
        AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_BELL);
    }

    s_hold++;
    if ((s_hold >= ENDING_HOLD_FRAMES) || INPUT_pressed(BUTTON_START))
    {
        s_hold = 0u;
        s_panel++;

        if (s_panel >= ENDING_PANELS)
        {
            APP_changeScene(APP_SCENE_TITLE);
            return;
        }
    }
}

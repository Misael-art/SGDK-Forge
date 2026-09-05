#include <genesis.h>

#include "audio/xgm_router.h"
#include "core/app.h"
#include "game_vars.h"
#include "minigames/mg_common.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MISSAO 2026-08-24: base comum dos minigames + hub.
 *
 * Toda tela de minigame e texto em PAL3 sobre fundo escuro, S/H OFF (mesma
 * raca do title/menu: font SGDK x Shadow/Highlight nao coexiste). Musica
 * parada: o PSG canal 3 vira o instrumento dos jogos via AUDIO_playUiTone.
 */

#define MG_INPUT_LOCK 30u

static const char* s_title;
static u16 s_frames;
static u16 s_lock;
static bool s_resultMode;

void MG_begin(const char* title)
{
    SPR_reset();
    SPR_update();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101018));
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    VDP_setTextPlane(BG_A);
    VDP_setHilightShadow(FALSE);

    s_title = title;
    s_frames = 0u;
    s_lock = 0u;
    s_resultMode = FALSE;

    VDP_drawText(title, (u16) (20 - (strlen(title) >> 1)), 2);
    VDP_drawText("----------------------------------------", 0, 3);
    VDP_drawText("B: SAIR", 1, HUD_ROW_HINT_PRIMARY);

    AUDIO_playMusic(NULL);   /* PSG livre para o jogo */
}

void MG_drawBackdrop(bool withHill)
{
    u16 tile = TILE_USER_INDEX;

    PAL_setPalette(PAL0, img_ph_title_stars.palette->data, DMA);
    VDP_drawImageEx(BG_B, &img_ph_title_stars,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, tile),
                    0, 0, FALSE, TRUE);
    tile += img_ph_title_stars.tileset->numTile;

    /*
     * Faixa de montanhas em BG_B (linhas 12..23): fica ATRAS do texto do jogo
     * (BG_B sob BG_A) e sobrevive a qualquer erase de caracteres. E o que da'
     * densidade visual real a tela sem brigar com a legibilidade.
     */
    VDP_drawImageEx(BG_B, &img_ph_mount,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE,
                                   tile + img_ph_mount.tileset->numTile * 0),
                    0, 12, FALSE, TRUE);

    if (withHill)
    {
        PAL_setPalette(PAL1, img_ph_title_hill.palette->data, DMA);
        VDP_drawImageEx(BG_A, &img_ph_title_hill,
                        TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE,
                                       tile + img_ph_mount.tileset->numTile),
                        0, 23, FALSE, TRUE);
    }
}

void MG_tickCommon(void)
{
    s_frames++;
    if (s_lock > 0u) s_lock--;
}

bool MG_shouldReturn(void)
{
    if (s_resultMode)
    {
        /* Painel de resultado: qualquer botao principal volta ao hub. */
        if ((s_lock == 0u) &&
            (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START) ||
             INPUT_pressed(BUTTON_B)))
        {
            APP_changeScene(APP_SCENE_MGHUB);
            return TRUE;
        }
        return FALSE;
    }

    if (INPUT_pressed(BUTTON_B))
    {
        APP_changeScene(APP_SCENE_MENU);
        return TRUE;
    }
    return FALSE;
}

bool MG_resultActive(void) { return s_resultMode; }

u16 MG_frames(void) { return s_frames; }

void MG_finish(bool win, s16 score, const char* msg)
{
    char line[41];

    s_resultMode = TRUE;
    s_lock = MG_INPUT_LOCK;

    VDP_clearTextArea(4, 10, 32, 8);
    VDP_drawText(win ? "== VITORIA! ==" : "== FIM ==", 13, 11);
    if (msg != NULL) VDP_drawText(msg, (u16) (20 - (strlen(msg) >> 1)), 13);

    strclr(line);
    strcat(line, "PONTOS: ");
    intToStr((s32) score, line + 8, 1);
    VDP_drawText(line, 15, 15);
    VDP_drawText("A/START: VOLTAR", 12, 18);

    AUDIO_playUiTone(win ? 659u : 196u, 24u);
    AUDIO_playCue(win ? AUDIO_CUE_BRAND_AUTHOR_BELL
                      : AUDIO_CUE_BRAND_PROJECT_WHOOSH);
}

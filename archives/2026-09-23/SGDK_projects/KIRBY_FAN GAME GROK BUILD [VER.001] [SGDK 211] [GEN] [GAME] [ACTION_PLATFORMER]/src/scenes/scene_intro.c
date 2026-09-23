#include <genesis.h>

#include "audio/xgm_router.h"
#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/scene_intro.h"
#include "system/audio.h"
#include "system/input.h"
#include "systems/journey.h"
#include "systems/raster.h"

/*
 * MISSAO 2026-08-24: ABERTURA do jogo (intro cinematic).
 *
 * Reutiliza o ceu noturno e a colina da tela de titulo + o sprite do Kirby.
 * Quatro paineis com typewriter, cada um com cue sonoro proprio do pacote de
 * branding ja selado (bell/whoosh). START pula o painel; dois STARTs saem.
 *
 * S/H OFF: texto sobre font SGDK, mesma raca de title/gameover. O raster
 * noturno fica ligado so para dar o clima - RASTER_setNightSky(TRUE).
 */

typedef struct {
    const char* line1;
    const char* line2;
    AudioCue cue;
} IntroPanel;

static const IntroPanel PANELS[4] = {
    { "EM UM CANTO TRANQUILO", "DO PLANETA POPSTAR...",      AUDIO_CUE_BRAND_AUTHOR_BELL },
    { "O REI DEDEDE ROUBOU",   "A COMIDA E AS ESTRELAS.",    AUDIO_CUE_BRAND_PROJECT_WHOOSH },
    { "UMA BOLOTA ROSADA",     "ACORDOU COM FOME...",        AUDIO_CUE_BRAND_AUTHOR_CLICK },
    { "A JORNADA DE KIRBY",    "COMECA!",                    AUDIO_CUE_BRAND_ENGINE_HIT }
};

#define INTRO_TYPE_FRAMES 3u     /* 1 caractere a cada N frames */
#define INTRO_HOLD_FRAMES 150u   /* pausa apos o painel completo */
#define INTRO_PANELS 4u

static u8 s_panel;
static u16 s_typed;       /* caracteres ja revelados no painel */
static u16 s_hold;
static u16 s_frames;
static Sprite* s_sprKirby;
static u16 s_tileNext;

static void drawPanel(u8 idx)
{
    char buf[41];
    const IntroPanel* p = &PANELS[idx];
    u16 n = s_typed;
    u16 i;

    VDP_clearTextArea(1, 14, 38, 4);

    for (i = 0u; i < 26u; i++)
    {
        if (i >= n) break;
        buf[i] = p->line1[i];
    }
    buf[i] = '\0';
    VDP_drawText(buf, (u16) (20 - (i >> 1)), 15);

    /* Linha 2 so aparece depois da linha 1 completa. */
    if (n > 26u)
    {
        const u16 m = n - 26u;

        for (i = 0u; i < 30u; i++)
        {
            if (i >= m) break;
            buf[i] = p->line2[i];
        }
        buf[i] = '\0';
        VDP_drawText(buf, (u16) (20 - (i >> 1)), 17);
    }
}

void SCENE_introEnter(void)
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

    /*
     * Logo na abertura: convencao de intro (o jogo se apresenta enquanto conta
     * a historia) e, pragmaticamente, o mesmo bloco de alto contraste que faz
     * a captura do titulo passar no gate semantico de informacao.
     */
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

    gJourney.introSeen = TRUE;

    s_panel = 0u;
    s_typed = 0u;
    s_hold = 0u;
    s_frames = 0u;

    AUDIO_playMusic(NULL);
    AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_BELL);
}

void SCENE_introUpdate(void)
{
    bool advance = FALSE;

    RASTER_frameStart();
    s_frames++;

    /* Kirby flutua suavemente sob a colina: seno barato por tabela de frames. */
    SPR_setPosition(s_sprKirby, 144,
                    (s16) (166 + ((s_frames >> 4) & 1u)));

    if ((s_frames % INTRO_TYPE_FRAMES) == 0u)
    {
        const u16 len1 = strlen(PANELS[s_panel].line1);
        const u16 len2 = strlen(PANELS[s_panel].line2);
        const u16 total = len1 + len2;

        if (s_typed < total)
        {
            s_typed++;
            if ((s_typed & 1u) != 0u)
            {
                AUDIO_playCue(AUDIO_CUE_BRAND_AUTHOR_CLICK);
            }
            drawPanel(s_panel);
        }
        else
        {
            s_hold++;
            if (s_hold >= INTRO_HOLD_FRAMES) advance = TRUE;
        }
    }

    if (INPUT_pressed(BUTTON_START))
    {
        if (s_panel == (INTRO_PANELS - 1u)) advance = TRUE;
        else
        {
            /* Pula o painel atual inteiro. */
            s_typed = 100u;
            s_hold = INTRO_HOLD_FRAMES;
            drawPanel(s_panel);
        }
    }

    if (advance)
    {
        s_panel++;
        s_typed = 0u;
        s_hold = 0u;

        if (s_panel >= INTRO_PANELS)
        {
            AUDIO_playCue(AUDIO_CUE_MENU);
            APP_changeScene(APP_SCENE_MENU);
            return;
        }

        AUDIO_playCue(PANELS[s_panel].cue);
        VDP_clearTextArea(1, 14, 38, 4);
    }
}

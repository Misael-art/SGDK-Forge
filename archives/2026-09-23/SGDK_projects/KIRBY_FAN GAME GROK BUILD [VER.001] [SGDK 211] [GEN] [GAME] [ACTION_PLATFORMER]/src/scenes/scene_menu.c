#include <genesis.h>

#include "audio/xgm_router.h"

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/scene_menu.h"
#include "system/audio.h"
#include "system/input.h"
#include "systems/journey.h"

/*
 * MISSAO 2026-08-24: menu real do jogo, substituindo o placeholder do template
 * (que era a casa das 11 violacoes de audio baselined).
 *
 * Tres estados inline, sem sub-cenas:
 *   MAIN    -> HISTORIA / FASES / MINIGAMES
 *   STAGES  -> as 5 fases da jornada, com trava por progresso
 *   MG      -> os 7 minigames (sempre liberados)
 *
 * Texto sempre em PAL3 (cinza canonical de overlay) sobre fundo limpo:
 * S/H permanece OFF nesta cena - mesma raca do title/gameover, o font SGDK
 * nao coexiste com S/H global sem tratamento especial (ver scene_title.c).
 */

#define MENU_ITEM_COUNT 3u

typedef enum MenuState {
    MENU_MAIN = 0,
    MENU_STAGES = 1,
    MENU_MG = 2
} MenuState;

static const char* const MAIN_ITEMS[MENU_ITEM_COUNT] = {
    "HISTORIA",
    "FASES",
    "MINIGAMES"
};

static MenuState s_state;
static u8 s_cursor;
static u16 s_frames;

static void drawMain(void)
{
    u8 i;

    VDP_clearPlane(BG_A, TRUE);

    /*
     * MISSAO 2026-08-24: identidade visual do menu. Fundo de estrelas em BG_B,
     * colina fechando a tela e o logo no topo - o mesmo vocabulario do titulo,
     * para que o menu nao seja uma tela de texto flutuando no vazio (o gate
     * semantico de captura rejeita composicao pobre, e com razao).
     */
    VDP_drawImageEx(BG_B, &img_ph_title_stars,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, TILE_USER_INDEX),
                    0, 0, FALSE, TRUE);
    VDP_drawImageEx(BG_A, &img_ph_title_logo,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE,
                                   TILE_USER_INDEX + img_ph_title_stars.tileset->numTile),
                    6, 2, FALSE, TRUE);
    VDP_drawImageEx(BG_A, &img_ph_title_hill,
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE,
                                   TILE_USER_INDEX + img_ph_title_stars.tileset->numTile +
                                   img_ph_title_logo.tileset->numTile),
                    0, 21, FALSE, TRUE);

    for (i = 0u; i < MENU_ITEM_COUNT; i++)
    {
        VDP_drawText(MAIN_ITEMS[i], 15, (u16) (12 + (i * 2)));
    }
}

static void drawStages(void)
{
    u8 i;

    VDP_clearPlane(BG_A, TRUE);
    VDP_drawText("SELECIONAR FASE", 13, 4);

    for (i = 0u; i < JOURNEY_STAGE_COUNT; i++)
    {
        char line[32];
        const StageDef* def = JOURNEY_stageDef(i);
        const bool unlocked = ((gJourney.unlockedMask & (1u << i)) != 0u);

        strclr(line);
        strcat(line, "FASE ");
        line[5] = (char) ('1' + i);
        line[6] = ' ';
        line[7] = '\0';
        strcat(line, unlocked ? def->name : "BLOQUEADA");
        VDP_drawText(line, 4, (u16) (7 + (i * 2)));
    }
}

static void drawMg(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_drawText("MINIGAMES", 15, 4);
    VDP_drawText("1 DUELO RELAMPAGO", 6, 7);
    VDP_drawText("2 CHUVA DE ESTRELAS", 6, 9);
    VDP_drawText("3 SOCO MEGATON", 6, 11);
    VDP_drawText("4 DESVIA OVOS", 6, 13);
    VDP_drawText("5 ECO ESTELAR", 6, 15);
    VDP_drawText("6 SALTO ESTELAR", 6, 17);
    VDP_drawText("7 BATERIA PSG", 6, 19);
}

static void drawCursor(u8 count)
{
    u8 i;
    char blank[40];

    strclr(blank);
    for (i = 0u; i < count; i++)
    {
        /* Coluna fixa do cursor; apaga a linha anterior antes de desenhar. */
        VDP_drawText(" ", 4, (u16) (7 + (i * 2)));
        VDP_drawText(" ", 14, (u16) (12 + (i * 2)));
    }
    (void) blank;

    switch (s_state)
    {
        case MENU_MAIN:
            VDP_drawText(">", 14, (u16) (12 + (s_cursor * 2)));
            break;
        case MENU_STAGES:
            VDP_drawText(">", 3, (u16) (7 + (s_cursor * 2)));
            break;
        default:
            break;
    }

    if (s_state == MENU_MG)
    {
        VDP_drawText(">", 5, (u16) (7 + (s_cursor * 2)));
    }
}

static void drawHint(void)
{
    VDP_drawText("A/START OK   B VOLTAR   C HUD", 6, HUD_ROW_HINT_PRIMARY);
}

void SCENE_menuEnter(void)
{
    SPR_reset();
    SPR_update();

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102410));
    PAL_setPalette(PAL0, img_ph_title_stars.palette->data, DMA);
    PAL_setPalette(PAL1, img_ph_title_logo.palette->data, DMA);
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);

    s_state = MENU_MAIN;
    s_cursor = 0u;
    s_frames = 0u;

    drawMain();
    drawCursor(MENU_ITEM_COUNT);
    drawHint();

    AUDIO_playMusic(NULL);   /* menu em silencio: o PSG dos minigames comeca limpo */
}

void SCENE_menuUpdate(void)
{
    s_frames++;

    if ((s_frames & 7u) == 0u)
    {
        /* Cursor pisca sem custo de blit por frame: so a cada 8 frames. */
        if (s_state == MENU_MAIN)
        {
            VDP_drawText(((s_frames & 8u) != 0u) ? ">" : " ", 14,
                         (u16) (12 + (s_cursor * 2)));
        }
        else if (s_state == MENU_STAGES)
        {
            VDP_drawText(((s_frames & 8u) != 0u) ? ">" : " ", 3,
                         (u16) (7 + (s_cursor * 2)));
        }
        else
        {
            VDP_drawText(((s_frames & 8u) != 0u) ? ">" : " ", 5,
                         (u16) (7 + (s_cursor * 2)));
        }
    }

    if (INPUT_pressed(BUTTON_UP))
    {
        if (s_cursor > 0u) s_cursor--;
        AUDIO_playCue(AUDIO_CUE_MENU);
    }
    else if (INPUT_pressed(BUTTON_DOWN))
    {
        u8 max = MENU_ITEM_COUNT - 1u;

        if (s_state == MENU_STAGES) max = JOURNEY_STAGE_COUNT - 1u;
        else if (s_state == MENU_MG) max = 6u;

        if (s_cursor < max) s_cursor++;
        AUDIO_playCue(AUDIO_CUE_MENU);
    }

    if (INPUT_pressed(BUTTON_B))
    {
        AUDIO_playCue(AUDIO_CUE_MENU);
        if (s_state == MENU_MAIN)
        {
            APP_changeScene(APP_SCENE_TITLE);
            return;
        }
        s_state = MENU_MAIN;
        s_cursor = 0u;
        drawMain();
        drawCursor(MENU_ITEM_COUNT);
        return;
    }

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START))
    {
        AUDIO_playCue(AUDIO_CUE_MENU);

        switch (s_state)
        {
            case MENU_MAIN:
                if (s_cursor == 0u)
                {
                    JOURNEY_resetNewGame();
                    JOURNEY_seedFromInput();
                    APP_changeScene(APP_SCENE_INTRO);
                    return;
                }
                if (s_cursor == 1u)
                {
                    s_state = MENU_STAGES;
                    s_cursor = 0u;
                    drawStages();
                    drawHint();
                }
                else
                {
                    s_state = MENU_MG;
                    s_cursor = 0u;
                    drawMg();
                    drawHint();
                }
                break;

            case MENU_STAGES:
            {
                const bool unlocked =
                    ((gJourney.unlockedMask & (1u << s_cursor)) != 0u);

                if (!unlocked)
                {
                    VDP_drawText("COMPLETE A FASE ANTERIOR!", 8, 20);
                    break;
                }
                gJourney.stageIndex = s_cursor;
                gJourney.bossPending = FALSE;
                gJourney.finalBoss = FALSE;
                JOURNEY_seedFromInput();
                APP_changeScene(APP_SCENE_STAGE);
                return;
            }

            default:
            {
                static const AppScene MG_SCENES[7] = {
                    APP_SCENE_MG_QUICKDRAW,
                    APP_SCENE_MG_STARFALL,
                    APP_SCENE_MG_PUNCH,
                    APP_SCENE_MG_DODGE,
                    APP_SCENE_MG_SIMON,
                    APP_SCENE_MG_HIGHJUMP,
                    APP_SCENE_MG_RHYTHM
                };

                APP_changeScene(MG_SCENES[s_cursor]);
                return;
            }
        }
    }
}

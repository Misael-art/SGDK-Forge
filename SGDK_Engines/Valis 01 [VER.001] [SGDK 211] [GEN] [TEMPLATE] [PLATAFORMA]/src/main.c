#include <genesis.h>

#include "gfx.h"
#include "sprites.h"

// Este template demonstra um menu visual simples:
// fundo estatico, tres sprites e selecao via controle.
static Sprite *gSprites[3];
static const s16 gSpriteX[3] = {48, 144, 256};
static const s16 gSpriteY[3] = {144, 128, 160};
static const char *gSpriteNames[3] = {"Heroina", "Esqueleto", "Pocao"};

// Monta o fundo do exemplo e carrega a paleta principal.
static void draw_stage(void)
{
    VDP_setScreenWidth320();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_drawImageEx(
        BG_B,
        &bg_image,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, 1),
        0,
        0,
        FALSE,
        TRUE);
    PAL_setPalette(PAL0, bg_palette.data, DMA);
}

// Atualiza o texto do topo para mostrar qual sprite esta selecionado.
static void draw_hud(u16 selected)
{
    VDP_clearTextArea(0, 0, 40, 4);
    VDP_drawText("VALIS 01 TEMPLATE", 1, 0);
    VDP_drawText("LEFT/RIGHT = troca sprite", 1, 1);
    VDP_drawText("A/B/C = selecao direta", 1, 2);
    VDP_drawText("Selecionado:", 1, 3);
    VDP_drawText((char *)gSpriteNames[selected], 14, 3);
}

// Inicializa o sistema de sprites e cria os tres elementos visuais da cena.
static void init_scene(void)
{
    draw_stage();
    SPR_init();

    PAL_setPalette(PAL1, imgvalis.palette->data, DMA);
    PAL_setPalette(PAL2, imgesqueleto.palette->data, DMA);
    PAL_setPalette(PAL3, imgpocao.palette->data, DMA);

    gSprites[0] = SPR_addSprite(&imgvalis, gSpriteX[0], gSpriteY[0], TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
    gSprites[1] = SPR_addSprite(&imgesqueleto, gSpriteX[1], gSpriteY[1], TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    gSprites[2] = SPR_addSprite(&imgpocao, gSpriteX[2], gSpriteY[2], TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
}

// O sprite selecionado sobe alguns pixels para funcionar como cursor visual.
static void update_selection(u16 selected)
{
    u16 index;

    for (index = 0; index < 3; index++)
    {
        s16 y = gSpriteY[index];
        if (index == selected)
        {
            y -= 8;
        }

        SPR_setPosition(gSprites[index], gSpriteX[index], y);
    }
}

// Aqui temos um loop de menu: leitura do controle, mudanca da selecao,
// atualizacao dos sprites e sincronizacao com o VBlank.
int main(void)
{
    u16 selected = 0;
    u16 previousJoy = 0;

    JOY_init();
    init_scene();
    draw_hud(selected);

    while (TRUE)
    {
        u16 joy = JOY_readJoypad(JOY_1);
        // Detecta apenas o instante em que o botao foi apertado.
        u16 pressed = joy & ~previousJoy;

        if (pressed & BUTTON_LEFT)
        {
            selected = (selected == 0) ? 2 : (selected - 1);
            draw_hud(selected);
        }
        if (pressed & BUTTON_RIGHT)
        {
            selected = (selected + 1) % 3;
            draw_hud(selected);
        }
        if (pressed & BUTTON_A)
        {
            selected = 0;
            draw_hud(selected);
        }
        if (pressed & BUTTON_B)
        {
            selected = 1;
            draw_hud(selected);
        }
        if (pressed & BUTTON_C)
        {
            selected = 2;
            draw_hud(selected);
        }

        update_selection(selected);
        SPR_update();
        SYS_doVBlankProcess();
        previousJoy = joy;
    }
}

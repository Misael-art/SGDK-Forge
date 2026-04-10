#include <genesis.h>
#include "bg.h"
#include "bt.h"

// Este exemplo mostra o ciclo minimo de um prototipo 2D em SGDK:
// preparar o cenario, criar um sprite, ler o controle e atualizar a tela.
static Sprite *gHero = NULL;
static s16 gX = 144;
static s16 gY = 128;
static bool gFlip = FALSE;

// Desenha o fundo e um pequeno HUD para explicar os comandos.
static void draw_scene(void)
{
    VDP_setScreenWidth320();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_drawImageEx(
        BG_B,
        &bg_musica,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, 1),
        0,
        0,
        FALSE,
        TRUE);
    PAL_setPalette(PAL0, bg_musica.palette->data, DMA);
    PAL_setPalette(PAL1, spr_kim_121.palette->data, DMA);

    VDP_drawText("IMGS EXAMPLE", 1, 1);
    VDP_drawText("DPAD = move", 1, 2);
    VDP_drawText("A = flip sprite", 1, 3);
    VDP_drawText("B = reset pos", 1, 4);
}

// Volta o personagem para o ponto inicial do exemplo.
static void reset_hero(void)
{
    gX = 144;
    gY = 128;
    gFlip = FALSE;
}

// O loop principal segue a ordem basica de quase todo jogo SGDK:
// ler input, atualizar estado, redesenhar sprites e esperar o VBlank.
int main(void)
{
    u16 previousJoy = 0;

    JOY_init();
    SPR_init();
    reset_hero();
    draw_scene();

    gHero = SPR_addSprite(&spr_kim_121, gX, gY, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));

    while (TRUE)
    {
        u16 joy = JOY_readJoypad(JOY_1);
        // "pressed" guarda apenas os botoes que acabaram de mudar para pressionado.
        u16 pressed = joy & ~previousJoy;

        if (joy & BUTTON_LEFT)  gX -= 2;
        if (joy & BUTTON_RIGHT) gX += 2;
        if (joy & BUTTON_UP)    gY -= 2;
        if (joy & BUTTON_DOWN)  gY += 2;

        if (pressed & BUTTON_A) gFlip = !gFlip;
        if (pressed & BUTTON_B) reset_hero();

        SPR_setHFlip(gHero, gFlip);
        SPR_setPosition(gHero, gX, gY);
        SPR_update();
        SYS_doVBlankProcess();
        previousJoy = joy;
    }
}

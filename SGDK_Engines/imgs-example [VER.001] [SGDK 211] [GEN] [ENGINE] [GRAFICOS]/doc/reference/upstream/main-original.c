
// *****************************************************************************
//  Scaling Example
//
//  Written in 2021 by Andreas Dietrich
// *****************************************************************************

// -----------------------------------------------------------------------------
//  Includes
// -----------------------------------------------------------------------------

// SGDK
#include <genesis.h>

// Resources
#include "bg.h"
#include "bt.h"
#include "sound.h"

// *****************************************************************************
//
//  Main
//
// *****************************************************************************

Sprite *spr1 = NULL;

u8 img_vdp[0x23];
u16 img_cram[64];
u32 *img_vram;
void IMG_load()
{
    SYS_doVBlankProcess();
    vu16 *pw;
    pw = (u16 *) VDP_CTRL_PORT;
    for (int i = 0x00; i < 0x12; i++) *pw = 0x8000 | (i << 8) | img_vdp[i]; // load vdp registers

    DMA_doCPUCopyDirect(0x40000000,&img_vram,0x8000,2); // load vram

    PAL_setColors(0, img_cram, 64, CPU); // load pal

}

void tela_principal()
{
    VDP_resetScreen();
    VDP_init();
    SPR_reset();
    SPR_init();
    SYS_doVBlankProcess();
    VDP_loadTileSet(bg_musica.tileset, 1, DMA);
    VDP_setTileMapEx(BG_B, bg_musica.tilemap,TILE_ATTR_FULL(PAL0, 0,0,0,1), 0,0,0,0, 40,28,DMA_QUEUE);
    PAL_setPalette(PAL0, bg_musica.palette->data, DMA_QUEUE);
    VDP_drawText("press B to load img ", 0,0);
    VDP_drawText("press A to reload normal img ", 0,1);
    SYS_doVBlankProcess();
    spr1 = SPR_addSprite(&spr_kim_121, 0, 0, TILE_ATTR(PAL3, FALSE, FALSE, TRUE));
    PAL_setPalette(PAL3, spr_kim_121.palette->data, DMA_QUEUE);
    SYS_doVBlankProcess();
}

void IMG_carregar()
{
    SPR_reset();
    SPR_update();
    SYS_doVBlankProcess();
    IMG_load();
}

int main()
{

    SYS_disableInts();
    {
        SPR_init();
    }
    SYS_enableInts();

    tela_principal();

    while (TRUE)
    {

        u16 joy = JOY_readJoypad(JOY_1);
        if (joy & BUTTON_B) {
            IMG_carregar();
        }
        if(joy & BUTTON_A){
            tela_principal();
        }

        SPR_update();
        SYS_doVBlankProcess();
    }
}

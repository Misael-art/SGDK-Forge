#include <genesis.h>
#include "arquivos.h"

#define ANIM_STAND 0
#define ANIM_RUN   1

#define NUM_OPTIONS 3

typedef struct
{
  u16 x;
  u16 y;
} Option;


Option options[NUM_OPTIONS] = {
    {80, 80},
    {80, 120},
    {80, 160},
};

u8 currentIndex = 0;

Sprite* cursor;
int cursor_posX = 80;
int cursor_posY= 160;

Sprite *sonic_obj;
int sonicX = 30;
int sonicY = 160;

Sprite *amy_obj;
int amyX = 30;
int amyY = 160;

Sprite *knuckles_obj;
int knucklesX = 30;
int knucklesY = 160;


void updateCursorPosition();
void moveUp();
void moveDown();
void joyEventHandlerMenu(u16 joy, u16 changed, u16 state);
void select(u16 Option);

void sonic_player();
void amy_player();
void knuckles_player();
void carregarFase();

static void handleInputSonic();
static void handleInputAmy();
static void handleInputKnuckles();

int main()
{

SPR_init();
JOY_init();
JOY_setEventHandler(&joyEventHandlerMenu);

VDP_setTextPlane(BG_A);
VDP_setTextPalette(PAL1);
VDP_drawText("SELECT YOUR PLAYER", 11, 4);

VDP_drawText("SONIC", 16, 12);
VDP_drawText("AMY", 17, 17);
VDP_drawText("KNUCKLES", 16, 22);

VDP_drawImageEx(BG_B, &tela_inicio, TILE_ATTR(PAL0,FALSE,FALSE,FALSE),0,0,FALSE,TRUE);
PAL_setPalette(PAL0,tela_inicio.palette->data, DMA);

cursor = SPR_addSprite(&cursor_spr, cursor_posX , cursor_posY, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
PAL_setPalette(PAL3, cursor_spr.palette->data, DMA);

updateCursorPosition();

while(1)
{

SPR_update();
handleInputSonic();
handleInputAmy();
handleInputKnuckles();
SYS_doVBlankProcess();

}

return(0);
}

 void updateCursorPosition()
{
    SPR_setPosition(cursor, options[currentIndex].x, options[currentIndex].y);
}


void moveUp()
{
    if (currentIndex > 0)
    {
        currentIndex--;
        updateCursorPosition();
    }
}

void moveDown()
{
    if (currentIndex < NUM_OPTIONS - 1)
    {
        currentIndex++;
        updateCursorPosition();
    }
}

void joyEventHandlerMenu(u16 joy, u16 changed, u16 state)
{
    if (changed & state & BUTTON_UP)
    {
        moveUp();
    }
    else if (changed & state & BUTTON_DOWN)
    {
        moveDown();
    }
    if (changed & state & BUTTON_START)
    {
        select(currentIndex);
    }
}

void select(u16 Option)
{
    switch (Option)
    {
    case 0:
    {
        sonic_player();
        break;
    }
    case 1:
    {
        amy_player();
        break;
    }
    case 2:
    {
        knuckles_player();
        break;
    }

    default:
    break;
  }
}

void carregarFase()
{

VDP_clearPlane(BG_A,TRUE);
VDP_clearPlane(BG_B,TRUE);

int ind_tileset = 1;

VDP_drawImageEx(BG_A, &bga_map, TILE_ATTR_FULL(PAL0,FALSE,FALSE,FALSE,ind_tileset),0,0,FALSE,TRUE);
ind_tileset += bga_map.tileset->numTile;
PAL_setPalette(PAL0,bga_map.palette->data, DMA);

VDP_drawImageEx(BG_B, &bgb_map, TILE_ATTR_FULL(PAL1,FALSE,FALSE,FALSE,ind_tileset),0,0,FALSE,TRUE);
ind_tileset += bgb_map.tileset->numTile;
PAL_setPalette(PAL1,bgb_map.palette->data, DMA);

}

void sonic_player()
{
  SPR_init();

  sonic_obj = SPR_addSprite(&sonic_spr, sonicX , sonicY, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
  PAL_setPalette(PAL3, sonic_spr.palette->data, DMA);

  carregarFase();

}

void amy_player()
{
  SPR_init();

  amy_obj = SPR_addSprite(&amy_spr, amyX , amyY, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
  PAL_setPalette(PAL3, amy_spr.palette->data, DMA);

  carregarFase();

}

void knuckles_player()
{
   SPR_init();

   knuckles_obj = SPR_addSprite(&knuckles_spr, knucklesX , knucklesY, TILE_ATTR(PAL3, TRUE, FALSE, FALSE));
   PAL_setPalette(PAL3, knuckles_spr.palette->data, DMA);

    carregarFase();

}

static void handleInputSonic()
{

    u16 value = JOY_readJoypad (JOY_1);

    if(value & BUTTON_LEFT)

      {
          sonicX -= 2;
          SPR_setAnim(sonic_obj, ANIM_RUN);
          SPR_setHFlip(sonic_obj, TRUE);
      }
    else if(value & BUTTON_RIGHT)
    {
          sonicX += 2;
          SPR_setAnim(sonic_obj, ANIM_RUN);
          SPR_setHFlip(sonic_obj, FALSE);
    }

    if(value & BUTTON_A)
    {
        SYS_hardReset();
    }

    if(!(value & BUTTON_LEFT) && !(value & BUTTON_RIGHT))
    {
       SPR_setAnim(sonic_obj, 0);
    }

    SPR_setPosition(sonic_obj, sonicX, sonicY);
}

static void handleInputAmy()
{

    u16 value = JOY_readJoypad (JOY_1);

    if(value & BUTTON_LEFT)

      {
          amyX -= 2;
          SPR_setAnim(amy_obj, ANIM_RUN);
          SPR_setHFlip(amy_obj, TRUE);
      }
    else if(value & BUTTON_RIGHT)
    {
          amyX += 2;
          SPR_setAnim(amy_obj, ANIM_RUN);
          SPR_setHFlip(amy_obj, FALSE);
    }

    if(value & BUTTON_A)
    {
        SYS_hardReset();
    }

    if(!(value & BUTTON_LEFT) && !(value & BUTTON_RIGHT))
    {
       SPR_setAnim(amy_obj, 0);
    }

    SPR_setPosition(amy_obj, amyX, amyY);
}

static void handleInputKnuckles()
{

    u16 value = JOY_readJoypad (JOY_1);

    if(value & BUTTON_LEFT)

      {
          knucklesX -= 2;
          SPR_setAnim(knuckles_obj, ANIM_RUN);
          SPR_setHFlip(knuckles_obj, TRUE);
      }
    else if(value & BUTTON_RIGHT)
    {
          knucklesX  += 2;
          SPR_setAnim(knuckles_obj, ANIM_RUN);
          SPR_setHFlip(knuckles_obj, FALSE);
    }

    if(value & BUTTON_A)
    {
        SYS_hardReset();
    }

    if(!(value & BUTTON_LEFT) && !(value & BUTTON_RIGHT))
    {
       SPR_setAnim(knuckles_obj, 0);
    }

    SPR_setPosition(knuckles_obj, knucklesX , knucklesY);
}

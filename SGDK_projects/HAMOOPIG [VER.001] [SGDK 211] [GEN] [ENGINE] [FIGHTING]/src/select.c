#include <genesis.h>
#include "select.h"
#include "globals.h"
#include "scene.h"
#include "sprite.h"
#include "ken.h"
#include "musgo.h"
#include "init.h"
#include "player.h"

static Sprite *sPreview[2];
static u8 sLocked[3];

static const char *fighter_name(u8 id)
{
	if(id == 2){ return "KEN  "; }
	if(id == 3){ return "MUSGO"; }
	return "RYO  ";
}

static void preview_def(u8 slot, u8 id)
{
	if(sPreview[slot])
	{
		SPR_releaseSprite(sPreview[slot]);
		sPreview[slot] = NULL;
	}
	if(id == 2)
	{
		sPreview[slot] = SPR_addSpriteExSafe(&spr_ken_100, (slot == 0) ? 48 : 208, 88,
			TILE_ATTR((slot == 0) ? PAL2 : PAL3, FALSE, FALSE, FALSE),
			SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	}
	else if(id == 3)
	{
		sPreview[slot] = SPR_addSpriteExSafe(&spr_musgo_100, (slot == 0) ? 40 : 200, 80,
			TILE_ATTR((slot == 0) ? PAL2 : PAL3, FALSE, FALSE, FALSE),
			SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	}
	else
	{
		sPreview[slot] = SPR_addSpriteExSafe(&spr_ryo_100, (slot == 0) ? 48 : 208, 80,
			TILE_ATTR((slot == 0) ? PAL2 : PAL3, FALSE, FALSE, FALSE),
			SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	}
	if(sPreview[slot] && slot == 1)
	{
		SPR_setHFlip(sPreview[slot], TRUE);
	}
}

static void apply_slot_palette(u8 slot, u8 id)
{
	u16 pal = (slot == 0) ? PAL2 : PAL3;
	if(id == 2){ PAL_setPalette(pal, spr_ken_pal1.palette->data, CPU); }
	else if(id == 3){ PAL_setPalette(pal, spr_musgo_pal1.palette->data, CPU); }
	else { PAL_setPalette(pal, spr_ryo_pal1.palette->data, CPU); }
}

void FUNCAO_SELECT_INIT()
{
	u16 i;

	sPreview[0] = NULL;
	sPreview[1] = NULL;
	sLocked[1] = 0;
	sLocked[2] = 0;
	cursorP1_ID = 1;
	cursorP2_ID = 3;
	endP1Selection = FALSE;
	endP2Selection = FALSE;
	charSelStep = 0;

	VDP_setBackgroundColor(0);
	PAL_setPalette(PAL1, spr_point.palette->data, CPU);
	VDP_setTextPalette(PAL1);
	VDP_drawText("SELECT FIGHTER", 13, 2);
	VDP_drawText("P1: LEFT/RIGHT  A/START", 7, 4);
	VDP_drawText("P2: LEFT/RIGHT  A/START", 7, 5);
	VDP_drawText(fighter_name(cursorP1_ID), 9, 24);
	VDP_drawText(fighter_name(cursorP2_ID), 25, 24);
	VDP_drawText("LEFT/RIGHT: RYO KEN MUSGO", 7, 7);

	apply_slot_palette(0, cursorP1_ID);
	apply_slot_palette(1, cursorP2_ID);
	preview_def(0, cursorP1_ID);
	preview_def(1, cursorP2_ID);

	for(i = 0; i < 12; i++)
	{
		P[1].key_JOY_status[i] = KEY_FREE;
		P[2].key_JOY_status[i] = KEY_FREE;
	}
}

static void cycle_id(u8 *id)
{
	*id = (*id == 1) ? 2 : ((*id == 2) ? 3 : 1);
}

void FUNCAO_SELECT_UPDATE()
{

	if(!sLocked[1])
	{
		if(P[1].key_JOY_LEFT_status == 1 || P[1].key_JOY_RIGHT_status == 1)
		{
			cycle_id(&cursorP1_ID);
			apply_slot_palette(0, cursorP1_ID);
			preview_def(0, cursorP1_ID);
			VDP_drawText(fighter_name(cursorP1_ID), 9, 24);
		}
		if(P[1].key_JOY_A_status == 1 || P[1].key_JOY_START_status == 1)
		{
			sLocked[1] = 1;
			endP1Selection = TRUE;
			VDP_drawText("OK", 10, 25);
		}
	}
	if(!sLocked[2])
	{
		if(P[2].key_JOY_LEFT_status == 1 || P[2].key_JOY_RIGHT_status == 1)
		{
			cycle_id(&cursorP2_ID);
			apply_slot_palette(1, cursorP2_ID);
			preview_def(1, cursorP2_ID);
			VDP_drawText(fighter_name(cursorP2_ID), 25, 24);
		}
		if(P[2].key_JOY_A_status == 1 || P[2].key_JOY_START_status == 1)
		{
			sLocked[2] = 1;
			endP2Selection = TRUE;
			VDP_drawText("OK", 26, 25);
		}
	}

	if(sLocked[1] && !sLocked[2] && P[1].key_JOY_START_status == 1 && gFrames > 4)
	{
		/* P1 confirmed and pressed Start again: P2 keeps current cursor */
		sLocked[2] = 1;
		endP2Selection = TRUE;
		VDP_drawText("OK", 26, 25);
	}

	if(gPing2 == 0)
	{
		VDP_drawText("<P1>", 9, 23);
		VDP_drawText("<P2>", 25, 23);
	}

	if(sLocked[1] && sLocked[2])
	{
		charSelStep++;
		if(charSelStep >= 20)
		{
			FUNCAO_SELECT_EXIT();
		}
	}
}

void FUNCAO_SELECT_EXIT()
{
	P[1].id = cursorP1_ID;
	P[2].id = cursorP2_ID;
	P[1].palID = 1;
	P[2].palID = (P[1].id == P[2].id) ? 2 : 1;
	cursorP1ColorChoice = P[1].palID;
	cursorP2ColorChoice = P[2].palID;
	if(sPreview[0]){ SPR_releaseSprite(sPreview[0]); sPreview[0] = NULL; }
	if(sPreview[1]){ SPR_releaseSprite(sPreview[1]); sPreview[1] = NULL; }
	CLEAR_VDP();
	SCENE_request(SCENE_FIGHT);
}

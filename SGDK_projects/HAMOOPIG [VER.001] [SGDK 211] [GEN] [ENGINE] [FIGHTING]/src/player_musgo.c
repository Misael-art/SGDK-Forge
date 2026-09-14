#include <genesis.h>
#include "player.h"
#include "globals.h"
#include "player_musgo_table.h"

void PLAYER_STATE_MUSGO(u8 Player, u16 State)
{
	const MusgoStateAnim *a = musgo_anim_for(State);
	u8 i;

	if(State==100 || State==610 || State==607 || State==611 || State==612 || State==615 || State==570
		|| State==200 || State==201 || State==207 || State==208 || State==209 || State==608
		|| State==410 || State==420 || State==471 || State==472
		|| State==101 || State==102 || State==104 || State==105 || State==106
		|| State==107 || State==108 || State==109 || State==110 || State==113 || State==151
		|| State==152 || State==154 || State==155
		|| State==700)
	{
		P[Player].y = gAlturaPiso;
	}

	P[Player].w = a->w;
	P[Player].h = a->h;
	P[Player].axisX = a->axisX;
	P[Player].axisY = a->axisY;
	P[Player].animFrameTotal = a->frames;
	for(i = 0; i < 12; i++)
	{
		P[Player].dataAnim[i + 1] = a->timing[i];
	}

	if(State==550)
	{
		P[Player].gravidadeY = 3;
		P[Player].impulsoY = -14;
		P[Player].y -= (7 * 8) - 4;
	}

	P[Player].sprite = SPR_addSpriteExSafe(
		a->def,
		P[Player].x - P[Player].axisX,
		P[Player].y - P[Player].axisY,
		TILE_ATTR(P[Player].paleta, FALSE, FALSE, FALSE),
		SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE | SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
}

#include <genesis.h>
#include "hud.h"
#include "globals.h"
#include "scene.h"
#include "timing.h"
#include "sprite.h"
#include "hud_gfx.h"

static void hud_window_draw_clock(void);

void FUNCAO_RELOGIO()
{
	if(gClockTimer>0 && (gClockLTimer>0 || gClockRTimer>0) && (P[1].energiaBase>0 && P[2].energiaBase>0) ){ gClockTimer--; }

	if(gClockTimer==0)
	{
		gClockRTimer--;
		if(gClockRTimer==-1)
		{
			if(gClockLTimer>0)
			{
				gClockLTimer--;
				gClockRTimer=9;
			}
			else
			{
				gClockRTimer=0;
			}
		}
		gClockTimer=(s8)TIMING_roundClockTicks();
		hud_window_draw_clock();
	}
}

#define HUD_P1_X            8
#define HUD_P2_X            184
#define HUD_BAR_SEGMENTS    8
#define HUD_BAR_Y           4
#define HUD_BAR_STEP        16
#define HUD_CLK_L_X         144
#define HUD_CLK_R_X         160
#define HUD_CLK_Y           24
#define HUD_MESSAGE_ROW     5
#define HUD_MESSAGE_ROWS    6

static u16 sHudMessageTileBase;
static u16 sHudBlackTile;
static u8 sHudMessage = 0xFF;
static u16 sHudMessageMap[40 * HUD_MESSAGE_ROWS];
static Sprite *sHudP1Segments[HUD_BAR_SEGMENTS];
static Sprite *sHudP2Segments[HUD_BAR_SEGMENTS];
static Sprite *sHudClockSpriteL;
static Sprite *sHudClockSpriteR;
static u16 sHudSegmentTile;
static s8  sHudClockDigitL = -1;
static s8  sHudClockDigitR = -1;
static u8  sHudWindowActive = 0;

/* PAL1 index 11 = black. Kept only for the transient result-message panel;
   the life bars themselves no longer paint a full-width WINDOW rectangle. */
static const u32 kHudBlackTile[8] =
{
	0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB,
	0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB, 0xBBBBBBBB
};

void hud_window_load(void)
{
	/* Bars and clock are sprites. Their definitions allocate VRAM from the
	   sprite pool and no longer consume the stage/plane tile range here. */
	sHudMessageTileBase = gInd_tileset;
	VDP_loadTileSet(&ts_hud_message_font, sHudMessageTileBase, DMA);
	gInd_tileset += ts_hud_message_font.numTile;
	sHudBlackTile = gInd_tileset;
	VDP_loadTileData(kHudBlackTile, sHudBlackTile, 1, CPU);
	gInd_tileset += 1;
	sHudMessage = 0xFF;
}

static u8 hud_clock_digit(s8 v)
{
	if(v < 0){ return 0; }
	if(v > 9){ return 9; }
	return (u8)v;
}

static void hud_window_put_digit(u8 side, u8 digit)
{
	Sprite *sprite = (side == 0) ? sHudClockSpriteL : sHudClockSpriteR;
	if(!sprite){ return; }
	SPR_setFrame(sprite, digit);
}

static void hud_window_draw_clock(void)
{
	s8 left;
	s8 right;

	if(!sHudWindowActive){ return; }
	left = (s8)hud_clock_digit(gClockLTimer);
	right = (s8)hud_clock_digit(gClockRTimer);
	if(left == sHudClockDigitL && right == sHudClockDigitR){ return; }
	sHudClockDigitL = left;
	sHudClockDigitR = right;
	hud_window_put_digit(0, (u8)left);
	hud_window_put_digit(1, (u8)right);
}

static u8 hud_segment_count(s8 energy)
{
	u16 e = (energy < 0) ? 0 : (energy > 96 ? 96 : (u16)energy);
	return (u8)((e * HUD_BAR_SEGMENTS + 95) / 96);
}

static void hud_set_bar(Sprite **segments, u8 count, u16 baseX, u8 reverse)
{
	u8 i;
	for(i = 0; i < HUD_BAR_SEGMENTS; i++)
	{
		Sprite *sprite = segments[i];
		if(!sprite){ continue; }
		if(i < count)
		{
			u16 x = reverse ? (u16)(baseX + (HUD_BAR_SEGMENTS - 1 - i) * HUD_BAR_STEP)
			                : (u16)(baseX + i * HUD_BAR_STEP);
			SPR_setPosition(sprite, x, HUD_BAR_Y);
			SPR_setVisibility(sprite, VISIBLE);
		}
		else
		{
			SPR_setVisibility(sprite, HIDDEN);
		}
	}
}

void hud_window_init(void)
{
	u16 attr;
	u8 i;
	const u16 autoFlags = SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE | SPR_FLAG_AUTO_VISIBILITY |
		SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD;
	const u16 sharedFlags = SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE | SPR_FLAG_AUTO_VISIBILITY;

	memset(sHudP1Segments, 0, sizeof(sHudP1Segments));
	memset(sHudP2Segments, 0, sizeof(sHudP2Segments));
	sHudSegmentTile = 0;
	sHudP1Segments[0] = SPR_addSpriteExSafe(&spr_hud_energy_segment, HUD_P1_X, HUD_BAR_Y,
		TILE_ATTR(PAL1, FALSE, FALSE, FALSE), autoFlags);
	if(!sHudP1Segments[0]){ SYS_die("HUD segment sprite allocation failed"); return; }
	sHudSegmentTile = (u16)(sHudP1Segments[0]->attribut & 0x07FF);
	for(i = 1; i < HUD_BAR_SEGMENTS; i++)
	{
		attr = TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, sHudSegmentTile);
		sHudP1Segments[i] = SPR_addSpriteExSafe(&spr_hud_energy_segment, HUD_P1_X, HUD_BAR_Y, attr, sharedFlags);
		sHudP2Segments[i] = SPR_addSpriteExSafe(&spr_hud_energy_segment, HUD_P2_X, HUD_BAR_Y, attr, sharedFlags);
		if(!sHudP1Segments[i] || !sHudP2Segments[i]){ SYS_die("HUD segment sprite allocation failed"); return; }
	}
	attr = TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, sHudSegmentTile);
	sHudP2Segments[0] = SPR_addSpriteExSafe(&spr_hud_energy_segment, HUD_P2_X, HUD_BAR_Y, attr, sharedFlags);
	if(!sHudP2Segments[0]){ SYS_die("HUD segment sprite allocation failed"); return; }
	for(i = 0; i < HUD_BAR_SEGMENTS; i++)
	{
		if(sHudP1Segments[i]){ SPR_setDepth(sHudP1Segments[i], 3); SPR_setVisibility(sHudP1Segments[i], HIDDEN); }
		if(sHudP2Segments[i]){ SPR_setDepth(sHudP2Segments[i], 3); SPR_setVisibility(sHudP2Segments[i], HIDDEN); }
	}

	sHudClockSpriteL = SPR_addSpriteExSafe(&spr_hud_clock_digit, HUD_CLK_L_X, HUD_CLK_Y,
		TILE_ATTR(PAL1, FALSE, FALSE, FALSE), autoFlags);
	if(!sHudClockSpriteL){ SYS_die("HUD clock sprite allocation failed"); return; }
	sHudClockSpriteR = SPR_addSpriteExSafe(&spr_hud_clock_digit, HUD_CLK_R_X, HUD_CLK_Y,
		TILE_ATTR(PAL1, FALSE, FALSE, FALSE), autoFlags);
	if(!sHudClockSpriteR){ SYS_die("HUD clock sprite allocation failed"); return; }
	if(sHudClockSpriteL){ SPR_setDepth(sHudClockSpriteL, 3); }
	if(sHudClockSpriteR){ SPR_setDepth(sHudClockSpriteR, 3); }
	sHudClockDigitL = -1;
	sHudClockDigitR = -1;
	sHudWindowActive = 1;
	hud_window_update();
	hud_window_draw_clock();
}

void hud_window_update(void)
{
	if(!sHudWindowActive){ return; }
	hud_set_bar(sHudP1Segments, hud_segment_count(P[1].energiaBase), HUD_P1_X, FALSE);
	hud_set_bar(sHudP2Segments, hud_segment_count(P[2].energiaBase), HUD_P2_X, TRUE);
}

void hud_window_off(void)
{
	u8 i;
	hud_message_clear();
	for(i = 0; i < HUD_BAR_SEGMENTS; i++)
	{
		if(sHudP1Segments[i]){ SPR_releaseSprite(sHudP1Segments[i]); sHudP1Segments[i] = NULL; }
		if(sHudP2Segments[i]){ SPR_releaseSprite(sHudP2Segments[i]); sHudP2Segments[i] = NULL; }
	}
	if(sHudClockSpriteL){ SPR_releaseSprite(sHudClockSpriteL); sHudClockSpriteL = NULL; }
	if(sHudClockSpriteR){ SPR_releaseSprite(sHudClockSpriteR); sHudClockSpriteR = NULL; }
	sHudWindowActive = 0;
	sHudClockDigitL = -1;
	sHudClockDigitR = -1;
	sHudSegmentTile = 0;
}

/* Atlas cells are 16x16 (2x2 tiles), 36 cells across in ROW order.
   PAL1 belongs to the HUD; fighter palettes can change independently. */
static void hud_message_line(const char *str, u16 row)
{
	u16 col = (40 - strlen(str) * 2) / 2;
	while(*str)
	{
		u8 ch = *str++;
		u16 glyph;
		u16 base;
		if(ch >= 'A' && ch <= 'Z'){ glyph = ch - 'A'; }
		else if(ch >= '0' && ch <= '9'){ glyph = 26 + ch - '0'; }
		else { col += 2; continue; }
		base = sHudMessageTileBase + glyph * 2;
		sHudMessageMap[(row-HUD_MESSAGE_ROW)*40+col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base);
		sHudMessageMap[(row-HUD_MESSAGE_ROW)*40+col+1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+1);
		sHudMessageMap[(row-HUD_MESSAGE_ROW+1)*40+col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+72);
		sHudMessageMap[(row-HUD_MESSAGE_ROW+1)*40+col+1] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, base+73);
		col += 2;
	}
}

void hud_message_clear(void)
{
	memset(sHudMessageMap, 0, sizeof(sHudMessageMap));
	VDP_setTileMapDataRect(BG_A, sHudMessageMap, 0, HUD_MESSAGE_ROW, 40, HUD_MESSAGE_ROWS, 40, DMA_QUEUE_COPY);
	sHudMessage = 0;
}

void hud_message_update(void)
{
	u8 message = 0;
	if(gRoom == SCENE_AFTER_MATCH){ message = (gWinnerID == 1) ? 7 : 8; }
	else if(gPauseKoTimer > 0 && gPauseKoTimer < 330){ message = 3; }
	else if(P[1].state == 611 || P[1].state == 612){ message = 4; }
	else if(P[2].state == 611 || P[2].state == 612){ message = 5; }
	else if(P[1].state == 615 && P[2].state == 615){ message = 6; }
	else if(gFrames < 180){ message = 1; }
	else if(gFrames < 300){ message = 2; }
	if(message == sHudMessage){ return; }
	memset(sHudMessageMap, 0, sizeof(sHudMessageMap));
	sHudMessage = message;
	if(!message){ hud_message_clear(); return; }
	{
		u16 row, col;
		for(row=0; row < ((message>=7) ? HUD_MESSAGE_ROWS : 2); row++)
			for(col=2; col<38; col++)
				sHudMessageMap[row*40+col] = TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, sHudBlackTile);
	}
	if(message == 1){
		char roundText[] = "ROUND 0";
		roundText[6] = '0' + ((gRound > 9) ? 9 : gRound);
		hud_message_line(roundText, HUD_MESSAGE_ROW);
	}
	if(message == 2){ hud_message_line("FIGHT", HUD_MESSAGE_ROW); }
	if(message == 3){ hud_message_line("KO", HUD_MESSAGE_ROW); }
	if(message == 4 || message == 7){ hud_message_line("PLAYER 1 WINS", HUD_MESSAGE_ROW); }
	if(message == 5 || message == 8){ hud_message_line("PLAYER 2 WINS", HUD_MESSAGE_ROW); }
	if(message == 6){ hud_message_line("DRAW", HUD_MESSAGE_ROW); }
	if(message >= 7){
		hud_message_line("A REMATCH", HUD_MESSAGE_ROW+2);
		hud_message_line("START SELECT", HUD_MESSAGE_ROW+4);
	}
	VDP_setTileMapDataRect(BG_A, sHudMessageMap, 0, HUD_MESSAGE_ROW, 40, HUD_MESSAGE_ROWS, 40, DMA_QUEUE_COPY);
}

void FUNCAO_BARRAS_DE_ENERGIA()
{
	
	for(i=1; i<=2; i++)
	{
		if( P[i].energia != P[i].energiaBase )
		{ 
			if(P[i].energia > P[i].energiaBase){ P[i].energia--; } //decrementa a 'energia' aos poucos, até igualar a 'energiaBase'
			if(P[i].energia < P[i].energiaBase){ P[i].energia++; } //incrementa a 'energia' aos poucos, até igualar a 'energiaBase'
		} 
		
		/* P1 and P2 yellow are WINDOW tiles. Red lag sprites not spawned. */
		
		//Exibe a barra de especial, e fica piscando, caso seja == 32
		/*
		if(P[i].energiaSP<32)
		{
			SPR_setAnimAndFrame(GE[6+i].sprite, 0, P[i].energiaSP);
		}else{
			if(gPing2==1){
				SPR_setAnimAndFrame(GE[6+i].sprite, 0, 32);
			}else{
				SPR_setAnimAndFrame(GE[6+i].sprite, 0, 33);
			}
		}
		*/
		
	}

	hud_window_update();
	
	//if(P[1].energiaSP>=32){ SPR_setVisibility(GE[ 9].sprite, VISIBLE); }else{ SPR_setVisibility(GE[ 9].sprite, HIDDEN); }
	//if(P[2].energiaSP>=32){ SPR_setVisibility(GE[10].sprite, VISIBLE); }else{ SPR_setVisibility(GE[10].sprite, HIDDEN); }
	
}

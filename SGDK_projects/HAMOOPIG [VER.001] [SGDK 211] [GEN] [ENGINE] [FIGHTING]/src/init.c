#include <genesis.h>
#include "init.h"
#include "globals.h"
#include "timing.h"
#include "gfx.h"
#include "sprite.h"
#include "ken.h"
#include "hud_gfx.h"
#include "hud.h"
#include "player.h"
#include "graphics.h"

void FUNCAO_INICIALIZACAO()
{
	gPodeMover=0;
	doubleHitStep=0;
	gPauseSystem=0;
	gPauseKoTimer=0;
	gResultTimer=0;
	hud_message_clear();
	Spark1_countDown=0;
	Spark2_countDown=0;
	if(Spark[1]){ SPR_releaseSprite(Spark[1]); Spark[1]=NULL; }
	if(Spark[2]){ SPR_releaseSprite(Spark[2]); Spark[2]=NULL; }
	
	//BG_B
	gInd_tileset=1; //Antes de carregar o Background, definir o ponto de inicio de carregamento na VRAM
	{
		u16 stageTiles = (gBG_Choice == 1) ? gfx_showdown.tileset->numTile : gfx_bgb2.tileset->numTile;
		u16 hudTiles = ts_hud_message_font.numTile + 1;
		if(gInd_tileset + stageTiles + hudTiles > TILE_SPRITE_INDEX)
		{
			SYS_die("Fight tiles overlap sprite VRAM");
		}
	}
	
	// Showdown park (compare_flat IMAGE). Extra 32px height is jump V headroom.
	if(gBG_Choice==1){ 
		gBG_Width = 512;
		gBG_Height = 256;
		gScrollValue=-(gBG_Width-320)/2;
		VDP_loadTileSet(gfx_showdown.tileset,gInd_tileset,DMA); 
		VDP_setTileMapEx(BG_B,gfx_showdown.tilemap,TILE_ATTR_FULL(PAL0,0,FALSE,FALSE,gInd_tileset),0,0,0,0,gBG_Width/8,gBG_Height/8,DMA_QUEUE);
		PAL_setPalette(PAL0, gfx_showdown.palette->data, CPU);
		gInd_tileset += gfx_showdown.tileset->numTile;
		camPosX = (s16)((gBG_Width - 320) / 2);
		camPosXanterior = -1;
		camPosY = 0;
		camPosYanterior = -1;
		VDP_setHorizontalScroll(BG_B, -camPosX);
		VDP_setVerticalScroll(BG_B, (s16)(gBG_Height - 224));
	} 
	
	//Load the tileset 'BGB2'
	if(gBG_Choice==2){ 
		gBG_Width = 512;
		gBG_Height = 224;
		gScrollValue=-(gBG_Width-320)/2;
		VDP_loadTileSet(gfx_bgb2.tileset,gInd_tileset,DMA); 
		VDP_setTileMapEx(BG_B,gfx_bgb2.tilemap,TILE_ATTR_FULL(PAL0,0,FALSE,FALSE,gInd_tileset),0,0,0,0,gBG_Width/8,28,DMA_QUEUE);
		PAL_setPalette(PAL0, gfx_bgb2.palette->data, CPU);
		gInd_tileset += gfx_bgb2.tileset->numTile;
	}

	/* Runtime ceiling is TILE_SPRITE_INDEX, not a hard-coded 1532. */
	hud_window_load(); 
	
	//load palette HUD in PAL1, GFX load AFTER round intro...
	//PALETA DA HUD!!!
	PAL_setPalette(PAL1, spr_hud_energy_y.palette->data, CPU); 
	VDP_setBackgroundColor(16 + 11); /* HUD black, independent of stage color 0. */
	
	/* gBG_Height ja esta definido acima, entao aqui e o primeiro ponto em que
	   da para decidir se 240 linhas cabem neste cenario. A funcao tambem
	   recalcula gAlturaPiso, que depende da altura de tela. */
	gScreenH = 0; /* forca a reavaliacao mesmo que a altura nao va mudar */
	FUNCAO_SCREEN_HEIGHT_APPLY();

	for(i=1; i<=2; i++) {
		memset(P[i].key_JOY_status, KEY_FREE, sizeof(P[i].key_JOY_status));
		memset(P[i].key_JOY_countdown, 0, sizeof(P[i].key_JOY_countdown));
		memset(P[i].joyDirTimer, 0, sizeof(P[i].joyDirTimer));
		memset(P[i].inputArray, 0, sizeof(P[i].inputArray));
		if(P[i].fball.spriteFBall){ SPR_releaseSprite(P[i].fball.spriteFBall); }
		P[i].fball.spriteFBall=NULL;
		P[i].fball.active=0;
		P[i].fball.countDown=0;
		P[i].fball.x=-250;
		P[i].fball.y=-250;
		P[i].hSpeed=0;
		P[i].impulsoY=0;
		P[i].gravidadeY=0;
		P[i].puloTimer=0;
		P[i].shotJump=FALSE;
		P[i].control=TRUE;
		P[i].setup=FALSE;
	}
	
	//P1
	P[1].energia = 96;
	P[1].energiaBase = 96;
	P[1].energiaSP = 0;
	P[1].rageTimerCountdown=RAGETIMER;
	P[1].wins = 0;
	P[1].x = (gBG_Width/2)-80; //P[1].x = (320/4);
	P[1].y = gAlturaPiso;
	P[1].hitPause = 0;
	P[1].direcao = 1;
	P[1].state = 610; //610, Intro State!
	P[1].puloTimer = 0;
	P[1].dataMBox[0] = -BODYSPACE;
	P[1].dataMBox[1] = -60;
	P[1].dataMBox[2] = +BODYSPACE;
	P[1].dataMBox[3] = - 1;
	P[1].paleta = PAL2;
	P[1].cicloInteracoesGravidade = CIGD; //CIGD eh uma definicao global! ver inicio do codigo
	P[1].cicloInteracoesGravidadeCont = 0;
	P[1].fball.active = 0;
	P[1].bufferSpecial = 0;
	P[1].hitCounter = 0;
	P[1].stateMoveType = 0;
	
	//P2
	P[2].energia = 96;
	P[2].energiaBase = 96;
	P[2].energiaSP = 0;
	P[2].rageTimerCountdown=RAGETIMER;
	P[2].wins = 0;
	P[2].x = (gBG_Width/2)+80; //P[2].x = (320/4)*3;
	P[2].y = gAlturaPiso;
	P[2].hitPause = 0;
	P[2].direcao = -1;
	P[2].state = 610; //610, Intro State!
	P[2].puloTimer = 0;
	P[2].dataMBox[0] = -BODYSPACE;
	P[2].dataMBox[1] = -60;
	P[2].dataMBox[2] = +BODYSPACE;
	P[2].dataMBox[3] = - 1;
	P[2].paleta = PAL3;
	P[2].cicloInteracoesGravidade = CIGD; //CIGD eh uma definicao global! ver inicio do codigo
	P[2].cicloInteracoesGravidadeCont = 0;
	P[2].fball.active = 0;
	P[2].bufferSpecial = 0;
	P[2].hitCounter = 0;
	P[2].stateMoveType = 0;


	//Para verificar a vantagem ou desvantagem em relacao aos frames
	frameAdvCounterP1 = 0;
	lastFrameAdvCounterP1 = 0;
	frameAdvCounterP2 = 0;
	lastFrameAdvCounterP2 = 0;

	if(P[1].sombra){ SPR_releaseSprite(P[1].sombra); P[1].sombra = NULL; }
	if(P[2].sombra){ SPR_releaseSprite(P[2].sombra); P[2].sombra = NULL; }
	P[1].sombra = SPR_addSpriteExSafe(&spr_sombra, P[1].x-32, P[1].y-2, TILE_ATTR(PAL1, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	if(gSombraStyle==2)
	{
		P[2].sombra = SPR_addSpriteExSafe(&spr_sombra, P[2].x-32, P[2].y-2, TILE_ATTR(PAL1, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	}
	
	//reset Graphic Elements
	if (GE[ 1].sprite){ SPR_releaseSprite(GE[ 1].sprite); GE[ 1].sprite = NULL; }
	if (GE[ 2].sprite){ SPR_releaseSprite(GE[ 2].sprite); GE[ 2].sprite = NULL; }
	if (GE[ 3].sprite){ SPR_releaseSprite(GE[ 3].sprite); GE[ 3].sprite = NULL; }
	if (GE[ 4].sprite){ SPR_releaseSprite(GE[ 4].sprite); GE[ 4].sprite = NULL; }
	if (GE[ 5].sprite){ SPR_releaseSprite(GE[ 5].sprite); GE[ 5].sprite = NULL; }
	if (GE[ 6].sprite){ SPR_releaseSprite(GE[ 6].sprite); GE[ 6].sprite = NULL; }
	if (GE[ 7].sprite){ SPR_releaseSprite(GE[ 7].sprite); GE[ 7].sprite = NULL; }
	if (GE[ 8].sprite){ SPR_releaseSprite(GE[ 8].sprite); GE[ 8].sprite = NULL; }
	if (GE[ 9].sprite){ SPR_releaseSprite(GE[ 9].sprite); GE[ 9].sprite = NULL; }
	if (GE[10].sprite){ SPR_releaseSprite(GE[10].sprite); GE[10].sprite = NULL; }
	if (GE[11].sprite){ SPR_releaseSprite(GE[11].sprite); GE[11].sprite = NULL; }
	if (GE[12].sprite){ SPR_releaseSprite(GE[12].sprite); GE[12].sprite = NULL; }
	if (GE[13].sprite){ SPR_releaseSprite(GE[13].sprite); GE[13].sprite = NULL; }
	if (GE[14].sprite){ SPR_releaseSprite(GE[14].sprite); GE[14].sprite = NULL; }
	if (GE[15].sprite){ SPR_releaseSprite(GE[15].sprite); GE[15].sprite = NULL; }
	if (GE[16].sprite){ SPR_releaseSprite(GE[16].sprite); GE[16].sprite = NULL; }
	if (GE[17].sprite){ SPR_releaseSprite(GE[17].sprite); GE[17].sprite = NULL; }
	if (GE[18].sprite){ SPR_releaseSprite(GE[18].sprite); GE[18].sprite = NULL; }
	if (GE[19].sprite){ SPR_releaseSprite(GE[19].sprite); GE[19].sprite = NULL; }
	if (GE[20].sprite){ SPR_releaseSprite(GE[20].sprite); GE[20].sprite = NULL; }
	
	gClockTimer=(s8)TIMING_roundClockTicks(); //NORMAL: 60 ticks = 1 segundo real
	gClockLTimer=9; //Digito esquerdo do Relogio
	gClockRTimer=9; //Digito direito do Relogio
	gRound=1;       //Round Number
	if(ClockL){ SPR_releaseSprite(ClockL); ClockL = NULL; }
	if(ClockR){ SPR_releaseSprite(ClockR); ClockR = NULL; }

	/* HUD spawned after fighters (see below) so AUTO_VRAM lands in leftover pool. */
	
	if(RELEASE==0)
	{
		/* Sem SPR_setVRAMTileIndex: fixar o indice NAO carrega os tiles, e
		   ninguem escreve spr_rect_bb/hb em 1453/1454 -- os cantos saiam como
		   blocos pretos.  Medido no BlastEm.  Auto-alocar faz o upload e custa
		   16 tiles (cada rect e 1x1). */
		Rect1BB1_Q1 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect1BB1_Q2 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect1BB1_Q3 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect1BB1_Q4 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect1HB1_Q1 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect1HB1_Q2 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect1HB1_Q3 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect1HB1_Q4 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		
		Rect2BB1_Q1 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect2BB1_Q2 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect2BB1_Q3 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect2BB1_Q4 = SPR_addSprite(&spr_rect_bb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect2HB1_Q1 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect2HB1_Q2 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect2HB1_Q3 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		Rect2HB1_Q4 = SPR_addSprite(&spr_rect_hb, -8, -8, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		
		SPR_setHFlip(Rect1BB1_Q2, TRUE);
		SPR_setVFlip(Rect1BB1_Q3, TRUE);
		SPR_setHFlip(Rect1BB1_Q4, TRUE); SPR_setVFlip(Rect1BB1_Q4, TRUE);
		SPR_setHFlip(Rect1HB1_Q2, TRUE);
		SPR_setVFlip(Rect1HB1_Q3, TRUE);
		SPR_setHFlip(Rect1HB1_Q4, TRUE); SPR_setVFlip(Rect1HB1_Q4, TRUE);
		
		SPR_setHFlip(Rect2BB1_Q2, TRUE);
		SPR_setVFlip(Rect2BB1_Q3, TRUE);
		SPR_setHFlip(Rect2BB1_Q4, TRUE); SPR_setVFlip(Rect2BB1_Q4, TRUE);
		SPR_setHFlip(Rect2HB1_Q2, TRUE);
		SPR_setVFlip(Rect2HB1_Q3, TRUE);
		SPR_setHFlip(Rect2HB1_Q4, TRUE); SPR_setVFlip(Rect2HB1_Q4, TRUE);
		SPR_setVisibility(Rect1BB1_Q1, HIDDEN); SPR_setVisibility(Rect1BB1_Q2, HIDDEN);
		SPR_setVisibility(Rect1BB1_Q3, HIDDEN); SPR_setVisibility(Rect1BB1_Q4, HIDDEN);
		SPR_setVisibility(Rect1HB1_Q1, HIDDEN); SPR_setVisibility(Rect1HB1_Q2, HIDDEN);
		SPR_setVisibility(Rect1HB1_Q3, HIDDEN); SPR_setVisibility(Rect1HB1_Q4, HIDDEN);
		SPR_setVisibility(Rect2BB1_Q1, HIDDEN); SPR_setVisibility(Rect2BB1_Q2, HIDDEN);
		SPR_setVisibility(Rect2BB1_Q3, HIDDEN); SPR_setVisibility(Rect2BB1_Q4, HIDDEN);
		SPR_setVisibility(Rect2HB1_Q1, HIDDEN); SPR_setVisibility(Rect2HB1_Q2, HIDDEN);
		SPR_setVisibility(Rect2HB1_Q3, HIDDEN); SPR_setVisibility(Rect2HB1_Q4, HIDDEN);
		
		SPR_setDepth(Rect1BB1_Q1, 1);
		SPR_setDepth(Rect1BB1_Q2, 1);
		SPR_setDepth(Rect1BB1_Q3, 1);
		SPR_setDepth(Rect1BB1_Q4, 1);
		SPR_setDepth(Rect1HB1_Q1, 1);
		SPR_setDepth(Rect1HB1_Q2, 1);
		SPR_setDepth(Rect1HB1_Q3, 1);
		SPR_setDepth(Rect1HB1_Q4, 1);
		
		SPR_setDepth(Rect2BB1_Q1, 1);
		SPR_setDepth(Rect2BB1_Q2, 1);
		SPR_setDepth(Rect2BB1_Q3, 1);
		SPR_setDepth(Rect2BB1_Q4, 1);
		SPR_setDepth(Rect2HB1_Q1, 1);
		SPR_setDepth(Rect2HB1_Q2, 1);
		SPR_setDepth(Rect2HB1_Q3, 1);
		SPR_setDepth(Rect2HB1_Q4, 1);
	}
	
	//Intro State, Player Start
	//P[1].sprite = SPR_addSpriteExSafe(&spr_point, P[1].x-P[1].axisX, P[1].y-P[1].axisY, TILE_ATTR(PAL2, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	//P[2].sprite = SPR_addSpriteExSafe(&spr_point, P[2].x-P[2].axisX, P[2].y-P[2].axisY, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	PLAYER_STATE(1,100);
	PLAYER_STATE(2,100);
	
	if(P[2].sprite){ SPR_setHFlip(P[2].sprite, TRUE); }
	
	//Define a paleta dos players...
	if(cursorP1ColorChoice){ P[1].palID=cursorP1ColorChoice; }
	if(cursorP2ColorChoice){ P[2].palID=cursorP2ColorChoice; }
	if(P[1].palID==0){ P[1].palID=1; }
	if(P[2].palID==0){ P[2].palID=1; } 
	
	if( P[1].id==P[2].id && P[1].palID==P[2].palID)
	{
		//se ambos os players forem iguais e com a mesma paleta...
		P[1].palID=1; //Por padrao, P1 fica com a paleta 1
		P[2].palID=2; //Por padrao, P2 fica com a paleta 2 'cor alternativa'
	}
	
	FUNCAO_APPLY_FIGHTER_PALETTE(1);
	FUNCAO_APPLY_FIGHTER_PALETTE(2);

	/* P1/P2 bars use compact repeated sprites; KO stays sprite. */
	GE[3].sprite = NULL;
	GE[4].sprite = NULL;
	GE[5].sprite = NULL;
	GE[6].sprite = NULL;
	GE[7].sprite = SPR_addSpriteExSafe(&spr_hud_ko, 136, 2, TILE_ATTR(PAL1, FALSE, FALSE, FALSE), SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD);
	if(GE[7].sprite){ SPR_setDepth(GE[7].sprite, 4); }
	hud_window_init();
	
	//AXIS
	if(RELEASE==0)
	{
		if (GE[1].sprite){ SPR_releaseSprite(GE[1].sprite); GE[1].sprite = NULL; }
		if (GE[2].sprite){ SPR_releaseSprite(GE[2].sprite); GE[2].sprite = NULL; }
		GE[1].sprite = SPR_addSprite(&spr_point, P[1].x-4, P[1].y-5, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		GE[2].sprite = SPR_addSprite(&spr_point, P[2].x-4, P[2].y-5, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
		SPR_setVRAMTileIndex(GE[1].sprite, 1455); //define uma posicao especifica para o GFX na VRAM
		SPR_setVRAMTileIndex(GE[2].sprite, 1455); //define uma posicao especifica para o GFX na VRAM
		SPR_setVisibility(GE[1].sprite, HIDDEN);
		SPR_setVisibility(GE[2].sprite, HIDDEN);
		
		//DEPTH
		SPR_setDepth(GE[1].sprite, 1 );
		SPR_setDepth(GE[2].sprite, 2 );
	}
	
	//depth 3 e 4 reservados
	if (P[1].sprite){ SPR_setDepth(P[1].sprite,  5 ); } 
	if (P[2].sprite){ SPR_setDepth(P[2].sprite,  6 ); } 
	//depth 7 e 8 reservados
	if(P[1].sombra){ SPR_setDepth(P[1].sombra, 98 ); }
	if(gSombraStyle==2 && P[2].sombra){ SPR_setDepth(P[2].sombra, 99 ); }
}

void FUNCAO_ROUND_INIT()
{
	gPodeMover=1;
}

void FUNCAO_ROUND_RESTART()
{
	u8 p1Wins = P[1].wins;
	u8 p2Wins = P[2].wins;
	u8 nextRound = (u8)(gRound + 1);
	/* Wait for a visible result and the actual landing, independently of
	   the winner's authored animation duration (Musgo idle is only 32 ticks). */
	if(gRoom == 10)
	{
		if(gResultTimer < 180){ return; }
		if(P[1].energiaBase == 0 || P[2].energiaBase == 0)
		{
			if(gPauseKoTimer < 440){ return; }
			if(P[1].energiaBase == 0 && P[1].state != 570){ return; }
			if(P[2].energiaBase == 0 && P[2].state != 570){ return; }
		}
	}

	gPodeMover=0;
	gPauseSystem=0;
	gPauseKoTimer=0;
	if(gRoom==10 && (p1Wins>=ROUNDS_TO_WIN || p2Wins>=ROUNDS_TO_WIN))
	{
		gWinnerID = (p1Wins>=ROUNDS_TO_WIN) ? 1 : 2;
		gLoseID = (gWinnerID==1) ? 2 : 1;
		gContinueOption = FALSE;
		gRoom=11;
		gFrames=1;
		return;
	}
	if(gRoom==10)
	{
		/* Leave the animation owner first. The reset is committed by main
		   after the animation call returns, never inside its player loop. */
		gRoom=12;
		gFrames=0;
		return;
	}
	if(gRoom!=12){ return; }

	/* Full scene-owned reset: clears projectiles, hit pause, input buffers,
	   positions, health, clock, HUD and sprite state symmetrically. */
	FUNCAO_INICIALIZACAO();
	P[1].wins=p1Wins;
	P[2].wins=p2Wins;
	gRound=nextRound;
	gRoom=10;
	gFrames=1;
}

void CLEAR_VDP()
{
	SYS_disableInts();
	/* Release HUD-owned sprite handles before SPR_reset invalidates the pool. */
	hud_window_off();
	 SPR_reset();
	 /* SPR_reset invalidates every handle owned by the previous room. */
	 for(i=1; i<=2; i++)
	 {
		P[i].sprite = NULL;
		P[i].sombra = NULL;
		P[i].fball.spriteFBall = NULL;
		P[i].fball.active = 0;
	 }
	 for(i=1; i<25; i++){ GE[i].sprite = NULL; }
	 Spark[1] = NULL;
	 Spark[2] = NULL;
	 ClockL = NULL;
	 ClockR = NULL;
	 HUD_Lethers = NULL;
	 Rect1BB1_Q1 = NULL; Rect1BB1_Q2 = NULL; Rect1BB1_Q3 = NULL; Rect1BB1_Q4 = NULL;
	 Rect1HB1_Q1 = NULL; Rect1HB1_Q2 = NULL; Rect1HB1_Q3 = NULL; Rect1HB1_Q4 = NULL;
	 Rect2BB1_Q1 = NULL; Rect2BB1_Q2 = NULL; Rect2BB1_Q3 = NULL; Rect2BB1_Q4 = NULL;
	 Rect2HB1_Q1 = NULL; Rect2HB1_Q2 = NULL; Rect2HB1_Q3 = NULL; Rect2HB1_Q4 = NULL;
	 //VDP_resetSprites();
	 //VDP_releaseAllSprites();
	 //SPR_defragVRAM();
	 VDP_clearPlane(BG_A, TRUE);
	 VDP_clearPlane(BG_B, TRUE);	
	 VDP_setTextPlane(BG_A);  
	 VDP_setHorizontalScroll(BG_B, 0); 
	 VDP_setVerticalScroll(BG_B, 0); 
	 VDP_setHorizontalScroll(BG_A, 0); 
	 VDP_setVerticalScroll(BG_A, 0);
	 VDP_setBackgroundColor(0);
	 VDP_resetScreen();
	 //PAL_setPaletteColors(0, (u16*) palette_black, CPU);
	SYS_enableInts();
	gInd_tileset=0;
}

//EOF - END OF FILE; by GAMEDEVBOSS 2015-2022

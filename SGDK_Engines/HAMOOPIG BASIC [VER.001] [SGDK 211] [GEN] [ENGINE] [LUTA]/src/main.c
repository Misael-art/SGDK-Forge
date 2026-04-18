/*********************************************************
*** HAMOOPI(G) by GameDevBoss (Daniel Moura) 2015-2022 ***
*********************************************************/

#include <genesis.h>
#include "sprite.h"
#include "gfx.h"
#include "sound.h"

// Esta versao curta funciona como um recorte da engine HAMOOPIG.
// Ela e util para entender a base antes de abrir as versoes maiores:
// setup do video, estado dos personagens e atualizacao simples de animacao.

//--- FUNCOES ---//
void FUNCAO_INICIALIZACAO();
void PLAYER_STATE(int Player, int State);
void FUNCAO_ANIMACAO();

//--- VARIAVEIS ---//
u32 frames=-1;
u8 i;            //variavel de uso geral
char str[64];    //variavel para armazenar textos, usada no debug
u16 ind_tileset; //variavel utilizada para carregar dados de background
u8 ping2 = 0;    //variavel que alterna entre 0 e 1 constantemente

struct PlayerDEF {
	Sprite* sprite;      //Sprite do Player 
	Sprite* sombra;      //Sprite (sombra) do Player 
	u16 state;           //Controla o estado (animacao) do Player
	u8  id;              //Identificacao numerica do personagem selecionado
	u16 x;               //Posicao X do Player
	u16 y;               //Posicao Y do Player
	u8  axisX;           //Posicao X do Ponto Pivot
	u8  axisY;           //Posicao Y do Ponto Pivot
	s8  direcao;         //Direcao para qual o Player esta olhando (1 ; -1)
	u16 frameTimeAtual;  //Tempo atual do frame de animacao corrente
	u16 frameTimeTotal;  //Tempo total do frame de animacao corrente
	u16 animFrame;       //Frame de animacao atual
	u16 animFrameTotal;  //Qtde total de frames deste estado (animacao)
	u8  hitPause;        //Tempo de congelamento apos o Hit
	u16 dataAnim[60];    //Total de frames disponiveis para cada estado (animacao)
}; struct PlayerDEF P[4];

struct GraphicElementDEF {
	Sprite* sprite;      //Sprite do Graphic Element
}; struct GraphicElementDEF GE[2];

// Neste prototipo o fluxo e direto: inicializa uma vez, atualiza a animacao
// dos lutadores e fecha o frame com SPR_update + VBlank.
int main(u16 hard)
{
    //inicializacao da VDP (Video Display Processor)
	SYS_disableInts();
	 VDP_init();                    //Inicializa a VDP (Video Display Processor)
	 VDP_setScreenWidth320();       //Resolucao padrao de 320x224 (Largura)
	 VDP_setScreenHeight224();      //Resolucao padrao de 320x224 (Altura)
	 VDP_setPlaneSize(64,32,TRUE);  //Recomendado para BGs grandes
	 VDP_setTextPlane(BG_A);        //Textos serao desenhados no BG_A
	 VDP_setTextPalette(PAL0);      //Textos serao desenhados com a ultima cor da PAL0
     SPR_init();       //SPR_init()
	 VDP_setBackgroundColor(0);     //Range 0-63 //4 Paletas de 16 cores = 64 cores
	SYS_enableInts();
	
    while(TRUE)
    {
        frames++; 
		if(frames==0){ FUNCAO_INICIALIZACAO(); } //Inicializacao
		if(ping2 == 1){ ping2 =-1; } ping2++; //var 'ping2' variacao: 0;1
		
		// A animacao aqui roda separada de input e fisica para deixar o exemplo enxuto.
		FUNCAO_ANIMACAO();
		
		//ESPECIFICO DO SAMURAI SHODOW. ESPADA PISCANDO E SOMBRA
		if(ping2==0)
		{ 
			PAL_setPalette(PAL2, spr_haohmaru_pal1.palette ->data, DMA); //P1
			SPR_setVisibility(P[1].sombra, VISIBLE);
			PAL_setPalette(PAL3, spr_haohmaru_pal2.palette ->data, DMA); //P2
			SPR_setVisibility(P[2].sombra, HIDDEN);
		}
		if(ping2==1)
		{ 
			PAL_setPalette(PAL2, spr_haohmaru_pal1b.palette->data, DMA); //P1
			SPR_setVisibility(P[1].sombra, HIDDEN);
			PAL_setPalette(PAL3, spr_haohmaru_pal2b.palette->data, DMA); //P2
			SPR_setVisibility(P[2].sombra, VISIBLE);
		}
		
		
		//--- DEBUG ---//
		
		VDP_drawText("HAMOOPIG ENGINE", 1, 1);
		sprintf(str, "P1-> %i,%i S:%i T:%i/%i F:%i/%i    ", P[1].x, P[1].y, P[1].state, P[1].frameTimeAtual, P[1].frameTimeTotal, P[1].animFrame, P[1].animFrameTotal ); 
		VDP_drawText(str, 1, 2);	

		
		//--- FINALIZACOES ---//
		
		// Atualiza (desenha) os sprites
		SPR_update();
        // wait for screen refresh and do all SGDK VBlank tasks
        SYS_doVBlankProcess();
    }

    return 0;
}

//--- FUNCOES ---//

void PLAYER_STATE(int Player, int State)
{
	SPR_releaseSprite(P[Player].sprite);
	P[Player].animFrame = 1;
	P[Player].frameTimeAtual = 1;
	P[Player].state = State;
	
	//valor para template vazio, (util para o dev)
	P[Player].dataAnim[1]   = 1;
	P[Player].animFrameTotal = 1;
	
	//--- HAOHMARU ---//
	if(P[Player].id==1)
	{
		
		if(State==100)
		{
			P[Player].axisX = (10*8)/2;
			P[Player].axisY = 15*8;
			P[Player].dataAnim[1]  = 8;
			P[Player].dataAnim[2]  = 7;
			P[Player].dataAnim[3]  = 7;
			P[Player].dataAnim[4]  = 7;
			P[Player].dataAnim[5]  = 7;
			P[Player].dataAnim[6]  = 7;
			P[Player].animFrameTotal = 6;
			
			if(Player==1){ P[1].sprite = SPR_addSpriteExSafe(&spr_haohmaru_100, P[1].x-P[1].axisX, P[1].y-P[1].axisY, TILE_ATTR(PAL2, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);  }
			if(Player==2){ P[2].sprite = SPR_addSpriteExSafe(&spr_haohmaru_100, P[2].x-P[2].axisX, P[2].y-P[2].axisY, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);  }
			
			u8 depth;
			if(Player==1){ depth=5; }
			if(Player==2){ depth=6; }
			SPR_setDepth(P[Player].sprite, depth);
		}
		
	}
	
	if(P[Player].direcao==1){SPR_setHFlip(P[Player].sprite, FALSE);}else{SPR_setHFlip(P[Player].sprite, TRUE);}
	SPR_setAnimAndFrame(P[Player].sprite, 0, P[Player].animFrame-1);
	P[Player].frameTimeTotal  = P[Player].dataAnim[1];
}

void FUNCAO_ANIMACAO()
{
	//CONTROLE DE ANIMACAO E END ANIMATION
	if(P[1].hitPause==0 && P[2].hitPause==0)
	{ 
		for(i=1; i<=2; i++)
		{
			P[i].frameTimeAtual++; 
			if(P[i].frameTimeAtual>P[i].frameTimeTotal) //hora de trocar o frame!
			{
				P[i].animFrame++;
				if(P[i].animFrame>P[i].animFrameTotal) //hora de trocar ou recarregar a animacao!
				{
					if(P[i].state==100){ PLAYER_STATE(i,100); }
				}
				P[i].frameTimeAtual=1;
				P[i].frameTimeTotal = P[i].dataAnim[P[i].animFrame];
				SPR_setAnimAndFrame(P[i].sprite, 0, P[i].animFrame-1);
			}
		}
	}
}

void FUNCAO_INICIALIZACAO()
{
	//BG_B
	ind_tileset=1; //Antes de carregar o Background, definir o ponto de inicio de carregamento na VRAM
	VDP_drawImageEx(BG_B, &gfx_bgb, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, ind_tileset), 0, 0, FALSE, TRUE);
	ind_tileset += gfx_bgb.tileset->numTile;
	PAL_setPalette(PAL0, gfx_bgb.palette->data, DMA);
	
	//P1
	P[1].id = 1;
	P[1].x = (320/4);
	P[1].y = (224/20)*19;
	P[1].axisX = (10*8)/2;
	P[1].axisY = 15*8;
	P[1].hitPause = 0;
	P[1].direcao = 1;
	P[1].state = 100;
	P[1].sprite = SPR_addSpriteExSafe(&spr_haohmaru_100, P[1].x-P[1].axisX, P[1].y-P[1].axisY, TILE_ATTR(PAL2, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);
	P[1].sombra = SPR_addSpriteExSafe(&spr_haohmaru_sombra, P[1].x-P[1].axisX, P[1].y-10, TILE_ATTR(PAL2, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);
	PAL_setPalette(PAL2, spr_haohmaru_pal1.palette->data, DMA);
	
	//P2
	P[2].id = 1;
	P[2].x = (320/4)*3;
	P[2].y = (224/20)*19;
	P[2].axisX = (10*8)/2;
	P[2].axisY = 15*8;
	P[2].hitPause = 0;
	P[2].direcao = -1;
	P[2].state = 100;
	P[2].sprite = SPR_addSpriteExSafe(&spr_haohmaru_100, P[2].x-P[2].axisX, P[2].y-P[2].axisY, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);
	P[2].sombra = SPR_addSpriteExSafe(&spr_haohmaru_sombra, P[2].x-P[1].axisX, P[2].y-10, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);
	PAL_setPalette(PAL3, spr_haohmaru_pal2.palette->data, DMA);
	SPR_setHFlip(P[2].sprite, TRUE);
	
	//AXIS
	GE[1].sprite = SPR_addSpriteExSafe(&spr_point, P[1].x-4, P[1].y-5, TILE_ATTR(PAL1, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);
	GE[2].sprite = SPR_addSpriteExSafe(&spr_point, P[2].x-4, P[2].y-5, TILE_ATTR(PAL1, FALSE, FALSE, FALSE), SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | SPR_FLAG_AUTO_VRAM_ALLOC);
	PAL_setPalette(PAL1, spr_point.palette->data, DMA);
	
	//DEPTH
	SPR_setDepth(GE[1].sprite, 1 );
	SPR_setDepth(GE[2].sprite, 2 );
	//depth 3 e 4 reservados
	SPR_setDepth(P[1].sprite,  5 );
	SPR_setDepth(P[2].sprite,  6 );
	//depth 7 e 8 reservados
	SPR_setDepth(P[1].sombra,  9 );
	SPR_setDepth(P[2].sombra, 10 );
}

//EOF - END OF FILE; by GAMEDEVBOSS 2022

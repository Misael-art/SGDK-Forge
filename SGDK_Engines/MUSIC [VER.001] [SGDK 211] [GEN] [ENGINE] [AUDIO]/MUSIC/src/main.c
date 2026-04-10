#include <genesis.h>
#include "sprite.h"
#include "gfx.h"
#include "sound.h"

// Este estudo demonstra um cenario musical com parallax em duas fases.
// O fluxo e simples: inicializar a fase uma vez, manter os backgrounds em scroll
// continuo e trocar de fase quando o jogador aperta START.

//variaveis
bool inicializacao=1; //ativa as funcoes de inicializacao
u16 contador_scrolling_bgA = 0; //contagem de pixels para mover o BG
u16 contador_scrolling_bgB = 0; //contagem de pixels para mover o BG
u16 frames=0;
u8 fase=1;
Sprite* FG1; //Sprite Foreground
Sprite* FG2; //Sprite Foreground
Sprite* P1CHAR; //Sprite do PERSONAGEM (CHARACTER)

// Como nao ha varias rooms, o controle principal fica na variavel "fase".
// Cada fase reaproveita a mesma ideia de setup, scroll e musica.
int main(u16 hard)
{
    // tudo que eh precedido de "//" eh um comentario
	// tire o "//" para habilitar um codigo...
	
	//VDP_drawText("SE QUISER COLOCAR UM TEXTO NA TELA...", 7, 12);
	
	//inicializacao da VDP (Video Display Processor)
	int ind_tileset=1;
	SYS_disableInts();
	VDP_init();
	VDP_setScreenWidth320();
	VDP_setScreenHeight224();
	SYS_enableInts();
	SPR_init() + 100); //inicializa o motor de sprites do SGDK
	
	VDP_setBackgroundColor(48); //Escolhe a cor de fundo //Range 0-63 //4 Paletas de 16 cores = 64 cores

    while(TRUE)
    {
        if(fase==1)
		{
			// Executa o setup apenas uma vez e depois deixa a fase rodando em loop.
			if(inicializacao==1)
			{
				
				//bg_A
				VDP_drawImageEx(BG_A, &bga, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, ind_tileset), 0, 0, FALSE, TRUE);
				ind_tileset += bga.tileset->numTile;
				PAL_setPalette(PAL2, bga.palette->data, DMA);
				//bg_B
				VDP_drawImageEx(BG_B, &bgb, TILE_ATTR_FULL(PAL3, FALSE, FALSE, FALSE, ind_tileset), 0, 0, FALSE, TRUE);
				ind_tileset += bgb.tileset->numTile;
				PAL_setPalette(PAL3, bgb.palette->data, DMA);
				//habilita a rolagem de scroll, que permite criar o efeito parallax
				VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
				
				//foreground
				//FG1 = SPR_addSprite(&spr_fg,   0, 185, TILE_ATTR(PAL0, FALSE, FALSE, FALSE));
				//FG2 = SPR_addSprite(&spr_fg, 300, 185, TILE_ATTR(PAL0, FALSE, FALSE, FALSE));
				//PAL_setPalette(PAL0, spr_fg.palette->data, DMA);
				
				//PERSONAGEM
				P1CHAR = SPR_addSprite(&terry, 80, 100, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
				PAL_setPalette(PAL1, terry.palette->data, DMA);
				SPR_update();
				
				//comeca a tocar a musica
				XGM_startPlay(music);
				XGM_isPlaying(); //FIX
				
				//desabilita a variavel de inicializacao
				inicializacao=0;
			}
			
			//move os backgrounds continuamente (BG_A e BG_B)
			//BG_B se move mais lentamente que o BG_A
			//Se usar + em vez de -, a rolagem será da esquerda para a direita :)
			contador_scrolling_bgA-=2;
			contador_scrolling_bgB-=1;
			VDP_setHorizontalScroll(BG_A, contador_scrolling_bgA);
			VDP_setHorizontalScroll(BG_B, contador_scrolling_bgB);
			
			//VAI PARA A FASE 2 APERTANDO START!
			u16 JOY1 = JOY_readJoypad(JOY_1);
			if(JOY1 & BUTTON_START)
			{
				fase=2;
				inicializacao=1;
				ind_tileset=1;
				SYS_disableInts();
				VDP_clearPlane(BG_A, TRUE);
				VDP_clearPlane(BG_B, TRUE);
				SYS_enableInts();
				SPR_releaseSprite(P1CHAR);
			}
		
		
		}
		
		if(fase==2)
		{
			// A segunda fase repete a estrutura da primeira com novos recursos graficos.
			if(inicializacao==1)
			{
				
				//bg_A
				VDP_drawImageEx(BG_A, &bga2, TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, ind_tileset), 0, 0, FALSE, TRUE);
				ind_tileset += bga2.tileset->numTile;
				PAL_setPalette(PAL2, bga2.palette->data, DMA);
				//bg_B
				VDP_drawImageEx(BG_B, &bgb2, TILE_ATTR_FULL(PAL3, FALSE, FALSE, FALSE, ind_tileset), 0, 0, FALSE, TRUE);
				ind_tileset += bgb2.tileset->numTile;
				PAL_setPalette(PAL3, bgb2.palette->data, DMA);
				//habilita a rolagem de scroll, que permite criar o efeito parallax
				VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
				
				//foreground
				//FG1 = SPR_addSprite(&spr_fg,   0, 185, TILE_ATTR(PAL0, FALSE, FALSE, FALSE));
				//FG2 = SPR_addSprite(&spr_fg, 300, 185, TILE_ATTR(PAL0, FALSE, FALSE, FALSE));
				//PAL_setPalette(PAL0, spr_fg.palette->data, DMA);
				
				//PERSONAGEM
				P1CHAR = SPR_addSprite(&terry, 80, 80, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
				PAL_setPalette(PAL1, terry.palette->data, DMA);
				SPR_update();
				
				//comeca a tocar a musica
				XGM_startPlay(music);
				XGM_isPlaying(); //FIX
				
				//desabilita a variavel de inicializacao
				inicializacao=0;
			}
			
			//move os backgrounds continuamente (BG_A e BG_B)
			//BG_B se move mais lentamente que o BG_A
			//Se usar + em vez de -, a rolagem será da esquerda para a direita :)
			contador_scrolling_bgA-=2;
			contador_scrolling_bgB-=1;
			VDP_setHorizontalScroll(BG_A, contador_scrolling_bgA);
			VDP_setHorizontalScroll(BG_B, contador_scrolling_bgB);
			
		}
		
		//atualiza sprites
		SPR_update();
        // wait for screen refresh and do all SGDK VBlank tasks
        SYS_doVBlankProcess();
    }

    return 0;
}

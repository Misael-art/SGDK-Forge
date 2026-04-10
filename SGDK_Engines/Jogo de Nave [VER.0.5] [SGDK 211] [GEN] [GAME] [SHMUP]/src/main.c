#include "genesis.h"
#include "sprite.h"
#include "gfx.h"
#include "sound.h"

//--- DEFINICOES ---//

#define INGAME_SFX 64
#define P1_SFX     65
#define P2_SFX     66
#define MAX_PLAYER_BULLETS 80
#define MAX_ITENS 16

// -- DECLARACAO DE VARIAVEIS -- //

u8  gRoom;                  //Sala atual
u32 gFrames;                //Frame Counter
u16 gInd_tileset;           //Variable used to load background data
u16 prevInput[3] = {0,0,0}; //Armazena o estado anterior dos botões
u16 curInput[3];            //Armazena o estado atual dos botões
u8  gNumberOfPlayers;       //Numero de jogadores inicial
Sprite *spr_mainMenu;       //SPRITE usado no Main Menu
u8  gMainMenuOptions;       //Opcoes do Main Menu
u8 gPing2 = 0;              //Variavel que alterna entre 0 e 1 constantemente
u8 gPing4 = 0;              //Variavel que alterna entre 0 ; 1 ; 2 ; 3 constantemente
u8 gPing10 = 0;             //Variavel que alterna entre 0 ; 1 ; 2 ... 7 ; 8 ; 9 constantemente
bool gBomb_active;          //Verifica se existe alguma bomba ativa

//teste de composicao
// Sprite *SPR_TEMPORARIO1;
// Sprite *SPR_TEMPORARIO2;
// Sprite *SPR_TEMPORARIO3;
// Sprite *SPR_TEMPORARIO4;
// Sprite *SPR_TEMPORARIO5;
// Sprite *SPR_TEMPORARIO6;

// -- STRUCTS -- //

struct PlayerDEF {
	Sprite* sprite;  //Sprite do Player 
	Sprite* spr_super; //Sprite FX Super Tiro
	bool active;     //Controle de ativacao do objeto
	bool podeMover;  //Habilita o controle por parte do jogador com o Joystick
	u16 x;           //Posicao X
	u16 y;           //Posicao Y
	s8 axisX;        //Ponto Pivot X
	s8 axisY;        //Ponto Pivot Y
	u8 lives;        //vidas
	s8 energia;      //Energia do Player, usada para fins de HUD, graficos das barras
	u16 state;       //Controla o estado (animacao) do Player
	s8 stability;    //Estabilidade da nave
	u8 stability_ctrl_anim; //controle de animacao de estabilidade
	s16 ctrlTimer;   //timer de controle
	u8 velocidadeDaNave;  //velocidade de deslocamento da nave na tela
	u8 bullet_type;       //tipo de tiro
	u8 bullet_red_level;  //forca do tiro red
	u8 bullet_blue_level; //forca do tiro blue
	u8 super_bar;         //barra que carrega o super tiro
	u8 bomb_cont;         //contador de bombas limpa tela
}; struct PlayerDEF P[3];

struct HudDEF {
	Sprite* spr_lives;  
	Sprite* spr_speed_bar;  
	Sprite* spr_super_bar; 
	Sprite* spr_bomb_cont; 
}; struct HudDEF Hud[3];

struct BulletDEF {
	Sprite* sprite; //Sprite do objeto 
	bool active;    //Controle de ativacao do objeto
	u16 x;          //Posicao X
	u16 y;          //Posicao Y
	s8 axisX;       //Ponto Pivot X
	s8 axisY;       //Ponto Pivot Y
	u16 state;      //Controla o estado (animacao) do objeto
	u8 ctrlTimer;   //timer de controle
	u8 dir;
	u8 energia;     //energia do tiro
}; struct BulletDEF Bullet[MAX_PLAYER_BULLETS];

struct ItemDEF {
	Sprite* sprite; //Sprite do objeto 
	bool active;    //Controle de ativacao do objeto
	u16 x;          //Posicao X
	u16 y;          //Posicao Y
	u8 type;
}; struct ItemDEF Item[MAX_ITENS];

struct ItemBoxDEF {
	Sprite* sprite; //Sprite do objeto 
	bool active;    //Controle de ativacao do objeto
	u16 x;          //Posicao X
	u16 y;          //Posicao Y
	u8 type;        //que tipo de item ele cai dropar. 0=speed; 1=vidas; 2=red; 3=blue; 9=aleatorio
	u16 quit_timer; //tempo para sair da tela
	s8 VelX;        //velocidade em X
	s8 VelY;        //velocidade em Y
}; struct ItemBoxDEF Item_Box[MAX_ITENS];

struct ExplosionDEF {
	Sprite* sprite; //Sprite do objeto 
	bool active;    //Controle de ativacao do objeto
	u16 x;          //Posicao X
	u16 y;          //Posicao Y
	u16 timer;      //temporizador para sumir
}; struct ExplosionDEF Explosion[MAX_PLAYER_BULLETS];

struct BombDEF {
	Sprite* sprite; //Sprite do objeto 
	bool active;    //Controle de ativacao do objeto
	u16 x;          //Posicao X
	u16 y;          //Posicao Y
	u16 timer;      //temporizador para sumir
	u8 state;       //estado da bomba; 1=inicio, 2=limpa a tela
}; struct BombDEF Bomb[2];


//--- FUNCOES ---//

void VDP_CLEAR();

void PLAYER_INIT();
void PLAYER_UPDATE();
void PLAYER_DESTROY();

void BULLET_RED_INIT(u8 playerID, u16 x, u16 y);
void BULLET_RED_UPDATE();
void BULLET_RED_DESTROY(u8 i);

void BULLET_BLUE_INIT(u8 playerID, u16 x, u16 y, u8 dir);
void BULLET_BLUE_UPDATE();
void BULLET_BLUE_DESTROY(u8 i);

void BULLET_SUPER_INIT(u8 playerID, u16 x, u16 y);
void BULLET_SUPER_UPDATE();
void BULLET_SUPER_DESTROY(u8 i);

void ITEM_BOX_INIT(u16 x, u16 y, u8 type);
void ITEM_BOX_UPDATE();
void ITEM_BOX_DESTROY(u8 i);

void ITEM_INIT(u16 x, u16 y, u8 type);
void ITEM_UPDATE();
void ITEM_DESTROY(u8 i);

void EXPLOSION_INIT(u16 x, u16 y, u16 timer);
void EXPLOSION_UPDATE();
void EXPLOSION_DESTROY(u8 i);

void BOMB_INIT(u8 playerID, u16 x, u16 y);
void BOMB_UPDATE();
void BOMB_DESTROY(u8 i);

//--- MAIN ---//

int main(bool hardReset)
{
    // -- INICIALIZACOES -- //
	
	SPR_init(); //SPR_initEx(300); //esta eh uma alternativa, que permite maior controle da memoria reservada para sprites
	gRoom = 1;
	gFrames = 0;
	gInd_tileset = 0;

    while(TRUE)
    {
        gFrames++;
		// PINGS
		if(gPing2  == 1){ gPing2 = -1; } gPing2++;  //var 'gPing2'  (50%) variacao: 0 ; 1
		if(gPing4  == 3){ gPing4 = -1; } gPing4++;  //var 'gPing4'  (25%) variacao: 0 ; 1 ; 2 ; 3
		if(gPing10 == 9){ gPing10= -1; } gPing10++; //var 'gPing10' (10%) variacao: 0 ; 1 ; 2 ; 3 ; 4 ; 5 ; 6 ; 7 ; 8 ; 9
		
		if(gRoom==1) //LOGO E MAIN MENU//
		{
			if(gFrames==1)
			{
				//BGB
				VDP_loadTileSet(gfx_bg_main.tileset,gInd_tileset,DMA); 
				VDP_setTileMapEx(BG_B,gfx_bg_main.tilemap,TILE_ATTR_FULL(PAL0,FALSE,FALSE,FALSE,gInd_tileset),0,0,0,0,64,28,DMA_QUEUE);
				PAL_setPalette(PAL0, gfx_bg_main.palette->data,DMA);
				gInd_tileset += gfx_bg_main.tileset->numTile;
				
				//BGA
				VDP_loadTileSet(gfx_logo.tileset,gInd_tileset,DMA); 
				VDP_setTileMapEx(BG_A,gfx_logo.tilemap,TILE_ATTR_FULL(PAL1,FALSE,FALSE,FALSE,gInd_tileset),0,0,0,0,40,28,DMA_QUEUE);
				PAL_setPalette(PAL1, gfx_logo.palette->data,DMA);
				gInd_tileset += gfx_logo.tileset->numTile;
				
				//PRESS START / MAIN MENU SPRITE
				spr_mainMenu = SPR_addSprite(&spr_main_menu, 88, 136, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
				PAL_setPalette(PAL2, spr_main_menu.palette->data,DMA);
				
				gMainMenuOptions = 0;
				gNumberOfPlayers = 1;
				
				XGM_startPlay(music_logo); XGM_isPlaying();
			}
			
			//anima o BGB, movimento horizontal (horizontal scrolling)
			VDP_setHorizontalScroll(BG_B, gFrames * -1);
			
			//---------------------------------------------------------------------------------
			//Obtém o estado atual dos botões (do Player1)
			curInput[1] = JOY_readJoypad(JOY_1);
			
			//Verifica se o botão START foi pressionado (uma vez)
			//Abre o Main Menu
			if (((curInput[1] & BUTTON_START) && !(prevInput[1] & BUTTON_START)) && gMainMenuOptions==0) {
				gMainMenuOptions = 1;
				SPR_setAnim(spr_mainMenu, gMainMenuOptions);
				prevInput[1] = curInput[1]; //Atualiza o estado anterior dos botões
			}
			
			//Verifica se o botão UP foi pressionado (uma vez)
			//Altera para a primeira opcao do menu, depois que ele foi aberto
			if (((curInput[1] & BUTTON_UP) && !(prevInput[1] & BUTTON_UP)) && gMainMenuOptions==2) {
				gMainMenuOptions = 1;
				gNumberOfPlayers = 1;
				SPR_setAnim(spr_mainMenu, gMainMenuOptions);
			}
			
			//Verifica se o botão UP foi pressionado (uma vez)
			//Altera para a primeira opcao do menu, depois que ele foi aberto
			if (((curInput[1] & BUTTON_UP) && !(prevInput[1] & BUTTON_UP)) && gMainMenuOptions==3) {
				gMainMenuOptions = 2;
				gNumberOfPlayers = 2;
				SPR_setAnim(spr_mainMenu, gMainMenuOptions);
			}
			
			//Verifica se o botão DOWN foi pressionado (uma vez)
			//Altera para a segunda opcao do menu, depois que ele foi aberto
			if (((curInput[1] & BUTTON_DOWN) && !(prevInput[1] & BUTTON_DOWN)) && gMainMenuOptions==2) {
				gMainMenuOptions = 3;
				SPR_setAnim(spr_mainMenu, gMainMenuOptions);
			}
			
			//Verifica se o botão DOWN foi pressionado (uma vez)
			//Altera para a segunda opcao do menu, depois que ele foi aberto
			if (((curInput[1] & BUTTON_DOWN) && !(prevInput[1] & BUTTON_DOWN)) && gMainMenuOptions==1) {
				gMainMenuOptions = 2;
				gNumberOfPlayers = 2;
				SPR_setAnim(spr_mainMenu, gMainMenuOptions);
			}
			
			//Verifica se o botão START foi pressionado (uma vez)
			//Vai para a ROOM INGAME
			if (((curInput[1] & BUTTON_START) && !(prevInput[1] & BUTTON_START)) && (gMainMenuOptions==1 || gMainMenuOptions==2) ) {
				
				//reseta as configuracoes de tela e vai para a proxima room
				VDP_CLEAR();
				gRoom=2;
				XGM_setPCM(INGAME_SFX, snd_start, sizeof(snd_start)); XGM_startPlayPCM(INGAME_SFX, 1, SOUND_PCM_CH3); //toca som de confirmacao
			}
			
			//Verifica se o botão START foi pressionado (uma vez)
			//Vai para a ROOM OPTIONS
			if (((curInput[1] & BUTTON_START) && !(prevInput[1] & BUTTON_START)) && gMainMenuOptions==3) {
				
				//reseta as configuracoes de tela e vai para a proxima room
				VDP_CLEAR();
				gRoom=3;
				XGM_setPCM(INGAME_SFX, snd_start, sizeof(snd_start)); XGM_startPlayPCM(INGAME_SFX, 1, SOUND_PCM_CH3); //toca som de confirmacao
			}
			
			//Atualiza o estado anterior dos botões
			prevInput[1] = curInput[1];
			//---------------------------------------------------------------------------------
			
		}
		
		if(gRoom==2) //INGAME//
		{
			if(gFrames==1)
			{
				//BGB
				VDP_loadTileSet(gfx_bg_main.tileset,gInd_tileset,DMA); 
				VDP_setTileMapEx(BG_B,gfx_bg_main.tilemap,TILE_ATTR_FULL(PAL0,FALSE,FALSE,FALSE,gInd_tileset),0,0,0,0,64,28,DMA_QUEUE);
				PAL_setPalette(PAL0, gfx_bg_main.palette->data,DMA);
				gInd_tileset += gfx_bg_main.tileset->numTile;
				
				//Inicializa 1 ou 2 players
				PLAYER_INIT(); P[1].lives = 3;
				if(gNumberOfPlayers==2){ PLAYER_INIT(); P[2].lives = 3; }
				
				//carregamento / inicializacao do HUD
				for(int i=1; i<=gNumberOfPlayers; i++){
					
					u16 a=0; if(i==2){ a=232; } //empurra o HUD do P2 para o lado direito da tela
					
					Hud[i].spr_lives     = SPR_addSprite(&spr_numbers  ,  8+a, 16, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
					Hud[i].spr_speed_bar = SPR_addSprite(&spr_speed_bar, 16+a, 16, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
					Hud[i].spr_super_bar = SPR_addSprite(&spr_super_bar, 40+a, 16, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
					Hud[i].spr_bomb_cont = SPR_addSprite(&spr_bomb_cont, 16+a, 24, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
					if(Hud[i].spr_lives){ SPR_setAnim(Hud[i].spr_lives, P[i].lives); } 
					if(Hud[i].spr_bomb_cont){ SPR_setAnim(Hud[i].spr_bomb_cont, P[i].bomb_cont); } 
				}
				
				//-------------------------------------------------------------
				// //posicionamento de itens (TEMPORARIO)
				
				// //speed
				// ITEM_INIT( 20, 140, 0);
				// ITEM_INIT( 40, 140, 0);
				
				// //vidas
				// ITEM_INIT( 20, 160, 1);
				// ITEM_INIT( 40, 160, 1);
				// ITEM_INIT( 60, 160, 1);
				// ITEM_INIT( 80, 160, 1);
				// ITEM_INIT(100, 160, 1);
				// ITEM_INIT(120, 160, 1);
				
				// //tiro red
				// ITEM_INIT( 20, 180, 2);
				// ITEM_INIT( 40, 180, 2);
				// ITEM_INIT( 60, 180, 2);
				
				// ITEM_INIT(120, 180, 2);
				// ITEM_INIT(140, 180, 2);
				// ITEM_INIT(160, 180, 2);
				
				// //tiro blue
				// ITEM_INIT( 20, 200, 3);
				// ITEM_INIT( 40, 200, 3);
				// ITEM_INIT( 60, 200, 3);
				
				// ITEM_INIT(120, 200, 3);
				// ITEM_INIT(140, 200, 3);
				// ITEM_INIT(160, 200, 3);
				
				//posicionamento de Item_Box
				ITEM_BOX_INIT(207, 100, 9);
				ITEM_BOX_INIT(195,  53, 9);
				ITEM_BOX_INIT(294, 104, 9);
				ITEM_BOX_INIT(101, 101, 9);
				ITEM_BOX_INIT( 39,  68, 9);
				ITEM_BOX_INIT(158, 181, 9);
				
				//teste de composicao
				// SPR_TEMPORARIO1 = SPR_addSprite(&spr_enemy01     ,  264,  56, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
				// SPR_TEMPORARIO2 = SPR_addSprite(&spr_enemy02     ,  264,  80, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
				// SPR_TEMPORARIO3 = SPR_addSprite(&spr_enemy03     ,  264, 112, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
				// SPR_TEMPORARIO4 = SPR_addSprite(&spr_enemy04     ,  272, 160, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
				// SPR_TEMPORARIO5 = SPR_addSprite(&spr_bomb        ,   40,  40, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
				// SPR_TEMPORARIO6 = SPR_addSprite(&spr_bullet_super,  160, 112, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
				// PAL_setPalette(PAL3, spr_enemy01.palette->data,DMA);
				//-------------------------------------------------------------
				
				XGM_startPlay(music_ingame); XGM_isPlaying();
				
			}
			
			//anima o BGB, movimento horizontal (horizontal scrolling)
			VDP_setHorizontalScroll(BG_B, gFrames * -1);
			
			gBomb_active=FALSE;
			BOMB_UPDATE();
			
			PLAYER_UPDATE();
			ITEM_UPDATE();
			ITEM_BOX_UPDATE();
			BULLET_RED_UPDATE();
			BULLET_BLUE_UPDATE();
			EXPLOSION_UPDATE();
			
		}
		
		if(gRoom==3) //OPTIONS//
		{
			char str[64];
			sprintf(str, "AQUI SERA PROGRAMADO O OPTIONS");
			VDP_drawText(str, 1, 10);
		}
		
		//------------------------------------------------------------------------------------------------------------------
		// -- DEBUG, OPCIONAL -- //
		
		if(gRoom==1) //LOGO DEBUG
		{
			char str[64];
			sprintf(str, "tiles usados nos BGs: %d", gInd_tileset); VDP_drawText(str, 1, 1);
			sprintf(str, "contagem de frames: %ld", gFrames); VDP_drawText(str, 1, 2);
		}
		
		if(gRoom==2) //INGAME DEBUG
		{
			VDP_showFPS(1, 1, 1); //Mostrar FPS
			
			// char str[64];
			
			// sprintf(str, "P1 bullet type.......: %d", P[1].bullet_type);       VDP_drawText(str, 1, 3);
			// sprintf(str, "   bullet RED level..: %d", P[1].bullet_red_level);  VDP_drawText(str, 1, 4);
			// sprintf(str, "   bullet BLUE level.: %d", P[1].bullet_blue_level); VDP_drawText(str, 1, 5);
			// sprintf(str, "   speed.............: %d", P[1].velocidadeDaNave);  VDP_drawText(str, 1, 6);
			// sprintf(str, "   lives.............: %d", P[1].lives);             VDP_drawText(str, 1, 7);
			// sprintf(str, "   super............: %2d", P[1].super_bar);         VDP_drawText(str, 1, 8);
			
			// sprintf(str, "P2 bullet type.......: %d", P[2].bullet_type);       VDP_drawText(str, 1,10);
			// sprintf(str, "   bullet RED level..: %d", P[2].bullet_red_level);  VDP_drawText(str, 1,11);
			// sprintf(str, "   bullet BLUE level.: %d", P[2].bullet_blue_level); VDP_drawText(str, 1,12);
			// sprintf(str, "   speed.............: %d", P[2].velocidadeDaNave);  VDP_drawText(str, 1,13);
			// sprintf(str, "   lives.............: %d", P[2].lives);             VDP_drawText(str, 1,14);
			// sprintf(str, "   super............: %2d", P[2].super_bar);         VDP_drawText(str, 1,15);
			
		}
		//------------------------------------------------------------------------------------------------------------------
		
		// -- FINALIZACOES -- //
		
        SPR_update(); // Atualização dos sprites na tela
        SYS_doVBlankProcess(); // Sincroniza com o VBlank
    }

    return 0;
}

//--- FUNCOES ---//

void VDP_CLEAR()
{
	SPR_reset();
	VDP_clearPlane(BG_A, TRUE);
	VDP_clearPlane(BG_B, TRUE);
	VDP_setBackgroundColor(0);
	VDP_resetScreen();
	//PAL_setColors(0, palette_black, 64, DMA);
	VDP_setHorizontalScroll(BG_B, 0); 
	VDP_setVerticalScroll(BG_B, 0); 
	VDP_setHorizontalScroll(BG_A, 0); 
	VDP_setVerticalScroll(BG_A, 0);
	gInd_tileset=0;
	gFrames=0;
}

void PLAYER_INIT()
{
	for (int i = 1; i <= 2; i++) {
        if (!P[i].active) {
			
			P[i].active = TRUE;
			
			if(i==1){ P[i].sprite = SPR_addSprite(&spr_spaceship,  320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE)); }
			if(i==2){ P[i].sprite = SPR_addSprite(&spr_spaceship2, 320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE)); } //P2 utiliza outro sprite
			
			P[i].spr_super = SPR_addSprite(&spr_super,  320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
			
			PAL_setPalette(PAL2, spr_spaceship.palette->data,DMA);
			P[i].podeMover = FALSE;
			P[i].x = 0;
            if(i==1){ P[i].y =  96; } //P1 posicao Y
			if(i==2){ P[i].y = 128; } //P2 é inicializado um pouco mais abaixo do que o P1
			P[i].axisX = 24;
            P[i].axisY = 16;
			P[i].energia = 1;
			P[i].state = 0;
			P[i].stability = 0;
			P[i].stability_ctrl_anim = 0;
			P[i].ctrlTimer = 0;
			P[i].velocidadeDaNave = 2;
			P[i].bullet_type=1;
			P[i].bullet_red_level=1;
			P[i].bullet_blue_level=0;
			P[i].super_bar=0;
			P[i].bomb_cont=3;
			
			break;
        }
    }
}

void PLAYER_UPDATE()
{
	for (int i = 1; i <= 2; i++) { 
		if (P[i].active)
		{
			
			//intro; state 0
			if(P[i].state==0)
			{
				u16 timerDuracaoDaIntro = 3*(12*3);
				//3*(12*3) //3 é o tempo de animacao do sprite no arquivo .res * ( 12 numero de frames do giro * 3 qtde de giros )
				
				P[i].ctrlTimer++;
				
				//move para a direita
				if( P[i].ctrlTimer <= timerDuracaoDaIntro )	{
					P[i].x+=2;
				}
				
				//troca a animacao
				if( P[i].ctrlTimer == timerDuracaoDaIntro )	{
					SPR_setAnim(P[i].sprite, 1);
				} 
				
				//move para a esquerda
				if( P[i].ctrlTimer > timerDuracaoDaIntro && P[i].ctrlTimer <= timerDuracaoDaIntro*2 ) {
					P[i].x--;
				}
				
				//finaliza a intro
				if( P[i].ctrlTimer == timerDuracaoDaIntro*2 ) {
					SPR_setAnim(P[i].sprite, 4); //4 eh o sprite da nave estabilizada na horizontal
					P[i].podeMover = TRUE;       //permite ao jogador controlar a nave
					P[i].state = 1;              //finaliza o estado de intro
					P[i].ctrlTimer = 0;          //ctrlTimer deixa de ser um temporizador da intro, e vai passar a controlar a estabilidade da nave em outro contexto
				} 
			}
			
			//gameplay; state 1
			if(P[i].state==1)
			{
				//---------------------------------------------------------------------------------
				// JOYSTICK
				//---------------------------------------------------------------------------------
				//Obtém o estado atual dos botões
				if(i==1){
					curInput[i] = JOY_readJoypad(JOY_1); //P1
				}else{
					curInput[i] = JOY_readJoypad(JOY_2); //P2
				}
				
				if(P[i].podeMover == TRUE)
				{
					//Verifica se o botão UP foi pressionado
					if (curInput[i] & BUTTON_UP) {
						P[i].y-=P[i].velocidadeDaNave;
						P[i].ctrlTimer+=2; 
					}
					
					//Verifica se o botão DOWN foi pressionado
					if (curInput[i] & BUTTON_DOWN) {
						P[i].y+=P[i].velocidadeDaNave;
						P[i].ctrlTimer-=2;
					}
					
					//Verifica se o botão LEFT foi pressionado
					if (curInput[i] & BUTTON_LEFT) {
						P[i].x-=P[i].velocidadeDaNave;
					}
					
					//Verifica se o botão RIGHT foi pressionado
					if (curInput[i] & BUTTON_RIGHT) {
						P[i].x+=P[i].velocidadeDaNave;
					}
					
					//controle de disparo!
					bool DISPARAR=FALSE;
					bool DISPARAR_SUPER=FALSE;
					
					//Verifica se o botão A foi pressionado (uma vez)
					if ((curInput[i] & BUTTON_A) && !(prevInput[i] & BUTTON_A)) {
						DISPARAR = TRUE;
						if(i==1){ XGM_setPCM(P1_SFX, snd_bullet, sizeof(snd_bullet)); XGM_startPlayPCM(P1_SFX, 1, SOUND_PCM_CH1);  }
						if(i==2){ XGM_setPCM(P2_SFX, snd_bullet, sizeof(snd_bullet)); XGM_startPlayPCM(P2_SFX, 1, SOUND_PCM_CH2);  }
					}
					
					//Verifica se o botão A se mantem apertado (segurar o botao carrega o super tiro)
					if (curInput[i] & BUTTON_A){
						if(P[i].super_bar<32 && (gPing10==0 || gPing10==5) )
						{ 
							P[i].super_bar++; 
							if(Hud[i].spr_super_bar){ SPR_setAnim(Hud[i].spr_super_bar, P[i].super_bar); }
						}
					}
					
					//Verifica se o botão A foi SOLTO (uma vez)
					if (!(curInput[i] & BUTTON_A) && (prevInput[i] & BUTTON_A)) {
						if(P[i].super_bar==32){ DISPARAR_SUPER=TRUE; }
						P[i].super_bar=0;
						if(Hud[i].spr_super_bar){ SPR_setAnim(Hud[i].spr_super_bar, P[i].super_bar); }
					}
					
					//Verifica se o botão B foi pressionado e gPing10==N (tiro automatico)
					if ( (curInput[i] & BUTTON_B) && (gPing10==1) ) {
						DISPARAR = TRUE;
					}					
					
					if(DISPARAR==TRUE){
						
						//tiro vermelho (RED)
						if(P[i].bullet_type==1)
						{
							if(P[i].bullet_red_level==1)
							{
								BULLET_RED_INIT(i, P[i].x, P[i].y);
							}
							if(P[i].bullet_red_level==2)
							{
								BULLET_RED_INIT(i, P[i].x, P[i].y-4);
								BULLET_RED_INIT(i, P[i].x, P[i].y+4);
							}
							if(P[i].bullet_red_level==3)
							{
								BULLET_RED_INIT(i, P[i].x-8, P[i].y-8);
								BULLET_RED_INIT(i, P[i].x, P[i].y);
								BULLET_RED_INIT(i, P[i].x-8, P[i].y+8);
							}
						}
						
						//tiro azul (BLUE)
						if(P[i].bullet_type==2)
						{
							if(P[i].bullet_blue_level==1)
							{
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 9);
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 3);
							}
							if(P[i].bullet_blue_level==2)
							{
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 9);
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 6);
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 3);
							}
							if(P[i].bullet_blue_level==3)
							{
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 8);
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 9);
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 6);
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 3);
								BULLET_BLUE_INIT(i, P[i].x, P[i].y, 2);
							}
						}
						
						//prevInput[i] = curInput; //Atualiza o estado anterior dos botões
					}
					
					if(DISPARAR_SUPER==TRUE){
						BULLET_SUPER_INIT(i, P[i].x, P[i].y);
					}
					
					//Verifica se o botão C foi pressionado (uma vez)
					if ((curInput[i] & BUTTON_C) && !(prevInput[i] & BUTTON_C)) {
						
						//atribui ID correto para a Bomba
						u8 checkBomb;
						if(i==1){ checkBomb=0; }else{ checkBomb=1; }
						
						//verifica se a bomba do Player atual nao esta ativa e SE ele tem bombas antes de soltar
						if ( (!Bomb[checkBomb].active) && (P[i].bomb_cont>0) )
						{
							if(i==1){ XGM_setPCM(P1_SFX, snd_bullet, sizeof(snd_bullet)); XGM_startPlayPCM(P1_SFX, 1, SOUND_PCM_CH1);  }
							if(i==2){ XGM_setPCM(P2_SFX, snd_bullet, sizeof(snd_bullet)); XGM_startPlayPCM(P2_SFX, 1, SOUND_PCM_CH2);  }
							
							BOMB_INIT(checkBomb, P[i].x, P[i].y);
							P[i].bomb_cont--;
							if(Hud[i].spr_bomb_cont){ SPR_setAnim(Hud[i].spr_bomb_cont, P[i].bomb_cont); } 
						}
						
					}
					
				}
				
				//Atualiza o estado anterior dos botões
				prevInput[i] = curInput[i];
				//---------------------------------------------------------------------------------
				
				//LIMITADOR DE MOVIMENTO; evita que a nave saia da tela
				if( P[i].x < 14){ P[i].x= 14; }
				if( P[i].x >306){ P[i].x=306; }
				if( P[i].y < 10){ P[i].y= 10; }
				if( P[i].y >214){ P[i].y=214; }
				
				//---------------------------------------------------------------------------------
				// ESTABILIZACAO / INCLINACAO
				//---------------------------------------------------------------------------------
				//Controle de estabilidade / inclinacao da Nave
				if(P[i].ctrlTimer>0){ P[i].ctrlTimer--; } 
				if(P[i].ctrlTimer<0){ P[i].ctrlTimer++; } 
				
				//Esses 2 comandos abaixo sao opcionais, eles apenas aceleram a estabilizacao da nave; 
				//a ideia é que ela se incline devagar qdo sobe (ou desce), e incline mais rapido para voltar ao estado estavel, fica mais bonita a animacao
				if((curInput[i] & !BUTTON_UP)   && P[i].ctrlTimer>0) { P[i].ctrlTimer--; }
				if((curInput[i] & !BUTTON_DOWN) && P[i].ctrlTimer<0) { P[i].ctrlTimer++; }
				
				//para nao passar dos limites; sao apenas 2 frames de inclinacao, cada um durando 10 frames
				if(P[i].ctrlTimer> 20){ P[i].ctrlTimer= 20; }
				if(P[i].ctrlTimer<-20){ P[i].ctrlTimer=-20; }
				
				//atualiza o sprite de acordo com a inclinacao
				bool atualizar_anim = FALSE;
				if(P[i].ctrlTimer> 10 && P[i].ctrlTimer<= 20 && P[i].stability_ctrl_anim!=2){ P[i].stability_ctrl_anim=2; atualizar_anim=TRUE; }
				if(P[i].ctrlTimer>  0 && P[i].ctrlTimer<= 10 && P[i].stability_ctrl_anim!=3){ P[i].stability_ctrl_anim=3; atualizar_anim=TRUE; }
				if(P[i].ctrlTimer==0  && P[i].stability_ctrl_anim!=4)                       { P[i].stability_ctrl_anim=4; atualizar_anim=TRUE; }
				if(P[i].ctrlTimer<  0 && P[i].ctrlTimer>=-10 && P[i].stability_ctrl_anim!=5){ P[i].stability_ctrl_anim=5; atualizar_anim=TRUE; }
				if(P[i].ctrlTimer<-10 && P[i].ctrlTimer>=-20 && P[i].stability_ctrl_anim!=6){ P[i].stability_ctrl_anim=6; atualizar_anim=TRUE; }
				if(atualizar_anim==TRUE){
					SPR_setAnim(P[i].sprite, P[i].stability_ctrl_anim);
				}
				//---------------------------------------------------------------------------------
				
			}
			
			//atualiza a posicao da nave na tela
			if(P[i].sprite){ SPR_setPosition(P[i].sprite, P[i].x-P[i].axisX, P[i].y-P[i].axisY); }
			
			//super tiro
			if(P[i].super_bar==32){
				if(P[i].spr_super){ SPR_setPosition(P[i].spr_super, (P[i].x+16)-10, P[i].y-6); } //mostra o efeito do super tiro seguindo sua nave
			}else{
				if(P[i].spr_super){ SPR_setPosition(P[i].spr_super, 320, 224); } //esconde o sprite fora da tela
			}
			
		}
	}
}

void PLAYER_DESTROY()
{
	//em breve
}

void BULLET_RED_INIT(u8 playerID, u16 x, u16 y)
{
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (!Bullet[i].active) {
			
			Bullet[i].active = TRUE;
			
			Bullet[i].sprite = SPR_addSprite(&spr_bullet_red, 320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
			Bullet[i].x = x;
            Bullet[i].y = y;
			Bullet[i].axisX = 4;
            Bullet[i].axisY = 4;
			Bullet[i].state = 1;
			Bullet[i].ctrlTimer = 0;
			Bullet[i].dir = 6;
			Bullet[i].energia = 1;
			
			break;
        }
    }
}

void BULLET_RED_UPDATE()
{
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (Bullet[i].active) {
			
			if(Bullet[i].state!=9){ Bullet[i].x += 10; }
			
			if(Bullet[i].x>320){
				BULLET_RED_DESTROY(i);
			}
			
			if(Bullet[i].state==9)
			{
				if(Bullet[i].ctrlTimer>=16){ BULLET_RED_DESTROY(i); }
				if(Bullet[i].ctrlTimer!=0){ Bullet[i].ctrlTimer++; }
				if(Bullet[i].ctrlTimer==0){ Bullet[i].ctrlTimer=1; }
			} 
			
			//atualiza a posicao do objeto na tela
			if(Bullet[i].sprite){ SPR_setPosition(Bullet[i].sprite, Bullet[i].x-Bullet[i].axisX, Bullet[i].y-Bullet[i].axisY); }
        }
    }
}

void BULLET_RED_DESTROY(u8 i)
{
	if (Bullet[i].active)
	{
		Bullet[i].active = FALSE;
		if(Bullet[i].sprite)
		{ 
			SPR_releaseSprite(Bullet[i].sprite); 
			Bullet[i].sprite = NULL; 
		}
	}
}

void BULLET_BLUE_INIT(u8 playerID, u16 x, u16 y, u8 dir)
{
	// A direcao do tiro eh baseada no teclado numerico
	//
	// 7 8 9
	// 4 5 6
	// 1 2 3
	
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (!Bullet[i].active) {
			
			Bullet[i].active = TRUE;
			
			Bullet[i].sprite = SPR_addSprite(&spr_bullet_blue, 320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
			Bullet[i].x = x;
            Bullet[i].y = y;
			Bullet[i].axisX = 4;
            Bullet[i].axisY = 4;
			Bullet[i].state = 1;
			Bullet[i].ctrlTimer = 0;
			Bullet[i].dir = dir;
			Bullet[i].energia = 1;
			
			break;
        }
    }
}

void BULLET_BLUE_UPDATE()
{
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (Bullet[i].active) {
			
			if(Bullet[i].state!=9)
			{ 
				if     (Bullet[i].dir==8){ Bullet[i].y -= 10; }
				else if(Bullet[i].dir==9){ Bullet[i].y -= 5; }
				else if(Bullet[i].dir==6){ } //tiro na direcao 6 nao sofre alteracao no eixo Y
				else if(Bullet[i].dir==3){ Bullet[i].y += 5; }
				else if(Bullet[i].dir==2){ Bullet[i].y += 10; }
				Bullet[i].x += 10; //bullets sempre se movem para a direita (independente da direcao do "Bullet[i].dir")
			}
			
			if(Bullet[i].x>320 || Bullet[i].y<1 || Bullet[i].y>224){
				BULLET_BLUE_DESTROY(i);
			}
			
			if(Bullet[i].state==9)
			{
				if(Bullet[i].ctrlTimer>=16){ BULLET_BLUE_DESTROY(i); }
				if(Bullet[i].ctrlTimer!=0){ Bullet[i].ctrlTimer++; }
				if(Bullet[i].ctrlTimer==0){ Bullet[i].ctrlTimer=1; }
			} 
			
			//atualiza a posicao do objeto na tela
			if(Bullet[i].sprite){ SPR_setPosition(Bullet[i].sprite, Bullet[i].x-Bullet[i].axisX, Bullet[i].y-Bullet[i].axisY); }
        }
    }
}

void BULLET_BLUE_DESTROY(u8 i)
{
	if (Bullet[i].active)
	{
		Bullet[i].active = FALSE;
		if(Bullet[i].sprite)
		{ 
			SPR_releaseSprite(Bullet[i].sprite); 
			Bullet[i].sprite = NULL; 
		}
	}
}

void BULLET_SUPER_INIT(u8 playerID, u16 x, u16 y)
{
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (!Bullet[i].active) {
			
			Bullet[i].active = TRUE;
			
			Bullet[i].sprite = SPR_addSprite(&spr_bullet_super, 320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
			Bullet[i].x = x;
            Bullet[i].y = y;
			Bullet[i].axisX = 23;
            Bullet[i].axisY = 8;
			Bullet[i].state = 1;
			Bullet[i].ctrlTimer = 0;
			Bullet[i].dir = 6;
			Bullet[i].energia = 10;
			
			break;
        }
    }
}

void BULLET_SUPER_UPDATE()
{
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (Bullet[i].active) {
			
			if(Bullet[i].state!=9){ Bullet[i].x += 4; }
			
			if(Bullet[i].x>320){
				BULLET_SUPER_DESTROY(i);
			}
			
			if(Bullet[i].state==9)
			{
				if(Bullet[i].ctrlTimer>=16){ BULLET_SUPER_DESTROY(i); }
				if(Bullet[i].ctrlTimer!=0){ Bullet[i].ctrlTimer++; }
				if(Bullet[i].ctrlTimer==0){ Bullet[i].ctrlTimer=1; }
			} 
			
			//atualiza a posicao do objeto na tela
			if(Bullet[i].sprite){ SPR_setPosition(Bullet[i].sprite, Bullet[i].x-Bullet[i].axisX, Bullet[i].y-Bullet[i].axisY); }
        }
    }
}

void BULLET_SUPER_DESTROY(u8 i)
{
	if (Bullet[i].active)
	{
		Bullet[i].active = FALSE;
		if(Bullet[i].sprite)
		{ 
			SPR_releaseSprite(Bullet[i].sprite); 
			Bullet[i].sprite = NULL; 
		}
	}
}

void ITEM_BOX_INIT(u16 x, u16 y, u8 type)
{
	for (int i = 0; i < MAX_ITENS; i++) {
        if (!Item_Box[i].active) {
			
			Item_Box[i].active = TRUE;
			
			Item_Box[i].sprite = SPR_addSprite(&spr_item_box, 320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
			Item_Box[i].x = x;
            Item_Box[i].y = y;
			Item_Box[i].type = type;
			
			Item_Box[i].quit_timer=10*60; //tempo para sair da tela; 10 segundos
			
			//---------------------------------------------------------------------------------------
			// Sorteio de movimento inicial do Item Box
			
			// METODO 1
			// Variável estática para incrementar a semente
			// static u16 seedOffset = 0; 
			// Define a semente do gerador de números aleatórios e soma ao "seedOffset"
			// setRandomSeed(getTick() + seedOffset++);
			
			// METODO 2
			// Define a semente do gerador de números aleatórios; faz um XOR entre getTick e o índice
			setRandomSeed(getTick() ^ i); 
			
			// Sorteio de uma opção entre 4 (valores: 0, 1, 2, 3)
			u16 randomOption = random() % 4;
			// Tabela de velocidades (X, Y) para cada opção
			const s8 velocityTable[4][2] = { {-1, -1}, {+1, -1}, {-1, +1}, {+1, +1} };
			// Aplica as velocidades correspondentes ao Item_Box[i]
			Item_Box[i].VelX = velocityTable[randomOption][0];
			Item_Box[i].VelY = velocityTable[randomOption][1];
			//---------------------------------------------------------------------------------------
			
			break;
        }
    }
}

void ITEM_BOX_UPDATE()
{
	for (int i = 0; i < MAX_ITENS; i++) {
        if (Item_Box[i].active) {
			
			//movimento
			if(gPing2==1){ Item_Box[i].x += Item_Box[i].VelX; }
			Item_Box[i].y += Item_Box[i].VelY; 
			
			// Mantém o item box na tela, enquanto não for o momento dele sair; rebate o Item_Box na tela
			if (Item_Box[i].quit_timer > 0)
			{
				Item_Box[i].quit_timer--;

				if (Item_Box[i].x < 16){ Item_Box[i].VelX = +1; }else if (Item_Box[i].x > 304){ Item_Box[i].VelX = -1; }
				if (Item_Box[i].y < 16){ Item_Box[i].VelY = +1; }else if (Item_Box[i].y > 208){ Item_Box[i].VelY = -1; }
			}
			
			// COLISAO: Item_Box x Tiros
			for(int j=0; j<MAX_PLAYER_BULLETS; j++)
			{
				// //teste de colisao simplificado :)
				if( (Bullet[j].x>Item_Box[i].x-12 && Bullet[j].x<Item_Box[i].x+12 && Bullet[j].y>Item_Box[i].y-12 && Bullet[j].y<Item_Box[i].y+12) && Bullet[j].active==TRUE )
				{ 
					//destroi o item box
					ITEM_BOX_DESTROY(i);
					
					//cria um item na tela
					if(Item_Box[i].type==9)
					{
						//atencao: Se item box type igual a 9, gPing4 sera usado para aleatoriamente um dos itens (0,1,2,3) 
						ITEM_INIT( Item_Box[i].x, Item_Box[i].y, gPing4); 
					}else{
						//caso contrario, irá criar item do tipo especificado
						ITEM_INIT( Item_Box[i].x, Item_Box[i].y, Item_Box[i].type); 
					}
					
					//altera o status do tiro que acertou o item box
					Bullet[j].energia--;
					if(Bullet[j].energia==0)
					{
						Bullet[j].state=9;
						SPR_setAnim(Bullet[j].sprite, 1);
					}
					
					//cria o FX de explosao
					EXPLOSION_INIT(Item_Box[i].x, Item_Box[i].y, 13*4);
				}
			}
			
			// Destroi com Bomba
			if(gBomb_active==TRUE)
			{
				//destroi o item box
				ITEM_BOX_DESTROY(i);
				
				//cria um item na tela
				if(Item_Box[i].type==9)
				{
					//atencao: Se item box type igual a 9, randomOption sera usado para aleatoriamente um dos itens (0,1,2,3) 
					setRandomSeed(getTick() ^ i); 
					u16 randomOption = random() % 4;
					ITEM_INIT( Item_Box[i].x, Item_Box[i].y, randomOption); 
				}else{
					//caso contrario, irá criar item do tipo especificado
					ITEM_INIT( Item_Box[i].x, Item_Box[i].y, Item_Box[i].type); 
				}
				
				//cria o FX de explosao
				EXPLOSION_INIT(Item_Box[i].x, Item_Box[i].y, 13*4);
			}
			
			if(Item_Box[i].x<1 || Item_Box[i].x>320 || Item_Box[i].y<1 || Item_Box[i].y>224){
				ITEM_BOX_DESTROY(i);
			}
			
			//atualiza a posicao do objeto na tela
			if(Item_Box[i].sprite){ SPR_setPosition(Item_Box[i].sprite, Item_Box[i].x-8, Item_Box[i].y-8); }
        }
    }
}

void ITEM_BOX_DESTROY(u8 i)
{
	if (Item_Box[i].active)
	{
		Item_Box[i].active = FALSE;
		
		if(Item_Box[i].sprite)
		{ 
			SPR_releaseSprite(Item_Box[i].sprite); 
			Item_Box[i].sprite = NULL; 
		}
	}
}

void ITEM_INIT(u16 x, u16 y, u8 type)
{
	for (int i = 0; i < MAX_ITENS; i++) {
        if (!Item[i].active) {
			
			Item[i].active = TRUE;
			
			Item[i].sprite = SPR_addSprite(&spr_itens, 320, 224, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
			SPR_setAnim(Item[i].sprite, type);
			Item[i].x = x;
            Item[i].y = y;
			Item[i].type = type;
			
			break;
        }
    }
}

void ITEM_UPDATE()
{
	for (int i = 0; i < MAX_ITENS; i++) {
        if (Item[i].active) {
			
			if(gPing4==1){ Item[i].x -= 1; }
			
			for(int j=1; j<=2; j++)
			{
				//teste de colisao simplificado :)
				if(P[j].x>Item[i].x-16 && P[j].x<Item[i].x+16 && P[j].y>Item[i].y-16 && P[j].y<Item[i].y+16)
				{ 
					//player pegou o item!
					if(Item[i].type==0){ if(P[j].velocidadeDaNave<4){ P[j].velocidadeDaNave+=1; } } //velocidade maxima 4
					if(Item[i].type==1){ if(P[j].lives<9){ P[j].lives++; } } //vidas maximas 9
					if(Item[i].type==2){ P[j].bullet_type=1; if(P[j].bullet_red_level<3){ P[j].bullet_red_level++; } } //red level maximo 3
					if(Item[i].type==3){ P[j].bullet_type=2; if(P[j].bullet_blue_level<3){ P[j].bullet_blue_level++; } } //blue level maximo 3
					
					if(Hud[j].spr_lives){ SPR_setAnim(Hud[j].spr_lives, P[j].lives); }
					if(Hud[j].spr_speed_bar){ SPR_setAnim(Hud[j].spr_speed_bar, P[j].velocidadeDaNave-2); }
					
					ITEM_DESTROY(i);
				}
			}
			
            //Item[i].ctrlTimer++; //nao usado
			
			if(Item[i].x<1){
				ITEM_DESTROY(i);
			}
			
			//atualiza a posicao do objeto na tela
			if(Item[i].sprite){ SPR_setPosition(Item[i].sprite, Item[i].x-8, Item[i].y-8); }
        }
    }
}

void ITEM_DESTROY(u8 i)
{
	if (Item[i].active)
	{
		Item[i].active = FALSE;
		if(Item[i].sprite)
		{ 
			SPR_releaseSprite(Item[i].sprite); 
			Item[i].sprite = NULL; 
		}
	}
}

void EXPLOSION_INIT(u16 x, u16 y, u16 timer)
{
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (!Explosion[i].active) {
			
			Explosion[i].active = TRUE;
			
			XGM_setPCM(INGAME_SFX, snd_explosion, sizeof(snd_explosion)); XGM_startPlayPCM(INGAME_SFX, 1, SOUND_PCM_CH3);
			
			Explosion[i].sprite = SPR_addSprite(&spr_explosion, 320, 224, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
			if(Explosion[i].sprite){ SPR_setDepth(Explosion[i].sprite, 1); }
			
			Explosion[i].x = x;
            Explosion[i].y = y;
			Explosion[i].timer = timer;
			
			break;
        }
    }
}

void EXPLOSION_UPDATE()
{
	for (int i = 0; i < MAX_PLAYER_BULLETS; i++) {
        if (Explosion[i].active) {
			
			Explosion[i].timer--;
			if( Explosion[i].timer==0 ){ EXPLOSION_DESTROY(i); }
			
			//atualiza a posicao do objeto na tela
			if(Explosion[i].sprite){ SPR_setPosition(Explosion[i].sprite, Explosion[i].x-20, Explosion[i].y-20); }
        }
    }
}

void EXPLOSION_DESTROY(u8 i)
{
	if (Explosion[i].active)
	{
		Explosion[i].active = FALSE;
		if(Explosion[i].sprite)
		{ 
			SPR_releaseSprite(Explosion[i].sprite); 
			Explosion[i].sprite = NULL; 
		}
	}
}

void BOMB_INIT(u8 playerID, u16 x, u16 y)
{

	int i = playerID;
	
	if (!Bomb[i].active) {
		
		Bomb[i].active = TRUE;
		
		XGM_setPCM(INGAME_SFX, snd_explosion, sizeof(snd_explosion)); XGM_startPlayPCM(INGAME_SFX, 1, SOUND_PCM_CH3);
		
		Bomb[i].sprite = SPR_addSprite(&spr_bomb, 320, 224, TILE_ATTR(PAL2, TRUE, FALSE, FALSE));
		if(Bomb[i].sprite){ SPR_setDepth(Bomb[i].sprite, 1); }
		
		Bomb[i].x = x;
		Bomb[i].y = y;
		Bomb[i].timer = 4*6; //4 frames * vel anim 6
		Bomb[i].state = 1;
		
		//faz com que a ultima bomba solta fique por cima da bomba anterior, se houver, em caso 2 players
		//i=0 Bomba do P1; i=1 Bomba do P2
		if(i==0)
		{
			if(Bomb[1].active) //Bomba do P2 esta ativa entao prioridade vai para a Bomba do P1
			{
				if(Bomb[0].sprite){ SPR_setDepth(Bomb[0].sprite, 1); }
				if(Bomb[1].sprite){ SPR_setDepth(Bomb[1].sprite, 2); }
			}
		}else{
			if(Bomb[0].active) //Bomba do P1 esta ativa entao prioridade vai para a Bomba do P2
			{
				if(Bomb[0].sprite){ SPR_setDepth(Bomb[0].sprite, 2); }
				if(Bomb[1].sprite){ SPR_setDepth(Bomb[1].sprite, 1); }
			}
		}
		
	}

}

void BOMB_UPDATE()
{
	for (int i = 0; i < 2; i++) {
        if (Bomb[i].active) {
			
			Bomb[i].timer--;
			
			if( Bomb[i].timer==0 && Bomb[i].state==1)
			{ 
				Bomb[i].state=2;
				Bomb[i].timer=8*6; //8 frames * vel anim 6
				
				//--------------------------------------------------------------------------------------
				// *Opcional; FLASH EFFECT, piscar na cor branca
				// Declara a paleta branca
				const u16 palette_white[16] = {
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF),
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF),
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF),
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF),
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF),
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF),
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF),
					RGB24_TO_VDPCOLOR(0xFFFFFF), RGB24_TO_VDPCOLOR(0xFFFFFF)
				};
				//reseta a primeira paleta (PAL0) para o branco
				PAL_setColors(0, palette_white, 16, DMA);
				//--------------------------------------------------------------------------------------
				
			}
			
			//-------------------------------------------------------------------------------------------------------------------
			//*Se for usado o Flash Effect, aqui eu restauro a paleta do cenario (PAL0)
			if( Bomb[i].timer==((8*6)-4) && Bomb[i].state==2 ){ PAL_setPalette(PAL0, gfx_bg_main.palette->data,DMA); }
			//-------------------------------------------------------------------------------------------------------------------
			
			if( Bomb[i].timer==0 && Bomb[i].state==2)
			{ 
				BOMB_DESTROY(i); 
			}
			
			if(Bomb[i].state==1)
			{
				Bomb[i].x+=4;
			}
			if(Bomb[i].state==2)
			{
				Bomb[i].x++;
				gBomb_active=TRUE;
			}
			
			//atualiza a posicao do objeto na tela
			if(Bomb[i].sprite){ SPR_setPosition(Bomb[i].sprite, Bomb[i].x-48, Bomb[i].y-48); }
        }
    }
}

void BOMB_DESTROY(u8 i)
{
	if (Bomb[i].active)
	{
		Bomb[i].active = FALSE;
		if(Bomb[i].sprite)
		{ 
			SPR_releaseSprite(Bomb[i].sprite); 
			Bomb[i].sprite = NULL; 
		}
	}
}


//EOF; End of File
//GameDevBoss 2025 -> youtube.com/@GameDevBoss


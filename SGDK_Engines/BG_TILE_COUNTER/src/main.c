#include "genesis.h"
#include "gfx.h"
#include "sprite.h"

//--- VARIABLES ---//

#define HOW_FAR_TO_LEFT_BEFORE_CAMERA_MOVES 152
#define HOW_FAR_TO_RIGHT_BEFORE_CAMERA_MOVES 153 
#define HOW_FAR_TO_TOP_BEFORE_CAMERA_MOVES 115 
#define HOW_FAR_TO_BOTTOM_BEFORE_CAMERA_MOVES 116
#define HORIZONTAL_RESOLUTION 320
#define VERTICAL_RESOLUTION 224

//Global variables
u8   i;                //General purpose integer variable
u32  gFrames = 0;      //Frame Counter
u16  gRoom = 1;        //Game 'Room' (Menu, In game, etc)
u16  gInd_tileset;     //Variable used to load background data
Map* level_map;        //BGA map
Map* level_mapb;       //BGB map
u16 gBG_Width;         //Map Size X in pixels
u16 gBG_Height;        //Map Size Y in pixels
int current_camera_x;  //current camera position X
int current_camera_y;  //current camera position Y
int new_camera_x; 	   //new camera position X
int new_camera_y; 	   //new camera position Y
bool gPauseSystem = 0; //Pause System
bool gEnableMove = 1;  //Disables player inputs at specific times

//Player Struct
struct PlayerDEF {
	Sprite* sprite;     //Player Sprite
	s16 x;              //X
	s16 y;              //Y
	u8  axisX;          //Pivot Point X
	u8  axisY;          //Pivot Point Y
}; struct PlayerDEF P[3];

Sprite* tileNumber_x000;
Sprite* tileNumber_0x00;
Sprite* tileNumber_00x0;
Sprite* tileNumber_000x;

//--- FUNCTIONS ---//

void CAMERA();

int main(bool hardReset)
{
    //Init VDP (Video Display Processor)
	SYS_disableInts();
	 VDP_init();                   //Initializes the VDP (Video Display Processor)
	 VDP_setScreenWidth320();      //Default resolution of 320x224 (Width)
	 VDP_setScreenHeight224();     //Default resolution of 320x224 (Height)
	 VDP_setPlaneSize(64,32,TRUE); //Recommended for large BGs //old: SGDK 1.65
	 VDP_setTextPlane(BG_A);       //Texts will be drawn on BG_A
	 VDP_setTextPalette(PAL0);     //Texts will be drawn with the latest PAL0 color
	 SPR_initEx(420);              //420 is the default value of SGDK 1.80
	 VDP_setBackgroundColor(0);    //Range 0-63 //4 16 color palettes = 64 colors
	SYS_enableInts();
	
	if(!hardReset){ SYS_hardReset(); } //Prevent reset bug

	//--- MAIN LOOP ---//
    while(TRUE)
    {
		if(gPauseSystem==0)
		{ 
			gFrames++; 
		}
		VDP_showFPS(1); //Shows FPS rate
		CAMERA();
		
		/*TITLE ROOM*/
		if(gRoom==1)
		{
			if(gFrames==1)
			{
				gInd_tileset=0;
				PAL_setColors(0, palette_black, 64, DMA); 
				VDP_setBackgroundColor(0); //Range 0-63 //4 Paletas de 16 cores = 64 cores
				
				//BGB
				VDP_loadTileSet(&bg_bgb_tileset, gInd_tileset, DMA);
				level_mapb = MAP_create(&bg_bgb_map, BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, gInd_tileset)); 
				PAL_setPalette(PAL0, bg_bgb_pal.palette->data,DMA);
				gInd_tileset += bg_bgb_tileset.numTile;
				MAP_scrollTo(level_mapb, 0, 0);
				
				//BGA
				VDP_loadTileSet(&bg_bga_tileset, gInd_tileset, DMA);
				level_map = MAP_create(&bg_bga_map, BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, gInd_tileset)); 
				PAL_setPalette(PAL1, bg_bga_pal.palette->data,DMA);
				gInd_tileset += bg_bga_tileset.numTile;
				MAP_scrollTo(level_map, 0, 0);
				
				gBG_Width  = 736;
				gBG_Height = 256;
				
				//posiciona o "player" no meio do cenario, na parte de baixo / posicao inicial do player
				P[1].x=gBG_Width/2;
				P[1].y=gBG_Height-16;
				
				//exibe a quantide de tiles gastos no cenario: BGB+BGA
				u16 a;
				u16 b;
				u16 c;
				u16 d;
				
				      if(gInd_tileset==   0                      ){ a=0; 
				}else if(gInd_tileset>    0 && gInd_tileset<= 999){ a=0; 
				}else if(gInd_tileset>=1000 && gInd_tileset<=1999){ a=1; 
				}else if(gInd_tileset>=2000 && gInd_tileset<=2999){ a=2; 
				}
				
				b=gInd_tileset-(a*1000);
				
				      if(b==   0           ){ b=0; 
				}else if(b>    0 && b<=  99){ b=0; 
				}else if(b>= 100 && b<= 199){ b=1; 
				}else if(b>= 200 && b<= 299){ b=2; 
				}else if(b>= 300 && b<= 399){ b=3; 
				}else if(b>= 400 && b<= 499){ b=4; 
				}else if(b>= 500 && b<= 599){ b=5; 
				}else if(b>= 600 && b<= 699){ b=6; 
				}else if(b>= 700 && b<= 799){ b=7; 
				}else if(b>= 800 && b<= 899){ b=8; 
				}else if(b>= 900 && b<= 999){ b=9; 
				}
				
				c=gInd_tileset-(a*1000)-(b*100);
				
				      if(c==  0          ){ c=0; 				
				}else if(c>   0 && c<=  9){ c=0; 
				}else if(c>= 10 && c<= 19){ c=1; 
				}else if(c>= 20 && c<= 29){ c=2; 
				}else if(c>= 30 && c<= 39){ c=3; 
				}else if(c>= 40 && c<= 49){ c=4; 
				}else if(c>= 50 && c<= 59){ c=5; 
				}else if(c>= 60 && c<= 69){ c=6; 
				}else if(c>= 70 && c<= 79){ c=7; 
				}else if(c>= 80 && c<= 89){ c=8; 
				}else if(c>= 90 && c<= 99){ c=9; 
				}
				
				d=gInd_tileset-(a*1000)-(b*100)-(c*10);
				
				tileNumber_x000 = SPR_addSpriteExSafe(&spr_numbers, 0, 0, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), 1, SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | 0x800 );
				tileNumber_0x00 = SPR_addSpriteExSafe(&spr_numbers, 0, 0, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), 1, SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | 0x800 );
				tileNumber_00x0 = SPR_addSpriteExSafe(&spr_numbers, 0, 0, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), 1, SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | 0x800 );
				tileNumber_000x = SPR_addSpriteExSafe(&spr_numbers, 0, 0, TILE_ATTR(PAL3, FALSE, FALSE, FALSE), 1, SPR_FLAG_AUTO_VISIBILITY | SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD | 0x800 );
				
				SPR_setAnimAndFrame(tileNumber_x000, 0, a);
				SPR_setAnimAndFrame(tileNumber_0x00, 0, b);
				SPR_setAnimAndFrame(tileNumber_00x0, 0, c);
				SPR_setAnimAndFrame(tileNumber_000x, 0, d);
				
				PAL_setPalette(PAL3, spr_numbers.palette->data,DMA);
				
			}
			
			if(JOY_readJoypad(JOY_1) & BUTTON_UP   ){P[1].y--;}
			if(JOY_readJoypad(JOY_1) & BUTTON_DOWN ){P[1].y++;}
			if(JOY_readJoypad(JOY_1) & BUTTON_LEFT ){P[1].x--;}
			if(JOY_readJoypad(JOY_1) & BUTTON_RIGHT){P[1].x++;}
		}
		
		//--- FINALIZATIONS ---//
		VDP_showFPS(1); //Shows FPS rate
		
		if(gPauseSystem==0){ SPR_update(); } //Updates (draws) the sprites
        SYS_doVBlankProcess(); //Wait for screen refresh and do all SGDK VBlank tasks
    }

    return 0;
}

void CAMERA() 
{
	//stop player from leaving map
	if (P[1].x < 0) { P[1].x = 0; }
	if (P[1].x > gBG_Width) { P[1].x = gBG_Width; }
	if (P[1].y < 0) { P[1].y = 0; }
	if (P[1].y > gBG_Height) { P[1].y = gBG_Height; }
	
	//position of player on map as a whole number
	int player_x_map_integer = P[1].x; //fix32ToInt(P[1].x);
	int player_y_map_integer = P[1].y+4; //fix32ToInt(P[1].y);
	
	//player position on screen
	int player_x_position_on_screen = player_x_map_integer - current_camera_x;
	int player_y_position_on_screen = player_y_map_integer - current_camera_y;

	//calculate new camera position
	if (player_x_position_on_screen > HOW_FAR_TO_RIGHT_BEFORE_CAMERA_MOVES) {
		new_camera_x = player_x_map_integer - HOW_FAR_TO_RIGHT_BEFORE_CAMERA_MOVES;
	}
	else if (player_x_position_on_screen < HOW_FAR_TO_LEFT_BEFORE_CAMERA_MOVES) {
		new_camera_x = player_x_map_integer - HOW_FAR_TO_LEFT_BEFORE_CAMERA_MOVES;
	}
	else new_camera_x = current_camera_x;

	if (player_y_position_on_screen > HOW_FAR_TO_BOTTOM_BEFORE_CAMERA_MOVES) {
		new_camera_y = player_y_map_integer - HOW_FAR_TO_BOTTOM_BEFORE_CAMERA_MOVES;
	}
	else if (player_y_position_on_screen < HOW_FAR_TO_TOP_BEFORE_CAMERA_MOVES) {
		new_camera_y = player_y_map_integer - HOW_FAR_TO_TOP_BEFORE_CAMERA_MOVES;
	}
	else new_camera_y = current_camera_y;

	//stop camera from going beyond boundaries of map
	if (new_camera_x <= 0) {
		new_camera_x = 0;
	}
	else if (new_camera_x > (gBG_Width - HORIZONTAL_RESOLUTION)) {
		new_camera_x = gBG_Width - HORIZONTAL_RESOLUTION;
	}
	if (new_camera_y <= 0) {
		new_camera_y = 0;
	}
	else if (new_camera_y > (gBG_Height - VERTICAL_RESOLUTION)) {
		new_camera_y = gBG_Height - VERTICAL_RESOLUTION;
	}

	//check if camera needs to scroll and do the scroll
	if ( (current_camera_x != new_camera_x) || (current_camera_y != new_camera_y) ) {
		current_camera_x = new_camera_x;
		current_camera_y = new_camera_y;

		MAP_scrollTo(level_map, new_camera_x, new_camera_y);
		MAP_scrollTo(level_mapb, new_camera_x/2, new_camera_y/2);
	}

	//SPR_setPosition(P[1].sprite, (P[1].x-P[1].axisX) - new_camera_x, (P[1].y-P[1].axisY) - new_camera_y);
	SPR_setPosition(tileNumber_x000, (P[1].x+ 8) - new_camera_x, (P[1].y) - new_camera_y);
	SPR_setPosition(tileNumber_0x00, (P[1].x+16) - new_camera_x, (P[1].y) - new_camera_y);
	SPR_setPosition(tileNumber_00x0, (P[1].x+24) - new_camera_x, (P[1].y) - new_camera_y);
	SPR_setPosition(tileNumber_000x, (P[1].x+32) - new_camera_x, (P[1].y) - new_camera_y);
	
}
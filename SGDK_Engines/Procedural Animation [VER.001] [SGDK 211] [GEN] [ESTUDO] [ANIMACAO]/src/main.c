//////////////////////////////////////////////////////////////////////////////
// GAME by UsagiRu www.usagiru.blogspot.com                                 //
// Programming by Sir Macho                                                 //
// medium.com/@linhares.vinicius                                            //
//                                                                          //
// * @PROJECT:                  =>  # MINI GAMES COLLECTION                 //
// * @START-DATE:               =>  2024.01.05                              //
// * @LAST-UPDATE:              =>  2024.01.17                              //
// * @LIB:                      =>  SGDK (v1.70) by Stephane Dallongeville  //
//////////////////////////////////////////////////////////////////////////////

#include <genesis.h>
#include "bg.h"
#include "sound.h"
#include "sprites.h"
#include "segalogo.h"
#include "snake.h"

#define SNAKE_MOVE 255
#define SNAKE_COLLECT 254
#define SNAKE_DIE 253
#define SNAKE_LEVEL_UP 252

//u8  gRoom=0;       //'Room' of the game (Presentation screen, Menu, In game, etc.)
u32 gFrames = 0;   // Frames counter
u16 gInd_tileset;  // Variable used to load background data

s16 movePlanB;
s16 movePlanA;
s16 gScrollValues[28] = { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }; 
s16 gScrollValue;

Sprite *snake_logo;
Sprite *explosion;

u16 explosion_timer;

/**
 * @brief initialize game
 *
 * @param score - score
 * @param snakeSize - size of the snake
 * @param velocity - speed of the snake
 * @param dir - direction of the snake
 * @param snake - snake
 * @param apple - apple sprite
 */ 
u16 initGame(u16 *score, u8 *snakeSize, u8 *velocity,  SnakeNode *snake,  Sprite *ship)
{
    u16 vramIndex = bga_snake.tileset->numTile + bgb_snake.tileset->numTile + 16;
    VDP_setTextPlane(WINDOW);
    VDP_setWindowVPos(14,22);
    VDP_setTextPriority (1);
    
    //gRoom=0;
    //gFrames++; 
    
    char text[32];
    for(int i=0; i < 70 && snake[i].node != NULL; i++)
    {
        SPR_releaseSprite(snake[i].node);
        snake[i].node = NULL;
    }
    
    if(ship != NULL)
    {
        SPR_releaseSprite(ship);
        ship = NULL;
    }
    if(explosion != NULL)
    {
        SPR_releaseSprite(explosion);
        explosion = NULL;
    }

    
    
    SPR_reset();
    SPR_update();
    SYS_doVBlankProcess();
    
    *score = 0;
    *snakeSize = 3;
    *velocity = 0;
    VDP_clearTextLine(26); // Clean up texts on lines 26 and 27
    VDP_clearTextLine(27);

    VDP_setTextPalette(PAL1);
    VDP_loadFont(gfx_font.tileset,CPU);

    sprintf(text, "LEVEL-%d", *velocity);
    VDP_drawText(text, 16,27);
    sprintf(text, "SCORE-%d", *score);
    VDP_drawText(text, 1,26);
    
    VDP_clearTextLine(22); // Clean up texts on lines 22 and 23
    VDP_clearTextLine(23);
    
    VDP_drawText("PRESS START", 14,22);
    
    PAL_setPalette(PAL2, spr_snake.palette->data, DMA_QUEUE); // load the snake palette
    PAL_setPalette(PAL3, spr_snake_logo.palette->data, DMA_QUEUE); // load the logo palette

    snake_logo = SPR_addSprite(&spr_snake_logo, 112, 32, TILE_ATTR(PAL3, FALSE, FALSE, FALSE)); 

    return createSnake(snake, vramIndex);
}

/**
 * @brief - Shows gameover tex
 * 
 * @param score - score
 */
void gameOver(u16 score)
{
    XGM_startPlayPCM(SNAKE_DIE, 3, SOUND_PCM_CH4);

    char text[32];
    
    VDP_drawText("G", 15, 22);
    waitMs(50);
    VDP_drawText("A", 16, 22);
    waitMs(50);
    VDP_drawText("M", 17, 22);
    waitMs(50);
    VDP_drawText("E", 18, 22);
    waitMs(50);
    VDP_drawText(" ", 19, 22);
    waitMs(50);
    VDP_drawText("O", 20, 22);
    waitMs(50);
    VDP_drawText("V", 21, 22);
    waitMs(50);
    VDP_drawText("E", 22, 22);
    waitMs(50);
    VDP_drawText("R", 23, 22);
    waitMs(50);
    VDP_drawText("!", 24, 22); 
    
    sprintf(text, "LAST SCORE-%d_", score); 
    VDP_drawText(text, 1,25); 
    
    VDP_drawText("T", 15, 23);
    waitMs(50);
    VDP_drawText("R", 16, 23);
    waitMs(50);
    VDP_drawText("Y", 17, 23);
    waitMs(50);
    VDP_drawText(" ", 18, 23);
    waitMs(50);
    VDP_drawText("A", 19, 23);
    waitMs(50);
    VDP_drawText("G", 20, 23);
    waitMs(50);
    VDP_drawText("A", 21, 23);
    waitMs(50);
    VDP_drawText("I", 22, 23);
    waitMs(50);
    VDP_drawText("N", 23, 23);
    waitMs(50);
    VDP_drawText("!", 24, 23);    
}

/**
 * @brief initializes sound effect IDs
 */
void initSoundFX()
{
    XGM_setPCM(SNAKE_COLLECT, snake_collect, sizeof(snake_collect));
    XGM_setPCM(SNAKE_DIE, snake_die, sizeof(snake_die));
    XGM_setPCM(SNAKE_MOVE, snake_move, sizeof(snake_move));
    XGM_setPCM(SNAKE_LEVEL_UP, snake_level_up, sizeof(snake_level_up));
}

//void FUNCTION_INPUT_SYSTEM();

int main(bool hardReset)
{    
    if(!hardReset){SYS_hardReset();} 
    
    _segalogo( ); // Bios
  
    // Initialization of the VDP (Video Display Processor)
    SYS_disableInts(); // Disable switches
    VDP_init(); // Start VDP
    VDP_setScreenWidth320();  //Resolution X
    VDP_setScreenHeight224(); //Resolution Y
    SYS_enableInts(); // Reactivate switches
    SPR_init(); // Initialization of sprites

    gFrames=0;
    //gRoom=1;
    
    SPR_init();
    VDP_drawImage(BG_A, &bga_snake, 0, 0); // load the A background along with its palette
    VDP_drawImage(BG_B, &bgb_snake, 0, 0); // load the B background along with its palette
    PAL_setPalette(PAL1, gfx_font.palette->data, DMA_QUEUE); // load the font palette
    PAL_setPalette(PAL2, spr_snake.palette->data, DMA_QUEUE); // load the snake palette
    PAL_setPalette(PAL3, spr_snake_logo.palette->data, DMA_QUEUE); // load the logo palette
    
    PAL_fadeIn(0, 15, bga_snake.palette->data, 30, TRUE); 
    
    initSoundFX();
    
    Sprite *ship = NULL;

    u16 gFrames70 = 0;
    u8 velocity = 0;
    bool start = FALSE;
    u16 score = 0;
    u8 snakeSize = 3;
    bool needUpdate = FALSE;
    char text[32];

    // Initialize the game
    initGame(&score, &snakeSize, &velocity,  snake,  ship);

    VDP_drawText("PRESS START", 14,22);
    
    //XGM_startPlay(music); //intro song
    
    while(TRUE)
    {            
        gFrames++; 

/*    
if(gRoom==1) 
// ------------------------- LOGO SEGA -------------------------
{
	//FUNCTION_INPUT_SYSTEM(); //Verifica os joysticks
    gInd_tileset=1; 
	if(gFrames==1){_segalogo( );}
	if(gFrames>2) {PAL_fadeOutAll(20,0);  gFrames=0; } //CLEAR_VDP();
}
*/
       
        movePlanA += 1;
        movePlanB += 2;
        VDP_setHorizontalScroll(BG_B, movePlanB);
        VDP_setVerticalScroll(BG_B, movePlanB);
        VDP_setHorizontalScroll(BG_A, movePlanA);
        VDP_setVerticalScroll(BG_A, movePlanA);
        gScrollValue=1; 
    
        gFrames70++;
        if(gFrames70 > 70)
        {
            gFrames70 = 0;
        }
        
        u16 key = JOY_readJoypad(JOY_1);
        
        // if game has started
        if(start == TRUE)
        {                       
            PAL_setPalette(PAL3, spr_ship.palette->data, DMA_QUEUE); // load the ship palette
            
            SPR_setVisibility(snake[0].node, VISIBLE);
            SPR_setVisibility(snake[1].node, VISIBLE);
            SPR_setVisibility(snake[2].node, VISIBLE);
        
            
            if(gFrames % (4) == 0)
            {
                if(needUpdate)
                {
                    snakeAddNode(snake, snakeSize);
                    snakeSize++;
                    
                    // Increases the snake's speed whenever the size
                    // of the snake is a multiple of 8
                    // mostra explosão no frame 0
                    
                    if(snakeSize % 8 == 0)
                    {
                        // Tests if the speed is already maximum
                        if(velocity < 6)
                        {
                            velocity++; 
                            XGM_startPlayPCM(SNAKE_LEVEL_UP, 2, SOUND_PCM_CH4);
                            sprintf(text, "LEVEL-%d", velocity);
                            VDP_drawText(text, 16, 27);
                        }
                    }
                    if(snakeSize == 70)
                    {
                        gameOver(score);
                        initGame(&score, &snakeSize, &velocity, snake, ship);
                        start = FALSE;
                    }
                    needUpdate = FALSE;
                }
                moveSnake(snake);
                s8 col = snakeColision(snake, ship);
                
                if(col == 1)
                {
                    // Hit the ship
                    score = score + (velocity + 1);
                    u32 pos = divmodu(gFrames70, 10); // Calculate division and modulus at the same time
                    s16 x = ((pos >> 16) & 0xFFFF) * 32; // x = (gFrames70 mod 10)*32 
                    s16 y = (pos & 0xFFFF) * 32; // y = (gFrames70/10)*32

                    if(x > 288)
                    {
                        x = 0;
                    }
                    if(y > 192)
                    {
                        y = 0;
                    }

                    SPR_setPosition(ship, x, y);
                    sprintf(text, "SCORE-%d", score);
                    VDP_drawText(text, 1,26);
                    XGM_startPlayPCM(SNAKE_COLLECT, 1, SOUND_PCM_CH2);
                    
                    //move a explosão pra tela
                    SPR_setPosition(explosion, snake[0].x, snake[0].y);
                    SPR_setFrame(explosion, 0);
                    explosion_timer = 9*2;
                    
                    needUpdate = TRUE;
                }
                else if( col == -1)
                {
                    // Collision (Game Over)
                    PAL_setPalette(PAL2, snake_grey_pal.data, DMA_QUEUE); // load the dead snake palette                   
                    XGM_startPlay(snake_over); 
                    gameOver(score);
                    waitMs(5000);
                    initGame(&score, &snakeSize, &velocity,  snake, ship);
                    start = FALSE;
                }
            }

            //tempo do sprite explosion
            explosion_timer--;
            if(explosion_timer == 0)
            {
                //tira explosão da tela
                SPR_setPosition(explosion, 400, -20);
            }
        }
        else 
        {
            if(key & BUTTON_START) // Tests if "Start" button has been pressed
            {
                SPR_releaseSprite(snake_logo); snake_logo = NULL;
                u32 pos = divmodu(gFrames70, 10);
                ship = SPR_addSprite(&spr_ship, ((pos >> 16) & 0xFFFF) * 32, (pos & 0xFFFF) * 32, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));

                explosion = SPR_addSprite(&spr_explosion, 400 , -20, TILE_ATTR(PAL1, FALSE, FALSE, FALSE)); 
                SPR_setDepth(explosion, SPR_MIN_DEPTH); //255
                
                // Leave the ship in front of the snake
                SPR_setDepth(ship, SPR_MIN_DEPTH);
                VDP_clearTextLine(22); // Clean up texts on lines 22, 23 and 24
                VDP_clearTextLine(23);
                VDP_clearTextLine(24);
                start = TRUE;
                XGM_startPlay(snake_main);
            }
        }
        
        SPR_update();
        SYS_doVBlankProcess();
    }
    return (0);
}

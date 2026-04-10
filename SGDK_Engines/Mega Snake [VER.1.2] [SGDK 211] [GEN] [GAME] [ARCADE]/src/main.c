/**
 * @file main.c
 * @author Paulo linhares
 * @brief 
 * @version 0.1
 * @date 2022-08-31
 * 
 * @copyright Copyright (c) 2022
 * 
 */
#include <genesis.h>
#include "sprites.h" 
#include "bg.h"
#include "sound.h"
#include "snake.h"

#define COLLECT_ID 64
#define DIE_ID 65

/**
 * @brief initialize game
 * 
 * @param score game score
 * @param snakeSize snake size
 * @param velocity  snake velocity
 * @param snake     snake object
 * @param apple     apple sprite
 */
void initGame(u16 *score, u8 *snakeSize, u8 *velocity, SnakeNode *snake,  Sprite *apple)
{
    char text[32];

    for(int i=0; i < 70 && snake[i].node != NULL; i++)
    {
        SPR_releaseSprite(snake[i].node);
        snake[i].node = NULL;
    }
    if(apple != NULL)
    {
        SPR_releaseSprite(apple);
        apple = NULL;
    }
    SPR_reset();
    SPR_update();
    
    *score = 0;
    *snakeSize = 3;
    *velocity = 0;

    VDP_clearTextLine(1);
    VDP_clearTextLine(2);

    VDP_setTextPalette(PAL1);
    VDP_loadFont(gfx_fonte.tileset,CPU);

    sprintf(text, "LEVEL %d", *velocity);
    VDP_drawText(text, 1,1);
    sprintf(text, "SCORE %d", *score);
    VDP_drawText(text, 1,2);

    createSnake(snake);
    
}

/**
 * @brief Show game over text
 * 
 * @param start 
 * @param score 
 */
void gameOver(bool *start, u16 score)
{
    char text[32];
    *start = FALSE;
    
    VDP_drawText("G", 15, 20);
    waitMs(50);
    VDP_drawText("A", 16, 20);
    waitMs(50);
    VDP_drawText("M", 17, 20);
    waitMs(50);
    VDP_drawText("E", 18, 20);
    waitMs(50);
    VDP_drawText(" ", 19, 20);
    waitMs(50);
    VDP_drawText("O", 20, 20);
    waitMs(50);
    VDP_drawText("V", 21, 20);
    waitMs(50);
    VDP_drawText("E", 22, 20);
    waitMs(50);
    VDP_drawText("R", 23, 20);
    waitMs(50);
    VDP_drawText("!", 24, 20); 
    
    sprintf(text, "SCORE %d", score);
    VDP_drawText(text, 15,21); 
    
    VDP_drawText("T", 15, 22);
    waitMs(50);
    VDP_drawText("R", 16, 22);
    waitMs(50);
    VDP_drawText("Y", 17, 22);
    waitMs(50);
    VDP_drawText(" ", 18, 22);
    waitMs(50);
    VDP_drawText("A", 19, 22);
    waitMs(50);
    VDP_drawText("G", 20, 22);
    waitMs(50);
    VDP_drawText("A", 21, 22);
    waitMs(50);
    VDP_drawText("I", 22, 22);
    waitMs(50);
    VDP_drawText("N", 23, 22);
    waitMs(50);
    VDP_drawText("!", 24, 22);    
    
    XGM_startPlayPCM(DIE_ID, 1, SOUND_PCM_CH2);
}


int main()
{
    SPR_initEx(1136);
    SPR_reset();
    VDP_drawImage(BG_B, &bgb, 0, 0);
    PAL_setPalette(PAL1, gfx_fonte.palette->data, DMA);
    PAL_setPalette(PAL2, cobra_spr.palette->data, DMA);
    PAL_setPalette(PAL3, maca_spr.palette->data, DMA);
    
    SnakeNode snake[70];
    Sprite *apple = NULL;
    
    Direction dir = LEFT;
    u32 frame = 0;
    u16 frame70 = 0;
    u8 velocity = 0;
    u32 pos;
    bool start = FALSE;
    u16 score = 0;
    u8 snakeSize = 3;
    bool needUpdate = FALSE;

    XGM_setPCM(COLLECT_ID, collect, sizeof(collect));
    XGM_setPCM(DIE_ID, die, sizeof(die));

    
    char text[32];

    initGame(&score, &snakeSize, &velocity, snake,  apple);
    XGM_startPlay(music);
    
    while(1)
    {
        frame ++;
        frame70++;
        if(frame70 > 70)
        {
            frame70 = 0;
        }
        u16 key = JOY_readJoypad(JOY_1);
        // if game has started
        if(start == TRUE)
        {
            if((key & BUTTON_DOWN) && ((snake[0].dir == RIGHT) || (snake[0].dir == LEFT)))
            {
                dir = DOWN;
            }
            else if((key & BUTTON_UP) && ((snake[0].dir == RIGHT) || (snake[0].dir == LEFT)))
            {
                dir = UP;
            }
            else if((key & BUTTON_LEFT) && ((snake[0].dir == UP) || (snake[0].dir == DOWN)))
            {
                dir = LEFT;
            }
            else if((key & BUTTON_RIGHT) && ((snake[0].dir == UP) || (snake[0].dir == DOWN)))
            {
                dir = RIGHT;
            }
            if(frame % (64>>velocity) == 0)
            {
                if(needUpdate)
                {
                    snakeAddNode(snake, snakeSize);
                    snakeSize++;
                    if(snakeSize % 8 == 0)
                    {
                        velocity++;
                        sprintf(text, "LEVEL %d", velocity);
                        VDP_drawText(text, 1,1);
                    }
                    if(snakeSize == 70)
                    {
                        gameOver(&start, score);
                        initGame(&score, &snakeSize, &velocity, snake,  apple);
                    }
                    needUpdate = FALSE;
                }
                moveSnake(snake, dir);
                s8 col = snakeColision(snake, apple, &score, velocity, frame70);
                if(col == 1)
                {
                    sprintf(text, "SCORE %d", score);
                    VDP_drawText(text, 1,2);
                    XGM_startPlayPCM(COLLECT_ID, 1, SOUND_PCM_CH2);
                    needUpdate = TRUE;
                }
                else if( col == -1)
                {
                    gameOver(&start, score);
                    initGame(&score, &snakeSize, &velocity, snake,  apple);
                }
                
            }
        }
        else // game has not started yet
        {
            if(key & BUTTON_START) // test if start  key has pressed
            {
                pos = divmodu(frame70,10);
                apple = SPR_addSprite(&maca_spr, ((pos >> 16)& 0xFFFF) << 5, (pos & 0xFFFF) << 5, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
                SPR_setDepth(apple, SPR_MIN_DEPTH);
                VDP_clearTextLine(20);
                VDP_clearTextLine(21);
                VDP_clearTextLine(22);
                start = TRUE;
            }
        }

        SPR_update();
        SYS_doVBlankProcess();
    }
    return (0);
}

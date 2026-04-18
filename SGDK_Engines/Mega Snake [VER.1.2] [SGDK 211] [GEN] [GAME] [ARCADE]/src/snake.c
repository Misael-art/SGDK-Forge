/**
 * @file snake.c
 * @author Paulo Linhares
 * @brief 
 * @version 0.1
 * @date 2022-09-04
 * 
 * @copyright Copyright (c) 2022
 * 
 */

#include "snake.h"

void createSnake(SnakeNode *snake)
{
    snake[0].node = SPR_addSprite(&cobra_spr,64,96,TILE_ATTR(PAL2,FALSE,FALSE,FALSE));
    snake[1].node = SPR_addSprite(&cobra_spr,96,96,TILE_ATTR(PAL2,FALSE,FALSE,FALSE));
    snake[2].node = SPR_addSprite(&cobra_spr,128,96,TILE_ATTR(PAL2,FALSE,TRUE,TRUE));
    
    snake[0].x = 64;
    snake[1].x = 96;
    snake[2].x = 128;

    snake[0].y = 96;
    snake[1].y = 96;
    snake[2].y = 96;

    snake[0].dir = LEFT;
    snake[1].dir = LEFT;
    snake[2].dir = LEFT;

    snake[0].lastDir = LEFT;
    snake[1].lastDir = LEFT;
    snake[2].lastDir = LEFT;

    SPR_setAnim(snake[0].node, 4);
    SPR_setAnim(snake[1].node, 3);
    SPR_setAnim(snake[2].node, 0);

}   

void moveSnake(SnakeNode *snake, Direction d)
{
    int i;

    snake[0].lastDir = snake[0].dir;
    snake[0].dir = d;
    
    //move head and change sprite
    if( snake[0].dir == RIGHT)
    {
        snake[0].x = snake[0].x + 32;
        SPR_setAnim(snake[0].node, 4);
        SPR_setHFlip(snake[0].node, TRUE);
        SPR_setVFlip(snake[0].node, FALSE);
    }
    else if( snake[0].dir == LEFT)
    {
        snake[0].x = snake[0].x - 32;
        SPR_setAnim(snake[0].node, 4);
        SPR_setHFlip(snake[0].node, FALSE);
        SPR_setVFlip(snake[0].node, FALSE);
    }
    else if( snake[0].dir == DOWN)
    {
        snake[0].y= snake[0].y + 32;
        SPR_setAnim(snake[0].node, 1);
        SPR_setVFlip(snake[0].node, FALSE);
        SPR_setHFlip(snake[0].node, FALSE);
    }
    else if(  snake[0].dir == UP)
    {
        snake[0].y= snake[0].y - 32;
        SPR_setAnim(snake[0].node, 1);
        SPR_setVFlip(snake[0].node, TRUE);
        SPR_setHFlip(snake[0].node, TRUE);
    }
    
    SPR_setPosition(snake[0].node, snake[0].x, snake[0].y);

    bool changed = FALSE;
    //move body and change sprite
    for(i=1; i < 70 && snake[i].node != NULL; i++)
    {
        changed = FALSE;
        // save last direction of snake node
        snake[i].lastDir = snake[i].dir;
        // update direction of snake node
        snake[i].dir =  snake[i-1].lastDir;
        
        // test if direction of before node as changed
        if(snake[i].dir != snake[i-1].dir)
        {
            changed = TRUE;
            SPR_setAnim(snake[i].node, 2);
        }
        // update snake node sprite
        if(snake[i].dir == RIGHT)
        {
            snake[i].x = snake[i].x + 32;
            if(!changed)
            {
                SPR_setAnim(snake[i].node, 3);
                SPR_setHFlip(snake[i].node, FALSE);
                SPR_setVFlip(snake[i].node, FALSE);
            }
            else
            {
                if(snake[i -1].dir == UP)
                {
                    SPR_setVFlip(snake[i].node, TRUE);
                    SPR_setHFlip(snake[i].node, FALSE);
                }
                else
                {
                    SPR_setVFlip(snake[i].node, FALSE);
                    SPR_setHFlip(snake[i].node, FALSE);
                }
            }
        }
        else if(snake[i].dir == LEFT)
        {
            snake[i].x = snake[i].x - 32;;
            if(!changed)
            {
                SPR_setAnim(snake[i].node, 3);
                SPR_setVFlip(snake[i].node, FALSE);
                SPR_setVFlip(snake[i].node, FALSE);
            }
            else if(snake[i -1].dir == UP)
            {
                SPR_setVFlip(snake[i].node, TRUE);
                SPR_setHFlip(snake[i].node, TRUE);
            }
            else
            {
                SPR_setVFlip(snake[i].node, FALSE);
                SPR_setHFlip(snake[i].node, TRUE);
            }
        }
        else if( snake[i].dir == DOWN)
        {
            snake[i].y = snake[i].y + 32;;
            if(!changed)
            {
                SPR_setAnim(snake[i].node, 6);
                SPR_setHFlip(snake[i].node, FALSE);
                SPR_setVFlip(snake[i].node, FALSE);
            }
            else if(snake[i -1].dir == LEFT)
            {
                SPR_setVFlip(snake[i].node, TRUE);
                SPR_setHFlip(snake[i].node, FALSE);
            }
            else
            {
                SPR_setVFlip(snake[i].node, TRUE);
                SPR_setHFlip(snake[i].node, TRUE);
            } 
        }
        else if( snake[i].dir == UP)
        {
            snake[i].y = snake[i].y - 32;;
            if(!changed)
            {
                SPR_setAnim(snake[i].node, 6);
                SPR_setHFlip(snake[i].node, TRUE);
                SPR_setVFlip(snake[i].node, TRUE);
            }
            else if(snake[i -1].dir == LEFT)
            {
                SPR_setVFlip(snake[i].node, FALSE);
                SPR_setHFlip(snake[i].node, FALSE);
            }
            else
            {
                SPR_setVFlip(snake[i].node, FALSE);
                SPR_setHFlip(snake[i].node, TRUE);
            }
        } 
        SPR_setPosition(snake[i].node, snake[i].x, snake[i].y);
    }
    //adjust tail sprite
    if(!changed)
    {
        if(snake[i-1].dir == RIGHT)
        {
            SPR_setAnim(snake[i-1].node, 0);
            SPR_setHFlip(snake[i-1].node, FALSE);
            SPR_setVFlip(snake[i-1].node, TRUE);
        }
        else if(snake[i-1].dir == LEFT)
        {
            SPR_setAnim(snake[i-1].node, 0);
            SPR_setHFlip(snake[i-1].node, TRUE);
            SPR_setVFlip(snake[i-1].node, TRUE);
        }
        else if(snake[i-1].dir == DOWN)
        {
            SPR_setAnim(snake[i-1].node, 5);
            SPR_setVFlip(snake[i-1].node, FALSE);
            SPR_setHFlip(snake[i-1].node, FALSE);
        }
        else if(snake[i-1].dir == UP)
        {
            SPR_setAnim(snake[i-1].node, 5);
            SPR_setVFlip(snake[i-1].node, TRUE);
            SPR_setHFlip(snake[i-1].node, TRUE);
        }
    }
}

void snakeAddNode(SnakeNode *snake, u8 lenght)
{
    //test if snake has the maximum lenght
    if(lenght < 71)
    {
        u16 x  = snake[lenght-1].x;
        u16 y = snake[lenght-1].y;
        //add next node behindg the snake
        if(snake[lenght-1].dir == UP)
        {
            y = y+32; 
        }
        else if(snake[lenght-1].dir == DOWN)
        {
            y = y-32; 
        }
        else if(snake[lenght-1].dir == RIGHT)
        {
            x = x-32; 
        }
        else if(snake[lenght-1].dir == LEFT)
        {
            x = x+32; 
        }
        snake[lenght].node = SPR_addSprite(&cobra_spr, x, y,TILE_ATTR(PAL2,FALSE,TRUE,TRUE));
        snake[lenght].x = x;
        snake[lenght].y = y;
    }
}

int snakeColision(SnakeNode *snake, Sprite *apple, u16 *score, u8 velocity, u16 frame70)
{
    //test colision with himself
    for(u8 i=1; i < 70 && snake[i].node != NULL; i++)
    { 
        if((snake[0].x == snake[i].x) && (snake[0].y == snake[i].y))
        {
            KLog("snakeColision dead by himself");
            return -1;
        }
    }
    //test colision with apple
    if(snake[0].node->x == apple->x && snake[0].node->y == apple->y)
    {
        KLog("snakeColision apple detected");
        *score = *score + (velocity+1);
        u32 pos = divmodu(frame70,10);
        s16 x = ((pos >> 16)& 0xFFFF) << 5;
        s16 y = (pos & 0xFFFF) << 5;

        if(x > 288)
        {
            x = 0;
        }
        if(y > 192)
        {
            y = 0;
        }
        KLog_S2(" ax ", x, " ay ", y);
        SPR_setPosition(apple, x, y);
        return 1;
    }
    //test colision with wall
    if(snake[0].x < 0 || snake[0].x > 288 || snake[0].y < 0 || snake[0].y > 192)
    {
        KLog("snakeColision dead by wall");
        return -1;
    }

    return 0;
}
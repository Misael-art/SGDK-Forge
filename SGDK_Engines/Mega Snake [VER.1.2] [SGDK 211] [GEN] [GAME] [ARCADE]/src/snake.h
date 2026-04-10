/**
 * @file snake.h
 * @author Paulo Linhares
 * @brief 
 * @version 0.1
 * @date 2022-09-04
 * 
 * @copyright Copyright (c) 2022
 * 
 */


#ifndef __SNAKE__
#define __SNAKE__

#include <genesis.h>
#include "sprites.h" 

typedef enum 
{
    UP,
    LEFT,
    DOWN,
    RIGHT
}Direction;

typedef struct 
{   
    Sprite *node;
    s16 x;
    s16 y;
    Direction dir;
    Direction lastDir;
}SnakeNode;


/**
 * @brief initialize a Snake object 
 * 
 * @param snake snake object
 */
void createSnake(SnakeNode *snake);

/**
 * @brief move snake in cenario
 * 
 * @param snake snake object
 * @param d direction to move
 */
void moveSnake(SnakeNode *snake, Direction d);

/**
 * @brief add a snake node
 * 
 * @param snake snake object
 * @param lenght actual snake lenght
 */
void snakeAddNode(SnakeNode *snake, u8 lenght);

/**
 * @brief Detect snake colision
 * 
 * @param snake snake object
 * @param apple apple sprite
 * @param score actual score
 * @param velocity actual velocity
 * @param frame70 frame counter
 * @return 0 if not colide, 1 if colide with apple and -1 if die
 */
int snakeColision(SnakeNode *snake, Sprite *apple, u16 *score, u8 velocity, u16 frame70);


#endif
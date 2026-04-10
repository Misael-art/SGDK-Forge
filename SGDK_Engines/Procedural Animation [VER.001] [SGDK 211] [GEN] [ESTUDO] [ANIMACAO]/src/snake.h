#ifndef __SNAKE__
#define __SNAKE__

#include <genesis.h>
#include "sprites.h" 

#define SNAKE_MAX_SIZE 70


// Structure that defines the type that will store the snake's nodes
typedef struct 
{   
    Sprite *node;           // Link sprite
    s16 x;                  // Link x position
    s16 y;                  // y position of the link
    fix16 velX;
    fix16 velY;
    fix16 posX;
    fix16 posY;
}SnakeNode;

// Variable that stores all the snake's nodes
extern SnakeNode snake[SNAKE_MAX_SIZE]; 

/**
 * @brief - initializes the snake
 *  
 * @param snake - snake node
 */
u16 createSnake(SnakeNode *snake,  u16 vramIndex);

/**
 * @brief - moves the snake on the stage
 *
 * @param snake - snake node
 */
void moveSnake(SnakeNode *snake);

/**
* @brief - adds a node to the snake
 *
 * @param snake - snake
 * @param length - size of the snake
 */
void snakeAddNode(SnakeNode *snake, u8 lenght);

/**
 * @brief - Collisions tests
 *
 * @param snake - snake
 * @param ship - ship sprite
 * @return 0 if you didn't collide, 1 if you collided with an ship and -1 if you died
 */
int snakeColision(SnakeNode *snake, Sprite *ship);

#endif

#include "snake.h"

u16** sprTileIndexes;
SnakeNode snake[SNAKE_MAX_SIZE];

static void frameChanged(Sprite* sprite);

u16 createSnake(SnakeNode *snake,  u16 vramIndex)
{
    u16 numTile;
    u16 ind;
    //Create the sprites of the snake's 3 initial nodes
    snake[0].node = SPR_addSprite(&spr_snake,128,96,TILE_ATTR(PAL2,FALSE,FALSE,FALSE));
    snake[1].node = SPR_addSprite(&spr_snake,160,96,TILE_ATTR(PAL2,FALSE,FALSE,FALSE));
    snake[2].node = SPR_addSprite(&spr_snake,192,96,TILE_ATTR(PAL2,FALSE,TRUE,TRUE));
    
    // Adjust x position of each node
    snake[0].x = 128;
    snake[1].x = 160;
    snake[2].x = 192;
    snake[0].posX = FIX16(128);
    snake[1].posX = FIX16(160);
    snake[2].posX = FIX16(192);

    // Adjust the y position of each node
    snake[0].y = 96;
    snake[1].y = 96;
    snake[2].y = 96;

    snake[0].posY = FIX16(96);
    snake[1].posY = FIX16(96);
    snake[2].posY = FIX16(96);

    snake[0].velX = FIX16(-1);
    snake[1].velX = FIX16(-1);
    snake[2].velX = FIX16(-1);

    snake[0].velY = FIX16(0);
    snake[1].velY = FIX16(0);
    snake[2].velY = FIX16(0);

    // Select the animation for each node
    SPR_setAnim(snake[0].node, 4); 
    SPR_setAnim(snake[1].node, 3); 
    SPR_setAnim(snake[2].node, 0); 
    
    SPR_setDepth(snake[0].node, SPR_MAX_DEPTH);
    SPR_setDepth(snake[1].node, SPR_MAX_DEPTH);
    SPR_setDepth(snake[2].node, SPR_MAX_DEPTH);

    SPR_setAutoTileUpload(snake[0].node, FALSE);
    SPR_setAutoTileUpload(snake[1].node, FALSE);
    SPR_setAutoTileUpload(snake[2].node, FALSE);

    SPR_setFrameChangeCallback(snake[0].node, &frameChanged);
    SPR_setFrameChangeCallback(snake[1].node, &frameChanged);
    SPR_setFrameChangeCallback(snake[2].node, &frameChanged);

    SPR_setVisibility(snake[0].node, HIDDEN);
    SPR_setVisibility(snake[1].node, HIDDEN);
    SPR_setVisibility(snake[2].node, HIDDEN);
    
    ind = vramIndex;
    sprTileIndexes = SPR_loadAllFrames(&spr_snake, ind, &numTile);
    ind = ind + numTile;
    return ind;
}   

void moveSnake(SnakeNode *snake)
{
    int i;

    s16 joy = JOY_readJoypad(JOY_1);

    if (joy & BUTTON_DOWN && joy & BUTTON_LEFT){
        snake[0].velX -= FIX16(0.17677669525);
        if (snake[0].velX < FIX16(-2.5)){
            snake[0].velX = FIX16(-2.5);
        }
        snake[0].velY += FIX16(0.17677669525);
        if (snake[0].velY > FIX16(2.5)){
            snake[0].velY = FIX16(2.5);
        }
    }else if (joy & BUTTON_DOWN && joy & BUTTON_RIGHT){
        snake[0].velX += FIX16(0.17677669525);
        if (snake[0].velX > FIX16(2.5)){
            snake[0].velX = FIX16(2.5);
        }
        snake[0].velY += FIX16(0.17677669525);
        if (snake[0].velY > FIX16(2.5)){
            snake[0].velY = FIX16(2.5);
        }
    }else if (joy & BUTTON_UP && joy & BUTTON_RIGHT){
        snake[0].velX += FIX16(0.17677669525);
        if (snake[0].velX > FIX16(2.5)){
            snake[0].velX = FIX16(2.5);
        }
        snake[0].velY -= FIX16(0.17677669525);
        if (snake[0].velY < FIX16(-2.5)){
            snake[0].velY = FIX16(-2.5);
        }
    }if (joy & BUTTON_UP && joy & BUTTON_LEFT){
        snake[0].velX -= FIX16(0.17677669525);
        if (snake[0].velX < FIX16(-2.5)){
            snake[0].velX = FIX16(-2.5);
        }
        snake[0].velY -= FIX16(0.17677669525);
        if (snake[0].velY < FIX16(-2.5)){
            snake[0].velY = FIX16(-2.5);
        }
    }
    else if (joy & BUTTON_UP ){
        snake[0].velY -= FIX16(0.25);
        if (snake[0].velY < FIX16(-2.5)){
            snake[0].velY = FIX16(-2.5);
        }
    }else if (joy & BUTTON_DOWN ){
        snake[0].velY += FIX16(0.25);
        if (snake[0].velY > FIX16(2.5)){
            snake[0].velY = FIX16(2.5);
        }
    }else if ( joy & BUTTON_LEFT){
        snake[0].velX -= FIX16(0.25);
        if (snake[0].velX < FIX16(-2.5)){
            snake[0].velX = FIX16(-2.5);
        }
    }else if ( joy & BUTTON_RIGHT){
        snake[0].velX += FIX16(0.25);
        if (snake[0].velX > FIX16(2.5)){
            snake[0].velX = FIX16(2.5);
        }
    }

    snake[0].posX += snake[0].velX;
    snake[0].posY += snake[0].velY;

    snake[0].x = F16_toRoundedInt(snake[0].posX); 
    snake[0].y = F16_toRoundedInt(snake[0].posY);     
   
    // Adjust the position of the snake's head
    SPR_setPosition(snake[0].node, snake[0].x, snake[0].y);

    // Move the rest of the snake's body
    for(i=1; i < SNAKE_MAX_SIZE && snake[i].node != NULL; i++)
    {
        fix16 dx = snake[i-1].posX - snake[i].posX;
        fix16 dy = snake[i-1].posY - snake[i].posY;

        fix16 distance = getApproximatedDistance(dx, dy);

        if (distance != 0){
            fix16 newX = (dx*FIX16(32))/distance;
            fix16 newY = (dy*FIX16(32))/distance;
            snake[i].posX = snake[i-1].posX - newX;
            snake[i].posY = snake[i-1].posY - newY;
        }

        snake[i].x = F16_toRoundedInt(snake[i].posX); 
        snake[i].y = F16_toRoundedInt(snake[i].posY);  

        SPR_setPosition(snake[i].node, snake[i].x, snake[i].y);
    }
    
}

void snakeAddNode(SnakeNode *snake, u8 lenght)
{
    // Test if snake has the maximum lenght
    if(lenght < SNAKE_MAX_SIZE) 
    {
        u16 x  = snake[lenght-1].x;
        u16 y = snake[lenght-1].y;

        x = x+32; 
        
        snake[lenght].node = SPR_addSprite(&spr_snake, x, y,TILE_ATTR(PAL2,FALSE,TRUE,TRUE));
        snake[lenght].x = x;
        snake[lenght].y = y;

        SPR_setAutoTileUpload(snake[lenght].node, FALSE);
        SPR_setFrameChangeCallback(snake[lenght].node, &frameChanged);
    }
}

int snakeColision(SnakeNode *snake, Sprite *ship)
{

    // Collision test with itself
    // for(u8 i=1; i < 70 && snake[i].node != NULL; i++)
    // { 
    //     if((snake[0].x == snake[i].x) && (snake[0].y == snake[i].y))
    //     {
    //         kprintf("colidiu consigo mesma");
    //         return -1;
    //     }
    // }

    // Collision test with the ship
    if(snake[0].node->x == ship->x && snake[0].node->y == ship->y)
    {
        return 1;
    }

    // Collision test with the wall
    if(snake[0].x < 0 || snake[0].x > 288 || snake[0].y < 0 || snake[0].y > 192) 
    {
        kprintf("colidiu com a parede");
        return -1;
    }

    return 0;
}

static void frameChanged(Sprite* sprite)
{
    // get VRAM tile index for this animation of this sprite
    u16 tileIndex = sprTileIndexes[sprite->animInd][sprite->frameInd];
    // manually set tile index for the current frame (preloaded in VRAM)
    SPR_setVRAMTileIndex(sprite, tileIndex);
}
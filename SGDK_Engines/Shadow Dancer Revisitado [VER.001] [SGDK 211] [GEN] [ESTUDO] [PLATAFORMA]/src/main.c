#include <genesis.h>
#include <resources.h>

#include <mapHandler.h>

#define ANIM_STAND       0
#define ANIM_WALK        4

//

#define VELOCIDADE       FIX32(2)   //velocidade do jogador
#define PULO_VEL         FIX32(-6)  //intensidade do pulo
#define GRAVIDADE        FIX32(0.2) //incremento de gravidade
#define GRAVIDADE_MAX    FIX32(8.0) //valor maximo da gravidade

//

const u32 largurabigmap[4] = {2048,2000,2048,2560}; //largura de cada cenario
const u32 alturabigmap[4] = {256,416,256,512};      //altura de cada cenario

const MapDefinition *arquivobigmap[4] = {&mBigMap0,&mBigMap1,&mBigMap2,&mBigMap3 };
const TileSet *tilesetbigmap[4] = {&tsBigMap0,&tsBigMap1,&tsBigMap2,&tsBigMap3};
const Palette *palettebigmap[4] = {&pBigMap0,&pBigMap1,&pBigMap2,&pBigMap3};
const Image *bigmapcolisao[4] = {&colisao0,&colisao1,&colisao2,&colisao3};

struct jogadores
{
    s8 eixo;
    s8 eixoY;

    fix32 velX;
    fix32 velY;

    fix32 posX;
    fix32 posY;

    u8 grounded;
    u8 pulo;

    Sprite* spr;
};

struct jogadores player;

Map* bigmap;
TileMap* colisoes;

fix32 cameraX, cameraY;

/* ESCOLHA A FASE INICIAL (fase 0 a 3) */
u8 fase = 1;

bool gravityOn;

static void handleInput()
{
    u16 value = JOY_readJoypad(0);

    if ((value & BUTTON_DOWN)) player.eixoY = 1;
    else if ((value & BUTTON_UP)) player.eixoY = -1;
    else player.eixoY = 0;

    if ((value & BUTTON_LEFT)) player.eixo = -1;
    else if ((value & BUTTON_RIGHT)) player.eixo = 1;
    else player.eixo = 0;
}

void PLAYER_doJoyAction(u16 joy, u16 changed, u16 state)
{
    if  (changed & state & (BUTTON_B | BUTTON_C))
    {
        if (gravityOn)
        {

            //so pula se estiver no chao
            if (player.grounded)
            {
                player.velY = PULO_VEL;
            }
        
            //pula independente se esta no chao ou nao
            //player.velY = PULO_VEL;

        }

        
    }

    if (changed & state & BUTTON_A)
    {
        if (gravityOn) gravityOn = FALSE;
        else gravityOn = TRUE;
    }
}

static void joyEvent(u16 joy, u16 changed, u16 state)
{
    PLAYER_doJoyAction(joy, changed, state);
}

static void moveJogador()
{
    if (gravityOn)
    {
        if (player.eixo > 0 )
        {
            player.velX = VELOCIDADE;
            SPR_setHFlip(player.spr,FALSE);
        }
        else if (player.eixo < 0 ) 
        {
            player.velX = -VELOCIDADE;
            SPR_setHFlip(player.spr,TRUE);
        }
        else if (player.eixo == 0 ) player.velX = 0;

        if (player.velY < GRAVIDADE_MAX) player.velY += GRAVIDADE;

        s8 bbox_side;   //metade da largura do sprite do jogador
        u8 bbox_altura; //altura do sprite do jogador
        u32 p1;
        u32 p2;
        u32 p3;
        u32 p4;

        bbox_side = 0;
        bbox_altura = 64;

        //colisao horizontal

        if (player.eixo > 0)
        {
            bbox_side = 16; //metade da largura do sprite do jogador
        }
        else if (player.eixo < 0)
        {
            bbox_side = -16; //valor negativo da metade da largura do sprite do jogador
        }

        if (player.posY  > FIX32(8) &&
            colisoes->tilemap[(F32_toInt(player.posX + FIX32(bbox_side) + player.velX )>>3)+((F32_toInt(player.posY -FIX32(8))>>3)*(largurabigmap[fase]>>3) )] == 1 )
        {
            player.velX = 0;
        }

        player.posX += player.velX;

        //colisao vertical

        bbox_side = 16;
        if (player.velY >= 0) bbox_altura = 0;
        else bbox_altura = 64;

        p1 = colisoes->tilemap[(F32_toInt(player.posX -FIX32(bbox_side) )>>3)+((F32_toInt(player.posY -FIX32(bbox_altura) )>>3)*(largurabigmap[fase]>>3))] ;
        p2 = colisoes->tilemap[(F32_toInt(player.posX +FIX32(bbox_side) )>>3)+((F32_toInt(player.posY -FIX32(bbox_altura) )>>3)*(largurabigmap[fase]>>3))] ;
        p3 = colisoes->tilemap[(F32_toInt(player.posX )>>3)+((F32_toInt(player.posY -FIX32(bbox_altura) )>>3)*(largurabigmap[fase]>>3))] ;
        p4 = colisoes->tilemap[(F32_toInt(player.posX )>>3)+((F32_toInt(player.posY)>>3)*(largurabigmap[fase]>>3))] ;

        if ( player.posY -FIX32(bbox_altura) > FIX32(bbox_altura + 8) && ((p1 == 1 && p3 == 1  )
            || (p1 == 2 && p4 == 2 && !bbox_altura  )
            || (p2 == 1 && p3 == 1  )
            || (p2 == 2 && p4 == 2 && !bbox_altura  )
            ))
        {
            player.velY = 0;

            if ( F32_toInt(player.posY) % 8 != 0 && !bbox_altura)
            {
                u8 tempY = F32_toInt(player.posY) % 8;
                player.posY -= FIX32(tempY);
            }

            if (!bbox_altura) player.grounded = 1;
        }

        player.posY += player.velY;
        
        p1 = colisoes->tilemap[(F32_toInt(player.posX -FIX32(bbox_side) )>>3)+((F32_toInt(player.posY +FIX32(4) )>>3)*(largurabigmap[fase]>>3))] ;
        p2 = colisoes->tilemap[(F32_toInt(player.posX +FIX32(bbox_side) )>>3)+((F32_toInt(player.posY +FIX32(4) )>>3)*(largurabigmap[fase]>>3))] ;
        p3 = colisoes->tilemap[(F32_toInt(player.posX )>>3)+((F32_toInt(player.posY +FIX32(4) )>>3)*(largurabigmap[fase]>>3))] ;
        

        if (player.velY < 0)
        {
            player.grounded = 0;
        }
        else if (player.velY >= 0 && 
            ((p1 == 0 && p2 == 0) || p3 == 0))
        {
            player.grounded = 0;
        }

    }
    else
    {
        if (player.eixoY > 0 ) player.posY += FIX32(4);
        else if (player.eixoY < 0 ) player.posY -= FIX32(4);

        if (player.eixo > 0 ) player.posX += FIX32(4);
        else if (player.eixo < 0 ) player.posX -= FIX32(4);

        player.velX = 0;
        player.velY = 0;
    }



    SPR_setPosition(player.spr,F32_toInt(player.posX - cameraX) - (player.spr->definition->w>>1) ,F32_toInt(player.posY - cameraY) - (player.spr->definition->h) );
    
    if (player.eixo || player.eixoY)
    {
        SPR_setAnim(player.spr,ANIM_WALK);
    }
    else
    {
        SPR_setAnim(player.spr,ANIM_STAND);
    }
}

static void updateCameraPosition()
{
    fix32 px = player.posX;
    fix32 py = player.posY;

    fix32 camX = cameraX;
    fix32 camY = cameraY;

    // current sprite position on screen
    fix32 px_scr = px - camX;
    fix32 py_scr = py - camY;

    fix32 npx_cam, npy_cam;

    // adjust new camera position
    if (px_scr > FIX32(180)) npx_cam = px - FIX32(180);
    else if (px_scr < FIX32(140)) npx_cam = px - FIX32(140);
    else npx_cam = camX;

    if (py_scr > FIX32(140)) npy_cam = py - FIX32(140);
    else if (py_scr < FIX32(112)) npy_cam = py - FIX32(112);
    else npy_cam = camY;

    if ((npx_cam != camX) || (npy_cam != camY))
    {
        cameraX = npx_cam;
        cameraY = npy_cam;

        cameraX = clamp(cameraX, FIX32(0), FIX32( largurabigmap[fase] - 320));
        cameraY = clamp(cameraY, FIX32(0), FIX32( alturabigmap[fase] - 224));

        //cameraX = clamp(cameraX, FIX32(0), FIX32( (bigmap->w<<7) - 320));
        //cameraY = clamp(cameraY, FIX32(0), FIX32( (bigmap->h<<7) - 224));

        int16_t camXtemp;
        int16_t camYtemp;

        camXtemp = F32_toInt(cameraX);
        camYtemp = F32_toInt(cameraY);

        MAP_scrollTo(bigmap, camXtemp,camYtemp);
    }    
}

int main(bool resetType) 
{
    if (!resetType) SYS_hardReset();

    VDP_setScreenHeight224();
    VDP_setScreenWidth320();

    PAL_setPalette(PAL1,palettebigmap[fase]->data,DMA);
    PAL_setPalette(PAL2,playerSpr.palette->data, DMA);

    JOY_setEventHandler(joyEvent);

    //SYS_showFrameLoad(true);

    // need to increase a bit DMA buffer size to init both plan tilemap and sprites
    DMA_setBufferSize(10000);
    DMA_setMaxTransferSize(10000);

    uint16_t vram = 1;

    bigmap = MAP_create((const MapDefinition *) arquivobigmap[fase], BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, 0));
    vram = tileCache_init(vram, (const TileSet *) tilesetbigmap[fase], 576); // (64*5) - 1
    MAP_setDataPatchCallback(bigmap, tileCache_callback);

    colisoes = bigmapcolisao[fase]->tilemap;

    SPR_init();

    player.posX = FIX32(128);
    player.posY = FIX32(112);

    player.spr = SPR_addSprite(&playerSpr, F32_toInt(player.posX), F32_toInt(player.posY), TILE_ATTR(PAL2, FALSE, FALSE, FALSE));

    uint16_t debugFrames = 10;
    while(1)
    {
        handleInput();

        moveJogador();

        updateCameraPosition();
        
        --debugFrames;
        if(debugFrames == 0)
        {
            tileCache_print();
            debugFrames = 10;
        }

        SPR_update();

        SYS_doVBlankProcess();       
    }
}
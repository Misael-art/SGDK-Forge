/**
 * Hello World Example
 * Created With Genesis-Code extension for Visual Studio Code
 * Use "Genesis Code: Compile" command to compile this program.
 **/
#include <genesis.h>
#include "bg.h"


bool TileFadeIn(s16 row, u16 tileIndex){
    
    if( row == 14){
        VDP_setTileMapRowEx(BG_A, bga.tilemap,TILE_ATTR_FULL(PAL1, FALSE, FALSE,FALSE, tileIndex),14, 0, 14, 40, DMA_QUEUE);
    }else if(row >= 0){
        VDP_setTileMapRowEx(BG_A, bga.tilemap,TILE_ATTR_FULL(PAL1, FALSE, FALSE,FALSE, tileIndex),row, 0, row, 40,DMA_QUEUE);
        VDP_setTileMapRowEx(BG_A, bga.tilemap,TILE_ATTR_FULL(PAL1, FALSE, FALSE,FALSE, tileIndex),28-row, 0, 28-row,40,DMA_QUEUE);
    }
    else{
        return TRUE;
    }
    return FALSE;
}


bool TileFadeOut(s16 row, u16 tileIndex){
    if(row < 14){
        VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0, TRUE, FALSE,FALSE, tileIndex),0,row,40,1);
        VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0, TRUE, FALSE,FALSE, tileIndex),0,28-row,40,1);
    }
    else if( row == 14){
        VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0, TRUE, FALSE,FALSE, tileIndex),0,row,40,1);
        return TRUE;
    }
    return FALSE;
}


void TileFideOutMosic1(s16 row, TileSet *t, u16 index){
    for (u32 i = 0; i < t->numTile*8; i = i + 8){
        t->tiles[row + i] = 0;
    }
    VDP_loadTileSet(t, index, DMA);
}

void TileFideOutMosic2(s16 row, TileSet *t, u16 index){
    u32 mask = (0x0FFFFFF0 >> (12*row)); 
    mask = mask << (8*row);
    for (u32 i = 0; i < t->numTile*8; i = i + 8){
        for (u8 j = row; j < 8; j++)
        {
            if(j == row){
                t->tiles[i+row] = 0;
                t->tiles[i + 7-row] = 0;
            }else{
                t->tiles[j + i] &= mask;
            }
        }
       
    }
    VDP_loadTileSet(t, index, DMA);
}

int main()
{
    TileSet tileset;

    tileset.tiles = malloc(sizeof(u32)* bgb.tileset->numTile*8);

    if (tileset.tiles == NULL){
        SYS_die("fail to alloc tileset");
    } else{
        tileset.numTile = bgb.tileset->numTile;
        memcpy(tileset.tiles, bgb.tileset->tiles, sizeof(u32) * bgb.tileset->numTile * 8);
    }

    SPR_init();
    u16 tileIndex = 1;

    VDP_loadTileSet(bgb.tileset, tileIndex, DMA);
    tileIndex += bgb.tileset->numTile;
    VDP_loadTileSet(bga.tileset, tileIndex, DMA);
    u32 blackTile[32];

    memsetU32(blackTile, 0xCCCCCCCC, 8);

    u16 tileIndex2 = tileIndex + bga.tileset->numTile;

    VDP_loadTileData(blackTile, tileIndex2, 1, DMA);


    VDP_setTileMapEx(BG_B, bgb.tilemap,TILE_ATTR_FULL(PAL0, FALSE, FALSE,FALSE, 1),0,0,0,0,40,28, DMA_QUEUE);
    VDP_setTileMapEx(BG_A, bga.tilemap,TILE_ATTR_FULL(PAL1, FALSE, FALSE,FALSE, tileIndex),0,0,0,0,40,28, DMA_QUEUE);

    PAL_setColors(0, bgb.palette->data, 16, DMA_QUEUE);
    PAL_setColors(16, bga.palette->data, 16, DMA_QUEUE);

 

    Sprite *kim_spr, *krauser_spr;

    kim_spr = SPR_addSprite(&kim, 10, 80, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
    PAL_setPalette(PAL2, kim.palette->data, DMA_QUEUE);
    krauser_spr = SPR_addSprite(&krauser, 150, 65, TILE_ATTR(PAL3, FALSE, FALSE, FALSE));
    PAL_setPalette(PAL3, krauser.palette->data, DMA_QUEUE);
    SPR_setHFlip(krauser_spr, TRUE);

    s16 row = 0;
    bool fadeIn = FALSE;
    bool fadeOut = FALSE;
    u32 frame = 0;
    u8 effect = 0;

    while(1)
    {
        SPR_update();
        SYS_doVBlankProcess();
        
        if(effect == 0){
            if(TileFadeOut(row, tileIndex2)){
                row = 14;
                effect++;
                continue;
            }
            row++;
        }
        if(effect == 1){
             if(TileFadeIn(row, tileIndex)){
                effect++;
                row = 0;
                continue;
            }
            row--;
        }
        
        if(effect==2 && (frame % 4 == 0) && (frame > 60*5)){
            TileFideOutMosic1(row, &tileset, 1);
            row++;
            if(row == 8){
                effect++;
                row = 0;
                waitMs(2000);
                memcpy(tileset.tiles, bgb.tileset->tiles, sizeof(u32) * bgb.tileset->numTile * 8);
                VDP_loadTileSet(bgb.tileset, 1, DMA);
            }
        }

        if(effect==3 && (frame % 4 == 0) && (frame > 60*10)){
            TileFideOutMosic2(row, &tileset, 1);
            row++;

            if(row == 4){
                effect=0;
                row = 0;
                frame = 0;
                waitMs(2000);
                memcpy(tileset.tiles, bgb.tileset->tiles, sizeof(u32) * bgb.tileset->numTile * 8);
                VDP_loadTileSet(bgb.tileset, 1, DMA);
                
            }
        }

        if(frame == 64){
            fadeOut = TRUE;
        }
        frame++;
         
        
       
    }
    return (0);
}

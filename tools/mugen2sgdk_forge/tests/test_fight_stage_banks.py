"""Exercise actual stage C against a physical VRAM/CRAM model and deferred DMA."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]'


def test_stage_banks_preserve_fighters_hud_maps_and_restore_after_super(tmp_path):
    cc = shutil.which('cc')
    if not cc:
        pytest.skip('host compiler unavailable')
    (tmp_path / 'mg').mkdir()
    (tmp_path / 'genesis.h').write_text(r'''
#ifndef TEST_GENESIS
#define TEST_GENESIS
#include <stdint.h>
#include <string.h>
#include <assert.h>
typedef uint8_t u8; typedef uint16_t u16; typedef int16_t s16; typedef uint32_t u32; typedef u8 bool;
#define TRUE 1
#define FALSE 0
#define TILE_FONT_INDEX 1440
#define TILE_SPRITE_INDEX 1010
#define TILE_INDEX_MASK 2047
#define TILE_ATTR_HFLIP_MASK 2048
#define TILE_ATTR_VFLIP_MASK 4096
#define HSCROLL_PLANE 0
#define VSCROLL_PLANE 0
typedef enum {BG_A, BG_B} VDPPlane;
typedef enum {CPU, DMA_QUEUE} TransferMethod;
typedef struct {u16 compression,numTile; u32 *tiles;} TileSet;
typedef struct {u16 compression,w,h; u16 *tilemap;} TileMap;
typedef struct {u16 length; u16 *data;} Palette;
typedef struct {Palette *palette; TileSet *tileset; TileMap *tilemap;} Image;
extern Image img_suzaku_anchor;
extern u32 vram[2048*8]; extern u16 cram[64], map[64*32];
extern const u16 *queued; extern u16 uploads, restores;
void VDP_setPlaneSize(u16 w,u16 h,bool b);
void VDP_setWindowAddress(u16 a);
void VDP_setScrollingMode(u16 h,u16 v);
void VDP_setHorizontalScroll(VDPPlane p,s16 x);
void VDP_setVerticalScroll(VDPPlane p,s16 y);
void VDP_loadTileData(const u32 *p,u16 i,u16 n,TransferMethod t);
void PAL_setColors(u16 i,const u16 *p,u16 n,TransferMethod t);
void VDP_setTileMapDataRect(VDPPlane p,const u16 *data,u16 x,u16 y,u16 w,u16 h,u16 stride,TransferMethod t);
#endif
''')
    (tmp_path / 'resources.h').write_text('#include "genesis.h"\n')
    (tmp_path / 'mg/mg_runtime.h').write_text('extern struct Fight {u8 bgfx_active; s16 shake_x,shake_y;} mg_fight;\n')
    (tmp_path / 'test.c').write_text(r'''
#include "genesis.h"
#include "mg/mg_runtime.h"
#include "scenes/fight_stage.h"
struct Fight mg_fight;
u32 vram[2048*8]; u16 cram[64],map[64*32]; const u16 *queued;
u16 uploads,restores;
static u32 pixels[648*8]; static u16 entries[42*32],colors[16];
static TileSet tiles={0,640,pixels}; static TileMap tilemap={0,42,32,entries};
static Palette palette={16,colors}; Image img_suzaku_anchor={&palette,&tiles,&tilemap};
static s16 current_hscroll,current_vscroll;
void VDP_setPlaneSize(u16 w,u16 h,bool b){assert(w==64 && h==32 && b);}
void VDP_setWindowAddress(u16 a){assert(a==0xE000);}
void VDP_setScrollingMode(u16 h,u16 v){assert(!h && !v);}
void VDP_setHorizontalScroll(VDPPlane p,s16 x){if(p==BG_A)assert(!x);else current_hscroll=x;}
void VDP_setVerticalScroll(VDPPlane p,s16 y){if(p==BG_A)assert(!y);else current_vscroll=y;}
void VDP_loadTileData(const u32 *p,u16 i,u16 n,TransferMethod t){
 assert(t==CPU && i+n<=2048); memcpy(vram+i*8,p,n*32); uploads++;
}
void PAL_setColors(u16 i,const u16 *p,u16 n,TransferMethod t){
 assert(t==CPU && i==0 && n==9);memcpy(cram+i,p,n*2);
}
void VDP_setTileMapDataRect(VDPPlane p,const u16 *data,u16 x,u16 y,u16 w,u16 h,u16 stride,TransferMethod t){
 assert(p==BG_B && !x && !y && w==42 && h==32 && stride==42);
 if(t==DMA_QUEUE){queued=data;restores++;}else
  for(u16 row=0;row<h;row++)memcpy(&map[row*64],&data[row*stride],w*sizeof(u16));
}
static int occupied(u16 tile){
 return (tile>=650 && tile<1010)||(tile>=1440 && tile<1536)||
        (tile>=1664 && tile<1792)||(tile>=1984 && tile<2040);
}
int main(void){
 for(u16 i=0;i<648*8;i++)pixels[i]=0xC0000000u+i;
 for(u16 i=0;i<42*32;i++)entries[i]=(i%640)|((i%4)<<11);
 for(u16 i=0;i<64;i++)cram[i]=0x777;
 for(u16 i=0;i<16;i++)colors[i]=i;
 for(u16 i=0;i<2048*8;i++)vram[i]=0xDEADBEEF;
 FIGHT_STAGE_setup(); assert(FIGHT_STAGE_init(650)); assert(uploads==4);
 for(u16 i=0;i<2048;i++)if(!occupied(i))for(u16 j=0;j<8;j++)assert(vram[i*8+j]==0xDEADBEEF);
 for(u16 y=0;y<32;y++)for(u16 x=0;x<42;x++){
  u16 i=y*42+x, actual=map[y*64+x];
  assert((actual&6144)==(entries[i]&6144));
  for(u16 j=0;j<8;j++)assert(vram[(actual&2047)*8+j]==pixels[(i%640)*8+j]);
 }
 assert(current_hscroll==-8 && current_vscroll==16);
 /* Combined authored shake range: horizontal +/-7, vertical +/-11. */
 for(s16 x=-7;x<=7;x++)for(s16 y=-11;y<=11;y++){
  mg_fight.shake_x=x;mg_fight.shake_y=y;FIGHT_STAGE_update();
  assert(current_hscroll==-8+x && current_vscroll==16-y);
 }
 for(u16 i=9;i<64;i++)assert(cram[i]==0x777);
 FIGHT_STAGE_update();assert(!restores);
 mg_fight.bgfx_active=1;FIGHT_STAGE_update();assert(!restores);
 assert(current_hscroll==7 && current_vscroll==-11);
 mg_fight.shake_x=mg_fight.shake_y=0;
 mg_fight.bgfx_active=0;FIGHT_STAGE_update();assert(restores==1);
 assert(current_hscroll==-8 && current_vscroll==16);
 /* Queue source is persistent after another stack frame is clobbered. */
 volatile u16 scratch[42*32];for(u16 i=0;i<42*32;i++)scratch[i]=0xBAD;
 assert(scratch[42*32-1]==0xBAD);assert(queued!=0);
 for(u16 y=0;y<32;y++)for(u16 x=0;x<42;x++)assert(queued[y*42+x]==map[y*64+x]);
 FIGHT_STAGE_update();assert(restores==1 && uploads==4);
 tiles.numTile=649; assert(!FIGHT_STAGE_init(650)); assert(uploads==4);
 assert(FIGHT_STAGE_initDiagnostics()->status==STAGE_INIT_CAPACITY);
 assert(FIGHT_STAGE_initDiagnostics()->required==649 && FIGHT_STAGE_initDiagnostics()->capacity==648);
 tiles.numTile=640; assert(!FIGHT_STAGE_init(1011)); assert(uploads==4);
 tiles.compression=1; assert(!FIGHT_STAGE_init(650)); assert(uploads==4);
 assert(FIGHT_STAGE_initDiagnostics()->status==STAGE_INIT_COMPRESSED);
 return 0;
}
''')
    exe = tmp_path / 'test'
    subprocess.run([cc, '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(tmp_path),
                    '-I', str(PROJECT / 'inc'), str(tmp_path / 'test.c'),
                    str(PROJECT / 'src/scenes/fight_stage.c'), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)

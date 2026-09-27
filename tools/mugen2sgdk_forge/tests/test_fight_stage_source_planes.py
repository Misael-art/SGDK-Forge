"""Compile and exercise the source-derived two-plane stage against VRAM banks."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]'


def test_source_planes_resolve_cross_bank_tiles_and_restore_hud_plane(tmp_path):
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
#define PAL0 0
#define TILE_FONT_INDEX 1440
#define TILE_SPRITE_INDEX 1010
#define TILE_INDEX_MASK 2047
#define TILE_ATTR_HFLIP_MASK 2048
#define TILE_ATTR_VFLIP_MASK 4096
#define TILE_ATTR_PALETTE_MASK (3u << 13)
#define TILE_ATTR_PRIORITY_MASK (1u << 15)
#define TILE_ATTR_MASK (TILE_ATTR_HFLIP_MASK|TILE_ATTR_VFLIP_MASK|TILE_ATTR_PALETTE_MASK|TILE_ATTR_PRIORITY_MASK)
#define TILE_ATTR_FULL(pal,prio,vflip,hflip,index) (((hflip)<<11)|((vflip)<<12)|((pal)<<13)|((prio)<<15)|(index))
#define HSCROLL_PLANE 0
#define VSCROLL_PLANE 0
typedef enum {BG_A, BG_B} VDPPlane;
typedef enum {CPU, DMA_QUEUE} TransferMethod;
typedef struct {u16 compression,numTile; u32 *tiles;} TileSet;
typedef struct {u16 compression,w,h; u16 *tilemap;} TileMap;
typedef struct {u16 length; u16 *data;} Palette;
typedef struct {Palette *palette; TileSet *tileset; TileMap *tilemap;} Image;
extern Image img_suzaku_far, img_suzaku_near;
extern u32 vram[2048*8]; extern u16 cram[64], map_a[64*32],map_b[64*32];
extern const u16 *queued_a,*queued_b; extern u16 uploads,restores;
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
u32 vram[2048*8]; u16 cram[64],map_a[64*32],map_b[64*32];
const u16 *queued_a,*queued_b; u16 uploads,restores;
static u32 far_pixels[259*8],near_pixels[426*8];
static u16 far_entries[42*32],near_entries[42*32],colors[9];
static TileSet far_tiles={0,259,far_pixels},near_tiles={0,426,near_pixels};
static TileMap far_map={0,42,32,far_entries},near_map={0,42,32,near_entries};
static Palette palette={9,colors};
Image img_suzaku_far={&palette,&far_tiles,&far_map};
Image img_suzaku_near={&palette,&near_tiles,&near_map};
static s16 hscroll_a,hscroll_b,vscroll_a,vscroll_b;
void VDP_setPlaneSize(u16 w,u16 h,bool b){assert(w==64 && h==32 && b);}
void VDP_setWindowAddress(u16 a){assert(a==0xE000);}
void VDP_setScrollingMode(u16 h,u16 v){assert(!h && !v);}
void VDP_setHorizontalScroll(VDPPlane p,s16 x){if(p==BG_A)hscroll_a=x;else hscroll_b=x;}
void VDP_setVerticalScroll(VDPPlane p,s16 y){if(p==BG_A)vscroll_a=y;else vscroll_b=y;}
void VDP_loadTileData(const u32 *p,u16 i,u16 n,TransferMethod t){
 assert(t==CPU && i+n<=2048);memcpy(vram+i*8,p,n*32);uploads++;
}
void PAL_setColors(u16 i,const u16 *p,u16 n,TransferMethod t){
 assert(t==CPU && i==0 && n==9);memcpy(cram+i,p,n*2);
}
void VDP_setTileMapDataRect(VDPPlane p,const u16 *data,u16 x,u16 y,u16 w,u16 h,u16 stride,TransferMethod t){
 assert(!x && !y && w==42 && h==32 && stride==42);
 if(t==DMA_QUEUE){if(p==BG_A)queued_a=data;else queued_b=data;restores++;}
 else {u16 *dst=p==BG_A?map_a:map_b;for(u16 row=0;row<h;row++)memcpy(&dst[row*64],&data[row*stride],w*sizeof(u16));}
}
static u16 physical(u16 logical){
 const u16 cap[]={410,96,128,64},base[]={600,1440,1664,1984};
 for(u8 i=0;i<4;i++){if(logical<cap[i])return base[i]+logical;logical-=cap[i];}
 return 0xFFFF;
}
int main(void){
 for(u16 t=0;t<259;t++)for(u8 w=0;w<8;w++)far_pixels[t*8+w]=0x10000000u+(u32)t*8+w;
 for(u16 t=0;t<426;t++)for(u8 w=0;w<8;w++)near_pixels[t*8+w]=0x20000000u+(u32)t*8+w;
 memset(&near_pixels[425*8],0,32);
 for(u16 i=0;i<42*32;i++){
  far_entries[i]=(u16)(i%259)|((i&1)?TILE_ATTR_HFLIP_MASK:0)|((i&2)?TILE_ATTR_VFLIP_MASK:0)|((i&4)?TILE_ATTR_PRIORITY_MASK:0);
  near_entries[i]=(u16)(i%426)|((i&1)?TILE_ATTR_HFLIP_MASK:0)|((i&2)?TILE_ATTR_VFLIP_MASK:0)|((i&4)?TILE_ATTR_PRIORITY_MASK:0);
 }
 for(u16 i=0;i<64;i++)cram[i]=0x777;
 for(u16 i=0;i<9;i++)colors[i]=i;
 for(u32 i=0;i<2048*8;i++)vram[i]=0xDEADBEEF;
 FIGHT_STAGE_setup(); assert(FIGHT_STAGE_init(600)); assert(uploads==5);
 assert(FIGHT_STAGE_takeHudInvalidation()); assert(!FIGHT_STAGE_takeHudInvalidation());
 assert(hscroll_a==-8 && hscroll_b==-8 && vscroll_a==16 && vscroll_b==16);
 for(u16 i=0;i<42*32;i++){
  u16 a=map_a[(i/42)*64+i%42],b=map_b[(i/42)*64+i%42];
  u16 ai=(u16)(i%426),bi=(u16)(i%259);
  assert((a&TILE_ATTR_MASK)==(near_entries[i]&TILE_ATTR_MASK));
  assert((b&TILE_ATTR_MASK)==(far_entries[i]&TILE_ATTR_MASK));
  assert((a&TILE_INDEX_MASK)==physical((u16)(259+ai)));
  assert((b&TILE_INDEX_MASK)==physical(bi));
  assert(vram[(a&TILE_INDEX_MASK)*8]==near_pixels[ai*8]);
  assert(vram[(b&TILE_INDEX_MASK)*8]==far_pixels[bi*8]);
 }
 for(u16 i=9;i<64;i++)assert(cram[i]==0x777);
 mg_fight.bgfx_active=1; FIGHT_STAGE_update();
 assert(queued_a && queued_b==0 && restores==1);
 const u16 blank=physical((u16)(259+425));
 for(u16 i=0;i<42*32;i++)assert(queued_a[i]==blank);
 mg_fight.bgfx_active=0; FIGHT_STAGE_update();
 assert(FIGHT_STAGE_restoreCount()==1 && FIGHT_STAGE_takeHudInvalidation());
 assert(queued_a!=0 && queued_b!=0 && restores==3);
 for(u16 i=0;i<42*32;i++){assert(queued_a[i]==map_a[(i/42)*64+i%42]);assert(queued_b[i]==map_b[(i/42)*64+i%42]);}
 return 0;
}
''')
    exe = tmp_path / 'test'
    subprocess.run([cc, '-DMG_STAGE_SOURCE_PLANES=1', '-std=c99', '-Wall', '-Wextra', '-Werror',
                    '-I', str(tmp_path), '-I', str(PROJECT / 'inc'), str(tmp_path / 'test.c'),
                    str(PROJECT / 'src/scenes/fight_stage.c'), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)

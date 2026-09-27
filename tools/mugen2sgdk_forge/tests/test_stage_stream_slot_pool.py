"""Compile the actual allocator functions; physical gaps differ from SGDK ceiling."""
import shutil
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"

def test_physical_gaps_and_atomic_rejection(tmp_path):
    cc = shutil.which("cc")
    if not cc:
        pytest.skip("host compiler unavailable")
    source = (PROJECT / "src/scenes/fight_stage_stream.c").read_text()
    allocator = source[source.index("static bool append_slots("):source.index("static s16 scroll_for(")]
    harness = r'''
#include <stdint.h>
#include <assert.h>
typedef uint16_t u16; typedef uint32_t u32; typedef int bool;
#define TRUE 1
#define FALSE 0
#define TILE_SIZE 32
#define TILE_MAX_NUM 1536
#define TILE_FONT_INDEX 1440
#define FONT_LEN 96
#define TILE_SPRITE_INDEX 1010
#define STREAM_MAX_CACHE 1024
#define STREAM_FIXED_BANKS 4
static u16 sSlotVram[1024],sCapacity,sFixedCapacity,sLoanBase,sLoanCount;
static bool MG_fightGetBgFxLoan(u16 *base,u16 *count){*base=220;*count=272;return TRUE;}
''' + allocator + r'''
int main(void){
 assert(build_slot_pool(650));assert(sFixedCapacity==648);assert(sCapacity==920);
 for(u16 i=0;i<sCapacity;i++){
  u16 t=sSlotVram[i];
  assert((t>=220&&t<492)||(t>=650&&t<1010)||(t>=1440&&t<1536)||
         (t>=1664&&t<1792)||(t>=1984&&t<2048));
  for(u16 j=0;j<i;j++)assert(t!=sSlotVram[j]);
 }
 assert(!append_slots(2047,2,TRUE));assert(sCapacity==920);
 assert(!append_slots(1535,2,TRUE));assert(sCapacity==920);
 assert(!append_slots(1791,2,TRUE));assert(sCapacity==920);
 assert(!append_slots(1920,1,TRUE));assert(sCapacity==920);
 assert(!append_slots(1952,1,TRUE));assert(sCapacity==920);
 /* First candidate free, second overlaps: neither may be committed. */
 assert(!append_slots(219,2,TRUE));assert(sCapacity==920);
 assert(append_slots(219,2,FALSE));assert(sCapacity==921);assert(sSlotVram[920]==219);
 return 0;
}
'''
    unit = tmp_path / "slots.c"
    unit.write_text(harness)
    binary = tmp_path / "slots"
    subprocess.run([cc, "-std=c99", "-Wall", "-Wextra", "-Werror", str(unit), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)

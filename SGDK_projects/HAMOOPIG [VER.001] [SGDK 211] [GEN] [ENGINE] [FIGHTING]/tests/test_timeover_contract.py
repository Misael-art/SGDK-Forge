#!/usr/bin/env python3
"""Host regression of the actual time-over decision block, not an emulator claim."""
from pathlib import Path
import subprocess
import tempfile
from test_health_contract import body, ROOT

def main():
    decision=body(ROOT/'src/fsm.c','if((gClockLTimer==0 && gClockRTimer==0)')
    code='''#include <assert.h>
#include <stdio.h>
typedef unsigned char bool;
struct {int state, energiaBase, wins;} P[3];
int gClockLTimer,gClockRTimer,entries;
void PLAYER_STATE(int p,int state){P[p].state=state;entries++;}
void decide(void){
'''+decision+'''
}
int main(void){
  for(int p1=1;p1<=96;p1++)for(int p2=1;p2<=96;p2++){
    P[1].energiaBase=p1;P[2].energiaBase=p2;
    P[1].state=P[2].state=100;P[1].wins=P[2].wins=0;entries=0;
    gClockLTimer=1;gClockRTimer=0;decide();assert(entries==0);
    gClockLTimer=0;gClockRTimer=1;decide();assert(entries==0);
    gClockRTimer=0;decide();
    assert(P[1].wins==(p1>p2));assert(P[2].wins==(p2>p1));
    assert(P[1].state==(p1>p2?611:615));
    assert(P[2].state==(p2>p1?611:615));
    assert(entries==2);
    for(int frame=0;frame<120;frame++)decide();
    assert(entries==2 && P[1].wins==(p1>p2) && P[2].wins==(p2>p1));
  }
  puts("PASS: 9216 health pairs; draw awards no point; correct winner; no repeated award; nonzero clock ignored");
}
'''
    with tempfile.TemporaryDirectory(prefix='hamoopig-timeover-') as temp:
        source=Path(temp)/'test.c';binary=Path(temp)/'test'
        source.write_text(code)
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)

if __name__=='__main__':main()

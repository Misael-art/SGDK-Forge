#!/usr/bin/env python3
"""Host regression on the actual C function bodies, with state entry mocked."""
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def body(path, signature):
    text=path.read_text()
    start=text.index(signature)
    opening=text.index('{',start)
    depth=1;end=opening+1
    while depth:
        if text[end]=='{':depth+=1
        if text[end]=='}':depth-=1
        end+=1
    return text[start:end]


def main():
    code='''#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <stdio.h>
typedef uint8_t u8; typedef uint16_t u16; typedef int8_t s8; typedef int16_t s16;
#define HUD_BAR_SEGMENTS 8
#define SPECIAL_METER_MAX 32
#define SPECIAL_METER_COST 32
#define COMBAT_EVENT_ATTACH_NONE 0
#define TRUE 1
#define FALSE 0
struct {s8 energiaBase,energia,energiaSP; int state;} P[3];
struct {int specialRules;} gConfig = {1};
static int entries;
void PLAYER_STATE(u8 p,int state){P[p].state=state;entries++;}
int COMBAT_EVENTS_ATTACH_METER_DELTA(u8 defender,s8 delta){(void)defender;(void)delta;return 0;}
int COMBAT_EVENTS_ATTACH_HEALTH_DELTA(u8 defender,s8 delta){(void)defender;(void)delta;return 0;}
'''
    code+=body(ROOT/'src/player.c','static void player_apply_special_delta(')+'\n'
    code+=body(ROOT/'src/player.c','static void player_apply_health_delta(')+'\n'
    code+=body(ROOT/'src/player.c','void FUNCAO_UPDATE_LIFESP(')+'\n'
    code+=body(ROOT/'src/player.c','bool FUNCAO_SPEND_SPECIAL(')+'\n'
    code+=body(ROOT/'src/hud.c','static u8 hud_special_count(')+'\n'
    code+='''int main(void){
  for(int p=1;p<=2;p++){
    for(int hp=1;hp<=96;hp++){
      P[p].energiaBase=hp;P[p].energia=hp;P[p].state=100;entries=0;
      FUNCAO_UPDATE_LIFESP(p,1,-hp);
      assert(P[p].energiaBase==0 && P[p].energia==0 && entries==1);
      FUNCAO_UPDATE_LIFESP(p,2,6);
      assert(entries==1); /* special meter must not apply another launch */
      assert(P[p].energiaSP==6);
      FUNCAO_UPDATE_LIFESP(p,2,127);
      assert(P[p].energiaSP==32); /* special meter clamps at full */
      FUNCAO_UPDATE_LIFESP(p,2,-127);
      assert(P[p].energiaSP==0); /* and never wraps below zero */
      P[p].energiaSP=31; assert(FUNCAO_SPEND_SPECIAL(p)==FALSE && P[p].energiaSP==31);
      P[p].energiaSP=32; assert(FUNCAO_SPEND_SPECIAL(p)==TRUE && P[p].energiaSP==0);
      gConfig.specialRules=0; P[p].energiaSP=0; FUNCAO_UPDATE_LIFESP(p,2,11); assert(P[p].energiaSP==0);
      gConfig.specialRules=1;
      FUNCAO_UPDATE_LIFESP(p,1,-12);
      assert(entries==1 && P[p].energiaBase==0);
    }
    P[p].energiaBase=6;P[p].state=550;entries=0;
    FUNCAO_UPDATE_LIFESP(p,1,-12);
    assert(entries==0 && P[p].energiaBase==0); /* already launched */
    P[p].energiaBase=95;P[p].state=100;
    FUNCAO_UPDATE_LIFESP(p,1,127);
    assert(P[p].energiaBase==96); /* no signed-byte wrap */
  }
  assert(hud_special_count(0)==0 && hud_special_count(-1)==0);
  assert(hud_special_count(32)==8 && hud_special_count(127)==8);
  for(int hp=1;hp<=96;hp++){
    assert(hud_special_count(hp)<=8);
    assert(hud_special_count(hp)>=hud_special_count(hp-1));
  }
  puts("PASS: both players, 192 lethal transitions, no repeated launch, healing clamp, all HUD health values");
}'''
    with tempfile.TemporaryDirectory(prefix='hamoopig-health-') as temp:
        source=Path(temp)/'test.c';binary=Path(temp)/'test'
        source.write_text(code)
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)


if __name__=='__main__':main()

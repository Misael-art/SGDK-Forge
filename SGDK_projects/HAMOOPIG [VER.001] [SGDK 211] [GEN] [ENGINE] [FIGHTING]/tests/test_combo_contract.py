#!/usr/bin/env python3
"""Host regression for the real C combo event/timer helpers."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def body(path: Path, signature: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(signature)
    opening = text.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        if text[end] == "{": depth += 1
        if text[end] == "}": depth -= 1
        end += 1
    return text[start:end]


def main():
    code = """#include <stdint.h>
#include <assert.h>
#include <stdio.h>
typedef uint8_t u8; typedef int8_t s8; typedef int16_t s16;
#define HIT_COMBO_WINDOW_TICKS 60u
#define COMBAT_EVENT_HIT 0u
#define COMBAT_EVENT_GUARD 1u
#define COMBAT_EVENT_THROW 2u
#define COMBAT_EVENT_RESULT_HIT 1u
#define COMBAT_EVENT_RESULT_KO 2u
#define COMBAT_EVENT_SOURCE_BODY 0u
#define COMBAT_EVENT_SOURCE_THROW 2u
 #define SPECIAL_METER_MAX 32
struct { u8 hitCounter, hitComboTimer, attackInstance; s8 energiaSP, energiaBase, energia; unsigned short state; } P[3];
struct { int specialRules; } gConfig = {1};
void PLAYER_STATE(u8 p, unsigned short state){ P[p].state=state; }
typedef struct { u8 attacker, defender; unsigned short attackState; u8 kind, source, sourceInstance, hitIndex; signed char meterAttackerDelta, meterDefenderDelta, legacyDefenderDelta, healthDelta; u8 healthAttached, result; unsigned short tick; } CombatEvent;
static CombatEvent events[8]; static u8 eventCount; static u8 claimed;
int COMBAT_EVENTS_EMIT(u8 a, u8 d, unsigned short s, u8 k){
  if(eventCount>=8 || a<1 || a>2 || d<1 || d>2 || a==d) return 0;
  events[eventCount]=(CombatEvent){a,d,s,k,0,0,eventCount,(k==COMBAT_EVENT_HIT)?4:1,(k==COMBAT_EVENT_HIT)?2:0,0,0,0,0,42}; eventCount++; return 1;
}
int COMBAT_EVENTS_EMIT_SOURCE(u8 a,u8 d,unsigned short s,u8 k,u8 source,u8 instance){ (void)source; (void)instance; return COMBAT_EVENTS_EMIT(a,d,s,k); }
int COMBAT_EVENTS_ATTACH_METER_DELTA(u8 d,signed char v){ (void)d; (void)v; return 0; }
void COMBAT_EVENTS_SET_RESULT(u8 i,u8 r){ (void)i; (void)r; }
int COMBAT_EVENTS_CLAIM_CONSUMPTION(void){ if(claimed) return 0; claimed=1; return 1; }
u8 COMBAT_EVENTS_COUNT(void){ return eventCount; }
const CombatEvent *COMBAT_EVENTS_AT(u8 i){ return i<eventCount ? &events[i] : 0; }
static void reset_events(void){ eventCount=0; claimed=0; }
"""
    source = ROOT / "src/player.c"
    code += body(source, "void FUNCAO_REGISTER_HIT(") + "\n"
    code += body(source, "static void player_apply_special_delta(") + "\n"
    code += body(source, "static void player_apply_health_delta(") + "\n"
    code += body(source, "void FUNCAO_CONSUME_COMBAT_EVENTS(") + "\n"
    code += body(source, "void FUNCAO_UPDATE_HIT_COMBOS(") + "\n"
    code += """int main(void){
  reset_events(); FUNCAO_REGISTER_HIT(1); FUNCAO_REGISTER_HIT(1);
  assert(P[1].hitCounter==0 && P[1].hitComboTimer==0 && eventCount==2);
  FUNCAO_CONSUME_COMBAT_EVENTS(); FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[1].hitCounter==2 && P[1].hitComboTimer==60 && P[1].energiaSP==8 && P[2].energiaSP==4);
  for(int i=0;i<59;i++) FUNCAO_UPDATE_HIT_COMBOS();
  assert(P[1].hitCounter==2 && P[1].hitComboTimer==1);
  FUNCAO_UPDATE_HIT_COMBOS();
  assert(P[1].hitCounter==0 && P[1].hitComboTimer==0);
  reset_events(); FUNCAO_REGISTER_HIT(2); FUNCAO_CONSUME_COMBAT_EVENTS(); FUNCAO_UPDATE_HIT_COMBOS();
  assert(P[2].hitCounter==1 && P[2].hitComboTimer==59);
  reset_events(); FUNCAO_REGISTER_HIT(0); FUNCAO_REGISTER_HIT(3); FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[0].hitCounter==0 && P[2].hitCounter==1);
  reset_events(); COMBAT_EVENTS_EMIT(1,2,101,COMBAT_EVENT_GUARD); FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[1].hitCounter==0 && P[1].hitComboTimer==0 && P[1].energiaSP==11);
  reset_events(); P[1].hitCounter=255; FUNCAO_REGISTER_HIT(1); FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[1].hitCounter==255 && P[1].hitComboTimer==60);
  puts("PASS: combo events are counted once, expire after 60 ticks, and stay per-player");
}
"""
    with tempfile.TemporaryDirectory(prefix="hamoopig-combo-") as temp:
        source_file = Path(temp) / "test.c"
        binary = Path(temp) / "test"
        source_file.write_text(code, encoding="utf-8")
        subprocess.run(["cc", "-std=c99", "-Wall", "-Wextra", "-Werror", str(source_file), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    main()

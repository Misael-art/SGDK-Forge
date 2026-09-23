#!/usr/bin/env python3
"""Verify that the real health path is queued once and consumed centrally."""
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
        if text[end] == "{":
            depth += 1
        elif text[end] == "}":
            depth -= 1
        end += 1
    return text[start:end]


def main():
    code = r"""#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <stdio.h>
#include "combat_event.h"
typedef uint8_t u8; typedef uint16_t u16; typedef int8_t s8; typedef int16_t s16;
#define TRUE 1
#define FALSE 0
#define SPECIAL_METER_MAX 32
#define SPECIAL_METER_COST 32
#define HIT_COMBO_WINDOW_TICKS 60u
struct { s8 energiaBase, energia, energiaSP; u16 state; u8 hitCounter, hitComboTimer; } P[3];
struct { int specialRules; } gConfig = {1};
static int entries;
void PLAYER_STATE(u8 p, u16 state){ P[p].state=state; entries++; }
"""
    source = ROOT / "src/player.c"
    code += body(source, "static void player_apply_special_delta(") + "\n"
    code += body(source, "static void player_apply_health_delta(") + "\n"
    code += body(source, "void FUNCAO_UPDATE_LIFESP(") + "\n"
    code += body(source, "void FUNCAO_CONSUME_COMBAT_EVENTS(") + "\n"
    code += r"""int main(void){ const CombatEvent *event;
  P[2].energiaBase=20; P[2].energia=20; P[2].state=100; entries=0;
  COMBAT_EVENTS_BEGIN_TICK(1);
  assert(COMBAT_EVENTS_EMIT(1,2,101,COMBAT_EVENT_HIT));
  FUNCAO_UPDATE_LIFESP(2,1,-7);
  assert(P[2].energiaBase==20); /* queued until the consumer */
  FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[2].energiaBase==13 && P[2].energia==20 && entries==0);
  assert(P[1].hitCounter==1 && P[1].energiaSP==4 && P[2].energiaSP==2);
  event=COMBAT_EVENTS_AT(0); assert(event && event->result==COMBAT_EVENT_RESULT_HIT);

  P[2].energiaBase=20; P[2].energia=20; P[2].state=100; entries=0;
  COMBAT_EVENTS_BEGIN_TICK(2);
  assert(COMBAT_EVENTS_EMIT(1,2,102,COMBAT_EVENT_HIT));
  FUNCAO_UPDATE_LIFESP(2,1,-7);
  FUNCAO_UPDATE_LIFESP(2,1,-7); /* duplicate observation must not double damage */
  FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[2].energiaBase==13 && entries==0);

  P[2].energiaBase=5; P[2].energia=5; P[2].state=100; entries=0;
  COMBAT_EVENTS_BEGIN_TICK(3);
  assert(COMBAT_EVENTS_EMIT(1,2,103,COMBAT_EVENT_HIT));
  FUNCAO_UPDATE_LIFESP(2,1,-10);
  FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[2].energiaBase==0 && P[2].energia==0 && P[2].state==550 && entries==1);
  event=COMBAT_EVENTS_AT(0); assert(event && event->result==COMBAT_EVENT_RESULT_KO);

  P[2].energiaBase=18; P[2].energia=18; P[2].state=100; P[1].hitCounter=0; P[1].energiaSP=0; entries=0;
  COMBAT_EVENTS_BEGIN_TICK(4);
  assert(COMBAT_EVENTS_EMIT(1,2,700,COMBAT_EVENT_GUARD));
  FUNCAO_UPDATE_LIFESP(2,1,-2);
  FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[2].energiaBase==16 && P[1].hitCounter==0 && P[1].energiaSP==1);

  P[1].energiaBase=30; P[1].energia=30; P[1].state=100;
  P[2].energiaBase=30; P[2].energia=30; P[2].state=100;
  COMBAT_EVENTS_BEGIN_TICK(5);
  assert(COMBAT_EVENTS_EMIT(1,2,104,COMBAT_EVENT_HIT));
  assert(COMBAT_EVENTS_EMIT(2,1,204,COMBAT_EVENT_HIT));
  FUNCAO_UPDATE_LIFESP(2,1,-3);
  FUNCAO_UPDATE_LIFESP(1,1,-4);
  FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[1].energiaBase==26 && P[2].energiaBase==27);

  P[1].energiaBase=5; P[1].energia=5; P[1].state=550; entries=0;
  COMBAT_EVENTS_BEGIN_TICK(6);
  FUNCAO_UPDATE_LIFESP(1,1,-2); /* no event: legacy fallback remains */
  assert(P[1].energiaBase==3 && entries==0);
  puts("PASS: health damage is queued once per event, consumed for HIT/GUARD, and keeps the legacy fallback");
}
"""
    with tempfile.TemporaryDirectory(prefix="hamoopig-health-event-") as temp:
        temp = Path(temp)
        fake = temp / "genesis.h"
        fake.write_text("#include <stdbool.h>\ntypedef unsigned char u8; typedef unsigned short u16; typedef signed char s8; typedef signed short s16;\n#define TRUE 1\n#define FALSE 0\n#ifndef NULL\n#define NULL ((void*)0)\n#endif\n")
        source_file = temp / "test.c"
        binary = temp / "test"
        source_file.write_text(code, encoding="utf-8")
        subprocess.run(["cc", "-std=c99", "-Wall", "-Wextra", "-Werror", "-I", str(fake.parent), "-I", str(ROOT / "inc"), str(ROOT / "src/combat_event.c"), str(source_file), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    main()

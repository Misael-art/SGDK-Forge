#!/usr/bin/env python3
"""Exercise the real C meter update and event consumer together."""
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
    code = r"""#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <stdio.h>
typedef uint8_t u8; typedef uint16_t u16; typedef int8_t s8; typedef int16_t s16;
#define TRUE 1
#define FALSE 0
#define SPECIAL_METER_MAX 32
#define COMBAT_EVENT_ATTACH_NONE 0u
#define HIT_COMBO_WINDOW_TICKS 60u
#define COMBAT_EVENT_HIT 0u
#define COMBAT_EVENT_GUARD 1u
#define COMBAT_EVENT_THROW 2u
#define COMBAT_EVENT_RESULT_HIT 1u
#define COMBAT_EVENT_RESULT_KO 2u
typedef struct {
  u8 attacker, defender; u16 attackState; u8 kind, source, sourceInstance, hitIndex;
  s8 meterAttackerDelta, meterDefenderDelta, legacyDefenderDelta, healthDelta;
  u8 healthAttached, result; u16 tick;
} CombatEvent;
struct { s8 energiaBase, energia, energiaSP; u16 state; u8 hitCounter, hitComboTimer; } P[3];
struct { int specialRules; } gConfig = {1};
void PLAYER_STATE(u8 p, u16 state){ P[p].state=(u8)state; }
void COMBAT_EVENTS_BEGIN_TICK(u16);
bool COMBAT_EVENTS_EMIT(u8,u8,u16,u8);
bool COMBAT_EVENTS_EMIT_SOURCE(u8,u8,u16,u8,u8,u8);
bool COMBAT_EVENTS_ATTACH_METER_DELTA(u8,s8);
u8 COMBAT_EVENTS_ATTACH_HEALTH_DELTA(u8,s8);
void COMBAT_EVENTS_SET_RESULT(u8,u8);
bool COMBAT_EVENTS_CLAIM_CONSUMPTION(void);
u8 COMBAT_EVENTS_COUNT(void);
const CombatEvent *COMBAT_EVENTS_AT(u8);
"""
    source = ROOT / "src/player.c"
    code += body(source, "static void player_apply_special_delta(") + "\n"
    code += body(source, "static void player_apply_health_delta(") + "\n"
    code += body(source, "void FUNCAO_UPDATE_LIFESP(") + "\n"
    code += body(source, "void FUNCAO_CONSUME_COMBAT_EVENTS(") + "\n"
    code += r"""int main(void){
  COMBAT_EVENTS_BEGIN_TICK(1);
  assert(COMBAT_EVENTS_EMIT(1,2,101,COMBAT_EVENT_HIT));
  FUNCAO_UPDATE_LIFESP(2,2,6);
  assert(P[2].energiaSP==0); /* queued, not applied at collision time */
  FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[1].energiaSP==4 && P[2].energiaSP==2);

  COMBAT_EVENTS_BEGIN_TICK(2);
  P[2].energiaSP=31;
  assert(COMBAT_EVENTS_EMIT(1,2,102,COMBAT_EVENT_HIT));
  FUNCAO_UPDATE_LIFESP(2,2,6);
  FUNCAO_CONSUME_COMBAT_EVENTS();
  assert(P[2].energiaSP==32); /* central consumer clamps */

  COMBAT_EVENTS_BEGIN_TICK(3);
  gConfig.specialRules=0; P[2].energiaSP=0;
  FUNCAO_UPDATE_LIFESP(2,2,11);
  assert(P[2].energiaSP==0);
  puts("PASS: special meter delta is queued on HIT, consumed once, clamped, and disabled by rules");
}
"""
    with tempfile.TemporaryDirectory(prefix="hamoopig-special-event-") as temp:
        temp = Path(temp)
        fake = temp / "genesis.h"
        fake.write_text("typedef unsigned char u8; typedef unsigned short u16; typedef signed char s8; typedef signed short s16; typedef unsigned char bool;\n#define TRUE 1\n#define FALSE 0\n#define NULL ((void*)0)\n")
        source_file = temp / "test.c"
        binary = temp / "test"
        source_file.write_text(code, encoding="utf-8")
        subprocess.run(["cc", "-std=c99", "-Wall", "-Wextra", "-Werror", "-I", str(fake.parent), "-I", str(ROOT / "inc"), str(ROOT / "src/combat_event.c"), str(source_file), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    main()

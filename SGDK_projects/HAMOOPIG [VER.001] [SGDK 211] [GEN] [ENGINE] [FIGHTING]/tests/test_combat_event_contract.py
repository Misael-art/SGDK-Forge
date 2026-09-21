#!/usr/bin/env python3
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory() as td:
        fake = Path(td) / "genesis.h"
        fake.write_text("typedef unsigned char u8; typedef unsigned short u16; typedef signed char s8; typedef signed short s16; typedef unsigned char bool;\n#define TRUE 1\n#define FALSE 0\n#define NULL ((void*)0)\n")
        probe = Path(td) / "probe.c"
        probe.write_text(r'''
#include "combat_event.h"
#include <stdio.h>
int main(void){ const CombatEvent *e; COMBAT_EVENTS_BEGIN_TICK(42);
if(!COMBAT_EVENTS_EMIT(1,2,101,0)) return 1;
if(!COMBAT_EVENTS_ATTACH_METER_DELTA(2,6)) return 2;
if(COMBAT_EVENTS_ATTACH_HEALTH_DELTA(2,-6)!=COMBAT_EVENT_ATTACH_ACCEPTED) return 3;
if(COMBAT_EVENTS_ATTACH_HEALTH_DELTA(2,-3)!=COMBAT_EVENT_ATTACH_DUPLICATE) return 4;
if(COMBAT_EVENTS_EMIT(1,2,101,0) || COMBAT_EVENTS_COUNT()!=1) return 5;
if(!COMBAT_EVENTS_ATTACH_METER_DELTA(2,2)) return 6;
if(COMBAT_EVENTS_EMIT_SOURCE(1,2,101,1,COMBAT_EVENT_SOURCE_BODY,0)) return 25;
if(!COMBAT_EVENTS_EMIT(2,1,202,1)) return 7;
if(COMBAT_EVENTS_EMIT(1,1,303,0) || COMBAT_EVENTS_COUNT()!=2) return 8;
if(!COMBAT_EVENTS_CLAIM_CONSUMPTION() || COMBAT_EVENTS_CLAIM_CONSUMPTION()) return 9;
if(COMBAT_EVENTS_ATTACH_METER_DELTA(1,6)) return 10;
e=COMBAT_EVENTS_AT(0); if(!e || e->meterAttackerDelta!=4 || e->meterDefenderDelta!=2 || e->legacyDefenderDelta!=8 || e->healthDelta!=-6 || !e->healthAttached) return 11;
e=COMBAT_EVENTS_AT(1); if(!e || e->attacker!=2 || e->defender!=1 || e->attackState!=202 || e->kind!=1 || e->tick!=42) return 12;
COMBAT_EVENTS_BEGIN_TICK(43); if(COMBAT_EVENTS_COUNT()!=0 || !COMBAT_EVENTS_CLAIM_CONSUMPTION()) return 13;
if(COMBAT_EVENTS_EMIT_SOURCE(1,2,101,0,COMBAT_EVENT_SOURCE_BODY,0)) return 22;
if(!COMBAT_EVENTS_EMIT_SOURCE(1,2,101,0,COMBAT_EVENT_SOURCE_BODY,1)) return 23;
COMBAT_EVENTS_RESET_ROUND(); COMBAT_EVENTS_BEGIN_TICK(43);
if(!COMBAT_EVENTS_EMIT_SOURCE(1,2,101,0,COMBAT_EVENT_SOURCE_BODY,0)) return 24;
COMBAT_EVENTS_BEGIN_TICK(44);
if(COMBAT_EVENTS_EMIT_SOURCE(1,2,101,COMBAT_EVENT_GUARD,COMBAT_EVENT_SOURCE_BODY,0)) return 26;
COMBAT_EVENTS_RESET_ROUND(); COMBAT_EVENTS_BEGIN_TICK(45);
if(!COMBAT_EVENTS_EMIT_SOURCE(1,2,101,COMBAT_EVENT_GUARD,COMBAT_EVENT_SOURCE_BODY,0)) return 27;
COMBAT_EVENTS_EMIT(1,2,999,0); COMBAT_EVENTS_RESET(); if(COMBAT_EVENTS_COUNT()!=0 || !COMBAT_EVENTS_CLAIM_CONSUMPTION()) return 14;
COMBAT_EVENTS_BEGIN_TICK(46);
if(!COMBAT_EVENTS_EMIT_SOURCE(1,2,700,0,COMBAT_EVENT_SOURCE_PROJECTILE,7)) return 15;
if(COMBAT_EVENTS_EMIT_SOURCE(1,2,700,0,COMBAT_EVENT_SOURCE_PROJECTILE,7) || COMBAT_EVENTS_COUNT()!=1) return 16;
if(!COMBAT_EVENTS_EMIT_SOURCE(1,2,700,0,COMBAT_EVENT_SOURCE_PROJECTILE,8) || COMBAT_EVENTS_COUNT()!=2) return 17;
e=COMBAT_EVENTS_AT(0); if(!e || e->source!=COMBAT_EVENT_SOURCE_PROJECTILE || e->sourceInstance!=7) return 18;
e=COMBAT_EVENTS_AT(1); if(!e || e->sourceInstance!=8) return 19;
COMBAT_EVENTS_BEGIN_TICK(45);
if(!COMBAT_EVENTS_EMIT_SOURCE(1,2,801,COMBAT_EVENT_THROW,COMBAT_EVENT_SOURCE_THROW,0)) return 20;
e=COMBAT_EVENTS_AT(0); if(!e || e->kind!=COMBAT_EVENT_THROW || e->meterAttackerDelta!=4 || e->meterDefenderDelta!=2) return 21;
puts("PASS: bounded combat event ledger records source instances and resets per tick"); return 0; }
''')
        out = Path(td) / "probe"
        subprocess.run(["cc", "-std=c99", "-I", str(fake.parent), "-I", str(ROOT / "inc"), str(ROOT / "src/combat_event.c"), str(probe), "-o", str(out)], check=True)
        subprocess.run([str(out)], check=True)

if __name__ == "__main__":
    main()

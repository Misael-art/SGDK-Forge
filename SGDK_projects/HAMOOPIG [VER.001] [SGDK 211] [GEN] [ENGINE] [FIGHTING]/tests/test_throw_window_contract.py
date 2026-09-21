#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FSM = (ROOT / "src/fsm.c").read_text(encoding="utf-8")
CAPTURE = (ROOT / "tests/capture_visual_ko.py").read_text(encoding="utf-8")

needle = "P[i].key_JOY_Y_status==1 && throwDistance <= 100"
assert needle in FSM, "throw must accept the complete close-range window"
assert "u16 throwDistance" in FSM and "throwDistance <= 100" in FSM, \
    "throw must use live world distance after physics updates"
PROBE = (ROOT / "src/hamoopig_runtime_probe.c").read_text(encoding="utf-8")
assert "sampleSemanticState(u8 scene)" in PROBE and "scene != SCENE_FIGHT" in PROBE, \
    "throw distance telemetry must exclude title/select scenes"
assert "fsm_throw_forward_held" in FSM, "throw must use relative forward input"
assert "stale facing bit" in FSM, "relative-direction rationale must remain documented"
assert "negative s16" in FSM and "gDistancia = (delta < 0)" in FSM, \
    "FSM distance must be absolute before close-range tests"
assert "fsm_throw_forward_held(i, (i==1) ? 2 : 1) || throwDistance <= 30" in FSM, \
    "point-blank Y must remain a reliable throw input"
assert "P[i].state==481 || P[i].state==606" in FSM, \
    "grounded recovery/landing states must accept close-range throw"
assert FSM.index(needle) < FSM.index("FUNCAO_FSM_DEFENSE(PA, PR)", FSM.index(needle)), \
    "throw check must run before defense/normal attack dispatch"
assert "playable close band is 0..100" in FSM, "throw boundary rationale must remain documented"
assert "P1's Y is W" in CAPTURE and "one input owner" in CAPTURE, \
    "throw capture route must use the correct controller ownership"
assert "time.sleep(3.70)" in CAPTURE and "key('j', True)" in CAPTURE and "key('w', True)" in CAPTURE, \
    "throw capture must approach in bounded legs and emit P1 Y edges"
print("PASS: throw uses the 0..100 close-range window before normal Y attack")

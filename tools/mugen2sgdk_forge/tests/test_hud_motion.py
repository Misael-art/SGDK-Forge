"""Run the game's actual presentation math, independently of emulation."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
INC = ROOT / 'SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/inc'


def test_corner_layout_and_decelerating_drain(tmp_path):
    cc = shutil.which('cc')
    if not cc:
        pytest.skip('C compiler absent')
    src = tmp_path / 'hud.c'
    src.write_text('''
#include <assert.h>
#include "scenes/fight_hud_motion.h"
int main(void) {
    assert(HUD_WIN_ROW + 2 <= HUD_COMBO_ROW);
    assert(HUD_POWER_ROW < 28);
    for (unsigned short c = 0; c < HUD_POWER_TILES; c++) {
        assert(hud_power_x(0,c) == 1+c);
        assert(hud_power_x(1,c) == 38-c);
        assert(hud_power_x(0,c)+hud_power_x(1,c) == 39);
    }
    HudPowerMotion m = {0};
    assert(hud_power_step(&m,40) == 40);
    unsigned short prev = 40, first = 0, tail = 0;
    for (unsigned short t=0; t<HUD_POWER_DRAIN_FRAMES; t++) {
        unsigned short v = hud_power_step(&m,0);
        assert(v <= prev);
        if (t<6) first += prev-v;
        if (t>=HUD_POWER_DRAIN_FRAMES-6) tail += prev-v;
        prev = v;
    }
    assert(prev == 0 && m.remaining == 0 && first > tail);
    assert(hud_power_step(&m,20) == 20);
    assert(hud_power_step(&m,10) < 20);
    assert(hud_power_step(&m,40) == 40 && m.remaining == 0);
    return 0;
}
''')
    exe = tmp_path / 'hud'
    subprocess.run([cc, '-Wall', '-Wextra', '-Werror', '-I', str(INC), str(src), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)

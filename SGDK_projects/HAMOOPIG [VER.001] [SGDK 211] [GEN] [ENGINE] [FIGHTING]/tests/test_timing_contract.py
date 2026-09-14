#!/usr/bin/env python3
"""Contrato da taxa logica (P01).

Compila o acumulador REAL de src/timing.c no host e mede o comportamento.
Nao reimplementa a formula em Python: reescrever a funcao sob teste e depois
testar a reescrita nao valida o runtime.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract(path: Path, start: str, end: str | None = None) -> str:
    text = path.read_text(encoding='utf-8', errors='replace')
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j]


def build_harness() -> str:
    """Reconstroi TIMING_ticksForThisFrame a partir do fonte, sem SGDK."""
    src = (ROOT / 'src' / 'timing.c').read_text(encoding='utf-8', errors='replace')

    body = extract(Path(ROOT / 'src' / 'timing.c'),
                   'u8 TIMING_ticksForThisFrame(void)', 'u8 TIMING_roundClockTicks')
    init = extract(Path(ROOT / 'src' / 'timing.c'),
                   'void TIMING_init(void)', 'u8 TIMING_ticksForThisFrame')

    # Constantes lidas do header, nao copiadas a mao.
    header = (ROOT / 'inc' / 'timing.h').read_text(encoding='utf-8', errors='replace')
    logic_hz = re.search(r'#define TIMING_LOGIC_HZ\s+(\d+)', header).group(1)
    max_ticks = re.search(r'#define TIMING_MAX_TICKS_PER_FRAME\s+(\d+)', header).group(1)

    assert 'sAccumulator += TIMING_LOGIC_HZ' in src, \
        'timing.c mudou de forma: o teste precisa ser revisto'

    return f"""
#include <stdio.h>
typedef unsigned char u8; typedef unsigned short u16; typedef int bool;
#define TRUE 1
#define FALSE 0
#define TIMING_LOGIC_HZ {logic_hz}u
#define TIMING_MAX_TICKS_PER_FRAME {max_ticks}u
#define TIMING_PROFILE_NORMAL 0u
#define TIMING_PROFILE_LEGACY 1u
#define LOGIC_RATE_60 60u
#define LOGIC_RATE_50 50u
#define ROUND_CLOCK_TICKS 38
u8 gTimingProfile, gLogicRate; bool gRegionIsPal;
static u16 sAccumulator, sVideoHz;
{init}
{body}

int main(int argc, char** argv) {{
    int pal = argv[1][0] == 'p';
    int frames = atoi(argv[2]);
    gRegionIsPal = pal; gTimingProfile = TIMING_PROFILE_NORMAL;
    gLogicRate = LOGIC_RATE_60;
    TIMING_init();
    int total = 0;
    for (int f = 0; f < frames; f++) {{
        u8 t = TIMING_ticksForThisFrame();
        total += t;
        if (f < 10) printf("%u", t);
    }}
    printf(" total=%d\\n", total);
    return 0;
}}
"""


def main() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'harness.c'
        src.write_text('#include <stdlib.h>\n' + build_harness())
        binary = Path(tmp) / 'harness'
        r = subprocess.run(['gcc', '-std=c11', '-O1', '-o', str(binary), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print('FAIL: harness nao compilou')
            print(r.stderr[:1500])
            return 1

        def run(region, frames):
            out = subprocess.run([str(binary), region, str(frames)],
                                 capture_output=True, text=True).stdout.strip()
            pattern, total = out.split(' total=')
            return pattern, int(total)

        # --- NTSC: 60 frames de video valem 60 ticks ---
        pat, total = run('n', 60)
        if total != 60:
            failures.append(f'NTSC 60 frames deu {total} ticks, esperado 60')
        if pat != '1111111111':
            failures.append(f'NTSC deveria ser 1 tick por frame, veio {pat}')

        # --- PAL: 50 frames de video tambem valem 60 ticks ---
        pat, total = run('p', 50)
        if total != 60:
            failures.append(f'PAL 50 frames deu {total} ticks, esperado 60')
        # 6 ticks a cada 5 frames: 1,1,1,1,2 repetindo
        if pat != '1111211112':
            failures.append(f'PAL deveria alternar 1,1,1,1,2; veio {pat}')

        # --- aceite do plano: 10 s de luta = 600 ticks nas DUAS regioes ---
        for region, fps, nome in (('n', 60, 'NTSC'), ('p', 50, 'PAL')):
            _, total = run(region, fps * 10)
            if total != 600:
                failures.append(f'{nome}: 10 s deram {total} ticks, esperado 600')

        # --- sem deriva em janela longa (5 min) ---
        for region, fps, nome in (('n', 60, 'NTSC'), ('p', 50, 'PAL')):
            _, total = run(region, fps * 300)
            if total != 300 * 60:
                failures.append(f'{nome}: 5 min deram {total} ticks, esperado {300*60}')

        # --- teto por frame respeitado ---
        _, total = run('p', 1)
        if total > 2:
            failures.append(f'um frame produziu {total} ticks, acima do teto')

    if failures:
        print('FAIL:')
        for f in failures:
            print('  -', f)
        return 1
    print('PASS: NTSC 1/frame, PAL 1,1,1,1,2, 600 ticks em 10 s nas duas regioes, '
          'sem deriva em 5 min, teto por frame respeitado')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

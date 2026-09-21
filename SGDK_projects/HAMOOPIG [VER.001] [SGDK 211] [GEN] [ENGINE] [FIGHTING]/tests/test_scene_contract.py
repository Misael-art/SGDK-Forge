#!/usr/bin/env python3
"""Contrato do gerenciador de cenas e da maquina da abertura (P02).

Compila SCENE_* de src/scene.c no host, e verifica por leitura estrutural as
invariantes que nao dao para exercitar sem SGDK.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_scene_harness() -> list[str]:
    """Exercita SCENE_request/commit reais compilados no host."""
    scene_c = (ROOT / 'src' / 'scene.c').read_text(encoding='utf-8', errors='replace')
    body = scene_c[scene_c.index('static u8 sPending'):]
    body = body.replace('#include <genesis.h>', '').replace('#include "scene.h"', '')
    body = body.replace('#include "globals.h"', '')

    harness = f"""
#include <stdio.h>
typedef unsigned char u8; typedef int bool;
#define TRUE 1
#define FALSE 0
#define SCENE_NONE 255u
#define SCENE_TITLE 1u
#define SCENE_SELECT 2u
#define SCENE_FIGHT 10u
u8 gRoom; unsigned long gFrames;
void STAGE_ambient_off(void) {{}}
{body}

int main(void) {{
    gRoom = 0; gFrames = 99;

    /* commit sem pedido nao mexe em nada */
    SCENE_commit();
    printf("noop room=%u frames=%lu\\n", gRoom, gFrames);

    /* primeiro pedido vence; o segundo do mesmo tick e ignorado */
    SCENE_request(SCENE_TITLE);
    SCENE_request(SCENE_FIGHT);
    printf("pending=%d\\n", SCENE_pending());
    SCENE_commit();
    printf("commit room=%u frames=%lu pending=%d\\n", gRoom, gFrames, SCENE_pending());

    /* segundo commit no mesmo tick nao repete a troca */
    gFrames = 7;
    SCENE_commit();
    printf("double room=%u frames=%lu\\n", gRoom, gFrames);

    /* pedido novo depois do commit funciona normalmente */
    SCENE_request(SCENE_SELECT);
    SCENE_commit();
    printf("again room=%u frames=%lu\\n", gRoom, gFrames);
    return 0;
}}
"""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'h.c'
        src.write_text(harness)
        binary = Path(tmp) / 'h'
        r = subprocess.run(['gcc', '-std=c11', '-O1', '-o', str(binary), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return ['HARNESS_FAIL:' + r.stderr[:800]]
        return subprocess.run([str(binary)], capture_output=True,
                              text=True).stdout.strip().splitlines()


def main() -> int:
    failures = []

    out = run_scene_harness()
    if out and out[0].startswith('HARNESS_FAIL'):
        print('FAIL: harness nao compilou\n' + out[0])
        return 1
    got = {}
    for line in out:
        key, _, rest = line.partition(' ')
        if '=' in key and not rest:          # linhas como "pending=1"
            k, _, v = key.partition('=')
            got[k] = v
        else:
            got[key] = rest

    if got['noop'] != 'room=0 frames=99':
        failures.append(f"commit sem pedido alterou estado: {got['noop']}")
    if got['pending'] != '1':
        failures.append(f"SCENE_pending deveria ser 1 apos o pedido, veio {got['pending']}")
    if got['commit'] != 'room=1 frames=0 pending=0':
        failures.append(f"o primeiro pedido deveria vencer e zerar gFrames: {got['commit']}")
    if got['double'] != 'room=1 frames=7':
        failures.append(f"segundo commit no mesmo tick repetiu a troca: {got['double']}")
    if got['again'] != 'room=2 frames=0':
        failures.append(f"pedido apos commit nao funcionou: {got['again']}")

    # --- invariantes estruturais ---
    srcs = {f.name: f.read_text(encoding='utf-8', errors='replace')
            for f in (ROOT / 'src').glob('*.c')}

    # Nenhum produtor pode escrever gRoom direto: e isso que o gerenciador
    # existe para impedir.
    for name, text in srcs.items():
        if name in ('scene.c', 'globals.c'):
            continue
        for m in re.finditer(r'gRoom\s*=\s*[^=]', text):
            line = text[:m.start()].count('\n') + 1
            failures.append(f'{name}:{line} escreve gRoom direto; use SCENE_request')

    # gFrames=0/1 manual era a convencao posicional antiga; deve ter sumido.
    for name, text in srcs.items():
        if name in ('scene.c', 'globals.c'):  # globals.c e a definicao, nao um ajuste
            continue
        for m in re.finditer(r'gFrames\s*=\s*[01]\s*;', text):
            line = text[:m.start()].count('\n') + 1
            failures.append(f'{name}:{line} ainda ajusta gFrames a mao')

    # SCENE_commit exatamente uma vez, no main.
    total = sum(t.count('SCENE_commit()') for t in srcs.values())
    if total != 1:
        failures.append(f'SCENE_commit aparece {total} vezes; deve ser uma so')
    if 'SCENE_commit()' not in srcs.get('main.c', ''):
        failures.append('SCENE_commit deveria estar em main.c')

    # A abertura precisa ser dona do proprio fade e nao pode confirmar no titulo.
    opening = (ROOT / 'src' / 'opening.c').read_text(encoding='utf-8', errors='replace')
    if 'KEY_FREE' not in opening:
        failures.append('opening.c nao consome a borda do skip; ela vazaria para o titulo')
    if 'SCENE_request(SCENE_TITLE)' not in opening:
        failures.append('opening.c nao entrega o controle ao titulo')

    # Duracoes em ticks logicos: depois do P01 nao precisam de conversao por regiao.
    header = (ROOT / 'inc' / 'opening.h').read_text(encoding='utf-8', errors='replace')
    vals = {k: int(v) for k, v in re.findall(r'#define OPENING_(\w+)_TICKS\s+(\d+)', header)}
    for nome, esperado in (('FADE_IN', 18), ('HOLD', 120), ('FADE_OUT', 15)):
        if vals.get(nome) != esperado:
            failures.append(f'OPENING_{nome}_TICKS={vals.get(nome)}, contrato pede {esperado}')

    if failures:
        print('FAIL:')
        for f in failures:
            print('  -', f)
        return 1
    print('PASS: commit unico por tick, primeiro pedido vence, gFrames zerado pelo gerenciador, '
          'nenhum produtor escreve gRoom nem gFrames a mao, abertura consome a borda do skip, '
          'duracoes em ticks logicos')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

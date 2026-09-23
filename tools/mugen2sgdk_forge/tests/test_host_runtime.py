"""Aceitacao do runtime C no host: golpes por entrada real e luta CPU x CPU.

Usa o Ken convertido localmente no Mugenesis_Demo (conteudo de terceiros fora do Git);
pula se o projeto/gcc nao estiverem disponiveis. Rodar apos `convert-char` + `install-runtime`.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent / "host"
PROJECT = Path(os.environ.get("MG_DEMO_PROJECT", Path(__file__).resolve().parents[3] / "SGDK_projects" /
                              "Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"))

pytestmark = pytest.mark.skipif(
    shutil.which("gcc") is None or not (PROJECT / "src" / "mg_gen" / "mg_ken.c").exists(),
    reason="gcc ou Ken convertido ausente (rode convert-char no Mugenesis_Demo)")


def build(tmp_path, main):
    out = tmp_path / main / "bin"
    out.parent.mkdir(parents=True)
    env = dict(os.environ, MG_HOST_MAIN=str(HERE / f"{main}.c"))
    subprocess.run([str(HERE / "build_host.sh"), str(PROJECT), str(out), "-O1"], check=True, env=env,
                   capture_output=True)
    return out


# P1 olha para a direita: R = frente, L = tras. Estados de destino do .cmd/.cns do Ken.
MOVES = [
    ("X:2", 200),                          # soco fraco em pe
    ("B:2", 261),                          # botao b (minusculo) = chute medio, nao "tras"
    ("D:6 DX:2 D:10", 400),                # soco agachado
    ("U:3", 40),                           # pulo
    ("R:1 0:1 R:1", 100),                  # corrida (F, F)
    ("L:1 0:1 L:1", 105),                  # passo para tras (B, B)
    ("D:1 DR:1 R:1 RX:2", 850),            # bola de fogo ~D, DF, F, x
    ("D:1 DR:1 R:1 RY:2", 851),
    ("R:1 D:1 DR:1 R:1 RX:2", 1000),       # shoryuken ~F, D, DF, x
    ("R:1 D:1 DR:1 R:1 RZ:2", 1010),
    ("D:1 L:1 LA:2", 2000),                # furacao ~D, B, a
]


def test_moves_reach_expected_states(tmp_path):
    exe = build(tmp_path, "moves")
    for seq, state in MOVES:
        got = json.loads(subprocess.run([str(exe), seq], check=True, capture_output=True, text=True).stdout)
        assert state in got, f"{seq}: esperado {state}, obtido {got}"


def test_cpu_fight_is_alive(tmp_path):
    exe = build(tmp_path, "harness")
    r = json.loads(subprocess.run([str(exe), "36000"], check=True, capture_output=True, text=True).stdout)
    assert r["damage_events"] > 20 and r["distinct_states"] > 60 and r["sound_plays"] > 100, r


def build_flags(tmp_path, main, *flags):
    out = tmp_path / (main + "_fp") / "bin"
    out.parent.mkdir(parents=True)
    env = dict(os.environ, MG_HOST_MAIN=str(HERE / f"{main}.c"))
    subprocess.run([str(HERE / "build_host.sh"), str(PROJECT), str(out), "-O1", *flags], check=True, env=env,
                   capture_output=True)
    return out


def test_super_effects_ring_parts_and_background(tmp_path):
    exe = build_flags(tmp_path, "moves", "-DMG_TEST_FULL_POWER")
    r = subprocess.run([str(exe), "CZ:2"], check=True, capture_output=True, text=True,
                       env=dict(os.environ, MG_FXDBG="1")).stdout
    assert "12000" in r and "anim=30100" in r and "partes=4" in r        # anel dividido em 4 sprites
    r = subprocess.run([str(exe), "D:1 DL:1 L:1 D:5 DL:5 L:1 LX:2"], check=True, capture_output=True, text=True).stdout
    assert "8000" in r                                                     # bola de fogo super
    exe = build_flags(tmp_path, "supers", "-DMG_TEST_FULL_POWER")
    r = json.loads(subprocess.run([str(exe)], check=True, capture_output=True, text=True).stdout)
    assert r["bg730_ticks"] > 0                                            # fundo do super via Helper


def test_hit_sparks_anchor_on_contact_and_vary_in_combo(tmp_path):
    """P1: faisca nasce no ponto de contato; golpe baixo gera faisca mais baixa que golpe alto;
    acertos seguidos na mesma regiao variam (>= 3 posicoes distintas, desvio sutil <= 4 px)."""
    exe = build(tmp_path, "sparks")
    sp = json.loads(subprocess.run([str(exe)], check=True, capture_output=True, text=True).stdout)
    high = [s for s in sp if s["tag"] == "high"]
    low = [s for s in sp if s["tag"] == "low"]
    assert len(high) >= 3 and len(low) >= 3, sp
    hy = sorted(s["y"] for s in high)[len(high) // 2]
    ly = sorted(s["y"] for s in low)[len(low) // 2]
    assert ly - hy >= 20, (hy, ly)                                   # ancorado por regiao
    assert len({s["var"] for s in high}) >= 3, high                  # >= 3 variacoes no combo
    assert max(s["y"] for s in high) < min(s["y"] for s in low), sp  # regioes separadas

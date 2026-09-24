#!/usr/bin/env python3
"""Contrato host da rota real de sondagem P04.

Este teste não afirma que a ROM gerou cada evento; ele impede que o roteiro
volte a usar a direção errada do guard ou um botão incompatível com a FSM.
O veredito de gameplay continua vindo exclusivamente do HPRB da sessão.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "tests/capture_visual_ko.py").read_text(encoding="utf-8")

assert "if '--semantics' in sys.argv:" in SOURCE
assert "Toggle RULES -> FREE" in SOURCE
assert "qcf('q')" in SOURCE, "rota semântica deve iniciar o projétil pelo comando real"
assert "key('l', True)" in SOURCE, "P2 deve segurar RIGHT como recuo ao olhar para a esquerda"
assert "tap('w')" in SOURCE, "agarrão precisa do botão Y (w)"
assert "time.sleep(.62)" in SOURCE, "cada ataque deve ter janela para encerrar o lifecycle"
assert "HPRB event-class telemetry only" in SOURCE

print("PASS: rota semântica P04 preserva direção, botões e escopo de telemetria")

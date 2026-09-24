"""REGRA 1: um lutador = uma linha de 15 cores para corpo + efeitos."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import palette_contract as pc  # noqa: E402

PROJECT = Path(__file__).resolve().parents[3] / "SGDK_projects" / \
    "Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
W = lambda r, g, b: (b << 9) | (g << 5) | (r << 1)  # noqa: E731  canais 0..7 -> palavra VDP (bits pares)


def test_counts_stable_clothing_and_dedicated_fx():
    base = [0] + [W(i % 8, i // 2 % 8, 7 - i % 8) for i in range(1, 16)]
    alt = list(base)
    alt[3], alt[4] = W(7, 0, 0), W(0, 7, 0)                 # 2 slots de roupa variam
    fx = [0] * 16
    fx[1] = base[1]                                          # tem par no corpo: nao custa slot
    fx[2], fx[3] = W(7, 7, 7), W(7, 7, 6)                   # brancos: sem par no corpo, 1 slot dedicado
    r = pc.slots_needed([base, alt], fx, {1: 10, 2: 5, 3: 5})
    assert (r["stable"], r["clothing"], r["fx_dedicated"]) == (13, 2, 1)
    assert r["needed"] == 16 and not r["fits"] and r["over_by"] == 1


def test_fits_when_effects_reuse_body():
    base = [0] + [W(i % 8, 0, 0) for i in range(1, 16)]
    r = pc.slots_needed([base], list(base), {1: 3, 2: 3})
    assert r["fits"] and r["fx_dedicated"] == 0


def test_ken_overflows_and_cli_rejects_unless_waived():
    if not (PROJECT / "src" / "mg_gen" / "mg_ken.c").exists():
        pytest.skip("Ken convertido ausente")
    r = pc.check_project(PROJECT, "ken")
    assert (r["stable"], r["clothing"], r["fx_dedicated"], r["needed"]) == (9, 6, 5, 20)
    cmd = [sys.executable, "-m", "mugen2sgdk_forge", "palette-check", "--project", str(PROJECT), "--id", "ken"]
    cwd = Path(__file__).resolve().parents[1]
    assert subprocess.run(cmd, cwd=cwd, capture_output=True).returncode == 1
    ok = subprocess.run(cmd + ["--waiver", "aguarda reautoria dos efeitos"], cwd=cwd, capture_output=True, text=True)
    assert ok.returncode == 0 and "aguarda reautoria" in ok.stdout

"""Motor de troca de CRAM (route iii): fidelidade do stub PAL_getColors e, adiante,
ownership por consumidor. Projecto default é o laboratorio cram_lab; producao nunca e default.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent / "host"
PROJECT = Path(os.environ.get(
    "MG_DEMO_PROJECT",
    "/mnt/sdcard/Projects/Sgdk Forge/SGDK_projects/"
    "Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/rascunho/temporario/cram_lab"))

pytestmark = pytest.mark.skipif(
    shutil.which("gcc") is None or not (PROJECT / "src" / "mg_gen" / "mg_ken.c").exists(),
    reason="gcc ou cram_lab ausente (rode Task 1 antes)")


def build(tmp_path, main):
    out = tmp_path / main / "bin"
    out.parent.mkdir(parents=True)
    env = dict(os.environ, MG_HOST_MAIN=str(HERE / f"{main}.c"))
    subprocess.run(["bash", str(HERE / "build_host.sh"), str(PROJECT), str(out), "-O1"], check=True, env=env,
                   capture_output=True)
    return out


def test_pal_getcolors_reads_cram(tmp_path):
    """O stub le host_cram de verdade: roundtrip save/restore e clamp sem ler/escrever fora."""
    exe = build(tmp_path, "cram_getcolors")
    r = subprocess.run([str(exe)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    got = json.loads(r.stdout)
    assert got["getcolors_roundtrip"] == 1, got
    assert got["clamped"] == 1, got

"""Fusao sem perda dos slots de corpo (REGRA 1) aplicada pelo conversor, no Ken real.

Prova pixel a pixel contra a conversao sem fusao (--no-merge-slots), nas 12 variantes; a sombra
(gerada pelo conversor) nao pode ocupar o slot liberado, que sera o de FX.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import palette_contract as pc  # noqa: E402

KEN = Path("/mnt/sdcard/Projects/Mugenesis/Base de Estudo/chars/street-fighter/ken_masters_adv.zip")
CLI = Path(__file__).resolve().parents[1]


def _convert(dst: Path, *flags):
    for d in ("res", "src", "inc", "doc"):
        (dst / d).mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "mugen2sgdk_forge", "convert-char", str(KEN), "--id", "ken",
                    "--project", str(dst), "--vivid-clothing", *flags], cwd=CLI, check=True, capture_output=True)
    src = (dst / "src/mg_gen/mg_ken.c").read_text()
    flat = pc._array(src, "static const u16 pals[][16]")
    return [flat[i:i + 16] for i in range(0, len(flat), 16)]


@pytest.fixture(scope="module")
def both(tmp_path_factory):
    if not KEN.exists():
        pytest.skip("pacote de terceiros do Ken ausente")
    a, b = tmp_path_factory.mktemp("nomerge"), tmp_path_factory.mktemp("merge")
    return a, _convert(a, "--no-merge-slots"), b, _convert(b)


def test_merge_frees_slot_6_without_changing_any_pixel(both):
    a, pa, b, pb = both
    rep = json.loads((b / "doc/mugen/ken_conversion_report.json").read_text())["sprites"]
    assert rep["merged_body_slots"] == {"6": 1} and rep["free_body_slots"] == [6]
    res = (b / "res/mgres_ken.res").read_text()
    checked = 0
    body = [(n, p) for n, p in re.findall(r'SPRITE (\w+) "([^"]+)"', res) if not n.endswith("_fx")]
    body.append(("portrait", "mugen/ken/portrait.png"))            # TILESET na linha do lutador (HUD)
    for name, path in body:
        old = Image.open(a / "res" / path).get_flattened_data()
        new = Image.open(b / "res" / path).get_flattened_data()
        assert 6 not in set(new), name                     # ninguem mais usa o slot liberado
        for x, y in zip(old, new):
            assert (x == 0) == (y == 0)
            if x:
                assert all(pa[v][x] == pb[v][y] for v in range(len(pa))), (name, x, y)
                checked += 1
    assert checked > 700_000 and len(pa) == 12


def test_checker_sees_one_free_slot_and_no_duplicates(both):
    b = both[2]
    r = pc.check_project(b, "ken")
    assert r["unused_body_indices"] == [6] and r["lossless_merges"] == {} and r["free_after_lossless"] == 1


def test_fx_pilot_package_contract(tmp_path):
    if not KEN.exists():
        pytest.skip("pacote de terceiros do Ken ausente")
    from mugen2sgdk_forge import fx_pilot
    from mugen2sgdk_forge.converters.sprites import vdp_rgb
    r = fx_pilot.build(KEN, tmp_path, "hadouken", [750, 751])
    assert (r["frames"], r["sprites"], r["fx_slot"]) == (8, 5, [6])
    doc = tmp_path / "doc/mugen/fx_pilot_hadouken"
    pal = json.loads((doc / "palette_roles.json").read_text())
    assert len(pal["stable_usable_by_fx"]) == 8 and len(pal["clothing_forbidden_for_fx"]) == 6
    assert pal["fx_dedicated"] == [6] and not set(pal["fx_dedicated"]) & set(pal["clothing_forbidden_for_fx"])
    frames = json.loads((doc / "frame_contract.json").read_text())["frames"]
    assert sum(f["empty"] for f in frames) == 3                  # o piscar do voo (-1) esta no contrato
    # o quadro "atual" usa as cores da CRAM (fxpal), nao a paleta embutida na sheet PNG
    cur = Image.open(tmp_path / "rascunho/processado/fx_pilot_hadouken/current_md_750_1.png")
    hashes = json.loads((doc / "source_hashes.json").read_text())
    assert hashes["source_package"] and any(k.endswith("current_md_750_1.png") for k in hashes)
    from mugen2sgdk_forge import character
    from mugen2sgdk_forge.converters import sprites as sc
    from mugen2sgdk_forge.source import Source
    fxpal = sc.convert(character.load(Source(KEN)), vivid_clothing=True).fx_palette
    assert [tuple(cur.getpalette()[k * 3:k * 3 + 3]) for k in range(16)] == [vdp_rgb(w) for w in fxpal]

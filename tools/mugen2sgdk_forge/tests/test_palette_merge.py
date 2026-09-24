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


@pytest.fixture(scope="module")
def pilot(tmp_path_factory):
    if not KEN.exists():
        pytest.skip("pacote de terceiros do Ken ausente")
    from mugen2sgdk_forge import fx_pilot
    t = tmp_path_factory.mktemp("pilot")
    doc = t / "doc/mugen/fx_pilot_hadouken"
    doc.mkdir(parents=True)
    (doc / "brief.md").write_text(f"x\n{fx_pilot.BUDGET_BEGIN}\nvelho: 16 sprites\n{fx_pilot.BUDGET_END}\ny\n")
    fx_pilot.build(KEN, t, "hadouken", [750, 751])
    return t, doc


def test_pilot_source_transparency_is_index_0_only(pilot):
    """P1: indice 0 -> alpha 0; qualquer outro (inclusive o nucleo PRETO visivel) -> alpha 255."""
    from mugen2sgdk_forge import character
    from mugen2sgdk_forge.source import Source
    t, _ = pilot
    by = {(s.group, s.image): s for s in character.load(Source(KEN)).sprites}
    black_checked = 0
    for k in range(5):
        s = by[(750, k)]
        a = Image.open(t / f"rascunho/processado/fx_pilot_hadouken/source_750_{k}.png").getchannel("A").tobytes()
        assert len(a) == len(s.pixels)
        assert all((al == 0) == (p == 0) for al, p in zip(a, s.pixels)), k
        black_checked += sum(1 for al, p in zip(a, s.pixels) if p and max(s.palette[p]) < 16 and al == 255)
    assert black_checked > 0                                   # o preto visivel sobreviveu opaco


def test_pilot_brief_budget_is_generated_from_contract(pilot):
    """P1: o texto do brief sai dos MESMOS numeros do budget_report.json (sem 2 contra 16)."""
    from mugen2sgdk_forge import fx_pilot
    _, doc = pilot
    budget = json.loads((doc / "budget_report.json").read_text())
    brief = (doc / "brief.md").read_text()
    assert fx_pilot.render_budget(budget) in brief and "velho: 16" not in brief
    lim = budget["limits"]
    assert (lim["max_tiles_8x8_per_frame"], lim["max_hw_sprites_per_frame"]) == (26, 2)
    assert budget["compiled"]["status"] == "a medir" and "ESTIMATIVA" in budget["estimate_source"]["method"]


def test_pilot_catalog_keeps_source_and_current(pilot):
    """P2: catalogo com a FONTE por familia; o preto do nucleo aparece como perda grave, nao some."""
    _, doc = pilot
    cat = json.loads((doc / "fx_catalog.json").read_text())
    fam = next(v for v in cat["source_by_family"].values() if [750, 1] in v["sprites"])
    assert fam["colours"].get("0x000", 0) > 0 and fam["map"]["0x000"]["delta_e"] > 50
    assert fam["visible_colours"] >= 8 and fam["transparent_px"] > 0
    assert len(cat["source_by_family"]) == len(cat["current_by_family"]) >= 10

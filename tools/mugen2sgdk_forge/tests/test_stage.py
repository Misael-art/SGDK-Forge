"""Parser de stage: o .def REAL do Suzaku Castle (SSF2) + fixtures sinteticos de fronteira."""
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge.parsers import stage  # noqa: E402

PROJECT = Path(__file__).resolve().parents[3] / "SGDK_projects" / \
    "Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
SUZAKU = PROJECT / "rascunho" / "entrada_bruta" / "ssf2_01_ryu.zip"


@pytest.fixture(scope="module")
def suzaku():
    if not SUZAKU.exists():
        pytest.skip("stage de terceiros fora do Git: copie ssf2_01_ryu.zip para rascunho/entrada_bruta/")
    with zipfile.ZipFile(SUZAKU) as z:
        return stage.parse(z.read("ssf2-01-ryu.def").decode("latin-1"), "ssf2-01-ryu.def")


def test_suzaku_real_def(suzaku):
    st = suzaku
    assert st.warnings == []
    assert (st.name, st.localcoord, st.zoffset) == ("(SSF2) Suzaku Castle", (320, 240), 216)
    assert (st.camera["boundleft"], st.camera["boundright"]) == (-224, 224)
    assert st.bound == {"screenleft": 40, "screenright": 40}
    assert [la.name for la in st.layers] == ["BG 0a", "BG 0b", "BG 1", "BG 2", "BG 3", "BG 4a", "BG 4b",
                                             "BG 5", "BG 5'", "BG 5''"]
    by = {la.name: la for la in st.layers}
    sky = by["BG 0a"]
    assert (sky.spriteno, sky.tile, sky.velocity, sky.delta) == ((0, 1), (1, 0), (-0.25, 0), (0, 1))
    par = by["BG 4a"]
    assert par.type == "parallax" and par.xscale == (1, 1.377466) and par.delta[0] == pytest.approx(0.79241)
    assert [by[n].mask for n in ("BG 1", "BG 2", "BG 3", "BG 4a")] == [True, True, True, False]
    anims = [la for la in st.layers if la.type == "anim"]
    assert [(a.actionno, a.id, a.start) for a in anims] == [(5, 51, (111, 90)), (5, 52, (47, 55)), (5, 53, (-32, 91))]
    act = st.actions[5]
    assert len(act.frames) == 51 and sum(f.time for f in act.frames) == 278
    # cada janela de Enable dura exatamente a animacao: evento de uma vez por ciclo de 3364 ticks
    assert stage.enabled_windows(st, 51) == [(900, 1178, 3364)]
    assert stage.enabled_windows(st, 52) == [(3086, 3364, 3364)]
    assert stage.enabled_windows(st, 53) == [(1778, 2056, 3364)]


def test_defaults_when_sections_are_missing():
    st = stage.parse("[BGdef]\nspr = x.sff\n[BG a]\nspriteno = 1,2\n")
    la = st.layers[0]
    assert (st.localcoord, st.zoffset, st.spr) == ((320, 240), 200, "x.sff")
    assert (la.type, la.delta, la.start, la.tile, la.mask, la.layerno, la.id) == \
        ("normal", (1, 1), (0, 0), (0, 0), False, 0, 0)
    assert st.camera["boundleft"] == -95 and st.bound["screenleft"] == 15


def test_numbers_without_leading_zero_and_trailing_junk():
    st = stage.parse("[BG a]\nspriteno = 0,0\nvelocity = -.25 , .5 ; nuvens\ndelta = .5,1x\nstart=+3,-.5\n")
    la = st.layers[0]
    assert la.velocity == (-0.25, 0.5) and la.delta == (0.5, 1) and la.start == (3, -0.5)


def test_parallax_width_and_xscale_ignored_outside_parallax():
    st = stage.parse("[BG p]\ntype = Parallax\nspriteno = 4,0\nwidth = 400, 1200\n"
                     "[BG n]\nspriteno = 1,0\nxscale = 1, 2\n")
    p, n = st.layers
    assert p.type == "parallax" and p.width == (400, 1200) and p.xscale is None
    assert n.xscale is None and any("[BG n] xscale/width so valem em parallax" in w for w in st.warnings)


def test_unknown_types_and_missing_refs_warn_with_line():
    st = stage.parse("[BG x]\ntype = voxel\nspriteno = 0,0\n[BG y]\ntype = anim\n[BG z]\ntype = anim\nactionno = 9\n"
                     "[BGCtrl orfao]\ntype = enable\n[BGCtrlDef d]\nctrlid = 77\n[BGCtrl c]\ntype = warp\ntime = 5\n")
    w = "\n".join(st.warnings)
    assert ":2: [BG x] type 'voxel'" in w and "[BG y] anim sem actionno" in w
    assert "[BG z] actionno 9 sem [Begin Action]" in w
    assert "[BGCtrl orfao] BGCtrl antes de qualquer BGCtrlDef" in w
    assert "BGCtrl type 'warp'" in w and "ctrlid 77 nao corresponde" in w
    assert st.ctrldefs[0].ctrls[0].type == "null" and st.ctrldefs[0].ctrls[0].time == (5, 5, -1)


def test_ctrl_inherits_def_ids_and_def_without_ids_controls_all():
    st = stage.parse("[BG a]\nspriteno=0,0\nid = 3\n[BG b]\nspriteno=0,0\nid = 4\n"
                     "[BGCtrlDef all]\nlooptime = 100\n"
                     "[BGCtrl on]\ntype = enable\ntime = 10\nvalue = 1\n[BGCtrl off]\ntype = enable\ntime = 20\nvalue = 0\n"
                     "[BGCtrlDef only4]\nctrlid = 4\n"
                     "[BGCtrl on2]\ntype = Enable\ntime = 30, 40, 50\nvalue = 1\nctrlid = 3\n"
                     "[BGCtrl off2]\ntype = enable\ntime = 60\nvalue = 0\nctrlid = 3\n")
    assert stage.enabled_windows(st, 4) == [(10, 20, 100)]
    assert stage.enabled_windows(st, 3) == [(10, 20, 100), (30, 60, -1)]   # o ctrlid do BGCtrl vence o do def
    assert st.ctrldefs[1].ctrls[0].time == (30, 40, 50)


def test_localcoord_window_sin_and_tile_count():
    st = stage.parse("[StageInfo]\nlocalcoord = 640, 480\nzoffset = 400\n"
                     "[BG w]\nspriteno = 0,0\ntile = 3, 1\ntilespacing = 2\nwindow = 0,0, 319,100\n"
                     "sin.y = 4, 60, 0.5\nlayerno = 1\ntrans = add\n")
    la = st.layers[0]
    assert st.localcoord == (640, 480) and st.zoffset == 400
    assert la.tile == (3, 1) and la.tilespacing == (2, 0) and la.window == (0, 0, 319, 100)
    assert la.sin_y == (4, 60, 0.5) and la.layerno == 1 and la.trans == "add"


def test_measure_suzaku_numbers_are_reproducible():
    if not SUZAKU.exists():
        pytest.skip("stage de terceiros fora do Git")
    from mugen2sgdk_forge import stage_measure
    r = stage_measure.measure(SUZAKU, "ssf2-01-ryu.def", "ssf2-01-ryu.sff")
    assert (r["stage_md_colours"], r["stage_sff_indices"]) == (56, 81)
    assert r["layers"]["BG 3"]["max_md_colours_per_tile"] == 16          # acima do limite de 15 do VDP
    by = {p["plan"].split(",")[0] + str(p["delta"]): p for p in r["planes"]}
    assert by["BG_B ceu+castelo+muro0.43"]["tiles_unique_with_flip"] == 739
    assert by["BG_A telhados+chao1.0"]["tiles_unique_with_flip"] == 540
    assert by["S1 BG_B estatico 320 (sem scroll)0.0"]["tiles_unique_with_flip"] == 476


def test_plane_stats_dedupes_mirrors_and_skips_empty():
    from mugen2sgdk_forge import stage_measure as sm
    pal = [(0, 0, 0), (255, 0, 0), (0, 255, 0)] + [(0, 0, 0)] * 253
    buf = [[0] * 24 for _ in range(sm.MD_H)]
    for y in range(8):
        buf[y][0] = 1                     # tile A: coluna esquerda vermelha
        buf[y][15] = 1                    # tile B = espelho horizontal de A
        buf[y][16 + y % 8] = 2            # tile C: diagonal verde
    s = sm.plane_stats(buf, pal)
    assert s["tiles_unique_with_flip"] == 2 and s["md_colours"] == 2
    assert s["empty_cells"] == 3 * (sm.MD_H // 8) - 3

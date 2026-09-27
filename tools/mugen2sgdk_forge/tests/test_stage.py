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
    anims = {a["id"]: a for a in r["animated_layers"]}
    assert set(anims) == {51, 52, 53}
    assert all(a["frame_count"] == 51 and a["loop_cycle_duration_ticks"] == 278 for a in anims.values())
    assert all(a["unique_nonempty_frame_tiles_with_flip"] == 9 for a in anims.values())
    assert all(a["enable_windows"][0]["matches_action_cycle"] for a in anims.values())
    back = r["static_layer_groups"]["suzaku_back_plane_source_layers"]
    assert back["layers"] == ["BG 0a", "BG 0b", "BG 1", "BG 2"]
    assert back["sum_without_cross_layer_dedup"] == 1399
    assert back["unique_nonempty_tiles_with_cross_layer_dedup_and_flip"] == 1021
    assert back["exact_pattern_savings"] == 378
    overlay = r["static_layer_groups"]["suzaku_back_overlay_without_tiled_sky_fallback"]
    assert overlay["unique_nonempty_tiles_with_cross_layer_dedup_and_flip"] == 959
    front = r["static_layer_groups"]["suzaku_front_banded_plane_source_layers"]
    assert front["sum_without_cross_layer_dedup"] == 700
    assert front["unique_nonempty_tiles_with_cross_layer_dedup_and_flip"] == 700
    assert front["status"] == "source_pattern_estimate_not_rescomp"
    bands = {name: r["layers"][name]["visible_y_bounds_exclusive"] for name in ("BG 3", "BG 4a", "BG 4b")}
    assert bands == {"BG 3": [0, 184], "BG 4a": [184, 220], "BG 4b": [220, 224]}  # default crop_top=8


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


def test_animated_stage_report_preserves_frames_tiles_and_enable_schedule():
    from mugen2sgdk_forge import stage_measure as sm
    from mugen2sgdk_forge.parsers.sff import Sprite

    st = stage.parse("""[BG spark]
type = anim
actionno = 9
id = 51
start = 111, 90
delta = .47, 1
[BGCtrlDef event]
looptime = 100
[BGCtrl on]
type = enable
time = 10
value = 1
[BGCtrl off]
type = enable
time = 13
value = 0
[Begin Action 9]
5,2,0,0,2
5,3,0,0,1
""")
    palette = [(0, 0, 0), (255, 0, 0), (0, 255, 0)] + [(0, 0, 0)] * 253
    pixels_a = bytes([0, 1, 0, 0, 0, 0, 0, 0] * 8)
    pixels_b = bytes([0, 0, 2, 0, 0, 0, 0, 0] * 8)
    sprites = {
        (5, 2): Sprite(5, 2, 0, 0, 8, 8, pixels_a, palette, False, None, 0),
        (5, 3): Sprite(5, 3, 0, 0, 8, 8, pixels_b, palette, False, None, 1),
    }
    report = sm.animated_layer_stats(st, sprites)
    assert len(report) == 1
    anim = report[0]
    assert anim["status"] == "measured"
    assert anim["frame_count"] == 2 and anim["first_pass_duration_ticks"] == 3
    assert anim["loop_cycle_duration_ticks"] == 3 and anim["has_infinite_frame"] is False
    assert anim["unique_nonempty_frame_tiles_with_flip"] == 2
    assert anim["enable_windows"] == [{"start": 10, "end": 13, "loop_ticks": 100,
                                       "enabled_ticks": 3, "matches_action_cycle": True}]
    assert [f["visible_pixels"] for f in anim["frames"]] == [8, 8]
    assert anim["frames"][0]["offset"] == [0, 0]


def test_animated_action_with_infinite_frame_has_unknown_cycle_duration():
    from mugen2sgdk_forge import stage_measure as sm
    from mugen2sgdk_forge.parsers.sff import Sprite
    st = stage.parse("""[BG spark]
type = anim
actionno = 9
id = 51
[Begin Action 9]
5,2,0,0,-1
""")
    palette = [(0, 0, 0), (255, 0, 0)] + [(0, 0, 0)] * 254
    sprite = Sprite(5, 2, 0, 0, 1, 1, bytes([1]), palette, False, None, 0)
    result = sm.animated_layer_stats(st, {(5, 2): sprite})[0]
    assert result["has_infinite_frame"] is True
    assert result["first_pass_duration_ticks"] is None
    assert result["loop_cycle_duration_ticks"] is None


def test_static_layer_group_reports_only_proven_cross_layer_reuse():
    from mugen2sgdk_forge import stage_measure as sm
    from mugen2sgdk_forge.parsers.sff import Sprite
    st = stage.parse("""[BG left]
spriteno = 1,0
[BG right]
spriteno = 1,1
""")
    palette = [(0, 0, 0), (255, 0, 0)] + [(0, 0, 0)] * 254
    a = bytes([1, 0, 0, 0, 0, 0, 0, 0] * 8)
    b = bytes([0, 0, 0, 0, 0, 0, 0, 1] * 8)
    sprites = {
        (1, 0): Sprite(1, 0, 0, 0, 8, 8, a, palette, False, None, 0),
        (1, 1): Sprite(1, 1, 0, 0, 8, 8, b, palette, False, None, 1),
    }
    result = sm.static_layer_group_stats(st, sprites, ["BG left", "BG right"])
    assert result["sum_without_cross_layer_dedup"] == 2
    assert result["unique_nonempty_tiles_with_cross_layer_dedup_and_flip"] == 1
    assert result["exact_pattern_savings"] == 1
    assert result["status"] == "source_pattern_estimate_not_rescomp"


def test_animated_stage_report_blocks_missing_sprite_references():
    from mugen2sgdk_forge import stage_measure as sm
    st = stage.parse("""[BG spark]
type = anim
actionno = 9
id = 51
[Begin Action 9]
5,2,0,0,1
""")
    report = sm.animated_layer_stats(st, {})
    assert report[0]["status"] == "missing_sprites"
    assert report[0]["missing_sff_sprites"] == [[5, 2]]

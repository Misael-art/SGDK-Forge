"""REGRA 1: um lutador = uma linha de 15 cores para corpo + efeitos.

Oraculos independentes do codigo medido: palavras VDP de hardware conhecidas, contraexemplos construidos
a mao e fatos estruturais do Ken (classes por variante), nao a contagem que o proprio medidor produz.
"""
import math
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import palette_contract as pc  # noqa: E402
from mugen2sgdk_forge.converters.sprites import vdp_rgb, vdp_word  # noqa: E402

PROJECT = Path(__file__).resolve().parents[3] / "SGDK_projects" / \
    "Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
CLI = Path(__file__).resolve().parents[1]
W = lambda r, g, b: (b << 9) | (g << 5) | (r << 1)  # noqa: E731  niveis 0..7 -> 0000BBB0GGG0RRR0


def test_vdp_decode_known_hardware_words():
    assert vdp_rgb(0x000) == (0, 0, 0)
    assert vdp_rgb(0x002) == (36, 0, 0)          # nivel 1 de vermelho
    assert vdp_rgb(0x00E) == (252, 0, 0)         # vermelho maximo
    assert vdp_rgb(0x0E0) == (0, 252, 0)
    assert vdp_rgb(0xE00) == (0, 0, 252)
    assert vdp_rgb(0xEEE) == (252, 252, 252)     # branco maximo (era 109 com a mascara 0xE)


def test_eight_distinct_increasing_levels_per_channel_and_roundtrip():
    for shift, ch in ((1, 0), (5, 1), (9, 2)):
        levels = [vdp_rgb(n << shift)[ch] for n in range(8)]
        assert levels == sorted(set(levels)) and len(levels) == 8
    assert all(vdp_word(vdp_rgb(W(r, g, b))) == W(r, g, b) for r in range(8) for g in range(8) for b in range(8))


def _flat(word):
    return [0] + [word] * 15


def test_identical_slots_count_as_one_colour():
    """Contraexemplo do parecer: 15 slots vermelhos iguais + efeito verde = 2 cores, nao 16."""
    r = pc.analyse([_flat(W(7, 0, 0))], [0, W(0, 7, 0)] + [0] * 14, set(range(1, 16)), {1: 50})
    assert r["body_classes"] == 1 and r["exact_need"] == 2 and r["fits"]
    assert r["free_after_lossless"] == 14


def test_duplicate_in_one_variant_but_not_other_is_not_merged():
    a = [0] + [W(i % 8, 0, 0) for i in range(1, 16)]
    a[2] = a[3] = W(0, 0, 7)
    b = list(a)
    b[3] = W(0, 7, 0)                              # diverge na variante b
    r = pc.analyse([a, b], [0] * 16, set(range(1, 16)), {})
    assert "2" not in r["lossless_merges"] and r["varying_classes"] >= 1


def test_merge_is_lossless_across_all_variants():
    a = [0] + [W(i % 8, i // 8, 1) for i in range(1, 16)]
    a[6] = a[1]
    b = list(a)
    b[9] = W(0, 7, 7)                              # outra variante muda so um slot de roupa
    r = pc.analyse([a, b], [0] * 16, set(range(1, 16)), {})
    assert r["lossless_merges"] == {"1": [1, 6]} and r["remap"] == {"6": 1}
    assert pc.verify_remap([a, b], {6: 1}, set(range(1, 16)))
    assert not pc.verify_remap([a, b], {9: 1}, set(range(1, 16)))   # fusao falsa e detectada


def test_unused_indices_are_reported_not_counted():
    a = [0] + [W(i % 8, 1, 2) for i in range(1, 16)]
    r = pc.analyse([a], [0] * 16, {1, 2, 3}, {})
    assert r["body_indices_used"] == 3 and r["unused_body_indices"] == list(range(4, 16))
    assert r["body_classes"] == 3


def test_transparency_and_invalid_inputs_are_rejected():
    ok = [0] + [W(1, 1, 1)] * 15
    with pytest.raises(ValueError):
        pc.analyse([ok], [0] * 16, {0, 1}, {})            # indice 0 usado como opaco
    for bad in (math.nan, math.inf, -1):
        with pytest.raises(ValueError):
            pc.analyse([ok], [0] * 16, {1}, {}, bad)
    with pytest.raises(ValueError):
        pc.analyse([ok[:10]], [0] * 16, {1}, {})          # paleta malformada


@pytest.fixture(scope="module")
def ken():
    if not (PROJECT / "src" / "mg_gen" / "mg_ken.c").exists():
        pytest.skip("Ken convertido ausente")
    return pc.check_project(PROJECT, "ken")


def test_ken_structure(ken):
    # fatos estruturais: 12 variantes, 8 classes estaveis + 6 de roupa, slots 1 e 6 iguais em todas
    assert (ken["variants"], ken["body_indices_used"], ken["stable_classes"], ken["varying_classes"]) == (12, 15, 8, 6)
    assert ken["lossless_merges"] == {"1": [1, 6]} and ken["remap_lossless_verified"]
    assert ken["free_after_lossless"] == 1
    assert not ken["fits"] and ken["exact_need"] > pc.LINE_SLOTS


def test_cli_waiver_records_but_never_approves():
    if not (PROJECT / "src" / "mg_gen" / "mg_ken.c").exists():
        pytest.skip("Ken convertido ausente")
    cmd = [sys.executable, "-m", "mugen2sgdk_forge", "palette-check", "--project", str(PROJECT), "--id", "ken"]
    plain = subprocess.run(cmd, cwd=CLI, capture_output=True, text=True)
    waived = subprocess.run(cmd + ["--waiver", "aguarda piloto de FX"], cwd=CLI, capture_output=True, text=True)
    assert plain.returncode == 1 and '"status": "fail"' in plain.stdout
    assert waived.returncode == 1 and '"status": "fail_waived"' in waived.stdout and "aguarda piloto" in waived.stdout
    bad = subprocess.run(cmd + ["--delta-e", "nan"], cwd=CLI, capture_output=True, text=True)
    assert bad.returncode == 2 and "invalid_input" in bad.stdout

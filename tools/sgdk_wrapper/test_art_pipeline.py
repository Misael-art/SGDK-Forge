#!/usr/bin/env python3
"""
test_art_pipeline.py — Suite de testes para validar a pericia do pipeline de arte SGDK

Cria assets sinteticos com problemas conhecidos, executa o diagnostico e verifica
se todos os issues foram detectados corretamente. Ao final, testa a conversao.

Uso:
  python tools/sgdk_wrapper/test_art_pipeline.py
  python tools/sgdk_wrapper/test_art_pipeline.py --verbose
  python tools/sgdk_wrapper/test_art_pipeline.py --keep-temp  # nao apaga artefatos

Requisito: pip install Pillow
Exit code: 0 = todos os testes passaram, 1 = falhas
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("[ERRO] Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).parent
DIAGNOSTIC_SCRIPT = SCRIPT_DIR / "art_diagnostic.py"
BATCH_SCRIPT = SCRIPT_DIR.parent / "image-tools" / "batch_resize_index.py"
FIX_SCRIPT = SCRIPT_DIR.parent / "image-tools" / "fix_png_transparency_final.py"

PASSED = 0
FAILED = 0
VERBOSE = False


def log(msg: str, indent: int = 0):
    if VERBOSE or "[PASS]" in msg or "[FAIL]" in msg or "[TEST]" in msg or "===" in msg:
        print("  " * indent + msg)


def ok(test_name: str, msg: str = ""):
    global PASSED
    PASSED += 1
    log(f"[PASS] {test_name}" + (f" — {msg}" if msg else ""))


def fail(test_name: str, msg: str = ""):
    global FAILED
    FAILED += 1
    log(f"[FAIL] {test_name}" + (f" — {msg}" if msg else ""))


def assert_equal(test_name: str, expected, actual):
    if expected == actual:
        ok(test_name, f"{expected}")
    else:
        fail(test_name, f"esperado={expected!r}, obtido={actual!r}")


def assert_in(test_name: str, needle, haystack):
    if needle in haystack:
        ok(test_name, f"{needle!r} encontrado")
    else:
        fail(test_name, f"{needle!r} NAO encontrado em {haystack!r}")


# ---------------------------------------------------------------------------
# Helpers para criar assets sinteticos
# ---------------------------------------------------------------------------

def make_rgba_sprite(path: Path, w: int, h: int, n_colors: int = 10):
    """Cria PNG RGBA (nao indexado) — deve ser detectado como NOT_INDEXED."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(n_colors):
        c = i * (255 // n_colors)
        img.paste((c, 128, 255-c, 255), (i*(w//n_colors), 0, (i+1)*(w//n_colors), h))
    img.save(path, "PNG")


def make_indexed_sprite_too_many_colors(path: Path, w: int = 32, h: int = 32):
    """Cria PNG indexado com 20 cores visiveis — deve ser detectado como TOO_MANY_COLORS."""
    img = Image.new("P", (w, h))
    # Paleta com 20 cores distintas
    palette = [0, 0, 0] * 256  # zerar paleta
    for i in range(20):
        palette[i*3]   = (i * 13) % 256
        palette[i*3+1] = (i * 7)  % 256
        palette[i*3+2] = (i * 19) % 256
    img.putpalette(palette)
    # Preencher com cores 0-19 em blocos
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (y * w + x) % 20
    img.save(path, "PNG")


def make_bad_dimensions_sprite(path: Path, w: int = 30, h: int = 25):
    """Cria PNG com dimensoes nao multiplas de 8 — deve ser detectado como DIM_NOT_MULTIPLE_8."""
    img = Image.new("P", (w, h))
    palette = [0] * 768
    palette[0:3] = [255, 0, 255]  # index 0 = magenta
    palette[3:6] = [0, 100, 200]  # index 1
    img.putpalette(palette)
    img.paste(1, (0, 0, w, h))
    img.save(path, "PNG")


def make_ok_sprite(path: Path, w: int = 32, h: int = 32):
    """Cria PNG indexado correto: 4 cores, dimensoes 32x32, index 0 = magenta."""
    img = Image.new("P", (w, h))
    palette = [0] * 768
    palette[0:3]   = [0xFF, 0x00, 0xFF]  # transparente
    palette[3:6]   = [0x00, 0x00, 0x00]  # contorno
    palette[6:9]   = [0x00, 0x44, 0xCC]  # cor base (no grid 9-bits: 0x00, 0x44, 0xCC)
    palette[9:12]  = [0x00, 0x22, 0x88]  # sombra
    palette[12:15] = [0x44, 0x66, 0xEE]  # destaque
    img.putpalette(palette)
    px = img.load()
    # Contorno
    for x in range(w):
        px[x, 0] = 1
        px[x, h-1] = 1
    for y in range(h):
        px[0, y] = 1
        px[w-1, y] = 1
    # Interior
    for y in range(1, h-1):
        for x in range(1, w-1):
            px[x, y] = 2 + ((x + y) % 3)
    img.save(path, "PNG")


def make_colors_not_9bit(path: Path, w: int = 16, h: int = 16):
    """Cria PNG indexado com cor fora do grid 9-bits — deve gerar aviso COLORS_NOT_9BIT."""
    img = Image.new("P", (w, h))
    palette = [0] * 768
    palette[0:3]  = [0xFF, 0x00, 0xFF]  # transparente (ok)
    palette[3:6]  = [0x00, 0x00, 0x00]  # preto (ok — 0x00 e valido)
    palette[6:9]  = [0xFF, 0x80, 0x00]  # INVALIDO — 0x80 nao e multiplo de 0x22
    img.putpalette(palette)
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (x + y) % 3
    img.save(path, "PNG")


# ---------------------------------------------------------------------------
# Testes de diagnostico
# ---------------------------------------------------------------------------

def run_diagnostic(project_path: Path) -> dict:
    """Executa art_diagnostic.py e retorna o JSON do relatorio."""
    result = subprocess.run(
        [sys.executable, str(DIAGNOSTIC_SCRIPT),
         "--project", str(project_path),
         "--json-only"],
        capture_output=True, text=True
    )
    if not result.stdout.strip():
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def test_detect_not_indexed(tmp_dir: Path):
    log("\n[TEST] Detectar sprite RGBA (nao indexado)")
    project = tmp_dir / "test_not_indexed"
    res_dir = project / "res" / "sprite"
    res_dir.mkdir(parents=True)

    make_rgba_sprite(res_dir / "player.png", 32, 32)

    # Criar .res file para ser lido pelo diagnostico
    (project / "res" / "sprite.res").write_text(
        'SPRITE player "sprite/player.png" 4 4 FAST 5\n'
    )

    report = run_diagnostic(project)
    if not report:
        fail("Diagnostico retornou JSON vazio")
        return

    assets = report.get("assets", [])
    assert_in("Tem 1 asset no relatorio", 1, [len(assets)])

    if assets:
        issues = [i["code"] for i in assets[0]["issues"]]
        assert_in("Detectou NOT_INDEXED", "NOT_INDEXED", issues)
        assert_equal("Cenario e precisa_conversao", "precisa_conversao", assets[0]["scenario"])


def test_detect_too_many_colors(tmp_dir: Path):
    log("\n[TEST] Detectar sprite com muitas cores (>15)")
    project = tmp_dir / "test_many_colors"
    res_dir = project / "res" / "sprite"
    res_dir.mkdir(parents=True)

    make_indexed_sprite_too_many_colors(res_dir / "enemy.png", 32, 32)
    (project / "res" / "sprite.res").write_text(
        'SPRITE enemy "sprite/enemy.png" 4 4 FAST 5\n'
    )

    report = run_diagnostic(project)
    assets = report.get("assets", [])
    assert_in("Tem assets no relatorio", True, [len(assets) > 0])

    if assets:
        issues = [i["code"] for i in assets[0]["issues"]]
        assert_in("Detectou TOO_MANY_COLORS", "TOO_MANY_COLORS", issues)


def test_detect_bad_dimensions(tmp_dir: Path):
    log("\n[TEST] Detectar dimensoes nao multiplas de 8")
    project = tmp_dir / "test_bad_dims"
    res_dir = project / "res" / "sprite"
    res_dir.mkdir(parents=True)

    make_bad_dimensions_sprite(res_dir / "bad_size.png", 30, 25)
    (project / "res" / "sprite.res").write_text(
        'SPRITE bad_size "sprite/bad_size.png" 4 3 FAST 5\n'
    )

    report = run_diagnostic(project)
    assets = report.get("assets", [])

    if assets:
        issues = [i["code"] for i in assets[0]["issues"]]
        assert_in("Detectou DIM_NOT_MULTIPLE_8", "DIM_NOT_MULTIPLE_8", issues)
        assert_equal("Dimensao W reportada", 30, assets[0]["width"])
        assert_equal("Dimensao H reportada", 25, assets[0]["height"])


def test_detect_ok_sprite(tmp_dir: Path):
    log("\n[TEST] Sprite correto nao tem issues criticos")
    project = tmp_dir / "test_ok"
    res_dir = project / "res" / "sprite"
    res_dir.mkdir(parents=True)

    make_ok_sprite(res_dir / "hero.png", 32, 32)
    (project / "res" / "sprite.res").write_text(
        'SPRITE hero "sprite/hero.png" 4 4 FAST 5\n'
    )

    report = run_diagnostic(project)
    assets = report.get("assets", [])

    if assets:
        criticos = [i for i in assets[0]["issues"] if i["severity"] == "critico"]
        assert_equal("Sem issues criticos", 0, len(criticos))
        assert_equal("Cenario e ok", "ok", assets[0]["scenario"])
        assert_equal("Modo e P (indexado)", "P", assets[0]["mode"])


def test_detect_colors_not_9bit(tmp_dir: Path):
    log("\n[TEST] Detectar cores fora do grid 9-bits")
    project = tmp_dir / "test_9bit"
    res_dir = project / "res" / "sprite"
    res_dir.mkdir(parents=True)

    make_colors_not_9bit(res_dir / "bad_colors.png", 16, 16)
    (project / "res" / "sprite.res").write_text(
        'SPRITE bad_colors "sprite/bad_colors.png" 2 2 FAST 5\n'
    )

    report = run_diagnostic(project)
    assets = report.get("assets", [])

    if assets:
        issues = [i["code"] for i in assets[0]["issues"]]
        assert_in("Detectou COLORS_NOT_9BIT", "COLORS_NOT_9BIT", issues)
        # Cores nao-9bit sao apenas aviso, nao critico
        criticos = [i for i in assets[0]["issues"] if i["severity"] == "critico"]
        assert_equal("COLORS_NOT_9BIT e apenas aviso (sem criticos)", 0, len(criticos))


def test_scenario_3_no_art(tmp_dir: Path):
    log("\n[TEST] Cenario 3 — detectar projeto sem arte")
    project = tmp_dir / "test_no_art"
    project.mkdir(parents=True)
    # Criar estrutura minima sem assets
    (project / "src").mkdir()
    (project / "res").mkdir()
    (project / "src" / "main.c").write_text("// stub\n")

    result = subprocess.run(
        [sys.executable, str(DIAGNOSTIC_SCRIPT), "--project", str(project)],
        capture_output=True, text=True
    )
    assert_equal("Exit code = 2 (sem arte)", 2, result.returncode)

    report = run_diagnostic(project)
    assert_equal("Cenario detectado e 3_no_art", "3_no_art", report.get("scenario_detected"))


def test_scenario_1_data_needs_conversion(tmp_dir: Path):
    log("\n[TEST] Cenario 1 — /data com RGBA detectado")
    project = tmp_dir / "test_cenario1"
    data_dir = project / "data"
    data_dir.mkdir(parents=True)
    (project / "res").mkdir()

    make_rgba_sprite(data_dir / "hero_raw.png", 40, 40)

    report = run_diagnostic(project)
    assert_in("Cenario e 1_data", "1_data", report.get("scenario_detected", ""))

    assets = report.get("assets", [])
    assert_in("Tem assets no relatorio", True, [len(assets) > 0])
    if assets:
        issues = [i["code"] for i in assets[0]["issues"]]
        assert_in("Detectou NOT_INDEXED em /data", "NOT_INDEXED", issues)


def test_conversion_fix_transparency(tmp_dir: Path):
    log("\n[TEST] fix_png_transparency_final.py — corrigir transparencia")
    if not FIX_SCRIPT.exists():
        fail("fix_png_transparency_final.py nao encontrado")
        return

    test_dir = tmp_dir / "test_fix_trans"
    test_dir.mkdir(parents=True)

    # Asset com problema
    make_rgba_sprite(test_dir / "broken.png", 32, 32)

    result = subprocess.run(
        [sys.executable, str(FIX_SCRIPT), str(test_dir / "broken.png")],
        capture_output=True, text=True
    )
    assert_equal("fix_png_transparency exit code 0", 0, result.returncode)

    # Verificar que o arquivo foi modificado para indexado
    with Image.open(test_dir / "broken.png") as img:
        assert_equal("Apos fix: modo e P (indexado)", "P", img.mode)


def test_conversion_batch_resize(tmp_dir: Path):
    log("\n[TEST] batch_resize_index.py — conversao em lote")
    if not BATCH_SCRIPT.exists():
        fail("batch_resize_index.py nao encontrado")
        return

    batch_root = tmp_dir / "test_batch"
    prod_dir = batch_root / "production"
    prod_dir.mkdir(parents=True)
    (batch_root / "indexed").mkdir()

    # Criar sprite RGBA 40x40 (nao multiplo de 8 para testar redim)
    make_rgba_sprite(prod_dir / "hero.png", 40, 40)

    # Spec JSON — com transparency=True: batch salva RGBA (estado intermediario valido para ResComp)
    spec = {
        "production": [{
            "name": "hero",
            "png_rel": "production/hero.png",
            "w": 32, "h": 32,
            "bmp_rel": "indexed/hero.bmp",
            "bmp_w": 32, "bmp_h": 32,
            "transparency": True
        }],
        "boards": []
    }
    spec_file = tmp_dir / "test_spec.json"
    spec_file.write_text(json.dumps(spec))

    result = subprocess.run(
        [sys.executable, str(BATCH_SCRIPT),
         "--spec", str(spec_file),
         "--batch-root", str(batch_root)],
        capture_output=True, text=True
    )
    assert_equal("batch_resize exit code 0", 0, result.returncode)

    # Com transparency=True: batch produz RGBA (intermediario) — ResComp aceita RGBA
    # Para obter modo P final, rodar fix_png_transparency_final.py depois
    with Image.open(prod_dir / "hero.png") as img:
        assert_in("Apos batch (transparency=True): modo RGBA ou P",
                  img.mode, ["RGBA", "P"])
        assert_equal("Apos batch: largura e 32", 32, img.size[0])
        assert_equal("Apos batch: altura e 32", 32, img.size[1])

    # Verificar que o BMP indexado foi criado
    bmp_path = batch_root / "indexed" / "hero.bmp"
    assert_equal("BMP indexado criado", True, bmp_path.exists())

    # Pipeline completo: batch + fix_transparency → modo P final
    if FIX_SCRIPT.exists():
        subprocess.run(
            [sys.executable, str(FIX_SCRIPT), str(prod_dir / "hero.png")],
            capture_output=True, text=True
        )
        with Image.open(prod_dir / "hero.png") as img:
            assert_equal("Apos batch+fix: modo e P (indexado)", "P", img.mode)


def test_res_suggestion_correctness(tmp_dir: Path):
    log("\n[TEST] .res suggestion — calculo correto de tiles")
    project = tmp_dir / "test_res_sug"
    res_dir = project / "res" / "sprite"
    res_dir.mkdir(parents=True)

    # Sprite 48x32 = 6x4 tiles
    make_ok_sprite(res_dir / "boss.png", 48, 32)
    (project / "res" / "sprite.res").write_text(
        'SPRITE boss "sprite/boss.png" 6 4 FAST 5\n'
    )

    report = run_diagnostic(project)
    assets = report.get("assets", [])

    if assets:
        res_sug = assets[0].get("res_suggestion", "")
        log(f"  .res sugerido: {res_sug}", indent=1)
        assert_in(".res menciona 6 tiles largura", "6", res_sug)
        assert_in(".res menciona 4 tiles altura", "4", res_sug)
        assert_in(".res e SPRITE type", "SPRITE", res_sug)


def test_full_pipeline_integration(tmp_dir: Path):
    log("\n[TEST] Integracao completa — diagnosticar, converter, re-diagnosticar")
    if not BATCH_SCRIPT.exists() or not FIX_SCRIPT.exists():
        fail("Scripts de conversao nao encontrados")
        return

    project = tmp_dir / "test_integration"
    data_dir = project / "data" / "production"
    data_dir.mkdir(parents=True)
    (project / "data" / "indexed").mkdir()
    (project / "res").mkdir()

    # 1. Criar asset com problemas
    make_rgba_sprite(data_dir / "player.png", 40, 35)  # RGBA + dim errada

    # 2. Diagnosticar — deve ter issues criticos
    report_before = run_diagnostic(project)
    assets_before = report_before.get("assets", [])
    had_issues = len(assets_before) > 0 and len(assets_before[0]["issues"]) > 0
    assert_equal("Antes da conversao: tem issues", True, had_issues)

    # 3. Converter
    spec = {
        "production": [{
            "name": "player",
            "png_rel": "production/player.png",
            "w": 40, "h": 32,  # ajuste para multiplo de 8
            "bmp_rel": "indexed/player.bmp",
            "bmp_w": 40, "bmp_h": 32,
            "transparency": True
        }],
        "boards": []
    }
    spec_file = tmp_dir / "integration_spec.json"
    spec_file.write_text(json.dumps(spec))

    subprocess.run(
        [sys.executable, str(BATCH_SCRIPT),
         "--spec", str(spec_file),
         "--batch-root", str(project / "data")],
        capture_output=True, text=True
    )

    # 4. Fix transparencia (batch com transparency=True produz RGBA intermediario)
    if FIX_SCRIPT.exists():
        subprocess.run(
            [sys.executable, str(FIX_SCRIPT), str(project / "data" / "production")],
            capture_output=True, text=True
        )

    # 5. Re-diagnosticar
    report_after = run_diagnostic(project)
    assets_after = report_after.get("assets", [])

    if assets_after:
        criticos_after = [i for i in assets_after[0]["issues"] if i["severity"] == "critico"]
        # Apos batch + fix, nao deve ter NOT_INDEXED
        assert_equal("Apos conversao+fix: sem NOT_INDEXED", True,
                    not any(i["code"] == "NOT_INDEXED" for i in criticos_after))
        assert_equal("Apos conversao+fix: modo e P", "P", assets_after[0]["mode"])


# ---------------------------------------------------------------------------
# Runner principal
# ---------------------------------------------------------------------------

def main():
    global VERBOSE

    parser = argparse.ArgumentParser(description="Suite de testes do pipeline de arte SGDK")
    parser.add_argument("--verbose", "-v", action="store_true", help="Output verboso")
    parser.add_argument("--keep-temp", action="store_true", help="Nao apagar diretorio temporario")
    args = parser.parse_args()
    VERBOSE = args.verbose

    if not DIAGNOSTIC_SCRIPT.exists():
        print(f"[ERRO] art_diagnostic.py nao encontrado em: {DIAGNOSTIC_SCRIPT}")
        return 1

    print("\n" + "="*65)
    print("  TEST SUITE: Art Pipeline SGDK / Mega Drive")
    print("="*65)

    tmp_dir = Path(tempfile.mkdtemp(prefix="art_test_"))
    log(f"Diretorio temporario: {tmp_dir}")

    try:
        # Testes de diagnostico
        test_detect_not_indexed(tmp_dir)
        test_detect_too_many_colors(tmp_dir)
        test_detect_bad_dimensions(tmp_dir)
        test_detect_ok_sprite(tmp_dir)
        test_detect_colors_not_9bit(tmp_dir)
        test_scenario_3_no_art(tmp_dir)
        test_scenario_1_data_needs_conversion(tmp_dir)

        # Testes de conversao
        test_conversion_fix_transparency(tmp_dir)
        test_conversion_batch_resize(tmp_dir)
        test_res_suggestion_correctness(tmp_dir)

        # Teste de integracao
        test_full_pipeline_integration(tmp_dir)

    finally:
        if not args.keep_temp:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        else:
            log(f"\nArtefatos preservados em: {tmp_dir}")

    total = PASSED + FAILED
    print("\n" + "="*65)
    print(f"  RESULTADO: {PASSED}/{total} testes passaram", end="")
    if FAILED > 0:
        print(f"  |  {FAILED} FALHAS")
    else:
        print("  [OK] TUDO OK")
    print("="*65)

    if FAILED > 0:
        print("\nPericia do pipeline: INSUFICIENTE -- revisar issues acima")
        return 1
    else:
        print("\nPericia do pipeline: VALIDADA -- agente apto para trabalho de arte")
        return 0


if __name__ == "__main__":
    sys.exit(main())

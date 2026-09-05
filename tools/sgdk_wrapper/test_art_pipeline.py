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
import hashlib
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
COLOR_LIB = SCRIPT_DIR / "forge_art" / "vdp_color.py"
PIXEL_CONTRACT = SCRIPT_DIR / "forge_art" / "pixel_contract.py"
JOB_LIB = SCRIPT_DIR / "forge_art" / "job.py"
GIMP_BATCH_LIB = SCRIPT_DIR / "forge_art" / "gimp_batch.py"

sys.path.insert(0, str(SCRIPT_DIR))

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

def run_diagnostic(project_path: Path, include_history: bool = False) -> dict:
    """Executa art_diagnostic.py e retorna o JSON do relatorio."""
    command = [sys.executable, str(DIAGNOSTIC_SCRIPT),
               "--project", str(project_path), "--json-only"]
    if include_history:
        command.append("--include-history")
    result = subprocess.run(
        command,
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


def test_diagnostic_active_only_excludes_history(tmp_dir: Path):
    log("\n[TEST] Diagnostico active-only nao oferece archive/staging como fonte")
    project = tmp_dir / "test_active_only"
    (project / "data/source_art").mkdir(parents=True)
    (project / "data/archive/rejected").mkdir(parents=True)
    (project / "data/staging/v99").mkdir(parents=True)
    (project / "res").mkdir()
    make_ok_sprite(project / "data/source_art/active.png")
    make_ok_sprite(project / "data/archive/rejected/old.png")
    make_ok_sprite(project / "data/staging/v99/probe.png")

    active = run_diagnostic(project)
    full = run_diagnostic(project, include_history=True)
    assert_equal("active-only analisa somente fonte ativa", 1, active["source_asset_status"]["total"])
    assert_equal("auditoria historica inclui as tres imagens", 3, full["source_asset_status"]["total"])
    assert_equal("modo active-only declarado", "active_only", active["discovery_policy"]["mode"])
    assert_equal("modo historico declarado", "full_history", full["discovery_policy"]["mode"])


def test_scenario_4_nested_lab_art_discovery(tmp_dir: Path):
    log("\n[TEST] Cenario 4 — laboratorio com arte e viewer SGDK aninhado")
    project = tmp_dir / "test_nested_lab"
    (project / "work" / "frames").mkdir(parents=True)
    (project / "analysis").mkdir()
    (project / "evidence").mkdir()
    (project / "rascunho" / "inputs").mkdir(parents=True)
    (project / "doc").mkdir()
    (project / "doc" / "project_hygiene_manifest.json").write_text(
        json.dumps({"schema_version": "1.0.0", "external_inputs": []})
    )

    make_ok_sprite(project / "work" / "frames" / "working_frame.png")
    make_ok_sprite(project / "analysis" / "palette_review.png")
    make_ok_sprite(project / "evidence" / "blastem_capture.png")
    (project / "rascunho" / "inputs" / "source_stage.sff").write_bytes(b"ElecbyteSpr")

    nested = project / "sgdk_viewer" / "viewer"
    (nested / "src").mkdir(parents=True)
    (nested / "res" / "gfx").mkdir(parents=True)
    (nested / "data" / "source_art").mkdir(parents=True)
    (nested / "doc").mkdir()
    (nested / "src" / "main.c").write_text("int main(void) { return 0; }\n")
    (nested / "res" / "resources.res").write_text(
        'IMAGE active_bg "gfx/active_bg.png" FAST\n'
    )
    (nested / "doc" / "project_hygiene_manifest.json").write_text(
        json.dumps({"schema_version": "1.0.0", "external_inputs": []})
    )
    make_ok_sprite(nested / "res" / "gfx" / "active_bg.png")
    make_ok_sprite(nested / "data" / "source_art" / "source_bg.png")

    external = tmp_dir / "external_art"
    external.mkdir()
    make_ok_sprite(external / "must_not_be_followed.png")
    symlink_created = False
    try:
        (project / "work" / "external_link").symlink_to(external, target_is_directory=True)
        symlink_created = True
    except (OSError, NotImplementedError):
        pass

    result = subprocess.run(
        [sys.executable, str(DIAGNOSTIC_SCRIPT), "--project", str(project), "--json-only"],
        capture_output=True, text=True
    )
    assert_equal("Cenario 4 nao usa exit 2", 0, result.returncode)
    report = json.loads(result.stdout)
    assert_equal("Cenario detectado e 4_lab_nested_art_review",
                 "4_lab_nested_art_review", report.get("scenario_detected"))

    inventory = report.get("art_inventory", {})
    assert_equal("Separa source art", 2, inventory.get("source_art", {}).get("count"))
    assert_equal("Separa evidence art", 1, inventory.get("evidence_art", {}).get("count"))
    assert_equal("Separa active res art", 1, inventory.get("active_res_art", {}).get("count"))
    assert_equal("Separa lab work art", 1, inventory.get("lab_work_art", {}).get("count"))
    assert_equal("Separa analysis art", 1, inventory.get("analysis_art", {}).get("count"))
    assert_equal("Detecta um viewer SGDK aninhado", 1, len(report.get("nested_projects", [])))
    if report.get("nested_projects"):
        assert_equal("Viewer aninhado possui hygiene manifest", True,
                     report["nested_projects"][0]["hygiene_manifest"]["present"])
    assert_equal("Discovery nao segue diretorios externos", False,
                 report.get("discovery_policy", {}).get("external_directories_followed"))

    if symlink_created:
        all_paths = [
            path
            for entry in inventory.values()
            for path in entry.get("paths", [])
        ]
        assert_equal("Arte externa via symlink nao entra no inventario", False,
                     any("must_not_be_followed" in path for path in all_paths))
        warning_codes = [w.get("code") for w in report.get("discovery_warnings", [])]
        assert_in("Symlink externo gera aviso explicito", "SYMLINK_DIRECTORY_SKIPPED", warning_codes)


def test_pillow_pixel_api_has_no_deprecation_warning(tmp_dir: Path):
    log("\n[TEST] Pillow — contagem de pixels sem Image.getdata deprecado")
    project = tmp_dir / "test_pillow_api"
    res_dir = project / "res" / "sprite"
    res_dir.mkdir(parents=True)
    make_ok_sprite(res_dir / "hero.png")
    (project / "res" / "sprite.res").write_text(
        'SPRITE hero "sprite/hero.png" 4 4 FAST 5\n'
    )

    result = subprocess.run(
        [sys.executable, "-W", "error::DeprecationWarning", str(DIAGNOSTIC_SCRIPT),
         "--project", str(project), "--json-only"],
        capture_output=True, text=True
    )
    assert_equal("Diagnostico passa com DeprecationWarning tratado como erro", 0, result.returncode)
    assert_equal("stderr nao contem DeprecationWarning", False,
                 "DeprecationWarning" in result.stderr)


# ---------------------------------------------------------------------------
# Regressao do contrato pixel-strict (forge-art P0.3)
#
# A versao anterior deste arquivo institucionalizava a contradicao que o
# pipeline tinha: aceitava RGBA como "estado intermediario valido para ResComp"
# e chamava `fix_png_transparency_final.py` de etapa final do "pipeline
# completo". O teste media que o modo virava `P` e nunca que o index 0
# sobrevivia — e o fixer, por construcao, compunha sobre preto e removia a
# transparencia. Verde estavel medindo a coisa errada.
#
# Os testes abaixo existem para FALHAR quando o pipeline reintroduzir: RGBA
# como saida, PLTE inflada, interpolacao proibida, index 0 incorreto, cor fora
# da grade do VDP ou saida nao deterministica.
# ---------------------------------------------------------------------------

def test_deprecated_converters_fail_closed(tmp_dir: Path):
    log("\n[TEST] conversores destrutivos foram removidos do caminho canonico")
    for label, script in (("batch_resize_index", BATCH_SCRIPT),
                          ("fix_png_transparency_final", FIX_SCRIPT)):
        if not script.exists():
            fail(f"{label}: shim de deprecacao ausente")
            continue
        result = subprocess.run(
            [sys.executable, str(script), str(tmp_dir)],
            capture_output=True, text=True,
        )
        assert_equal(f"{label} falha fechado (exit != 0)", True, result.returncode != 0)
        combined = result.stdout + result.stderr
        assert_in(f"{label} explica a proxima acao causal", "proxima acao", combined.lower())


def test_color_library_self_check(tmp_dir: Path):
    log("\n[TEST] biblioteca canonica de cor — self-check positivo e negativo")
    result = subprocess.run(
        [sys.executable, str(COLOR_LIB), "--self-check"],
        capture_output=True, text=True,
    )
    assert_equal("vdp_color --self-check exit 0", 0, result.returncode)
    report = json.loads(result.stdout)
    assert_equal("nenhuma fixture de cor falhou", False, report["blocking"])
    kinds = {f["kind"] for f in report["fixtures"]}
    assert_in("self-check de cor exercita fixture negativa", "negative", kinds)
    assert_in("self-check de cor exercita fixture positiva", "positive", kinds)


def test_pixel_contract_self_check(tmp_dir: Path):
    log("\n[TEST] contrato pixel-strict — self-check positivo e negativo")
    result = subprocess.run(
        [sys.executable, str(PIXEL_CONTRACT), "--self-check"],
        capture_output=True, text=True,
    )
    assert_equal("pixel_contract --self-check exit 0", 0, result.returncode)
    report = json.loads(result.stdout)
    assert_equal("nenhuma fixture de contrato falhou", False, report["blocking"])
    kinds = {f["kind"] for f in report["fixtures"]}
    assert_in("self-check de contrato exercita fixture negativa", "negative", kinds)


def test_rgba_output_is_rejected(tmp_dir: Path):
    log("\n[TEST] RGBA NAO e estado valido de saida (regressao da contradicao antiga)")
    from forge_art import pixel_contract as pc

    work = tmp_dir / "test_rgba_rejected"
    work.mkdir(parents=True)
    rgba_png = work / "hero.png"
    make_rgba_sprite(rgba_png, 32, 32)

    report = pc.validate_png(rgba_png, pc.ROLE_TRANSPARENT0)
    assert_in("RGBA dispara output_not_indexed", "output_not_indexed",
              report["blocking_statuses"])
    assert_equal("RGBA nao pode virar technical_candidate", "rejected", report["status"])


def test_conforming_asset_is_only_technical_candidate(tmp_dir: Path):
    log("\n[TEST] asset conforme nasce technical_candidate, nunca aprovado")
    from forge_art import pixel_contract as pc

    work = tmp_dir / "test_conforming"
    work.mkdir(parents=True)
    png = work / "sprite.png"
    pc._write_ok_sprite(png, 16, 16)

    report = pc.validate_png(png, pc.ROLE_TRANSPARENT0)
    assert_equal("asset conforme nao tem blockers", [], report["blocking_statuses"])
    assert_equal("status e technical_candidate", "technical_candidate", report["status"])
    assert_equal("scope declarado e static_contract", "static_contract", report["scope"])


def test_forbidden_interpolation_is_measurable(tmp_dir: Path):
    log("\n[TEST] interpolacao proibida reprova na guarda E no arquivo resultante")
    from forge_art import pixel_contract as pc

    work = tmp_dir / "test_interp"
    work.mkdir(parents=True)

    # 1. Guarda de API
    blocked = 0
    for method in sorted(pc.FORBIDDEN_RESAMPLE):
        try:
            pc.assert_nearest_resample(method)
        except pc.PixelContractError as exc:
            blocked += 1 if exc.blocker == "non_nearest_downscale" else 0
    assert_equal("todos os metodos interpolados sao bloqueados",
                 len(pc.FORBIDDEN_RESAMPLE), blocked)

    # 2. Calibracao anti-falso-positivo: NEAREST continua permitido
    assert_equal("NEAREST nao e falso positivo", "NEAREST",
                 pc.assert_nearest_resample("Image.Resampling.NEAREST"))

    # 3. Prova no arquivo: a saida Lanczos reprova por cor fora da grade
    source = Image.new("P", (64, 64))
    source.putpalette([0, 0, 0, 0x22, 0x22, 0x22, 0xEE, 0xCC, 0x88] + [0] * 759)
    px = source.load()
    for y in range(64):
        for x in range(64):
            px[x, y] = 0 if (x + y) % 7 == 0 else 1 + ((x // 8 + y // 8) % 2)

    lanczos_png = work / "lanczos.png"
    (source.convert("RGB")
           .resize((16, 16), Image.Resampling.LANCZOS)
           .quantize(colors=16)
           .save(lanczos_png, "PNG"))
    rep_lanczos = pc.validate_png(lanczos_png, pc.ROLE_UNUSED0)
    assert_in("saida Lanczos reprova por cor fora da grade", "color_off_vdp_grid",
              rep_lanczos["blocking_statuses"])

    nearest_png = work / "nearest.png"
    nearest = source.resize((16, 16), Image.Resampling.NEAREST)
    nearest.save(nearest_png, "PNG", bits=4, transparency=0)
    rep_nearest = pc.validate_png(nearest_png, pc.ROLE_TRANSPARENT0)
    assert_equal("saida NEAREST equivalente passa", "technical_candidate",
                 rep_nearest["status"])


def test_output_is_deterministic(tmp_dir: Path):
    log("\n[TEST] determinismo — mesmo conteudo produz o mesmo SHA-256")
    from forge_art import pixel_contract as pc

    work = tmp_dir / "test_determinism"
    work.mkdir(parents=True)
    a, b, c = work / "a.png", work / "b.png", work / "c.png"
    pc._write_ok_sprite(a, 16, 16)
    pc._write_ok_sprite(b, 16, 16)
    pc._write_ok_sprite(c, 24, 16)

    assert_equal("mesmo conteudo, mesmo hash",
                 pc.canonical_content_hash(a), pc.canonical_content_hash(b))
    assert_equal("conteudo diferente, hash diferente", True,
                 pc.canonical_content_hash(a) != pc.canonical_content_hash(c))
    # O hash nunca pode usar `hash()` do Python: instavel entre processos.
    remote = subprocess.run(
        [sys.executable, "-c",
         "import sys;sys.path.insert(0,%r);"
         "from forge_art import pixel_contract as pc;"
         "print(pc.canonical_content_hash(%r))" % (str(SCRIPT_DIR), str(a))],
        capture_output=True, text=True,
    )
    assert_equal("hash estavel entre processos",
                 pc.canonical_content_hash(a), remote.stdout.strip())


def test_source_is_never_overwritten(tmp_dir: Path):
    log("\n[TEST] a validacao nunca escreve na fonte")
    from forge_art import pixel_contract as pc

    work = tmp_dir / "test_readonly"
    work.mkdir(parents=True)
    png = work / "source.png"
    pc._write_ok_sprite(png, 16, 16)
    before = png.read_bytes()
    stat_before = png.stat().st_mtime_ns

    pc.validate_png(png, pc.ROLE_TRANSPARENT0)
    pc.validate_png(png, pc.ROLE_UNUSED0)
    pc.canonical_content_hash(png)

    assert_equal("bytes da fonte intactos", before, png.read_bytes())
    assert_equal("mtime da fonte intacto", stat_before, png.stat().st_mtime_ns)


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



def test_job_self_check(tmp_dir: Path):
    log("\n[TEST] jobs imutaveis — self-check positivo e negativo")
    result = subprocess.run(
        [sys.executable, str(JOB_LIB), "--self-check"],
        capture_output=True, text=True,
    )
    assert_equal("job --self-check exit 0", 0, result.returncode)
    report = json.loads(result.stdout)
    assert_equal("nenhuma fixture de job falhou", False, report["blocking"])
    kinds = {f["kind"] for f in report["fixtures"]}
    assert_in("self-check de job exercita fixture negativa", "negative", kinds)


def test_convert_self_check(tmp_dir: Path):
    log("\n[TEST] convert — schema, paleta ponderada, cache e caminhos hostis")
    from forge_art import convert as converter
    report = converter.self_check()
    assert_equal("convert self_check nao bloqueia", False, report["blocking"])
    assert_in("convert self_check cobre caminho hostil", "external_symlink_source_rejected", [f["name"] for f in report["fixtures"]])
    assert_in("convert rejeita report resealed sem metrics", "rejects_resealed_invalid_conversion_report", [f["name"] for f in report["fixtures"]])


def test_gimp_batch_contract_and_fail_closed(tmp_dir: Path):
    log("\n[TEST] GIMP batch opcional — headless, restrito e sem dependencia de GUI")
    from forge_art import gimp_batch

    report = gimp_batch.self_check()
    assert_equal("contrato GIMP batch nao bloqueia", False, report["blocking"])
    names = [fixture["name"] for fixture in report["fixtures"]]
    assert_in("operacao arbitraria e rejeitada",
              "arbitrary_operation_is_rejected", names)

    missing = tmp_dir / "gimp_definitely_missing"
    result = subprocess.run(
        [sys.executable, "-m", "forge_art", "gimp-batch-preflight",
         "--gimp", str(missing), "--timeout-seconds", "2"],
        capture_output=True, text=True, cwd=str(SCRIPT_DIR),
    )
    assert_equal("preflight sem GIMP falha fechado (exit 3)", 3, result.returncode)
    payload = json.loads(result.stdout)
    assert_in("preflight nomeia executavel ausente",
              "gimp_batch_executable_not_found", payload["blockers"])


def test_job_id_is_reproducible_across_processes(tmp_dir: Path):
    log("\n[TEST] job_id e reproduzivel por outro agente, em outro caminho")
    from forge_art import job as fj
    from forge_art import pixel_contract as pc

    work = tmp_dir / "test_job_repro"
    work.mkdir(parents=True)
    source = work / "hero.png"
    pc._write_ok_sprite(source, 16, 16)

    # O gemeo mora em outro diretorio E tem outro nome. Reusar o mesmo caminho
    # absoluto aqui testava apenas que o hash e estavel dentro da maquina, e
    # deixava passar a dependencia de caminho — que quebra o cache entre
    # checkouts e entre maquinas, exatamente o que o job_id promete.
    other = tmp_dir / "test_job_repro_outra_arvore"
    other.mkdir(parents=True)
    twin = other / "renomeado.png"
    twin.write_bytes(source.read_bytes())

    spec = fj.JobSpec(asset_id="hero", sources=(source,),
                      route=fj.ROUTE_TECHNICAL,
                      index0_role=pc.ROLE_TRANSPARENT0)
    local = fj.compute_job_id(spec)

    remote = subprocess.run(
        [sys.executable, "-c",
         "import sys;sys.path.insert(0,%r);"
         "from forge_art import job as fj;from forge_art import pixel_contract as pc;"
         "print(fj.compute_job_id(fj.JobSpec(asset_id='hero',sources=(%r,),"
         "route=fj.ROUTE_TECHNICAL,index0_role=pc.ROLE_TRANSPARENT0)))"
         % (str(SCRIPT_DIR), str(twin))],
        capture_output=True, text=True,
    )
    assert_equal("mesmo job_id em outro processo, outro caminho e outro nome",
                 local, remote.stdout.strip())


def test_job_never_writes_to_source(tmp_dir: Path):
    log("\n[TEST] job comportado: fonte e res/ intactos, saida so technical_candidate")
    from forge_art import job as fj
    from forge_art import pixel_contract as pc

    root = tmp_dir / "test_job_readonly"
    src_dir = root / "data" / "source_art"
    res_dir = root / "res"
    src_dir.mkdir(parents=True)
    res_dir.mkdir(parents=True)
    source = src_dir / "hero.png"
    pc._write_ok_sprite(source, 16, 16)
    guard = res_dir / "existing.png"
    pc._write_ok_sprite(guard, 16, 16)

    before_src = source.read_bytes()
    before_res = sorted(p.name for p in res_dir.iterdir())
    before_guard = guard.read_bytes()

    def honest_work(staging: Path) -> dict:
        candidate = staging / "basic" / "out.png"
        pc._write_ok_sprite(candidate, 16, 16)
        report = pc.validate_png(candidate, pc.ROLE_TRANSPARENT0)
        (staging / "reports" / fj.PIXEL_REPORT_NAME).write_text(
            json.dumps(report), encoding="utf-8")
        return {"ok": True}

    spec = fj.JobSpec(asset_id="hero", sources=(source,),
                      route=fj.ROUTE_TECHNICAL,
                      index0_role=pc.ROLE_TRANSPARENT0)
    state = fj.run_job(root, spec, work=honest_work)

    assert_equal("fonte intacta byte a byte", before_src, source.read_bytes())
    assert_equal("res/ nao ganhou nem perdeu arquivo", before_res,
                 sorted(p.name for p in res_dir.iterdir()))
    assert_equal("arquivo pre-existente em res/ intacto", before_guard, guard.read_bytes())
    assert_equal("job declarou a fonte intacta", True, state["source_intact"])
    assert_equal("job nasce technical_candidate", "technical_candidate",
                 state["output_status"])
    assert_equal("job nao e promovivel sozinho", False, state["promotion"]["promotable"])


def test_job_contains_hostile_work_step(tmp_dir: Path):
    """O teste anterior so provava que um `work` bem-comportado nao suja nada.

    Isso nao mede a contencao: mede a boa educacao do callback. Aqui o `work`
    tenta ativamente escrever fora do staging, e o que se exige e que o job
    reprove, nao publique, e DESFACA o estrago.
    """
    log("\n[TEST] job hostil: escrita fora do staging e barrada e revertida")
    from forge_art import job as fj
    from forge_art import pixel_contract as pc

    root = tmp_dir / "test_job_hostile"
    src_dir = root / "data" / "source_art"
    res_dir = root / "res"
    src_dir.mkdir(parents=True)
    res_dir.mkdir(parents=True)
    source = src_dir / "hero.png"
    pc._write_ok_sprite(source, 16, 16)
    before_src = source.read_bytes()
    injected = res_dir / "injected.png"

    # 1) work que injeta arquivo em res/ (promocao automatica disfarcada)
    def injects(staging: Path) -> dict:
        pc._write_ok_sprite(injected, 16, 16)
        return {}

    spec = fj.JobSpec(asset_id="hero", sources=(source,),
                      route=fj.ROUTE_TECHNICAL,
                      index0_role=pc.ROLE_TRANSPARENT0,
                      params={"inject": "res"})
    blocker = None
    try:
        fj.run_job(root, spec, work=injects)
    except fj.JobContractError as exc:
        blocker = exc.blocker
    assert_equal("escrita em res/ reprova o job", "protected_tree_mutated", blocker)
    assert_equal("arquivo injetado em res/ foi removido", False, injected.exists())
    assert_equal("job com escrita externa nao foi publicado", False,
                 fj.job_dir(root, spec, fj.compute_job_id(spec)).exists())

    # 2) work que sobrescreve a propria fonte
    def overwrites_source(staging: Path) -> dict:
        source.write_bytes(b"\x89PNG\r\n\x1a\nlixo")
        return {}

    spec2 = fj.JobSpec(asset_id="hero", sources=(source,),
                       route=fj.ROUTE_TECHNICAL,
                       index0_role=pc.ROLE_TRANSPARENT0,
                       params={"inject": "source"})
    blocker2 = None
    try:
        fj.run_job(root, spec2, work=overwrites_source)
    except fj.JobContractError as exc:
        blocker2 = exc.blocker
    assert_equal("sobrescrever a fonte reprova o job", "protected_tree_mutated", blocker2)
    assert_equal("fonte foi RESTAURADA, nao apenas detectada",
                 before_src, source.read_bytes())


def test_job_without_evidence_is_not_green(tmp_dir: Path):
    log("\n[TEST] job sem artefato nem relatorio nao se declara technical_candidate")
    from forge_art import job as fj
    from forge_art import pixel_contract as pc

    root = tmp_dir / "test_job_no_evidence"
    src_dir = root / "data" / "source_art"
    src_dir.mkdir(parents=True)
    source = src_dir / "hero.png"
    pc._write_ok_sprite(source, 16, 16)

    spec = fj.JobSpec(asset_id="hero", sources=(source,),
                      route=fj.ROUTE_TECHNICAL,
                      index0_role=pc.ROLE_TRANSPARENT0)
    blocker = None
    try:
        fj.run_job(root, spec, work=lambda d: {"note": "nao produzi nada"})
    except fj.JobContractError as exc:
        blocker = exc.blocker
    assert_equal("job sem evidencia reprova", "job_produced_no_candidate", blocker)

    # Evidencia PARCIAL tambem reprova: um arquivo qualquer em basic/ ou em
    # reports/ nao compra um technical_candidate.
    def only_reports(staging: Path) -> dict:
        (staging / "reports" / "note.txt").write_text("nada a ver")
        return {}

    def only_basic(staging: Path) -> dict:
        (staging / "basic" / "note.txt").write_text("nem PNG e")
        return {}

    def png_sem_relatorio(staging: Path) -> dict:
        pc._write_ok_sprite(staging / "basic" / "out.png", 16, 16)
        return {}

    for nome, esperado, fn in (
        ("so reports/", "job_produced_no_candidate", only_reports),
        ("so basic/ sem PNG", "job_produced_no_candidate", only_basic),
        ("PNG sem relatorio", "job_missing_pixel_report", png_sem_relatorio),
    ):
        got = None
        try:
            fj.run_job(root, fj.JobSpec(
                asset_id="hero", sources=(source,), route=fj.ROUTE_TECHNICAL,
                index0_role=pc.ROLE_TRANSPARENT0, params={"caso": nome}), work=fn)
        except fj.JobContractError as exc:
            got = exc.blocker
        assert_equal(f"evidencia parcial reprova ({nome})", esperado, got)

    blocker2 = None
    try:
        fj.run_job(root, spec, work=None)
    except fj.JobContractError as exc:
        blocker2 = exc.blocker
    assert_equal("job sem etapa de trabalho reprova", "job_without_work_step", blocker2)


def test_cli_exists_and_fails_closed_on_unimplemented(tmp_dir: Path):
    log("\n[TEST] CLI existe e comandos nao implementados falham fechado")
    r = subprocess.run([sys.executable, "-m", "forge_art", "--help"],
                       capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    assert_equal("`python3 -m forge_art --help` funciona", 0, r.returncode)
    for cmd in ("inspect", "validate", "palette", "translate", "convert",
                "source-audit", "route-shootout", "route-verify",
                "gimp-batch-preflight", "workset-validate", "self-check"):
        assert_in(f"CLI anuncia {cmd}", cmd, r.stdout)

    for cmd in ("atlas", "tiles", "compare", "promote"):
        rr = subprocess.run([sys.executable, "-m", "forge_art", cmd],
                            capture_output=True, text=True, cwd=str(SCRIPT_DIR))
        assert_equal(f"{cmd} falha fechado (exit 2)", 2, rr.returncode)
        assert_in(f"{cmd} nomeia a proxima acao", "next_action", rr.stdout)

    # convert e real: fixture neutra, fonte relativa, staging-only.
    from forge_art import pixel_contract as pc
    project = tmp_dir / "convert_project"; (project / "data").mkdir(parents=True); (project / "res").mkdir()
    pc._write_ok_sprite(project / "data" / "neutral.png", 16, 16)
    source_before = hashlib.sha256((project / "data" / "neutral.png").read_bytes()).hexdigest()
    spec = {"schema_version":"1.0.0","route":"technical_conversion","asset_id":"neutral_fixture","source":"data/neutral.png","source_kind":"technical_fixture","target_width":16,"target_height":16,"index0_role":"transparent0","resize_policy":"NEAREST","palette_strategy":"weighted_kmedoids_v1","max_visible_colors":15,"dithering_strategy":"none","transparency_policy":"binary_alpha","oracle":"rescomp","output_name":"neutral.png","intended_use":"neutral_fixture"}
    sp = project / "spec.json"; sp.write_text(json.dumps(spec))
    rc = subprocess.run([sys.executable,"-m","forge_art","convert","--project-root",str(project),"--spec",str(sp)],capture_output=True,text=True,cwd=str(SCRIPT_DIR))
    assert_equal("convert tecnico pela CLI", 0, rc.returncode)
    payload=json.loads(rc.stdout)
    assert_equal("convert permanece technical_candidate", "technical_candidate", payload["output_status"])
    assert_equal("convert nao promove", False, payload["promotion"]["promotable"])
    from forge_art import schema_gate
    job_root = Path(payload["job_dir"])
    conversion = json.loads((job_root / "reports" / "conversion_report.json").read_text())
    pixel_report = json.loads((job_root / "reports" / "pixel_compliance_report.json").read_text())
    try:
        schema_gate.validate_named(payload, "job_state")
        schema_gate.validate_named(conversion, "conversion_report")
        schema_gate.validate_named(pixel_report, "pixel_compliance_report")
        schema_valid = True
    except Exception:
        schema_valid = False
    assert_equal("reports e job_state passam schemas", True, schema_valid)
    assert_equal("hash fonte coincide no report", source_before, conversion["source_sha256"])
    assert_equal("fonte permanece intacta", source_before, hashlib.sha256((project / "data" / "neutral.png").read_bytes()).hexdigest())
    assert_equal("res permanece vazio", [], list((project / "res").iterdir()))
    cached = subprocess.run([sys.executable,"-m","forge_art","convert","--project-root",str(project),"--spec",str(sp)],capture_output=True,text=True,cwd=str(SCRIPT_DIR))
    assert_equal("cache de convert reproduz job", payload["job_id"], json.loads(cached.stdout)["job_id"])

    # translate nao gera pixel: registra encaminhamento e sai reprovado.
    rt = subprocess.run([sys.executable, "-m", "forge_art", "translate",
                         "--asset-id", "taina_idle_48x64"],
                        capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    assert_equal("translate nao devolve sucesso", 3, rt.returncode)
    assert_in("translate encaminha para produtor capaz",
              "blocked_pending_capable_producer", rt.stdout)

    # Source sanitation + route portfolio: one clean source passes, a
    # contaminated declaration fails, and every emitted route remains a guide.
    route_source = project / "data" / "route_source.png"
    route_image = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    route_image.paste((0x22, 0x66, 0xAA, 255), (8, 4, 24, 46))
    route_image.save(route_source, "PNG")
    authority = project / "data" / "route_authority.png"
    route_image.save(authority, "PNG")
    authority_sha = hashlib.sha256(authority.read_bytes()).hexdigest()
    authority_contract = project / "data" / "route_visual_dna.json"
    authority_contract.write_text(json.dumps({"scale_contract": {"authorized_targets": [{"width": 32, "height": 48}]}}), encoding="utf-8")
    observations = {
        "baked_checkerboard": False, "ground_shadow": "absent",
        "dust_or_particles": "absent", "smoke_or_clouds": "absent",
        "floor_line": "absent", "text_or_annotation": "absent",
        "multiple_overlapping_poses": False, "cropped_extremities": False,
        "occluded_identity_features": False, "motion_blur": False,
        "background_color_collision": False, "notes": "neutral fixture",
    }
    triage_spec = {
        "schema_version": "1.0.0", "source_path": "data/route_source.png",
        "source_class": "high_res_full_body_character",
        "intended_role": "translation_source", "matte_policy": "existing_alpha",
        "reviewer": "agent_visual_triage",
        "identity_authority_path": "data/route_authority.png",
        "identity_authority_sha256": authority_sha,
        "visual_source_of_truth_contract": "data/route_visual_dna.json",
        "derivation": "fixture_translation_from_authority",
        "observations": observations,
    }
    triage_spec_path = project / "triage_spec.json"
    triage_spec_path.write_text(json.dumps(triage_spec), encoding="utf-8")
    triage_report_path = project / "out" / "logs" / "source_triage_report.json"
    source_audit = subprocess.run([
        sys.executable, "-m", "forge_art", "source-audit",
        "--project-root", str(project), "--spec", str(triage_spec_path),
        "--out", str(triage_report_path),
    ], capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    assert_equal("source-audit aceita fonte limpa", 0, source_audit.returncode)
    assert_equal("fonte limpa libera shootout", True,
                 json.loads(source_audit.stdout)["route_exploration_allowed"])

    contaminated = json.loads(json.dumps(triage_spec))
    contaminated["observations"]["ground_shadow"] = "touching_silhouette"
    contaminated_path = project / "triage_contaminated.json"
    contaminated_path.write_text(json.dumps(contaminated), encoding="utf-8")
    contaminated_report = project / "out" / "logs" / "contaminated_report.json"
    rejected = subprocess.run([
        sys.executable, "-m", "forge_art", "source-audit",
        "--project-root", str(project), "--spec", str(contaminated_path),
        "--out", str(contaminated_report),
    ], capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    assert_equal("source-audit bloqueia sombra tocando silhueta", 1, rejected.returncode)
    assert_in("sombra bloqueada e nomeada", "ground_shadow_touching_silhouette",
              json.loads(rejected.stdout)["blockers"])

    shootout_spec = {
        "schema_version": "1.0.0", "source_path": "data/route_source.png",
        "source_triage_report_path": "out/logs/source_triage_report.json",
        "source_class": "high_res_full_body_character",
        "scale_contract_path": "data/route_visual_dna.json",
        "output_dir": "out/route_shootout_fixture",
        "target": {"width": 32, "height": 48, "anchor": "bottom_center"},
        "route_policy": "preferred_plus_challengers",
        "include_negative_controls": False,
        "include_unavailable_placeholders": False,
    }
    shootout_spec_path = project / "route_shootout_spec.json"
    shootout_spec_path.write_text(json.dumps(shootout_spec), encoding="utf-8")
    shootout = subprocess.run([
        sys.executable, "-m", "forge_art", "route-shootout",
        "--project-root", str(project), "--spec", str(shootout_spec_path),
    ], capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    assert_equal("route-shootout CLI passa", 0, shootout.returncode)
    shootout_payload = json.loads(shootout.stdout)
    assert_equal("shootout nunca escolhe vencedor", None,
                 shootout_payload["automatic_winner"])
    assert_equal("shootout permanece guia mecanico", "mechanical_geometry_probe",
                 shootout_payload["claim_ceiling"])
    report_path = project / "out" / "route_shootout_fixture" / "route_shootout_report.json"
    route_verify = subprocess.run([
        sys.executable, "-m", "forge_art", "route-verify",
        "--project-root", str(project), "--report", str(report_path),
    ], capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    assert_equal("route-verify confirma causalidade e hashes", 0, route_verify.returncode)
    assert_equal("shootout nao toca res", [], list((project / "res").iterdir()))


def test_partial_alpha_is_rejected(tmp_dir: Path):
    log("\n[TEST] alpha parcial e segundo indice transparente reprovam")
    from PIL import Image
    from forge_art import pixel_contract as pc

    work = tmp_dir / "test_alpha"
    work.mkdir(parents=True)
    img = Image.new("P", (16, 16))
    img.putpalette([0x00, 0x00, 0x00, 0x22, 0x22, 0x22, 0x44, 0x66, 0xAA])
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = 0 if (x == 0 or y == 0) else 1 + ((x + y) % 2)

    partial = work / "partial.png"
    img.save(partial, "PNG", bits=4, transparency=bytes([0, 128, 255]))
    rep = pc.validate_png(partial, pc.ROLE_TRANSPARENT0)
    assert_in("alpha parcial reprova", "partial_alpha_rejected", rep["blocking_statuses"])
    assert_equal("asset com alpha parcial nao e technical_candidate",
                 "rejected", rep["status"])

    extra = work / "extra_transparent.png"
    img.save(extra, "PNG", bits=4, transparency=bytes([0, 0, 255]))
    rep2 = pc.validate_png(extra, pc.ROLE_TRANSPARENT0)
    assert_in("segundo indice transparente reprova", "extra_transparent_index",
              rep2["blocking_statuses"])

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
        test_diagnostic_active_only_excludes_history(tmp_dir)
        test_scenario_4_nested_lab_art_discovery(tmp_dir)
        test_pillow_pixel_api_has_no_deprecation_warning(tmp_dir)

        test_res_suggestion_correctness(tmp_dir)

        # Regressao do contrato pixel-strict (forge-art P0.3)
        test_deprecated_converters_fail_closed(tmp_dir)
        test_color_library_self_check(tmp_dir)
        test_pixel_contract_self_check(tmp_dir)
        test_rgba_output_is_rejected(tmp_dir)
        test_conforming_asset_is_only_technical_candidate(tmp_dir)
        test_forbidden_interpolation_is_measurable(tmp_dir)
        test_output_is_deterministic(tmp_dir)
        test_source_is_never_overwritten(tmp_dir)

        # Jobs imutaveis (forge-art P0.4)
        test_job_self_check(tmp_dir)
        test_convert_self_check(tmp_dir)
        test_gimp_batch_contract_and_fail_closed(tmp_dir)
        test_job_id_is_reproducible_across_processes(tmp_dir)
        test_job_never_writes_to_source(tmp_dir)
        test_job_contains_hostile_work_step(tmp_dir)
        test_job_without_evidence_is_not_green(tmp_dir)
        test_partial_alpha_is_rejected(tmp_dir)

        # CLI (forge-art P1, parcial)
        test_cli_exists_and_fails_closed_on_unimplemented(tmp_dir)

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
        # Nao dizer "agente apto para trabalho de arte": esta suite mede
        # conformidade de hardware e procedencia de processo. Ela nao mede
        # silhueta, anatomia, material nem leitura.
        print("\nContrato tecnico do pipeline: VALIDADO")
        print("Limite: nada aqui aprova QUALIDADE VISUAL. Nenhuma saida de "
              "maquina passa de technical_candidate sem decisao humana "
              "registrada. atlas, tiles, compare e promote continuam "
              "deliberadamente nao implementados.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

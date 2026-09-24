#!/usr/bin/env python3
"""
art_diagnostic.py - Diagnostico de assets visuais para projetos SGDK / Mega Drive

Analisa os diretorios /data e /res de um projeto e gera um relatorio estruturado
classificando cada asset como: ok, precisa_conversao, inadequado, ausente.

Uso:
  python tools/sgdk_wrapper/art_diagnostic.py --project <caminho_do_projeto>
  python tools/sgdk_wrapper/art_diagnostic.py --project <caminho> --output report.json
  python tools/sgdk_wrapper/art_diagnostic.py --project <caminho> --res-file sprite.res

Requisito: pip install Pillow
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:
    print("[ERRO] Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constantes do Mega Drive
# ---------------------------------------------------------------------------
VALID_9BIT_VALUES = {0x00, 0x22, 0x44, 0x66, 0x88, 0xAA, 0xCC, 0xEE}
MAX_PALETTE_COLORS = 15        # cores visiveis (index 0 = transparente)
MAX_SPRITE_DIM_TILES = 4       # 4x4 tiles = 32x32 px
MAX_SPRITE_PX = 32             # pixels por dimensao
MAX_BG_COLORS = 15             # por paleta
MAGENTA_TRANSPARENT = (0xFF, 0x00, 0xFF)  # convencao de transparencia
VISUAL_EXTENSIONS = {".png", ".pcx", ".bmp", ".gif", ".jpg", ".jpeg"}
SOURCE_ART_EXTENSIONS = VISUAL_EXTENSIONS | {".sff", ".ase", ".aseprite", ".psd"}
GENERATED_ARTIFACT_EXTENSIONS = {".bin", ".map", ".pal", ".tiles", ".tilemap"}
INVENTORY_PATH_PREVIEW_LIMIT = 25
HISTORICAL_PATH_MARKERS = ("archive", "rejected", "superseded", "negative_evidence")


# ---------------------------------------------------------------------------
# Estruturas de dados
# ---------------------------------------------------------------------------
@dataclass
class AssetIssue:
    code: str
    severity: str   # "critico" | "aviso" | "info"
    message: str
    suggestion: str = ""


@dataclass
class AssetReport:
    path: str
    asset_type: str        # "sprite" | "tileset" | "imagem" | "desconhecido"
    scenario: str          # "ok" | "precisa_conversao" | "inadequado" | "ausente"
    mode: str = ""         # modo PIL: RGBA, RGB, P, etc.
    width: int = 0
    height: int = 0
    color_count: int = 0
    has_transparency: bool = False
    ownership: str = "unknown"
    issues: list = field(default_factory=list)
    res_suggestion: str = ""


@dataclass
class ProjectDiagnostic:
    project_path: str
    scenario_detected: str   # "1_data_exists" | "2_res_inadequate" | "3_no_art" | "4_lab_nested_art_review"
    summary: str = ""
    total_assets: int = 0
    ok: int = 0
    needs_conversion: int = 0
    inadequate: int = 0
    absent: int = 0
    assets: list = field(default_factory=list)
    source_asset_status: dict = field(default_factory=dict)
    active_res_asset_status: dict = field(default_factory=dict)
    build_blocking_issues: list = field(default_factory=list)
    discovered_artifacts: int = 0
    art_inventory: dict = field(default_factory=dict)
    nested_projects: list = field(default_factory=list)
    discovery_policy: dict = field(default_factory=dict)
    discovery_warnings: list = field(default_factory=list)
    recommended_actions: list = field(default_factory=list)
    conversion_commands: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Analise de imagem individual
# ---------------------------------------------------------------------------
def _is_multiple_of_8(n: int) -> bool:
    return n % 8 == 0


def _image_pixel_data(img: Image.Image):
    """Usa a API Pillow atual, com fallback para releases anteriores."""
    flattened = getattr(img, "get_flattened_data", None)
    if callable(flattened):
        return flattened()
    return img.getdata()


def _count_unique_colors(img: Image.Image) -> int:
    """Conta cores unicas visiveis (excluindo index 0 se indexada)."""
    if img.mode == "P":
        indexed = _image_pixel_data(img)
        unique = set(indexed)
        # Remove index 0 (transparente por convencao)
        unique.discard(0)
        return len(unique)
    elif img.mode == "RGBA":
        pixels = set()
        for px in _image_pixel_data(img):
            if px[3] > 0:
                pixels.add(px[:3])
        return len(pixels)
    else:
        return len(set(_image_pixel_data(img)))


def _colors_within_9bit_grid(img: Image.Image) -> list[tuple]:
    """Retorna lista de cores fora do grid 9-bits (0x00, 0x22, ..., 0xEE por canal)."""
    if img.mode == "P":
        palette = img.getpalette()
        if not palette:
            return []
        bad = []
        n_colors = len(palette) // 3
        for i in range(1, min(n_colors, 16)):  # ignora index 0
            r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
            if r not in VALID_9BIT_VALUES or g not in VALID_9BIT_VALUES or b not in VALID_9BIT_VALUES:
                bad.append((r, g, b))
        return bad
    return []  # nao indexada = nao analisavel sem conversao


def _has_transparent_index_0(img: Image.Image) -> bool:
    """Verifica se a imagem indexada tem index 0 como transparente."""
    if img.mode != "P":
        return False
    palette = img.getpalette()
    if not palette:
        return False
    r, g, b = palette[0], palette[1], palette[2]
    return (r, g, b) == MAGENTA_TRANSPARENT


def _guess_asset_type(path: Path, w: int, h: int) -> str:
    """Heuristica simples para determinar o tipo de asset."""
    name = path.stem.lower()
    if any(k in name for k in ["sprite", "player", "enemy", "boss", "char", "hero", "npc"]):
        return "sprite"
    if any(k in name for k in ["tile", "map", "bg", "background", "tileset", "level"]):
        return "tileset"
    if w <= 64 and h <= 64:
        return "sprite"
    if w >= 128 or h >= 128:
        return "tileset"
    return "imagem"


def analyze_image(path: Path) -> AssetReport:
    """Analisa um asset PNG e retorna o relatorio de issues."""
    report = AssetReport(
        path=str(path),
        asset_type="desconhecido",
        scenario="ok",
    )

    if not path.exists():
        report.scenario = "ausente"
        report.issues.append(asdict(AssetIssue(
            code="FILE_NOT_FOUND",
            severity="critico",
            message=f"Arquivo nao encontrado: {path}",
            suggestion="Verifique o caminho ou crie o asset."
        )))
        return report

    try:
        with Image.open(path) as img:
            report.mode = img.mode
            report.width, report.height = img.size
            w, h = report.width, report.height
    except Exception as e:
        report.scenario = "inadequado"
        report.issues.append(asdict(AssetIssue(
            code="OPEN_FAILED",
            severity="critico",
            message=f"Nao foi possivel abrir: {e}",
            suggestion="O arquivo pode estar corrompido ou em formato nao suportado."
        )))
        return report

    report.asset_type = _guess_asset_type(path, w, h)

    with Image.open(path) as img:
        # ── Modo (nao indexado = precisa conversao) ─────────────────────────
        if img.mode not in ("P",):
            report.issues.append(asdict(AssetIssue(
                code="NOT_INDEXED",
                severity="critico",
                message=f"Modo {img.mode} - nao e PNG indexado (modo P).",
                suggestion="Indexar para PNG modo P com PLTE <= 16 e index 0 por papel declarado. Rota: forge-art convert (technical_conversion). Fonte high-res de personagem/cenario de identidade exige assisted_native_translation, nao conversao automatica."
            )))
            report.scenario = "precisa_conversao"

        # -- Dimensoes - multiplos de 8 --
        if not _is_multiple_of_8(w) or not _is_multiple_of_8(h):
            report.issues.append(asdict(AssetIssue(
                code="DIM_NOT_MULTIPLE_8",
                severity="critico",
                message=f"Dimensoes {w}x{h} nao sao multiplas de 8.",
                suggestion=f"Redimensionar para {((w+7)//8)*8}x{((h+7)//8)*8} px."
            )))
            if report.scenario == "ok":
                report.scenario = "inadequado"

        # A largura total de um strip nao e o tamanho de uma entrada VDP.
        # Sem o contrato de celula do .res, o diagnostico nao infere metasprite.
        if report.asset_type == "sprite" and (w > 32 or h > 32):
            report.issues.append(asdict(AssetIssue(
                code="SPRITE_TOO_LARGE",
                severity="info",
                message=(
                    f"Imagem candidata a sprite mede {w}x{h}px; o tamanho total "
                    "pode representar strip/sheet e nao uma celula."
                ),
                suggestion=(
                    "Validar cada frame no contrato .res e no "
                    "sprite_artifact_report.v2; nao usar a largura total do "
                    "strip como limite de uma entrada VDP."
                )
            )))

        # ── Numero de cores ───────────────────────────────────────────────
        try:
            color_count = _count_unique_colors(img)
            report.color_count = color_count
            if color_count > MAX_PALETTE_COLORS:
                report.issues.append(asdict(AssetIssue(
                    code="TOO_MANY_COLORS",
                    severity="critico",
                    message=f"{color_count} cores visiveis - limite e 15 (index 0 reservado).",
                    suggestion="Recurar a paleta para 15 cores visiveis por material, nao por frequencia estatistica. Snap pela biblioteca canonica: python3 tools/sgdk_wrapper/forge_art/vdp_color.py --convert R,G,B"
                )))
                if report.scenario == "ok":
                    report.scenario = "inadequado"
        except Exception:
            pass

        # ── Grid 9-bits ───────────────────────────────────────────────────
        if img.mode == "P":
            bad_colors = _colors_within_9bit_grid(img)
            if bad_colors:
                report.issues.append(asdict(AssetIssue(
                    code="COLORS_NOT_9BIT",
                    severity="aviso",
                    message=f"{len(bad_colors)} cor(es) fora do grid 9-bits Mega Drive (multiplos de 0x22).",
                    suggestion="O VDP trunca bits menos significativos. Ajustar paleta manualmente ou aceitar o arredondamento automatico do SGDK."
                )))

        # ── Transparencia ─────────────────────────────────────────────────
        if img.mode == "P":
            report.has_transparency = "transparency" in img.info
            if not _has_transparent_index_0(img):
                report.issues.append(asdict(AssetIssue(
                    code="NO_MAGENTA_TRANSPARENT",
                    severity="aviso",
                    message="Index 0 da paleta nao e magenta (#FF00FF) - convencao de transparencia SGDK.",
                    suggestion="Definir index 0 como #FF00FF ou garantir que index 0 seja a cor transparente no .res."
                )))
        elif img.mode == "RGBA":
            report.has_transparency = True
            report.issues.append(asdict(AssetIssue(
                code="RGBA_NOT_INDEXED",
                severity="critico",
                message="Imagem RGBA nao e indexada. Alpha sera perdido sem conversao correta.",
                suggestion="Declarar o papel do index 0 (transparent0 ou unused0) ANTES de escolher a paleta. Nunca compor sobre preto/branco para resolver transparencia. Medir com: python3 tools/sgdk_wrapper/forge_art/pixel_contract.py --validate <png> --index0-role transparent0"
            )))
            if report.scenario == "ok":
                report.scenario = "precisa_conversao"

    # ── Sugestao de entrada .res ──────────────────────────────────────────
    if report.asset_type == "sprite" and _is_multiple_of_8(w) and _is_multiple_of_8(h):
        w_tiles = w // 8
        h_tiles = h // 8
        stem = path.stem.lower().replace(" ", "_")
        report.res_suggestion = f'SPRITE {stem} "sprite/{path.name}" {w_tiles} {h_tiles} FAST 5'

    if not report.issues:
        report.scenario = "ok"

    return report


# ---------------------------------------------------------------------------
# Leitura de .res para identificar assets referenciados
# ---------------------------------------------------------------------------
def parse_res_file(res_path: Path) -> list[str]:
    """Extrai caminhos de imagem de um arquivo .res do SGDK."""
    paths = []
    if not res_path.exists():
        return paths
    for line in res_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith(("#", "//")):
            continue
        parts = line.split()
        for part in parts:
            if part.startswith('"') and part.endswith('"'):
                p = part.strip('"')
                if p.lower().endswith(".png"):
                    paths.append(p)
    return paths


# ---------------------------------------------------------------------------
# Discovery seguro de projetos laboratoriais
# ---------------------------------------------------------------------------
def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _safe_project_files(project_path: Path) -> tuple[list[Path], list[dict]]:
    """Coleta arquivos sem seguir symlinks nem sair do root do projeto."""
    project_root = project_path.resolve()
    files: list[Path] = []
    warnings: list[dict] = []

    for current, dirnames, filenames in os.walk(project_root, topdown=True, followlinks=False):
        current_path = Path(current)
        safe_dirs = []
        for dirname in sorted(dirnames):
            candidate = current_path / dirname
            if candidate.is_symlink():
                warnings.append({
                    "code": "SYMLINK_DIRECTORY_SKIPPED",
                    "path": candidate.relative_to(project_root).as_posix(),
                    "target_within_project": _is_within(candidate, project_root),
                    "message": "Diretorio symlink ignorado; discovery nunca segue diretorios externos.",
                })
                continue
            if not _is_within(candidate, project_root):
                warnings.append({
                    "code": "OUTSIDE_PROJECT_DIRECTORY_SKIPPED",
                    "path": str(candidate),
                    "target_within_project": False,
                    "message": "Diretorio fora do root do projeto ignorado.",
                })
                continue
            safe_dirs.append(dirname)
        dirnames[:] = safe_dirs

        for filename in sorted(filenames):
            candidate = current_path / filename
            if candidate.is_symlink():
                warnings.append({
                    "code": "SYMLINK_FILE_SKIPPED",
                    "path": candidate.relative_to(project_root).as_posix(),
                    "target_within_project": _is_within(candidate, project_root),
                    "message": "Arquivo symlink ignorado pelo discovery.",
                })
                continue
            if candidate.is_file() and _is_within(candidate, project_root):
                files.append(candidate)

    return files, warnings


def _is_historical_or_staging(rel: Path) -> bool:
    lowered = [part.lower() for part in rel.parts]
    if "staging" in lowered:
        return True
    return any(marker in part for part in lowered for marker in HISTORICAL_PATH_MARKERS)


def _inventory_entry(paths: list[str], include_history: bool) -> dict:
    unique = sorted(set(paths))
    visible = unique if include_history else unique[:INVENTORY_PATH_PREVIEW_LIMIT]
    return {
        "count": len(unique),
        "paths": visible,
        "paths_omitted": len(unique) - len(visible),
    }


def _build_art_inventory(
    project_path: Path, files: list[Path], include_history: bool
) -> tuple[dict, list[dict]]:
    """Separa arte-fonte, evidencias, trabalho e recursos ativos."""
    root = project_path.resolve()
    buckets: dict[str, list[str]] = {
        "source_art": [],
        "evidence_art": [],
        "active_res_art": [],
        "lab_work_art": [],
        "analysis_art": [],
        "staging_art": [],
        "historical_art": [],
        "generated_artifacts": [],
    }

    relative_files: list[tuple[Path, Path]] = []
    for path in files:
        rel = path.relative_to(root)
        relative_files.append((path, rel))
        parts = rel.parts
        lowered = tuple(part.lower() for part in parts)
        suffix = path.suffix.lower()
        rel_text = rel.as_posix()

        if suffix in SOURCE_ART_EXTENSIONS and "staging" in lowered:
            buckets["staging_art"].append(rel_text)
        elif suffix in SOURCE_ART_EXTENSIONS and _is_historical_or_staging(rel):
            buckets["historical_art"].append(rel_text)
        elif suffix in VISUAL_EXTENSIONS and "res" in lowered:
            buckets["active_res_art"].append(rel_text)
        elif suffix in VISUAL_EXTENSIONS and (
            "evidence" in lowered or (len(lowered) > 1 and lowered[:2] == ("out", "evidence"))
        ):
            buckets["evidence_art"].append(rel_text)
        elif suffix in SOURCE_ART_EXTENSIONS and (
            "data" in lowered or
            (len(lowered) > 1 and lowered[0] == "rascunho" and lowered[1] in {"inputs", "entrada_bruta"})
        ):
            buckets["source_art"].append(rel_text)
        elif suffix in VISUAL_EXTENSIONS and lowered and lowered[0] == "analysis":
            buckets["analysis_art"].append(rel_text)
        elif suffix in VISUAL_EXTENSIONS and lowered and lowered[0] == "work":
            buckets["lab_work_art"].append(rel_text)

        if suffix in GENERATED_ARTIFACT_EXTENSIONS and lowered and lowered[0] == "work":
            buckets["generated_artifacts"].append(rel_text)

    nested_roots: set[Path] = set()
    for path, rel in relative_files:
        if path.suffix.lower() != ".res" or "res" not in tuple(p.lower() for p in rel.parts):
            continue
        lowered = [part.lower() for part in rel.parts]
        res_index = lowered.index("res")
        if res_index == 0:
            continue
        candidate = root.joinpath(*rel.parts[:res_index])
        if (candidate / "src" / "main.c").is_file():
            nested_roots.add(candidate)

    nested_projects = []
    for nested_root in sorted(nested_roots):
        rel_root = nested_root.relative_to(root).as_posix()
        prefix = rel_root + "/"
        nested_projects.append({
            "path": rel_root,
            "hygiene_manifest": {
                "path": f"{rel_root}/doc/project_hygiene_manifest.json",
                "present": (nested_root / "doc" / "project_hygiene_manifest.json").is_file(),
            },
            "source_art_count": sum(1 for p in buckets["source_art"] if p.startswith(prefix)),
            "active_res_art_count": sum(1 for p in buckets["active_res_art"] if p.startswith(prefix)),
        })

    inventory = {
        name: _inventory_entry(paths, include_history)
        for name, paths in buckets.items()
    }
    return inventory, nested_projects


# ---------------------------------------------------------------------------
# Diagnostico de projeto
# ---------------------------------------------------------------------------
def diagnose_project(
    project_path: Path,
    res_file: Optional[str] = None,
    include_history: bool = False,
) -> ProjectDiagnostic:
    diag = ProjectDiagnostic(project_path=str(project_path), scenario_detected="")

    data_dir = project_path / "data"
    res_dir  = project_path / "res"

    project_files, discovery_warnings = _safe_project_files(project_path)
    diag.art_inventory, diag.nested_projects = _build_art_inventory(
        project_path, project_files, include_history
    )
    diag.discovery_warnings = discovery_warnings
    hygiene_manifest = project_path / "doc" / "project_hygiene_manifest.json"
    diag.discovery_policy = {
        "scope": "project_root_only",
        "follow_symlinks": False,
        "external_directories_followed": False,
        "mode": "full_history" if include_history else "active_only",
        "inventory_path_preview_limit": None if include_history else INVENTORY_PATH_PREVIEW_LIMIT,
        "hygiene_manifest": {
            "path": "doc/project_hygiene_manifest.json",
            "present": hygiene_manifest.is_file(),
        },
    }
    diag.discovered_artifacts = sum(
        diag.art_inventory[name]["count"]
        for name in ("source_art", "evidence_art", "active_res_art", "lab_work_art", "analysis_art")
    )

    root = project_path.resolve()
    data_pngs = [
        path for path in project_files
        if path.suffix.lower() == ".png"
        and path.relative_to(root).parts
        and path.relative_to(root).parts[0].lower() == "data"
        and (include_history or not _is_historical_or_staging(path.relative_to(root)))
    ]
    top_res_pngs = [
        path for path in project_files
        if path.suffix.lower() == ".png"
        and path.relative_to(root).parts
        and path.relative_to(root).parts[0].lower() == "res"
    ]
    has_data = bool(data_pngs)
    has_res = res_dir.is_dir() and not res_dir.is_symlink()

    res_pngs: list[Path] = []
    if has_res:
        # Verificar .res files para encontrar sprites referenciados
        res_files = [
            path for path in project_files
            if path.suffix.lower() == ".res"
            and len(path.relative_to(root).parts) == 2
            and path.relative_to(root).parts[0].lower() == "res"
        ]
        if res_file:
            specific_res = project_path / res_file
            if specific_res.exists():
                res_files = [specific_res]
        for rf in res_files:
            for rel_path in parse_res_file(rf):
                abs_path = project_path / "res" / rel_path
                if not abs_path.exists():
                    abs_path = project_path / rel_path
                if abs_path.exists() and not abs_path.is_symlink() and _is_within(abs_path, root):
                    res_pngs.append(abs_path)

        if not res_pngs:
            res_pngs = top_res_pngs

    # Determinar cenario
    if has_data and has_res and res_pngs:
        diag.scenario_detected = "2_res_inadequate_check"
    elif has_data and not has_res:
        diag.scenario_detected = "1_data_needs_conversion"
    elif has_data and has_res:
        diag.scenario_detected = "1_data_and_res_check"
    elif not has_data and has_res and res_pngs:
        diag.scenario_detected = "2_res_exists_check"
    elif diag.discovered_artifacts > 0 or diag.nested_projects:
        diag.scenario_detected = "4_lab_nested_art_review"
    else:
        diag.scenario_detected = "3_no_art"

    # Analisar assets em /data
    data_reports = []
    if has_data:
        for png in sorted(data_pngs):
            r = analyze_image(png)
            r.ownership = "source_art"
            data_reports.append(r)

    # Analisar assets em /res
    res_reports = []
    for png in sorted(set(res_pngs)):
        r = analyze_image(png)
        r.ownership = "active_res_art"
        res_reports.append(r)

    all_reports = data_reports + res_reports
    diag.assets = [asdict(r) for r in all_reports]
    diag.total_assets = len(all_reports)
    diag.ok            = sum(1 for r in all_reports if r.scenario == "ok")
    diag.needs_conversion = sum(1 for r in all_reports if r.scenario == "precisa_conversao")
    diag.inadequate    = sum(1 for r in all_reports if r.scenario == "inadequado")
    diag.absent        = sum(1 for r in all_reports if r.scenario == "ausente")
    diag.source_asset_status = _summarize_asset_reports(data_reports)
    diag.active_res_asset_status = _summarize_asset_reports(res_reports)
    diag.build_blocking_issues = [
        {
            "path": report.path,
            "code": issue["code"],
            "message": issue["message"],
        }
        for report in res_reports
        for issue in report.issues
        if issue["severity"] == "critico"
    ]

    # Gerar sumario
    _build_summary(diag, project_path, data_dir, res_dir)

    return diag


def _summarize_asset_reports(reports: list[AssetReport]) -> dict:
    return {
        "total": len(reports),
        "ok": sum(1 for report in reports if report.scenario == "ok"),
        "needs_conversion": sum(
            1 for report in reports if report.scenario == "precisa_conversao"
        ),
        "inadequate": sum(
            1 for report in reports if report.scenario == "inadequado"
        ),
        "absent": sum(1 for report in reports if report.scenario == "ausente"),
        "critical_issues": sum(
            1
            for report in reports
            for issue in report.issues
            if issue["severity"] == "critico"
        ),
    }


def _build_summary(diag: ProjectDiagnostic, project_path: Path, data_dir: Path, res_dir: Path):
    s = diag.scenario_detected
    actions = []
    commands = []

    if s == "3_no_art":
        diag.summary = "Projeto sem nenhuma arte. Escolha: (A) gerar com IA + converter, ou (B) baixar assets da web + converter."
        actions += [
            "ROTA A: Gerar arte pixel art com IA (Claude Sonnet via API de imagem ou Stable Diffusion) e converter.",
            "ROTA A: Executar photo2sgdk.exe para converter imagens geradas para formato SGDK.",
            "ROTA B: Baixar sprite sheets de opengameart.org, itch.io (assets CC0/CC-BY).",
            "ROTA B: Baixar so com licenca auditavel; registrar em asset_provenance_manifest.json.",
            "Toda saida de maquina nasce technical_candidate; promocao para res/ exige decisao humana registrada.",
        ]
        commands += [
            "# Abrir photo2sgdk GUI:",
            r"call tools\photo2sgdk\run.bat",
            "# Medir conformidade de um PNG candidato (nao converte, nao escreve):",
            "python3 tools/sgdk_wrapper/forge_art/pixel_contract.py --validate <png> --index0-role transparent0",
        ]

    elif s == "4_lab_nested_art_review":
        inv = diag.art_inventory
        diag.summary = (
            "Projeto laboratorial com arte fora do layout SGDK convencional: "
            f"{inv['source_art']['count']} fonte(s), "
            f"{inv['evidence_art']['count']} evidencia(s), "
            f"{inv['active_res_art']['count']} recurso(s) ativo(s), "
            f"{inv['lab_work_art']['count']} artefato(s) de trabalho e "
            f"{len(diag.nested_projects)} subprojeto(s) SGDK."
        )
        actions += [
            "Tratar o root como estudo/laboratorio; nao iniciar rota de criacao de arte por ausencia.",
            "Revisar source_art e lab_work_art antes de promover qualquer asset para res/.",
            "Validar active_res_art no subprojeto SGDK que possui ownership do runtime.",
            "Manter evidence_art separada de fonte e de recursos ativos; captura nao e asset de producao.",
            "Preservar o confinamento ao root e nao seguir symlinks ou diretorios externos.",
        ]
        commands += [
            "# Executar o diagnostico no viewer SGDK aninhado indicado em nested_projects:",
            "python tools/sgdk_wrapper/art_diagnostic.py --project <nested_project_path>",
            "# Validar recursos no contexto do subprojeto owner do runtime:",
            "powershell -File tools/sgdk_wrapper/validate_resources.ps1 -ProjectPath <nested_project_path>",
        ]

    elif "1_data" in s:
        criticos = sum(
            1 for a in diag.assets
            if any(i["severity"] == "critico" for i in a["issues"])
        )
        diag.summary = (
            f"Projeto tem {len(diag.assets)} asset(s) em /data para converter. "
            f"{criticos} com issues criticos. "
            f"{diag.ok} ja adequados."
        )
        actions += [
            "Revisar issues criticos (NOT_INDEXED, DIM_NOT_MULTIPLE_8, TOO_MANY_COLORS) - bloqueantes.",
            "Classificar cada fonte: pixel nativo (technical_conversion) ou high-res de identidade (assisted_native_translation).",
            "Fonte ja indexada: normalizar PLTE/index 0 com normalize_indexed_sgdk_png.py.",
            "Validar com validate_resources.ps1 antes do build.",
            "Copiar assets validados para res/ e atualizar .res files.",
        ]
        data_path_str = str(data_dir).replace("\\", "/")
        commands += [
            "# Normalizar PNG JA indexado (PLTE inflada / papel do index 0):",
            "python3 tools/image-tools/normalize_indexed_sgdk_png.py transparent0 <arquivo.png>",
            "# Medir conformidade pixel-strict de um candidato:",
            "python3 tools/sgdk_wrapper/forge_art/pixel_contract.py --validate <png> --index0-role transparent0",
        ]

    elif "2_res" in s:
        active = diag.active_res_asset_status
        source = diag.source_asset_status
        criticos = active["critical_issues"]
        diag.summary = (
            f"Projeto tem {active['total']} asset(s) ativos referenciados em /res: "
            f"{active['ok']} ok, {active['needs_conversion']} precisam conversao, "
            f"{active['inadequate']} inadequados, {active['absent']} ausentes. "
            f"Ha tambem {source['total']} asset(s) fonte em /data; issues de fonte "
            "roteiam conversao, mas nao bloqueiam o build enquanto nao forem "
            "referenciados pelo grafo .res."
        )
        if criticos > 0:
            actions += [
                f"ATENCAO: {criticos} asset(s) com issues criticos - build pode falhar.",
                "Apresentar este relatorio ao dono do projeto para decisao de rota.",
            ]
        if active["needs_conversion"] > 0:
            actions += [
                "Assets nao indexados: converter para PNG modo P (indexed) com max 16 cores.",
                "Declarar o papel do index 0 e reindexar; nunca compor sobre preto para resolver alpha.",
            ]
        if active["inadequate"] > 0:
            actions += [
                "Assets inadequados: verificar dimensoes (multiplos de 8) e contagem de cores.",
                "Ajustar dimensoes por padding/crop declarado preservando pivot. Resize interpolado e blocker (non_nearest_downscale).",
            ]
        commands += [
            "# Medir conformidade pixel-strict dos assets ativos:",
            "python3 tools/sgdk_wrapper/forge_art/pixel_contract.py --validate <png> --index0-role transparent0",
            "# Validar recursos:",
            r"powershell -File tools\sgdk_wrapper\validate_resources.ps1",
            "# Auto-fix sprite.res:",
            r"powershell -File tools\sgdk_wrapper\autofix_sprite_res.ps1",
        ]

    diag.recommended_actions = actions
    diag.conversion_commands = commands


# ---------------------------------------------------------------------------
# Output formatado para console
# ---------------------------------------------------------------------------
def print_report(diag: ProjectDiagnostic, use_unicode: bool = False):
    SEV_ICONS_ASCII = {"critico": "ERR", "aviso": "WARN", "info": "INFO"}
    SEV_ICONS_UNICODE = {"critico": "X", "aviso": "!", "info": "i"}
    STATUS_ASCII = {"ok": "OK", "precisa_conversao": "CONVERT", "inadequado": "BAD", "ausente": "MISSING"}
    STATUS_UNICODE = {"ok": "OK", "precisa_conversao": "CONVERT", "inadequado": "BAD", "ausente": "MISSING"}
    sev_icons = SEV_ICONS_UNICODE if use_unicode else SEV_ICONS_ASCII
    status_icons = STATUS_UNICODE if use_unicode else STATUS_ASCII

    print("\n" + "="*70)
    print(f"  ART DIAGNOSTIC - {diag.project_path}")
    print("="*70)
    print(f"  Cenario detectado : {diag.scenario_detected}")
    print(f"  Resumo            : {diag.summary}")
    print(f"  Total assets      : {diag.total_assets}")
    print(f"  Arte descoberta   : {diag.discovered_artifacts}")
    print(f"  ok                : {diag.ok}")
    print(f"  precisa_conversao : {diag.needs_conversion}")
    print(f"  inadequado        : {diag.inadequate}")
    print(f"  ausente           : {diag.absent}")
    print(f"  fonte /data       : {diag.source_asset_status.get('total', 0)}")
    print(f"  ativo /res        : {diag.active_res_asset_status.get('total', 0)}")
    print(f"  blockers de build : {len(diag.build_blocking_issues)}")

    if diag.art_inventory:
        print("\n" + "-"*70)
        print("  INVENTARIO POR OWNERSHIP")
        print("-"*70)
        for name, entry in diag.art_inventory.items():
            print(f"  {name:<22}: {entry['count']}")
        print(f"  nested_projects       : {len(diag.nested_projects)}")

    if diag.assets:
        print("\n" + "-"*70)
        print("  ASSETS")
        print("-"*70)
        for a in diag.assets:
            status_icon = status_icons.get(a["scenario"], "?")
            rel = Path(a["path"]).name
            mode_info = f"{a['mode']} {a['width']}x{a['height']}px" if a["width"] else ""
            colors_info = f"{a['color_count']}cores" if a["color_count"] else ""
            print(f"\n  {status_icon} {rel}  [{a['asset_type']}]  {mode_info}  {colors_info}")
            for issue in a["issues"]:
                icon = sev_icons.get(issue["severity"], "*")
                print(f"       {icon} [{issue['code']}] {issue['message']}")
                if issue["suggestion"]:
                    print(f"          -> {issue['suggestion']}")
            if a.get("res_suggestion"):
                print(f"       RES_SUGGESTION: {a['res_suggestion']}")

    if diag.recommended_actions:
        print("\n" + "-"*70)
        print("  ACOES RECOMENDADAS")
        print("-"*70)
        for i, action in enumerate(diag.recommended_actions, 1):
            print(f"  {i}. {action}")

    if diag.conversion_commands:
        print("\n" + "-"*70)
        print("  COMANDOS DE CONVERSAO")
        print("-"*70)
        for cmd in diag.conversion_commands:
            print(f"  {cmd}")

    print("\n" + "="*70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnostica assets visuais de um projeto SGDK para Mega Drive."
    )
    parser.add_argument(
        "--project", required=True,
        help="Caminho raiz do projeto SGDK (deve conter /data e/ou /res)."
    )
    parser.add_argument(
        "--output", default=None,
        help="Salvar relatorio JSON neste arquivo (opcional)."
    )
    parser.add_argument(
        "--res-file", default=None,
        help="Arquivo .res especifico para inspecionar (ex: res/sprite.res)."
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Imprimir apenas o JSON do relatorio (sem formatacao)."
    )
    parser.add_argument(
        "--unicode", action="store_true",
        help="Habilitar simbolos unicode na saida formatada."
    )
    parser.add_argument(
        "--include-history", action="store_true",
        help="Inclui archive/staging/rejeitados e listas completas; use somente em auditoria historica.",
    )
    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    if not project_path.is_dir():
        print(f"[ERRO] Diretorio nao encontrado: {project_path}", file=sys.stderr)
        return 1

    diag = diagnose_project(
        project_path,
        res_file=args.res_file,
        include_history=args.include_history,
    )

    if args.json_only:
        print(json.dumps(asdict(diag), indent=2, ensure_ascii=True))
    else:
        print_report(diag, use_unicode=args.unicode)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(asdict(diag), f, indent=2, ensure_ascii=True)
        print(f"\n[INFO] Relatorio salvo em: {out_path}")

    # Arte fonte nao referenciada nao bloqueia um grafo .res ativo e valido.
    if diag.scenario_detected == "3_no_art":
        return 2
    active = diag.active_res_asset_status
    if active.get("total", 0) > 0:
        if (
            active["needs_conversion"] > 0
            or active["inadequate"] > 0
            or active["absent"] > 0
        ):
            return 1
        return 0
    source = diag.source_asset_status
    if (
        source.get("needs_conversion", 0) > 0
        or source.get("inadequate", 0) > 0
        or source.get("absent", 0) > 0
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

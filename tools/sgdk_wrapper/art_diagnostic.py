#!/usr/bin/env python3
"""
art_diagnostic.py — Diagnostico de assets visuais para projetos SGDK / Mega Drive

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
    issues: list = field(default_factory=list)
    res_suggestion: str = ""


@dataclass
class ProjectDiagnostic:
    project_path: str
    scenario_detected: str   # "1_data_exists" | "2_res_inadequate" | "3_no_art"
    summary: str = ""
    total_assets: int = 0
    ok: int = 0
    needs_conversion: int = 0
    inadequate: int = 0
    absent: int = 0
    assets: list = field(default_factory=list)
    recommended_actions: list = field(default_factory=list)
    conversion_commands: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Analise de imagem individual
# ---------------------------------------------------------------------------
def _is_multiple_of_8(n: int) -> bool:
    return n % 8 == 0


def _count_unique_colors(img: Image.Image) -> int:
    """Conta cores unicas visiveis (excluindo index 0 se indexada)."""
    if img.mode == "P":
        indexed = img.getdata()
        unique = set(indexed)
        # Remove index 0 (transparente por convencao)
        unique.discard(0)
        return len(unique)
    elif img.mode == "RGBA":
        pixels = set()
        for px in img.getdata():
            if px[3] > 0:
                pixels.add(px[:3])
        return len(pixels)
    else:
        return len(set(img.getdata()))


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
                message=f"Modo {img.mode} — nao e PNG indexado (modo P).",
                suggestion="Converter para PNG indexado 4-bit com max 16 cores usando photo2sgdk ou batch_resize_index.py."
            )))
            report.scenario = "precisa_conversao"

        # ── Dimensoes — multiplos de 8 ────────────────────────────────────
        if not _is_multiple_of_8(w) or not _is_multiple_of_8(h):
            report.issues.append(asdict(AssetIssue(
                code="DIM_NOT_MULTIPLE_8",
                severity="critico",
                message=f"Dimensoes {w}x{h} nao sao multiplas de 8.",
                suggestion=f"Redimensionar para {((w+7)//8)*8}x{((h+7)//8)*8} px."
            )))
            if report.scenario == "ok":
                report.scenario = "inadequado"

        # ── Tamanho de sprite excede 32x32 (sem metasprite) ──────────────
        if report.asset_type == "sprite" and (w > 32 or h > 32):
            report.issues.append(asdict(AssetIssue(
                code="SPRITE_TOO_LARGE",
                severity="aviso",
                message=f"Sprite {w}x{h} excede 32x32 px (limite hardware de 1 entrada).",
                suggestion="Usar metasprite (multiplas entradas na sprite table) ou dividir em tiles menores."
            )))

        # ── Numero de cores ───────────────────────────────────────────────
        try:
            color_count = _count_unique_colors(img)
            report.color_count = color_count
            if color_count > MAX_PALETTE_COLORS:
                report.issues.append(asdict(AssetIssue(
                    code="TOO_MANY_COLORS",
                    severity="critico",
                    message=f"{color_count} cores visiveis — limite e 15 (index 0 reservado).",
                    suggestion="Reduzir paleta para 15 cores. Usar quantizacao com photo2sgdk ou batch_resize_index.py."
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
                    message="Index 0 da paleta nao e magenta (#FF00FF) — convencao de transparencia SGDK.",
                    suggestion="Definir index 0 como #FF00FF ou garantir que index 0 seja a cor transparente no .res."
                )))
        elif img.mode == "RGBA":
            report.has_transparency = True
            report.issues.append(asdict(AssetIssue(
                code="RGBA_NOT_INDEXED",
                severity="critico",
                message="Imagem RGBA nao e indexada. Alpha sera perdido sem conversao correta.",
                suggestion="Converter com batch_resize_index.py --max-colors 15 preservando canal alpha como index 0."
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
# Diagnostico de projeto
# ---------------------------------------------------------------------------
def diagnose_project(project_path: Path, res_file: Optional[str] = None) -> ProjectDiagnostic:
    diag = ProjectDiagnostic(project_path=str(project_path), scenario_detected="")

    data_dir = project_path / "data"
    res_dir  = project_path / "res"

    has_data = data_dir.exists() and any(data_dir.rglob("*.png"))
    has_res  = res_dir.exists()

    res_pngs: list[Path] = []
    if has_res:
        # Verificar .res files para encontrar sprites referenciados
        res_files = list(res_dir.glob("*.res"))
        if res_file:
            specific_res = project_path / res_file
            if specific_res.exists():
                res_files = [specific_res]
        for rf in res_files:
            for rel_path in parse_res_file(rf):
                abs_path = project_path / "res" / rel_path
                if not abs_path.exists():
                    abs_path = project_path / rel_path
                if abs_path.exists():
                    res_pngs.append(abs_path)

        if not res_pngs:
            res_pngs = list(res_dir.rglob("*.png"))

    # Determinar cenario
    if has_data and has_res and res_pngs:
        diag.scenario_detected = "2_res_inadequate_check"
    elif has_data and not has_res:
        diag.scenario_detected = "1_data_needs_conversion"
    elif has_data and has_res:
        diag.scenario_detected = "1_data_and_res_check"
    elif not has_data and has_res and res_pngs:
        diag.scenario_detected = "2_res_exists_check"
    else:
        diag.scenario_detected = "3_no_art"

    # Analisar assets em /data
    data_reports = []
    if has_data:
        for png in sorted(data_dir.rglob("*.png")):
            r = analyze_image(png)
            data_reports.append(r)

    # Analisar assets em /res
    res_reports = []
    for png in sorted(set(res_pngs)):
        r = analyze_image(png)
        res_reports.append(r)

    all_reports = data_reports + res_reports
    diag.assets = [asdict(r) for r in all_reports]
    diag.total_assets = len(all_reports)
    diag.ok            = sum(1 for r in all_reports if r.scenario == "ok")
    diag.needs_conversion = sum(1 for r in all_reports if r.scenario == "precisa_conversao")
    diag.inadequate    = sum(1 for r in all_reports if r.scenario == "inadequado")
    diag.absent        = sum(1 for r in all_reports if r.scenario == "ausente")

    # Gerar sumario
    _build_summary(diag, project_path, data_dir, res_dir)

    return diag


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
            "ROTA B: Converter assets baixados com batch_resize_index.py.",
            "Criar spec JSON em tools/image-tools/specs/ para automatizar o pipeline.",
        ]
        commands += [
            "# Abrir photo2sgdk GUI:",
            r"call tools\photo2sgdk\run.bat",
            "# OU converter via linha de comando (apos gerar/baixar assets em data/):",
            f"python tools/image-tools/batch_resize_index.py --spec tools/image-tools/specs/{project_path.name}_spec.json --batch-root {project_path / 'data'}",
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
            "Revisar issues criticos (NOT_INDEXED, DIM_NOT_MULTIPLE_8, TOO_MANY_COLORS) — bloqueantes.",
            "Criar spec JSON para batch_resize_index.py com dimensoes e nomes corretos.",
            "Executar conversao em lote.",
            "Validar com validate_resources.ps1 antes do build.",
            "Copiar assets validados para res/ e atualizar .res files.",
        ]
        data_path_str = str(data_dir).replace("\\", "/")
        commands += [
            "# Corrigir transparencia em todos os PNGs de /data:",
            f"python tools/image-tools/fix_png_transparency_final.py {data_dir}",
            "# Converter lote (criar spec antes em tools/image-tools/specs/):",
            f"python tools/image-tools/batch_resize_index.py --spec tools/image-tools/specs/<spec>.json --batch-root {data_dir}",
            "# OU usar interface grafica:",
            r"call tools\photo2sgdk\run.bat",
        ]

    elif "2_res" in s:
        criticos = sum(
            1 for a in diag.assets
            if any(i["severity"] == "critico" for i in a["issues"])
        )
        diag.summary = (
            f"Projeto tem {len(diag.assets)} asset(s) em /res. "
            f"{diag.ok} ok, {diag.needs_conversion} precisam conversao, "
            f"{diag.inadequate} inadequados, {diag.absent} ausentes."
        )
        if criticos > 0:
            actions += [
                f"ATENCAO: {criticos} asset(s) com issues criticos — build pode falhar.",
                "Apresentar este relatorio ao dono do projeto para decisao de rota.",
            ]
        if diag.needs_conversion > 0:
            actions += [
                "Assets nao indexados: converter para PNG modo P (indexed) com max 16 cores.",
                "Usar fix_png_transparency_final.py para corrigir transparencia.",
            ]
        if diag.inadequate > 0:
            actions += [
                "Assets inadequados: verificar dimensoes (multiplos de 8) e contagem de cores.",
                "Redimensionar com batch_resize_index.py ou photo2sgdk.",
            ]
        commands += [
            "# Corrigir transparencia automaticamente:",
            f"python tools/image-tools/fix_png_transparency_final.py {res_dir}",
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
def print_report(diag: ProjectDiagnostic):
    SEV_ICONS = {"critico": "❌", "aviso": "⚠️ ", "info": "ℹ️ "}

    print("\n" + "="*70)
    print(f"  ART DIAGNOSTIC — {diag.project_path}")
    print("="*70)
    print(f"  Cenario detectado : {diag.scenario_detected}")
    print(f"  Resumo            : {diag.summary}")
    print(f"  Total assets      : {diag.total_assets}")
    print(f"  ok                : {diag.ok}")
    print(f"  precisa_conversao : {diag.needs_conversion}")
    print(f"  inadequado        : {diag.inadequate}")
    print(f"  ausente           : {diag.absent}")

    if diag.assets:
        print("\n" + "-"*70)
        print("  ASSETS")
        print("-"*70)
        for a in diag.assets:
            status_icon = {"ok": "✅", "precisa_conversao": "🔄", "inadequado": "❌", "ausente": "👻"}.get(a["scenario"], "?")
            rel = Path(a["path"]).name
            mode_info = f"{a['mode']} {a['width']}x{a['height']}px" if a["width"] else ""
            colors_info = f"{a['color_count']}cores" if a["color_count"] else ""
            print(f"\n  {status_icon} {rel}  [{a['asset_type']}]  {mode_info}  {colors_info}")
            for issue in a["issues"]:
                icon = SEV_ICONS.get(issue["severity"], "•")
                print(f"       {icon} [{issue['code']}] {issue['message']}")
                if issue["suggestion"]:
                    print(f"          → {issue['suggestion']}")
            if a.get("res_suggestion"):
                print(f"       📋 .res sugerido: {a['res_suggestion']}")

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
    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    if not project_path.is_dir():
        print(f"[ERRO] Diretorio nao encontrado: {project_path}", file=sys.stderr)
        return 1

    diag = diagnose_project(project_path, res_file=args.res_file)

    if args.json_only:
        print(json.dumps(asdict(diag), indent=2, ensure_ascii=False))
    else:
        print_report(diag)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(asdict(diag), f, indent=2, ensure_ascii=False)
        print(f"\n[INFO] Relatorio salvo em: {out_path}")

    # Exit code: 0 = tudo ok, 1 = issues criticos, 2 = nenhuma arte
    if diag.scenario_detected == "3_no_art":
        return 2
    if diag.needs_conversion > 0 or diag.inadequate > 0 or diag.absent > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

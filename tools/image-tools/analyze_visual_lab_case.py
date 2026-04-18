#!/usr/bin/env python3
"""
analyze_visual_lab_case.py - Agregador do BENCHMARK_VISUAL_LAB.

Compoe o caso side-by-side em duas lanes (basic e elite), normaliza
transparencia por indice 0 para simular o comportamento do VDP e usa o
juiz estetico existente para produzir um score comparativo real.

Uso:
  python analyze_visual_lab_case.py --manifest <json> --output <json>
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
AESTHETIC_ANALYZER = SCRIPT_DIR / "analyze_aesthetic.py"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def find_project_root(manifest_path: Path) -> Path:
    for parent in [manifest_path.parent] + list(manifest_path.parents):
        if (parent / "res").is_dir() and (parent / "src").is_dir():
            return parent
    raise FileNotFoundError(f"Nao foi possivel resolver a raiz do projeto para {manifest_path}")


def resolve_asset(project_root: Path, asset_path: str) -> Path:
    resolved = (project_root / asset_path).resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Asset nao encontrado: {resolved}")
    return resolved


def indexed_zero_to_transparent(source: Path, destination: Path) -> Path:
    image = Image.open(source)

    if image.mode != "P":
        rgba = image.convert("RGBA")
        destination.parent.mkdir(parents=True, exist_ok=True)
        rgba.save(destination)
        return destination

    rgba = image.convert("RGBA")
    index_pixels = image.load()
    rgba_pixels = rgba.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b, _ = rgba_pixels[x, y]
            alpha = 0 if index_pixels[x, y] == 0 else 255
            rgba_pixels[x, y] = (r, g, b, alpha)

    destination.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(destination)
    return destination


def compose_pair(bg_b_path: Path, bg_a_path: Path, destination: Path) -> Path:
    bg_b = Image.open(bg_b_path).convert("RGBA")
    bg_a = Image.open(bg_a_path).convert("RGBA")

    if bg_b.size != bg_a.size:
        bg_a = bg_a.resize(bg_b.size, Image.Resampling.NEAREST)

    paired = Image.alpha_composite(bg_b, bg_a)
    destination.parent.mkdir(parents=True, exist_ok=True)
    paired.save(destination)
    return destination


def run_aesthetic_analysis(
    asset_path: Path,
    role: str,
    reference_profile: str,
    output_path: Path,
    paired_bg: Path | None,
    critical_visual: bool
) -> dict[str, Any]:
    args = [
        sys.executable,
        str(AESTHETIC_ANALYZER),
        "--asset",
        str(asset_path),
        "--role",
        role,
        "--reference-profile",
        reference_profile,
        "--output",
        str(output_path),
    ]

    if paired_bg is not None:
        args.extend(["--paired-bg", str(paired_bg)])
    if critical_visual:
        args.append("--critical-visual")

    completed = subprocess.run(args, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"analyze_aesthetic.py falhou para {asset_path}: {stderr}")

    return load_json(output_path)


def lane_status(analyses: list[dict[str, Any]]) -> str:
    statuses = {analysis["status"] for analysis in analyses}
    if "rework" in statuses:
        return "rework"
    if "needs_review" in statuses:
        return "needs_review"
    return "elite_ready"


def weighted_lane_score(analyses: dict[str, dict[str, Any]], weights: dict[str, float]) -> float:
    total = 0.0
    for role, weight in weights.items():
        total += analyses[role]["metrics"]["visual_excellence_score"] * weight
    return round(total, 4)


def build_evidence(project_root: Path) -> dict[str, Any]:
    captures_dir = project_root / "out" / "captures"
    evidence = {
        "captured": False,
        "captures_dir": str(captures_dir),
        "screenshot_path": None,
        "quicksave_path": None,
        "visual_vdp_dump_path": None,
        "save_sram_path": None,
        "quicksave_captured": False,
    }

    if not captures_dir.is_dir():
        return evidence

    screenshot = captures_dir / "benchmark_visual.png"
    dump_path = captures_dir / "visual_vdp_dump.bin"
    sram_path = captures_dir / "save.sram"

    quicksave_candidates = [
        item for item in captures_dir.glob("*")
        if item.is_file()
        and item.name not in {"benchmark_visual.png", "visual_vdp_dump.bin", "save.sram"}
    ]
    quicksave = max(quicksave_candidates, key=lambda item: item.stat().st_mtime) if quicksave_candidates else None

    evidence["screenshot_path"] = str(screenshot) if screenshot.is_file() else None
    evidence["quicksave_path"] = str(quicksave) if quicksave else None
    evidence["visual_vdp_dump_path"] = str(dump_path) if dump_path.is_file() else None
    evidence["save_sram_path"] = str(sram_path) if sram_path.is_file() else None
    evidence["quicksave_captured"] = bool(evidence["quicksave_path"])
    evidence["captured"] = all(
        [
            evidence["screenshot_path"],
            evidence["visual_vdp_dump_path"],
            evidence["save_sram_path"],
        ]
    )

    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="Agrega o BENCHMARK_VISUAL_LAB em lanes basic e elite.")
    parser.add_argument("--manifest", required=True, help="Manifesto JSON do caso do benchmark.")
    parser.add_argument("--output", required=True, help="JSON de saida.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        print(f"Erro: manifesto nao encontrado: {manifest_path}", file=sys.stderr)
        return 1

    if not AESTHETIC_ANALYZER.is_file():
        print(f"Erro: analyzer ausente: {AESTHETIC_ANALYZER}", file=sys.stderr)
        return 1

    manifest = load_json(manifest_path)
    project_root = find_project_root(manifest_path)
    output_path = Path(args.output).resolve()
    output_dir = output_path.parent
    work_dir = output_dir / "visual_lab_pairs"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    reference_profile = manifest.get("reference_profile", "generic-megadrive-elite")
    asset_weights = manifest.get("asset_weights", {"sprite": 0.45, "bg_a": 0.35, "bg_b": 0.2})
    lane_outputs: dict[str, Any] = {}
    flat_assets: list[dict[str, Any]] = []

    for lane_name, lane in manifest["lanes"].items():
        lane_dir = work_dir / lane_name
        lane_dir.mkdir(parents=True, exist_ok=True)

        critical_visual = bool(lane.get("critical_visual", False))
        lane_reference = lane.get("reference_profile", reference_profile)

        bg_b_original = resolve_asset(project_root, lane["bg_b"])
        bg_a_original = resolve_asset(project_root, lane["bg_a"])
        sprite_original = resolve_asset(project_root, lane["sprite"])

        bg_b_rgba = indexed_zero_to_transparent(bg_b_original, lane_dir / "bg_b_rgba.png")
        bg_a_rgba = indexed_zero_to_transparent(bg_a_original, lane_dir / "bg_a_rgba.png")
        sprite_rgba = indexed_zero_to_transparent(sprite_original, lane_dir / "sprite_rgba.png")
        paired_bg = compose_pair(bg_b_rgba, bg_a_rgba, lane_dir / "paired_bg.png")

        analyses = {
            "bg_b": run_aesthetic_analysis(
                asset_path=bg_b_rgba,
                role="bg_b",
                reference_profile=lane_reference,
                output_path=lane_dir / "bg_b_analysis.json",
                paired_bg=bg_a_rgba,
                critical_visual=critical_visual,
            ),
            "bg_a": run_aesthetic_analysis(
                asset_path=bg_a_rgba,
                role="bg_a",
                reference_profile=lane_reference,
                output_path=lane_dir / "bg_a_analysis.json",
                paired_bg=bg_b_rgba,
                critical_visual=critical_visual,
            ),
            "sprite": run_aesthetic_analysis(
                asset_path=sprite_rgba,
                role="sprite",
                reference_profile=lane_reference,
                output_path=lane_dir / "sprite_analysis.json",
                paired_bg=paired_bg,
                critical_visual=critical_visual,
            ),
        }

        score = weighted_lane_score(analyses, asset_weights)
        status = lane_status(list(analyses.values()))
        lane_outputs[lane_name] = {
            "label": lane.get("label", lane_name.upper()),
            "critical_visual": critical_visual,
            "reference_profile": lane_reference,
            "tags": lane.get("tags", []),
            "score": score,
            "status": status,
            "normalized_assets": {
                "bg_b": str(bg_b_rgba),
                "bg_a": str(bg_a_rgba),
                "sprite": str(sprite_rgba),
                "paired_bg": str(paired_bg),
            },
            "assets": analyses,
        }

        for role, analysis in analyses.items():
            analysis_copy = dict(analysis)
            analysis_copy["lane"] = lane_name
            analysis_copy["lane_label"] = lane_outputs[lane_name]["label"]
            analysis_copy["role"] = role
            flat_assets.append(analysis_copy)

    basic_score = lane_outputs["basic"]["score"]
    elite_score = lane_outputs["elite"]["score"]
    minimum_delta = float(manifest.get("minimum_delta", 0.0))
    delta = round(elite_score - basic_score, 4)
    passed_delta = elite_score > basic_score and delta >= minimum_delta

    elite_lane_status = lane_outputs["elite"]["status"]
    basic_lane_status = lane_outputs["basic"]["status"]
    if not passed_delta:
        benchmark_status = "delta_insufficient"
        report_status = "alerta_forte"
    elif elite_lane_status == "rework":
        benchmark_status = "elite_lane_rework"
        report_status = "reprovado"
    elif elite_lane_status == "needs_review":
        benchmark_status = "elite_lane_needs_review"
        report_status = "alerta"
    else:
        benchmark_status = "elite_delta_confirmed"
        report_status = "aprovado"

    evidence = build_evidence(project_root)
    payload = {
        "generated_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "manifest_path": str(manifest_path),
        "benchmark_id": manifest["benchmark_id"],
        "reference_asset": str(resolve_asset(project_root, manifest["reference_asset"])),
        "reference_profile": reference_profile,
        "minimum_delta": minimum_delta,
        "status": report_status,
        "assets": flat_assets,
        "lane_scores": lane_outputs,
        "comparison": {
            "basic_lane_score": basic_score,
            "elite_lane_score": elite_score,
            "elite_minus_basic": delta,
            "minimum_delta": minimum_delta,
            "passed_delta": passed_delta,
            "basic_lane_status": basic_lane_status,
            "elite_lane_status": elite_lane_status,
        },
        "benchmark_status": benchmark_status,
        "evidence": evidence,
    }

    save_json(output_path, payload)
    print(json.dumps({
        "benchmark_id": payload["benchmark_id"],
        "benchmark_status": benchmark_status,
        "elite_lane_score": elite_score,
        "basic_lane_score": basic_score,
        "elite_minus_basic": delta,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

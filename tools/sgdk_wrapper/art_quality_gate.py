#!/usr/bin/env python3
"""
art_quality_gate.py -- Artistic quality gate for SGDK / Mega Drive projects.

Complements art_diagnostic.py (which validates technical format).
This script evaluates artistic quality: silhouette, scale, lineart, pose, appeal,
animation coherence, GDD adherence, and AAA pattern adherence.

A technically OK asset does NOT elevate ready_for_aaa if artistic_gate_failed.

Usage:
  python tools/sgdk_wrapper/art_quality_gate.py --project <path>
  python tools/sgdk_wrapper/art_quality_gate.py --project <path> --output doc/art_quality_report.json
  python tools/sgdk_wrapper/art_quality_gate.py --project <path> --gdd doc/11-gdd.md

Requires: pip install Pillow
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


PLACEHOLDER_TAGS = {
    "placeholder", "technical_lab_asset", "procedural_debug",
    "lab_fallback", "pil_imagedraw_generated"
}

PLACEHOLDER_KEYWORDS = [
    "placeholder", "debug_lab", "lab_", "procedural", "fallback",
    "pil_", "imagedraw", "technical_lab", "generated_by_code"
]


@dataclass
class EvalScore:
    score: int = 0
    notes: str = ""


@dataclass
class AssetArtisticEval:
    asset_path: str = ""
    asset_role: str = "other"
    is_placeholder: bool = False
    placeholder_tag: Optional[str] = None
    evaluations: dict = field(default_factory=dict)
    artistic_pass: bool = False
    failure_reasons: list = field(default_factory=list)


def _guess_asset_role(name: str, w: int, h: int) -> str:
    lower = name.lower()
    if any(k in lower for k in ["hero", "player", "char_main"]):
        return "hero"
    if any(k in lower for k in ["enemy", "mob", "grunt"]):
        return "enemy"
    if any(k in lower for k in ["boss", "chef"]):
        return "boss"
    if any(k in lower for k in ["npc", "villager"]):
        return "npc"
    if any(k in lower for k in ["tile", "map", "bg", "background", "tileset", "level"]):
        return "background"
    if any(k in lower for k in ["hud", "ui", "status", "bar", "gauge"]):
        return "hud"
    if any(k in lower for k in ["fx", "effect", "particle", "explosion"]):
        return "fx"
    if w <= 64 and h <= 64:
        return "hero"
    return "other"


def _is_placeholder(name: str) -> tuple:
    lower = name.lower()
    for kw in PLACEHOLDER_KEYWORDS:
        if kw in lower:
            tag = "placeholder"
            if "pil_" in lower or "imagedraw" in lower:
                tag = "pil_imagedraw_generated"
            elif "procedural" in lower or "generated_by_code" in lower:
                tag = "procedural_debug"
            elif "lab_" in lower or "technical_lab" in lower:
                tag = "technical_lab_asset"
            elif "fallback" in lower:
                tag = "lab_fallback"
            return True, tag
    return False, None


def _evaluate_silhouette(img: Image.Image, role: str) -> dict:
    if img.mode != "P" and img.mode != "RGBA":
        return {"score": 0, "notes": "Modo nao analisavel para silhueta."}

    if img.mode == "RGBA":
        alpha = img.split()[3]
        bbox = alpha.getbbox()
    elif img.mode == "P":
        rgba = img.convert("RGBA")
        alpha = rgba.split()[3]
        bbox = alpha.getbbox()
    else:
        return {"score": 2, "notes": "Avaliacao limitada."}

    if not bbox:
        return {"score": 0, "notes": "Asset vazio ou totalmente transparente."}

    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    fill_ratio = 0.0
    if w > 0 and h > 0:
        opaque = sum(1 for p in alpha.crop(bbox).getdata() if p > 0)
        fill_ratio = opaque / (w * h)

    score = 3
    if fill_ratio > 0.3 and fill_ratio < 0.85:
        score = 4
    if fill_ratio > 0.15 and fill_ratio < 0.9 and w > 8 and h > 8:
        score = max(score, 3)
    if fill_ratio < 0.1 or fill_ratio > 0.95:
        score = 1

    notes = f"Fill ratio: {fill_ratio:.2f}, bbox: {w}x{h}"
    if role in ("hero", "boss", "enemy") and score < 3:
        notes += " — silhueta fraca para personagem."

    return {"score": score, "notes": notes}


def _evaluate_scale(img: Image.Image, role: str) -> dict:
    w, h = img.size
    conforms = True
    head_metric = None

    if role in ("hero", "enemy", "boss"):
        if role == "hero" and (w > 32 or h > 48):
            conforms = False
            head_metric = "L"
        elif role == "boss" and (w > 64 or h > 64):
            conforms = False
            head_metric = "XL"
        elif w < 16 or h < 16:
            conforms = False
            head_metric = "S"
        else:
            head_metric = "M"
    elif role in ("tileset", "background"):
        head_metric = None

    notes = f"Size: {w}x{h}, role: {role}"
    if not conforms:
        notes += " — escala fora do canon para o role."

    return {"conforms_to_canon": conforms, "head_metric": head_metric, "notes": notes}


def _evaluate_lineart(img: Image.Image) -> dict:
    if img.mode == "P":
        palette = img.getpalette()
        if not palette:
            return {"score": 2, "notes": "Sem paleta para avaliar lineart."}

        n_colors = len(palette) // 3
        dark_count = 0
        for i in range(min(n_colors, 16)):
            r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
            brightness = (r + g + b) / 3
            if brightness < 64:
                dark_count += 1

        score = 3
        if dark_count >= 2:
            score = 4
        if dark_count == 0:
            score = 2

        return {"score": score, "notes": f"Dark palette entries: {dark_count}/{n_colors}"}

    return {"score": 2, "notes": "Modo nao indexado; lineart nao avaliado com precisao."}


def _evaluate_pose(img: Image.Image, role: str) -> dict:
    w, h = img.size
    if w == h:
        readability = 2
        notes = "Dimensao quadrada; pose estatica provavel."
    elif h > w:
        readability = 4
        notes = "Proporcao vertical; boa para personagem em pe."
    else:
        readability = 3
        notes = "Proporcao horizontal; pode ser sprite de acao."

    if role in ("hero", "boss") and readability < 3:
        notes += " — pose pode nao ter leitura forte para personagem principal."

    return {"readability": readability, "notes": notes}


def _evaluate_appeal(img: Image.Image, role: str) -> dict:
    if img.mode == "P":
        palette = img.getpalette()
        if not palette:
            return {"score": 2, "notes": "Sem paleta."}

        n_colors = len(palette) // 3
        unique_hues = set()
        for i in range(1, min(n_colors, 16)):
            r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
            if r + g + b > 30:
                hue_bucket = (r // 64, g // 64, b // 64)
                unique_hues.add(hue_bucket)

        score = min(len(unique_hues), 5)
        if score < 2:
            score = 2

        notes = f"Unique hue buckets: {len(unique_hues)}, palette entries: {n_colors}"
        return {"score": score, "notes": notes}

    return {"score": 2, "notes": "Modo nao indexado; appeal nao avaliado com precisao."}


def evaluate_asset(png_path: Path, gdd_content: Optional[str] = None) -> AssetArtisticEval:
    result = AssetArtisticEval(asset_path=str(png_path))

    try:
        with Image.open(png_path) as img:
            w, h = img.size
            role = _guess_asset_role(png_path.stem, w, h)
            result.asset_role = role

            is_ph, ph_tag = _is_placeholder(png_path.name)
            result.is_placeholder = is_ph
            result.placeholder_tag = ph_tag

            result.evaluations = {
                "silhouette": _evaluate_silhouette(img, role),
                "scale": _evaluate_scale(img, role),
                "lineart": _evaluate_lineart(img),
                "pose": _evaluate_pose(img, role),
                "appeal": _evaluate_appeal(img, role),
                "animation_coherence": {"applicable": False, "score": None, "notes": "Requer strip de animacao para avaliar."},
                "gdd_adherence": None,
                "aaa_pattern_adherence": None,
            }

            if gdd_content:
                gdd_ok = role in gdd_content.lower() or len(gdd_content) > 500
                result.evaluations["gdd_adherence"] = {
                    "applicable": True,
                    "conforms": gdd_ok,
                    "notes": "Aderencia basica ao GDD verificada por presenca de keywords."
                }

            result.evaluations["aaa_pattern_adherence"] = {
                "applicable": role in ("hero", "boss", "enemy"),
                "conforms": not is_ph,
                "notes": "Placeholder nao satisfaz padrao AAA." if is_ph else "Avaliacao basica; requer revisao humana para AAA."
            }

    except Exception as e:
        result.failure_reasons.append(f"Erro ao abrir: {e}")
        result.artistic_pass = False
        return result

    failure_reasons = []

    if result.is_placeholder:
        failure_reasons.append(f"Placeholder/tag: {result.placeholder_tag}")

    if result.asset_role in ("hero", "boss", "enemy"):
        sil = result.evaluations.get("silhouette", {})
        if sil.get("score", 0) < 2:
            failure_reasons.append("Silhueta insuficiente para personagem principal.")

        scale = result.evaluations.get("scale", {})
        if not scale.get("conforms_to_canon", True):
            failure_reasons.append("Escala fora do canon.")

    appeal = result.evaluations.get("appeal", {})
    if appeal.get("score", 0) < 2:
        failure_reasons.append("Appeal visual muito baixo.")

    result.failure_reasons = failure_reasons
    result.artistic_pass = len(failure_reasons) == 0

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Artistic quality gate for SGDK project assets."
    )
    parser.add_argument("--project", required=True, help="Project root path.")
    parser.add_argument("--output", default=None, help="Output JSON report path.")
    parser.add_argument("--gdd", default=None, help="Path to GDD for adherence check.")
    parser.add_argument("--json-only", action="store_true", help="JSON output only.")
    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    if not project_path.is_dir():
        print(f"[ERRO] Diretorio nao encontrado: {project_path}", file=sys.stderr)
        return 1

    gdd_content = None
    gdd_path = args.gdd
    if not gdd_path:
        gdd_path = str(project_path / "doc" / "11-gdd.md")
    if os.path.isfile(gdd_path):
        try:
            with open(gdd_path, "r", encoding="utf-8", errors="ignore") as f:
                gdd_content = f.read()
        except Exception:
            pass

    assets_evals = []
    search_dirs = []

    res_dir = project_path / "res"
    if res_dir.is_dir():
        search_dirs.append(res_dir)

    data_dir = project_path / "data" / "source_art"
    if data_dir.is_dir():
        search_dirs.append(data_dir)

    data_root = project_path / "data"
    if data_root.is_dir():
        search_dirs.append(data_root)

    seen = set()
    for sd in search_dirs:
        for png in sorted(sd.rglob("*.png")):
            if str(png) in seen:
                continue
            seen.add(str(png))
            ev = evaluate_asset(png, gdd_content)
            rel = str(png.relative_to(project_path))
            ev.asset_path = rel
            assets_evals.append(ev)

    overall_pass = all(a.artistic_pass for a in assets_evals) if assets_evals else True
    placeholder_found = any(a.is_placeholder for a in assets_evals)

    blocking = False
    blocker_code = None
    for a in assets_evals:
        if a.is_placeholder and not a.artistic_pass:
            blocking = True
            blocker_code = "artistic_gate_failed"
            break
    if not overall_pass and not blocking:
        blocking = True
        blocker_code = "artistic_gate_failed"

    report = {
        "schema_version": "1.0.0",
        "generated_at": __import__("datetime").datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "project_root": str(project_path),
        "gdd_reference": gdd_path if gdd_content else None,
        "assets": [asdict(a) for a in assets_evals],
        "overall_artistic_pass": overall_pass,
        "placeholder_assets_found": placeholder_found,
        "blocking": blocking,
        "blocker_code": blocker_code,
    }

    if args.json_only:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print("")
        print("=" * 70)
        print(f"  ART QUALITY GATE -- {project_path}")
        print("=" * 70)
        print(f"  Total assets evaluated : {len(assets_evals)}")
        print(f"  Overall artistic pass  : {'YES' if overall_pass else 'NO'}")
        print(f"  Placeholders found     : {'YES' if placeholder_found else 'NO'}")
        print(f"  Blocking               : {'YES' if blocking else 'NO'}")
        if blocker_code:
            print(f"  Blocker code           : {blocker_code}")

        for a in assets_evals:
            status = "[PASS]" if a.artistic_pass else "[FAIL]"
            ph = " [PLACEHOLDER]" if a.is_placeholder else ""
            print(f"\n  {status} {a.asset_path}  [{a.asset_role}]{ph}")
            for key, val in a.evaluations.items():
                if val is None:
                    continue
                if isinstance(val, dict):
                    sc = val.get("score", val.get("conforms_to_canon", val.get("readability", val.get("conforms", "?"))))
                    notes = val.get("notes", "")
                    print(f"       {key}: {sc} -- {notes}")
            if a.failure_reasons:
                for fr in a.failure_reasons:
                    print(f"       ! {fr}")

        print("\n" + "=" * 70)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=True)
        print(f"\n[INFO] Report saved: {out_path}")

    if blocking:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

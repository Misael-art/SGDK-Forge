#!/usr/bin/env python3
"""Build review-only evidence from persisted sources and native candidates.

This script never writes candidate pixels.  It only composes a labelled panel
and a qualitative review record so source roles stay auditable.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit(image, box):
    image = image.convert("RGBA")
    image.thumbnail(box, Image.Resampling.NEAREST)
    layer = Image.new("RGBA", box, (20, 22, 30, 255))
    layer.alpha_composite(image, ((box[0] - image.width) // 2, (box[1] - image.height) // 2))
    return layer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root.resolve()
    candidate = args.candidate.resolve()
    model = root / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
    direction = root / "data/source_art/visual_producer_outputs/taina_idle_guard_scale_shootout_v01/taina_idle_guard_56x80_visual_source_v01.png"
    iteration_root = root / "rascunho/taina_native_authoring_56x80_v01"
    candidates = [
        ("v01", iteration_root / "exports/taina_idle_guard_56x80_native_authoring_v01.png"),
        ("v02", iteration_root / "exports/taina_idle_guard_56x80_native_authoring_v02.png"),
        ("v03", iteration_root / "exports/taina_idle_guard_56x80_native_authoring_v03.png"),
        ("v04", candidate),
    ]
    for path in [model, direction, candidate, *[p for _, p in candidates]]:
        if not path.is_file():
            raise FileNotFoundError(path)
    out = args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    panel = Image.new("RGBA", (1200, 760), (14, 16, 24, 255))
    draw = ImageDraw.Draw(panel)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except OSError:
        font = small = ImageFont.load_default()
    draw.text((28, 18), "TAÍNA — revisão nativa 56×80 / v04", fill=(245, 240, 220), font=font)
    draw.text((28, 52), "model sheet = identidade | fonte 56×80 = direção/proporção | v04 = pixels nativos locais", fill=(190, 198, 210), font=small)

    cards = [("MODEL SHEET\nidentity source", model, (32, 92, 330, 360)),
             ("56×80 SOURCE\ndirection only", direction, (352, 92, 650, 360)),
             ("V04 NATIVE\nreview candidate", candidate, (672, 92, 1168, 360))]
    for label, path, (x0, y0, x1, y1) in cards:
        draw.rectangle((x0, y0, x1, y1), outline=(86, 96, 118), width=2)
        draw.text((x0 + 12, y0 + 10), label, fill=(245, 240, 220), font=small)
        slot = (x1 - x0 - 24, y1 - y0 - 58)
        rendered = fit(Image.open(path), slot)
        panel.alpha_composite(rendered, (x0 + 12, y0 + 46))
    draw.text((32, 390), "CAUSAL NATIVE ITERATIONS", fill=(245, 240, 220), font=font)
    cell_w, cell_h = 270, 300
    for i, (label, path) in enumerate(candidates):
        x, y = 32 + i * 292, 430
        draw.rectangle((x, y, x + cell_w, y + cell_h), outline=(86, 96, 118), width=2)
        draw.text((x + 10, y + 10), label.upper(), fill=(245, 240, 220), font=font)
        panel.alpha_composite(fit(Image.open(path), (cell_w - 20, 235)), (x + 10, y + 48))
        draw.text((x + 10, y + 270), "native editor action log", fill=(190, 198, 210), font=small)
    panel.convert("RGB").save(out, "PNG")
    review = {
        "schema_version": "native_visual_review.v1",
        "status": "pending_human_decision",
        "candidate_asset_id": "taina_idle_guard_56x80_native_authoring_v04",
        "candidate_sha256": sha(candidate),
        "scale": "56x80",
        "source_role_policy": {
            "identity_source": {"path": str(model.relative_to(root)), "sha256": sha(model), "role": "identity_only"},
            "approved_direction_source": {"path": str(direction.relative_to(root)), "sha256": sha(direction), "role": "proportion_and_direction_only"},
            "pixel_copy_from_sources": False,
        },
        "observations": {
            "gains": [
                "1x reads as a standing brawler with a diagonal two-arm guard",
                "eye/gaze marks and asymmetric hair with front lock are present",
                "orange top is separated from the exposed skin abdomen by a clean hem",
                "teal wraps, lateral sash with knot/tail, indigo wide trousers and planted feet are visible",
            ],
            "losses_or_risks": [
                "face remains compact at native 1x and needs human perceptual confirmation",
                "fists and elbows are readable as clusters but still have limited internal articulation",
                "warm-dark outline is consistent but less neutral than a black control",
                "leg and foot clusters are readable but retain rough native-authoring edges",
            ],
            "comparison": "v04 is materially richer than v01-v03 because geometry and material topology were changed in the native grid, not merely requantized; the candidate still requires a human visual gate.",
        },
        "review_panel": str(out.relative_to(root)),
        "iteration_hashes": {label: sha(path) for label, path in candidates},
        "no_numeric_aesthetic_score": True,
    }
    report = out.with_name("native_visual_review_report.json")
    report.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"panel": str(out.relative_to(root)), "report": str(report.relative_to(root)), "candidate_sha256": review["candidate_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

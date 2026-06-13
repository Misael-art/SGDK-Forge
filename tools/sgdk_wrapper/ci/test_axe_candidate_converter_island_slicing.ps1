<#
.SYNOPSIS
    Verifica que o conversor AXE usa ilhas globais para spritesheets com espacamento irregular.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$converter = Join-Path $workspaceRoot "tools\image-tools\convert_axe_premium_sources.py"
$fixtureRoot = Join-Path $workspaceRoot "out\ci\axe_candidate_converter_island_slicing_fixture"

if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $fixtureRoot | Out-Null

$env:AXE_CONVERTER_FIXTURE_ROOT = $fixtureRoot
@'
from pathlib import Path
import os
from PIL import Image, ImageDraw

root = Path(os.environ["AXE_CONVERTER_FIXTURE_ROOT"])
source = root / "irregular_source.png"
img = Image.new("RGBA", (360, 150), (234, 34, 231, 255))
draw = ImageDraw.Draw(img)

# Three large silhouettes with deliberately uneven horizontal spacing.
draw.rectangle((10, 30, 85, 125), fill=(220, 220, 220, 255), outline=(0, 0, 0, 255))
draw.rectangle((125, 28, 200, 125), fill=(220, 220, 220, 255), outline=(0, 0, 0, 255))
draw.rectangle((265, 32, 340, 125), fill=(220, 220, 220, 255), outline=(0, 0, 0, 255))
img.save(source)
'@ | python -

$env:AXE_CONVERTER_PATH = $converter
@'
import importlib.util
import os
from pathlib import Path
from PIL import Image

converter_path = Path(os.environ["AXE_CONVERTER_PATH"])
fixture_root = Path(os.environ["AXE_CONVERTER_FIXTURE_ROOT"])
spec = importlib.util.spec_from_file_location("convert_axe_premium_sources", converter_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

img = Image.open(fixture_root / "irregular_source.png").convert("RGBA")
bg = module.bg_color(img)
reports, blockers = module.select_frame_crops(img, 3, bg, pad=4)

if blockers:
    raise SystemExit(f"expected no blockers for three clean global islands, got {blockers}")
if len(reports) != 3:
    raise SystemExit(f"expected 3 frame reports, got {len(reports)}")

expected_x = [(6, 90), (121, 205), (261, 345)]
for idx, (report, expected) in enumerate(zip(reports, expected_x), start=1):
    crop = report.get("crop_box")
    if not crop:
        raise SystemExit(f"frame {idx} missing crop_box: {report}")
    actual = (crop[0], crop[2])
    if actual != expected:
        raise SystemExit(f"frame {idx} expected x crop {expected}, got {actual}; full crop={crop}")
    if report.get("slicing_method") != "global_bfs_islands":
        raise SystemExit(f"frame {idx} did not record global_bfs_islands: {report.get('slicing_method')}")

print("axe candidate converter island slicing: passed")

throw_report = {
    "asset_id": "spr_test_throw",
    "state_profile": "throw",
    "frame_metrics": [
        {"bbox_size": [70, 28], "bottom": 76},
        {"bbox_size": [70, 54], "bottom": 76},
        {"bbox_size": [70, 76], "bottom": 77},
    ],
    "quantization_reports": [
        {"scale": 0.15},
        {"scale": 0.15},
        {"scale": 0.15},
    ],
    "fixed_scale": 0.15,
}
scale_report = module.scale_lock_report([throw_report])
if scale_report["overall_status"] != "passed":
    raise SystemExit(f"stable throw pose scale lock should pass, got {scale_report['blocking_statuses']}")

print("axe candidate converter throw scale profile: passed")
'@ | python -

if ($LASTEXITCODE -ne 0) {
    throw "AXE candidate converter island slicing regression failed"
}

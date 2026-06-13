<#
.SYNOPSIS
    Verifica o gate de integridade de strips de personagem.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$tool = Join-Path $workspaceRoot "tools\image-tools\analyze_sprite_strip_integrity.py"
$fixtureRoot = Join-Path $workspaceRoot "out\ci\sprite_strip_integrity_fixture"

if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $fixtureRoot | Out-Null

$env:FIXTURE_ROOT = $fixtureRoot
@'
from pathlib import Path
import os
from PIL import Image, ImageDraw

root = Path(os.environ["FIXTURE_ROOT"])
magenta = (255, 0, 255)

def save_indexed(path, image):
    palette = [
        255, 0, 255,
        0, 0, 0,
        255, 255, 255,
        40, 80, 160,
        240, 190, 130,
        240, 220, 40,
        136, 136, 170,
    ] + [0, 0, 0] * (256 - 7)
    indexed = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=7)
    indexed.putpalette(palette)
    # Remap exact magenta to index 0 after adaptive conversion.
    rgb = image.convert("RGB")
    out = Image.new("P", image.size, 0)
    out.putpalette(palette)
    out_px = out.load()
    rgb_px = rgb.load()
    for y in range(image.height):
        for x in range(image.width):
            c = rgb_px[x, y]
            if c == magenta:
                out_px[x, y] = 0
            elif c == (0, 0, 0):
                out_px[x, y] = 1
            elif c == (255, 255, 255):
                out_px[x, y] = 2
            elif c == (40, 80, 160):
                out_px[x, y] = 3
            elif c == (240, 190, 130):
                out_px[x, y] = 4
            elif c == (240, 220, 40):
                out_px[x, y] = 5
            else:
                out_px[x, y] = 6
    out.save(path)

clean = Image.new("RGB", (96 * 3, 64), magenta)
d = ImageDraw.Draw(clean)
for frame in range(3):
    ox = frame * 96
    d.rectangle((ox + 30, 12, ox + 62, 54), fill=(255, 255, 255), outline=(0, 0, 0))
    d.rectangle((ox + 38 + frame, 28, ox + 54 + frame, 58), fill=(40, 80, 160), outline=(0, 0, 0))
    d.rectangle((ox + 36, 6, ox + 56, 20), fill=(240, 190, 130), outline=(0, 0, 0))
save_indexed(root / "clean.png", clean)

broken = Image.new("RGB", (96 * 2, 64), magenta)
d = ImageDraw.Draw(broken)
for frame in range(2):
    ox = frame * 96
    d.rectangle((ox + 15, 0, ox + 72, 60), fill=(136, 136, 170))
    d.rectangle((ox + 30, 8, ox + 66, 58), fill=(255, 255, 255), outline=(0, 0, 0))
broken.putpixel((95, 60), (255, 255, 255))
d.rectangle((118, 18, 130, 28), fill=(240, 220, 40))
d.rectangle((170, 42, 188, 58), fill=(255, 255, 255), outline=(0, 0, 0))
save_indexed(root / "broken.png", broken)
'@ | python -

function Assert-True {
    param([string]$Name, [bool]$Condition)
    if (-not $Condition) {
        throw "[FAIL] $Name"
    }
    Write-Host "  [PASS] $Name"
}

Write-Host ""
Write-Host "=== Sprite Strip Integrity Analyzer Test ==="
Write-Host ""

$cleanReportPath = Join-Path $fixtureRoot "clean_report.json"
python $tool --image (Join-Path $fixtureRoot "clean.png") --frame-width 96 --frame-height 64 --output $cleanReportPath
if ($LASTEXITCODE -ne 0) { throw "Clean strip should pass" }
$cleanReport = Get-Content -LiteralPath $cleanReportPath -Raw | ConvertFrom-Json
Assert-True "clean strip passou" ($cleanReport.status -eq "passed")

$brokenReportPath = Join-Path $fixtureRoot "broken_report.json"
python $tool --image (Join-Path $fixtureRoot "broken.png") --frame-width 96 --frame-height 64 --detect-baked-fx --output $brokenReportPath
if ($LASTEXITCODE -eq 0) { throw "Broken strip should fail" }
$brokenReport = Get-Content -LiteralPath $brokenReportPath -Raw | ConvertFrom-Json
$codes = @($brokenReport.findings | ForEach-Object { $_.code })
Assert-True "broken strip reprovou" ($brokenReport.status -eq "rework")
Assert-True "detecta clipping/envelope" ($codes -contains "FRAME_EDGE_CLIPPING")
Assert-True "detecta matte nao transparente" ($codes -contains "NON_INDEX0_BACKGROUND_MATTE")
Assert-True "detecta componente desconectado grande" ($codes -contains "STRAY_LARGE_COMPONENT")
Assert-True "detecta FX embutido" ($codes -contains "BAKED_FX_IN_CHARACTER_SHEET")

$paletteDomainPath = Join-Path $fixtureRoot "palette_domain_report.json"
@{
    schema = "palette_domain_report.v1"
    measurement_level = "measured"
    characters = @{
        test_character = @{
            transparent = @(0)
            outline = @(1)
            cloth = @(2, 3)
            skin = @(4)
            warm_sash_or_highlight = @(5)
            fx = @()
        }
    }
    fx = @{
        transparent = @(0)
        spark = @(5)
    }
    status = "passed"
    blocking_statuses = @()
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $paletteDomainPath -Encoding UTF8

$materialReportPath = Join-Path $fixtureRoot "broken_character_material_report.json"
python $tool --image (Join-Path $fixtureRoot "broken.png") --frame-width 96 --frame-height 64 --detect-baked-fx --asset-kind character_animation_strip --state-profile standing --palette-domain-report $paletteDomainPath --palette-domain test_character --output $materialReportPath
if ($LASTEXITCODE -eq 0) { throw "Broken strip should still fail on structural issues" }
$materialReport = Get-Content -LiteralPath $materialReportPath -Raw | ConvertFrom-Json
$materialCodes = @($materialReport.findings | ForEach-Object { $_.code })
Assert-True "dominio de personagem nao classifica material quente como FX" ($materialCodes -notcontains "BAKED_FX_IN_CHARACTER_SHEET")

Write-Host ""
Write-Host "=== Results: 7/7 passed, 0 failed ==="

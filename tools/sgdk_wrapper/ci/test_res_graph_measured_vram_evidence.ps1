<#
.SYNOPSIS
    Verifica evidencia medida de residencia VRAM vinculada ao hash da ROM.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$auditScript = Join-Path $wrapperRoot 'res_graph_audit.ps1'
$projectRoot = Join-Path $workspaceRoot 'out\ci\res_graph_measured_vram_fixture'
$reportPath = Join-Path $projectRoot 'out\logs\res_graph_report.json'

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

Write-Host ''
Write-Host '=== Res Graph Measured VRAM Evidence Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\bgs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src\core') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'doc') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'out\logs') | Out-Null

$env:VRAM_FIXTURE_ROOT = $projectRoot
@'
from pathlib import Path
import os
from PIL import Image

root = Path(os.environ["VRAM_FIXTURE_ROOT"])
palette = [0, 0, 0] * 256
for name in ("bg_b.png", "bg_a.png", "letterbox.png"):
    image = Image.new("P", (8, 8), 1)
    image.putpalette(palette)
    image.save(root / "res" / "bgs" / name)
'@ | python -

Set-Content -LiteralPath (Join-Path $projectRoot 'res\resources.res') -Encoding ASCII -Value @(
    'IMAGE bg_b "bgs/bg_b.png" BEST'
    'IMAGE bg_a "bgs/bg_a.png" BEST'
    'TILESET letterbox "bgs/letterbox.png" NONE NONE'
)
Set-Content -LiteralPath (Join-Path $projectRoot 'src\core\app.c') -Encoding ASCII -Value @(
    '#include <genesis.h>'
    'void app_init(void) { SPR_initEx(680); }'
)
[System.IO.File]::WriteAllBytes((Join-Path $projectRoot 'out\rom.bin'), [byte[]](1..32))
$romHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot 'out\rom.bin') -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -LiteralPath (Join-Path $projectRoot 'out\logs\build_output.log') -Encoding ASCII -Value @(
    "'bg_b_tileset_data' packed with APLIB, size = 16 (50% - origin size = 128)"
    "'bg_a_tileset_data' packed with APLIB, size = 16 (50% - origin size = 64)"
)

$evidence = [ordered]@{
    schema_version = '1.0.0'
    status = 'measured'
    res_graph_evidence = [ordered]@{
        measurement_level = 'rescomp_build_output'
        rom_sha256 = $romHash
        build_log = 'out/logs/build_output.log'
        resident_resources = @(
            [ordered]@{ resource_name = 'bg_b'; unique_tiles = 4; measurement_method = 'rescomp_origin_size'; data_symbol = 'bg_b_tileset_data' }
            [ordered]@{ resource_name = 'bg_a'; unique_tiles = 2; measurement_method = 'rescomp_origin_size'; data_symbol = 'bg_a_tileset_data' }
            [ordered]@{ resource_name = 'letterbox'; unique_tiles = 1; measurement_method = 'source_png_unique' }
        )
    }
}
$evidence | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $projectRoot 'doc\vram_residency_report.json') -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -ProjectRoot $projectRoot -WarnOnly | Out-Null
$validExit = $LASTEXITCODE
$validReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'valid measured evidence exits cleanly' ($validExit -eq 0) "exit=$validExit"
Assert-True 'measured evidence is accepted' ([string]$validReport.vram.measured_evidence.status -eq 'valid')
Assert-True 'measurement level is measured' ([string]$validReport.vram.measurement_level -eq 'measured')
Assert-True 'only active resident resources are counted' (@($validReport.vram.tile_ranges).Count -eq 3)
Assert-True 'measured user tiles stay clear of reserve' ([string]$validReport.vram.status -eq 'ok')

$evidence.res_graph_evidence.rom_sha256 = ('0' * 64)
$evidence | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $projectRoot 'doc\vram_residency_report.json') -Encoding UTF8
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -ProjectRoot $projectRoot -WarnOnly | Out-Null
$invalidReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'stale ROM hash rejects measured evidence' ([string]$invalidReport.vram.measured_evidence.status -eq 'invalid')
Assert-True 'rejected evidence falls back to estimate' ([string]$invalidReport.vram.measurement_level -eq 'estimated')
Assert-True 'rejection emits traceable issue' (@($invalidReport.issues | Where-Object { $_.code -eq 'RG_VRAMEVIDENCE001' }).Count -eq 1)

$sourceHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot 'res\bgs\bg_b.png') -Algorithm SHA256).Hash.ToLowerInvariant()
$evidence.res_graph_evidence.measurement_level = 'rescomp_source_hash_snapshot'
$evidence.res_graph_evidence.rom_sha256 = $romHash
$evidence.res_graph_evidence.PSObject.Properties.Remove('build_log')
$evidence.res_graph_evidence.resident_resources = @(
    [ordered]@{
        resource_name = 'bg_b'
        unique_tiles = 4
        measurement_method = 'rescomp_origin_size_snapshot'
        origin_size_bytes = 128
        source_sha256 = $sourceHash
    }
    [ordered]@{ resource_name = 'letterbox'; unique_tiles = 1; measurement_method = 'source_png_unique' }
)
$evidence | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $projectRoot 'doc\vram_residency_report.json') -Encoding UTF8
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -ProjectRoot $projectRoot -WarnOnly | Out-Null
$snapshotReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'source-hash snapshot is accepted without current ResComp log' ([string]$snapshotReport.vram.measured_evidence.status -eq 'valid')
Assert-True 'snapshot method is exposed' ([string]$snapshotReport.vram.method -eq 'rescomp_source_hash_snapshot_bound_to_rom_sha256')

$evidence.res_graph_evidence.resident_resources[0].source_sha256 = ('0' * 64)
$evidence | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $projectRoot 'doc\vram_residency_report.json') -Encoding UTF8
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -ProjectRoot $projectRoot -WarnOnly | Out-Null
$staleSourceReport = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'changed source hash rejects measured snapshot' ([string]$staleSourceReport.vram.measured_evidence.status -eq 'invalid')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0

<#
.SYNOPSIS
    Verifica estimativa de residencia VRAM no res_graph_audit.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$auditScript = Join-Path $wrapperRoot 'res_graph_audit.ps1'
$projectRoot = Join-Path $workspaceRoot 'out\ci\res_graph_vram_fixture'
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
Write-Host '=== Res Graph VRAM Residency Test ==='
Write-Host ''

if (Test-Path -LiteralPath $projectRoot) {
    Remove-Item -LiteralPath $projectRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'res\bgs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'src\core') | Out-Null

$env:VRAM_FIXTURE_ROOT = $projectRoot
@'
from pathlib import Path
import os
from PIL import Image

root = Path(os.environ["VRAM_FIXTURE_ROOT"])
palette = []
for i in range(16):
    palette.extend(((i * 17) % 256, (i * 41) % 256, (i * 73) % 256))
palette.extend([0, 0, 0] * (256 - 16))

def write_unique_tiles(path, width, height, seed):
    img = Image.new("P", (width, height), 0)
    img.putpalette(palette)
    px = img.load()
    tid = seed
    for ty in range(height // 8):
        for tx in range(width // 8):
            tid += 1
            n = tid
            for y in range(8):
                for x in range(8):
                    px[tx * 8 + x, ty * 8 + y] = (n % 15) + 1
                    n //= 15
    img.save(path)

write_unique_tiles(root / "res" / "bgs" / "bg_b.png", 320, 160, 3)
write_unique_tiles(root / "res" / "bgs" / "bg_a.png", 320, 64, 900)
'@ | python -

Set-Content -LiteralPath (Join-Path $projectRoot 'res\resources.res') -Encoding ASCII -Value @(
    'IMAGE bg_b "bgs/bg_b.png" FAST ALL 0'
    'IMAGE bg_a "bgs/bg_a.png" FAST ALL 0'
)
Set-Content -LiteralPath (Join-Path $projectRoot 'src\core\app.c') -Encoding ASCII -Value @(
    '#include <genesis.h>'
    'void app_init(void) { SPR_init(); }'
)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -ProjectRoot $projectRoot -WarnOnly | Out-Null
$exitCode = $LASTEXITCODE
$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'audit exits cleanly with WarnOnly' ($exitCode -eq 0) "exit=$exitCode"
Assert-True 'vram report exists' ($null -ne $report.vram)
Assert-True 'sprite reserve default detected' ([int]$report.vram.sprite_reserve_tiles -eq 420)
Assert-True 'collision risk detected' ([string]$report.vram.status -eq 'collision_risk') "status=$($report.vram.status)"
Assert-True 'overlap is reported' (@($report.vram.overlaps).Count -gt 0)
Assert-True 'summary exposes overlap count' ([int]$report.summary.vram_overlap_count -gt 0)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0

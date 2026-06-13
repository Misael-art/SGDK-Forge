<#
.SYNOPSIS
    Verifica blockers canonicos para projetos sem .res, tiles hardcoded,
    captura vazia, dump VDP falso e cena capturada divergente.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\no_res_and_emulator_evidence_blockers_fixture'
$resGraphScript = Join-Path $wrapperRoot 'res_graph_audit.ps1'
$validateScript = Join-Path $wrapperRoot 'validate_resources.ps1'
$resGraphReportPath = Join-Path $fixtureRoot 'out\logs\res_graph_report.json'
$validationReportPath = Join-Path $fixtureRoot 'out\logs\validation_report.json'

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

function New-LowInformationPng {
    param([Parameter(Mandatory = $true)][string]$Path)

    Add-Type -AssemblyName System.Drawing -ErrorAction Stop
    $bitmap = New-Object System.Drawing.Bitmap 32, 32
    try {
        for ($y = 0; $y -lt 32; $y++) {
            for ($x = 0; $x -lt 32; $x++) {
                $color = if ($x -lt 16) { [System.Drawing.Color]::FromArgb(0, 0, 49) } else { [System.Drawing.Color]::Black }
                $bitmap.SetPixel($x, $y, $color)
            }
        }
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $bitmap.Dispose()
    }
}

Write-Host ''
Write-Host '=== No .res and Emulator Evidence Blockers Test ==='
Write-Host ''

if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'src\core') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\changelog') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\captures') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\evidence\blastem') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'res') | Out-Null

Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\11-gdd.md') -Encoding UTF8 -Value @'
# CI Fixture

Entrega visual AAA de gameplay shmup. Deve gerar ROM, emulador e evidencia visual.
'@
Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\changelog\changelog.md') -Encoding UTF8 -Value '# CI fixture'
Set-Content -LiteralPath (Join-Path $fixtureRoot 'src\core\app.c') -Encoding UTF8 -Value @'
#include <genesis.h>
static const u32 sTiles[16][8] = {0};
void main(void) {
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_loadTileData((const u32*)sTiles, TILE_USER_INDEX, 16, DMA);
    VDP_fillTileMapRect(BG_A, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX), 0, 0, 20, 10);
}
'@
[System.IO.File]::WriteAllBytes((Join-Path $fixtureRoot 'out\rom.bin'), [byte[]](1..64))

$screenshotPath = Join-Path $fixtureRoot 'out\captures\benchmark_visual.png'
New-LowInformationPng -Path $screenshotPath
$saveBytes = [System.Text.Encoding]::ASCII.GetBytes('VLAB fake fixture dump')
[System.IO.File]::WriteAllBytes((Join-Path $fixtureRoot 'out\captures\save.sram'), $saveBytes)
[System.IO.File]::WriteAllBytes((Join-Path $fixtureRoot 'out\captures\visual_vdp_dump.bin'), $saveBytes)

$runtimeMetrics = @{
    scene_id = 4
    expected_app_scene_id = 8
    samples_recorded = 12
    frames = @(1..12)
    over_budget_frames = 0
    cpu_load_max = 20
    cpu_load_p95 = 18
    cpu_load_jitter_max = 2
    max_scanline_sprites = 8
    fx_peak_concurrency = 1
}
[System.IO.File]::WriteAllText((Join-Path $fixtureRoot 'out\logs\runtime_metrics.json'), ($runtimeMetrics | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

$emulatorSession = @{
    timestamp = (Get-Date).ToUniversalTime().ToString('o')
    emulator = 'blastem'
    rom_path = (Join-Path $fixtureRoot 'out\rom.bin')
    rom_size_bytes = 64
    boot_emulador = 'ok'
    gameplay_basico = 'funcional'
    launch_status = 'captured'
    sandbox_root = (Join-Path $fixtureRoot 'out')
    save_root = (Join-Path $fixtureRoot 'out\captures')
    target_scene = 8
    expected_app_scene_id = 8
    captures = @($screenshotPath)
    evidence_files = @($screenshotPath)
    published_capture_files = @($screenshotPath, (Join-Path $fixtureRoot 'out\captures\save.sram'), (Join-Path $fixtureRoot 'out\captures\visual_vdp_dump.bin'))
    save_sram_path = (Join-Path $fixtureRoot 'out\captures\save.sram')
    visual_vdp_dump_path = (Join-Path $fixtureRoot 'out\captures\visual_vdp_dump.bin')
    fresh_sram_confirmed = $true
}
[System.IO.File]::WriteAllText((Join-Path $fixtureRoot 'out\logs\emulator_session.json'), ($emulatorSession | ConvertTo-Json -Depth 8), [System.Text.Encoding]::UTF8)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $resGraphScript -ProjectRoot $fixtureRoot | Out-Host
Assert-True 'res_graph_report generated' (Test-Path -LiteralPath $resGraphReportPath)
$resGraphReport = Get-Content -LiteralPath $resGraphReportPath -Raw | ConvertFrom-Json
Assert-True 'code-loaded tiles detected' ($resGraphReport.vram.status -eq 'code_loaded_tiles_unmeasured') ("status=$($resGraphReport.vram.status)")
Assert-True 'code-loaded estimate present' ([int]$resGraphReport.vram.code_loaded_tiles.estimated_tiles -ge 16) ("estimate=$($resGraphReport.vram.code_loaded_tiles.estimated_tiles)")

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validateScript -WorkDir $fixtureRoot | Out-Host
$validateExit = $LASTEXITCODE
Assert-True 'validate_resources returns non-zero' ($validateExit -ne 0) "exit=$validateExit"
Assert-True 'validation_report generated' (Test-Path -LiteralPath $validationReportPath)
$validationReport = Get-Content -LiteralPath $validationReportPath -Raw | ConvertFrom-Json
$statuses = @($validationReport.blocking_statuses)
Assert-True 'missing .res blocked' ($statuses -contains 'resources_res_missing_for_visual_delivery') ($statuses -join ',')
Assert-True 'asset pipeline not started blocked' ($statuses -contains 'asset_pipeline_not_started') ($statuses -join ',')
Assert-True 'code-loaded tiles blocked' ($statuses -contains 'code_loaded_tiles_unmeasured') ($statuses -join ',')
Assert-True 'low-information screenshot blocked' ($statuses -contains 'blank_or_low_information_capture') ($statuses -join ',')
Assert-True 'invalid VDP dump blocked' ($statuses -contains 'invalid_visual_vdp_dump') ($statuses -join ',')
Assert-True 'target scene mismatch blocked' ($statuses -contains 'runtime_target_scene_mismatch') ($statuses -join ',')
Assert-True 'ready_for_aaa false' (-not [bool]$validationReport.status_panel.ready_for_aaa)
Assert-True 'validado_budget false' (-not [bool]$validationReport.status_panel.validado_budget)

Write-Host ''
Write-Host "Total: $total | Passed: $passed | Failed: $failed"

if ($failed -gt 0) {
    exit 1
}
exit 0

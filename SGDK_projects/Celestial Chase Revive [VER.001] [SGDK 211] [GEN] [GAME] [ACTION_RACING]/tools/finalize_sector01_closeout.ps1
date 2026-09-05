[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$WorkspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot "..\.."))
$WrapperRoot = Join-Path $WorkspaceRoot "tools\sgdk_wrapper"
$RomPath = Join-Path $ProjectRoot "out\rom.bin"
$SuccessMetrics = Join-Path $ProjectRoot "out\evidence\blastem\routes\success\runtime_metrics.json"
$ReportPath = Join-Path $ProjectRoot "out\logs\sector01_final_closeout_report.json"

$ExpectedRomSha256 = "4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e"
$AllowedBlockingStatuses = @(
    "visual_gate_blocked",
    "procedural_fallback_as_final",
    "visual_direction_failed",
    "code_loaded_tiles_unmeasured"
)

function Invoke-Required {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][scriptblock]$Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

function Read-Json {
    param([Parameter(Mandatory)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required JSON artifact not found: $Path"
    }
    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

if (-not (Test-Path -LiteralPath $RomPath -PathType Leaf)) {
    throw "Frozen ROM not found: $RomPath"
}

$RomHashBefore = (Get-FileHash -LiteralPath $RomPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($RomHashBefore -ne $ExpectedRomSha256) {
    throw "Frozen ROM identity mismatch before closeout: $RomHashBefore"
}

Push-Location $ProjectRoot
try {
    Invoke-Required "Python regression" {
        python "tools\tests\test_sector01_recovery.py"
    }
    Invoke-Required "PowerShell recovery contracts" {
        & "tools\test_sector01_recovery_contracts.ps1"
    }
    Invoke-Required "Sector 01 report generation" {
        python "tools\generate_sector01_closeout_reports.py"
    }

    & (Join-Path $WrapperRoot "res_graph_audit.ps1") `
        -ProjectRoot $ProjectRoot `
        -WarnOnly
    if ($LASTEXITCODE -ne 0) {
        throw "Resource graph audit failed with exit code $LASTEXITCODE"
    }

    Invoke-Required "Measured scene budget" {
        & (Join-Path $WrapperRoot "audit_scene_budget.ps1") `
            -ProjectRoot $ProjectRoot `
            -RuntimeMetricsPath $SuccessMetrics `
            -SceneId "sector_01_farol_quebrado"
    }

    Invoke-Required "Emulator evidence seal" {
        & (Join-Path $WrapperRoot "finalize_emulator_evidence.ps1") `
            -ProjectRoot $ProjectRoot
    }

    # First pass refreshes validation after documents/reports changed.
    & (Join-Path $WrapperRoot "validate_resources.ps1") `
        -WorkDir $ProjectRoot `
        -CloseoutGate

    Invoke-Required "Freshness audit" {
        & (Join-Path $WrapperRoot "freshness_audit.ps1") `
            -ProjectRoot $ProjectRoot
    }

    # Canonical closeout is observational: no build and no new capture.
    Invoke-Required "Scene closeout gate" {
        & (Join-Path $WrapperRoot "scene_closeout_gate.ps1") `
            -ProjectRoot $ProjectRoot `
            -SceneId "sector_01_farol_quebrado" `
            -TargetScene 3 `
            -SkipBuild `
            -SkipRuntimeCapture `
            -SkipSceneRegression `
            -WarnOnly
    }

    Invoke-Required "Final freshness audit" {
        & (Join-Path $WrapperRoot "freshness_audit.ps1") `
            -ProjectRoot $ProjectRoot
    }

    # Non-zero is expected while the explicitly allowed creative hold is active.
    & (Join-Path $WrapperRoot "validate_resources.ps1") `
        -WorkDir $ProjectRoot `
        -CloseoutGate

    Invoke-Required "ROM mastering observation" {
        & (Join-Path $WrapperRoot "write_rom_mastering_report.ps1") `
            -ProjectRoot $ProjectRoot `
            -RomPath $RomPath
    }

    Invoke-Required "Project learning capture" {
        & (Join-Path $WrapperRoot "audit_project_learning.ps1") `
            -ProjectRoot $ProjectRoot `
            -Mode Capture `
            -OutputFormat Json
    }
}
finally {
    Pop-Location
}

$RomHashAfter = (Get-FileHash -LiteralPath $RomPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($RomHashAfter -ne $RomHashBefore) {
    throw "ROM changed during report-only closeout: before=$RomHashBefore after=$RomHashAfter"
}

$Validation = Read-Json (Join-Path $ProjectRoot "out\logs\validation_report.json")
$Freshness = Read-Json (Join-Path $ProjectRoot "out\logs\freshness_audit_report.json")
$EvidenceSeal = Read-Json (Join-Path $ProjectRoot "out\logs\evidence_closeout_report.json")
$SceneCloseout = Read-Json (Join-Path $ProjectRoot "out\logs\scene_closeout_gate_report.json")
$SceneBudget = Read-Json (Join-Path $ProjectRoot "out\logs\scene_budget_report.json")
$MemoryBudget = Read-Json (Join-Path $ProjectRoot "out\logs\memory_budget_report.json")
$SpritePressure = Read-Json (Join-Path $ProjectRoot "out\logs\sprite_scanline_pressure_report.json")

$ActualBlockingStatuses = @(
    $Validation.blocking_statuses |
        Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
        Sort-Object -Unique
)
$UnexpectedBlockingStatuses = @(
    $ActualBlockingStatuses |
        Where-Object { $_ -notin $AllowedBlockingStatuses }
)
$MissingExpectedHolds = @(
    $AllowedBlockingStatuses |
        Where-Object { $_ -notin $ActualBlockingStatuses }
)

if ($UnexpectedBlockingStatuses.Count -gt 0) {
    throw "Unexpected closeout blocker(s): $($UnexpectedBlockingStatuses -join ', ')"
}
if ($MissingExpectedHolds.Count -gt 0) {
    throw "Expected hold(s) disappeared without authorization: $($MissingExpectedHolds -join ', ')"
}
if ([string]$Freshness.status -ne "ok") {
    throw "Freshness audit is not clean: $($Freshness.status)"
}
if ([string]$EvidenceSeal.seal_status -ne "sealed" -or -not [bool]$EvidenceSeal.rom_identity_stable) {
    throw "Emulator evidence seal is not stable"
}
if ([string]$SceneBudget.status -notin @("ok", "passed")) {
    throw "Measured scene budget is not approved: $($SceneBudget.status)"
}
if ([string]$MemoryBudget.status -ne "ok") {
    throw "Memory budget is not approved: $($MemoryBudget.status)"
}
if ([string]$SpritePressure.status -ne "ok") {
    throw "Sprite pressure report is not approved: $($SpritePressure.status)"
}

$FinalReport = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    status = "technical_closeout_complete_creative_hold"
    project_root = $ProjectRoot
    rom = [ordered]@{
        path = $RomPath
        sha256 = $RomHashAfter
        size_bytes = (Get-Item -LiteralPath $RomPath).Length
        unchanged_during_closeout = $true
    }
    verification = [ordered]@{
        regressions = "passed"
        freshness = $Freshness.status
        evidence_seal = $EvidenceSeal.seal_status
        scene_closeout = $SceneCloseout.closeout_status
        scene_budget = $SceneBudget.status
        memory_budget = $MemoryBudget.status
        sprite_pressure = $SpritePressure.status
    }
    allowed_blocking_statuses = $ActualBlockingStatuses
    release_hold = @(
        "definitive_art",
        "audio",
        "upgrade_beacon_intermission",
        "sector_02"
    )
    ready_for_aaa = $false
    mastering_ready = $false
}

$FinalReport |
    ConvertTo-Json -Depth 8 |
    Set-Content -LiteralPath $ReportPath -Encoding UTF8

Write-Host "[SECTOR01-CLOSEOUT] status=$($FinalReport.status)"
Write-Host "[SECTOR01-CLOSEOUT] rom_sha256=$RomHashAfter"
Write-Host "[SECTOR01-CLOSEOUT] report=$ReportPath"

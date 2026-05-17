<#
.SYNOPSIS
    Runs the canonical closeout sequence for an SGDK scene/project.
.DESCRIPTION
    Orchestrates existing wrapper tools in the expected order and writes a
    machine-readable report to out/logs/scene_closeout_gate_report.json.

    This script does not replace the individual validators. It gives agents a
    single conservative path for: build -> contracts -> resource graph ->
    validation -> runtime capture -> scene regression -> freshness audit.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$SceneId = "",

    [Parameter(Mandatory = $false)]
    [int]$TargetScene = -1,

    [Parameter(Mandatory = $false)]
    [switch]$SkipBuild,

    [Parameter(Mandatory = $false)]
    [switch]$SkipRuntimeCapture,

    [Parameter(Mandatory = $false)]
    [switch]$SkipSceneRegression,

    [Parameter(Mandatory = $false)]
    [switch]$WarnOnly,

    [Parameter(Mandatory = $false)]
    [switch]$PlanOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = (Get-Location).Path
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "ProjectRoot not found: $ProjectRoot"
}

$ScriptRoot = $PSScriptRoot
$LogDir = Join-Path $ProjectRoot "out\logs"
if (-not (Test-Path -LiteralPath $LogDir -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}
$ReportPath = Join-Path $LogDir "scene_closeout_gate_report.json"

function New-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Kind,
        [Parameter(Mandatory = $true)][string]$Command,
        [string[]]$Arguments = @(),
        [bool]$Required = $true
    )

    return [ordered]@{
        name = $Name
        kind = $Kind
        command = $Command
        arguments = @($Arguments)
        required = [bool]$Required
        status = "pending"
        exit_code = $null
        log_path = $null
        started_at = $null
        finished_at = $null
        duration_ms = $null
        skipped_reason = $null
    }
}

function Invoke-CloseoutStep {
    param([Parameter(Mandatory = $true)]$Step)

    $Step.started_at = (Get-Date).ToUniversalTime().ToString("o")
    $safeName = ($Step.name -replace '[^A-Za-z0-9_.-]', '_')
    $stepLog = Join-Path $LogDir ("scene_closeout_{0}.log" -f $safeName)
    $Step.log_path = $stepLog

    if ($PlanOnly) {
        $Step.status = "planned"
        $Step.finished_at = (Get-Date).ToUniversalTime().ToString("o")
        $Step.duration_ms = 0
        return $Step
    }

    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $output = New-Object System.Collections.ArrayList
    $exitCode = 0

    try {
        $cmdOutput = & $Step.command @($Step.arguments) 2>&1
        foreach ($line in @($cmdOutput)) {
            [void]$output.Add([string]$line)
        }
        if ($LASTEXITCODE -is [int] -and $LASTEXITCODE -ne 0) {
            $exitCode = [int]$LASTEXITCODE
        }
    } catch {
        [void]$output.Add($_.Exception.Message)
        $exitCode = 1
    }

    $timer.Stop()
    $Step.exit_code = $exitCode
    $Step.duration_ms = [int]$timer.ElapsedMilliseconds
    $Step.finished_at = (Get-Date).ToUniversalTime().ToString("o")
    [System.IO.File]::WriteAllLines($stepLog, [string[]]$output, [System.Text.Encoding]::UTF8)

    if ($exitCode -eq 0) {
        $Step.status = "ok"
    } elseif ($WarnOnly -or -not $Step.required) {
        $Step.status = "warning"
    } else {
        $Step.status = "failed"
    }

    return $Step
}

$steps = New-Object System.Collections.ArrayList

if (-not $SkipBuild) {
    $buildBat = Join-Path $ProjectRoot "build.bat"
    if (Test-Path -LiteralPath $buildBat -PathType Leaf) {
        [void]$steps.Add((New-Step -Name "build" -Kind "build" -Command "cmd.exe" -Arguments @("/c", $buildBat) -Required $true))
    } else {
        [void]$steps.Add((New-Step -Name "build" -Kind "build" -Command "cmd.exe" -Arguments @("/c", (Join-Path $ScriptRoot "build.bat"), $ProjectRoot) -Required $true))
    }
}

[void]$steps.Add((New-Step -Name "scene_contract_compiler" -Kind "contract" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "scene_contract_compiler.ps1"), "-ProjectRoot", $ProjectRoot) -Required $true))

[void]$steps.Add((New-Step -Name "res_graph_audit" -Kind "resources" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "res_graph_audit.ps1"), "-ProjectRoot", $ProjectRoot) -Required $true))

[void]$steps.Add((New-Step -Name "validate_resources" -Kind "validation" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "validate_resources.ps1"), "-WorkDir", $ProjectRoot) -Required $true))

if (-not $SkipRuntimeCapture) {
    if ($TargetScene -ge 0) {
        [void]$steps.Add((New-Step -Name "runtime_capture" -Kind "emulator" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "run_runtime_capture.ps1"), "-ProjectDir", $ProjectRoot, "-TargetScene", ([string]$TargetScene), "-Emulator", "blastem") -Required $true))
        [void]$steps.Add((New-Step -Name "validate_resources_post_runtime" -Kind "validation" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "validate_resources.ps1"), "-WorkDir", $ProjectRoot) -Required $true))
    } else {
        $step = New-Step -Name "runtime_capture" -Kind "emulator" -Command "powershell.exe" -Arguments @() -Required $false
        $step.status = "skipped"
        $step.skipped_reason = "TargetScene not provided"
        [void]$steps.Add($step)
    }
}

if (-not $SkipSceneRegression) {
    $regressionArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "run_scene_regression.ps1"), "-ProjectRoot", $ProjectRoot)
    if (-not [string]::IsNullOrWhiteSpace($SceneId)) {
        $regressionArgs += @("-SceneId", $SceneId)
    }
    if ($WarnOnly) {
        $regressionArgs += @("-WarnOnly")
    }
    [void]$steps.Add((New-Step -Name "scene_regression" -Kind "emulator" -Command "powershell.exe" -Arguments $regressionArgs -Required $true))
    [void]$steps.Add((New-Step -Name "validate_resources_final" -Kind "validation" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "validate_resources.ps1"), "-WorkDir", $ProjectRoot) -Required $true))
}

[void]$steps.Add((New-Step -Name "freshness_audit" -Kind "freshness" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "freshness_audit.ps1"), "-ProjectRoot", $ProjectRoot) -Required $true))

$executed = New-Object System.Collections.ArrayList
$failed = $false
foreach ($step in @($steps)) {
    if ($step.status -eq "skipped") {
        [void]$executed.Add($step)
        continue
    }

    $result = Invoke-CloseoutStep -Step $step
    [void]$executed.Add($result)
    Write-Host ("[CLOSEOUT] {0}: {1}" -f $result.name, $result.status)

    if ($result.status -eq "failed") {
        $failed = $true
        break
    }
}

$validationReportPath = Join-Path $ProjectRoot "out\logs\validation_report.json"
$freshnessReportPath = Join-Path $ProjectRoot "out\logs\freshness_audit_report.json"
$sceneRegressionReportPath = Join-Path $ProjectRoot "out\logs\scene_regression_report.json"
$runtimeMetricsPath = Join-Path $ProjectRoot "out\logs\runtime_metrics.json"
$resGraphReportPath = Join-Path $ProjectRoot "out\logs\res_graph_report.json"
$validationBlockingStatuses = @()
$closeoutBlockingStatuses = @()
$validationReportReadable = $false
if ((-not $PlanOnly) -and (Test-Path -LiteralPath $validationReportPath -PathType Leaf)) {
    try {
        $validationReport = Get-Content -LiteralPath $validationReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $validationReportReadable = $true
        if ($validationReport.PSObject.Properties.Name -contains "blocking_statuses") {
            $validationBlockingStatuses = @($validationReport.blocking_statuses | Where-Object {
                $null -ne $_ -and -not [string]::IsNullOrWhiteSpace([string]$_)
            } | Select-Object -Unique)
        }
    } catch {
        $validationBlockingStatuses = @("validation_report_unreadable")
    }
}
$resGraphVramStatus = $null
$resGraphVramOverlapCount = 0
if ((-not $PlanOnly) -and (Test-Path -LiteralPath $resGraphReportPath -PathType Leaf)) {
    try {
        $resGraphReport = Get-Content -LiteralPath $resGraphReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($resGraphReport.PSObject.Properties.Name -contains "vram") {
            $resGraphVramStatus = [string]$resGraphReport.vram.status
            $resGraphVramOverlapCount = @($resGraphReport.vram.overlaps).Count
            if ($resGraphVramStatus -eq "collision_risk" -or $resGraphVramOverlapCount -gt 0) {
                $closeoutBlockingStatuses += "vram_residency_collision_risk"
            }
        }
    } catch {
        $closeoutBlockingStatuses += "res_graph_report_unreadable"
    }
}
$closeoutBlockingStatuses += @($validationBlockingStatuses)
$closeoutBlockingStatuses = @($closeoutBlockingStatuses | Where-Object {
    $null -ne $_ -and -not [string]::IsNullOrWhiteSpace([string]$_)
} | Select-Object -Unique)
$closeoutBlocked = (-not $failed) -and (-not $PlanOnly) -and ($closeoutBlockingStatuses.Count -gt 0)

$report = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "scene_closeout_gate"
    tool_version = "0.1.0"
    project_root = $ProjectRoot
    scene_id = $SceneId
    target_scene = if ($TargetScene -ge 0) { $TargetScene } else { $null }
    plan_only = [bool]$PlanOnly
    warn_only = [bool]$WarnOnly
    status = if ($failed) { "failed" } elseif ($PlanOnly) { "planned" } elseif ($closeoutBlocked) { "blocked" } else { "ok" }
    summary = [ordered]@{
        steps_total = $executed.Count
        planned = @($executed | Where-Object { $_.status -eq "planned" }).Count
        succeeded = @($executed | Where-Object { $_.status -eq "ok" }).Count
        failed = @($executed | Where-Object { $_.status -eq "failed" }).Count
        warnings = @($executed | Where-Object { $_.status -eq "warning" }).Count
        skipped = @($executed | Where-Object { $_.status -eq "skipped" }).Count
        blocked = if ($closeoutBlocked) { 1 } else { 0 }
        validation_report_readable = [bool]$validationReportReadable
        validation_blocking_statuses = @($validationBlockingStatuses)
        closeout_blocking_statuses = @($closeoutBlockingStatuses)
        res_graph_vram_status = $resGraphVramStatus
        res_graph_vram_overlap_count = $resGraphVramOverlapCount
    }
    steps = @($executed)
    observed_artifacts = [ordered]@{
        validation_report = if (Test-Path -LiteralPath $validationReportPath) { $validationReportPath } else { $null }
        freshness_audit_report = if (Test-Path -LiteralPath $freshnessReportPath) { $freshnessReportPath } else { $null }
        res_graph_report = if (Test-Path -LiteralPath $resGraphReportPath) { $resGraphReportPath } else { $null }
        scene_regression_report = if (Test-Path -LiteralPath $sceneRegressionReportPath) { $sceneRegressionReportPath } else { $null }
        runtime_metrics = if (Test-Path -LiteralPath $runtimeMetricsPath) { $runtimeMetricsPath } else { $null }
        rom = if (Test-Path -LiteralPath (Join-Path $ProjectRoot "out\rom.bin")) { (Join-Path $ProjectRoot "out\rom.bin") } else { $null }
    }
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
Write-Host ("[CLOSEOUT] status={0} report={1}" -f $report.status, $ReportPath)

if (($failed -or $closeoutBlocked) -and -not $WarnOnly) {
    exit 1
}
exit 0

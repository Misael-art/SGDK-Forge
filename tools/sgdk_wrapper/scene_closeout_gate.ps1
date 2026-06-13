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
    [switch]$PlanOnly,

    [Parameter(Mandatory = $false)]
    [string]$ReportPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$libDir = Join-Path $PSScriptRoot 'lib'
$modulePath = Join-Path $libDir 'sgdk_artifact_contracts.psm1'
if (Test-Path -LiteralPath $modulePath -PathType Leaf) {
    Import-Module $modulePath -Force
}

$script:ToolName = 'scene_closeout_gate'
$script:ToolVersion = '0.2.0'
$script:WrittenOk = $false
$script:FailureMessage = ''
$script:ExitCode = 1
$previousCloseoutBuilding = $null

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = (Get-Location).Path
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$script:FallbackProjectRoot = $ProjectRoot

if (Get-Command Resolve-SgdkArtifactReportPath -ErrorAction SilentlyContinue) {
    $script:FallbackReportPath = Resolve-SgdkArtifactReportPath -ToolName $script:ToolName -ProjectRoot $ProjectRoot -ExplicitPath $ReportPath
} else {
    $script:FallbackReportPath = if ([string]::IsNullOrWhiteSpace($ReportPath)) { Join-Path $ProjectRoot 'out\logs\scene_closeout_gate_report.json' } else { $ReportPath }
}

try {
    if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
        throw "ProjectRoot not found: $ProjectRoot"
    }

    $ScriptRoot = $PSScriptRoot
    $LogDir = Join-Path $ProjectRoot "out\logs"
    if (-not (Test-Path -LiteralPath $LogDir -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    }
    $ReportPath = $script:FallbackReportPath
    $previousCloseoutBuilding = $env:SGDK_SCENE_CLOSEOUT_BUILDING
    $env:SGDK_SCENE_CLOSEOUT_BUILDING = "1"

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

function Get-SceneRegressionCloseoutIntent {
    param([Parameter(Mandatory = $true)][string]$Root)

    $manifestPath = Join-Path $Root "doc\scene-regression.json"
    $manifestSceneCount = 0
    $manifestRequired = $false
    if (Test-Path -LiteralPath $manifestPath -PathType Leaf) {
        try {
            $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($manifest.PSObject.Properties.Name -contains "scenes") {
                $manifestSceneCount = @($manifest.scenes).Count
            }
            if ($manifest.PSObject.Properties.Name -contains "required") {
                $manifestRequired = [bool]$manifest.required
            }
        } catch {
            $manifestRequired = $true
        }
    }

    $projectJsonPath = Join-Path $Root ".mddev\project.json"
    $projectSceneCount = 0
    $projectRequired = $false
    if (Test-Path -LiteralPath $projectJsonPath -PathType Leaf) {
        try {
            $projectJson = Get-Content -LiteralPath $projectJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($projectJson.PSObject.Properties.Name -contains "scene_regression" -and $projectJson.scene_regression) {
                if ($projectJson.scene_regression.PSObject.Properties.Name -contains "scenes") {
                    $projectSceneCount = @($projectJson.scene_regression.scenes).Count
                }
                if ($projectJson.scene_regression.PSObject.Properties.Name -contains "required") {
                    $projectRequired = [bool]$projectJson.scene_regression.required
                }
            }
        } catch {
            $projectRequired = $true
        }
    }

    return [ordered]@{
        required = [bool]($manifestRequired -or $projectRequired)
        scene_count = [int]($manifestSceneCount + $projectSceneCount)
        manifest_path = $manifestPath
        project_json_path = $projectJsonPath
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
$sceneRegressionIntent = Get-SceneRegressionCloseoutIntent -Root $ProjectRoot
$sceneRegressionExpected = [bool]($sceneRegressionIntent.required -or $sceneRegressionIntent.scene_count -gt 0)

if (-not $SkipBuild) {
    $buildBat = Join-Path $ProjectRoot "build.bat"
    if (Test-Path -LiteralPath $buildBat -PathType Leaf) {
        [void]$steps.Add((New-Step -Name "build" -Kind "build" -Command "cmd.exe" -Arguments @("/c", $buildBat) -Required $true))
    } else {
        [void]$steps.Add((New-Step -Name "build" -Kind "build" -Command "cmd.exe" -Arguments @("/c", (Join-Path $ScriptRoot "build.bat"), $ProjectRoot) -Required $true))
    }
}

[void]$steps.Add((New-Step -Name "scene_contract_compiler" -Kind "contract" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "scene_contract_compiler.ps1"), "-ProjectRoot", $ProjectRoot, "-Mode", "production") -Required $true))

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
    if ($sceneRegressionExpected -or $PlanOnly) {
        $regressionArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "run_scene_regression.ps1"), "-ProjectRoot", $ProjectRoot)
        if (-not [string]::IsNullOrWhiteSpace($SceneId)) {
            $regressionArgs += @("-SceneId", $SceneId)
        }
        if ($WarnOnly) {
            $regressionArgs += @("-WarnOnly")
        }
        [void]$steps.Add((New-Step -Name "scene_regression" -Kind "emulator" -Command "powershell.exe" -Arguments $regressionArgs -Required $true))
        [void]$steps.Add((New-Step -Name "validate_resources_after_scene_regression" -Kind "validation" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "validate_resources.ps1"), "-WorkDir", $ProjectRoot) -Required $true))
    } else {
        $step = New-Step -Name "scene_regression" -Kind "emulator" -Command "powershell.exe" -Arguments @() -Required $false
        $step.status = "skipped"
        $step.skipped_reason = "No scene-regression scenes declared"
        [void]$steps.Add($step)
    }
}

[void]$steps.Add((New-Step -Name "freshness_audit" -Kind "freshness" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "freshness_audit.ps1"), "-ProjectRoot", $ProjectRoot) -Required $true))

[void]$steps.Add((New-Step -Name "validate_resources_final" -Kind "validation" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "validate_resources.ps1"), "-WorkDir", $ProjectRoot) -Required $true))

[void]$steps.Add((New-Step -Name "project_learning_capture" -Kind "learning" -Command "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $ScriptRoot "audit_project_learning.ps1"), "-ProjectRoot", $ProjectRoot, "-Mode", "Capture", "-OutputFormat", "Json") -Required $true))

$executed = New-Object System.Collections.ArrayList
$failed = $false
$reportFailureStep = ''
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
        $reportFailureStep = $result.name
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
            $codeLoadedStatus = ""
            if ($resGraphReport.vram.PSObject.Properties.Name -contains "code_loaded_tiles" -and $resGraphReport.vram.code_loaded_tiles) {
                $codeLoadedStatus = [string]$resGraphReport.vram.code_loaded_tiles.status
            }
            if ($resGraphVramStatus -eq "code_loaded_tiles_unmeasured" -or $codeLoadedStatus -eq "code_loaded_tiles_unmeasured") {
                $closeoutBlockingStatuses += "code_loaded_tiles_unmeasured"
            }
        }
    } catch {
        $closeoutBlockingStatuses += "res_graph_report_unreadable"
    }
}
if ((-not $PlanOnly) -and $TargetScene -ge 0 -and (Test-Path -LiteralPath $runtimeMetricsPath -PathType Leaf)) {
    try {
        $runtimeMetricsReport = Get-Content -LiteralPath $runtimeMetricsPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($runtimeMetricsReport.PSObject.Properties.Name -contains "scene_id") {
            $runtimeSceneId = [int]$runtimeMetricsReport.scene_id
            if ($runtimeSceneId -ne $TargetScene) {
                $closeoutBlockingStatuses += "runtime_target_scene_mismatch"
            }
        }
    } catch {
        $closeoutBlockingStatuses += "runtime_metrics_unreadable"
    }
}
if ((-not $PlanOnly) -and (Test-Path -LiteralPath $freshnessReportPath -PathType Leaf)) {
    try {
        $freshnessReport = Get-Content -LiteralPath $freshnessReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $freshnessStatus = if ($freshnessReport.PSObject.Properties.Name -contains "status") { [string]$freshnessReport.status } else { "" }
        $staleCount = 0
        if ($freshnessReport.PSObject.Properties.Name -contains "stale_count") {
            $staleCount = [int]$freshnessReport.stale_count
        } elseif ($freshnessReport.PSObject.Properties.Name -contains "summary" -and $freshnessReport.summary.PSObject.Properties.Name -contains "stale_count") {
            $staleCount = [int]$freshnessReport.summary.stale_count
        }
        if ($freshnessStatus -and $freshnessStatus.ToLowerInvariant() -notin @("ok", "passed", "pass")) {
            $closeoutBlockingStatuses += "freshness_audit_stale"
        }
        if ($staleCount -gt 0) {
            $closeoutBlockingStatuses += "freshness_audit_stale"
        }
    } catch {
        $closeoutBlockingStatuses += "freshness_audit_unreadable"
    }
}
if ((-not $PlanOnly) -and $sceneRegressionExpected -and (Test-Path -LiteralPath $sceneRegressionReportPath -PathType Leaf)) {
    try {
        $sceneRegressionReport = Get-Content -LiteralPath $sceneRegressionReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $sceneResults = @()
        if ($sceneRegressionReport.PSObject.Properties.Name -contains "results") {
            $sceneResults = @($sceneRegressionReport.results)
        }
        if ($sceneResults.Count -eq 0) {
            $closeoutBlockingStatuses += "scene_regression_results_missing"
        }
        foreach ($sceneResult in $sceneResults) {
            if ($null -eq $sceneResult) { continue }
            $resultStatus = ([string]$sceneResult.status).ToLowerInvariant()
            if ($resultStatus -in @("missing", "baseline_missing", "no_baseline")) {
                $closeoutBlockingStatuses += "scene_regression_baseline_missing"
            } elseif ($resultStatus -and $resultStatus -notin @("passed", "ok")) {
                $closeoutBlockingStatuses += "scene_regression_failed"
            }
            $baselinePath = if ($sceneResult.PSObject.Properties.Name -contains "baseline_path") { [string]$sceneResult.baseline_path } else { "" }
            if ([string]::IsNullOrWhiteSpace($baselinePath) -or -not (Test-Path -LiteralPath $baselinePath)) {
                $closeoutBlockingStatuses += "scene_regression_baseline_missing"
            }
        }
    } catch {
        $closeoutBlockingStatuses += "scene_regression_report_unreadable"
    }
}
$closeoutBlockingStatuses += @($validationBlockingStatuses)
$closeoutBlockingStatuses = @($closeoutBlockingStatuses | Where-Object {
    $null -ne $_ -and -not [string]::IsNullOrWhiteSpace([string]$_)
} | Select-Object -Unique)
$closeoutBlocked = (-not $failed) -and (-not $PlanOnly) -and ($closeoutBlockingStatuses.Count -gt 0)

    $workspaceRoot = if ($env:MD_ROOT) { $env:MD_ROOT } else { 'UNKNOWN' }
    $closeoutRawStatus = if ($failed) { "failed" } elseif ($PlanOnly) { "planned" } elseif ($closeoutBlocked) { "blocked" } else { "ok" }
    $commonStatus = if ($failed) { "error" } elseif ($closeoutBlocked) { if ($WarnOnly) { "warn" } else { "error" } } else { "ok" }
    $failureReason = if ($failed) { "Closeout failed at step: $($reportFailureStep)" } elseif ($closeoutBlocked) { "Blocked by: $($closeoutBlockingStatuses -join '; ')" } else { $null }

    $report = [ordered]@{
        schema_version = "1.0.0"
        generated_at = (Get-Date).ToUniversalTime().ToString("o")
        tool_name = $script:ToolName
        tool_version = $script:ToolVersion
        project_root = $ProjectRoot
        workspace_root = $workspaceRoot
        status = $commonStatus
        failure_reason = $failureReason
        closeout_status = $closeoutRawStatus
        scene_id = $SceneId
        target_scene = if ($TargetScene -ge 0) { $TargetScene } else { $null }
        plan_only = [bool]$PlanOnly
        warn_only = [bool]$WarnOnly
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

    $reportParent = Split-Path $ReportPath -Parent
    if (-not [string]::IsNullOrWhiteSpace($reportParent) -and -not (Test-Path -LiteralPath $reportParent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $reportParent | Out-Null
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
    $script:WrittenOk = $true
    Write-Host ("[CLOSEOUT] status={0} report={1}" -f $report.status, $ReportPath)

    if ($failed) {
        $script:ExitCode = 1
    } elseif ($closeoutBlocked -and -not $WarnOnly) {
        $script:ExitCode = 1
    } else {
        $script:ExitCode = 0
    }
} catch {
    $script:FailureMessage = $_.Exception.Message
    $script:ExitCode = 1
    Write-Host ("[CLOSEOUT] UNHANDLED EXCEPTION: {0}" -f $script:FailureMessage)
} finally {
    if ($null -eq $previousCloseoutBuilding) {
        Remove-Item Env:\SGDK_SCENE_CLOSEOUT_BUILDING -ErrorAction SilentlyContinue
    } else {
        $env:SGDK_SCENE_CLOSEOUT_BUILDING = $previousCloseoutBuilding
    }
    if (-not $script:WrittenOk) {
        $domain = @{
            closeout_status = 'error'
            scene_id = $SceneId
            plan_only = [bool]$PlanOnly
        }
        $reason = if ([string]::IsNullOrWhiteSpace($script:FailureMessage)) { 'Unknown scene closeout failure.' } else { $script:FailureMessage }
        Write-SgdkFallbackFailureArtifact -ReportPath $script:FallbackReportPath -ToolName $script:ToolName -ToolVersion $script:ToolVersion -ProjectRoot $script:FallbackProjectRoot -FailureReason $reason -DomainData $domain
    }
    exit $script:ExitCode
}

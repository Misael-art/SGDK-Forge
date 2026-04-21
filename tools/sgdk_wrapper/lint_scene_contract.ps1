<#
.SYNOPSIS
    Validates a project's scene contract manifest against schema and semantic rules.
.DESCRIPTION
    Standalone linter for the AAA agent ecosystem. Reads doc/scene-contracts.json,
    checks structural validity, asset existence, and enforces rules based on the
    chosen rigor mode (lab/production/aaa_gate).

    This script does NOT modify any existing wrapper behavior.
    It writes only to out/logs/scene_contract_report.json.
.PARAMETER ProjectRoot
    Absolute path to the project root directory.
.PARAMETER ContractPath
    Absolute path to the scene-contracts.json. Defaults to <ProjectRoot>/doc/scene-contracts.json.
.PARAMETER Mode
    Rigor level: lab (relaxed), production (standard), aaa_gate (strict). Default: lab.
.PARAMETER WarnOnly
    If set, all errors are downgraded to warnings and exit code is 0.
.EXAMPLE
    .\lint_scene_contract.ps1 -ProjectRoot "C:\Projects\MyGame"
.EXAMPLE
    .\lint_scene_contract.ps1 -ProjectRoot "C:\Projects\MyGame" -Mode production
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [string]$ContractPath,
    [ValidateSet('lab', 'production', 'aaa_gate')]
    [string]$Mode = 'lab',
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ToolVersion = '0.1.0'

# ---------------------------------------------------------------------------
# Import modules
# ---------------------------------------------------------------------------
$libDir = Join-Path $PSScriptRoot 'lib'
Import-Module (Join-Path $libDir 'sgdk_artifact_contracts.psm1') -Force

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path

if ([string]::IsNullOrWhiteSpace($ContractPath)) {
    $ContractPath = Join-Path $ProjectRoot 'doc\scene-contracts.json'
}

$workspaceRoot = $PSScriptRoot
for ($i = 0; $i -lt 5; $i++) {
    $workspaceRoot = Split-Path $workspaceRoot -Parent
    if (Test-Path (Join-Path $workspaceRoot 'CLAUDE.md')) { break }
}

# ---------------------------------------------------------------------------
# Initialize report
# ---------------------------------------------------------------------------
$report = New-SgdkArtifactEnvelope `
    -ToolName 'lint_scene_contract' `
    -ToolVersion $ToolVersion `
    -ProjectRoot $ProjectRoot `
    -WorkspaceRoot $workspaceRoot

$report['mode'] = $Mode
$report['contract_path'] = $ContractPath
$report['scenes_checked'] = 0
$report['total_findings'] = 0
$report['scene_statuses'] = @{}
$report['findings'] = @()

$logsDir = Join-Path $ProjectRoot 'out\logs'
$reportPath = Join-Path $logsDir 'scene_contract_report.json'

$findings = [System.Collections.ArrayList]::new()

# ---------------------------------------------------------------------------
# Helper: add finding
# ---------------------------------------------------------------------------
function Add-Finding {
    param(
        [string]$SceneId,
        [string]$Severity,
        [string]$Code,
        [string]$Message,
        [string]$RelatedPath = $null
    )
    $f = [ordered]@{
        scene_id     = $SceneId
        severity     = $Severity
        code         = $Code
        message      = $Message
        related_path = $RelatedPath
    }
    [void]$findings.Add($f)
}

# ---------------------------------------------------------------------------
# Load and parse contract
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $ContractPath)) {
    Add-Finding '_manifest' 'error' 'SC001' "Contract file not found: $ContractPath" $ContractPath
    $report['findings'] = @($findings.ToArray())
    $report['total_findings'] = $findings.Count
    Set-SgdkArtifactFailure -Artifact $report -Reason 'Contract file not found' -Warn:$WarnOnly
    Write-SgdkJsonArtifact -Data $report -Path $reportPath | Out-Null
    Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] Contract file not found: $ContractPath"
    Write-Host "[INFO]  Report: $reportPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

try {
    $contractRaw = Get-Content -LiteralPath $ContractPath -Raw -Encoding UTF8
    $contract = $contractRaw | ConvertFrom-Json
} catch {
    Add-Finding '_manifest' 'error' 'SC002' "Invalid JSON in contract: $($_.Exception.Message)" $ContractPath
    $report['findings'] = @($findings.ToArray())
    $report['total_findings'] = $findings.Count
    Set-SgdkArtifactFailure -Artifact $report -Reason 'Invalid JSON' -Warn:$WarnOnly
    Write-SgdkJsonArtifact -Data $report -Path $reportPath | Out-Null
    Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] Invalid JSON: $ContractPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

# ---------------------------------------------------------------------------
# Validate manifest-level fields
# ---------------------------------------------------------------------------
if (-not $contract.PSObject.Properties['schema_version']) {
    Add-Finding '_manifest' 'error' 'SC003' 'Missing required field: schema_version'
}

if (-not $contract.PSObject.Properties['project_profile']) {
    Add-Finding '_manifest' 'warn' 'SC004' 'Missing field: project_profile. Defaulting to lab.'
}

$validProfiles = @('lab', 'production', 'aaa_gate')
if ($contract.PSObject.Properties['project_profile'] -and $contract.project_profile -notin $validProfiles) {
    Add-Finding '_manifest' 'error' 'SC005' "Invalid project_profile: '$($contract.project_profile)'. Must be one of: $($validProfiles -join ', ')"
}

if (-not $contract.PSObject.Properties['scenes']) {
    Add-Finding '_manifest' 'error' 'SC006' 'Missing required field: scenes'
    $report['findings'] = @($findings.ToArray())
    $report['total_findings'] = $findings.Count
    Set-SgdkArtifactFailure -Artifact $report -Reason 'Missing scenes array' -Warn:$WarnOnly
    Write-SgdkJsonArtifact -Data $report -Path $reportPath | Out-Null
    Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] Missing scenes array in contract"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

# ---------------------------------------------------------------------------
# Validate each scene
# ---------------------------------------------------------------------------
$validRoles = @('menu', 'title', 'gameplay', 'boss', 'cutscene', 'lab', 'debug', 'benchmark')
$validBootModes = @('debug_menu', 'sram_bootstrap', 'runtime_flag', 'direct_boot', 'unsupported')
$sceneIds = @{}
$sceneStatuses = @{}

foreach ($scene in $contract.scenes) {
    $sid = if ($scene.PSObject.Properties['scene_id']) { $scene.scene_id } else { '_unknown' }

    # SC010: scene_id required and valid
    if (-not $scene.PSObject.Properties['scene_id'] -or [string]::IsNullOrWhiteSpace($scene.scene_id)) {
        Add-Finding $sid 'error' 'SC010' 'Missing or empty scene_id'
        $sceneStatuses[$sid] = 'error'
        continue
    }

    if ($sid -notmatch '^[a-z0-9_]+$') {
        Add-Finding $sid 'error' 'SC011' "Invalid scene_id format: '$sid'. Must match ^[a-z0-9_]+$"
        $sceneStatuses[$sid] = 'error'
        continue
    }

    # SC012: duplicate scene_id
    if ($sceneIds.ContainsKey($sid)) {
        Add-Finding $sid 'error' 'SC012' "Duplicate scene_id: '$sid'"
        $sceneStatuses[$sid] = 'error'
        continue
    }
    $sceneIds[$sid] = $true

    $sceneSeverity = 'ok'

    # SC020: scene_role
    if (-not $scene.PSObject.Properties['scene_role']) {
        Add-Finding $sid 'error' 'SC020' 'Missing required field: scene_role'
        $sceneSeverity = 'error'
    } elseif ($scene.scene_role -notin $validRoles) {
        Add-Finding $sid 'error' 'SC021' "Invalid scene_role: '$($scene.scene_role)'. Must be one of: $($validRoles -join ', ')"
        $sceneSeverity = 'error'
    }

    # SC030: boot_mode
    if (-not $scene.PSObject.Properties['boot_mode']) {
        Add-Finding $sid 'error' 'SC030' 'Missing required field: boot_mode'
        $sceneSeverity = 'error'
    } elseif ($scene.boot_mode -notin $validBootModes) {
        Add-Finding $sid 'error' 'SC031' "Invalid boot_mode: '$($scene.boot_mode)'. Must be one of: $($validBootModes -join ', ')"
        $sceneSeverity = 'error'
    }

    # SC040: effects require warmup_frames
    if ($scene.PSObject.Properties['effects_active'] -and @($scene.effects_active).Count -gt 0) {
        if (-not $scene.PSObject.Properties['warmup_frames'] -or $scene.warmup_frames -le 0) {
            $sev = if ($Mode -eq 'lab') { 'warn' } else { 'error' }
            Add-Finding $sid $sev 'SC040' "Scene has active effects ($(@($scene.effects_active) -join ', ')) but no warmup_frames declared"
            if ($sev -eq 'error') { $sceneSeverity = 'error' } elseif ($sceneSeverity -ne 'error') { $sceneSeverity = 'warn' }
        }
    }

    # SC050: visual state changes require cleanup
    $stateChangingRoles = @('gameplay', 'boss', 'cutscene', 'benchmark')
    if ($scene.PSObject.Properties['scene_role'] -and $scene.scene_role -in $stateChangingRoles) {
        if (-not $scene.PSObject.Properties['cleanup_required'] -or $scene.cleanup_required -ne $true) {
            $sev = if ($Mode -eq 'aaa_gate') { 'error' } else { 'warn' }
            Add-Finding $sid $sev 'SC050' "Scene role '$($scene.scene_role)' should declare cleanup_required=true"
            if ($sev -eq 'error') { $sceneSeverity = 'error' } elseif ($sceneSeverity -ne 'error') { $sceneSeverity = 'warn' }
        }
    }

    # SC060: critical scenes need regression baseline (production and aaa_gate)
    if ($Mode -in @('production', 'aaa_gate')) {
        $criticalRoles = @('gameplay', 'boss', 'title')
        if ($scene.PSObject.Properties['scene_role'] -and $scene.scene_role -in $criticalRoles) {
            if (-not $scene.PSObject.Properties['regression_required'] -or $scene.regression_required -ne $true) {
                $sev = if ($Mode -eq 'aaa_gate') { 'error' } else { 'warn' }
                Add-Finding $sid $sev 'SC060' "Critical scene '$sid' (role: $($scene.scene_role)) should declare regression_required=true in '$Mode' mode"
                if ($sev -eq 'error') { $sceneSeverity = 'error' } elseif ($sceneSeverity -ne 'error') { $sceneSeverity = 'warn' }
            }
        }
    }

    # SC070: required_assets must exist
    if ($scene.PSObject.Properties['required_assets'] -and @($scene.required_assets).Count -gt 0) {
        foreach ($asset in $scene.required_assets) {
            $assetPath = Join-Path $ProjectRoot $asset
            if (-not (Test-Path -LiteralPath $assetPath)) {
                Add-Finding $sid 'warn' 'SC070' "Required asset not found: $asset" $assetPath
                if ($sceneSeverity -ne 'error') { $sceneSeverity = 'warn' }
            }
        }
    }

    # SC080: capture_frame should be set for scenes with regression
    if ($scene.PSObject.Properties['regression_required'] -and $scene.regression_required -eq $true) {
        if (-not $scene.PSObject.Properties['capture_frame']) {
            $sev = if ($Mode -eq 'aaa_gate') { 'error' } else { 'warn' }
            Add-Finding $sid $sev 'SC080' "Scene requires regression but has no capture_frame defined"
            if ($sev -eq 'error') { $sceneSeverity = 'error' } elseif ($sceneSeverity -ne 'error') { $sceneSeverity = 'warn' }
        }
    }

    # SC090: unsupported boot_mode
    if ($scene.PSObject.Properties['boot_mode'] -and $scene.boot_mode -eq 'unsupported') {
        $sceneStatuses[$sid] = 'unsupported'
        Add-Finding $sid 'info' 'SC090' "Scene has boot_mode=unsupported, skipping further deterministic checks"
        continue
    }

    $sceneStatuses[$sid] = $sceneSeverity
}

# ---------------------------------------------------------------------------
# Finalize report
# ---------------------------------------------------------------------------
$report['scenes_checked'] = $sceneIds.Count
$report['total_findings'] = $findings.Count
$report['scene_statuses'] = $sceneStatuses
$report['findings'] = @($findings.ToArray())

$hasErrors = @($findings | Where-Object { $_.severity -eq 'error' }).Count -gt 0
$hasWarnings = @($findings | Where-Object { $_.severity -eq 'warn' }).Count -gt 0

if ($hasErrors) {
    if ($WarnOnly) {
        $report['status'] = 'warn'
        $report['failure_reason'] = "$($findings.Count) finding(s), including errors downgraded to warnings"
    } else {
        $report['status'] = 'error'
        $report['failure_reason'] = "$($findings.Count) finding(s) with errors"
    }
} elseif ($hasWarnings) {
    $report['status'] = 'warn'
    $report['failure_reason'] = "$($findings.Count) finding(s) with warnings"
} else {
    $report['status'] = 'ok'
}

Write-SgdkJsonArtifact -Data $report -Path $reportPath | Out-Null

# Summary output
$errCount = @($findings | Where-Object { $_.severity -eq 'error' }).Count
$warnCount = @($findings | Where-Object { $_.severity -eq 'warn' }).Count
$infoCount = @($findings | Where-Object { $_.severity -eq 'info' }).Count

Write-Host "[$($report['status'].ToString().ToUpper())] Scene contract lint: $($sceneIds.Count) scene(s), $($findings.Count) finding(s) [E:$errCount W:$warnCount I:$infoCount] mode=$Mode"
Write-Host "[INFO]  Report: $reportPath"

foreach ($f in $findings) {
    $prefix = switch ($f.severity) {
        'error' { '[ERROR]' }
        'warn'  { '[WARN] ' }
        default { '[INFO] ' }
    }
    Write-Host "  $prefix [$($f.code)] $($f.scene_id): $($f.message)"
}

if ($hasErrors -and -not $WarnOnly) { exit 1 }
exit 0

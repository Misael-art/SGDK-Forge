<#
.SYNOPSIS
    Validates an active_iteration.json artifact against its schema and its
    memory-bank anchor, without blocking on a stale anchor.
.DESCRIPTION
    Checks required fields and causal vocabulary from active_iteration.schema.json,
    then verifies the recorded memory_bank_hash against the current SHA-256 of the
    project doc/10-memory-bank.md. A hash divergence is reported as status
    'stale_anchor' (warn, exit 0). Schema violation or missing file is an error.

    This script NEVER affects the build pipeline. It fails only in its own exit
    code, never in build.bat or run.bat.
.PARAMETER SchemaPath
    Absolute path to active_iteration.schema.json.
.PARAMETER ArtifactPath
    Absolute path to the active_iteration.json artifact to validate.
.PARAMETER MemoryBankPath
    Optional absolute path to the project doc/10-memory-bank.md used as anchor.
    When omitted, no anchor check runs.
.PARAMETER WarnOnly
    If set, schema validation failures become warnings instead of fatal exit codes.
.EXAMPLE
    .\validate_active_iteration.ps1 -SchemaPath .\schemas\active_iteration.schema.json ^
        -ArtifactPath .\SGDK_projects\MARE_BRAVA [VER.001]\doc\active_iteration.json ^
        -MemoryBankPath .\SGDK_projects\MARE_BRAVA [VER.001]\doc\10-memory-bank.md
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SchemaPath,
    [Parameter(Mandatory)][string]$ArtifactPath,
    [string]$MemoryBankPath,
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-ValidationResult {
    param([string]$Severity, [string]$Message)
    $prefix = switch ($Severity) {
        'ERROR' { '[ERROR]' }
        'WARN'  { '[WARN] ' }
        'OK'    { '[OK]   ' }
        default { '[INFO] ' }
    }
    Write-Host "$prefix $Message"
}

if (-not (Test-Path -LiteralPath $SchemaPath)) {
    Write-ValidationResult 'ERROR' "Schema file not found: $SchemaPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}
if (-not (Test-Path -LiteralPath $ArtifactPath)) {
    Write-ValidationResult 'ERROR' "Artifact file not found: $ArtifactPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

try {
    $artifactRaw = Get-Content -LiteralPath $ArtifactPath -Raw -Encoding UTF8
    $artifact = $artifactRaw | ConvertFrom-Json
} catch {
    Write-ValidationResult 'ERROR' "Artifact is not valid JSON: $($_.Exception.Message)"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

try {
    $schemaRaw = Get-Content -LiteralPath $SchemaPath -Raw -Encoding UTF8
    $schema = $schemaRaw | ConvertFrom-Json
} catch {
    Write-ValidationResult 'ERROR' "Schema is not valid JSON: $($_.Exception.Message)"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

$errors = @()
$warnings = @()

# ---------------------------------------------------------------------------
# Required fields + specific checks
# ---------------------------------------------------------------------------
$requiredFields = @($schema.required)
foreach ($field in $requiredFields) {
    if (-not $artifact.PSObject.Properties[$field]) {
        $errors += "Missing required field: '$field'"
    }
}

# Causal vocabulary: delta_status vs cause consistency
$deltaStatus = $artifact.delta_status
$cause = $artifact.cause
if (($deltaStatus -eq 'no_change' -or $deltaStatus -eq 'regressed') -and (-not $cause)) {
    $warnings += "delta_status='$deltaStatus' without a cause; classify the failure to advance the loop"
}
if ($deltaStatus -eq 'pending' -and $cause) {
    $warnings += "delta_status='pending' but cause is set; cause should be cleared until measured"
}
if ($null -ne $artifact.evidence_after -and $deltaStatus -eq 'pending') {
    $warnings += "evidence_after is set but delta_status='pending'; measurement may not have been recorded"
}
if ($deltaStatus -eq 'pending' -and $null -eq $artifact.evidence_before) {
    $warnings += "delta_status='pending' without evidence_before; a delta requires a before state"
}

# status='closed' requires stop_reason
if ($artifact.status -eq 'closed' -and (-not $artifact.PSObject.Properties['stop_reason'] -or -not $artifact.stop_reason)) {
    $errors += "status='closed' requires a stop_reason"
}

# ---------------------------------------------------------------------------
# Anchor check (non-blocking)
# ---------------------------------------------------------------------------
$staleAnchor = $false
if ($MemoryBankPath -and (Test-Path -LiteralPath $MemoryBankPath)) {
    $hash = (Get-FileHash -LiteralPath $MemoryBankPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $recordedHash = $artifact.memory_bank_hash
    if ($recordedHash -and ($recordedHash -ne $hash)) {
        $staleAnchor = $true
        $warnings += "memory_bank_hash diverges: recorded=$recordedHash current=$hash -> stale_anchor"
    } elseif (-not $recordedHash) {
        $warnings += "artifact has no memory_bank_hash to compare against -> stale_anchor"
    }
}

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
$artifactName = Split-Path $ArtifactPath -Leaf

if ($errors.Count -eq 0) {
    Write-ValidationResult 'OK' "Artifact '$artifactName' passes schema validation ($($requiredFields.Count) required fields checked)"
    foreach ($w in $warnings) { Write-ValidationResult 'WARN' $w }
    if ($staleAnchor) {
        Write-ValidationResult 'WARN' "Artifact '$artifactName' anchor is stale (report only, non-blocking)"
    }
    exit 0
} else {
    foreach ($err in $errors) {
        $sev = if ($WarnOnly) { 'WARN' } else { 'ERROR' }
        Write-ValidationResult $sev $err
    }
    foreach ($w in $warnings) { Write-ValidationResult 'WARN' $w }
    Write-ValidationResult $(if ($WarnOnly) { 'WARN' } else { 'ERROR' }) "Artifact '$artifactName' has $($errors.Count) validation issue(s)"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

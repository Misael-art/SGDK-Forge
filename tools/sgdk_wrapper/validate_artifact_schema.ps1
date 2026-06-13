<#
.SYNOPSIS
    Validates a JSON artifact against its expected schema structure.
.DESCRIPTION
    Standalone validation script for AAA ecosystem artifacts.
    Checks required fields from common_artifact.schema.json and
    optional tool-specific required fields from a given schema.

    This script NEVER affects the build pipeline.
    It fails only in its own exit code, never in build.bat or run.bat.
.PARAMETER SchemaPath
    Absolute path to the JSON schema file.
.PARAMETER ArtifactPath
    Absolute path to the JSON artifact to validate.
.PARAMETER WarnOnly
    If set, validation failures produce warnings instead of error exit codes.
.EXAMPLE
    .\validate_artifact_schema.ps1 -SchemaPath .\schemas\blastem_evidence.schema.json -ArtifactPath .\out\logs\blastem_evidence.json
.EXAMPLE
    .\validate_artifact_schema.ps1 -SchemaPath .\schemas\common_artifact.schema.json -ArtifactPath .\out\logs\test.json -WarnOnly
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SchemaPath,
    [Parameter(Mandatory)][string]$ArtifactPath,
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Load files
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Validate required fields
# ---------------------------------------------------------------------------
$errors = @()
$warnings = @()

# Check required fields from schema
$requiredFields = @()
if ($schema.PSObject.Properties['required']) {
    $requiredFields = @($schema.required)
}

foreach ($field in $requiredFields) {
    if (-not $artifact.PSObject.Properties[$field]) {
        $errors += "Missing required field: '$field'"
    }
}

# ---------------------------------------------------------------------------
# Validate field types from schema properties
# ---------------------------------------------------------------------------
if ($schema.PSObject.Properties['properties']) {
    foreach ($prop in $schema.properties.PSObject.Properties) {
        $fieldName = $prop.Name
        $fieldSpec = $prop.Value

        # Skip if field not present and not required
        if (-not $artifact.PSObject.Properties[$fieldName]) { continue }

        $value = $artifact.$fieldName

        # Check enum constraints
        if ($fieldSpec.PSObject.Properties['enum'] -and $null -ne $value) {
            $allowed = @($fieldSpec.enum)
            if ($value -notin $allowed) {
                $errors += "Field '$fieldName' has value '$value' not in allowed values: $($allowed -join ', ')"
            }
        }

        # Check pattern constraints on strings
        if ($fieldSpec.PSObject.Properties['pattern'] -and $null -ne $value -and $value -is [string]) {
            $pat = $fieldSpec.pattern
            if ($value -notmatch $pat) {
                $errors += "Field '$fieldName' value '$value' does not match pattern '$pat'"
            }
        }

        # Check schema_version specifically
        if ($fieldName -eq 'schema_version' -and $null -ne $value) {
            if ($value -notmatch '^\d+\.\d+\.\d+$') {
                $errors += "Field 'schema_version' must be semver format (got: '$value')"
            }
        }
    }
}

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
$artifactName = Split-Path $ArtifactPath -Leaf

if ($errors.Count -eq 0) {
    Write-ValidationResult 'OK' "Artifact '$artifactName' passes schema validation ($($requiredFields.Count) required fields checked)"
    exit 0
} else {
    foreach ($err in $errors) {
        $sev = if ($WarnOnly) { 'WARN' } else { 'ERROR' }
        Write-ValidationResult $sev $err
    }
    Write-ValidationResult $(if ($WarnOnly) { 'WARN' } else { 'ERROR' }) "Artifact '$artifactName' has $($errors.Count) validation issue(s)"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

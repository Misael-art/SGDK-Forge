<#
.SYNOPSIS
    Validates the opt-in fighting_2d_traditional specialization: manifest, design
    contract, moveset frame data files, and phase-aware blockers.

.DESCRIPTION
    Canonical top-level validator for the genre specialization fighting_2d_traditional.

    Behavior contract (locked):
      * When doc/genre_specialization_manifest.json is ABSENT, the project is
        generalista. Validator exits ok with manifest_status=absent and a stub
        report. No genre blocker is raised.
      * When present, the validator validates the manifest, the
        fighting_2d_design_contract.json, every referenced moveset frame data
        file, and emits a phase-aware blocker audit.
      * Phase is read from doc/project_methodology_manifest.json
        (claim_ceiling). vertical_slice never trips phase_aware_blockers.
      * Phase-aware blockers (registry-driven):
          - fighting_training_mode_missing_for_product
          - fighting_lore_moveset_unbound
          - fighting_balance_evidence_missing

    This script NEVER affects the build pipeline.
    It fails only via exit code, never via build.bat or run.bat.

.PARAMETER ProjectRoot
    Absolute path to the project root directory.

.PARAMETER OutputPath
    Absolute path to write the JSON report. Defaults to
    <ProjectRoot>/out/logs/fighting_specialization_report.json.

.EXAMPLE
    .\validate_fighting_specialization.ps1 -ProjectRoot F:\Projects\MyFighter
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory = $false)][string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TOOL_NAME = "validate_fighting_specialization.ps1"
$TOOL_VERSION = "1.0.0"
$SPECIALIZATION_ID = "fighting_2d_traditional"
$REGISTRY_PATH_DEFAULT = "doc/07_game_design/genre_specialization_registry.json"
$MANIFEST_PATH_DEFAULT = "doc/genre_specialization_manifest.json"

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$wrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "tools\sgdk_wrapper"))
$wrapperRootAlt = [System.IO.Path]::GetFullPath((Join-Path (Split-Path $PSScriptRoot -Parent) ""))
# script lives at tools/sgdk_wrapper/validate_fighting_specialization.ps1
$wrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ""))
$schemasDir = Join-Path $wrapperRoot "schemas"
$registryDefault = Join-Path (Split-Path $wrapperRoot -Parent) $REGISTRY_PATH_DEFAULT

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $logsDir = Join-Path $ProjectRoot "out\logs"
    if (-not (Test-Path -LiteralPath $logsDir)) {
        New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    }
    $OutputPath = Join-Path $logsDir "fighting_specialization_report.json"
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Write-Log {
    param([string]$Severity, [string]$Message)
    $prefix = switch ($Severity) {
        'ERROR' { '[ERROR]' }
        'WARN'  { '[WARN] ' }
        'OK'    { '[OK]   ' }
        'INFO'  { '[INFO] ' }
        default { '[INFO] ' }
    }
    Write-Host "$prefix $Message"
}

function Read-JsonObject {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        return ($raw | ConvertFrom-Json)
    } catch {
        Write-Log 'ERROR' "Invalid JSON in $Path : $($_.Exception.Message)"
        return $null
    }
}

function Get-RequiredString {
    param($Obj, [string]$Field)
    if ($null -eq $Obj) { return $null }
    if (-not $Obj.PSObject.Properties[$Field]) { return $null }
    $v = $Obj.$Field
    if ($null -eq $v) { return $null }
    if ($v -is [string] -and [string]::IsNullOrWhiteSpace($v)) { return $null }
    return $v
}

# ---------------------------------------------------------------------------
# JSON Schema-lite validator (top-level + per-array-item)
#   - Recursively checks required fields and enum/pattern/type constraints
#   - Not a full Draft-07 implementation; sufficient for the 5 schemas of this
#     specialization. Always rejects unknown top-level required fields.
# ---------------------------------------------------------------------------
function Test-JsonSchema {
    param($Instance, $Schema, [string]$Path = '$')

    $errors = @()
    if ($null -eq $Schema) { return $errors }
    if (-not $Schema.PSObject.Properties['type']) { return $errors }
    $type = $Schema.type

    if ($type -eq 'object') {
        if ($null -ne $Instance -and $Instance -isnot [System.Management.Automation.PSCustomObject] -and $Instance -isnot [hashtable]) {
            $errors += "$Path : expected object, got $($Instance.GetType().FullName)"
            return $errors
        }
        $instanceObj = $Instance
        if ($null -eq $instanceObj) {
            $errors += "$Path : expected object, got null"
            return $errors
        }
        if ($Schema.PSObject.Properties['required']) {
            foreach ($req in $Schema.required) {
                if (-not $instanceObj.PSObject.Properties[$req]) {
                    $errors += "$Path : missing required field '$req'"
                }
            }
        }
        if ($Schema.PSObject.Properties['properties'] -and $instanceObj) {
            foreach ($prop in $Schema.properties.PSObject.Properties) {
                $fieldName = $prop.Name
                $fieldSpec = $prop.Value
                if (-not $instanceObj.PSObject.Properties[$fieldName]) { continue }
                $value = $instanceObj.$fieldName
                $sub = $Path + '.' + $fieldName
                $errors += Test-JsonSchema -Instance $value -Schema $fieldSpec -Path $sub
            }
        }
        if ($Schema.PSObject.Properties['additionalProperties'] -and $Schema.additionalProperties -eq $false -and $Schema.PSObject.Properties['properties'] -and $instanceObj) {
            foreach ($field in $instanceObj.PSObject.Properties) {
                if (-not $Schema.properties.PSObject.Properties[$field.Name]) {
                    $errors += "$Path : unknown property '$($field.Name)'"
                }
            }
        }
    }
    elseif ($type -eq 'array') {
        if ($null -eq $Instance) {
            $errors += "$Path : expected array, got null"
            return $errors
        }
        if ($Instance -isnot [System.Array] -and $Instance -isnot [System.Collections.IList] -and $Instance -isnot [System.Collections.Generic.List[Object]]) {
            $errors += "$Path : expected array"
            return $errors
        }
        if ($Schema.PSObject.Properties['minItems']) {
            if ($Instance.Count -lt $Schema.minItems) {
                $errors += "$Path : array has $($Instance.Count) items, minItems=$($Schema.minItems)"
            }
        }
        if ($Schema.PSObject.Properties['maxItems']) {
            if ($Instance.Count -gt $Schema.maxItems) {
                $errors += "$Path : array has $($Instance.Count) items, maxItems=$($Schema.maxItems)"
            }
        }
        if ($Schema.PSObject.Properties['items']) {
            for ($i = 0; $i -lt $Instance.Count; $i++) {
                $errors += Test-JsonSchema -Instance $Instance[$i] -Schema $Schema.items -Path "$Path[$i]"
            }
        }
    }
    elseif ($type -eq 'string') {
        if ($null -eq $Instance) {
            $errors += "$Path : expected string, got null"
            return $errors
        }
        if ($Instance -isnot [string]) {
            $errors += "$Path : expected string, got $($Instance.GetType().FullName)"
            return $errors
        }
        if ($Schema.PSObject.Properties['pattern']) {
            if ($Instance -notmatch $Schema.pattern) {
                $errors += "$Path : value '$Instance' does not match pattern '$($Schema.pattern)'"
            }
        }
        if ($Schema.PSObject.Properties['const']) {
            if ($Instance -ne $Schema.const) {
                $errors += "$Path : value '$Instance' != const '$($Schema.const)'"
            }
        }
        if ($Schema.PSObject.Properties['minLength']) {
            if ($Instance.Length -lt $Schema.minLength) {
                $errors += "$Path : length $($Instance.Length) < minLength $($Schema.minLength)"
            }
        }
    }
    elseif ($type -eq 'integer') {
        if ($null -eq $Instance) {
            $errors += "$Path : expected integer, got null"
            return $errors
        }
        if ($Instance -isnot [int] -and $Instance -isnot [long]) {
            $errors += "$Path : expected integer, got $($Instance.GetType().FullName)"
            return $errors
        }
        if ($Schema.PSObject.Properties['minimum']) {
            if ($Instance -lt $Schema.minimum) { $errors += "$Path : $Instance < minimum $($Schema.minimum)" }
        }
    }
    elseif ($type -eq 'boolean') {
        if ($null -eq $Instance) {
            $errors += "$Path : expected boolean, got null"
            return $errors
        }
        if ($Instance -isnot [bool]) {
            $errors += "$Path : expected boolean, got $($Instance.GetType().FullName)"
        }
    }

    # enum applies to any single-valued field
    if ($Schema.PSObject.Properties['enum'] -and $null -ne $Instance) {
        $allowed = @($Schema.enum)
        if (($Instance -is [string] -or $Instance -is [int] -or $Instance -is [long]) -and $allowed -notcontains $Instance) {
            $errors += "$Path : value '$Instance' not in enum ($($allowed -join ', '))"
        }
    }

    return $errors
}

# ---------------------------------------------------------------------------
# Phase resolution
# ---------------------------------------------------------------------------
function Get-ProjectPhase {
    param([string]$ProjectRoot)
    $methodology = Read-JsonObject -Path (Join-Path $ProjectRoot "doc\project_methodology_manifest.json")
    if ($null -eq $methodology) { return "vertical_slice" }
    $ceiling = Get-RequiredString -Obj $methodology -Field "claim_ceiling"
    switch ($ceiling) {
        "ready_for_aaa" { return "ready_for_aaa" }
        "closeout" { return "closeout" }
        default { return "vertical_slice" }
    }
}

# ---------------------------------------------------------------------------
# Phase-aware blocker evaluation
# ---------------------------------------------------------------------------
$REQUIRED_FRAME_FIELDS = @(
    "startup_frames",
    "active_frames",
    "recovery_frames",
    "on_hit_advantage_frames",
    "on_block_advantage_frames"
)

function Test-PhaseBlockers {
    param(
        $Manifest, $DesignContract, $MovesetAudits, $Phase
    )

    $blockers = @()

    # 1. training_mode_missing_for_product (ready_for_aaa/closeout)
    $trainingFired = $false
    $trainingEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['modes']) {
        $hasTraining = $false
        foreach ($m in $DesignContract.modes) {
            if ($m.PSObject.Properties['kind'] -and $m.kind -eq 'training') {
                $hasTraining = $true
                if ($m.PSObject.Properties['training_features']) {
                    $trainingEvidence = "training mode declared with features"
                } else {
                    $trainingEvidence = "training mode declared but no training_features"
                }
                break
            }
        }
        if (-not $hasTraining) { $trainingEvidence = "no training mode in design contract" }
        $trainingFired = (-not $hasTraining)
    }
    $blockers += @{
        blocker_id = "fighting_training_mode_missing_for_product"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $trainingFired
        evidence = $trainingEvidence
    }

    # 2. lore_moveset_unbound (ready_for_aaa/closeout)
    $unboundFired = $false
    $unboundEvidence = "all characters bound"
    foreach ($audit in $MovesetAudits) {
        if ($audit.schema_status -in @("error", "absent")) {
            $unboundFired = $true
            $unboundEvidence = "unbound character: $($audit.character_id) (status=$($audit.schema_status))"
            break
        }
    }
    $blockers += @{
        blocker_id = "fighting_lore_moveset_unbound"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $unboundFired
        evidence = $unboundEvidence
    }

    # 3. balance_evidence_missing (ready_for_aaa/closeout)
    $balanceFired = $false
    $balanceEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['balance']) {
        $balance = $DesignContract.balance
        $hasMethod = $balance.PSObject.Properties['method'] -and $null -ne $balance.method
        $hasEvidence = $false
        $missingFiles = @()
        if ($balance.PSObject.Properties['evidence_paths']) {
            foreach ($p in $balance.evidence_paths) {
                $resolved = Join-Path $ProjectRoot $p
                if (Test-Path -LiteralPath $resolved) { $hasEvidence = $true } else { $missingFiles += $p }
            }
        }
        $balanceFired = (-not $hasMethod) -or (-not $hasEvidence)
        $balanceEvidence = if ($balanceFired) {
            if (-not $hasMethod) { "balance.method missing" }
            elseif ($missingFiles.Count -gt 0) { "missing evidence files: $($missingFiles -join ', ')" }
            else { "balance evidence missing" }
        } else { "balance method and evidence present" }
    }
    $blockers += @{
        blocker_id = "fighting_balance_evidence_missing"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $balanceFired
        evidence = $balanceEvidence
    }

    return $blockers
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
$manifestPath = Join-Path $ProjectRoot $MANIFEST_PATH_DEFAULT
$manifest = Read-JsonObject -Path $manifestPath

$phase = Get-ProjectPhase -ProjectRoot $ProjectRoot

# Case 1: no manifest -> generalista
if ($null -eq $manifest) {
    Write-Log 'INFO' "No genre specialization manifest at $manifestPath - project is generalista."
    $report = [ordered]@{
        schema_version = "1.0.0"
        project = @{ name = (Split-Path $ProjectRoot -Leaf) }
        generated_at = (Get-Date).ToString("o")
        tool_name = $TOOL_NAME
        tool_version = $TOOL_VERSION
        status = "ok"
        specialization_id = $SPECIALIZATION_ID
        registry_source = $REGISTRY_PATH_DEFAULT
        manifest_path = $MANIFEST_PATH_DEFAULT
        manifest_status = "absent"
        design_contract_path = ""
        design_contract_status = "absent"
        moveset_audits = @()
        blockers = @()
        summary = @{ passed = 1; warned = 0; failed = 0; notes = "generalista path" }
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Log 'OK' "Validator OK (generalista). Report: $OutputPath"
    exit 0
}

# Case 2: manifest present -> validate
Write-Log 'INFO' "Manifest found at $manifestPath - validating $SPECIALIZATION_ID."

$manifestSchema = Read-JsonObject -Path (Join-Path $schemasDir "genre_specialization_manifest.schema.json")
$designSchema = Read-JsonObject -Path (Join-Path $schemasDir "fighting_2d_design_contract.schema.json")
$movesetSchema = Read-JsonObject -Path (Join-Path $schemasDir "fighting_moveset_frame_data.schema.json")
$reportSchema = Read-JsonObject -Path (Join-Path $schemasDir "fighting_specialization_report.schema.json")

$failed = 0
$warned = 0
$passed = 0

# Validate manifest
$manifestErrors = @()
if ($null -eq $manifestSchema) {
    $manifestErrors += "manifest schema not loaded"
} else {
    $manifestErrors = @(Test-JsonSchema -Instance $manifest -Schema $manifestSchema -Path '$.manifest')
}
if ($manifestErrors.Count -gt 0) {
    Write-Log 'ERROR' "Manifest invalid: $($manifestErrors.Count) issue(s)"
    foreach ($e in $manifestErrors) { Write-Log 'ERROR' "  $e" }
    $failed += @($manifestErrors).Count
} else {
    Write-Log 'OK' "Manifest schema valid"
    $passed++
}

$manifestStatus = if ($manifestErrors.Count -gt 0) { "invalid" } else { "present" }

# Validate design contract (path from manifest)
$designContractPath = ""
$designContract = $null
$designContractStatus = "absent"
$designContractErrors = @()
if ($manifest.PSObject.Properties['active_specializations'] -and @($manifest.active_specializations).Count -gt 0) {
    $first = @($manifest.active_specializations)[0]
    $designContractPath = Get-RequiredString -Obj $first -Field "design_contract_path"
    if ($designContractPath) {
        $absDesignPath = Join-Path $ProjectRoot $designContractPath
        $designContract = Read-JsonObject -Path $absDesignPath
        if ($null -eq $designContract) {
            $designContractStatus = "invalid"
            $designContractErrors += "design contract not parseable at $absDesignPath"
        } elseif ($null -eq $designSchema) {
            $designContractStatus = "invalid"
            $designContractErrors += "design contract schema not loaded"
        } else {
            $designContractErrors = @(Test-JsonSchema -Instance $designContract -Schema $designSchema -Path '$.design_contract')
            if ($designContractErrors.Count -gt 0) {
                $designContractStatus = "invalid"
            } else {
                $designContractStatus = "present"
            }
        }
    } else {
        $designContractStatus = "absent"
        $designContractErrors += "manifest declares no design_contract_path"
    }
}

if ($designContractErrors.Count -gt 0) {
    Write-Log 'ERROR' "Design contract invalid: $($designContractErrors.Count) issue(s)"
    foreach ($e in $designContractErrors) { Write-Log 'ERROR' "  $e" }
    $failed += @($designContractErrors).Count
} else {
    Write-Log 'OK' "Design contract schema valid"
    $passed++
}

# Validate each moveset frame data file
$movesetAudits = @()
if ($null -ne $designContract -and $designContract.PSObject.Properties['roster'] -and $designContract.roster.PSObject.Properties['characters']) {
    foreach ($char in $designContract.roster.characters) {
        $charId = Get-RequiredString -Obj $char -Field "id"
        $charRole = Get-RequiredString -Obj $char -Field "role"
        $movesetRelPath = Get-RequiredString -Obj $char -Field "moveset_frame_data_path"
        $audit = [ordered]@{
            character_id = $charId
            role = $charRole
            path = $movesetRelPath
            schema_status = "absent"
            missing_required_frame_fields = @()
        }
        if ($movesetRelPath) {
            $absMovesetPath = Join-Path $ProjectRoot $movesetRelPath
            $moveset = Read-JsonObject -Path $absMovesetPath
            if ($null -eq $moveset) {
                $audit.schema_status = "error"
                $audit.missing_required_frame_fields = @("file_unreadable")
                $failed++
            } else {
                $movesetErrors = @()
                if ($null -ne $movesetSchema) {
                    $movesetErrors = @(Test-JsonSchema -Instance $moveset -Schema $movesetSchema -Path '$.moveset')
                }
                if ($movesetErrors.Count -gt 0) {
                    $audit.schema_status = "error"
                    $audit.missing_required_frame_fields = @($movesetErrors)
                    $failed += @($movesetErrors).Count
                    foreach ($e in $movesetErrors) { Write-Log 'ERROR' "  moveset[$charId]: $e" }
                } else {
                    # For primary characters, verify frame data presence on non-system/movement moves
                    $missingFields = @()
                    if ($charRole -eq "primary" -and $moveset.PSObject.Properties['moves']) {
                        foreach ($mv in $moveset.moves) {
                            $cat = Get-RequiredString -Obj $mv -Field "category"
                            if ($cat -notin @("system", "movement")) {
                                foreach ($rf in $REQUIRED_FRAME_FIELDS) {
                                    if (-not $mv.PSObject.Properties[$rf]) {
                                        $missingFields += $rf
                                    }
                                }
                            }
                        }
                    }
                    if ($missingFields.Count -gt 0) {
                        $audit.schema_status = "warn"
                        $audit.missing_required_frame_fields = @($missingFields | Select-Object -Unique)
                        $warned += $missingFields.Count
                        Write-Log 'WARN' "moveset[$charId] primary missing frame fields: $(@($missingFields | Select-Object -Unique) -join ', ')"
                    } else {
                        $audit.schema_status = "ok"
                        $passed++
                        Write-Log 'OK' "moveset[$charId] valid ($charRole)"
                    }
                }
            }
        } else {
            $audit.schema_status = "absent"
            $audit.missing_required_frame_fields = @("path_missing")
            $failed++
        }
        $movesetAudits += $audit
    }
}

# Phase-aware blockers
$blockers = Test-PhaseBlockers -Manifest $manifest -DesignContract $designContract -MovesetAudits $movesetAudits -Phase $phase
foreach ($b in $blockers) {
    if ($b.fired) {
        Write-Log 'ERROR' "Blocker $($b.blocker_id) FIRED: $($b.evidence)"
        $failed++
    } else {
        Write-Log 'OK' "Blocker $($b.blocker_id) dormant ($($b.evidence))"
        $passed++
    }
}

# Validate report itself against its own schema (sanity)
$report = [ordered]@{
    schema_version = "1.0.0"
    project = @{ name = (Split-Path $ProjectRoot -Leaf) }
    generated_at = (Get-Date).ToString("o")
    tool_name = $TOOL_NAME
    tool_version = $TOOL_VERSION
    status = if ($failed -gt 0) { "error" } elseif ($warned -gt 0) { "warn" } else { "ok" }
    specialization_id = $SPECIALIZATION_ID
    registry_source = $REGISTRY_PATH_DEFAULT
    manifest_path = $MANIFEST_PATH_DEFAULT
    manifest_status = $manifestStatus
    design_contract_path = $designContractPath
    design_contract_status = $designContractStatus
    moveset_audits = $movesetAudits
    blockers = $blockers
    summary = @{
        passed = $passed
        warned = $warned
        failed = $failed
        notes = "phase=$phase"
    }
}

if ($null -ne $reportSchema) {
    $reportErrors = @(Test-JsonSchema -Instance $report -Schema $reportSchema -Path '$.report')
    if ($reportErrors.Count -gt 0) {
        Write-Log 'ERROR' "Report self-validation failed: $($reportErrors.Count) issue(s)"
        foreach ($e in $reportErrors) { Write-Log 'ERROR' "  $e" }
    }
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8

Write-Log 'INFO' "Report: $OutputPath"
Write-Log 'INFO' "Summary: passed=$passed warned=$warned failed=$failed"

if ($failed -gt 0) {
    Write-Log 'ERROR' "Validator FAILED for $SPECIALIZATION_ID"
    exit 1
}
Write-Log 'OK' "Validator OK for $SPECIALIZATION_ID"
exit 0

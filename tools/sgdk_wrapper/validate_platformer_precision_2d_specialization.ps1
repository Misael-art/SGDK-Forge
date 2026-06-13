<#
.SYNOPSIS
    Validates the opt-in platformer_precision_2d specialization: manifest,
    design contract, level segment frame data files, and phase-aware blockers.

.DESCRIPTION
    Canonical top-level validator for the genre specialization platformer_precision_2d.

    Behavior contract (locked):
      * When doc/genre_specialization_manifest.json is ABSENT, the project is
        generalista. Validator exits ok with manifest_status=absent.
      * When present, validates manifest, design contract, every referenced
        level segment frame data file, and emits phase-aware blocker audit.
      * Phase is read from doc/project_methodology_manifest.json (claim_ceiling).
        vertical_slice never trips phase_aware_blockers.
      * Phase-aware blockers (registry-driven):
          - platformer_coyote_time_overflow
          - metroidvania_ability_unlock_path (sub-rule: precision 2d has no
            abilities, so this triggers only if designer adds them)
          - puzzle_undo_count_unbounded (sub-rule: precision 2d has no undo)

    This script NEVER affects the build pipeline.

.PARAMETER ProjectRoot
    Absolute path to the project root directory.

.PARAMETER OutputPath
    Absolute path to write the JSON report.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory = $false)][string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TOOL_NAME = "validate_platformer_precision_2d_specialization.ps1"
$TOOL_VERSION = "1.0.0"
$SPECIALIZATION_ID = "platformer_precision_2d"
$REGISTRY_PATH_DEFAULT = "doc/07_game_design/genre_specialization_registry.json"
$MANIFEST_PATH_DEFAULT = "doc/genre_specialization_manifest.json"
$COYOTE_TIME_MAX = 6
$JUMP_BUFFER_MAX = 6

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$wrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ""))
$schemasDir = Join-Path $wrapperRoot "schemas"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $logsDir = Join-Path $ProjectRoot "out\logs"
    if (-not (Test-Path -LiteralPath $logsDir)) {
        New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    }
    $OutputPath = Join-Path $logsDir "platformer_specialization_report.json"
}

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
        if ($null -eq $instanceObj) { $errors += "$Path : expected object, got null"; return $errors }
        if ($Schema.PSObject.Properties['required']) {
            foreach ($req in $Schema.required) {
                if (-not $instanceObj.PSObject.Properties[$req]) { $errors += "$Path : missing required field '$req'" }
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
        if ($null -eq $Instance) { $errors += "$Path : expected array, got null"; return $errors }
        if ($Instance -isnot [System.Array] -and $Instance -isnot [System.Collections.IList] -and $Instance -isnot [System.Collections.Generic.List[Object]]) {
            $errors += "$Path : expected array"
        }
        if ($Schema.PSObject.Properties['minItems'] -and $Instance.Count -lt $Schema.minItems) {
            $errors += "$Path : array has $($Instance.Count) items, minItems=$($Schema.minItems)"
        }
        if ($Schema.PSObject.Properties['maxItems'] -and $Instance.Count -gt $Schema.maxItems) {
            $errors += "$Path : array has $($Instance.Count) items, maxItems=$($Schema.maxItems)"
        }
        if ($Schema.PSObject.Properties['items']) {
            for ($i = 0; $i -lt $Instance.Count; $i++) {
                $errors += Test-JsonSchema -Instance $Instance[$i] -Schema $Schema.items -Path "$Path[$i]"
            }
        }
    }
    elseif ($type -eq 'string') {
        if ($null -eq $Instance) { $errors += "$Path : expected string, got null"; return $errors }
        if ($Instance -isnot [string]) { $errors += "$Path : expected string, got $($Instance.GetType().FullName)" }
        if ($Schema.PSObject.Properties['pattern'] -and $Instance -notmatch $Schema.pattern) { $errors += "$Path : value '$Instance' does not match pattern '$($Schema.pattern)'" }
        if ($Schema.PSObject.Properties['const'] -and $Instance -ne $Schema.const) { $errors += "$Path : value '$Instance' != const '$($Schema.const)'" }
        if ($Schema.PSObject.Properties['minLength'] -and $Instance.Length -lt $Schema.minLength) { $errors += "$Path : length $($Instance.Length) < minLength $($Schema.minLength)" }
    }
    elseif ($type -eq 'integer') {
        if ($null -eq $Instance) { $errors += "$Path : expected integer, got null"; return $errors }
        if ($Instance -isnot [int] -and $Instance -isnot [long]) { $errors += "$Path : expected integer, got $($Instance.GetType().FullName)" }
        if ($Schema.PSObject.Properties['minimum'] -and $Instance -lt $Schema.minimum) { $errors += "$Path : $Instance < minimum $($Schema.minimum)" }
        if ($Schema.PSObject.Properties['maximum'] -and $Instance -gt $Schema.maximum) { $errors += "$Path : $Instance > maximum $($Schema.maximum)" }
    }
    elseif ($type -eq 'boolean') {
        if ($null -eq $Instance) { $errors += "$Path : expected boolean, got null"; return $errors }
        if ($Instance -isnot [bool]) { $errors += "$Path : expected boolean, got $($Instance.GetType().FullName)" }
    }
    elseif ($type -eq 'number') {
        if ($null -eq $Instance) { $errors += "$Path : expected number, got null"; return $errors }
        if ($Instance -isnot [int] -and $Instance -isnot [long] -and $Instance -isnot [double] -and $Instance -isnot [decimal]) {
            $errors += "$Path : expected number, got $($Instance.GetType().FullName)"
        }
    }

    if ($Schema.PSObject.Properties['enum'] -and $null -ne $Instance) {
        $allowed = @($Schema.enum)
        if (($Instance -is [string] -or $Instance -is [int] -or $Instance -is [long]) -and $allowed -notcontains $Instance) {
            $errors += "$Path : value '$Instance' not in enum ($($allowed -join ', '))"
        }
    }

    return $errors
}

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

$REQUIRED_LAYOUT_FIELDS = @("width_tiles", "height_tiles", "tile_size_px", "gravity_zone_count")

function Test-PhaseBlockers {
    param(
        $Manifest, $DesignContract, $LevelAudits, $Phase
    )

    $blockers = @()

    # 1. platformer_coyote_time_overflow (ready_for_aaa/closeout)
    $coyoteFired = $false
    $coyoteEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['player_profile']) {
        $pp = $DesignContract.player_profile
        $coyote = if ($pp.PSObject.Properties['coyote_time_frames']) { [int]$pp.coyote_time_frames } else { 0 }
        $buffer = if ($pp.PSObject.Properties['jump_buffer_frames']) { [int]$pp.jump_buffer_frames } else { 0 }
        if ($coyote -gt $COYOTE_TIME_MAX) {
            $coyoteFired = $true
            $coyoteEvidence = "coyote_time_frames=$coyote > $COYOTE_TIME_MAX (breaks challenge)"
        } elseif ($buffer -gt $JUMP_BUFFER_MAX) {
            $coyoteFired = $true
            $coyoteEvidence = "jump_buffer_frames=$buffer > $JUMP_BUFFER_MAX (breaks challenge)"
        } else {
            $coyoteFired = $false
            $coyoteEvidence = "coyote_time_frames=$coyote, jump_buffer_frames=$buffer within cap"
        }
    }
    $blockers += @{
        blocker_id = "platformer_coyote_time_overflow"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $coyoteFired
        evidence = $coyoteEvidence
    }

    # 2. metroidvania_ability_unlock_path (sub-rule for precision_2d: no abilities)
    # In precision 2d, abilities are per-level (movement, combat, special, utility).
    # The blocker fires only if any ability has frames_active > 30 (special moves should
    # be short for precision genre).
    $abilityFired = $false
    $abilityEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['ability_set']) {
        $slowAbilities = @()
        foreach ($a in $DesignContract.ability_set) {
            $fa = if ($a.PSObject.Properties['frames_active']) { [int]$a.frames_active } else { 0 }
            if ($fa -gt 30) {
                $slowAbilities += "$($a.id):$fa"
            }
        }
        if ($slowAbilities.Count -gt 0) {
            $abilityFired = $true
            $abilityEvidence = "abilities with frames_active > 30: $($slowAbilities -join ', ')"
        } else {
            $abilityFired = $false
            $abilityEvidence = "all abilities have frames_active <= 30"
        }
    }
    $blockers += @{
        blocker_id = "metroidvania_ability_unlock_path"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $abilityFired
        evidence = $abilityEvidence
    }

    # 3. puzzle_undo_count_unbounded (sub-rule: precision 2d has no undo)
    # The blocker fires only if the design contract declares an undo field
    # (which it does not currently in this schema). The blocker is dormant
    # for precision_2d.
    $undoFired = $false
    $undoEvidence = "precision_2d has no undo system; this is a sub-rule for puzzle subgeneros (sokoban/tile-matching); dormant for $SPECIALIZATION_ID"
    $blockers += @{
        blocker_id = "puzzle_undo_count_unbounded"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $undoFired
        evidence = $undoEvidence
    }

    return $blockers
}

# MAIN
$manifestPath = Join-Path $ProjectRoot $MANIFEST_PATH_DEFAULT
$manifest = Read-JsonObject -Path $manifestPath
$phase = Get-ProjectPhase -ProjectRoot $ProjectRoot

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
        level_audits = @()
        blockers = @()
        summary = @{ passed = 1; warned = 0; failed = 0; notes = "generalista path" }
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Log 'OK' "Validator OK (generalista). Report: $OutputPath"
    exit 0
}

Write-Log 'INFO' "Manifest found at $manifestPath - validating $SPECIALIZATION_ID."

$manifestSchema = Read-JsonObject -Path (Join-Path $schemasDir "genre_specialization_manifest.schema.json")
$designSchema = Read-JsonObject -Path (Join-Path $schemasDir "platformer_precision_2d_design_contract.schema.json")
$levelSchema = Read-JsonObject -Path (Join-Path $schemasDir "platformer_level_segment_frame_data.schema.json")
$reportSchema = Read-JsonObject -Path (Join-Path $schemasDir "platformer_specialization_report.schema.json")

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

# Validate design contract
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

# Validate each level segment frame data file
$levelAudits = @()
if ($null -ne $designContract -and $designContract.PSObject.Properties['level_catalog']) {
    foreach ($lvl in $designContract.level_catalog) {
        $lId = Get-RequiredString -Obj $lvl -Field "level_id"
        $lRole = Get-RequiredString -Obj $lvl -Field "display_name"
        # Use "level_id" role fallback since schema doesn't have level_role per level
        $lRoleAudit = if ($lvl.PSObject.Properties['level_id']) { [string]$lvl.level_id } else { "unknown" }
        $lPath = Get-RequiredString -Obj $lvl -Field "level_segment_frame_data_path"
        $audit = [ordered]@{
            level_id = $lId
            level_role = $lRoleAudit
            path = $lPath
            schema_status = "absent"
            missing_required_layout_fields = @()
        }
        if ($lPath) {
            $absPath = Join-Path $ProjectRoot $lPath
            $lvlData = Read-JsonObject -Path $absPath
            if ($null -eq $lvlData) {
                $audit.schema_status = "error"
                $audit.missing_required_layout_fields = @("file_unreadable")
                $failed++
            } else {
                $lvlErrors = @()
                if ($null -ne $levelSchema) {
                    $lvlErrors = @(Test-JsonSchema -Instance $lvlData -Schema $levelSchema -Path '$.level_segment')
                }
                if ($lvlErrors.Count -gt 0) {
                    $audit.schema_status = "error"
                    $audit.missing_required_layout_fields = @($lvlErrors)
                    $failed += @($lvlErrors).Count
                    foreach ($e in $lvlErrors) { Write-Log 'ERROR' "  level[$lId]: $e" }
                } else {
                    $missing = @()
                    if ($lvlData.PSObject.Properties['layout']) {
                        foreach ($rf in $REQUIRED_LAYOUT_FIELDS) {
                            if (-not $lvlData.layout.PSObject.Properties[$rf]) { $missing += $rf }
                        }
                    } else {
                        $missing = @("layout_missing")
                    }
                    if ($missing.Count -gt 0) {
                        $audit.schema_status = "warn"
                        $audit.missing_required_layout_fields = @($missing | Select-Object -Unique)
                        $warned += $missing.Count
                        Write-Log 'WARN' "level[$lId] missing layout fields: $(@($missing | Select-Object -Unique) -join ', ')"
                    } else {
                        $audit.schema_status = "ok"
                        $passed++
                        Write-Log 'OK' "level[$lId] valid"
                    }
                }
            }
        } else {
            $audit.schema_status = "absent"
            $audit.missing_required_layout_fields = @("path_missing")
            $failed++
        }
        $levelAudits += $audit
    }
}

# Phase-aware blockers
$blockers = Test-PhaseBlockers -Manifest $manifest -DesignContract $designContract -LevelAudits $levelAudits -Phase $phase
foreach ($b in $blockers) {
    if ($b.fired) {
        Write-Log 'ERROR' "Blocker $($b.blocker_id) FIRED: $($b.evidence)"
        $failed++
    } else {
        Write-Host "  [OK]   Blocker $($b.blocker_id) dormant ($($b.evidence))"
        $passed++
    }
}

# Build report
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
    level_audits = $levelAudits
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

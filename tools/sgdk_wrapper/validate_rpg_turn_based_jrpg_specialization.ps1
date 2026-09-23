<#
.SYNOPSIS
    Validates the opt-in rpg_turn_based_jrpg specialization: manifest, design
    contract, party member frame data files, and phase-aware blockers.

.DESCRIPTION
    Canonical top-level validator for the genre specialization rpg_turn_based_jrpg.

    Behavior contract (locked):
      * When doc/genre_specialization_manifest.json is ABSENT, the project is
        generalista. Validator exits ok with manifest_status=absent and a stub
        report. No genre blocker is raised.
      * When present, the validator validates the manifest, the
        rpg_turn_based_jrpg_design_contract.json, every referenced party
        member frame data file, and emits a phase-aware blocker audit.
      * Phase is read from doc/project_methodology_manifest.json
        (claim_ceiling). vertical_slice never trips phase_aware_blockers.
      * Phase-aware blockers (registry-driven):
          - rpg_party_size_unbounded
          - rpg_encounter_resolution_ambiguous
          - rpg_save_corruption_risk

    This script NEVER affects the build pipeline.
    It fails only via exit code, never via build.bat or run.bat.

.PARAMETER ProjectRoot
    Absolute path to the project root directory.

.PARAMETER OutputPath
    Absolute path to write the JSON report. Defaults to
    <ProjectRoot>/out/logs/rpg_specialization_report.json.

.EXAMPLE
    .\validate_rpg_turn_based_jrpg_specialization.ps1 -ProjectRoot F:\Projects\MyJRPG
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory = $false)][string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TOOL_NAME = "validate_rpg_turn_based_jrpg_specialization.ps1"
$TOOL_VERSION = "1.0.0"
$SPECIALIZATION_ID = "rpg_turn_based_jrpg"
$REGISTRY_PATH_DEFAULT = "doc/07_game_design/genre_specialization_registry.json"
$MANIFEST_PATH_DEFAULT = "doc/genre_specialization_manifest.json"
$PARTY_SIZE_MAX = 4

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$wrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ""))
$schemasDir = Join-Path $wrapperRoot "schemas"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $logsDir = Join-Path $ProjectRoot "out\logs"
    if (-not (Test-Path -LiteralPath $logsDir)) {
        New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    }
    $OutputPath = Join-Path $logsDir "rpg_specialization_report.json"
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
# JSON Schema-lite validator (same as fighting; sufficient for our 4 RPG schemas)
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
        if ($Schema.PSObject.Properties['maximum']) {
            if ($Instance -gt $Schema.maximum) { $errors += "$Path : $Instance > maximum $($Schema.maximum)" }
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
$REQUIRED_BASE_STATS = @(
    "hp", "mp", "attack", "defense", "agility", "magic"
)

function Test-PhaseBlockers {
    param(
        $Manifest, $DesignContract, $PartyAudits, $Phase
    )

    $blockers = @()

    # 1. rpg_party_size_unbound (ready_for_aaa/closeout)
    $partyFired = $false
    $partyEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['party']) {
        $party = $DesignContract.party
        $size = 0
        $sizeOk = $false
        if ($party.PSObject.Properties['size']) {
            $size = [int]$party.size
            $sizeOk = ($size -ge 1 -and $size -le $PARTY_SIZE_MAX)
        }
        if ($sizeOk) {
            $partyEvidence = "party.size=$size within cap $PARTY_SIZE_MAX"
        } else {
            $partyEvidence = "party.size=$size outside cap $PARTY_SIZE_MAX"
        }
        $partyFired = -not $sizeOk
    }
    $blockers += @{
        blocker_id = "rpg_party_size_unbounded"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $partyFired
        evidence = $partyEvidence
    }

    # 2. rpg_encounter_resolution_ambiguous (ready_for_aaa/closeout)
    $encounterFired = $false
    $encounterEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['combat'] -and $DesignContract.PSObject.Properties['encounter_trigger']) {
        $combat = $DesignContract.combat
        $trigger = [string]$DesignContract.encounter_trigger
        $hasTurnOrder = $combat.PSObject.Properties['turn_order'] -and $combat.turn_order.PSObject.Properties['formula']
        $hasActionMenu = $combat.PSObject.Properties['action_menu'] -and $combat.action_menu.PSObject.Properties['actions'] -and @($combat.action_menu.actions).Count -ge 3
        if ($hasTurnOrder -and $hasActionMenu -and -not [string]::IsNullOrWhiteSpace($trigger)) {
            $encounterEvidence = "encounter_trigger=$trigger, turn_order.formula present, action_menu has >=3 actions"
            $encounterFired = $false
        } else {
            $encounterFired = $true
            $encounterEvidence = "ambiguous: trigger='$trigger' hasTurnOrder=$hasTurnOrder hasActionMenu=$hasActionMenu"
        }
    } else {
        $encounterFired = $true
        $encounterEvidence = "no combat or encounter_trigger in design contract"
    }
    $blockers += @{
        blocker_id = "rpg_encounter_resolution_ambiguous"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $encounterFired
        evidence = $encounterEvidence
    }

    # 3. rpg_save_corruption_risk (ready_for_aaa/closeout)
    # Heuristic: this fires if no modes declares save_model, or all modes use 'save_anywhere' without confirm.
    $saveFired = $false
    $saveEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['modes'] -and @($DesignContract.modes).Count -gt 0) {
        $hasSafeSave = $false
        $allAnywhere = $true
        foreach ($m in $DesignContract.modes) {
            $sm = Get-RequiredString -Obj $m -Field "save_model"
            if ($null -eq $sm) { $allAnywhere = $false; continue }
            if ($sm -ne "save_anywhere") { $hasSafeSave = $true; $allAnywhere = $false }
        }
        if ($hasSafeSave) {
            $saveEvidence = "at least one mode uses save_station or save_anywhere_with_confirm"
            $saveFired = $false
        } elseif ($allAnywhere) {
            $saveEvidence = "all modes use save_anywhere without confirm (corruption risk)"
            $saveFired = $true
        } else {
            $saveEvidence = "no mode declares save_model (corruption risk)"
            $saveFired = $true
        }
    } else {
        $saveFired = $true
        $saveEvidence = "no modes declared in design contract"
    }
    $blockers += @{
        blocker_id = "rpg_save_corruption_risk"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $saveFired
        evidence = $saveEvidence
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
        party_audits = @()
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
$designSchema = Read-JsonObject -Path (Join-Path $schemasDir "rpg_turn_based_jrpg_design_contract.schema.json")
$partySchema = Read-JsonObject -Path (Join-Path $schemasDir "rpg_party_frame_data.schema.json")
$reportSchema = Read-JsonObject -Path (Join-Path $schemasDir "rpg_specialization_report.schema.json")

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

# Validate each party member frame data file
$partyAudits = @()
if ($null -ne $designContract -and $designContract.PSObject.Properties['party'] -and $designContract.party.PSObject.Properties['members']) {
    foreach ($member in $designContract.party.members) {
        $memberId = Get-RequiredString -Obj $member -Field "id"
        $memberRole = Get-RequiredString -Obj $member -Field "role"
        $partyRelPath = Get-RequiredString -Obj $member -Field "party_frame_data_path"
        $audit = [ordered]@{
            member_id = $memberId
            role = $memberRole
            path = $partyRelPath
            schema_status = "absent"
            missing_required_base_stats = @()
        }
        if ($partyRelPath) {
            $absPartyPath = Join-Path $ProjectRoot $partyRelPath
            $partyData = Read-JsonObject -Path $absPartyPath
            if ($null -eq $partyData) {
                $audit.schema_status = "error"
                $audit.missing_required_base_stats = @("file_unreadable")
                $failed++
            } else {
                $partyErrors = @()
                if ($null -ne $partySchema) {
                    $partyErrors = @(Test-JsonSchema -Instance $partyData -Schema $partySchema -Path '$.party_frame_data')
                }
                if ($partyErrors.Count -gt 0) {
                    $audit.schema_status = "error"
                    $audit.missing_required_base_stats = @($partyErrors)
                    $failed += @($partyErrors).Count
                    foreach ($e in $partyErrors) { Write-Log 'ERROR' "  party[$memberId]: $e" }
                } else {
                    # For every member, verify base_stats presence (R: hp/mp/attack/defense/agility/magic)
                    $missingStats = @()
                    if ($partyData.PSObject.Properties['base_stats']) {
                        foreach ($bs in $REQUIRED_BASE_STATS) {
                            if (-not $partyData.base_stats.PSObject.Properties[$bs]) {
                                $missingStats += $bs
                            }
                        }
                    } else {
                        $missingStats = @("base_stats_missing")
                    }
                    if ($missingStats.Count -gt 0) {
                        $audit.schema_status = "warn"
                        $audit.missing_required_base_stats = @($missingStats | Select-Object -Unique)
                        $warned += $missingStats.Count
                        Write-Log 'WARN' "party[$memberId] missing base_stats fields: $(@($missingStats | Select-Object -Unique) -join ', ')"
                    } else {
                        $audit.schema_status = "ok"
                        $passed++
                        Write-Log 'OK' "party[$memberId] valid ($memberRole)"
                    }
                }
            }
        } else {
            $audit.schema_status = "absent"
            $audit.missing_required_base_stats = @("path_missing")
            $failed++
        }
        $partyAudits += $audit
    }
}

# Phase-aware blockers
$blockers = Test-PhaseBlockers -Manifest $manifest -DesignContract $designContract -PartyAudits $partyAudits -Phase $phase
foreach ($b in $blockers) {
    if ($b.fired) {
        Write-Log 'ERROR' "Blocker $($b.blocker_id) FIRED: $($b.evidence)"
        $failed++
    } else {
        Write-Log 'OK' "Blocker $($b.blocker_id) dormant ($($b.evidence))"
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
    party_audits = $partyAudits
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

<#
.SYNOPSIS
    Validates the opt-in strategy_tower_defense specialization: manifest,
    design contract, tower frame data files, and phase-aware blockers.

.DESCRIPTION
    Canonical top-level validator for the genre specialization strategy_tower_defense.

    Behavior contract (locked):
      * When doc/genre_specialization_manifest.json is ABSENT, the project is
        generalista. Validator exits ok with manifest_status=absent and a stub
        report. No genre blocker is raised.
      * When present, the validator validates the manifest, the
        strategy_tower_defense_design_contract.json, every referenced tower
        frame data file, and emits a phase-aware blocker audit.
      * Phase is read from doc/project_methodology_manifest.json
        (claim_ceiling). vertical_slice never trips phase_aware_blockers.
      * Phase-aware blockers (registry-driven):
          - strategy_grid_vram_overflow
          - strategy_unit_ap_unbounded
          - strategy_fog_of_war_race

    This script NEVER affects the build pipeline.
    It fails only via exit code, never via build.bat or run.bat.

.PARAMETER ProjectRoot
    Absolute path to the project root directory.

.PARAMETER OutputPath
    Absolute path to write the JSON report. Defaults to
    <ProjectRoot>/out/logs/strategy_specialization_report.json.

.EXAMPLE
    .\validate_strategy_tower_defense_specialization.ps1 -ProjectRoot F:\Projects\MyTD
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory = $false)][string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TOOL_NAME = "validate_strategy_tower_defense_specialization.ps1"
$TOOL_VERSION = "1.0.0"
$SPECIALIZATION_ID = "strategy_tower_defense"
$REGISTRY_PATH_DEFAULT = "doc/07_game_design/genre_specialization_registry.json"
$MANIFEST_PATH_DEFAULT = "doc/genre_specialization_manifest.json"
$TOWER_SLOTS_MAX = 24
$VRAM_BUDGET_MAX_KB = 64

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
    $OutputPath = Join-Path $logsDir "strategy_specialization_report.json"
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

# ---------------------------------------------------------------------------
# Phase-aware blocker evaluation
# ---------------------------------------------------------------------------
$REQUIRED_TIER_FIELDS = @(
    "tier_id", "tier_name", "cost", "damage", "range_tiles",
    "fire_rate_frames", "projectile_speed_tiles_per_second"
)

function Test-PhaseBlockers {
    param(
        $Manifest, $DesignContract, $TowerAudits, $Phase
    )

    $blockers = @()

    # 1. strategy_grid_vram_overflow (ready_for_aaa/closeout)
    $gridFired = $false
    $gridEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['grid_layout']) {
        $grid = $DesignContract.grid_layout
        $w = if ($grid.PSObject.Properties['width_tiles']) { [int]$grid.width_tiles } else { 0 }
        $h = if ($grid.PSObject.Properties['height_tiles']) { [int]$grid.height_tiles } else { 0 }
        $slotCount = if ($grid.PSObject.Properties['tower_slot_count']) { [int]$grid.tower_slot_count } else { 0 }
        $vramKb = if ($grid.PSObject.Properties['vram_budget_estimate_kb']) { [int]$grid.vram_budget_estimate_kb } else { 0 }
        $vramOk = ($vramKb -gt 0 -and $vramKb -le $VRAM_BUDGET_MAX_KB)
        $slotOk = ($slotCount -gt 0 -and $slotCount -le $TOWER_SLOTS_MAX)
        $sizeOk = ($w -ge 16 -and $w -le 64) -and ($h -ge 16 -and $h -le 64)
        if ($vramOk -and $slotOk -and $sizeOk) {
            $gridEvidence = "grid=${w}x${h}, slots=$slotCount, vram=${vramKb}KB within MD budget"
        } else {
            $gridEvidence = "overflow risk: grid=${w}x${h}, slots=$slotCount (cap=$TOWER_SLOTS_MAX), vram=${vramKb}KB (cap=${VRAM_BUDGET_MAX_KB}KB)"
        }
        $gridFired = -not ($vramOk -and $slotOk -and $sizeOk)
    }
    $blockers += @{
        blocker_id = "strategy_grid_vram_overflow"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $gridFired
        evidence = $gridEvidence
    }

    # 2. strategy_unit_ap_unbounded (ready_for_aaa/closeout)
    # In TD, no AP system. We check fire_rate_frames per tower (each must be >=6 to avoid CPU saturation).
    $apFired = $false
    $apEvidence = "no design contract"
    if ($null -ne $TowerAudits -and @($TowerAudits).Count -gt 0) {
        $hasUnsafe = $false
        $unsafeTowers = @()
        foreach ($audit in $TowerAudits) {
            if ($audit.schema_status -ne "ok") { continue }
            $absPath = Join-Path $ProjectRoot $audit.path
            $td = Read-JsonObject -Path $absPath
            if ($null -eq $td -or -not $td.PSObject.Properties['tiers']) { continue }
            foreach ($t in $td.tiers) {
                $fr = if ($t.PSObject.Properties['fire_rate_frames']) { [int]$t.fire_rate_frames } else { 0 }
                if ($fr -lt 6) { $hasUnsafe = $true; $unsafeTowers += "$($audit.tower_id):$fr" }
            }
        }
        if ($hasUnsafe) {
            $apFired = $true
            $apEvidence = "unsafe fire_rate (<6 frames) on towers: $($unsafeTowers -join ', ')"
        } else {
            $apFired = $false
            $apEvidence = "all towers have fire_rate_frames >= 6"
        }
    } else {
        $apEvidence = "no tower frame data audited yet"
    }
    $blockers += @{
        blocker_id = "strategy_unit_ap_unbounded"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $apFired
        evidence = $apEvidence
    }

    # 3. strategy_fog_of_war_race (ready_for_aaa/closeout)
    # In TD, fog of war is typically absent. We require the design contract to declare
    # wave_count and spawn_groups so VBlank-budget can be calculated.
    $fogFired = $false
    $fogEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['wave_composition']) {
        $wc = $DesignContract.wave_composition
        $waveCount = if ($wc.PSObject.Properties['wave_count']) { [int]$wc.wave_count } else { 0 }
        $hasWaves = $wc.PSObject.Properties['waves'] -and @($wc.waves).Count -ge 5
        if ($waveCount -ge 5 -and $hasWaves) {
            $fogEvidence = "wave_count=$waveCount, waves array has $((@($wc.waves)).Count) entries; VBlank-update feasible"
            $fogFired = $false
        } else {
            $fogFired = $true
            $fogEvidence = "wave_composition incomplete: wave_count=$waveCount, hasWaves=$hasWaves (min 5 waves required for VBlank-deterministic spawn)"
        }
    } else {
        $fogFired = $true
        $fogEvidence = "no wave_composition in design contract"
    }
    $blockers += @{
        blocker_id = "strategy_fog_of_war_race"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $fogFired
        evidence = $fogEvidence
    }

    return $blockers
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
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
        tower_audits = @()
        blockers = @()
        summary = @{ passed = 1; warned = 0; failed = 0; notes = "generalista path" }
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Log 'OK' "Validator OK (generalista). Report: $OutputPath"
    exit 0
}

Write-Log 'INFO' "Manifest found at $manifestPath - validating $SPECIALIZATION_ID."

$manifestSchema = Read-JsonObject -Path (Join-Path $schemasDir "genre_specialization_manifest.schema.json")
$designSchema = Read-JsonObject -Path (Join-Path $schemasDir "strategy_tower_defense_design_contract.schema.json")
$towerSchema = Read-JsonObject -Path (Join-Path $schemasDir "strategy_tower_frame_data.schema.json")
$reportSchema = Read-JsonObject -Path (Join-Path $schemasDir "strategy_specialization_report.schema.json")

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

# Validate each tower frame data file
$towerAudits = @()
if ($null -ne $designContract -and $designContract.PSObject.Properties['tower_catalog']) {
    foreach ($tower in $designContract.tower_catalog) {
        $towerId = Get-RequiredString -Obj $tower -Field "id"
        $towerCat = Get-RequiredString -Obj $tower -Field "category"
        $towerRelPath = Get-RequiredString -Obj $tower -Field "tower_frame_data_path"
        $audit = [ordered]@{
            tower_id = $towerId
            category = $towerCat
            path = $towerRelPath
            schema_status = "absent"
            missing_required_tier_fields = @()
        }
        if ($towerRelPath) {
            $absTowerPath = Join-Path $ProjectRoot $towerRelPath
            $towerData = Read-JsonObject -Path $absTowerPath
            if ($null -eq $towerData) {
                $audit.schema_status = "error"
                $audit.missing_required_tier_fields = @("file_unreadable")
                $failed++
            } else {
                $towerErrors = @()
                if ($null -ne $towerSchema) {
                    $towerErrors = @(Test-JsonSchema -Instance $towerData -Schema $towerSchema -Path '$.tower_frame_data')
                }
                if ($towerErrors.Count -gt 0) {
                    $audit.schema_status = "error"
                    $audit.missing_required_tier_fields = @($towerErrors)
                    $failed += @($towerErrors).Count
                    foreach ($e in $towerErrors) { Write-Log 'ERROR' "  tower[$towerId]: $e" }
                } else {
                    $missingFields = @()
                    if ($towerData.PSObject.Properties['tiers']) {
                        foreach ($tier in $towerData.tiers) {
                            foreach ($rf in $REQUIRED_TIER_FIELDS) {
                                if (-not $tier.PSObject.Properties[$rf]) { $missingFields += $rf }
                            }
                        }
                    } else {
                        $missingFields = @("tiers_missing")
                    }
                    if ($missingFields.Count -gt 0) {
                        $audit.schema_status = "warn"
                        $audit.missing_required_tier_fields = @($missingFields | Select-Object -Unique)
                        $warned += $missingFields.Count
                        Write-Log 'WARN' "tower[$towerId] missing tier fields: $(@($missingFields | Select-Object -Unique) -join ', ')"
                    } else {
                        $audit.schema_status = "ok"
                        $passed++
                        Write-Log 'OK' "tower[$towerId] valid ($towerCat)"
                    }
                }
            }
        } else {
            $audit.schema_status = "absent"
            $audit.missing_required_tier_fields = @("path_missing")
            $failed++
        }
        $towerAudits += $audit
    }
}

# Phase-aware blockers
$blockers = Test-PhaseBlockers -Manifest $manifest -DesignContract $designContract -TowerAudits $towerAudits -Phase $phase
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
    tower_audits = $towerAudits
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

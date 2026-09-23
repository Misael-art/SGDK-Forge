<#
.SYNOPSIS
    Validates the opt-in brawler_belt_scroll specialization: manifest,
    design contract, enemy archetype frame data files, and phase-aware blockers.

.DESCRIPTION
    Canonical top-level validator for the genre specialization brawler_belt_scroll.

    Behavior contract (locked):
      * When doc/genre_specialization_manifest.json is ABSENT, the project is
        generalista. Validator exits ok with manifest_status=absent.
      * When present, validates manifest, design contract, every referenced
        enemy archetype frame data file, and emits phase-aware blocker audit.
      * Phase is read from doc/project_methodology_manifest.json (claim_ceiling).
        vertical_slice never trips phase_aware_blockers.
      * Phase-aware blockers (registry-driven):
          - brawler_iframe_window_unsafe
          - brawler_pickup_drop_unbounded
          - brawler_wave_spawner_deterministic

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

$TOOL_NAME = "validate_brawler_belt_scroll_specialization.ps1"
$TOOL_VERSION = "1.0.0"
$SPECIALIZATION_ID = "brawler_belt_scroll"
$REGISTRY_PATH_DEFAULT = "doc/07_game_design/genre_specialization_registry.json"
$MANIFEST_PATH_DEFAULT = "doc/genre_specialization_manifest.json"
$ENEMY_ON_SCREEN_MAX = 8
$IFRAME_MIN_FRAMES = 8

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$wrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ""))
$schemasDir = Join-Path $wrapperRoot "schemas"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $logsDir = Join-Path $ProjectRoot "out\logs"
    if (-not (Test-Path -LiteralPath $logsDir)) {
        New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    }
    $OutputPath = Join-Path $logsDir "brawler_specialization_report.json"
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
        # DateKind String (PowerShell 7.5+) keeps ISO timestamps as strings so
        # schema "type: string" checks do not see System.DateTime instances.
        if ((Get-Command ConvertFrom-Json).Parameters.Keys -contains 'DateKind') {
            return ($raw | ConvertFrom-Json -DateKind String)
        }
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

$REQUIRED_BASE_STATS = @("hp", "damage", "move_speed_px_per_second", "score_reward", "hit_stun_frames")

function Test-PhaseBlockers {
    param(
        $Manifest, $DesignContract, $EnemyArchetypeAudits, $Phase
    )

    $blockers = @()

    # 1. brawler_iframe_window_unsafe (ready_for_aaa/closeout)
    $iframeFired = $false
    $iframeEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['player_roster']) {
        $unsafePlayers = @()
        foreach ($p in $DesignContract.player_roster) {
            $iframe = if ($p.PSObject.Properties['iframe_frames']) { [int]$p.iframe_frames } else { 0 }
            if ($iframe -lt $IFRAME_MIN_FRAMES) {
                $unsafePlayers += "$($p.id):$iframe"
            }
        }
        if ($unsafePlayers.Count -gt 0) {
            $iframeFired = $true
            $iframeEvidence = "unsafe iframe (<$IFRAME_MIN_FRAMES frames) on players: $($unsafePlayers -join ', ')"
        } else {
            $iframeFired = $false
            $iframeEvidence = "all players have iframe_frames >= $IFRAME_MIN_FRAMES"
        }
    }
    $blockers += @{
        blocker_id = "brawler_iframe_window_unsafe"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $iframeFired
        evidence = $iframeEvidence
    }

    # 2. brawler_pickup_drop_unbounded (ready_for_aaa/closeout)
    $pickupFired = $false
    $pickupEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['pickup_catalog']) {
        $unboundedPickups = @()
        foreach ($pickup in $DesignContract.pickup_catalog) {
            $chance = if ($pickup.PSObject.Properties['drop_chance_pct']) { [int]$pickup.drop_chance_pct } else { 0 }
            $maxOnScreen = if ($pickup.PSObject.Properties['max_on_screen']) { [int]$pickup.max_on_screen } else { 0 }
            if ($chance -gt 50 -and $maxOnScreen -gt 8) {
                $unboundedPickups += "$($pickup.id):chance=$chance,max=$maxOnScreen"
            }
        }
        if ($unboundedPickups.Count -gt 0) {
            $pickupFired = $true
            $pickupEvidence = "high drop + high cap on pickups: $($unboundedPickups -join ', ')"
        } else {
            $pickupFired = $false
            $pickupEvidence = "all pickups have chance<=50 or max_on_screen<=8"
        }
    }
    $blockers += @{
        blocker_id = "brawler_pickup_drop_unbounded"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $pickupFired
        evidence = $pickupEvidence
    }

    # 3. brawler_wave_spawner_deterministic (ready_for_aaa/closeout)
    # In belt-scroll, wave spawner is determined by stages[]: each stage has
    # wave_count>=2 AND boss_archetype_id must reference an enemy archetype
    # with archetype=boss in the enemy_archetypes array.
    $waveFired = $false
    $waveEvidence = "no design contract"
    if ($null -ne $DesignContract -and $DesignContract.PSObject.Properties['stages'] -and $DesignContract.PSObject.Properties['enemy_archetypes']) {
        $bossIds = @()
        foreach ($a in $DesignContract.enemy_archetypes) {
            if ($a.PSObject.Properties['archetype'] -and $a.archetype -eq 'boss') {
                $bossIds += [string]$a.id
            }
        }
        $brokenStages = @()
        foreach ($s in $DesignContract.stages) {
            $wc = if ($s.PSObject.Properties['wave_count']) { [int]$s.wave_count } else { 0 }
            $bossId = if ($s.PSObject.Properties['boss_archetype_id']) { [string]$s.boss_archetype_id } else { "" }
            if ($wc -lt 2) { $brokenStages += "$($s.id):wave_count=$wc<2" }
            elseif ([string]::IsNullOrWhiteSpace($bossId) -or ($bossIds -notcontains $bossId)) { $brokenStages += "$($s.id):boss_archetype_id='$bossId' (valid=$($bossIds -join ','))" }
        }
        if ($brokenStages.Count -gt 0) {
            $waveFired = $true
            $waveEvidence = "broken stages: $($brokenStages -join '; ')"
        } else {
            $waveFired = $false
            $waveEvidence = "all $($DesignContract.stages.Count) stages have wave_count>=2 with valid boss_archetype_id"
        }
    } else {
        $waveFired = $true
        $waveEvidence = "no stages or enemy_archetypes in design contract"
    }
    $blockers += @{
        blocker_id = "brawler_wave_spawner_deterministic"
        phase = $Phase
        fired = ($Phase -ne "vertical_slice") -and $waveFired
        evidence = $waveEvidence
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
        enemy_archetype_audits = @()
        blockers = @()
        summary = @{ passed = 1; warned = 0; failed = 0; notes = "generalista path" }
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Log 'OK' "Validator OK (generalista). Report: $OutputPath"
    exit 0
}

Write-Log 'INFO' "Manifest found at $manifestPath - validating $SPECIALIZATION_ID."

$manifestSchema = Read-JsonObject -Path (Join-Path $schemasDir "genre_specialization_manifest.schema.json")
$designSchema = Read-JsonObject -Path (Join-Path $schemasDir "brawler_belt_scroll_design_contract.schema.json")
$archetypeSchema = Read-JsonObject -Path (Join-Path $schemasDir "brawler_enemy_archetype_frame_data.schema.json")
$reportSchema = Read-JsonObject -Path (Join-Path $schemasDir "brawler_specialization_report.schema.json")

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

# Validate each enemy archetype frame data file
$archetypeAudits = @()
if ($null -ne $designContract -and $designContract.PSObject.Properties['enemy_archetypes']) {
    foreach ($a in $designContract.enemy_archetypes) {
        $aId = Get-RequiredString -Obj $a -Field "id"
        $aRole = Get-RequiredString -Obj $a -Field "archetype"
        $aRelPath = Get-RequiredString -Obj $a -Field "enemy_archetype_frame_data_path"
        $audit = [ordered]@{
            archetype_id = $aId
            archetype_role = $aRole
            path = $aRelPath
            schema_status = "absent"
            missing_required_base_stats = @()
        }
        if ($aRelPath) {
            $absPath = Join-Path $ProjectRoot $aRelPath
            $aData = Read-JsonObject -Path $absPath
            if ($null -eq $aData) {
                $audit.schema_status = "error"
                $audit.missing_required_base_stats = @("file_unreadable")
                $failed++
            } else {
                $aErrors = @()
                if ($null -ne $archetypeSchema) {
                    $aErrors = @(Test-JsonSchema -Instance $aData -Schema $archetypeSchema -Path '$.enemy_archetype')
                }
                if ($aErrors.Count -gt 0) {
                    $audit.schema_status = "error"
                    $audit.missing_required_base_stats = @($aErrors)
                    $failed += @($aErrors).Count
                    foreach ($e in $aErrors) { Write-Log 'ERROR' "  archetype[$aId]: $e" }
                } else {
                    $missing = @()
                    if ($aData.PSObject.Properties['base_stats']) {
                        foreach ($bs in $REQUIRED_BASE_STATS) {
                            if (-not $aData.base_stats.PSObject.Properties[$bs]) { $missing += $bs }
                        }
                    } else {
                        $missing = @("base_stats_missing")
                    }
                    if ($missing.Count -gt 0) {
                        $audit.schema_status = "warn"
                        $audit.missing_required_base_stats = @($missing | Select-Object -Unique)
                        $warned += $missing.Count
                        Write-Log 'WARN' "archetype[$aId] missing base_stats: $(@($missing | Select-Object -Unique) -join ', ')"
                    } else {
                        $audit.schema_status = "ok"
                        $passed++
                        Write-Log 'OK' "archetype[$aId] valid ($aRole)"
                    }
                }
            }
        } else {
            $audit.schema_status = "absent"
            $audit.missing_required_base_stats = @("path_missing")
            $failed++
        }
        $archetypeAudits += $audit
    }
}

# Phase-aware blockers
$blockers = Test-PhaseBlockers -Manifest $manifest -DesignContract $designContract -EnemyArchetypeAudits $archetypeAudits -Phase $phase
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
    enemy_archetype_audits = $archetypeAudits
    blockers = $blockers
    summary = @{
        passed = $passed
        warned = $warned
        failed = $failed
        notes = "phase=$phase"
    }
}

if ($null -ne $reportSchema) {
    # Self-validate the serialized form: $report is an OrderedDictionary, which
    # Test-JsonSchema cannot walk; the JSON round-trip yields PSCustomObjects and
    # matches exactly what is written to disk below. DateKind String keeps ISO
    # timestamps as strings instead of DateTime (PowerShell 7.5+).
    $convertFromJsonArgs = @{}
    if ((Get-Command ConvertFrom-Json).Parameters.Keys -contains 'DateKind') {
        $convertFromJsonArgs['DateKind'] = 'String'
    }
    $reportForValidation = $report | ConvertTo-Json -Depth 8 | ConvertFrom-Json @convertFromJsonArgs
    $reportErrors = @(Test-JsonSchema -Instance $reportForValidation -Schema $reportSchema -Path '$.report')
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

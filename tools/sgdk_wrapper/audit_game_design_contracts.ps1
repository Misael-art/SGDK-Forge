<#
.SYNOPSIS
    Audita contratos de design (mechanic, level, enemy, tdd) com separacao em 3 buckets.

.DESCRIPTION
    Este auditor NAO analisa gameplay, ROM ou asset. Ele faz:
    1. Validacao cross-reference entre mechanic_contract -> level_blueprint -> enemy_roster -> tdd_contract.
    2. Checagem de uso de roles canonicas contra enemy_ai_role_catalog.json.
    3. Checagem de uso de mechanic_roles contra mechanic_role_catalog.json.
    4. Checagem de head_metric contra head_metric_reference.json.
    5. Emite audit_game_design_contracts_report.json com 3 buckets de severidade.

    Separacao de severidades (Canonical Hardening v2):
    - blocker:           quebra integridade do contrato ou do runtime.
                         Afeta blocking_statuses e status=blocked.
    - creative_blocker:  quebra direcao/criacao visual ou narrativa.
                         Afeta creative_blocking_statuses e creative_ready.
                         NAO afeta blocking_statuses (para nao reprovar lab).
    - technical_artifact: quebra apenas o status de "entregavel" (asset validation,
                         lineage, optimization, premium source, etc).
                         Afeta technical_artifact_status.
                         NAO afeta blocking_statuses (lab pode passar).
    - warn:              observacao sem consequencia de gate.

    Ready flags computados no final:
    - technical_ready:  nenhum blocker E nenhum technical_artifact pendente.
    - creative_ready:   nenhum creative_blocker E semantic_audit_status != failed.
    - ready_for_aaa:    technical_ready AND creative_ready AND blocking_statuses
                         vazio AND creative_blocking_statuses vazio
                         AND semantic_audit_status != failed
                         AND semantic_audit_repeated_effect_learning_notes false.
    - ready_for_aaa NAO eh promovido aqui por claim_ceiling; isso fica no
      validate_resources.ps1 (cabe a politica de produto).

.PARAMETER MechanicContractPath
    Caminho para mechanic_contract.json. Opcional; ausente gera blocker mechanic_contract_missing.

.PARAMETER LevelBlueprintPath
    Caminho para level_blueprint.json. Opcional; ausente gera blocker level_blueprint_missing.

.PARAMETER EnemyRosterPath
    Caminho para enemy_roster.json. Opcional; ausente gera blocker enemy_roster_missing.

.PARAMETER TddContractPath
    Caminho para tdd_contract.json. Opcional; ausente gera blocker tdd_missing_for_product (quando nao-lab).

.PARAMETER ProductStatus
    technical_lab_validated | vertical_slice_candidate | ready_for_aaa. Default: vertical_slice_candidate.

.PARAMETER OutputPath
    Caminho do audit_game_design_contracts_report.json. Default: out/logs/audit_game_design_contracts_report.json.

.PARAMETER WrapperRoot
    Caminho do wrapper SGDK (para localizar schemas e catalogos). Default: diretorio pai deste script.

.PARAMETER SemanticAuditPath
    Caminho opcional para semantic_audit_report.json. Quando existir, o auditor le
    status e repeated_effect_learning_notes para alimentar ready_for_aaa.

.EXAMPLE
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File audit_game_design_contracts.ps1 `
        -MechanicContractPath contract.json `
        -LevelBlueprintPath blueprint.json `
        -EnemyRosterPath roster.json `
        -TddContractPath tdd.json `
        -ProductStatus vertical_slice_candidate `
        -OutputPath out/logs/audit_game_design_contracts_report.json

.EXIT_CODES
    0 = passed (technical_ready=true, creative_ready=true, sem blockers)
    1 = warn (creative_blockers ou technical_artifacts presentes, mas sem blockers)
    2 = blocked (blocking_statuses nao vazio)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$MechanicContractPath = "",

    [Parameter(Mandatory = $false)]
    [string]$LevelBlueprintPath = "",

    [Parameter(Mandatory = $false)]
    [string]$EnemyRosterPath = "",

    [Parameter(Mandatory = $false)]
    [string]$TddContractPath = "",

    [Parameter(Mandatory = $false)]
    [ValidateSet("technical_lab_validated", "vertical_slice_candidate", "ready_for_aaa", "technical_incomplete", "unscoped")]
    [string]$ProductStatus = "vertical_slice_candidate",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [string]$WrapperRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$SemanticAuditPath = ""
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($WrapperRoot)) {
    $WrapperRoot = $PSScriptRoot
}

$wrapperAgent = Join-Path $WrapperRoot ".agent"
$schemasDir = Join-Path $WrapperRoot "schemas"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $WrapperRoot "out\logs\audit_game_design_contracts_report.json"
}

$reportDir = Split-Path $OutputPath -Parent
if (-not (Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
}

# Tabela canonica de severidade por codigo (Canonical Hardening v2).
# Codigos nao listados aqui caem em fallback "blocker" para nao regredir.
$codeSeverity = [ordered]@{
    # --- blockers (integridade de contrato / runtime) ---
    "mechanic_contract_missing"           = "blocker"
    "mechanic_contract_invalid_json"      = "blocker"
    "mechanic_contract_invalid_shape"     = "blocker"
    "mechanic_role_invalid"               = "blocker"
    "mechanic_underused"                  = "blocker"
    "mechanic_no_combination"             = "blocker"
    "mechanic_probability_undeclared"     = "blocker"
    "mechanic_input_ambiguous"            = "blocker"
    "level_blueprint_missing"             = "blocker"
    "level_blueprint_invalid_json"        = "blocker"
    "golden_path_missing"                 = "blocker"
    "phase_rhythm_missing"                = "blocker"
    "level_mechanic_reuse_missing"        = "blocker"
    "enemy_roster_missing"                = "blocker"
    "enemy_roster_invalid_json"           = "blocker"
    "enemy_roster_invalid_shape"          = "blocker"
    "enemy_role_missing"                  = "blocker"
    "enemy_role_invalid"                  = "blocker"
    "enemy_telegraph_missing"             = "blocker"
    "enemy_synergy_missing"               = "blocker"
    "enemy_head_metric_invalid"           = "blocker"
    "tdd_missing_for_product"             = "blocker"
    "tdd_invalid_json"                    = "blocker"
    "scene_fsm_missing"                   = "blocker"
    "memory_pool_missing"                 = "blocker"
    "runtime_ownership_missing"           = "blocker"
    "region_timing_missing_for_product"   = "blocker"
    "input_contract_missing_for_product"  = "blocker"
    "tdd_technique_selection_missing"     = "blocker"
    # --- creative_blockers (direcao / autoria / direcao visual) ---
    "art_direction_undeclared"            = "creative_blocker"
    "style_catalog_not_consulted"         = "creative_blocker"
    "style_clone_risk_unbounded"          = "creative_blocker"
    "art_direction_low_confidence"        = "creative_blocker"
    "scene_direction_undeclared"          = "creative_blocker"
    "archetype_catalog_not_consulted"     = "creative_blocker"
    "decorative_only_blocked"             = "creative_blocker"
    "mode7_claim_on_megadrive"            = "creative_blocker"
    "monumental_promised_without_budget"  = "creative_blocker"
    "signature_only_without_fallback"     = "creative_blocker"
    "background_ecology_unbounded"        = "creative_blocker"
    "gdd_substantial_insufficient"        = "creative_blocker"
    "gdd_substantial_missing"             = "creative_blocker"
    "feature_creep"                       = "creative_blocker"
    "core_loop_undefined"                 = "creative_blocker"
    "visual_direction_failed"             = "creative_blocker"
    "animation_gate_failed"               = "creative_blocker"
    "gameplay_consequence_missing"        = "creative_blocker"
    "visual_gate_blocked"                 = "creative_blocker"
    "visual_delivery_gate_missing"        = "creative_blocker"
    "procedural_fallback_as_final"        = "creative_blocker"
    "decision_log_too_shallow"            = "creative_blocker"
    "axis_evidence_missing"               = "creative_blocker"
    # --- technical_artifacts (asset/lineage/optimization/premium source) ---
    "style_manifest_missing"              = "technical_artifact"
    "style_drift_uncorrected"             = "technical_artifact"
    "asset_lineage_missing"               = "technical_artifact"
    "style_memory_drift"                  = "technical_artifact"
    "premium_source_missing"              = "technical_artifact"
    "source_validity_failed"              = "technical_artifact"
    "authoriality_gate_failed"            = "technical_artifact"
    "clone_risk_report_missing"           = "technical_artifact"
    "frame_budget_missing"                = "technical_artifact"
    "pivot_scale_contract_missing"        = "technical_artifact"
    "animation_state_plan_missing"        = "technical_artifact"
    "motion_phase_map_missing"            = "technical_artifact"
    "frame_delta_report_missing"          = "technical_artifact"
    "asset_optimization_unmeasured"       = "technical_artifact"
    "dedup_unmeasured"                    = "technical_artifact"
    "missing_semantic_parse"              = "technical_artifact"
    "translation_without_review"          = "technical_artifact"
    "raster_fx_owner_collision"           = "technical_artifact"
    "palette_cycle_ownership_conflict"    = "technical_artifact"
    "cutscene_visual_contract_missing"    = "technical_artifact"
    "cutscene_fullscreen_unjustified"     = "technical_artifact"
    "cutscene_contract_missing"           = "technical_artifact"
    "architectural_baseline_undefined"    = "technical_artifact"
    "level_risk_untelegraphed"            = "technical_artifact"
}

$report = [ordered]@{
    schema_version = "2.0.0"
    audit_id = "audit_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    timestamp = (Get-Date).ToString("o")
    product_status = $ProductStatus
    status = "passed"
    issues = [System.Collections.ArrayList]::new()
    blocking_statuses = [System.Collections.ArrayList]::new()
    creative_blocking_statuses = [System.Collections.ArrayList]::new()
    technical_artifact_codes = [System.Collections.ArrayList]::new()
    technical_artifact_status = "not_audited"
    semantic_audit_status = "not_provided"
    semantic_audit_repeated_effect_learning_notes = $false
    technical_ready = $false
    creative_ready = $false
    ready_for_aaa = $false
    cross_references = @{
        mechanic_to_level = @()
        enemy_to_level = @()
        tdd_to_level = @()
        tdd_to_mechanic = @()
    }
    catalog_checks = @{
        enemy_ai_role_catalog = @{ valid_roles_used = [System.Collections.ArrayList]::new(); invalid_roles = [System.Collections.ArrayList]::new() }
        mechanic_role_catalog = @{ valid_roles_used = [System.Collections.ArrayList]::new(); invalid_roles = [System.Collections.ArrayList]::new() }
        head_metric_reference = @{ valid_metrics_used = [System.Collections.ArrayList]::new(); invalid_metrics = [System.Collections.ArrayList]::new() }
    }
    input_paths = @{
        mechanic_contract = $MechanicContractPath
        level_blueprint = $LevelBlueprintPath
        enemy_roster = $EnemyRosterPath
        tdd_contract = $TddContractPath
        semantic_audit_report = $SemanticAuditPath
    }
}

function Resolve-Severity {
    param([string]$Code, [string]$Default = "blocker")
    if ($codeSeverity.Contains($Code)) { return $codeSeverity[$Code] }
    return $Default
}

function Add-Issue {
    param(
        [string]$Code,
        [string]$Severity,
        [string]$Message
    )
    $effectiveSeverity = $Severity
    if ($script:isLab -and $effectiveSeverity -eq "blocker") {
        $effectiveSeverity = "warn"
    }
    $script:report.issues += [ordered]@{
        code = $Code
        severity = $effectiveSeverity
        bucket = if ($effectiveSeverity -eq "creative_blocker") { "creative_blocker" }
                 elseif ($effectiveSeverity -eq "technical_artifact") { "technical_artifact" }
                 elseif ($effectiveSeverity -eq "blocker") { "blocker" }
                 else { "warn" }
        message = $Message
    }
    switch ($effectiveSeverity) {
        "blocker" {
            [void]$script:report.blocking_statuses.Add($Code)
            $script:report.status = "blocked"
        }
        "creative_blocker" {
            [void]$script:report.creative_blocking_statuses.Add($Code)
            if ($script:report.status -eq "passed") { $script:report.status = "warn" }
        }
        "technical_artifact" {
            [void]$script:report.technical_artifact_codes.Add($Code)
            $script:report.technical_artifact_status = $Code
            if ($script:report.status -eq "passed") { $script:report.status = "warn" }
        }
        default {
            if ($script:report.status -eq "passed") { $script:report.status = "warn" }
        }
    }
}

function Load-JsonFile {
    param([string]$Path, [string]$Label)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    if (-not (Test-Path -LiteralPath $Path)) {
        $severity = if ($Label -like "*catalog*") { "warn" } else { "blocker" }
        Add-Issue -Code "${Label}_missing" -Severity $severity -Message "Contract file not found: $Path"
        return $null
    }
    try {
        $content = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        return ($content | ConvertFrom-Json)
    } catch {
        Add-Issue -Code "${Label}_invalid_json" -Severity "blocker" -Message "Could not parse $Path as JSON: $($_.Exception.Message)"
        return $null
    }
}

# Carrega semantic_audit_report (opcional) - alimenta ready_for_aaa.
if (-not [string]::IsNullOrWhiteSpace($SemanticAuditPath) -and (Test-Path -LiteralPath $SemanticAuditPath)) {
    try {
        $sa = Get-Content -LiteralPath $SemanticAuditPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $report.semantic_audit_status = if ($sa.PSObject.Properties.Name -contains "status") { [string]$sa.status } else { "not_provided" }
        $notes = $null
        if ($sa.PSObject.Properties.Name -contains "repeated_effect_learning_notes") { $notes = $sa.repeated_effect_learning_notes }
        if ($notes -and $notes -ne $false -and $notes -ne "" -and $notes -ne @()) {
            $report.semantic_audit_repeated_effect_learning_notes = $true
        }
    } catch {
        $report.semantic_audit_status = "invalid_json"
    }
}

$mechanic = Load-JsonFile -Path $MechanicContractPath -Label "mechanic_contract"
$level = Load-JsonFile -Path $LevelBlueprintPath -Label "level_blueprint"
$enemy = Load-JsonFile -Path $EnemyRosterPath -Label "enemy_roster"
$tdd = Load-JsonFile -Path $TddContractPath -Label "tdd_contract"

# Carrega catalogos
$catalogEnemyRoles = Load-JsonFile -Path (Join-Path $wrapperAgent "references\enemy_ai_role_catalog.json") -Label "enemy_ai_role_catalog"
$catalogMechanicRoles = Load-JsonFile -Path (Join-Path $wrapperAgent "references\mechanic_role_catalog.json") -Label "mechanic_role_catalog"
$catalogHeadMetric = Load-JsonFile -Path (Join-Path $wrapperAgent "references\head_metric_reference.json") -Label "head_metric_reference"

$validEnemyRoles = @()
if ($catalogEnemyRoles) {
    foreach ($r in $catalogEnemyRoles.roles) {
        $validEnemyRoles += $r.role_id
    }
}

$validMechanicRoles = @()
if ($catalogMechanicRoles) {
    foreach ($r in $catalogMechanicRoles.roles) {
        $validMechanicRoles += $r.role_id
    }
}

$validHeadMetrics = @()
if ($catalogHeadMetric) {
    foreach ($m in $catalogHeadMetric.metric_classes) {
        $validHeadMetrics += $m.metric_id
    }
}

$isLab = $ProductStatus -eq "technical_lab_validated"
$script:isLab = $isLab

# 1. Mechanic contract checks
if ($mechanic) {
    if ($mechanic.PSObject.Properties.Name -contains "mechanics" -and $mechanic.mechanics) {
        foreach ($m in $mechanic.mechanics) {
            $mid = $m.mechanic_id
            $mrole = $m.mechanic_role

            if ($validMechanicRoles -contains $mrole) {
                if (-not $report.catalog_checks.mechanic_role_catalog.valid_roles_used.Contains($mrole)) {
                    [void]$report.catalog_checks.mechanic_role_catalog.valid_roles_used.Add($mrole)
                }
            } else {
                [void]$report.catalog_checks.mechanic_role_catalog.invalid_roles.Add("$mid=$mrole")
                $sev = Resolve-Severity "mechanic_role_invalid"
                Add-Issue -Code "mechanic_role_invalid" -Severity $sev -Message "Mechanic $mid uses invalid mechanic_role '$mrole'."
            }

            if ($mrole -eq "core") {
                $vc = if ($m.PSObject.Properties.Name -contains "versatility_cases") { @($m.versatility_cases).Count } else { 0 }
                $mr = if ($m.PSObject.Properties.Name -contains "level_design_reuse_plan") { [int]$m.level_design_reuse_plan.min_reuses } else { 0 }
                $cm = if ($m.PSObject.Properties.Name -contains "combination_map") { @($m.combination_map).Count } else { 0 }

                if ($vc -lt 3) {
                    $sev = Resolve-Severity "mechanic_underused"
                    Add-Issue -Code "mechanic_underused" -Severity $sev -Message "Core mechanic $mid has versatility_cases=$vc (< 3)."
                }
                if ($mr -lt 3) {
                    $sev = Resolve-Severity "mechanic_underused"
                    Add-Issue -Code "mechanic_underused" -Severity $sev -Message "Core mechanic $mid has level_design_reuse_plan.min_reuses=$mr (< 3)."
                }
                if ($cm -lt 1) {
                    $sev = Resolve-Severity "mechanic_no_combination"
                    Add-Issue -Code "mechanic_no_combination" -Severity $sev -Message "Core mechanic $mid has combination_map=$cm (< 1)."
                }
            }

            if ($m.PSObject.Properties.Name -contains "probability_model") {
                $ptype = [string]$m.probability_model.type
                if ($ptype -ne "deterministic") {
                    $hasPct = $m.probability_model.PSObject.Properties.Name -contains "success_rate_percent"
                    if (-not $hasPct) {
                        $sev = Resolve-Severity "mechanic_probability_undeclared"
                        Add-Issue -Code "mechanic_probability_undeclared" -Severity $sev -Message "Mechanic $mid has probability_model.type=$ptype but no success_rate_percent."
                    }
                }
            }
        }
    } elseif ($mechanic.PSObject.Properties.Name -contains "mechanic_id") {
        $mid = $mechanic.mechanic_id
        $mrole = $mechanic.mechanic_role
        if ($validMechanicRoles -contains $mrole) {
            if (-not $report.catalog_checks.mechanic_role_catalog.valid_roles_used.Contains($mrole)) {
                [void]$report.catalog_checks.mechanic_role_catalog.valid_roles_used.Add($mrole)
            }
        } else {
            [void]$report.catalog_checks.mechanic_role_catalog.invalid_roles.Add("$mid=$mrole")
            $sev = Resolve-Severity "mechanic_role_invalid"
            Add-Issue -Code "mechanic_role_invalid" -Severity $sev -Message "Mechanic $mid uses invalid mechanic_role '$mrole'."
        }
    } else {
        $sev = Resolve-Severity "mechanic_contract_invalid_shape"
        Add-Issue -Code "mechanic_contract_invalid_shape" -Severity $sev -Message "mechanic_contract has no mechanics[] and no mechanic_id."
    }
} else {
    if (-not $isLab) {
        $sev = Resolve-Severity "mechanic_contract_missing"
        Add-Issue -Code "mechanic_contract_missing" -Severity $sev -Message "mechanic_contract.json not provided and product_status != technical_lab_validated."
    }
}

# 2. Level blueprint checks
if ($level) {
    $hasGolden = $level.PSObject.Properties.Name -contains "golden_path" -and $level.golden_path -and $level.golden_path.PSObject.Properties.Name -contains "waypoint_sequence" -and @($level.golden_path.waypoint_sequence).Count -ge 2
    if (-not $hasGolden) {
        $sev = Resolve-Severity "golden_path_missing"
        Add-Issue -Code "golden_path_missing" -Severity $sev -Message "level_blueprint has no golden_path with waypoint_sequence >= 2."
    }

    $hasRhythm = $false
    if ($level.PSObject.Properties.Name -contains "phase_rhythm_map" -and $level.phase_rhythm_map) {
        $phases = @()
        foreach ($p in $level.phase_rhythm_map) { $phases += [string]$p.phase }
        $hasCalm = $phases -contains "calm"
        $hasPressure = $phases -contains "pressure"
        $hasRhythm = $hasCalm -and $hasPressure
    }
    if (-not $hasRhythm) {
        $sev = Resolve-Severity "phase_rhythm_missing"
        Add-Issue -Code "phase_rhythm_missing" -Severity $sev -Message "level_blueprint has no phase_rhythm_map with calm AND pressure."
    }

    if ($level.PSObject.Properties.Name -contains "mechanic_reuse_map") {
        $used = @()
        if ($level.mechanic_reuse_map) {
            foreach ($r in $level.mechanic_reuse_map) { $used += [string]$r.mechanic_id }
        }
        if ($mechanic) {
            $coreMechs = @()
            $mechList = if ($mechanic.PSObject.Properties.Name -contains "mechanics") { $mechanic.mechanics } elseif ($mechanic.PSObject.Properties.Name -contains "mechanic_id") { @($mechanic) } else { @() }
            foreach ($m in $mechList) {
                if ($m.mechanic_role -eq "core") { $coreMechs += [string]$m.mechanic_id }
            }
            $missing = @()
            foreach ($cm in $coreMechs) {
                if ($used -notcontains $cm) { $missing += $cm }
            }
            foreach ($m in $missing) {
                $sev = Resolve-Severity "level_mechanic_reuse_missing"
                Add-Issue -Code "level_mechanic_reuse_missing" -Severity $sev -Message "Core mechanic $m is not in level_blueprint.mechanic_reuse_map."
            }
        }
    }
} else {
    if (-not $isLab) {
        $sev = Resolve-Severity "level_blueprint_missing"
        Add-Issue -Code "level_blueprint_missing" -Severity $sev -Message "level_blueprint.json not provided and product_status != technical_lab_validated."
    }
}

# 3. Enemy roster checks
if ($enemy) {
    if ($enemy.PSObject.Properties.Name -contains "enemies" -and $enemy.enemies) {
        foreach ($e in $enemy.enemies) {
            $eid = $e.enemy_id
            $erole = [string]$e.role
            $emetric = [string]$e.head_metric

            if (-not (($erole))) {
                $sev = Resolve-Severity "enemy_role_missing"
                Add-Issue -Code "enemy_role_missing" -Severity $sev -Message "Enemy $eid has no role."
            } else {
                if ($validEnemyRoles -contains $erole) {
                    if (-not $report.catalog_checks.enemy_ai_role_catalog.valid_roles_used.Contains($erole)) {
                        [void]$report.catalog_checks.enemy_ai_role_catalog.valid_roles_used.Add($erole)
                    }
                } else {
                    [void]$report.catalog_checks.enemy_ai_role_catalog.invalid_roles.Add("$eid=$erole")
                    $sev = Resolve-Severity "enemy_role_invalid"
                    Add-Issue -Code "enemy_role_invalid" -Severity $sev -Message "Enemy $eid uses invalid role '$erole'."
                }
            }

            if ($validHeadMetrics -contains $emetric) {
                if (-not $report.catalog_checks.head_metric_reference.valid_metrics_used.Contains($emetric)) {
                    [void]$report.catalog_checks.head_metric_reference.valid_metrics_used.Add($emetric)
                }
            } else {
                [void]$report.catalog_checks.head_metric_reference.invalid_metrics.Add("$eid=$emetric")
                $sev = Resolve-Severity "enemy_head_metric_invalid"
                Add-Issue -Code "enemy_head_metric_invalid" -Severity $sev -Message "Enemy $eid uses invalid head_metric '$emetric'."
            }

            if ($erole -eq "boss" -and $emetric -ne "XL") {
                $sev = Resolve-Severity "enemy_head_metric_invalid"
                Add-Issue -Code "enemy_head_metric_invalid" -Severity $sev -Message "Boss enemy $eid has head_metric=$emetric (boss requires XL)."
            }
            if ($erole -ne "boss" -and $erole -ne "" -and $emetric -eq "XL") {
                $sev = Resolve-Severity "enemy_head_metric_invalid"
                Add-Issue -Code "enemy_head_metric_invalid" -Severity $sev -Message "Non-boss enemy $eid has head_metric=XL (XL is reserved for boss)."
            }

            $hasTelegraph = $e.PSObject.Properties.Name -contains "telegraph_model" -and $e.telegraph_model -and $e.telegraph_model.PSObject.Properties.Name -contains "telegraph_frames" -and ([int]$e.telegraph_model.telegraph_frames) -ge 1
            if (-not $hasTelegraph) {
                $sev = Resolve-Severity "enemy_telegraph_missing"
                Add-Issue -Code "enemy_telegraph_missing" -Severity $sev -Message "Enemy $eid has no telegraph_model with telegraph_frames >= 1."
            }

            $hasSynergy = $e.PSObject.Properties.Name -contains "synergy_partners" -and @($e.synergy_partners).Count -gt 0
            if (-not $hasSynergy -and $erole -ne "solo_tutorial" -and $erole -ne "boss") {
                $sev = Resolve-Severity "enemy_synergy_missing"
                Add-Issue -Code "enemy_synergy_missing" -Severity $sev -Message "Enemy $eid has no synergy_partners (only solo_tutorial and boss allowed)."
            }
        }
    } else {
        $sev = Resolve-Severity "enemy_roster_invalid_shape"
        Add-Issue -Code "enemy_roster_invalid_shape" -Severity $sev -Message "enemy_roster has no enemies[]."
    }
} else {
    if (-not $isLab) {
        $sev = Resolve-Severity "enemy_roster_missing"
        Add-Issue -Code "enemy_roster_missing" -Severity $sev -Message "enemy_roster.json not provided and product_status != technical_lab_validated."
    }
}

# 4. TDD checks
if ($tdd) {
    $hasFsm = $tdd.PSObject.Properties.Name -contains "state_fsm_map" -and @($tdd.state_fsm_map).Count -ge 1
    if (-not $hasFsm) {
        $sev = Resolve-Severity "scene_fsm_missing"
        Add-Issue -Code "scene_fsm_missing" -Severity $sev -Message "tdd_contract has no state_fsm_map."
    }
    $hasMemory = $tdd.PSObject.Properties.Name -contains "memory_pool_map" -and @($tdd.memory_pool_map).Count -ge 1
    if (-not $hasMemory) {
        $sev = Resolve-Severity "memory_pool_missing"
        Add-Issue -Code "memory_pool_missing" -Severity $sev -Message "tdd_contract has no memory_pool_map."
    }
    $hasVblank = $tdd.PSObject.Properties.Name -contains "vblank_dma_ownership" -and $tdd.vblank_dma_ownership -and $tdd.vblank_dma_ownership.PSObject.Properties.Name -contains "vblank_owner" -and $tdd.vblank_dma_ownership.vblank_owner
    if (-not $hasVblank) {
        $sev = Resolve-Severity "runtime_ownership_missing"
        Add-Issue -Code "runtime_ownership_missing" -Severity $sev -Message "tdd_contract has no vblank_dma_ownership.vblank_owner."
    }
    $hasRegion = $tdd.PSObject.Properties.Name -contains "region_timing_scope" -and $tdd.region_timing_scope -and $tdd.region_timing_scope.PSObject.Properties.Name -contains "region" -and $tdd.region_timing_scope.region
    if (-not $hasRegion) {
        $sev = Resolve-Severity "region_timing_missing_for_product"
        Add-Issue -Code "region_timing_missing_for_product" -Severity $sev -Message "tdd_contract has no region_timing_scope.region."
    }
    $hasTechniqueSelection =
        $tdd.PSObject.Properties.Name -contains "technique_selection" -and
        $tdd.technique_selection -and
        $tdd.technique_selection.PSObject.Properties.Name -contains "selected_registry_ids" -and
        @($tdd.technique_selection.selected_registry_ids).Count -ge 1 -and
        $tdd.technique_selection.PSObject.Properties.Name -contains "required_tags" -and
        @($tdd.technique_selection.required_tags).Count -ge 1 -and
        $tdd.technique_selection.PSObject.Properties.Name -contains "owner_skills" -and
        @($tdd.technique_selection.owner_skills).Count -ge 1 -and
        $tdd.technique_selection.PSObject.Properties.Name -contains "selection_rationale" -and
        $tdd.technique_selection.selection_rationale -and
        $tdd.technique_selection.PSObject.Properties.Name -contains "fallback_strategy" -and
        $tdd.technique_selection.fallback_strategy -and
        $tdd.technique_selection.PSObject.Properties.Name -contains "application_plan" -and
        @($tdd.technique_selection.application_plan).Count -ge @($tdd.technique_selection.selected_registry_ids).Count -and
        $tdd.technique_selection.PSObject.Properties.Name -contains "rejected_or_deferred"
    if (-not $hasTechniqueSelection) {
        $sev = Resolve-Severity "tdd_technique_selection_missing"
        Add-Issue -Code "tdd_technique_selection_missing" -Severity $sev -Message "tdd_contract must select registry techniques and provide tags, owner skills, purpose, budget evidence, fallback, application plan, and rejected/deferred decisions."
    }
} else {
    if (-not $isLab) {
        $sev = Resolve-Severity "tdd_missing_for_product"
        Add-Issue -Code "tdd_missing_for_product" -Severity $sev -Message "tdd_contract.json not provided and product_status != technical_lab_validated."
    }
}

# Cross-references
if ($mechanic -and $level) {
    $mechList = if ($mechanic.PSObject.Properties.Name -contains "mechanics") { $mechanic.mechanics } elseif ($mechanic.PSObject.Properties.Name -contains "mechanic_id") { @($mechanic) } else { @() }
    $mechIds = @()
    foreach ($m in $mechList) { $mechIds += [string]$m.mechanic_id }
    $usedMechIds = @()
    if ($level.PSObject.Properties.Name -contains "mechanic_reuse_map" -and $level.mechanic_reuse_map) {
        foreach ($r in $level.mechanic_reuse_map) { $usedMechIds += [string]$r.mechanic_id }
    }
    foreach ($mid in $mechIds) {
        $ok = $usedMechIds -contains $mid
        $report.cross_references.mechanic_to_level += [ordered]@{
            mechanic_id = $mid
            used_in = if ($ok) { @("level_blueprint") } else { @() }
            ok = $ok
        }
        if (-not $ok -and $mechList.Count -gt 0) {
            $m = $mechList | Where-Object { $_.mechanic_id -eq $mid } | Select-Object -First 1
            if ($m -and $m.mechanic_role -eq "core") {
                $sev = Resolve-Severity "level_mechanic_reuse_missing"
                Add-Issue -Code "level_mechanic_reuse_missing" -Severity $sev -Message "Core mechanic $mid not used in level_blueprint."
            }
        }
    }
}

if ($enemy -and $level) {
    $enemyIds = @()
    if ($enemy.PSObject.Properties.Name -contains "enemies" -and $enemy.enemies) {
        foreach ($e in $enemy.enemies) { $enemyIds += [string]$e.enemy_id }
    }
    $report.cross_references.enemy_to_level += [ordered]@{
        enemy_count = $enemyIds.Count
        level_scope_id = if ($level.PSObject.Properties.Name -contains "scope_id") { $level.scope_id } else { "" }
        ok = ($enemyIds.Count -gt 0)
    }
}

if ($tdd -and $level) {
    $fsmScopeIds = @()
    if ($tdd.PSObject.Properties.Name -contains "state_fsm_map" -and $tdd.state_fsm_map) {
        foreach ($f in $tdd.state_fsm_map) { $fsmScopeIds += [string]$f.scene_id }
    }
    $levelScopeId = if ($level.PSObject.Properties.Name -contains "scope_id") { $level.scope_id } else { "" }
    $report.cross_references.tdd_to_level += [ordered]@{
        tdd_fsm_scene_ids = $fsmScopeIds
        level_scope_id = $levelScopeId
        ok = ($fsmScopeIds -contains $levelScopeId) -or ($fsmScopeIds.Count -gt 0)
    }
    if ($levelScopeId -and ($fsmScopeIds -notcontains $levelScopeId)) {
        $sev = Resolve-Severity "tdd_fsm_scope_mismatch"
        Add-Issue -Code "tdd_fsm_scope_mismatch" -Severity "warn" -Message "tdd.state_fsm_map does not include level_blueprint.scope_id '$levelScopeId'."
    }
}

# --- Computa ready flags (Canonical Hardening v2) ---
$report.blocking_statuses = @($report.blocking_statuses | Select-Object -Unique)
$report.creative_blocking_statuses = @($report.creative_blocking_statuses | Select-Object -Unique)
$report.technical_artifact_codes = @($report.technical_artifact_codes | Select-Object -Unique)
$report.issues = @($report.issues | Select-Object -Unique)

if ($report.technical_artifact_status -eq "not_audited" -and $report.technical_artifact_codes.Count -eq 0) {
    $report.technical_artifact_status = "technical_artifact_ok"
}

$report.technical_ready = [bool](
    $report.blocking_statuses.Count -eq 0 -and
    $report.technical_artifact_codes.Count -eq 0
)

$report.creative_ready = [bool](
    $report.creative_blocking_statuses.Count -eq 0 -and
    $report.semantic_audit_status -ne "failed"
)

$report.ready_for_aaa = [bool](
    $report.technical_ready -and
    $report.creative_ready -and
    $report.blocking_statuses.Count -eq 0 -and
    $report.creative_blocking_statuses.Count -eq 0 -and
    $report.semantic_audit_status -ne "failed" -and
    (-not $report.semantic_audit_repeated_effect_learning_notes)
)

$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $OutputPath -Encoding UTF8

Write-Host "[audit_game_design_contracts] status=$($report.status) blockers=$($report.blocking_statuses.Count) creative=$($report.creative_blocking_statuses.Count) tech_artifacts=$($report.technical_artifact_codes.Count) technical_ready=$($report.technical_ready) creative_ready=$($report.creative_ready) ready_for_aaa=$($report.ready_for_aaa) report=$OutputPath"

if ($report.status -eq "blocked") { exit 2 }
if ($report.status -eq "warn") { exit 1 }
exit 0

<#
.SYNOPSIS
    Validates structured methodology adoption and explicit high-risk claims.

.DESCRIPTION
    This validator intentionally does not infer claims from generic words in
    source code or Markdown. Claims become enforceable only through
    doc/project_methodology_manifest.json.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$WorkspaceRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Prop {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $Default }
    return $property.Value
}

function Get-Text {
    param($Value, [string]$Default = '')
    if ($null -eq $Value) { return $Default }
    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) { return $Default }
    return $text.Trim()
}

function Resolve-ProjectPath {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $script:ResolvedProjectRoot $Value))
}

function Test-UnderProject {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    $full = [System.IO.Path]::GetFullPath($Path)
    $root = $script:ResolvedProjectRoot.TrimEnd('\', '/')
    return $full.Equals($root, [System.StringComparison]::OrdinalIgnoreCase) -or
        $full.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-ProjectFile {
    param([string]$Value)
    $path = Resolve-ProjectPath $Value
    return $path -and (Test-UnderProject $path) -and (Test-Path -LiteralPath $path -PathType Leaf)
}

function Read-JsonOrNull {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Add-Blocker {
    param(
        [string]$Status,
        [string]$Message,
        [string]$Path = '',
        $Details = $null
    )
    if (-not ($script:Report.blocking_statuses -contains $Status)) {
        $script:Report.blocking_statuses += $Status
    }
    $script:Report.details += [ordered]@{
        status = $Status
        message = $Message
        path = $Path
        details = $Details
    }
}

function Test-RequiredSet {
    param(
        [string[]]$Actual,
        [string[]]$Required,
        [string]$Status,
        [string]$Context
    )
    $missing = @($Required | Where-Object { $Actual -notcontains $_ })
    if ($missing.Count -gt 0) {
        Add-Blocker $Status "$Context nao declara todos os itens obrigatorios." $script:ManifestPath @{
            missing = $missing
        }
        return $false
    }
    return $true
}

function Get-CombinedSourceText {
    param($SourcePaths)
    $chunks = @()
    foreach ($value in @($SourcePaths)) {
        $path = Resolve-ProjectPath (Get-Text $value)
        if (-not $path -or -not (Test-UnderProject $path) -or -not (Test-Path -LiteralPath $path -PathType Leaf)) {
            return $null
        }
        $chunks += Get-Content -LiteralPath $path -Raw -Encoding UTF8
    }
    return ($chunks -join "`n")
}

function Validate-ClaimState {
    param([string]$ClaimName, $Claim)
    if ($null -eq $Claim) {
        Add-Blocker 'project_methodology_manifest_invalid' "Claim '$ClaimName' ausente." $script:ManifestPath
        return $false
    }
    $applicability = Get-Text (Get-Prop $Claim 'applicability' '')
    $rationale = Get-Text (Get-Prop $Claim 'rationale' '')
    if ($applicability -notin @('review_required', 'not_applicable', 'required') -or $rationale.Length -lt 8) {
        Add-Blocker 'project_methodology_manifest_invalid' "Claim '$ClaimName' possui applicability/rationale invalido." $script:ManifestPath
        return $false
    }
    if ($applicability -eq 'review_required') {
        Add-Blocker 'project_methodology_manifest_invalid' "Claim '$ClaimName' ainda precisa ser classificado." $script:ManifestPath
        return $false
    }
    return $true
}

function Validate-CriticalMotionClaim {
    param($Claim, [string[]]$DeclaredSkills)
    if ((Get-Text (Get-Prop $Claim 'applicability' '')) -ne 'required') { return }

    [void](Test-RequiredSet $DeclaredSkills @(
        'art/visual-excellence-standards',
        'code/sgdk-runtime-coder'
    ) 'project_methodology_manifest_invalid' 'Claim critical_motion')

    $missingSignals = @()
    $criticalAssets = @((Get-Prop $Claim 'critical_asset_ids' @()))
    if ($criticalAssets.Count -eq 0) { $missingSignals += 'critical_asset_ids' }

    $motionPath = Get-Text (Get-Prop $Claim 'motion_gif_path' '')
    if (-not (Test-ProjectFile $motionPath)) { $missingSignals += 'motion_gif' }

    $approvalPath = Get-Text (Get-Prop $Claim 'human_approval_record_path' '')
    if (-not (Test-ProjectFile $approvalPath)) { $missingSignals += 'human_approval_record' }

    $metricsPath = Join-Path $script:ResolvedProjectRoot 'out\logs\runtime_metrics.json'
    $metrics = Read-JsonOrNull $metricsPath
    $perceptual = Get-Prop $metrics 'perceptual_check' $null
    foreach ($axis in @('fluidez', 'leitura', 'naturalidade', 'impacto')) {
        $value = Get-Prop $perceptual $axis $null
        $number = 0.0
        if ($null -eq $value -or -not [double]::TryParse([string]$value, [ref]$number) -or $number -le 0) {
            $missingSignals += "perceptual_check.$axis"
        }
    }

    $blastemPath = Join-Path $script:ResolvedProjectRoot 'out\logs\blastem_evidence.json'
    $blastem = Read-JsonOrNull $blastemPath
    $screenshotPresent = [bool](Get-Prop $blastem 'screenshot_present' $false)
    $screenshotPath = Get-Text (Get-Prop $blastem 'screenshot_path' '')
    if (-not $screenshotPresent -or -not (Test-ProjectFile $screenshotPath)) { $missingSignals += 'screenshot_dedicado' }

    $sramPresent = [bool](Get-Prop $blastem 'sram_present' $false)
    $freshSram = [bool](Get-Prop $blastem 'fresh_sram_confirmed' $false)
    $sramPath = Get-Text (Get-Prop $blastem 'sram_path' '')
    if (-not $sramPresent -or -not $freshSram -or -not (Test-ProjectFile $sramPath)) { $missingSignals += 'save.sram_fresco' }

    $vdpPresent = [bool](Get-Prop $blastem 'vdp_dump_present' $false)
    $vdpPath = Get-Text (Get-Prop $blastem 'vdp_dump_path' '')
    if (-not $vdpPresent -or -not (Test-ProjectFile $vdpPath)) { $missingSignals += 'visual_vdp_dump.bin' }

    if ($missingSignals.Count -gt 0) {
        Add-Blocker 'perceptual_motion_unvalidated' 'Claim critical_motion exige todos os sinais perceptivos e aprovacao humana; nenhum sinal isolado libera o gate.' $script:ManifestPath @{
            missing_signals = @($missingSignals | Select-Object -Unique)
            required_signals = @(
                'critical_asset_ids',
                'motion_gif',
                'human_approval_record',
                'perceptual_check.fluidez>0',
                'perceptual_check.leitura>0',
                'perceptual_check.naturalidade>0',
                'perceptual_check.impacto>0',
                'screenshot_dedicado',
                'save.sram_fresco',
                'visual_vdp_dump.bin'
            )
        }
    }
}

function Validate-RoadPhysicsClaim {
    param($Claim, [string[]]$DeclaredSkills)
    if ((Get-Text (Get-Prop $Claim 'applicability' '')) -ne 'required') { return }

    [void](Test-RequiredSet $DeclaredSkills @(
        'design/level-design-canonical',
        'code/sgdk-runtime-coder',
        'hardware/megadrive-vdp-budget-analyst'
    ) 'project_methodology_manifest_invalid' 'Claim road_physics')

    $contractValue = Get-Text (Get-Prop $Claim 'contract_path' '')
    $contractPath = Resolve-ProjectPath $contractValue
    $contract = if ($contractPath -and (Test-UnderProject $contractPath)) { Read-JsonOrNull $contractPath } else { $null }
    $issues = @()
    if ($null -eq $contract) {
        $issues += 'contract_missing_or_invalid_json'
    } else {
        foreach ($field in @('contract_id', 'scene_id', 'lane_model', 'parallax_equation', 'curvature', 'impact_frame', 'screen_shake', 'hscroll_budget', 'runtime_source_paths', 'runtime_symbols')) {
            if ($null -eq (Get-Prop $contract $field $null)) { $issues += "missing:$field" }
        }
        $laneModel = Get-Prop $contract 'lane_model' $null
        if ([int](Get-Prop $laneModel 'lane_count' 0) -lt 1 -or [int](Get-Prop $laneModel 'lane_width_px' 0) -lt 1) {
            $issues += 'invalid:lane_model'
        }
        $hscroll = Get-Prop $contract 'hscroll_budget' $null
        if ([int](Get-Prop $hscroll 'rows_updated' 0) -lt 1 -or [int](Get-Prop $hscroll 'bytes_per_frame' 0) -lt 1 -or (Get-Text (Get-Prop $hscroll 'update_phase' '')) -notin @('vblank', 'loading')) {
            $issues += 'invalid:hscroll_budget'
        }
        $sourceText = Get-CombinedSourceText (Get-Prop $contract 'runtime_source_paths' @())
        if ($null -eq $sourceText) {
            $issues += 'runtime_source_paths_missing'
        } else {
            $symbols = Get-Prop $contract 'runtime_symbols' $null
            foreach ($symbolName in @('lane_update', 'curvature_update', 'impact_handler')) {
                $symbol = Get-Text (Get-Prop $symbols $symbolName '')
                if (-not $symbol -or $sourceText -notmatch [regex]::Escape($symbol)) {
                    $issues += "runtime_symbol_missing:$symbolName"
                }
            }
        }
    }
    if ($issues.Count -gt 0) {
        Add-Blocker 'road_physics_contract_invalid' 'Claim road_physics exige contrato valido e simbolos implementados no runtime.' $contractPath @{
            issues = @($issues | Select-Object -Unique)
        }
    }
}

function Validate-ModularBossClaim {
    param($Claim, [string[]]$DeclaredSkills)
    if ((Get-Text (Get-Prop $Claim 'applicability' '')) -ne 'required') { return }

    [void](Test-RequiredSet $DeclaredSkills @(
        'code/forward-kinematics-rigging',
        'code/sgdk-runtime-coder',
        'hardware/megadrive-vdp-budget-analyst'
    ) 'project_methodology_manifest_invalid' 'Claim modular_boss')

    $contractValue = Get-Text (Get-Prop $Claim 'contract_path' '')
    $contractPath = Resolve-ProjectPath $contractValue
    $contract = if ($contractPath -and (Test-UnderProject $contractPath)) { Read-JsonOrNull $contractPath } else { $null }
    $issues = @()
    if ($null -eq $contract) {
        $issues += 'contract_missing_or_invalid_json'
    } else {
        foreach ($field in @('boss_id', 'scene_id', 'parts', 'fk_chain', 'fk_update_symbol', 'runtime_source_paths', 'scanline_budget')) {
            if ($null -eq (Get-Prop $contract $field $null)) { $issues += "missing:$field" }
        }
        $parts = @((Get-Prop $contract 'parts' @()))
        if ($parts.Count -lt 2) { $issues += 'parts_minimum_2' }
        $chains = @((Get-Prop $contract 'fk_chain' @()))
        if ($chains.Count -lt 1) { $issues += 'fk_chain_minimum_1' }
        $sourceText = Get-CombinedSourceText (Get-Prop $contract 'runtime_source_paths' @())
        if ($null -eq $sourceText) {
            $issues += 'runtime_source_paths_missing'
        } else {
            foreach ($part in $parts) {
                $symbol = Get-Text (Get-Prop $part 'runtime_symbol' '')
                if (-not $symbol -or $sourceText -notmatch [regex]::Escape($symbol)) {
                    $issues += "part_runtime_symbol_missing:$symbol"
                }
            }
            $fkSymbol = Get-Text (Get-Prop $contract 'fk_update_symbol' '')
            if (-not $fkSymbol -or $sourceText -notmatch [regex]::Escape($fkSymbol)) {
                $issues += 'fk_update_symbol_missing'
            }
        }
        $budget = Get-Prop $contract 'scanline_budget' $null
        $maximum = [int](Get-Prop $budget 'maximum_sprites_per_line' 0)
        $peak = [int](Get-Prop $budget 'measured_peak' -1)
        if ($maximum -lt 1 -or $maximum -gt 20 -or $peak -lt 0 -or $peak -gt $maximum) {
            $issues += 'invalid:scanline_budget'
        }
    }
    if ($issues.Count -gt 0) {
        Add-Blocker 'modular_boss_runtime_invalid' 'Claim modular_boss exige partes runtime, FK chain e budget de scanline validos.' $contractPath @{
            issues = @($issues | Select-Object -Unique)
        }
    }
}

$script:ResolvedProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if (-not (Test-Path -LiteralPath $script:ResolvedProjectRoot -PathType Container)) {
    throw "ProjectRoot inexistente: $script:ResolvedProjectRoot"
}
if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $script:ResolvedProjectRoot 'out\logs\project_methodology_report.json'
}
$script:ManifestPath = Join-Path $script:ResolvedProjectRoot 'doc\project_methodology_manifest.json'
$script:Report = [ordered]@{
    schema_version = '1.0.0'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    project_root = $script:ResolvedProjectRoot
    manifest_path = $script:ManifestPath
    status = 'blocked'
    ready = $false
    blocking_statuses = @()
    details = @()
}

$manifest = Read-JsonOrNull $script:ManifestPath
if (-not (Test-Path -LiteralPath $script:ManifestPath -PathType Leaf)) {
    Add-Blocker 'project_methodology_manifest_missing' 'Projeto sem doc/project_methodology_manifest.json; adote a metodologia antes do closeout.' $script:ManifestPath
} elseif ($null -eq $manifest) {
    Add-Blocker 'project_methodology_manifest_invalid' 'project_methodology_manifest.json possui JSON invalido.' $script:ManifestPath
} else {
    $project = Get-Prop $manifest 'project' $null
    $projectName = Get-Text (Get-Prop $project 'name' '')
    $projectFolderName = Split-Path $script:ResolvedProjectRoot -Leaf
    $lifecycle = Get-Text (Get-Prop $project 'lifecycle' '')
    $rootPolicy = Get-Text (Get-Prop $project 'project_root_policy' '')
    $workflow = Get-Text (Get-Prop $manifest 'active_workflow' '')
    $declaredSkills = @((Get-Prop $manifest 'required_skills' @()) | ForEach-Object { Get-Text $_ } | Where-Object { $_ })
    $declaredValidations = @((Get-Prop $manifest 'required_validations' @()) | ForEach-Object { Get-Text $_ } | Where-Object { $_ })

    if ($lifecycle -notin @('new', 'existing', 'reseed')) {
        Add-Blocker 'project_methodology_manifest_invalid' 'project.lifecycle precisa ser new, existing ou reseed.' $script:ManifestPath @{
            lifecycle = $lifecycle
        }
    }
    if (-not $projectName -or $projectName -eq '__PROJECT_NAME__' -or $projectName -ne $projectFolderName) {
        Add-Blocker 'project_naming_invalid' 'project.name precisa usar o nome real do diretorio do projeto, sem placeholder.' $script:ManifestPath @{
            project_name = $projectName
            project_folder_name = $projectFolderName
            naming_standard = 'doc/PADRAO_NOMENCLATURA.md'
        }
    }
    $canonicalProjectNamePattern = '^[^\\/:*?"<>|\[\]\r\n]+ \[VER\.[0-9]+(?:\.[0-9]+)*\] \[SGDK [0-9]+\] \[[A-Z0-9][A-Z0-9 _-]*\] \[[A-Z0-9][A-Z0-9 _-]*\] \[[A-Z0-9][A-Z0-9 _-]*\]$'
    if ($lifecycle -in @('new', 'reseed') -and $projectFolderName -notmatch $canonicalProjectNamePattern) {
        Add-Blocker 'project_naming_invalid' 'Projeto new/reseed precisa usar o padrao canonico de diretorio.' $script:ManifestPath @{
            project_folder_name = $projectFolderName
            expected_pattern = 'NOME [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]'
            naming_standard = 'doc/PADRAO_NOMENCLATURA.md'
        }
    }
    $mddevPath = Join-Path $script:ResolvedProjectRoot '.mddev\project.json'
    $mddev = Read-JsonOrNull $mddevPath
    if ($mddev) {
        $mddevName = Get-Text (Get-Prop $mddev 'name' '')
        $mddevDisplayName = Get-Text (Get-Prop $mddev 'display_name' '')
        if ($mddevName -eq '__PROJECT_NAME__' -or $mddevDisplayName -eq '__PROJECT_NAME__' -or
            ($mddevName -and $mddevName -ne $projectFolderName) -or
            ($mddevDisplayName -and $mddevDisplayName -ne $projectFolderName)) {
            Add-Blocker 'project_naming_invalid' '.mddev/project.json precisa refletir o nome real do diretorio do projeto.' $mddevPath @{
                project_name = $mddevName
                display_name = $mddevDisplayName
                project_folder_name = $projectFolderName
                naming_standard = 'doc/PADRAO_NOMENCLATURA.md'
            }
        }
    }
    if ($rootPolicy -ne 'all_project_material_inside_project') {
        Add-Blocker 'project_methodology_manifest_invalid' 'project_root_policy precisa manter todo material dentro do projeto.' $script:ManifestPath
    }
    if ($workflow -ne 'production-loop') {
        Add-Blocker 'project_methodology_manifest_invalid' 'active_workflow precisa ser production-loop.' $script:ManifestPath
    }
    [void](Test-RequiredSet $declaredSkills @(
        'governance/truth-hierarchy-guard',
        'governance/doc-sync-audit',
        'operation/sgdk-build-wrapper-operator'
    ) 'project_methodology_manifest_invalid' 'Metodologia base')
    [void](Test-RequiredSet $declaredValidations @(
        'preflight_host',
        'validate_resources',
        'scene_closeout_gate',
        'freshness_audit',
        'project_hygiene',
        'project_context'
    ) 'project_methodology_manifest_invalid' 'Validacoes base')

    $claims = Get-Prop $manifest 'claims' $null
    $criticalMotion = Get-Prop $claims 'critical_motion' $null
    $roadPhysics = Get-Prop $claims 'road_physics' $null
    $modularBoss = Get-Prop $claims 'modular_boss' $null
    [void](Validate-ClaimState 'critical_motion' $criticalMotion)
    [void](Validate-ClaimState 'road_physics' $roadPhysics)
    [void](Validate-ClaimState 'modular_boss' $modularBoss)
    Validate-CriticalMotionClaim $criticalMotion $declaredSkills
    Validate-RoadPhysicsClaim $roadPhysics $declaredSkills
    Validate-ModularBossClaim $modularBoss $declaredSkills
}

$script:Report.ready = ($script:Report.blocking_statuses.Count -eq 0)
$script:Report.status = if ($script:Report.ready) { 'passed' } else { 'blocked' }
$outputParent = Split-Path $OutputPath -Parent
if (-not (Test-Path -LiteralPath $outputParent)) {
    New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
}
[System.IO.File]::WriteAllText(
    $OutputPath,
    ($script:Report | ConvertTo-Json -Depth 20),
    [System.Text.Encoding]::UTF8
)

Write-Host ("[validate_project_methodology] status={0} blockers={1} report={2}" -f $script:Report.status, $script:Report.blocking_statuses.Count, $OutputPath)
if ($script:Report.ready) { exit 0 }
exit 1

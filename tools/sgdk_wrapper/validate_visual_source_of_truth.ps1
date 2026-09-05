<#
.SYNOPSIS
    Valida que a geracao visual parte apenas da fonte autoral aprovada.
.DESCRIPTION
    Bloqueia o anti-padrao de usar sprite sheets derivadas, parciais ou
    reprovadas como source/baseline/reference_for_generation/img2img_base.
    Sprite sheets podem ser evidencia, comparacao ou runtime candidate, mas
    nunca origem de nova arte.
#>

[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$ContractPath = "",
    [string]$SchemaPath = "",
    [string]$OutputPath = "",
    [switch]$SelfCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $SchemaPath) {
    $SchemaPath = Join-Path $PSScriptRoot 'schemas\visual_source_of_truth.schema.json'
}
if (-not $OutputPath -and $ProjectRoot) {
    $OutputPath = Join-Path $ProjectRoot 'out\logs\visual_source_lineage_report.json'
}

function Normalize-VisualPath {
    param([object]$Value)
    if ($null -eq $Value) { return "" }
    $s = [string]$Value
    $s = $s.Trim()
    $s = $s -replace '\\', '/'
    while ($s.StartsWith('./')) {
        $s = $s.Substring(2)
    }
    return $s.ToLowerInvariant()
}

function Get-JsonPropertyValue {
    param([object]$Object, [string]$Name, [object]$Default = $null)
    if ($null -eq $Object) { return $Default }
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $Default }
    return $prop.Value
}

function ConvertTo-RelativePath {
    param([string]$Path)
    if (-not $Path) { return "" }
    $fullProject = [System.IO.Path]::GetFullPath($ProjectRoot)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if ($fullPath.StartsWith($fullProject, [System.StringComparison]::OrdinalIgnoreCase)) {
        return (Normalize-VisualPath $fullPath.Substring($fullProject.Length).TrimStart('\', '/'))
    }
    return (Normalize-VisualPath $Path)
}

function Test-VisualPatternMatch {
    param([string]$Path, [string]$Pattern)
    $p = Normalize-VisualPath $Path
    $pat = Normalize-VisualPath $Pattern
    if (-not $p -or -not $pat) { return $false }
    return ($p -like $pat)
}

function Test-LineageScalar {
    param([object]$Value)
    if ($null -eq $Value) { return $true }
    if ($Value -is [string] -or $Value -is [char] -or $Value -is [bool] -or
        $Value -is [datetime] -or $Value.GetType().IsEnum -or $Value.GetType().IsValueType) {
        return $true
    }
    return $false
}

function Test-LineageContainer {
    param([object]$Value)
    if (Test-LineageScalar $Value) { return $false }
    if ($Value -is [System.Collections.IDictionary]) { return $true }
    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) { return $true }
    return ($Value -is [pscustomobject])
}

function Test-ValueContainsForbiddenPath {
    param([object]$Value, [string[]]$ForbiddenPatterns, [int]$Depth = 0, [int]$MaxDepth = 64)
    if ($null -eq $Value) { return $false }
    if ($Depth -gt $MaxDepth) { return $false }

    if ($Value -is [string]) {
        $normalized = Normalize-VisualPath $Value
        foreach ($pattern in $ForbiddenPatterns) {
            if (Test-VisualPatternMatch $normalized $pattern) { return $true }
            if ($normalized.Contains((Normalize-VisualPath $pattern).TrimEnd('*'))) { return $true }
        }
        return $false
    }

    if ($Value -is [System.Collections.IDictionary]) {
        foreach ($key in $Value.Keys) {
            if (Test-ValueContainsForbiddenPath $Value[$key] $ForbiddenPatterns ($Depth + 1) $MaxDepth) { return $true }
        }
        return $false
    }

    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        foreach ($item in $Value) {
            if (Test-ValueContainsForbiddenPath $item $ForbiddenPatterns ($Depth + 1) $MaxDepth) { return $true }
        }
        return $false
    }

    if (-not (Test-LineageContainer $Value)) { return $false }
    foreach ($prop in $Value.PSObject.Properties) {
        if (Test-ValueContainsForbiddenPath $prop.Value $ForbiddenPatterns ($Depth + 1) $MaxDepth) { return $true }
    }
    return $false
}

function Add-Finding {
    param(
        [string]$Code,
        [string]$Severity,
        [string]$Message,
        [string]$File = "",
        [string]$Field = "",
        [string]$Path = ""
    )

    $finding = [ordered]@{
        code = $Code
        severity = $Severity
        message = $Message
    }
    if ($File) { $finding.file = $File }
    if ($Field) { $finding.field = $Field }
    if ($Path) { $finding.path = $Path }
    $script:findings += [pscustomobject]$finding

    if ($Severity -eq 'ERROR') {
        if ($script:blockingStatuses -notcontains $Code) {
            $script:blockingStatuses += $Code
        }
        if ($script:creativeBlockingStatuses -notcontains $Code) {
            $script:creativeBlockingStatuses += $Code
        }
    }
}

function Test-ObjectForLineageReference {
    param(
        [object]$Node,
        [string]$FieldPath,
        [string]$FilePath,
        [string[]]$BlockedFields,
        [string[]]$ForbiddenPatterns,
        [int]$Depth = 0,
        [int]$MaxDepth = 64
    )

    if ($null -eq $Node) { return }
    if ($Depth -gt $MaxDepth) {
        Add-Finding 'visual_lineage_depth_limit' 'ERROR' "Objeto JSON excede a profundidade maxima de linhagem ($MaxDepth)." $FilePath $FieldPath
        return
    }
    if (Test-LineageScalar $Node) { return }

    if ($Node -is [System.Collections.IDictionary]) {
        foreach ($key in $Node.Keys) {
            $name = [string]$key
            $nextFieldPath = if ($FieldPath) { "$FieldPath.$name" } else { $name }
            $value = $Node[$key]
            if (($name.ToLowerInvariant() -in $BlockedFields) -and (Test-ValueContainsForbiddenPath $value $ForbiddenPatterns 0 $MaxDepth)) {
                Add-Finding 'visual_lineage_forbidden_reference' 'ERROR' "Campo de linhagem visual usa sprite sheet derivada/reprovada como origem de geracao." $FilePath $nextFieldPath
            }
            Test-ObjectForLineageReference $value $nextFieldPath $FilePath $BlockedFields $ForbiddenPatterns ($Depth + 1) $MaxDepth
        }
        return
    }

    if ($Node -is [System.Collections.IEnumerable] -and -not ($Node -is [string])) {
        $index = 0
        foreach ($item in $Node) {
            Test-ObjectForLineageReference $item "$FieldPath[$index]" $FilePath $BlockedFields $ForbiddenPatterns ($Depth + 1) $MaxDepth
            $index++
        }
        return
    }

    if (-not (Test-LineageContainer $Node)) { return }

    foreach ($prop in $Node.PSObject.Properties) {
        $name = [string]$prop.Name
        $nextFieldPath = if ($FieldPath) { "$FieldPath.$name" } else { $name }
        if (($name.ToLowerInvariant() -in $BlockedFields) -and (Test-ValueContainsForbiddenPath $prop.Value $ForbiddenPatterns)) {
            Add-Finding `
                -Code 'visual_lineage_forbidden_reference' `
                -Severity 'ERROR' `
                -Message "Campo de linhagem visual usa sprite sheet derivada/reprovada como origem de geracao." `
                -File $FilePath `
                -Field $nextFieldPath
        }
        Test-ObjectForLineageReference $prop.Value $nextFieldPath $FilePath $BlockedFields $ForbiddenPatterns ($Depth + 1) $MaxDepth
    }
}

function Write-ReportAndExit {
    param([int]$ExitCode)

    $reportDir = Split-Path $OutputPath -Parent
    if ($reportDir -and -not (Test-Path -LiteralPath $reportDir)) {
        New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
    }

    $status = if ($blockingStatuses.Count -gt 0) { 'blocked' } else { 'passed' }
    $report = [ordered]@{
        schema_version = '1.0.0'
        report_kind = 'visual_source_lineage_report'
        generated_at = (Get-Date).ToString('s')
        status = $status
        project_root = $ProjectRoot
        contract_path = $ContractPath
        schema_path = $SchemaPath
        blocking_statuses = @($blockingStatuses | Select-Object -Unique)
        creative_blocking_statuses = @($creativeBlockingStatuses | Select-Object -Unique)
        findings = @($findings)
        approved_authorial_source = $approvedAuthorialSource
        allowed_generation_sources = @($allowedSources)
        forbidden_generation_sources = @($forbiddenSources)
        obsolete_assets = @($obsoleteAssets)
        partial_runtime_candidates = @($partialRuntimeCandidates)
        scan_findings = @($scanFindings)
        decision = [ordered]@{
            generation_source_locked = [bool]$generationSourceLocked
            next_sprite_sheet_must_start_from_model_sheet = [bool]$nextSpriteSheetMustStartFromModelSheet
            ready_for_aaa = [bool]$readyForAaa
        }
    }

    [System.IO.File]::WriteAllText($OutputPath, ($report | ConvertTo-Json -Depth 20), [System.Text.Encoding]::UTF8)
    if ($ExitCode -ne 0) { exit $ExitCode }
    exit 0
}

$script:blockingStatuses = @()
$script:creativeBlockingStatuses = @()
$script:findings = @()
$script:scanFindings = @()
$approvedAuthorialSource = $null
$allowedSources = @()
$forbiddenSources = @()
$obsoleteAssets = @()
$partialRuntimeCandidates = @()
$generationSourceLocked = $false
$nextSpriteSheetMustStartFromModelSheet = $false
$readyForAaa = $false

function Invoke-VisualSourceSelfCheck {
    $results = @()
    $blocked = @('res/sprites/taina/candidates_v05/*')
    $script:findings = @(); $script:blockingStatuses = @(); $script:creativeBlockingStatuses = @()
    $deep = [ordered]@{ leaf = 'safe' }
    for ($i = 0; $i -lt 20; $i++) { $deep = [pscustomobject]@{ child = $deep } }
    $timer = [Diagnostics.Stopwatch]::StartNew()
    Test-ObjectForLineageReference ([pscustomobject]@{ data = $deep; flags = @(1, $true, $false, 9) }) '' 'deep.json' @('source') $blocked
    $timer.Stop()
    $results += [pscustomobject]@{ name = 'deep_json_and_scalar_arrays_finish'; passed = (($script:findings.Count -eq 0) -and ($timer.ElapsedMilliseconds -lt 5000)) }

    $script:findings = @(); $script:blockingStatuses = @(); $script:creativeBlockingStatuses = @()
    Test-ObjectForLineageReference ([pscustomobject]@{ source = 'res/sprites/taina/candidates_v05/a.png' }) '' 'direct.json' @('source') $blocked
    $results += [pscustomobject]@{ name = 'direct_forbidden_source_detected'; passed = ($script:blockingStatuses -contains 'visual_lineage_forbidden_reference') }

    $script:findings = @(); $script:blockingStatuses = @(); $script:creativeBlockingStatuses = @()
    Test-ObjectForLineageReference ([pscustomobject]@{ nested = [pscustomobject]@{ source = 'res/sprites/taina/candidates_v05/a.png' } }) '' 'nested.json' @('source') $blocked
    $results += [pscustomobject]@{ name = 'deep_forbidden_source_detected'; passed = ($script:blockingStatuses -contains 'visual_lineage_forbidden_reference') }

    $script:findings = @(); $script:blockingStatuses = @(); $script:creativeBlockingStatuses = @()
    Test-ObjectForLineageReference ([pscustomobject]@{ evidence = 'res/sprites/taina/candidates_v05/a.png'; comparison = 'res/sprites/taina/candidates_v05/a.png' }) '' 'history.json' @('source') $blocked
    $results += [pscustomobject]@{ name = 'historical_evidence_text_allowed'; passed = ($script:findings.Count -eq 0) }

    $temp = Join-Path ([IO.Path]::GetTempPath()) ('visual_source_selfcheck_' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $temp | Out-Null
    try {
        Set-Content -LiteralPath (Join-Path $temp 'visual_source_of_truth_taina_v01.json') -Value '{}' -Encoding UTF8
        Set-Content -LiteralPath (Join-Path $temp 'visual_source_of_truth_taina_v02.json') -Value '{}' -Encoding UTF8
        $selected = Get-ChildItem -LiteralPath $temp -Filter 'visual_source_of_truth*.json' -File | Sort-Object @{ Expression = { if ($_.Name -match '_v(\d+)\.json$') { [int]$Matches[1] } else { -1 } }; Descending = $true }, FullName | Select-Object -First 1
        $results += [pscustomobject]@{ name = 'selects_highest_contract_version'; passed = ($selected.Name -eq 'visual_source_of_truth_taina_v02.json') }
    } finally { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
    $failed = @($results | Where-Object { -not $_.passed })
    [pscustomobject]@{ command = 'validate_visual_source_of_truth'; self_check = $true; fixtures = $results; fixtures_passed = $results.Count - $failed.Count; fixtures_total = $results.Count; blocking = ($failed.Count -gt 0) } | ConvertTo-Json -Depth 6
    if ($failed.Count -gt 0) { exit 1 }
    exit 0
}

if ($SelfCheck) { Invoke-VisualSourceSelfCheck }

try {
    if (-not (Test-Path -LiteralPath $ProjectRoot)) {
        Add-Finding 'visual_project_root_missing' 'ERROR' "ProjectRoot nao encontrado." "" "" $ProjectRoot
        Write-ReportAndExit 1
    }

    if (-not $ContractPath) {
        $contractsRoot = Join-Path $ProjectRoot 'doc\contracts'
        if (Test-Path -LiteralPath $contractsRoot) {
            $candidate = Get-ChildItem -LiteralPath $contractsRoot -Filter 'visual_source_of_truth*.json' -File -ErrorAction SilentlyContinue |
                Sort-Object @{ Expression = {
                    if ($_.Name -match '_v(\d+)\.json$') { [int]$Matches[1] } else { -1 }
                }; Descending = $true }, FullName |
                Select-Object -First 1
            if ($candidate) { $ContractPath = $candidate.FullName }
        }
    }

    if (-not $ContractPath -or -not (Test-Path -LiteralPath $ContractPath)) {
        Add-Finding 'visual_source_of_truth_missing' 'ERROR' "Contrato visual_source_of_truth nao encontrado."
        Write-ReportAndExit 1
    }

    if ($SchemaPath -and -not (Test-Path -LiteralPath $SchemaPath)) {
        Add-Finding 'visual_source_schema_missing' 'ERROR' "Schema visual_source_of_truth nao encontrado." "" "" $SchemaPath
    }

    $raw = Get-Content -LiteralPath $ContractPath -Raw -Encoding UTF8
    $contract = $raw | ConvertFrom-Json

    $requiredFields = @(
        'schema_version',
        'asset_id',
        'approved_authorial_source',
        'allowed_generation_sources',
        'forbidden_generation_sources',
        'obsolete_assets',
        'lineage_scan_policy',
        'decision'
    )
    foreach ($field in $requiredFields) {
        if (-not $contract.PSObject.Properties[$field]) {
            Add-Finding 'visual_source_contract_invalid' 'ERROR' "Campo obrigatorio ausente em visual_source_of_truth." $ContractPath $field
        }
    }

    $approvedAuthorialSource = Get-JsonPropertyValue $contract 'approved_authorial_source' $null
    $allowedSources = @((Get-JsonPropertyValue $contract 'allowed_generation_sources' @()))
    $forbiddenSources = @((Get-JsonPropertyValue $contract 'forbidden_generation_sources' @()))
    $obsoleteAssets = @((Get-JsonPropertyValue $contract 'obsolete_assets' @()))
    $partialRuntimeCandidates = @((Get-JsonPropertyValue $contract 'partial_runtime_candidates' @()))
    $decision = Get-JsonPropertyValue $contract 'decision' $null
    $generationSourceLocked = [bool](Get-JsonPropertyValue $decision 'generation_source_locked' $false)
    $nextSpriteSheetMustStartFromModelSheet = [bool](Get-JsonPropertyValue $decision 'next_sprite_sheet_must_start_from_model_sheet' $false)
    $readyForAaa = [bool](Get-JsonPropertyValue $decision 'ready_for_aaa' $false)

    if (-not $generationSourceLocked -or -not $nextSpriteSheetMustStartFromModelSheet) {
        Add-Finding 'visual_source_decision_not_locked' 'ERROR' "Contrato nao trava a proxima geracao no model sheet aprovado." $ContractPath 'decision'
    }

    $approvedPath = Normalize-VisualPath (Get-JsonPropertyValue $approvedAuthorialSource 'path' '')
    if (-not $approvedPath) {
        Add-Finding 'approved_authorial_source_missing' 'ERROR' "Fonte autoral aprovada sem path." $ContractPath 'approved_authorial_source.path'
    } else {
        $approvedFullPath = Join-Path $ProjectRoot ($approvedPath -replace '/', '\')
        if (-not (Test-Path -LiteralPath $approvedFullPath)) {
            Add-Finding 'approved_authorial_source_file_missing' 'ERROR' "Arquivo da fonte autoral aprovada nao existe no projeto." $ContractPath 'approved_authorial_source.path' $approvedPath
        }
    }

    $forbiddenPatterns = New-Object System.Collections.Generic.List[string]
    foreach ($pattern in $forbiddenSources) {
        $normalized = Normalize-VisualPath $pattern
        if ($normalized) { $forbiddenPatterns.Add($normalized) }
    }
    foreach ($obsolete in $obsoleteAssets) {
        $path = Normalize-VisualPath (Get-JsonPropertyValue $obsolete 'path' '')
        if ($path) { $forbiddenPatterns.Add($path) }
    }
    foreach ($candidate in $partialRuntimeCandidates) {
        $path = Normalize-VisualPath (Get-JsonPropertyValue $candidate 'path' '')
        if ($path) { $forbiddenPatterns.Add($path) }
    }

    foreach ($source in $allowedSources) {
        $sourcePath = Normalize-VisualPath (Get-JsonPropertyValue $source 'path' '')
        $role = [string](Get-JsonPropertyValue $source 'role' '')
        if (-not $sourcePath) {
            Add-Finding 'allowed_generation_source_missing_path' 'ERROR' "Fonte permitida sem path." $ContractPath 'allowed_generation_sources.path'
            continue
        }
        if ($role -notin @('model_sheet', 'visual_dna', 'direction_brief', 'art_gameplay_direction_gate', 'lineart_blocking', 'human_review_record')) {
            Add-Finding 'allowed_generation_source_invalid_role' 'ERROR' "Fonte permitida usa role nao autorizado para geracao visual." $ContractPath 'allowed_generation_sources.role' $sourcePath
        }
        foreach ($pattern in $forbiddenPatterns) {
            if (Test-VisualPatternMatch $sourcePath $pattern) {
                Add-Finding 'forbidden_generation_source_used' 'ERROR' "Fonte permitida aponta para diretorio/padrao proibido." $ContractPath 'allowed_generation_sources.path' $sourcePath
                break
            }
        }
        foreach ($obsolete in $obsoleteAssets) {
            $obsoletePath = Normalize-VisualPath (Get-JsonPropertyValue $obsolete 'path' '')
            if ($obsoletePath -and (Test-VisualPatternMatch $sourcePath $obsoletePath)) {
                Add-Finding 'obsolete_generation_source_used' 'ERROR' "Asset obsoleto foi usado como fonte de geracao." $ContractPath 'allowed_generation_sources.path' $sourcePath
                break
            }
        }
        foreach ($candidate in $partialRuntimeCandidates) {
            $candidatePath = Normalize-VisualPath (Get-JsonPropertyValue $candidate 'path' '')
            if ($candidatePath -and (Test-VisualPatternMatch $sourcePath $candidatePath)) {
                Add-Finding 'runtime_candidate_used_as_generation_source' 'ERROR' "Runtime candidate parcial foi usado como fonte de geracao." $ContractPath 'allowed_generation_sources.path' $sourcePath
                break
            }
        }
    }

    $lineagePolicy = Get-JsonPropertyValue $contract 'lineage_scan_policy' $null
    $blockedFields = @((Get-JsonPropertyValue $lineagePolicy 'blocked_fields' @()) | ForEach-Object { ([string]$_).ToLowerInvariant() })
    if ($blockedFields.Count -eq 0) {
        $blockedFields = @('source', 'baseline', 'reference_for_generation', 'img2img_base', 'generation_source', 'image_reference')
    }
    $scanRoots = @((Get-JsonPropertyValue $lineagePolicy 'scan_roots' @()))
    foreach ($root in $scanRoots) {
        $rootPath = Join-Path $ProjectRoot ([string]$root -replace '/', '\')
        if (-not (Test-Path -LiteralPath $rootPath)) { continue }

        $files = Get-ChildItem -LiteralPath $rootPath -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension.ToLowerInvariant() -in @('.json', '.md', '.txt', '.py', '.ps1') }
        foreach ($file in $files) {
            $relativeFile = ConvertTo-RelativePath $file.FullName
            if ((Normalize-VisualPath $file.FullName) -eq (Normalize-VisualPath $ContractPath)) {
                continue
            }

            try {
                if ($file.Extension.ToLowerInvariant() -eq '.json') {
                    $json = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                    Test-ObjectForLineageReference $json "" $relativeFile $blockedFields @($forbiddenPatterns)
                    if ($relativeFile -like 'out/logs/visual_delivery_gate_report*.json') {
                        $reportReadyForAaa = [bool](Get-JsonPropertyValue $json 'ready_for_aaa' $false)
                        $reportCreativeBlockers = @((Get-JsonPropertyValue $json 'creative_blocking_statuses' @()))
                        $visualVdpStatus = [string](Get-JsonPropertyValue $json 'visual_vdp_dump_status' '')
                        $visualRouteStatus = [string](Get-JsonPropertyValue $json 'visual_route_status' '')
                        $hasPartialVisualGate =
                            ($reportCreativeBlockers -contains 'human_visual_review_missing_for_aaa') -or
                            ($reportCreativeBlockers -contains 'visual_vdp_dump_missing') -or
                            ($reportCreativeBlockers -contains 'visual_gate_blocked') -or
                            ($reportCreativeBlockers -contains 'runtime_60fps_metrics_missing') -or
                            ($visualVdpStatus -eq 'missing') -or
                            ($visualRouteStatus -eq 'visual_gate_blocked')
                        if ($reportReadyForAaa -and $hasPartialVisualGate) {
                            Add-Finding `
                                -Code 'visual_partial_pass_promoted_to_aaa' `
                                -Severity 'ERROR' `
                                -Message "Relatorio visual tentou promover ready_for_aaa com revisao humana, VDP dump, runtime metrics ou gate visual ainda pendente." `
                                -File $relativeFile `
                                -Field 'ready_for_aaa'
                        }
                    }
                    $script:scanFindings += [pscustomobject]@{
                        file = $relativeFile
                        kind = 'json_scanned'
                    }
                } else {
                    $lines = @(Get-Content -LiteralPath $file.FullName -Encoding UTF8)
                    for ($i = 0; $i -lt $lines.Count; $i++) {
                        $line = Normalize-VisualPath $lines[$i]
                        $fieldHit = $false
                        foreach ($field in $blockedFields) {
                            if ($line.Contains($field.ToLowerInvariant())) {
                                $fieldHit = $true
                                break
                            }
                        }
                        if (-not $fieldHit) { continue }
                        foreach ($pattern in $forbiddenPatterns) {
                            $trimmedPattern = (Normalize-VisualPath $pattern).TrimEnd('*')
                            if ($line.Contains($trimmedPattern)) {
                                Add-Finding `
                                    -Code 'visual_lineage_forbidden_reference' `
                                    -Severity 'ERROR' `
                                    -Message "Texto de builder/prompt usa sprite sheet derivada/reprovada como origem de geracao." `
                                    -File $relativeFile `
                                    -Field ("line:{0}" -f ($i + 1))
                                break
                            }
                        }
                    }
                    $script:scanFindings += [pscustomobject]@{
                        file = $relativeFile
                        kind = 'text_scanned'
                    }
                }
            } catch {
                Add-Finding 'visual_lineage_scan_read_failed' 'ERROR' "Falha ao ler arquivo durante varredura de linhagem visual: $($_.Exception.Message)" $relativeFile
            }
        }
    }

    if ($blockingStatuses.Count -gt 0) {
        Write-ReportAndExit 1
    }
    Write-ReportAndExit 0
} catch {
    Add-Finding 'visual_source_validator_exception' 'ERROR' "Excecao no validador de fonte visual: $($_.Exception.Message)"
    Write-ReportAndExit 1
}

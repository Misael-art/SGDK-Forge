<#
.SYNOPSIS
    Audita semanticamente campanhas de ROMs de efeitos para evitar falso verde AAA.

.DESCRIPTION
    Este auditor nao substitui build, BlastEm ou validate_resources.ps1. Ele procura
    o tipo de falsa entrega que passa por checks estruturais: projetos repetidos,
    fallback procedural generico, painel de texto/debug vendido como microfase,
    tecnicas sem APIs/assets correspondentes e reports que dizem ready_for_aaa
    apesar de gates visuais/closeout ausentes ou stale.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$WorkspaceRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$CampaignRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$ProjectsRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$ReportPath = "",

    [Parameter(Mandatory = $false)]
    [string]$MarkdownPath = "",

    [Parameter(Mandatory = $false)]
    [switch]$FailOnBlocker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-DefaultWorkspaceRoot {
    $wrapperRoot = Split-Path -Parent $PSCommandPath
    return (Split-Path (Split-Path $wrapperRoot -Parent) -Parent)
}

function Get-TextOrEmpty {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return "" }
    try { return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8) } catch { return "" }
}

function Read-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}

function Add-Finding {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.Generic.List[object]]$List,
        [Parameter(Mandatory = $true)][string]$Severity,
        [Parameter(Mandatory = $true)][string]$Code,
        [Parameter(Mandatory = $true)][string]$Message,
        [Parameter(Mandatory = $false)][string]$Project = "",
        [Parameter(Mandatory = $false)][string]$File = "",
        [Parameter(Mandatory = $false)][hashtable]$Extra = @{}
    )

    $payload = [ordered]@{
        severity = $Severity
        code = $Code
        message = $Message
        project = $Project
        file = $File
    }
    foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
    $List.Add([pscustomobject]$payload) | Out-Null
}

function Test-ObjectTruthy {
    param($Value)
    if ($null -eq $Value) { return $false }
    if ($Value -is [bool]) { return [bool]$Value }
    $text = ([string]$Value).Trim().ToLowerInvariant()
    return $text -in @("true", "1", "yes", "sim", "ok", "passed", "pass")
}

function Get-PropertyValue {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    if ($Object.PSObject.Properties.Name -contains $Name) { return $Object.$Name }
    return $Default
}

function Get-AxisSlugFromProjectName {
    param([string]$Name)
    if ($Name -match '^AAA EFFECT LAB - (.+?) \[VER\.001\] \[SGDK 211\] \[GEN\] \[LAB\] \[TECHDEMO\]$') {
        return $Matches[1]
    }
    return ""
}

function Test-SourceHasAny {
    param([string]$SourceText, [string[]]$Patterns)
    foreach ($pattern in $Patterns) {
        if ($SourceText -match $pattern) { return $true }
    }
    return $false
}

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = Resolve-DefaultWorkspaceRoot
}
$WorkspaceRoot = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
if ([string]::IsNullOrWhiteSpace($CampaignRoot)) {
    $CampaignRoot = Join-Path $WorkspaceRoot "SGDK_projects\data\aaa_effect_lab_campaign"
}
if ([string]::IsNullOrWhiteSpace($ProjectsRoot)) {
    $ProjectsRoot = Join-Path $WorkspaceRoot "SGDK_projects"
}
if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportPath = Join-Path $CampaignRoot "semantic_audit_report.json"
}
if ([string]::IsNullOrWhiteSpace($MarkdownPath)) {
    $MarkdownPath = Join-Path $CampaignRoot "semantic_audit_report.md"
}

$findings = [System.Collections.Generic.List[object]]::new()
$projectReports = [System.Collections.Generic.List[object]]::new()

$coveragePath = Join-Path $CampaignRoot "master_coverage_180.json"
$coverage = Read-JsonOrNull -Path $coveragePath
$techniques = @()
if ($null -eq $coverage) {
    Add-Finding -List $findings -Severity "blocker" -Code "coverage_table_missing" -Message "Tabela mestre JSON da campanha ausente ou ilegivel." -File $coveragePath
} else {
    $techniques = @(Get-PropertyValue $coverage "techniques" @())
    if ($techniques.Count -ne 180) {
        Add-Finding -List $findings -Severity "blocker" -Code "coverage_count_not_180" -Message "Tabela mestre nao possui exatamente 180 tecnicas." -File $coveragePath -Extra @{ count = $techniques.Count }
    }

    $proposalOnly = @($techniques | Where-Object {
        ([string](Get-PropertyValue $_ "registry_link" "")) -eq "proposal_only" -or
        ([string](Get-PropertyValue $_ "registry_id" "")) -eq "proposal_only"
    })
    $registryBacked = @($techniques | Where-Object { ([string](Get-PropertyValue $_ "registry_link" "")) -eq "registry_backed" })
    $canonicalCatalogVerified = Test-ObjectTruthy (Get-PropertyValue $coverage "canonical_180_catalog_verified" $false)
    if ($proposalOnly.Count -gt 0 -and -not $canonicalCatalogVerified) {
        Add-Finding -List $findings -Severity "blocker" -Code "canonical_180_identity_unverified" -Message "A campanha usa entradas proposal_only sem catalogo canonico 180 verificado; isto permite inflar cobertura." -File $coveragePath -Extra @{
            proposal_only = $proposalOnly.Count
            registry_backed = $registryBacked.Count
        }
    }

    $fallbackGroups = $techniques |
        Group-Object { ([string](Get-PropertyValue $_ "fallback" "")).Trim().ToLowerInvariant() } |
        Where-Object { $_.Name -ne "" } |
        Sort-Object Count -Descending
    foreach ($group in $fallbackGroups) {
        if ($group.Count -ge 8 -and $group.Name -match 'fallback procedural|texto curto|bg_a/b|variacao temporal segura|varia[cç]ao temporal segura') {
            Add-Finding -List $findings -Severity "blocker" -Code "mass_generic_procedural_fallback" -Message "Fallback procedural generico foi reutilizado em massa no lugar de implementar intencao especifica dos efeitos." -File $coveragePath -Extra @{
                repeated_count = $group.Count
                fallback = $group.Name
            }
            break
        }
    }

    $emptyLibCases = @($registryBacked | Where-Object { @((Get-PropertyValue $_ "lib_cases_consulted" @())).Count -eq 0 })
    if ($registryBacked.Count -gt 0 -and $emptyLibCases.Count -eq $registryBacked.Count) {
        Add-Finding -List $findings -Severity "blocker" -Code "registry_backed_without_lib_cases" -Message "Entradas registry_backed nao registram consulta a lib_cases; o agente pulou memoria tecnica reutilizavel." -File $coveragePath -Extra @{
            registry_backed = $registryBacked.Count
        }
    }
}

$projectDirs = @()
if (Test-Path -LiteralPath $ProjectsRoot -PathType Container) {
    $projectDirs = @(Get-ChildItem -LiteralPath $ProjectsRoot -Directory -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match '^AAA EFFECT LAB - .+ \[VER\.001\] \[SGDK 211\] \[GEN\] \[LAB\] \[TECHDEMO\]$'
    })
}
if ($projectDirs.Count -ne 17) {
    Add-Finding -List $findings -Severity "blocker" -Code "axis_project_count_not_17" -Message "Quantidade de projetos AAA EFFECT LAB diferente de 17." -File $ProjectsRoot -Extra @{ count = $projectDirs.Count }
}

foreach ($projectDir in $projectDirs) {
    $projectRoot = $projectDir.FullName
    $axisSlug = Get-AxisSlugFromProjectName -Name $projectDir.Name
    $srcText = ""
    $srcFiles = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot "src") -Recurse -Include "*.c", "*.h", "*.s" -File -ErrorAction SilentlyContinue)
    foreach ($src in $srcFiles) { $srcText += "`n" + (Get-TextOrEmpty -Path $src.FullName) }
    $srcLower = $srcText.ToLowerInvariant()

    $resFiles = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot "res") -Recurse -File -ErrorAction SilentlyContinue)
    $resText = ""
    foreach ($res in @($resFiles | Where-Object { $_.Extension -eq ".res" -or $_.Extension -eq ".h" })) {
        $resText += "`n" + (Get-TextOrEmpty -Path $res.FullName)
    }
    $resLower = $resText.ToLowerInvariant()

    $projectBlockers = [System.Collections.Generic.List[string]]::new()
    $projectWarnings = [System.Collections.Generic.List[string]]::new()

    $debugMarkers = @(
        'fallback procedural',
        'safe rhythm lane',
        'efeito empurra',
        've pulso',
        'effect_names',
        'drawbackground',
        'draweffectpanel',
        'use_line_scroll 0',
        'microfase de laboratorio'
    )
    $markerHits = @()
    foreach ($marker in $debugMarkers) {
        if ($srcLower -match [regex]::Escape($marker)) { $markerHits += $marker }
    }
    $drawTextCount = ([regex]::Matches($srcText, 'VDP_drawText')).Count + ([regex]::Matches($srcText, 'VDP_drawTextBG')).Count
    $spriteApiCount = ([regex]::Matches($srcText, '\bSPR_')).Count
    $imageMapDeclarations = ([regex]::Matches($resText, '^\s*(IMAGE|MAP|SPRITE|TILESET)\s+', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
    $labBgOnly = ($resFiles.Count -le 4 -and $resLower -match 'lab_bg_b' -and $resLower -notmatch 'sprite|map|tileset')

    if ($markerHits.Count -ge 2 -or ($drawTextCount -ge 12 -and $spriteApiCount -eq 0 -and $imageMapDeclarations -le 1)) {
        $projectBlockers.Add("generic_debug_text_panel") | Out-Null
        Add-Finding -List $findings -Severity "blocker" -Code "generic_debug_text_panel" -Message "Projeto parece painel procedural/debug, nao microfase AAA jogavel." -Project $projectDir.Name -File (Join-Path $projectRoot "src") -Extra @{
            marker_hits = @($markerHits)
            draw_text_calls = $drawTextCount
            sprite_api_calls = $spriteApiCount
            image_map_declarations = $imageMapDeclarations
        }
    }

    if ($labBgOnly) {
        $projectBlockers.Add("generic_lab_resource_set") | Out-Null
        Add-Finding -List $findings -Severity "blocker" -Code "generic_lab_resource_set" -Message "Projeto usa conjunto de recursos generico de laboratorio; isso nao sustenta visual AAA por eixo." -Project $projectDir.Name -File (Join-Path $projectRoot "res") -Extra @{
            resource_count = $resFiles.Count
        }
    }

    $axisRequirements = @{
        "distorcao-raster-hint" = @("VDP_setHorizontalScrollLine", "SYS_setHIntCallback", "VDP_setHIntCounter", "HSCROLL_LINE", "VDP_setScrollingMode", "VDP_setVerticalScroll")
        "pseudo-3d" = @("VDP_setHorizontalScrollLine", "HSCROLL_LINE", "zmap", "road", "VDP_setScrollingMode")
        "paleta-cor" = @("PAL_set", "PAL_fade", "VDP_setHilightShadow", "CRAM")
        "iluminacao-dinamica" = @("VDP_setHilightShadow", "PAL_set", "shadow", "highlight")
        "audio-visual-sync" = @("XGM_", "SND_", "PCM", "Z80", "WAV", "VGM")
        "hud-ui" = @("WINDOW", "VDP_setWindow", "VDP_drawText", "SPR_")
        "rotacao" = @("SPR_", "rotation", "angle", "rot")
        "zoom-escala" = @("SPR_", "scale", "zoom", "VDP_setHorizontalScrollLine")
    }
    if ($axisRequirements.ContainsKey($axisSlug)) {
        $haystack = $srcText + "`n" + $resText
        if (-not (Test-SourceHasAny -SourceText $haystack -Patterns $axisRequirements[$axisSlug])) {
            $projectBlockers.Add("axis_api_signature_missing") | Out-Null
            Add-Finding -List $findings -Severity "blocker" -Code "axis_api_signature_missing" -Message "Eixo nao usa assinaturas minimas de API/asset esperadas para sua tecnica; ha risco de ROM generica." -Project $projectDir.Name -File $projectRoot -Extra @{
                axis_slug = $axisSlug
                expected_any = @($axisRequirements[$axisSlug])
            }
        }
    }

    $validationPath = Join-Path $projectRoot "out\logs\validation_report.json"
    $validation = Read-JsonOrNull -Path $validationPath
    if ($null -eq $validation) {
        $projectBlockers.Add("validation_report_missing") | Out-Null
        Add-Finding -List $findings -Severity "blocker" -Code "validation_report_missing" -Message "validation_report.json ausente ou ilegivel." -Project $projectDir.Name -File $validationPath
    } else {
        $readyForAaa = Test-ObjectTruthy (Get-PropertyValue (Get-PropertyValue $validation "status_panel" $null) "ready_for_aaa" $false)
        $blockingStatuses = @((Get-PropertyValue $validation "blocking_statuses" @()))
        if ($readyForAaa -and $blockingStatuses.Count -gt 0) {
            $projectBlockers.Add("ready_for_aaa_with_blockers") | Out-Null
            Add-Finding -List $findings -Severity "blocker" -Code "ready_for_aaa_with_blockers" -Message "validation_report declara ready_for_aaa=true apesar de blocking_statuses." -Project $projectDir.Name -File $validationPath -Extra @{
                blocking_statuses = @($blockingStatuses)
            }
        }

        $observedReports = Get-PropertyValue $validation "observed_reports" $null
        if ($null -eq $observedReports) {
            $observedReports = Get-PropertyValue $validation "wrapper_reports" $null
        }
        foreach ($reportName in @("visual_delivery_gate", "freshness_audit", "scene_closeout_gate", "res_graph")) {
            $reportStatus = Get-PropertyValue $observedReports $reportName $null
            if ($null -eq $reportStatus -and $reportName -eq "visual_delivery_gate") {
                $statusPanel = Get-PropertyValue $validation "status_panel" $null
                $evidence = Get-PropertyValue $validation "evidence" $null
                $visualGatePath = [string](Get-PropertyValue $evidence "visual_delivery_gate_report_path" "")
                $visualGate = if (-not [string]::IsNullOrWhiteSpace($visualGatePath)) { Read-JsonOrNull -Path $visualGatePath } else { $null }
                $visualGateReady = Test-ObjectTruthy (Get-PropertyValue $statusPanel "visual_gate_ready" $false)
                $romIdentity = Get-PropertyValue $evidence "rom_identity" $null
                $validationRomSha = [string](Get-PropertyValue $romIdentity "sha256" "")
                $visualGateRomSha = [string](Get-PropertyValue $visualGate "rom_sha256" "")
                $reportStatus = [pscustomobject][ordered]@{
                    report_present = ($visualGateReady -and $null -ne $visualGate)
                    stale = (-not $visualGateReady -or ($validationRomSha -and $visualGateRomSha -and $validationRomSha -ne $visualGateRomSha))
                }
            }
            $present = Test-ObjectTruthy (Get-PropertyValue $reportStatus "report_present" $false)
            $stale = Test-ObjectTruthy (Get-PropertyValue $reportStatus "stale" $false)
            if ($readyForAaa -and (-not $present -or $stale)) {
                $projectBlockers.Add("ready_for_aaa_with_unproven_$reportName") | Out-Null
                Add-Finding -List $findings -Severity "blocker" -Code "ready_for_aaa_with_unproven_report" -Message "ready_for_aaa=true com report obrigatorio ausente ou stale." -Project $projectDir.Name -File $validationPath -Extra @{
                    report_name = $reportName
                    report_present = $present
                    stale = $stale
                }
            }
        }
    }

    $effectNotesPath = Join-Path $projectRoot "out\agent_learning\effect_implementation_notes.json"
    $effectNotes = Read-JsonOrNull -Path $effectNotesPath
    if ($effectNotes) {
        $items = @()
        if ($effectNotes.PSObject.Properties.Name -contains "effects") { $items = @($effectNotes.effects) }
        elseif ($effectNotes.PSObject.Properties.Name -contains "techniques") { $items = @($effectNotes.techniques) }
        if ($items.Count -gt 0) {
            $fallbackNoteGroups = $items | Group-Object { ([string](Get-PropertyValue $_ "fallback" "") + [string](Get-PropertyValue $_ "fallback_used" "") + [string](Get-PropertyValue $_ "implementation_note" "")).Trim().ToLowerInvariant() } | Sort-Object Count -Descending
            $topGroup = @($fallbackNoteGroups | Where-Object { $_.Name }) | Select-Object -First 1
            if ($topGroup -and $topGroup.Count -ge [Math]::Max(3, [int]($items.Count * 0.6))) {
                $projectBlockers.Add("repeated_effect_learning_notes") | Out-Null
                Add-Finding -List $findings -Severity "blocker" -Code "repeated_effect_learning_notes" -Message "Notas de implementacao/aprendizado repetem o mesmo texto para a maioria dos efeitos; aprendizado local provavelmente nao foi observado de verdade." -Project $projectDir.Name -File $effectNotesPath -Extra @{
                    repeated_count = $topGroup.Count
                    total = $items.Count
                }
            }
        }
    } else {
        $projectWarnings.Add("effect_learning_notes_missing") | Out-Null
        Add-Finding -List $findings -Severity "warning" -Code "effect_learning_notes_missing" -Message "effect_implementation_notes.json ausente ou ilegivel." -Project $projectDir.Name -File $effectNotesPath
    }

    $projectReports.Add([pscustomobject][ordered]@{
        project = $projectDir.Name
        axis_slug = $axisSlug
        blockers = @($projectBlockers)
        warnings = @($projectWarnings)
        src_files = $srcFiles.Count
        res_files = $resFiles.Count
        draw_text_calls = $drawTextCount
        sprite_api_calls = $spriteApiCount
        image_map_declarations = $imageMapDeclarations
    }) | Out-Null
}

$blockers = @($findings | Where-Object { $_.severity -eq "blocker" })
$warnings = @($findings | Where-Object { $_.severity -eq "warning" })
$summary = [ordered]@{
    status = if ($blockers.Count -gt 0) { "failed" } else { "passed" }
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    workspace_root = $WorkspaceRoot
    campaign_root = $CampaignRoot
    projects_root = $ProjectsRoot
    projects_checked = $projectDirs.Count
    blockers = $blockers.Count
    warnings = $warnings.Count
    total_techniques = $techniques.Count
    proposal_only = @($techniques | Where-Object { ([string](Get-PropertyValue $_ "registry_link" "")) -eq "proposal_only" }).Count
    registry_backed = @($techniques | Where-Object { ([string](Get-PropertyValue $_ "registry_link" "")) -eq "registry_backed" }).Count
}

$report = [ordered]@{
    schema = "effect_campaign_semantic_audit.v1"
    summary = $summary
    findings = @($findings)
    projects = @($projectReports)
}

$reportDir = Split-Path -Parent $ReportPath
if ($reportDir -and -not (Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
}
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($ReportPath, ($report | ConvertTo-Json -Depth 16), $utf8NoBom)

$md = New-Object System.Collections.Generic.List[string]
$md.Add("# Semantic Audit Report") | Out-Null
$md.Add("") | Out-Null
$md.Add(('- status: `{0}`' -f $summary.status)) | Out-Null
$md.Add(('- projects_checked: `{0}`' -f $summary.projects_checked)) | Out-Null
$md.Add(('- blockers: `{0}`' -f $summary.blockers)) | Out-Null
$md.Add(('- warnings: `{0}`' -f $summary.warnings)) | Out-Null
$md.Add(('- total_techniques: `{0}`' -f $summary.total_techniques)) | Out-Null
$md.Add(('- proposal_only: `{0}`' -f $summary.proposal_only)) | Out-Null
$md.Add(('- registry_backed: `{0}`' -f $summary.registry_backed)) | Out-Null
$md.Add("") | Out-Null
$md.Add("## Blockers") | Out-Null
if ($blockers.Count -eq 0) {
    $md.Add("- none") | Out-Null
} else {
    foreach ($finding in $blockers) {
        $scope = if ($finding.project) { $finding.project } else { $finding.file }
        $md.Add(('- `{0}`: {1} ({2})' -f $finding.code, $finding.message, $scope)) | Out-Null
    }
}
$md.Add("") | Out-Null
$md.Add("## Warnings") | Out-Null
if ($warnings.Count -eq 0) {
    $md.Add("- none") | Out-Null
} else {
    foreach ($finding in $warnings) {
        $scope = if ($finding.project) { $finding.project } else { $finding.file }
        $md.Add(('- `{0}`: {1} ({2})' -f $finding.code, $finding.message, $scope)) | Out-Null
    }
}

$markdownDir = Split-Path -Parent $MarkdownPath
if ($markdownDir -and -not (Test-Path -LiteralPath $markdownDir)) {
    New-Item -ItemType Directory -Force -Path $markdownDir | Out-Null
}
[System.IO.File]::WriteAllText($MarkdownPath, ($md -join [Environment]::NewLine), $utf8NoBom)

Write-Host ("Semantic audit status: {0} | blockers={1} warnings={2}" -f $summary.status, $summary.blockers, $summary.warnings)
Write-Host ("JSON: {0}" -f $ReportPath)
Write-Host ("MD: {0}" -f $MarkdownPath)

if ($FailOnBlocker -and $blockers.Count -gt 0) { exit 1 }
exit 0

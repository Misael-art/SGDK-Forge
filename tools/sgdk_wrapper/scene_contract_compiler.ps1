<#
.SYNOPSIS
    Compiles doc/13-spec-cenas.md into doc/scene-contracts.json.
.DESCRIPTION
    Hybrid compiler: recognizes canonical blocks and headings from the scene
    spec, applies limited heuristics for known patterns, and merges with
    doc/scene-regression.json for runtime fields (boot_mode, capture_frame,
    expected_app_scene_id, etc.).

    After writing scene-contracts.json, runs lint_scene_contract.ps1 in
    WarnOnly mode and appends lint status to the compile report.
.NOTES
    doc/scene-contracts.json becomes a compiled artifact, not a handwritten file.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$SpecPath,

    [Parameter(Mandatory = $false)]
    [string]$RegressionPath,

    [Parameter(Mandatory = $false)]
    [ValidateSet('lab', 'production', 'aaa_gate')]
    [string]$Mode = 'lab',

    [Parameter(Mandatory = $false)]
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
$ScriptRoot = $PSScriptRoot
$LibDir = Join-Path $ScriptRoot 'lib'

Import-Module (Join-Path $LibDir 'sgdk_artifact_contracts.psm1') -Force

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if ([string]::IsNullOrWhiteSpace($SpecPath)) {
    $SpecPath = Join-Path $ProjectRoot 'doc\13-spec-cenas.md'
}
if ([string]::IsNullOrWhiteSpace($RegressionPath)) {
    $RegressionPath = Join-Path $ProjectRoot 'doc\scene-regression.json'
}

$ContractPath = Join-Path $ProjectRoot 'doc\scene-contracts.json'
$LogDir = Join-Path $ProjectRoot 'out\logs'
$ReportPath = Join-Path $LogDir 'scene_contract_compile_report.json'

# ---------------------------------------------------------------------------
# Artifact envelope
# ---------------------------------------------------------------------------
$artifact = New-SgdkArtifactEnvelope `
    -ToolName 'scene_contract_compiler' `
    -ToolVersion '0.1.0' `
    -ProjectRoot $ProjectRoot

$artifact['mode'] = $Mode
$artifact['spec_path'] = $SpecPath
$artifact['regression_path'] = $RegressionPath
$artifact['contract_path'] = $ContractPath

$findings = [System.Collections.ArrayList]::new()

function Add-Finding {
    param(
        [string]$SceneId = '_compiler',
        [string]$Severity = 'info',
        [string]$Code,
        [string]$Message
    )
    [void]$findings.Add([ordered]@{
        scene_id = $SceneId
        severity = $Severity
        code     = $Code
        message  = $Message
    })
}

# ---------------------------------------------------------------------------
# Load spec
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $SpecPath -PathType Leaf)) {
    Set-SgdkArtifactFailure -Artifact $artifact -Reason "Spec file not found: $SpecPath"
    Add-Finding -Code 'CC001' -Severity 'error' -Message "Spec file not found: $SpecPath"
    $artifact['findings'] = @($findings.ToArray())
    $artifact['scenes_compiled'] = 0
    Write-SgdkJsonArtifact -Data $artifact -Path $ReportPath | Out-Null
    Write-Host "[FAIL] Spec not found: $SpecPath" -ForegroundColor Red
    if (-not $WarnOnly) { exit 1 }
    exit 0
}

$specLines = Get-Content -LiteralPath $SpecPath -Encoding UTF8

# ---------------------------------------------------------------------------
# Load regression manifest (optional)
# ---------------------------------------------------------------------------
$regressionScenes = @{}
if (Test-Path -LiteralPath $RegressionPath -PathType Leaf) {
    try {
        $regressionManifest = Get-Content -LiteralPath $RegressionPath -Raw | ConvertFrom-Json
        foreach ($rs in $regressionManifest.scenes) {
            $regressionScenes[$rs.scene_id] = $rs
        }
        Add-Finding -Code 'CC010' -Message "Merged with regression manifest: $($regressionScenes.Count) scenes"
    } catch {
        Add-Finding -Code 'CC011' -Severity 'warn' -Message "Failed to parse regression manifest: $($_.Exception.Message)"
    }
} else {
    Add-Finding -Code 'CC012' -Message "Regression manifest not found, skipping merge"
}

# ---------------------------------------------------------------------------
# Load optional cutscene contracts from doc/contracts
# ---------------------------------------------------------------------------
$cutsceneContracts = @{}
$contractsDir = Join-Path $ProjectRoot 'doc\contracts'
if (Test-Path -LiteralPath $contractsDir -PathType Container) {
    foreach ($contractFile in Get-ChildItem -LiteralPath $contractsDir -Filter '*_contract.json' -File -ErrorAction SilentlyContinue) {
        try {
            $candidate = Get-Content -LiteralPath $contractFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Add-Finding -Code 'CC071' -Severity 'warn' -Message "Failed to parse cutscene contract candidate $($contractFile.FullName): $($_.Exception.Message)"
            continue
        }

        $hasSceneId = $candidate.PSObject.Properties['scene_id'] -and -not [string]::IsNullOrWhiteSpace([string]$candidate.scene_id)
        $hasCutsceneShape = $candidate.PSObject.Properties['cutscene_mode'] -and
            $candidate.PSObject.Properties['fsm_script'] -and
            $candidate.PSObject.Properties['resource_plan']

        if (-not $hasSceneId -or -not $hasCutsceneShape) {
            continue
        }

        $cutsceneSceneId = [string]$candidate.scene_id
        if (-not $cutsceneContracts.ContainsKey($cutsceneSceneId)) {
            $cutsceneContracts[$cutsceneSceneId] = $candidate
            Add-Finding -SceneId $cutsceneSceneId -Code 'CC070' -Message "Loaded cutscene contract from doc/contracts/$($contractFile.Name)"
        } else {
            Add-Finding -SceneId $cutsceneSceneId -Code 'CC072' -Severity 'warn' -Message "Duplicate cutscene contract ignored: doc/contracts/$($contractFile.Name)"
        }
    }
}

# ---------------------------------------------------------------------------
# Parse spec: extract scenes from headings
# ---------------------------------------------------------------------------
$scenes = [System.Collections.ArrayList]::new()
$currentScene = $null
$currentSection = $null

# Pattern for scene headings like:
#   ### Cena N - Name
#   ### Cena N - `scene_id`
#   ## Cena: [NOME]
$sceneHeadingPattern = '^(?:###\s+Cena\s+\d+\s*-\s*(.+)|##\s+Cena:\s*(.+))$'
# Pattern for key-value lines like: - key: value
$kvPattern = '^\s*-\s+`?([^:`]+)`?\s*:\s*(.+)$'
# Pattern for working name like: nome de trabalho: `scene_xxx`
$workingNamePattern = 'nome de trabalho.*`([a-z0-9_]+)`'
# Pattern for sub-sections like: - resource_budget_model:
$subSectionPattern = '^\s*-\s+(resource_budget_model|budget alvo|riscos de VDP|contrato de evidencia)\s*:\s*$'

foreach ($line in $specLines) {
    # Detect scene heading
    if ($line -match $sceneHeadingPattern) {
        if ($currentScene) {
            [void]$scenes.Add($currentScene)
        }

        $headingName = if ($matches[1]) { $matches[1].Trim() } else { $matches[2].Trim() }
        # Extract scene_id from backticks in heading
        $sceneId = $null
        if ($headingName -match '`([a-z0-9_]+)`') {
            $sceneId = $matches[1]
        } elseif ($headingName -match '^[a-z0-9_]+$') {
            $sceneId = $headingName
        }

        $currentScene = [ordered]@{
            scene_id             = $sceneId
            source_heading       = $line.Trim()
            scene_role           = $null
            boot_mode            = 'unsupported'
            compile_origin       = 'canonical_block'
            raw_properties       = [ordered]@{}
            resource_budget      = [ordered]@{}
            effects_active       = @()
            risks                = @()
        }
        $currentSection = 'main'
        continue
    }

    # Detect major section headings
    if ($line -match '^##\s+') {
        if ($currentScene) {
            [void]$scenes.Add($currentScene)
            $currentScene = $null
        }
        $currentSection = $null
        continue
    }

    if (-not $currentScene) { continue }

    # Detect sub-sections
    if ($line -match $subSectionPattern) {
        $subName = $matches[1].Trim()
        if ($subName -match 'resource_budget') {
            $currentSection = 'resource_budget'
        } elseif ($subName -match 'riscos') {
            $currentSection = 'risks'
        } elseif ($subName -match 'contrato de evidencia') {
            $currentSection = 'evidence_contract'
        } elseif ($subName -match 'budget') {
            $currentSection = 'budget_target'
        }
        continue
    }

    # Parse key-value lines
    if ($line -match $kvPattern) {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim().TrimEnd(',', ';')

        # Remove backticks from value
        $cleanValue = $value -replace '`', ''

        switch ($currentSection) {
            'resource_budget' {
                $currentScene.resource_budget[$key] = $cleanValue
            }
            'risks' {
                $currentScene.risks += $cleanValue
            }
            default {
                $currentScene.raw_properties[$key] = $cleanValue

                # Extract working name / scene_id
                if ($key -match 'nome de trabalho') {
                    if ($cleanValue -match '([a-z0-9_]+)') {
                        $currentScene.scene_id = $matches[1]
                    }
                }

                # Extract scene role from 'papel' or 'classe de problema'
                if ($key -match 'papel|classe de problema') {
                    $currentScene.raw_properties['papel'] = $cleanValue
                }
            }
        }
        continue
    }

    # Risk lines (indented bullet under risks section)
    if ($currentSection -eq 'risks' -and $line -match '^\s+-\s+(.+)$') {
        $currentScene.risks += $matches[1].Trim()
    }
}

# Don't forget last scene
if ($currentScene) {
    [void]$scenes.Add($currentScene)
}

# ---------------------------------------------------------------------------
# Infer scene_role from context
# ---------------------------------------------------------------------------
function Infer-SceneRole {
    param([System.Collections.IDictionary]$Scene)

    $papel = ''
    if ($null -ne $Scene.raw_properties) {
        $papelValue = $Scene.raw_properties['papel']
        if ($null -ne $papelValue) {
            $papel = ([string]$papelValue).ToLowerInvariant()
        }
    }
    $headingSource = if ($null -ne $Scene.source_heading) { [string]$Scene.source_heading } else { '' }
    $sceneIdSource = if ($null -ne $Scene.scene_id) { [string]$Scene.scene_id } else { '' }
    $heading = $headingSource.ToLowerInvariant()
    $sid = $sceneIdSource.ToLowerInvariant()

    if ($papel -match 'menu|porta de entrada|front.?end|seletor') { return 'menu' }
    if ($heading -match 'front.?end|menu') { return 'menu' }
    if ($sid -match 'menu|front_end') { return 'menu' }

    if ($papel -match 'benchmark|laboratorio|showcase|baseline') { return 'benchmark' }
    if ($heading -match 'showcase|benchmark|lab') { return 'benchmark' }
    if ($sid -match 'showcase|benchmark|lab') { return 'benchmark' }

    if ($papel -match 'boss') { return 'boss' }
    if ($papel -match 'cutscene|cinemat') { return 'cutscene' }
    if ($papel -match 'gameplay|jogabilidade|acao') { return 'gameplay' }
    if ($heading -match 'gameplay|playable') { return 'gameplay' }
    if ($sid -match 'gameplay|playable|first_playable_slice') { return 'gameplay' }
    if ($papel -match 'titulo|title') { return 'title' }
    if ($papel -match 'debug') { return 'debug' }

    return 'lab'
}

function Get-SceneSpecificityScore {
    param([System.Collections.IDictionary]$Scene)

    $score = 0
    if ($null -ne $Scene.resource_budget) {
        $score += @($Scene.resource_budget.Keys).Count * 10
    }
    if ($null -ne $Scene.raw_properties) {
        $score += @($Scene.raw_properties.Keys).Count
    }
    $headingSource = if ($null -ne $Scene.source_heading) { [string]$Scene.source_heading } else { '' }
    if ($headingSource -match '`') {
        $score += 5
    }
    return $score
}

# ---------------------------------------------------------------------------
# Build contract entries
# ---------------------------------------------------------------------------
$contractScenes = [System.Collections.ArrayList]::new()
$scenesCompiled = 0
$sceneMap = [ordered]@{}

foreach ($scene in $scenes) {
    $sid = $scene.scene_id
    if (-not $sid) {
        continue
    }

    if (-not $sceneMap.Contains($sid)) {
        $sceneMap[$sid] = $scene
        continue
    }

    $existing = $sceneMap[$sid]
    $existingScore = Get-SceneSpecificityScore -Scene $existing
    $candidateScore = Get-SceneSpecificityScore -Scene $scene
    if ($candidateScore -gt $existingScore) {
        $sceneMap[$sid] = $scene
    }
}

foreach ($scene in $sceneMap.Values) {
    $sid = $scene.scene_id
    if (-not $sid) {
        Add-Finding -Code 'CC020' -Severity 'warn' -Message "Scene without scene_id from heading: $($scene.source_heading)"
        continue
    }

    $role = Infer-SceneRole -Scene $scene
    $scene.scene_role = $role

    $entry = [ordered]@{
        scene_id        = $sid
        scene_role      = $role
        boot_mode       = 'unsupported'
        compile_origin  = $scene.compile_origin
        source_heading  = $scene.source_heading
    }

    # Copy resource budget if present
    if ($scene.resource_budget.Count -gt 0) {
        $entry['resource_budget_model'] = $scene.resource_budget
    }

    # Copy effects from resource_budget keywords
    $effects = @()
    $sid_lower = $sid.ToLowerInvariant()
    if ($sid_lower -match 'water|fx|hscroll') { $effects += 'raster_scroll' }
    if ($sid_lower -match 'depth|vscroll|column') { $effects += 'column_scroll' }
    if ($sid_lower -match 'multiplane') { $effects += 'multi_plane' }
    if ($effects.Count -gt 0) {
        $entry['effects_active'] = $effects
    }

    # State-changing scenes should declare cleanup
    if ($role -in @('gameplay', 'boss', 'cutscene', 'benchmark')) {
        $entry['cleanup_required'] = $true
    }

    # Merge optional scene-local cutscene contract.
    if ($role -eq 'cutscene' -and $cutsceneContracts.ContainsKey($sid)) {
        $entry['cutscene_contract'] = $cutsceneContracts[$sid]
        Add-Finding -SceneId $sid -Code 'CC073' -Message "Merged cutscene_contract into compiled scene contract"
    }

    # Merge with regression manifest
    if ($regressionScenes.ContainsKey($sid)) {
        $rs = $regressionScenes[$sid]
        $entry.compile_origin = 'merged_with_regression'

        if ($rs.PSObject.Properties['boot_mode']) {
            $entry.boot_mode = $rs.boot_mode
        }
        if ($rs.PSObject.Properties['capture_kind']) {
            $entry['capture_kind'] = $rs.capture_kind
        }
        if ($rs.PSObject.Properties['capture_frame']) {
            $entry['capture_frame'] = $rs.capture_frame
        }
        if ($rs.PSObject.Properties['warmup_frames']) {
            $entry['warmup_frames'] = $rs.warmup_frames
        }
        if ($rs.PSObject.Properties['expected_app_scene_id']) {
            $entry['expected_app_scene_id'] = $rs.expected_app_scene_id
        }
        if ($rs.PSObject.Properties['bootstrap_scene_id']) {
            $entry['bootstrap_scene_id'] = $rs.bootstrap_scene_id
        }
        if ($rs.PSObject.Properties['scene_key']) {
            $entry['scene_key'] = $rs.scene_key
        }
        if ($rs.PSObject.Properties['required_artifacts']) {
            $entry['required_artifacts'] = $rs.required_artifacts
        }
        if ($rs.PSObject.Properties['comparison_artifacts']) {
            $entry['comparison_artifacts'] = $rs.comparison_artifacts
        }
        if ($rs.PSObject.Properties['navigation_sequence']) {
            $entry['navigation_sequence'] = $rs.navigation_sequence
        }

        $entry['regression_required'] = $true
        Add-Finding -SceneId $sid -Code 'CC030' -Message "Merged with regression manifest (boot_mode=$($entry.boot_mode))"
    } else {
        Add-Finding -SceneId $sid -Code 'CC031' -Message "No regression manifest entry - boot_mode remains unsupported"
    }

    # Log inferred fields
    if ($scene.compile_origin -eq 'canonical_block') {
        Add-Finding -SceneId $sid -Code 'CC040' -Message "Inferred scene_role=$role from spec"
    }

    [void]$contractScenes.Add($entry)
    $scenesCompiled++
}

# ---------------------------------------------------------------------------
# Build contract manifest
# ---------------------------------------------------------------------------
$contract = [ordered]@{
    schema_version  = '1.0.0'
    project_profile = $Mode
    compiled_at     = (Get-Date).ToUniversalTime().ToString('o')
    compiled_from   = $SpecPath
    scenes          = @($contractScenes.ToArray())
}

# ---------------------------------------------------------------------------
# Write contract
# ---------------------------------------------------------------------------
$contractDir = Split-Path $ContractPath -Parent
if (-not (Test-Path -LiteralPath $contractDir)) {
    New-Item -ItemType Directory -Path $contractDir -Force | Out-Null
}

$contractChanged = $true
if (Test-Path -LiteralPath $ContractPath -PathType Leaf) {
    try {
        $existingContract = Get-Content -LiteralPath $ContractPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $existingComparable = [ordered]@{
            schema_version  = $existingContract.schema_version
            project_profile = $existingContract.project_profile
            compiled_from   = $existingContract.compiled_from
            scenes          = $existingContract.scenes
        }
        $newComparable = [ordered]@{
            schema_version  = $contract.schema_version
            project_profile = $contract.project_profile
            compiled_from   = $contract.compiled_from
            scenes          = $contract.scenes
        }
        $contractChanged = (($existingComparable | ConvertTo-Json -Depth 10 -Compress) -ne
            ($newComparable | ConvertTo-Json -Depth 10 -Compress))
    } catch {
        $contractChanged = $true
    }
}

if ($contractChanged) {
    $contractJson = $contract | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($ContractPath, $contractJson, [System.Text.Encoding]::UTF8)
    Add-Finding -Code 'CC050' -Message "Wrote $scenesCompiled scenes to $ContractPath"
} else {
    Add-Finding -Code 'CC051' -Message "Contract unchanged; preserved timestamp for $ContractPath"
}

# ---------------------------------------------------------------------------
# Run linter in WarnOnly mode
# ---------------------------------------------------------------------------
$lintResult = [ordered]@{
    lint_ran    = $false
    lint_status = $null
    lint_path   = $null
}

$lintScript = Join-Path $ScriptRoot 'lint_scene_contract.ps1'
if (Test-Path -LiteralPath $lintScript -PathType Leaf) {
    try {
        $lintArgs = @(
            '-File', $lintScript,
            '-ProjectRoot', $ProjectRoot,
            '-ContractPath', $ContractPath,
            '-Mode', $Mode,
            '-WarnOnly'
        )
        $lintArgumentList = @('-NoProfile', '-ExecutionPolicy', 'Bypass') + $lintArgs
        $lintOutput = & powershell.exe @lintArgumentList 2>&1
        foreach ($line in @($lintOutput)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$line)) {
                Write-Host $line
            }
        }
        $lintExitCode = if ($LASTEXITCODE -is [int]) { [int]$LASTEXITCODE } else { 0 }
        $lintResult.lint_ran = $true
        $lintResult.lint_status = if ($lintExitCode -eq 0) { 'ok' } else { 'warn' }
        $lintResult.lint_path = Join-Path $LogDir 'scene_contract_report.json'
        Add-Finding -Code 'CC060' -Message "Lint completed: status=$($lintResult.lint_status)"
    } catch {
        $lintResult.lint_status = 'error'
        Add-Finding -Code 'CC061' -Severity 'warn' -Message "Lint failed: $($_.Exception.Message)"
    }
} else {
    Add-Finding -Code 'CC062' -Severity 'info' -Message "lint_scene_contract.ps1 not found, skipping"
}

# ---------------------------------------------------------------------------
# Assemble and write compile report
# ---------------------------------------------------------------------------
$artifact['scenes_compiled'] = $scenesCompiled
$artifact['lint_result'] = $lintResult
$artifact['findings'] = @($findings.ToArray())

$hasErrors = @($findings | Where-Object { $_.severity -eq 'error' }).Count -gt 0
if ($hasErrors -and -not $WarnOnly) {
    Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Compilation had errors'
}

Write-SgdkJsonArtifact -Data $artifact -Path $ReportPath | Out-Null

# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------
Write-Host ''
Write-Host "[COMPILED] $scenesCompiled scenes from spec -> $ContractPath" -ForegroundColor Green
Write-Host "  Mode: $Mode"
$lintStatusLabel = if ($null -ne $lintResult.lint_status -and -not [string]::IsNullOrWhiteSpace([string]$lintResult.lint_status)) {
    [string]$lintResult.lint_status
} else {
    'skipped'
}
Write-Host "  Lint: $lintStatusLabel"
Write-Host "  Findings: $($findings.Count)"
Write-Host "  Report: $ReportPath"

if ($hasErrors -and -not $WarnOnly) { exit 1 }
exit 0

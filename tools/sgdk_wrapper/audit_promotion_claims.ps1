<#
.SYNOPSIS
    Reconciles delivery claims with fresh, scoped evidence for the current ROM.
.DESCRIPTION
    This gate prevents promotion by inventory, screenshot extrapolation,
    procedural asset score, manual closeout reports, non-MDRT statistics, or
    optimistic report selection. It writes a deterministic machine-readable
    report and exits non-zero when a requested claim exceeds its evidence.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$ManifestPath = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-PropertyValue {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    if ($Object -is [System.Collections.IDictionary]) {
        if ($Object.Contains($Name)) { return $Object[$Name] }
        return $Default
    }
    if ($Object.PSObject -and $Object.PSObject.Properties.Name -contains $Name) {
        return $Object.$Name
    }
    return $Default
}

function Test-ClaimRequested {
    param([string]$Id)
    return @($script:RequestedClaims) -contains $Id
}

function Add-Blocker {
    param(
        [string]$Code,
        [string]$Message,
        [string]$Claim = "",
        [string]$Artifact = ""
    )
    if ($script:BlockerCodes -notcontains $Code) {
        $script:BlockerCodes += $Code
    }
    $script:Findings += [ordered]@{
        code = $Code
        message = $Message
        claim = if ([string]::IsNullOrWhiteSpace($Claim)) { $null } else { $Claim }
        artifact = if ([string]::IsNullOrWhiteSpace($Artifact)) { $null } else { $Artifact }
    }
}

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "ProjectRoot not found: $ProjectRoot"
}

if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
    $ManifestPath = Join-Path $ProjectRoot 'doc\promotion_claim_manifest.json'
}
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot 'out\logs\promotion_claim_audit_report.json'
}

$romPath = Join-Path $ProjectRoot 'out\rom.bin'
$romHash = $null
if (Test-Path -LiteralPath $romPath -PathType Leaf) {
    $romHash = (Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
}

$script:BlockerCodes = @()
$script:Findings = @()
$script:RequestedClaims = @()
$leastConsistentStatus = $null

if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    $report = [ordered]@{
        schema_version = '1.0.0'
        generated_at = (Get-Date).ToUniversalTime().ToString('o')
        tool_name = 'audit_promotion_claims'
        project_root = $ProjectRoot
        manifest_path = $ManifestPath
        status = 'not_applicable'
        rom_sha256 = $romHash
        requested_claims = @()
        blocker_codes = @()
        findings = @()
        claim_ceiling = 'no_promotion_requested'
        least_consistent_status = $null
    }
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $OutputPath)) | Out-Null
    $report | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    $report | ConvertTo-Json -Depth 20
    exit 0
}

try {
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Add-Blocker 'promotion_claim_manifest_unreadable' $_.Exception.Message '' $ManifestPath
    $manifest = [pscustomobject]@{ claims = @() }
}

$script:RequestedClaims = @(
    @(Get-PropertyValue $manifest 'claims' @()) |
        ForEach-Object { [string](Get-PropertyValue $_ 'id' '') } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Select-Object -Unique
)

$declaredRomHash = [string](Get-PropertyValue $manifest 'rom_sha256' '')
if ($romHash -and $declaredRomHash -and $declaredRomHash.ToLowerInvariant() -ne $romHash) {
    Add-Blocker 'claim_rom_hash_mismatch' 'The claim manifest targets a different ROM hash.' '' $ManifestPath
}

$evidence = @(Get-PropertyValue $manifest 'evidence' @())
foreach ($item in $evidence) {
    $evidenceHash = [string](Get-PropertyValue $item 'rom_sha256' '')
    $evidencePath = [string](Get-PropertyValue $item 'path' '')
    if ($romHash -and $evidenceHash -and $evidenceHash.ToLowerInvariant() -ne $romHash) {
        Add-Blocker 'claim_rom_hash_mismatch' 'Evidence belongs to a different ROM hash.' '' $evidencePath
    }
    if ($evidencePath) {
        $absoluteEvidencePath = if ([System.IO.Path]::IsPathRooted($evidencePath)) {
            $evidencePath
        } else {
            Join-Path $ProjectRoot $evidencePath
        }
        if ((Test-Path -LiteralPath $absoluteEvidencePath -PathType Leaf) -and
            (Test-Path -LiteralPath $romPath -PathType Leaf)) {
            $evidenceTime = (Get-Item -LiteralPath $absoluteEvidencePath).LastWriteTimeUtc
            $romTime = (Get-Item -LiteralPath $romPath).LastWriteTimeUtc
            if ($evidenceTime -lt $romTime) {
                Add-Blocker 'evidence_predates_rom' 'Evidence is older than the current ROM build.' '' $evidencePath
            }
        }
    }
}

$gameplayClaims = @('first_playable', 'gameplay_rom_aprovada')
$observedScopes = @($evidence | ForEach-Object { [string](Get-PropertyValue $_ 'scope' '') })
foreach ($claimId in $script:RequestedClaims) {
    if ($claimId -in $gameplayClaims) {
        $hasGameplayScope = @($observedScopes | Where-Object { $_ -in @('gameplay', 'full_route', 'result_route') }).Count -gt 0
        if (-not $hasGameplayScope -and $evidence.Count -gt 0) {
            Add-Blocker 'claim_scope_not_observed' 'Boot/title or screenshot evidence cannot prove gameplay.' $claimId
        }
    }
    if ($claimId -eq 'performance_estavel') {
        $hasPerformanceScope = @($observedScopes | Where-Object { $_ -eq 'performance' }).Count -gt 0
        if ($evidence.Count -gt 0 -and -not $hasPerformanceScope) {
            Add-Blocker 'claim_scope_not_observed' 'Screenshot evidence cannot prove stable performance.' $claimId
        }
    }
    if ($claimId -eq 'audio_ok') {
        $hasAudioScope = @($observedScopes | Where-Object { $_ -eq 'audio' }).Count -gt 0
        if ($evidence.Count -gt 0 -and -not $hasAudioScope) {
            Add-Blocker 'claim_scope_not_observed' 'Screenshot evidence cannot prove audio.' $claimId
        }
    }
}

$build = Get-PropertyValue $manifest 'build' $null
$criticalWarnings = @(Get-PropertyValue $build 'critical_warnings' @())
foreach ($warning in $criticalWarnings) {
    $warningText = [string]$warning
    if ($warningText -match '(always false|always true|limited range|unreachable|comparison.*impossible)') {
        Add-Blocker 'critical_compiler_warning' 'A compiler warning indicates impossible or unreachable logic.' '' 'build'
        break
    }
}

$assets = @(Get-PropertyValue $manifest 'assets' @())
if (Test-ClaimRequested 'assets_premium') {
    foreach ($asset in $assets) {
        $channel = ([string](Get-PropertyValue $asset 'generation_channel' '')).ToLowerInvariant()
        $technicalScore = Get-PropertyValue $asset 'technical_score' $null
        $artApproval = Get-PropertyValue $asset 'artistic_approval' $null
        if ($channel -in @('procedural_renderer', 'local_author_pixel_rasterization', 'pil_imagedraw_generated', 'procedural_debug')) {
            Add-Blocker 'procedural_asset_quarantined' 'Procedural assets are technical placeholders, not premium delivery art.' 'assets_premium'
        }
        $humanApproval = $false
        if ($artApproval -and -not ($artApproval -is [string])) {
            $approvalStatus = [string](Get-PropertyValue $artApproval 'status' '')
            $reviewer = [string](Get-PropertyValue $artApproval 'reviewer' '')
            $humanApproval = ($approvalStatus -eq 'approved' -and -not [string]::IsNullOrWhiteSpace($reviewer))
        }
        if ($null -ne $technicalScore -and -not $humanApproval) {
            Add-Blocker 'technical_score_not_artistic_approval' 'Automatic technical score does not constitute artistic approval.' 'assets_premium'
        }
    }
}

$modules = @(Get-PropertyValue $manifest 'modules' @())
if ((Test-ClaimRequested 'first_playable') -or (Test-ClaimRequested 'gameplay_rom_aprovada') -or (Test-ClaimRequested 'ready_for_aaa')) {
    foreach ($module in $modules) {
        $moduleStatus = [string](Get-PropertyValue $module 'status' 'module_present')
        if ($moduleStatus -ne 'runtime_proven') {
            Add-Blocker 'runtime_feature_not_proven' 'A declared module is not runtime_proven; presence or integration is insufficient.' '' ([string](Get-PropertyValue $module 'id' 'unknown'))
        }
    }
}

if ([bool](Get-PropertyValue $manifest 'parallel_work' $false)) {
    $integrationOwner = [string](Get-PropertyValue $manifest 'integration_owner' '')
    if ([string]::IsNullOrWhiteSpace($integrationOwner)) {
        Add-Blocker 'integration_owner_missing' 'Parallel runtime/visual work requires one integration owner.'
    }
}

if (Test-ClaimRequested 'scene_closeout') {
    $executedCloseout = Join-Path $ProjectRoot 'out\logs\scene_closeout_gate_report.json'
    if (-not (Test-Path -LiteralPath $executedCloseout -PathType Leaf)) {
        Add-Blocker 'executed_closeout_gate_missing' 'Manual closeout report does not replace scene_closeout_gate_report.json.' 'scene_closeout'
    }
}

$metrics = Get-PropertyValue $manifest 'metrics' $null
if (Test-ClaimRequested 'performance_estavel') {
    $metricFormat = ([string](Get-PropertyValue $metrics 'format' '')).ToUpperInvariant()
    if ($metricFormat -ne 'MDRT') {
        Add-Blocker 'mdrt_performance_evidence_missing' 'MTR statistics are not canonical MDRT performance evidence.' 'performance_estavel'
    }
}

$runtime = Get-PropertyValue $manifest 'runtime' $null
$routeStatus = ([string](Get-PropertyValue $runtime 'route_status' '')).ToLowerInvariant()
$resultReached = [bool](Get-PropertyValue $runtime 'result_reached' $false)
if ($routeStatus -in @('crash', 'address_error', 'softlock')) {
    Add-Blocker 'runtime_route_crashed' 'The observed route crashed or softlocked before closeout.'
}
if ((Test-ClaimRequested 'first_playable') -and -not $resultReached -and $null -ne $runtime) {
    Add-Blocker 'route_result_not_proven' 'First playable requires a complete route through its result state.' 'first_playable'
}

$visual = Get-PropertyValue $manifest 'visual' $null
$visualCorruption = [bool](Get-PropertyValue $visual 'corruption' $false)
if ($visualCorruption) {
    Add-Blocker 'visual_corruption_observed' 'Visible corruption blocks runtime and delivery promotion.'
}

$review = Get-PropertyValue $manifest 'review' $null
$reviewDecision = ([string](Get-PropertyValue $review 'decision' '')).ToLowerInvariant()
if ($reviewDecision -in @('review_blocked', 'blocked', 'changes_required')) {
    Add-Blocker 'review_blocked' 'Formal review blocks promotion.'
}

if (Test-ClaimRequested 'validado_budget') {
    $budget = Get-PropertyValue $manifest 'budget' $null
    $budgetStatus = ([string](Get-PropertyValue $budget 'status' '')).ToLowerInvariant()
    if ($budgetStatus -notin @('passed', 'validado_budget')) {
        Add-Blocker 'budget_evidence_missing' 'validado_budget requires a passed hardware budget report.' 'validado_budget'
    }
}

$statusRank = @{
    'documentado' = 0
    'implemented' = 1
    'implementado' = 1
    'buildado' = 2
    'testado_em_emulador' = 3
    'validado_budget' = 4
    'first_playable' = 5
    'ready_for_aaa' = 6
}
$reconciliation = Get-PropertyValue $manifest 'reconciliation' $null
$statuses = @(Get-PropertyValue $reconciliation 'statuses' @())
if ($statuses.Count -gt 0) {
    $ranked = @()
    foreach ($entry in $statuses) {
        $statusName = ([string](Get-PropertyValue $entry 'status' '')).ToLowerInvariant()
        $rank = if ($statusRank.ContainsKey($statusName)) { [int]$statusRank[$statusName] } else { -1 }
        $ranked += [pscustomobject][ordered]@{ status = $statusName; rank = $rank }
    }
    $knownRanks = @($ranked | Where-Object { $_.rank -ge 0 })
    if (@($knownRanks | Select-Object -ExpandProperty rank -Unique).Count -gt 1) {
        Add-Blocker 'canonical_status_conflict' 'Canonical reports disagree; the least optimistic consistent status wins.'
    }
    if ($knownRanks.Count -gt 0) {
        $least = $knownRanks | Sort-Object rank | Select-Object -First 1
        $leastConsistentStatus = $least.status
        $highestRequestedRank = -1
        foreach ($claimId in $script:RequestedClaims) {
            if ($statusRank.ContainsKey($claimId)) {
                $claimRank = [int]$statusRank[$claimId]
                if ($claimRank -gt $highestRequestedRank) { $highestRequestedRank = $claimRank }
            }
        }
        if ($highestRequestedRank -gt [int]$least.rank) {
            Add-Blocker 'claim_exceeds_consistent_ceiling' 'Requested claim exceeds the least consistent canonical status.'
        }
    }
}

if (Test-ClaimRequested 'advance_next_phase') {
    if ($routeStatus -in @('crash', 'address_error', 'softlock') -or $visualCorruption -or $reviewDecision -in @('review_blocked', 'blocked', 'changes_required')) {
        Add-Blocker 'phase_advance_blocked' 'Cannot advance while the current phase has crash, visual corruption, or blocked review.' 'advance_next_phase'
    }
}

if (Test-ClaimRequested 'ready_for_aaa') {
    if ($routeStatus -in @('crash', 'address_error', 'softlock') -or $visualCorruption -or $reviewDecision -in @('review_blocked', 'blocked', 'changes_required')) {
        Add-Blocker 'ready_for_aaa_blocked_by_runtime_or_review' 'AAA promotion is blocked by current runtime, visual, or review state.' 'ready_for_aaa'
    }
}

$status = if ($script:BlockerCodes.Count -gt 0) { 'blocked' } else { 'passed' }
$claimCeiling = if ($script:BlockerCodes.Count -gt 0) {
    if ($leastConsistentStatus) { $leastConsistentStatus } else { 'buildado_or_lower_until_evidence_reconciled' }
} else {
    'requested_claims_supported'
}

$report = [ordered]@{
    schema_version = '1.0.0'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    tool_name = 'audit_promotion_claims'
    project_root = $ProjectRoot
    manifest_path = $ManifestPath
    status = $status
    rom_sha256 = $romHash
    requested_claims = @($script:RequestedClaims)
    blocker_codes = @($script:BlockerCodes)
    findings = @($script:Findings)
    claim_ceiling = $claimCeiling
    least_consistent_status = $leastConsistentStatus
}

[System.IO.Directory]::CreateDirectory((Split-Path -Parent $OutputPath)) | Out-Null
$report | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$report | ConvertTo-Json -Depth 20

if ($status -eq 'blocked' -and -not $WarnOnly) { exit 1 }
exit 0

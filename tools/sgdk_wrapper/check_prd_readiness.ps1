<#
.SYNOPSIS
    Checks project PRD/frontmatter readiness against the canonical PRD catalog.

.DESCRIPTION
    This is a lightweight autonomy gate. It does not judge the quality of a
    design decision; it verifies that the project has the decision authority
    artifacts required before an agent tries to produce AAA/stable/release work.
#>

param(
    [string]$ProjectRoot = ".",
    [string]$CatalogPath = "",
    [string]$OutPath = "",
    [ValidateSet("auto", "prototype", "AAA", "stable", "release", "delivery")]
    [string]$TargetProfile = "auto",
    [switch]$WarnOnly
)

$ErrorActionPreference = "Stop"

function Resolve-ExistingPath([string]$PathValue, [string]$Description) {
    $resolved = Resolve-Path -LiteralPath $PathValue -ErrorAction SilentlyContinue
    if (-not $resolved) {
        throw "$Description not found: $PathValue"
    }
    return $resolved.Path
}

function Get-PropertyValue($Object, [string]$Name, $Default = $null) {
    if ($null -eq $Object) { return $Default }
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $Default }
    return $prop.Value
}

function Read-JsonFile([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue)) { return $null }
    $raw = Get-Content -LiteralPath $PathValue -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return $raw | ConvertFrom-Json
}

function Read-FrontMatter([string]$PathValue) {
    $result = [ordered]@{
        present = $false
        values = @{}
    }
    if (-not (Test-Path -LiteralPath $PathValue)) { return $result }

    $content = Get-Content -LiteralPath $PathValue -Raw -Encoding UTF8
    if (-not $content.StartsWith("---")) { return $result }

    $match = [regex]::Match($content, "(?s)^---\s*\r?\n(.*?)\r?\n---")
    if (-not $match.Success) { return $result }

    $values = @{}
    foreach ($line in ($match.Groups[1].Value -split "\r?\n")) {
        if ($line -match "^\s*([A-Za-z0-9_\-]+)\s*:\s*(.*?)\s*$") {
            $key = $matches[1]
            $value = $matches[2].Trim()
            $values[$key] = $value
        }
    }

    $result.present = $true
    $result.values = $values
    return $result
}

function Test-StatusMeetsMinimum([string]$Status, [string]$Minimum) {
    $rank = @{
        "seed" = 1
        "filled" = 2
        "locked" = 3
    }
    if (-not $rank.ContainsKey($Status)) { return $false }
    if (-not $rank.ContainsKey($Minimum)) { return $false }
    return ([int]$rank[$Status] -ge [int]$rank[$Minimum])
}

function Get-BoolFlag($Index, [string]$FlagName) {
    $flags = Get-PropertyValue $Index "scope_flags" $null
    if ($null -eq $flags) { return $false }
    $prop = $flags.PSObject.Properties[$FlagName]
    if ($null -eq $prop) { return $false }
    return [bool]$prop.Value
}

$projectRootResolved = Resolve-ExistingPath $ProjectRoot "Project root"
$wrapperRoot = Split-Path -Parent $PSCommandPath
if ([string]::IsNullOrWhiteSpace($CatalogPath)) {
    $CatalogPath = Join-Path $wrapperRoot ".agent\references\project_prd_catalog.json"
}
$catalogResolved = Resolve-ExistingPath $CatalogPath "PRD catalog"

$catalog = Read-JsonFile $catalogResolved
if ($null -eq $catalog) {
    throw "Could not parse PRD catalog: $catalogResolved"
}

$docRoot = Join-Path $projectRootResolved "doc"
$indexPath = Join-Path $docRoot "prd_index.json"
$index = Read-JsonFile $indexPath
if ($null -eq $index) {
    $index = [pscustomobject]@{
        target_profile = "prototype"
        required_prds = @()
        scope_flags = [pscustomobject]@{}
    }
}

if ($TargetProfile -eq "auto") {
    $TargetProfile = [string](Get-PropertyValue $index "target_profile" "prototype")
    if ([string]::IsNullOrWhiteSpace($TargetProfile)) { $TargetProfile = "prototype" }
}

$aaaProfiles = @("AAA", "stable", "release", "delivery")
$isAaaClaim = $aaaProfiles -contains $TargetProfile
$requiredFromIndex = @{}
foreach ($id in @((Get-PropertyValue $index "required_prds" @()))) {
    if (-not [string]::IsNullOrWhiteSpace([string]$id)) {
        $requiredFromIndex[[string]$id] = $true
    }
}

$defaultMinimum = Get-PropertyValue $catalog "default_minimum_status" $null
$minimumStatus = "seed"
if ($null -ne $defaultMinimum) {
    $minProp = $defaultMinimum.PSObject.Properties[$TargetProfile]
    if ($null -ne $minProp) { $minimumStatus = [string]$minProp.Value }
}

$blockers = New-Object System.Collections.Generic.List[string]
$prdResults = New-Object System.Collections.Generic.List[object]
$summary = [ordered]@{
    required = 0
    missing = 0
    seed = 0
    filled = 0
    locked = 0
    not_applicable = 0
    blocked = 0
}

foreach ($prd in @($catalog.prds)) {
    $prdId = [string]$prd.id
    $path = [string]$prd.path
    $requiredWhen = @($prd.required_when)
    $required = $false

    if ($requiredWhen -contains "always") { $required = $true }
    if ($requiredFromIndex.ContainsKey($prdId)) { $required = $true }
    if (($requiredWhen -contains "aaa_claim") -and $isAaaClaim) { $required = $true }
    foreach ($token in $requiredWhen) {
        if ([string]$token -like "has_*" -and (Get-BoolFlag $index ([string]$token))) {
            $required = $true
        }
    }

    $absolutePath = Join-Path $projectRootResolved $path
    $exists = Test-Path -LiteralPath $absolutePath
    $frontmatter = Read-FrontMatter $absolutePath
    $frontmatterRequired = [bool](Get-PropertyValue $prd "frontmatter_required" $false)
    $notApplicableAllowed = [bool](Get-PropertyValue $prd "not_applicable_allowed" $false)

    $status = "missing"
    if ($exists) {
        if ($frontmatter.present) {
            $status = [string]($frontmatter.values["status"])
            if ([string]::IsNullOrWhiteSpace($status)) { $status = "status_missing" }
        } elseif ($frontmatterRequired) {
            $status = "frontmatter_missing"
        } else {
            $status = "filled"
        }
    }

    if ($summary.Contains($status)) {
        $summary[$status] = [int]$summary[$status] + 1
    }
    if ($required) {
        $summary.required = [int]$summary.required + 1
    }

    $decision = "not_required"
    $minimumForPrd = $minimumStatus
    if (-not $required) {
        $decision = "available_optional"
        if (-not $exists) { $decision = "not_required_missing" }
    } else {
        if ($status -eq "missing") {
            $decision = "blocked_missing"
            $blockers.Add("${prdId}_missing") | Out-Null
        } elseif ($status -eq "frontmatter_missing") {
            $decision = "blocked_frontmatter_missing"
            $blockers.Add("${prdId}_frontmatter_missing") | Out-Null
        } elseif ($status -eq "status_missing") {
            $decision = "blocked_status_missing"
            $blockers.Add("${prdId}_status_missing") | Out-Null
        } elseif ($status -eq "not_applicable") {
            if ($notApplicableAllowed) {
                $decision = "not_applicable"
            } else {
                $decision = "blocked_not_applicable_forbidden"
                $blockers.Add("${prdId}_not_applicable_forbidden") | Out-Null
            }
        } elseif (Test-StatusMeetsMinimum $status $minimumForPrd) {
            $decision = "ready"
        } else {
            $decision = "blocked_below_minimum_status"
            $blockers.Add("${prdId}_status_${status}_below_${minimumForPrd}") | Out-Null
        }
    }

    if ($decision -like "blocked*") {
        $summary.blocked = [int]$summary.blocked + 1
    }
    if ($status -eq "missing") {
        $summary.missing = [int]$summary.missing + 1
    }

    $prdResults.Add([pscustomobject]@{
        prd_id = $prdId
        title = [string]$prd.title
        tier = [int]$prd.tier
        path = $path
        required = [bool]$required
        status = $status
        minimum_status = $minimumForPrd
        decision = $decision
        frontmatter_present = [bool]$frontmatter.present
        unlocks = @($prd.unlocks)
    }) | Out-Null
}

$overallStatus = "ok"
if ($blockers.Count -gt 0) {
    $overallStatus = "blocked"
}

$report = [ordered]@{
    schema_version = "1.0.0"
    tool = "check_prd_readiness.ps1"
    status = $overallStatus
    target_profile = $TargetProfile
    project_root = $projectRootResolved
    catalog_path = $catalogResolved
    prd_index_path = $indexPath
    generated_at = (Get-Date).ToString("o")
    summary = [pscustomobject]$summary
    blockers = @($blockers.ToArray())
    prds = @($prdResults.ToArray())
}

if ([string]::IsNullOrWhiteSpace($OutPath)) {
    $OutPath = Join-Path $projectRootResolved "out\logs\prd_readiness_report.json"
}
$outDir = Split-Path -Parent $OutPath
if (-not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutPath -Encoding UTF8

Write-Host "[PRD] status=$overallStatus target=$TargetProfile blockers=$($blockers.Count) report=$OutPath"
if (($blockers.Count -gt 0) -and (-not $WarnOnly)) {
    exit 1
}
exit 0

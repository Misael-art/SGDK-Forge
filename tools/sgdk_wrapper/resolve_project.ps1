[CmdletBinding()]
param(
    [string]$EntryDir = ".",
    [ValidateSet("Batch", "Json")]
    [string]$OutputFormat = "Batch"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$ignoredChildNames = @(
    ".git", ".hg", ".svn", ".vscode", ".mddev", "doc", "docs", "out",
    "archives", "archive", "manual_review", "tmp", "temp", "dist", "build", "node_modules"
)

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Test-IsInsideWorkspace {
    param([Parameter(Mandatory = $true)][string]$Path)
    return $Path.StartsWith($workspaceRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

function Get-PathInfo {
    param([Parameter(Mandatory = $true)][string]$Path)

    $children = @(Get-ChildItem -LiteralPath $Path -Force -ErrorAction SilentlyContinue)
    $directories = @($children | Where-Object { $_.PSIsContainer })
    $files = @($children | Where-Object { -not $_.PSIsContainer })

    $hasSrc = [System.IO.Directory]::Exists([System.IO.Path]::Combine($Path, "src"))
    $hasRes = [System.IO.Directory]::Exists([System.IO.Path]::Combine($Path, "res"))
    $hasInc = [System.IO.Directory]::Exists([System.IO.Path]::Combine($Path, "inc"))
    $hasDoc = [System.IO.Directory]::Exists([System.IO.Path]::Combine($Path, "doc"))

    [PSCustomObject]@{
        Path    = $Path
        HasSrc  = $hasSrc
        HasRes  = $hasRes
        HasInc  = $hasInc
        HasDoc  = $hasDoc
        BatCount = @(Get-ChildItem -LiteralPath $Path -File -Filter "*.bat" -ErrorAction SilentlyContinue).Count
        ShCount  = @(Get-ChildItem -LiteralPath $Path -File -Filter "*.sh" -ErrorAction SilentlyContinue).Count
        Directories = @($directories | ForEach-Object { $_.Name })
        Files       = @($files | ForEach-Object { $_.Name })
    }
}

function Get-ChildProjectCandidates {
    param([Parameter(Mandatory = $true)][string]$Path)
    $directories = @(Get-ChildItem -LiteralPath $Path -Directory -Force -ErrorAction SilentlyContinue)
    foreach ($directory in $directories) {
        if ($ignoredChildNames -contains $directory.Name.ToLowerInvariant()) { continue }
        $info = Get-PathInfo -Path $directory.FullName
        $score = 0
        if ($info.HasSrc) { $score += 5 }
        if ($info.HasRes) { $score += 3 }
        if ($info.HasInc) { $score += 1 }
        if ($info.BatCount -gt 0) { $score += 1 }
        if ($info.ShCount -gt 0) { $score += 1 }
        if ($info.HasDoc) { $score += 1 }
        if ($score -ge 5) {
            [PSCustomObject]@{
                Path  = $directory.FullName
                Name  = $directory.Name
                Score = $score
                Info  = $info
            }
        }
    }
}

function Get-ManifestFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    $current = $Path
    while ($true) {
        if (-not (Test-IsInsideWorkspace -Path $current)) { return $null }
        $manifestPath = [System.IO.Path]::Combine($current, ".mddev", "project.json")
        if ([System.IO.File]::Exists($manifestPath)) { return $manifestPath }
        if ($current -eq $workspaceRoot) { return $null }
        $parent = [System.IO.Path]::GetDirectoryName($current)
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) { return $null }
        $current = $parent
    }
}

function Get-ManifestStringField {
    param($Manifest, [string[]]$Names, [string]$Default = "")
    foreach ($name in $Names) {
        $property = $Manifest.PSObject.Properties[$name]
        if ($null -eq $property) { continue }
        $value = [string]$property.Value
        if (-not [string]::IsNullOrWhiteSpace($value)) { return $value }
    }
    return $Default
}

function Resolve-ManifestContext {
    param([Parameter(Mandatory = $true)][string]$ManifestPath)
    $manifestRoot = [System.IO.Path]::GetDirectoryName([System.IO.Path]::GetDirectoryName($ManifestPath))
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $projectRootRel = Get-ManifestStringField -Manifest $manifest -Names @("project_root", "projectRoot") -Default "."
    $sgdkRootRel = Get-ManifestStringField -Manifest $manifest -Names @("sgdk_root", "sgdkRoot") -Default "."
    $projectRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($manifestRoot, $projectRootRel))
    $sgdkRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($manifestRoot, $sgdkRootRel))

    if (-not [System.IO.Directory]::Exists($projectRoot)) { throw "Manifesto invalido: project_root nao encontrado em '$projectRoot'." }
    if (-not [System.IO.Directory]::Exists($sgdkRoot)) { throw "Manifesto invalido: sgdk_root nao encontrado em '$sgdkRoot'." }

    $displayName = Get-ManifestStringField -Manifest $manifest -Names @("display_name") -Default ""
    if ([string]::IsNullOrWhiteSpace($displayName)) { $displayName = [System.IO.Path]::GetFileName($manifestRoot) }
    
    [PSCustomObject]@{
        EntryDir         = $manifestRoot
        ProjectRoot      = $projectRoot
        SgdkRoot         = $sgdkRoot
        Layout           = Get-ManifestStringField -Manifest $manifest -Names @("layout") -Default "manifest"
        ManifestPath     = $ManifestPath
        DisplayName      = $displayName
        Kind             = Get-ManifestStringField -Manifest $manifest -Names @("kind") -Default ""
        Category         = Get-ManifestStringField -Manifest $manifest -Names @("category") -Default ""
        BuildPolicy      = Get-ManifestStringField -Manifest $manifest -Names @("build_policy") -Default "enabled"
        Notes            = Get-ManifestStringField -Manifest $manifest -Names @("notes") -Default ""
        ResolutionReason = "manifest"
    }
}

function Resolve-HeuristicContext {
    param([Parameter(Mandatory = $true)][string]$Path)
    $entryInfo = Get-PathInfo -Path $Path
    $childCandidates = @(Get-ChildProjectCandidates -Path $Path)
    $completeChildren = @($childCandidates | Where-Object { $_.Info.HasSrc -and $_.Info.HasRes })

    if ($entryInfo.HasSrc -and $entryInfo.HasRes) {
        if ($completeChildren.Count -eq 1 -and $entryInfo.HasInc -eq $false) {
            return [PSCustomObject]@{ EntryDir=$Path; ProjectRoot=$Path; SgdkRoot=$completeChildren[0].Path; Layout="nested"; ManifestPath=""; DisplayName=[System.IO.Path]::GetFileName($Path); Kind=""; Category=""; BuildPolicy="enabled"; Notes=""; ResolutionReason="nested-complete-child" }
        }
        return [PSCustomObject]@{ EntryDir=$Path; ProjectRoot=$Path; SgdkRoot=$Path; Layout="flat"; ManifestPath=""; DisplayName=[System.IO.Path]::GetFileName($Path); Kind=""; Category=""; BuildPolicy="enabled"; Notes=""; ResolutionReason="direct-complete" }
    }
    
    if ($childCandidates.Count -eq 1) {
        return [PSCustomObject]@{ EntryDir=$Path; ProjectRoot=$Path; SgdkRoot=$childCandidates[0].Path; Layout="nested"; ManifestPath=""; DisplayName=[System.IO.Path]::GetFileName($Path); Kind=""; Category=""; BuildPolicy="enabled"; Notes=""; ResolutionReason="single-child-candidate" }
    }

    if ($childCandidates.Count -gt 1) {
        $sorted = @($childCandidates | Sort-Object Score -Descending)
        if ($sorted.Count -ge 2 -and $sorted[0].Score -gt $sorted[1].Score) {
            return [PSCustomObject]@{ EntryDir=$Path; ProjectRoot=$Path; SgdkRoot=$sorted[0].Path; Layout="nested"; ManifestPath=""; DisplayName=[System.IO.Path]::GetFileName($Path); Kind=""; Category=""; BuildPolicy="enabled"; Notes=""; ResolutionReason="highest-score-child" }
        }
    }
    throw ("Nao foi possivel localizar o SGDK root a partir de '{0}'." -f $Path)
}

function Convert-ToBatchLine {
    param([string]$Name, [string]$Value)
    $safe = $Value.Replace('"', '""')
    return ('set "{0}={1}"' -f $Name, $safe)
}

try {
    $entryPath = Resolve-FullPath -Path $EntryDir
    $manifestPath = Get-ManifestFile -Path $entryPath
    if ($manifestPath) { $context = Resolve-ManifestContext -ManifestPath $manifestPath } 
    else { $context = Resolve-HeuristicContext -Path $entryPath }

    $srcCheckPath = [System.IO.Path]::Combine($context.SgdkRoot, "src")
    if ($context.BuildPolicy -ne "disabled" -and -not [System.IO.Directory]::Exists($srcCheckPath)) {
        throw ("SGDK root resolvido sem pasta src: '{0}'." -f $context.SgdkRoot)
    }

    if ($OutputFormat -eq "Json") { $context | ConvertTo-Json -Depth 4; exit 0 }

    $pairs = [ordered]@{
        "SGDK_ENTRY_DIR" = $context.EntryDir; "SGDK_PROJECT_ROOT" = $context.ProjectRoot; "SGDK_WORK_DIR" = $context.SgdkRoot; "SGDK_LAYOUT" = $context.Layout; "SGDK_MANIFEST_PATH" = $context.ManifestPath; "SGDK_DISPLAY_NAME" = $context.DisplayName; "SGDK_KIND" = $context.Kind; "SGDK_CATEGORY" = $context.Category; "SGDK_BUILD_POLICY" = $context.BuildPolicy; "SGDK_NOTES" = $context.Notes; "SGDK_RESOLUTION_REASON" = $context.ResolutionReason
    }
    foreach ($pair in $pairs.GetEnumerator()) { Convert-ToBatchLine -Name $pair.Key -Value ([string]$pair.Value) }
}
catch { Write-Error $_; exit 1 }

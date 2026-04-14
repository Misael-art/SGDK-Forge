[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectRoot = ".",
    [Parameter(Mandatory = $false)]
    [string]$Task = "wrapper_snapshot",
    [Parameter(Mandatory = $false)]
    [string[]]$Skills = @(),
    [Parameter(Mandatory = $false)]
    [string]$Notes = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Get-ProjectRelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $rootFull = (Resolve-FullPath $Root).TrimEnd('\')
    $pathFull = Resolve-FullPath $Path
    if ($pathFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $pathFull.Substring($rootFull.Length).TrimStart('\').Replace('\', '/')
    }
    return $pathFull.Replace('\', '/')
}

function Get-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Write-JsonUtf8 {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $Object | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-FileIdentity {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $item = Get-Item -LiteralPath $Path
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash($stream)
            $hash = ([System.BitConverter]::ToString($hashBytes).Replace("-", "")).ToLowerInvariant()
        } finally {
            $sha256.Dispose()
        }
    } finally {
        $stream.Dispose()
    }

    return [pscustomobject]@{
        path = $item.FullName
        size_bytes = [int64]$item.Length
        last_write_utc = $item.LastWriteTimeUtc.ToString("o")
        sha256 = $hash
    }
}

function Get-PngSummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 29) {
        return $null
    }

    if ($bytes[0] -ne 0x89 -or $bytes[1] -ne 0x50) {
        return $null
    }

    $width = [int]$bytes[16] * 16777216 + [int]$bytes[17] * 65536 + [int]$bytes[18] * 256 + [int]$bytes[19]
    $height = [int]$bytes[20] * 16777216 + [int]$bytes[21] * 65536 + [int]$bytes[22] * 256 + [int]$bytes[23]
    $bitDepth = [int]$bytes[24]
    $colorType = [int]$bytes[25]

    $paletteEntries = 0
    $offset = 8
    while ($offset -lt ($bytes.Length - 12)) {
        $chunkLength = [int]$bytes[$offset] * 16777216 + [int]$bytes[$offset + 1] * 65536 + [int]$bytes[$offset + 2] * 256 + [int]$bytes[$offset + 3]
        $chunkType = [System.Text.Encoding]::ASCII.GetString($bytes, $offset + 4, 4)
        if ($chunkType -eq "PLTE") {
            $paletteEntries = [int]($chunkLength / 3)
            break
        }
        if ($chunkType -eq "IDAT") {
            break
        }
        $offset += 12 + $chunkLength
    }

    return [ordered]@{
        width = $width
        height = $height
        bit_depth = $bitDepth
        color_type = $colorType
        indexed = ($colorType -eq 3)
        palette_entries = $paletteEntries
    }
}

function Normalize-AssetId {
    param([Parameter(Mandatory = $true)][string]$Value)

    $normalized = $Value.ToLowerInvariant() -replace '[^a-z0-9_-]', '_'
    $normalized = $normalized.Trim('_')
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return "asset"
    }
    return $normalized
}

function Get-NextVersionLabel {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Prefix
    )

    $max = 0
    if (Test-Path -LiteralPath $Root -PathType Container) {
        foreach ($dir in Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue) {
            if ($dir.Name -match "^$Prefix(\d{3})$") {
                $value = [int]$matches[1]
                if ($value -gt $max) {
                    $max = $value
                }
            }
        }
    }
    return ("{0}{1:D3}" -f $Prefix, ($max + 1))
}

function Get-LatestVersionMetadata {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Prefix,
        [Parameter(Mandatory = $true)][string]$MetaName
    )

    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return $null
    }

    $candidates = @()
    foreach ($dir in Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue) {
        if ($dir.Name -match "^$Prefix(\d{3})$") {
            $metaPath = Join-Path $dir.FullName $MetaName
            $meta = Get-JsonOrNull $metaPath
            if ($meta) {
                $candidates += [pscustomobject]@{
                    version = $dir.Name
                    ordinal = [int]$matches[1]
                    dir = $dir.FullName
                    meta_path = $metaPath
                    meta = $meta
                }
            }
        }
    }

    if (-not $candidates) {
        return $null
    }

    return $candidates | Sort-Object ordinal -Descending | Select-Object -First 1
}

function Get-BuildTileCountMap {
    param([Parameter(Mandatory = $true)][string]$BuildLogPath)

    $map = @{}
    if (-not (Test-Path -LiteralPath $BuildLogPath -PathType Leaf)) {
        return $map
    }

    foreach ($line in Get-Content -LiteralPath $BuildLogPath) {
        if ($line -match "^'([^']+)_tileset_data' packed .* origin size = (\d+)") {
            $resourceName = $matches[1]
            $tiles = [int]([int64]$matches[2] / 32)
            if (-not $map.ContainsKey($resourceName)) {
                $map[$resourceName] = $tiles
            }
        }
    }

    return $map
}

function Get-ResourceEntries {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    $entries = @()
    $seen = @{}
    $resRoot = Join-Path $ProjectRoot "res"
    if (-not (Test-Path -LiteralPath $resRoot -PathType Container)) {
        return $entries
    }

    $resFiles = Get-ChildItem -LiteralPath $resRoot -Recurse -Filter "*.res" -File -ErrorAction SilentlyContinue
    foreach ($resFile in $resFiles) {
        $baseDir = Split-Path $resFile.FullName
        foreach ($line in Get-Content -LiteralPath $resFile.FullName) {
            if ($line -match '^\s*(IMAGE|SPRITE|MAP|TILESET|PALETTE|BIN|OBJECT)\s+([A-Za-z0-9_]+)\s+"([^"]+)"') {
                $kind = $matches[1]
                $name = $matches[2]
                $relativeSource = $matches[3]
                $absoluteSource = Join-Path $baseDir $relativeSource
                if (-not (Test-Path -LiteralPath $absoluteSource -PathType Leaf)) {
                    continue
                }

                $key = "{0}|{1}" -f $name, $absoluteSource.ToLowerInvariant()
                if ($seen.ContainsKey($key)) {
                    continue
                }
                $seen[$key] = $true

                $entries += [pscustomobject]@{
                    resource_name = $name
                    resource_kind = $kind
                    source_relative_path = Get-ProjectRelativePath -Root $ProjectRoot -Path $absoluteSource
                    source_absolute_path = (Resolve-FullPath $absoluteSource)
                    asset_id = Normalize-AssetId $name
                }
            }
        }
    }

    return $entries
}

function Get-GitCommitOrNull {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    try {
        $output = & git -C $ProjectRoot rev-parse HEAD 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($output)) {
            return ($output | Select-Object -First 1).Trim()
        }
    } catch {
    }
    return $null
}

function Update-MemoryBankGeneratedSection {
    param(
        [Parameter(Mandatory = $true)][string]$MemoryBankPath,
        [Parameter(Mandatory = $true)][string]$GeneratedMarkdown
    )

    $startMarker = "<!-- SGDK GENERATED STATUS START -->"
    $endMarker = "<!-- SGDK GENERATED STATUS END -->"
    $block = @(
        $startMarker
        $GeneratedMarkdown.TrimEnd()
        $endMarker
        ""
    ) -join "`r`n"

    if (-not (Test-Path -LiteralPath $MemoryBankPath -PathType Leaf)) {
        Set-Content -LiteralPath $MemoryBankPath -Value ($block + "`r`n") -Encoding UTF8
        return
    }

    $content = Get-Content -LiteralPath $MemoryBankPath -Raw
    $startIndex = $content.IndexOf($startMarker, [System.StringComparison]::Ordinal)
    $endIndex = $content.LastIndexOf($endMarker, [System.StringComparison]::Ordinal)
    if ($startIndex -ge 0 -and $endIndex -ge $startIndex) {
        $afterIndex = $endIndex + $endMarker.Length
        while ($afterIndex -lt $content.Length -and ($content[$afterIndex] -eq "`r" -or $content[$afterIndex] -eq "`n")) {
            $afterIndex++
        }
        $suffix = $content.Substring($afterIndex)
        $updated = $block + $suffix
        Set-Content -LiteralPath $MemoryBankPath -Value $updated -Encoding UTF8
        return
    }

    $updatedContent = $block + $content
    Set-Content -LiteralPath $MemoryBankPath -Value $updatedContent -Encoding UTF8
}

$resolvedProjectRoot = Resolve-FullPath $ProjectRoot
Set-Location -LiteralPath $resolvedProjectRoot

$changelogRoot = Join-Path $resolvedProjectRoot "doc\changelog"
$assetsRoot = Join-Path $changelogRoot "assets"
$romsRoot = Join-Path $changelogRoot "roms"
$changelogPath = Join-Path $changelogRoot "changelog.md"
$memoryBankPath = Join-Path $resolvedProjectRoot "doc\10-memory-bank.md"
$validationReportPath = Join-Path $resolvedProjectRoot "out\logs\validation_report.json"
$emulatorSessionPath = Join-Path $resolvedProjectRoot "out\logs\emulator_session.json"
$buildLogPath = Join-Path $resolvedProjectRoot "out\logs\build_output.log"
$romPath = Join-Path $resolvedProjectRoot "out\rom.bin"

Ensure-Directory $changelogRoot
Ensure-Directory $assetsRoot
Ensure-Directory $romsRoot
Ensure-Directory (Split-Path $memoryBankPath)

$validationReport = Get-JsonOrNull $validationReportPath
$emulatorSession = Get-JsonOrNull $emulatorSessionPath
$validationBlockingStatuses = @()
if ($validationReport -and ($validationReport.PSObject.Properties.Name -contains "blocking_statuses")) {
    $validationBlockingStatuses = @($validationReport.blocking_statuses | Where-Object { $null -ne $_ -and -not [string]::IsNullOrWhiteSpace([string]$_) })
}
$buildTileCountMap = Get-BuildTileCountMap $buildLogPath
$resourceEntries = Get-ResourceEntries $resolvedProjectRoot
$gitCommit = Get-GitCommitOrNull $resolvedProjectRoot
$timestamp = (Get-Date).ToString("o")

$currentAssetVersions = @()
$newAssetVersions = @()

foreach ($entry in $resourceEntries) {
    $assetRoot = Join-Path $assetsRoot $entry.asset_id
    Ensure-Directory $assetRoot

    $sourceIdentity = Get-FileIdentity $entry.source_absolute_path
    if (-not $sourceIdentity) {
        continue
    }

    $latest = Get-LatestVersionMetadata -Root $assetRoot -Prefix "v" -MetaName "meta.json"
    $versionLabel = $null
    $metaPath = $null

    if ($latest -and $latest.meta.source_sha256 -eq $sourceIdentity.sha256) {
        $versionLabel = $latest.version
        $metaPath = $latest.meta_path
    } else {
        $versionLabel = Get-NextVersionLabel -Root $assetRoot -Prefix "v"
        $versionDir = Join-Path $assetRoot $versionLabel
        Ensure-Directory $versionDir

        $targetAssetPath = Join-Path $versionDir ([System.IO.Path]::GetFileName($entry.source_absolute_path))
        Copy-Item -LiteralPath $entry.source_absolute_path -Destination $targetAssetPath -Force

        $metaPath = Join-Path $versionDir "meta.json"
        $paletteSummary = $null
        if ([System.IO.Path]::GetExtension($entry.source_absolute_path).ToLowerInvariant() -eq ".png") {
            $paletteSummary = Get-PngSummary $entry.source_absolute_path
        }

        $metaObject = [ordered]@{
            asset_id = $entry.asset_id
            version = $versionLabel
            resource_name = $entry.resource_name
            resource_kind = $entry.resource_kind
            source_path = $entry.source_relative_path
            source_sha256 = $sourceIdentity.sha256
            derived_from = @($entry.source_relative_path)
            palette_summary = $paletteSummary
            tile_count_when_known = if ($buildTileCountMap.ContainsKey($entry.resource_name)) { $buildTileCountMap[$entry.resource_name] } else { $null }
            notes = "Snapshot canonico criado por update_project_changelog.ps1"
            created_at = $timestamp
        }
        Write-JsonUtf8 -Object $metaObject -Path $metaPath

        $newAssetVersions += [pscustomobject]@{
            asset_id = $entry.asset_id
            version = $versionLabel
            source_path = $entry.source_relative_path
        }
    }

    $currentAssetVersions += [pscustomobject]@{
        asset_id = $entry.asset_id
        version = $versionLabel
        source_path = $entry.source_relative_path
        source_sha256 = $sourceIdentity.sha256
        resource_name = $entry.resource_name
        resource_kind = $entry.resource_kind
        meta_path = $metaPath
    }
}

$romIdentity = Get-FileIdentity $romPath
$latestBuild = Get-LatestVersionMetadata -Root $romsRoot -Prefix "build_v" -MetaName "build_meta.json"
$buildVersion = $null
$buildMetaPath = $null
$createdRomSnapshot = $false

if ($romIdentity) {
    if ($latestBuild -and $latestBuild.meta.rom_sha256 -eq $romIdentity.sha256) {
        $buildVersion = $latestBuild.version
        $buildMetaPath = $latestBuild.meta_path
    } else {
        $buildVersion = Get-NextVersionLabel -Root $romsRoot -Prefix "build_v"
        $buildDir = Join-Path $romsRoot $buildVersion
        Ensure-Directory $buildDir
        Copy-Item -LiteralPath $romPath -Destination (Join-Path $buildDir "rom.bin") -Force
        $buildMetaPath = Join-Path $buildDir "build_meta.json"
        $createdRomSnapshot = $true
    }

    $validationSummary = $null
    if ($validationReport) {
        $validationSummary = [ordered]@{
            errors = $validationReport.summary.errors
            warnings = $validationReport.summary.warnings
            blocking_statuses = @($validationBlockingStatuses)
        }
    }

    $buildMeta = [ordered]@{
        build_version = $buildVersion
        rom_sha256 = $romIdentity.sha256
        size_bytes = $romIdentity.size_bytes
        timestamp = $timestamp
        source_commit_when_available = $gitCommit
        validation_summary = $validationSummary
        emulator_evidence_status = if ($validationReport) { $validationReport.evidence.emulator_evidence_reason } elseif ($emulatorSession) { $emulatorSession.launch_status } else { "nao_avaliado" }
        linked_asset_versions = @($currentAssetVersions | ForEach-Object {
            [ordered]@{
                asset_id = $_.asset_id
                version = $_.version
                source_path = $_.source_path
            }
        })
        notes = if ($Notes) { $Notes } else { "Snapshot canonico criado por update_project_changelog.ps1" }
    }
    Write-JsonUtf8 -Object $buildMeta -Path $buildMetaPath
}

if (-not (Test-Path -LiteralPath $changelogPath -PathType Leaf)) {
    @(
        "# Changelog Canonico"
        ""
        "Este arquivo registra snapshots reais de assets e ROMs do projeto."
        ""
        '- assets vivem em `doc/changelog/assets/`'
        '- ROMs vivem em `doc/changelog/roms/`'
        "- novas versoes so nascem quando o hash muda"
        ""
    ) | Set-Content -LiteralPath $changelogPath -Encoding UTF8
}

$shouldAppendEntry = $createdRomSnapshot -or ($newAssetVersions.Count -gt 0)
if ($shouldAppendEntry) {
    $entryLines = @()
    $entryLines += "## $timestamp - $Task"
    $entryLines += ""
    $entryLines += "- Task: $Task"
    if ($Skills.Count -gt 0) {
        $entryLines += "- Skills: $($Skills -join ', ')"
    }
    if ($newAssetVersions.Count -gt 0) {
        $entryLines += "- Asset snapshots:"
        foreach ($assetVersion in $newAssetVersions) {
            $entryLines += "  - $($assetVersion.asset_id) -> $($assetVersion.version) ($($assetVersion.source_path))"
        }
    } else {
        $entryLines += "- Asset snapshots: nenhum hash novo"
    }
    if ($romIdentity) {
        $entryLines += "- ROM: $buildVersion (sha256 $($romIdentity.sha256), $($romIdentity.size_bytes) bytes)"
    } else {
        $entryLines += "- ROM: nenhuma ROM presente"
    }
    if ($validationReport) {
        $entryLines += "- Validation: errors=$($validationReport.summary.errors), warnings=$($validationReport.summary.warnings)"
        if ($validationBlockingStatuses.Count -gt 0) {
            $entryLines += "- Blockers: $($validationBlockingStatuses -join ', ')"
        }
        $entryLines += "- Emulator evidence: $($validationReport.evidence.emulator_evidence_reason)"
    }
    if ($Notes) {
        $entryLines += "- Notes: $Notes"
    }
    $entryLines += ""
    Add-Content -LiteralPath $changelogPath -Value ($entryLines -join "`r`n") -Encoding UTF8
}

$latestValidationErrors = if ($validationReport) { [int]$validationReport.summary.errors } else { 0 }
$latestValidationWarnings = if ($validationReport) { [int]$validationReport.summary.warnings } else { 0 }
$latestBlockers = @($validationBlockingStatuses)
$latestEvidenceReason = if ($validationReport) { [string]$validationReport.evidence.emulator_evidence_reason } elseif ($emulatorSession) { [string]$emulatorSession.launch_status } else { "nao_avaliado" }
$latestBuildLabel = if ([string]::IsNullOrWhiteSpace($buildVersion)) { "nenhum" } else { $buildVersion }

$generatedStatus = @(
    "## 0. Estado Derivado dos Artefatos",
    "",
    '- Fonte: `doc/changelog` + `validation_report.json`',
    ('- Ultima sincronizacao: `{0}`' -f $timestamp),
    '- Changelog canonico: `doc/changelog/changelog.md`',
    "- Assets versionados rastreados: $($currentAssetVersions.Count)",
    "- Ultimo build versionado: $latestBuildLabel"
)

if ($romIdentity) {
    $generatedStatus += ('- ROM vigente: `{0}` (`{1}` bytes)' -f $romIdentity.sha256, $romIdentity.size_bytes)
} else {
    $generatedStatus += "- ROM vigente: nenhuma ROM encontrada"
}

$generatedStatus += "- Validation summary: errors=$latestValidationErrors warnings=$latestValidationWarnings"
$generatedStatus += "- Blockers vigentes: $($(if ($latestBlockers.Count -gt 0) { $latestBlockers -join ', ' } else { 'nenhum' }))"
$generatedStatus += "- Evidencia de emulador: $latestEvidenceReason"

Update-MemoryBankGeneratedSection -MemoryBankPath $memoryBankPath -GeneratedMarkdown ($generatedStatus -join "`r`n")

$result = [ordered]@{
    project_root = $resolvedProjectRoot
    changelog_path = $changelogPath
    memory_bank_path = $memoryBankPath
    asset_versions_created = @($newAssetVersions)
    current_asset_versions = @($currentAssetVersions | ForEach-Object {
        [ordered]@{
            asset_id = $_.asset_id
            version = $_.version
            source_path = $_.source_path
        }
    })
    rom_snapshot_created = $createdRomSnapshot
    build_version = $buildVersion
    rom_sha256 = if ($romIdentity) { $romIdentity.sha256 } else { $null }
}

$result | ConvertTo-Json -Depth 8

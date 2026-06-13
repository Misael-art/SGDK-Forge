<#
.SYNOPSIS
    Audits the resource graph declared in .res files for an SGDK project.
.DESCRIPTION
    Uses the shared res_graph.psm1 parser to produce a canonical graph of
    all declared resources, their existence, classification, and issues.
    Outputs res_graph_report.json and res_graph_summary.md.
.NOTES
    Observational tool - does not block builds. Enriches the pipeline surface.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string[]]$ResPath = @(),

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
Import-Module (Join-Path $LibDir 'res_graph.psm1') -Force

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$LogDir = Join-Path $ProjectRoot 'out\logs'
$ReportPath = Join-Path $LogDir 'res_graph_report.json'
$SummaryPath = Join-Path $LogDir 'res_graph_summary.md'

# ---------------------------------------------------------------------------
# Artifact envelope
# ---------------------------------------------------------------------------
$artifact = New-SgdkArtifactEnvelope `
    -ToolName 'res_graph_audit' `
    -ToolVersion '0.2.0' `
    -ProjectRoot $ProjectRoot

function Get-JsonPropertyValue {
    param(
        [Parameter(Mandatory = $false)]$Object,
        [Parameter(Mandatory)][string]$Name
    )

    if ($null -eq $Object) { return $null }
    if ($Object -is [System.Collections.IDictionary]) {
        if ($Object.Contains($Name)) { return $Object[$Name] }
        return $null
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -ne $property) { return $property.Value }
    return $null
}

# ---------------------------------------------------------------------------
# Discover and parse .res files
# ---------------------------------------------------------------------------
$resFiles = @(Get-SgdkResFiles -ProjectRoot $ProjectRoot -ResPath $ResPath)
$codeLoadedTiles = Get-SgdkCodeLoadedTileFootprint -ProjectRoot $ProjectRoot

if ($resFiles.Count -eq 0) {
    $issues = @()
    if ($codeLoadedTiles.status -eq 'code_loaded_tiles_unmeasured') {
        $issues += [ordered]@{
            res_file  = ''
            res_line  = 0
            severity  = 'warn'
            code      = 'RG_CODETILE001'
            message   = 'Runtime loads/draws tiles from C code but no .res graph exists; VDP budget is estimated, not validated.'
            resource  = 'code_loaded_tiles'
        }
        Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Runtime code-loaded tiles detected without .res graph' -Warn
    }
    $artifact['res_files'] = @()
    $artifact['declarations'] = @()
    $artifact['issues'] = @($issues)
    $artifact['summary'] = [ordered]@{
        res_files_count      = 0
        declarations_total   = 0
        declarations_ok      = 0
        declarations_missing = 0
        declarations_unparsed = 0
        audio_count          = 0
        image_count          = 0
        map_count            = 0
        binary_count         = 0
        unknown_count        = 0
        total_source_bytes   = 0
        issues_count         = $issues.Count
        vram_residency_status = if ($codeLoadedTiles.status -eq 'code_loaded_tiles_unmeasured') { 'code_loaded_tiles_unmeasured' } else { 'not_measured' }
        sprite_reserve_tiles = 0
        vram_overlap_count   = 0
        code_loaded_tiles_count = [int]$codeLoadedTiles.estimated_tiles
        code_loaded_tiles_status = $codeLoadedTiles.status
    }
    $artifact['vram'] = [ordered]@{
        status = if ($codeLoadedTiles.status -eq 'code_loaded_tiles_unmeasured') { 'code_loaded_tiles_unmeasured' } else { 'not_measured' }
        method = if ($codeLoadedTiles.status -eq 'code_loaded_tiles_unmeasured') { 'no_res_files_plus_static_code_scan' } else { 'no_res_files' }
        measurement_level = if ($codeLoadedTiles.status -eq 'code_loaded_tiles_unmeasured') { 'estimated' } else { 'not_measured' }
        tile_ranges = @()
        sprite_reserve_tiles = 0
        overlaps = @()
        code_loaded_tiles = $codeLoadedTiles
    }

    Write-SgdkJsonArtifact -Data $artifact -Path $ReportPath | Out-Null
    Write-Host '[INFO] No .res files found. Empty report written.'
    exit 0
}

$declarations = @(Get-SgdkResDeclarations -ResFiles $resFiles -ProjectRoot $ProjectRoot)

# ---------------------------------------------------------------------------
# Build issue list
# ---------------------------------------------------------------------------
$issues = [System.Collections.ArrayList]::new()

foreach ($decl in $declarations) {
    if ($decl.parser_status -eq 'source_missing' -and $decl.resource_kind -ne 'UNPARSED') {
        [void]$issues.Add([ordered]@{
            res_file  = $decl.res_file
            res_line  = $decl.res_line
            severity  = 'error'
            code      = 'RG001'
            message   = "Source file not found: $($decl.declared_path)"
            resource  = $decl.resource_name
        })
    }

    if ($decl.parser_status -eq 'unknown_kind') {
        [void]$issues.Add([ordered]@{
            res_file  = $decl.res_file
            res_line  = $decl.res_line
            severity  = 'warn'
            code      = 'RG002'
            message   = "Unknown resource kind: $($decl.resource_kind)"
            resource  = $decl.resource_name
        })
    }

    if ($decl.parser_status -eq 'unparsed') {
        [void]$issues.Add([ordered]@{
            res_file  = $decl.res_file
            res_line  = $decl.res_line
            severity  = 'info'
            code      = 'RG003'
            message   = "Unparsed line: $($decl.raw_line)"
            resource  = $null
        })
    }
}

# Check for duplicate resource names
$nameGroups = @($declarations | Where-Object { $_.resource_name } | Group-Object resource_name | Where-Object { $_.Count -gt 1 })
foreach ($group in $nameGroups) {
    foreach ($member in $group.Group) {
        [void]$issues.Add([ordered]@{
            res_file  = $member.res_file
            res_line  = $member.res_line
            severity  = 'warn'
            code      = 'RG004'
            message   = "Duplicate resource name '$($member.resource_name)' (appears $($group.Count) times)"
            resource  = $member.resource_name
        })
    }
}

# ---------------------------------------------------------------------------
# Compute summary
# ---------------------------------------------------------------------------
$okDecls = @($declarations | Where-Object { $_.parser_status -eq 'ok' })
$missingDecls = @($declarations | Where-Object { $_.parser_status -eq 'source_missing' })
$unparsedDecls = @($declarations | Where-Object { $_.parser_status -eq 'unparsed' })
$audioDecls = @($declarations | Where-Object { $_.classification -eq 'audio' })
$imageDecls = @($declarations | Where-Object { $_.classification -eq 'image' })
$mapDecls = @($declarations | Where-Object { $_.classification -eq 'map' })
$binaryDecls = @($declarations | Where-Object { $_.classification -eq 'binary' })
$unknownDecls = @($declarations | Where-Object { $_.classification -eq 'unknown' -and $_.parser_status -ne 'unparsed' })

$totalSourceBytes = 0
foreach ($d in $declarations) {
    if ($d.source_size_bytes) { $totalSourceBytes += $d.source_size_bytes }
}

$summary = [ordered]@{
    res_files_count       = $resFiles.Count
    declarations_total    = $declarations.Count
    declarations_ok       = $okDecls.Count
    declarations_missing  = $missingDecls.Count
    declarations_unparsed = $unparsedDecls.Count
    audio_count           = $audioDecls.Count
    image_count           = $imageDecls.Count
    map_count             = $mapDecls.Count
    binary_count          = $binaryDecls.Count
    unknown_count         = $unknownDecls.Count
    total_source_bytes    = $totalSourceBytes
    issues_count          = $issues.Count
}

# ---------------------------------------------------------------------------
# Determine artifact status
# ---------------------------------------------------------------------------
$hasErrors = @($issues | Where-Object { $_.severity -eq 'error' }).Count -gt 0
$hasWarns = @($issues | Where-Object { $_.severity -eq 'warn' }).Count -gt 0

if ($hasErrors) {
    if ($WarnOnly) {
        Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Resource graph has errors (downgraded to warn)' -Warn
    } else {
        Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Resource graph has errors'
    }
} elseif ($hasWarns) {
    Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Resource graph has warnings' -Warn
}

# ---------------------------------------------------------------------------
# Build edges (declaration -> source file relationships)
# ---------------------------------------------------------------------------
$edges = [System.Collections.ArrayList]::new()
foreach ($d in $declarations) {
    if ($d.resource_kind -eq 'UNPARSED') { continue }
    [void]$edges.Add([ordered]@{
        from_res       = $d.res_file
        from_line      = $d.res_line
        resource_name  = $d.resource_name
        resource_kind  = $d.resource_kind
        to_source      = $d.resolved_path
        exists         = $d.exists
        classification = $d.classification
    })
}

# ---------------------------------------------------------------------------
# Serialize declarations for JSON (flatten non-serializable parts)
# ---------------------------------------------------------------------------
$serializedDecls = [System.Collections.ArrayList]::new()
foreach ($d in $declarations) {
    $tileStats = $null
    if ($d.exists -and $d.classification -eq 'image' -and $d.resolved_path) {
        $tileStats = Get-SgdkPngTileStats -Path $d.resolved_path
    }
    [void]$serializedDecls.Add([ordered]@{
        resource_kind      = $d.resource_kind
        resource_name      = $d.resource_name
        declared_path      = $d.declared_path
        resolved_path      = $d.resolved_path
        res_file           = $d.res_file
        res_line           = $d.res_line
        exists             = $d.exists
        option_tokens      = @($d.option_tokens)
        normalized_options = $d.normalized_options
        source_size_bytes  = $d.source_size_bytes
        parser_status      = $d.parser_status
        classification     = $d.classification
        tile_stats         = $tileStats
    })
}

# ---------------------------------------------------------------------------
# Measured VRAM evidence, with conservative estimate as fallback
# ---------------------------------------------------------------------------
$spriteReserve = Get-SgdkSpriteEngineReservation -ProjectRoot $ProjectRoot
$defaultLowestMapAddress = 0xC000
$tileMaxBeforeMaps = [int]($defaultLowestMapAddress / 32)
$systemTileStart = 0
$systemTileCount = 16
$fontTileCount = 96
$spriteReserveTiles = [int]$spriteReserve.tiles
$fontStart = $tileMaxBeforeMaps - $fontTileCount
$spriteStart = $fontStart - $spriteReserveTiles
$userTileStart = $systemTileCount
$userTileEnd = $spriteStart - 1
$residentCursor = $userTileStart
$tileRanges = [System.Collections.ArrayList]::new()
$overlaps = [System.Collections.ArrayList]::new()
$measuredEvidencePath = Join-Path $ProjectRoot 'doc\vram_residency_report.json'
$measuredEvidence = $null
$measuredEvidenceStatus = 'not_found'
$measuredEvidenceReason = ''
$measuredResidentResources = @()
$measuredBuildLogPath = ''
$measuredRomSha256 = ''
$reservedFontResource = ''
$measuredEvidenceLevel = ''

if (Test-Path -LiteralPath $measuredEvidencePath -PathType Leaf) {
    try {
        $evidenceDocument = Get-Content -LiteralPath $measuredEvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $measuredEvidence = Get-JsonPropertyValue -Object $evidenceDocument -Name 'res_graph_evidence'
        if ($null -ne $measuredEvidence) {
            $measurementLevel = [string](Get-JsonPropertyValue -Object $measuredEvidence -Name 'measurement_level')
            $measuredEvidenceLevel = $measurementLevel
            $measuredRomSha256 = [string](Get-JsonPropertyValue -Object $measuredEvidence -Name 'rom_sha256')
            $buildLogRelative = [string](Get-JsonPropertyValue -Object $measuredEvidence -Name 'build_log')
            $reservedFontResource = [string](Get-JsonPropertyValue -Object $measuredEvidence -Name 'reserved_font_resource')
            $measuredResidentResources = @(Get-JsonPropertyValue -Object $measuredEvidence -Name 'resident_resources')
            $romIdentity = Get-SgdkRomIdentity -RomPath (Join-Path $ProjectRoot 'out\rom.bin')

            if ($measurementLevel -notin @('rescomp_build_output', 'rescomp_source_hash_snapshot')) {
                throw "unsupported measurement_level '$measurementLevel'"
            }
            if ([string]::IsNullOrWhiteSpace($measuredRomSha256) -or $measuredRomSha256 -notmatch '^[0-9a-fA-F]{64}$') {
                throw 'rom_sha256 must be a 64-character SHA-256'
            }
            if ($romIdentity.rom_sha256 -eq 'MISSING' -or $measuredRomSha256 -ine $romIdentity.rom_sha256) {
                throw "ROM hash mismatch: evidence=$measuredRomSha256 current=$($romIdentity.rom_sha256)"
            }
            $buildLogText = ''
            if ($measurementLevel -eq 'rescomp_build_output') {
                if ([string]::IsNullOrWhiteSpace($buildLogRelative) -or [System.IO.Path]::IsPathRooted($buildLogRelative)) {
                    throw 'build_log must be a project-relative path'
                }

                $projectPrefix = $ProjectRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
                $measuredBuildLogPath = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $buildLogRelative))
                if (-not $measuredBuildLogPath.StartsWith($projectPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                    throw 'build_log resolves outside ProjectRoot'
                }
                if (-not (Test-Path -LiteralPath $measuredBuildLogPath -PathType Leaf)) {
                    throw "build_log not found: $buildLogRelative"
                }
                $buildLogText = Get-Content -LiteralPath $measuredBuildLogPath -Raw -Encoding UTF8
            }
            if ($measuredResidentResources.Count -eq 0) {
                throw 'resident_resources must declare at least one active user-tile resource'
            }

            foreach ($measuredResource in $measuredResidentResources) {
                $resourceName = [string](Get-JsonPropertyValue -Object $measuredResource -Name 'resource_name')
                $tiles = [int](Get-JsonPropertyValue -Object $measuredResource -Name 'unique_tiles')
                $method = [string](Get-JsonPropertyValue -Object $measuredResource -Name 'measurement_method')
                $dataSymbol = [string](Get-JsonPropertyValue -Object $measuredResource -Name 'data_symbol')
                $sourceSha256 = [string](Get-JsonPropertyValue -Object $measuredResource -Name 'source_sha256')
                $originSizeBytes = [int](Get-JsonPropertyValue -Object $measuredResource -Name 'origin_size_bytes')
                $decl = @($serializedDecls.ToArray() | Where-Object { $_.resource_name -eq $resourceName }) | Select-Object -First 1

                if ([string]::IsNullOrWhiteSpace($resourceName) -or $tiles -le 0) {
                    throw 'resident_resources entries require resource_name and positive unique_tiles'
                }
                if ($null -eq $decl) {
                    throw "measured resource is not declared in .res: $resourceName"
                }

                if ($method -eq 'rescomp_origin_size') {
                    if ([string]::IsNullOrWhiteSpace($dataSymbol)) {
                        throw "rescomp_origin_size entry requires data_symbol: $resourceName"
                    }
                    $pattern = "'$([regex]::Escape($dataSymbol))'.*origin size = ([0-9]+)"
                    $match = [regex]::Match($buildLogText, $pattern)
                    if (-not $match.Success) {
                        throw "ResComp origin size not found for $resourceName ($dataSymbol)"
                    }
                    $originBytes = [int]$match.Groups[1].Value
                    if (($originBytes % 32) -ne 0 -or ($originBytes / 32) -ne $tiles) {
                        throw "ResComp tile count mismatch for ${resourceName}: evidence=$tiles origin_bytes=$originBytes"
                    }
                } elseif ($method -eq 'rescomp_origin_size_snapshot') {
                    if ($sourceSha256 -notmatch '^[0-9a-fA-F]{64}$') {
                        throw "rescomp_origin_size_snapshot requires source_sha256: $resourceName"
                    }
                    if ($originSizeBytes -le 0 -or ($originSizeBytes % 32) -ne 0 -or ($originSizeBytes / 32) -ne $tiles) {
                        throw "snapshot origin size mismatch for ${resourceName}: evidence=$tiles origin_bytes=$originSizeBytes"
                    }
                    $currentSourceSha256 = Get-SgdkBinarySha256 -FilePath $decl.resolved_path
                    if ($currentSourceSha256 -ine $sourceSha256) {
                        throw "snapshot source hash mismatch for $resourceName"
                    }
                } elseif ($method -eq 'source_png_unique') {
                    if ($null -eq $decl.tile_stats -or [int]$decl.tile_stats.unique_tiles -ne $tiles) {
                        throw "source PNG tile count mismatch for $resourceName"
                    }
                } else {
                    throw "unsupported measurement_method '$method' for $resourceName"
                }
            }

            if (-not [string]::IsNullOrWhiteSpace($reservedFontResource)) {
                $fontDecl = @($serializedDecls.ToArray() | Where-Object { $_.resource_name -eq $reservedFontResource }) | Select-Object -First 1
                if ($null -eq $fontDecl -or $fontDecl.resource_kind -ne 'TILESET') {
                    throw "reserved_font_resource is not a declared TILESET: $reservedFontResource"
                }
            }

            $measuredEvidenceStatus = 'valid'
        }
    } catch {
        $measuredEvidenceStatus = 'invalid'
        $measuredEvidenceReason = $_.Exception.Message
        [void]$issues.Add([ordered]@{
            res_file = $measuredEvidencePath
            res_line = 0
            severity = 'warn'
            code = 'RG_VRAMEVIDENCE001'
            message = "Explicit VRAM residency evidence rejected: $measuredEvidenceReason"
            resource = 'vram_residency_report'
        })
        Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Explicit VRAM residency evidence is invalid' -Warn
    }
}

$bgResidentDecls = @()
if ($measuredEvidenceStatus -eq 'valid') {
    foreach ($measuredResource in $measuredResidentResources) {
        $resourceName = [string](Get-JsonPropertyValue -Object $measuredResource -Name 'resource_name')
        $tiles = [int](Get-JsonPropertyValue -Object $measuredResource -Name 'unique_tiles')
        $decl = @($serializedDecls.ToArray() | Where-Object { $_.resource_name -eq $resourceName }) | Select-Object -First 1
        $start = $residentCursor
        $end = $residentCursor + $tiles - 1
        [void]$tileRanges.Add([ordered]@{
            resource_name = $resourceName
            resource_kind = $decl.resource_kind
            declared_path = $decl.declared_path
            start_tile = $start
            end_tile = $end
            unique_tiles = $tiles
            assignment_model = 'measured_rescomp_scene_residency'
        })
        if ($end -ge $spriteStart) {
            [void]$overlaps.Add([ordered]@{
                resource_name = $resourceName
                overlap_with = 'sprite_engine_reserve'
                overlap_start_tile = [math]::Max($start, $spriteStart)
                overlap_end_tile = [math]::Min($end, $fontStart - 1)
                resource_range = @($start, $end)
                sprite_reserve_range = @($spriteStart, ($fontStart - 1))
            })
        }
        $residentCursor = $end + 1
    }
} else {
    $bgResidentDecls = @($serializedDecls.ToArray() | Where-Object {
        $_.resource_kind -in @('IMAGE', 'TILESET') -and
        $_.tile_stats -and
        $_.tile_stats.status -eq 'ok'
    })

    foreach ($decl in $bgResidentDecls) {
        $tiles = [int]$decl.tile_stats.unique_tiles
        if ($tiles -le 0) { continue }
        $start = $residentCursor
        $end = $residentCursor + $tiles - 1
        [void]$tileRanges.Add([ordered]@{
            resource_name = $decl.resource_name
            resource_kind = $decl.resource_kind
            declared_path = $decl.declared_path
            start_tile = $start
            end_tile = $end
            unique_tiles = $tiles
            assignment_model = 'sequential_bg_preload_estimate'
        })
        if ($end -ge $spriteStart) {
            [void]$overlaps.Add([ordered]@{
                resource_name = $decl.resource_name
                overlap_with = 'sprite_engine_reserve'
                overlap_start_tile = [math]::Max($start, $spriteStart)
                overlap_end_tile = [math]::Min($end, $fontStart - 1)
                resource_range = @($start, $end)
                sprite_reserve_range = @($spriteStart, ($fontStart - 1))
            })
        }
        $residentCursor = $end + 1
    }
}

$vramStatus = if ($overlaps.Count -gt 0) {
    'collision_risk'
} elseif ($measuredEvidenceStatus -eq 'valid') {
    'ok'
} elseif ($bgResidentDecls.Count -eq 0) {
    'not_measured'
} else {
    'ok'
}
$vram = [ordered]@{
    status = $vramStatus
    method = if ($measuredEvidenceStatus -eq 'valid') {
        if ($measuredEvidenceLevel -eq 'rescomp_source_hash_snapshot') {
            'rescomp_source_hash_snapshot_bound_to_rom_sha256'
        } else {
            'rescomp_build_output_bound_to_rom_sha256'
        }
    } else {
        'png_unique_8x8_tiles_plus_sgdk_default_map_layout'
    }
    measurement_level = if ($measuredEvidenceStatus -eq 'valid') { 'measured' } else { 'estimated' }
    assumptions = if ($measuredEvidenceStatus -eq 'valid') {
        @(
            'resident_resources explicitly declare the active scene user-tile set',
            'ResComp origin size is authoritative for flip-aware deduplicated tile counts and is invalidated when a measured source hash changes',
            'reserved_font_resource replaces the SGDK reserved font region'
        )
    } else {
        @(
            'TILE_USER_INDEX starts at 16',
            'lowest map/table address defaults to 0xC000 unless runtime remaps VDP planes',
            'IMAGE/TILESET declarations are treated as scene-local resident in declaration order',
            'SPR_init() reserves 420 tiles on SGDK 2.11 unless SPR_initEx(n) is found'
        )
    }
    tile_max_before_maps = $tileMaxBeforeMaps
    system_tiles = [ordered]@{ start_tile = $systemTileStart; end_tile = ($systemTileCount - 1); count = $systemTileCount }
    user_tiles = [ordered]@{ start_tile = $userTileStart; end_tile = $userTileEnd; count = [math]::Max(0, ($userTileEnd - $userTileStart + 1)) }
    sprite_reserve_tiles = $spriteReserveTiles
    sprite_reserve = [ordered]@{ start_tile = $spriteStart; end_tile = ($fontStart - 1); count = $spriteReserveTiles; detection = $spriteReserve }
    font_tiles = [ordered]@{ start_tile = $fontStart; end_tile = ($tileMaxBeforeMaps - 1); count = $fontTileCount }
    tile_ranges = @($tileRanges.ToArray())
    overlaps = @($overlaps.ToArray())
    code_loaded_tiles = $codeLoadedTiles
    measured_evidence = [ordered]@{
        status = $measuredEvidenceStatus
        measurement_level = if ($measuredEvidenceStatus -eq 'valid') { $measuredEvidenceLevel } else { $null }
        path = if ($measuredEvidenceStatus -eq 'not_found') { $null } else { $measuredEvidencePath }
        rom_sha256 = if ($measuredEvidenceStatus -eq 'valid') { $measuredRomSha256.ToLowerInvariant() } else { $null }
        build_log = if ($measuredEvidenceStatus -eq 'valid' -and -not [string]::IsNullOrWhiteSpace($measuredBuildLogPath)) { $measuredBuildLogPath } else { $null }
        reserved_font_resource = if ($measuredEvidenceStatus -eq 'valid') { $reservedFontResource } else { $null }
        rejection_reason = if ($measuredEvidenceStatus -eq 'invalid') { $measuredEvidenceReason } else { $null }
    }
}

foreach ($overlap in $overlaps) {
    [void]$issues.Add([ordered]@{
        res_file = ''
        res_line = 0
        severity = 'warn'
        code = 'RG_VRAM001'
        message = "Estimated VRAM tile range for '$($overlap.resource_name)' overlaps sprite engine reserve [$($overlap.overlap_start_tile)..$($overlap.overlap_end_tile)]."
        resource = $overlap.resource_name
    })
}

$summary['vram_residency_status'] = $vramStatus
$summary['sprite_reserve_tiles'] = $spriteReserveTiles
$summary['vram_overlap_count'] = $overlaps.Count
$summary['issues_count'] = $issues.Count
if ($overlaps.Count -gt 0 -and $artifact['status'] -eq 'ok') {
    Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Estimated VRAM residency has BG/sprite reserve overlap' -Warn
}

if ($codeLoadedTiles.status -eq 'code_loaded_tiles_unmeasured') {
    [void]$issues.Add([ordered]@{
        res_file = ''
        res_line = 0
        severity = 'warn'
        code = 'RG_CODETILE001'
        message = "Runtime carrega tiles por codigo C; res_graph estimou $($codeLoadedTiles.estimated_tiles) tile(s), mas isso ainda nao substitui dump/telemetria VDP."
        resource = 'runtime_code_tiles'
    })
    if ($artifact['status'] -eq 'ok') {
        Set-SgdkArtifactFailure -Artifact $artifact -Reason 'Runtime code-loaded tiles require explicit VRAM evidence' -Warn
    }
}

$summary['code_loaded_tiles_status'] = $codeLoadedTiles.status
$summary['code_loaded_tiles_count'] = [int]$codeLoadedTiles.estimated_tiles
$summary['issues_count'] = $issues.Count

# ---------------------------------------------------------------------------
# Assemble and write report
# ---------------------------------------------------------------------------
$resFilePaths = @($resFiles | ForEach-Object { $_.FullName })

$artifact['res_files'] = $resFilePaths
$artifact['declarations'] = @($serializedDecls.ToArray())
$artifact['edges'] = @($edges.ToArray())
$artifact['issues'] = @($issues.ToArray())
$artifact['summary'] = $summary
$artifact['vram'] = $vram

Write-SgdkJsonArtifact -Data $artifact -Path $ReportPath | Out-Null

# ---------------------------------------------------------------------------
# Write markdown summary
# ---------------------------------------------------------------------------
$md = [System.Text.StringBuilder]::new()
[void]$md.AppendLine('# Resource Graph Audit')
[void]$md.AppendLine('')
[void]$md.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$md.AppendLine("Project: $ProjectRoot")
[void]$md.AppendLine('')
[void]$md.AppendLine('## Summary')
[void]$md.AppendLine('')
[void]$md.AppendLine("| Metric | Value |")
[void]$md.AppendLine("|--------|-------|")
[void]$md.AppendLine("| .res files | $($summary.res_files_count) |")
[void]$md.AppendLine("| Total declarations | $($summary.declarations_total) |")
[void]$md.AppendLine("| OK | $($summary.declarations_ok) |")
[void]$md.AppendLine("| Missing source | $($summary.declarations_missing) |")
[void]$md.AppendLine("| Unparsed | $($summary.declarations_unparsed) |")
[void]$md.AppendLine("| Audio | $($summary.audio_count) |")
[void]$md.AppendLine("| Image | $($summary.image_count) |")
[void]$md.AppendLine("| Map | $($summary.map_count) |")
[void]$md.AppendLine("| Binary | $($summary.binary_count) |")
[void]$md.AppendLine("| Total source bytes | $([math]::Round($summary.total_source_bytes / 1024, 1)) KB |")
[void]$md.AppendLine("| Issues | $($summary.issues_count) |")
[void]$md.AppendLine("| VRAM residency status | $($summary.vram_residency_status) |")
[void]$md.AppendLine("| Sprite reserve tiles | $($summary.sprite_reserve_tiles) |")
[void]$md.AppendLine("| VRAM overlaps | $($summary.vram_overlap_count) |")
[void]$md.AppendLine("| Code-loaded tiles status | $($summary.code_loaded_tiles_status) |")
[void]$md.AppendLine("| Code-loaded tiles estimate | $($summary.code_loaded_tiles_count) |")
[void]$md.AppendLine('')

[void]$md.AppendLine('## VRAM Residency Estimate')
[void]$md.AppendLine('')
[void]$md.AppendLine(('Method: `{0}`' -f $vram.method))
[void]$md.AppendLine('')
[void]$md.AppendLine("| Resource | Tile range | Unique tiles |")
[void]$md.AppendLine("|----------|------------|--------------|")
foreach ($range in $vram.tile_ranges) {
    [void]$md.AppendLine("| $($range.resource_name) | $($range.start_tile)-$($range.end_tile) | $($range.unique_tiles) |")
}
if ($vram.tile_ranges.Count -eq 0) {
    [void]$md.AppendLine("| n/a | n/a | 0 |")
}
[void]$md.AppendLine('')

if ($issues.Count -gt 0) {
    [void]$md.AppendLine('## Issues')
    [void]$md.AppendLine('')
    foreach ($issue in $issues) {
        $loc = "$($issue.res_file):$($issue.res_line)"
        [void]$md.AppendLine("- **$($issue.severity.ToUpper())** [$($issue.code)] $loc - $($issue.message)")
    }
    [void]$md.AppendLine('')
}

$parentDir = Split-Path $SummaryPath -Parent
if (-not (Test-Path -LiteralPath $parentDir)) {
    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
}
[System.IO.File]::WriteAllText($SummaryPath, $md.ToString(), [System.Text.Encoding]::UTF8)

# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------
Write-Host ''
if ($artifact['status'] -eq 'ok') {
    Write-Host "[PASS] Resource graph audit: $($summary.declarations_ok) declarations OK across $($summary.res_files_count) .res files." -ForegroundColor Green
} elseif ($artifact['status'] -eq 'warn') {
    Write-Host "[WARN] Resource graph audit: $($summary.issues_count) issues found." -ForegroundColor Yellow
} else {
    Write-Host "[FAIL] Resource graph audit: $($summary.issues_count) issues found." -ForegroundColor Red
}

Write-Host "Report: $ReportPath"
Write-Host "Summary: $SummaryPath"

if ($artifact['status'] -eq 'error' -and -not $WarnOnly) {
    exit 1
}
exit 0
